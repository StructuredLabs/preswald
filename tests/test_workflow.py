"""Tests for the Workflow/DAG engine."""

import time
from contextlib import contextmanager
from unittest.mock import patch

import pytest

from preswald.interfaces.workflow import (
    Atom,
    AtomCache,
    AtomResult,
    AtomStatus,
    RetryPolicy,
    Workflow,
    WorkflowContext,
)


# ---------------------------------------------------------------------------
# Mock service
# ---------------------------------------------------------------------------

class MockService:
    """Minimal mock of BasePreswaldService for Workflow tests."""

    def __init__(self):
        self._current_atom = None

    @contextmanager
    def active_atom(self, name: str):
        previous = self._current_atom
        self._current_atom = name
        try:
            yield
        finally:
            self._current_atom = previous

    @property
    def is_reactivity_enabled(self):
        return True


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def service():
    return MockService()


@pytest.fixture
def workflow(service):
    return Workflow(service=service)


@pytest.fixture
def bare_workflow():
    """Workflow without a service, for simpler tests."""
    return Workflow()


# ---------------------------------------------------------------------------
# 1. Atom registration
# ---------------------------------------------------------------------------

class TestAtomRegistration:
    def test_register_single_atom(self, workflow):
        @workflow.atom()
        def my_atom():
            return 42

        assert "my_atom" in workflow.atoms
        assert workflow.atoms["my_atom"].name == "my_atom"

    def test_register_multiple_atoms(self, workflow):
        @workflow.atom()
        def alpha():
            return 1

        @workflow.atom()
        def beta():
            return 2

        assert "alpha" in workflow.atoms
        assert "beta" in workflow.atoms
        assert len(workflow.atoms) == 2

    def test_register_atom_with_custom_name(self, workflow):
        @workflow.atom(name="custom_name")
        def some_func():
            return 0

        assert "custom_name" in workflow.atoms
        assert "some_func" not in workflow.atoms


# ---------------------------------------------------------------------------
# 2. Dependency tracking
# ---------------------------------------------------------------------------

class TestDependencyTracking:
    def test_explicit_dependencies(self, workflow):
        @workflow.atom()
        def source():
            return 10

        @workflow.atom(dependencies=["source"])
        def consumer(source):
            return source + 1

        assert workflow.atoms["consumer"].dependencies == ["source"]

    def test_inferred_dependencies(self, workflow):
        @workflow.atom()
        def a():
            return 1

        @workflow.atom()
        def b():
            return 2

        # Parameter names match atom names -> inferred deps
        @workflow.atom()
        def c(a, b):
            return a + b

        assert set(workflow.atoms["c"].dependencies) == {"a", "b"}

    def test_register_dependency_dynamically(self, workflow):
        @workflow.atom()
        def x():
            return 1

        @workflow.atom()
        def y():
            return 2

        workflow.register_dependency("y", "x")
        assert "x" in workflow.atoms["y"].dependencies


# ---------------------------------------------------------------------------
# 3. Execution order (topological)
# ---------------------------------------------------------------------------

class TestExecutionOrder:
    def test_chain_execution_order(self, bare_workflow):
        wf = bare_workflow
        execution_log = []

        @wf.atom()
        def step1():
            execution_log.append("step1")
            return 1

        @wf.atom(dependencies=["step1"])
        def step2(step1):
            execution_log.append("step2")
            return step1 + 1

        @wf.atom(dependencies=["step2"])
        def step3(step2):
            execution_log.append("step3")
            return step2 + 1

        with patch("preswald.interfaces.workflow.register_error"):
            results = wf.execute()

        assert execution_log == ["step1", "step2", "step3"]
        assert results["step3"].value == 3

    def test_diamond_execution_order(self, bare_workflow):
        wf = bare_workflow
        execution_log = []

        @wf.atom()
        def root():
            execution_log.append("root")
            return 1

        @wf.atom(dependencies=["root"])
        def left(root):
            execution_log.append("left")
            return root + 10

        @wf.atom(dependencies=["root"])
        def right(root):
            execution_log.append("right")
            return root + 20

        @wf.atom(dependencies=["left", "right"])
        def sink(left, right):
            execution_log.append("sink")
            return left + right

        with patch("preswald.interfaces.workflow.register_error"):
            results = wf.execute()

        # root must come before left and right; sink must come last
        assert execution_log.index("root") < execution_log.index("left")
        assert execution_log.index("root") < execution_log.index("right")
        assert execution_log.index("sink") == len(execution_log) - 1
        assert results["sink"].value == 32


# ---------------------------------------------------------------------------
# 4. Caching
# ---------------------------------------------------------------------------

class TestCaching:
    def test_cache_hit_on_same_inputs(self, bare_workflow):
        wf = bare_workflow
        call_count = 0

        @wf.atom()
        def cached_atom():
            nonlocal call_count
            call_count += 1
            return 42

        with patch("preswald.interfaces.workflow.register_error"):
            # First execution
            wf.execute()
            assert call_count == 1

            # Second execution -- cache is cleared each execute() call,
            # so we test via _execute_atom directly after populating cache.

        # Manually check AtomCache behaviour
        cache = AtomCache()
        h = cache.compute_input_hash("atom_a", {"x": 1})
        assert cache.should_recompute("atom_a", h) is True  # not cached yet

        cache.cache["atom_a"] = AtomResult(
            status=AtomStatus.COMPLETED, value=99, input_hash=h
        )
        assert cache.should_recompute("atom_a", h) is False  # cached

    def test_cache_miss_on_different_inputs(self):
        cache = AtomCache()
        h1 = cache.compute_input_hash("atom_a", {"x": 1})
        cache.cache["atom_a"] = AtomResult(
            status=AtomStatus.COMPLETED, value=99, input_hash=h1
        )

        h2 = cache.compute_input_hash("atom_a", {"x": 2})
        assert cache.should_recompute("atom_a", h2) is True


# ---------------------------------------------------------------------------
# 5. Selective recomputation
# ---------------------------------------------------------------------------

class TestSelectiveRecomputation:
    def test_only_affected_downstream_reruns(self, bare_workflow):
        wf = bare_workflow
        call_counts = {"a": 0, "b": 0, "c": 0}

        @wf.atom()
        def a():
            call_counts["a"] += 1
            return 1

        @wf.atom(dependencies=["a"])
        def b(a):
            call_counts["b"] += 1
            return a + 1

        @wf.atom()
        def c():
            call_counts["c"] += 1
            return 100

        with patch("preswald.interfaces.workflow.register_error"):
            # Initial full run
            wf.execute()
            assert call_counts == {"a": 1, "b": 1, "c": 1}

            # Selective recompute: only "a" changed -> "b" (downstream) should rerun
            # but "c" is independent. However _get_affected_atoms also pulls in
            # upstream deps of affected atoms, so both a and b should rerun.
            wf.execute(recompute_atoms={"a"})

        # a and b should have been re-executed; c should be skipped on rerun
        assert call_counts["a"] == 2
        assert call_counts["b"] == 2
        assert call_counts["c"] == 1  # not affected


# ---------------------------------------------------------------------------
# 6. Cycle detection
# ---------------------------------------------------------------------------

class TestCycleDetection:
    def test_circular_dependency_raises(self, bare_workflow):
        wf = bare_workflow

        @wf.atom(dependencies=["beta"])
        def alpha(beta):
            return 1

        @wf.atom(dependencies=["alpha"])
        def beta(alpha):
            return 2

        with pytest.raises(ValueError, match="Cycle detected"):
            wf._get_execution_order()

    def test_self_dependency_raises(self, bare_workflow):
        wf = bare_workflow

        @wf.atom(dependencies=["self_ref"])
        def self_ref():
            return 0

        with pytest.raises(ValueError, match="Cycle detected"):
            wf._get_execution_order()


# ---------------------------------------------------------------------------
# 7. Component producer tracking
# ---------------------------------------------------------------------------

class TestComponentProducer:
    def test_register_and_get_component_producer(self, workflow):
        @workflow.atom()
        def producer():
            return "widget"

        workflow.register_component_producer("comp-1", "producer")
        assert workflow.get_component_producer("comp-1") == "producer"

    def test_get_unknown_component_returns_none(self, workflow):
        assert workflow.get_component_producer("nonexistent") is None

    def test_register_for_unknown_atom_is_ignored(self, workflow):
        workflow.register_component_producer("comp-2", "does_not_exist")
        assert workflow.get_component_producer("comp-2") is None


# ---------------------------------------------------------------------------
# 8. Affected atoms (_get_affected_atoms)
# ---------------------------------------------------------------------------

class TestAffectedAtoms:
    def test_multi_level_dag(self, bare_workflow):
        """
        DAG:  a -> b -> d
              a -> c -> d
        Changing "a" should affect a, b, c, d (forward + backward closure).
        """
        wf = bare_workflow

        @wf.atom()
        def a():
            return 1

        @wf.atom(dependencies=["a"])
        def b(a):
            return a

        @wf.atom(dependencies=["a"])
        def c(a):
            return a

        @wf.atom(dependencies=["b", "c"])
        def d(b, c):
            return b + c

        affected = wf._get_affected_atoms({"a"})
        assert affected == {"a", "b", "c", "d"}

    def test_change_leaf_only_affects_subtree(self, bare_workflow):
        """
        DAG:  a -> b -> c
        Changing "c" should pull in b (upstream) and a (upstream of b),
        because _get_affected_atoms does backward closure too.
        """
        wf = bare_workflow

        @wf.atom()
        def a():
            return 1

        @wf.atom(dependencies=["a"])
        def b(a):
            return a

        @wf.atom(dependencies=["b"])
        def c(b):
            return b

        affected = wf._get_affected_atoms({"c"})
        # backward closure pulls in b and then a
        assert affected == {"a", "b", "c"}

    def test_change_middle_node(self, bare_workflow):
        """
        DAG:  a -> b -> c
        Changing "b" -> forward: c, backward: a  => all affected.
        """
        wf = bare_workflow

        @wf.atom()
        def a():
            return 1

        @wf.atom(dependencies=["a"])
        def b(a):
            return a

        @wf.atom(dependencies=["b"])
        def c(b):
            return b

        affected = wf._get_affected_atoms({"b"})
        assert affected == {"a", "b", "c"}

    def test_empty_changed_set(self, bare_workflow):
        wf = bare_workflow

        @wf.atom()
        def a():
            return 1

        affected = wf._get_affected_atoms(set())
        assert affected == set()


# ---------------------------------------------------------------------------
# 9. RetryPolicy
# ---------------------------------------------------------------------------

class TestRetryPolicy:
    def test_should_retry_within_max_attempts(self):
        policy = RetryPolicy(max_attempts=3)
        assert policy.should_retry(1, Exception("err")) is True
        assert policy.should_retry(2, Exception("err")) is True
        assert policy.should_retry(3, Exception("err")) is False

    def test_should_retry_only_matching_exceptions(self):
        policy = RetryPolicy(max_attempts=5, retry_exceptions=(ValueError,))
        assert policy.should_retry(1, ValueError("v")) is True
        assert policy.should_retry(1, TypeError("t")) is False

    def test_backoff_delay(self):
        policy = RetryPolicy(delay=1.0, backoff_factor=2.0)
        assert policy.get_delay(1) == 1.0
        assert policy.get_delay(2) == 2.0
        assert policy.get_delay(3) == 4.0

    def test_atom_retries_on_transient_failure(self, bare_workflow):
        wf = bare_workflow
        call_count = 0

        policy = RetryPolicy(max_attempts=3, delay=0.0, backoff_factor=1.0)

        @wf.atom(retry_policy=policy)
        def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("transient")
            return "ok"

        with patch("preswald.interfaces.workflow.register_error"):
            results = wf.execute()

        assert results["flaky"].status == AtomStatus.COMPLETED
        assert results["flaky"].value == "ok"
        assert call_count == 3

    def test_atom_fails_after_exhausting_retries(self, bare_workflow):
        wf = bare_workflow

        policy = RetryPolicy(max_attempts=2, delay=0.0, backoff_factor=1.0)

        @wf.atom(retry_policy=policy)
        def always_fails():
            raise RuntimeError("permanent")

        with patch("preswald.interfaces.workflow.register_error"):
            results = wf.execute()

        assert results["always_fails"].status == AtomStatus.FAILED
        assert isinstance(results["always_fails"].error, RuntimeError)
        assert results["always_fails"].attempts == 2


# ---------------------------------------------------------------------------
# 10. WorkflowContext
# ---------------------------------------------------------------------------

class TestWorkflowContext:
    def test_set_and_get_variable(self):
        ctx = WorkflowContext()
        ctx.set_variable("x", 42)
        assert ctx.get_variable("x") == 42

    def test_get_missing_variable_returns_none(self):
        ctx = WorkflowContext()
        assert ctx.get_variable("missing") is None

    def test_set_result_stores_completed_value(self):
        ctx = WorkflowContext()
        result = AtomResult(status=AtomStatus.COMPLETED, value="hello")
        ctx.set_result("my_atom", result)

        assert ctx.results["my_atom"] is result
        # Completed results also set the variable
        assert ctx.variables["my_atom"] == "hello"

    def test_set_result_failed_does_not_set_variable(self):
        ctx = WorkflowContext()
        result = AtomResult(status=AtomStatus.FAILED, error=Exception("boom"))
        ctx.set_result("bad_atom", result)

        assert ctx.results["bad_atom"] is result
        assert "bad_atom" not in ctx.variables


# ---------------------------------------------------------------------------
# 11. AtomResult status transitions
# ---------------------------------------------------------------------------

class TestAtomResult:
    def test_pending_to_completed(self):
        r = AtomResult(status=AtomStatus.PENDING)
        assert r.status == AtomStatus.PENDING

        r.status = AtomStatus.RUNNING
        assert r.status == AtomStatus.RUNNING

        r.status = AtomStatus.COMPLETED
        r.value = 99
        assert r.status == AtomStatus.COMPLETED
        assert r.value == 99

    def test_pending_to_failed(self):
        r = AtomResult(status=AtomStatus.PENDING)
        r.status = AtomStatus.RUNNING
        r.status = AtomStatus.FAILED
        r.error = RuntimeError("oops")
        assert r.status == AtomStatus.FAILED
        assert isinstance(r.error, RuntimeError)

    def test_execution_time_calculation(self):
        r = AtomResult(
            status=AtomStatus.COMPLETED,
            start_time=100.0,
            end_time=103.5,
        )
        assert r.execution_time == pytest.approx(3.5)

    def test_execution_time_none_when_missing(self):
        r = AtomResult(status=AtomStatus.PENDING)
        assert r.execution_time is None


# ---------------------------------------------------------------------------
# 12. Workflow.reset()
# ---------------------------------------------------------------------------

class TestWorkflowReset:
    def test_reset_clears_everything(self, bare_workflow):
        wf = bare_workflow

        @wf.atom()
        def something():
            return 1

        wf.context.set_variable("v", 10)
        wf.register_component_producer("comp-x", "something")
        wf._current_atom = "something"
        wf._is_rerun = True

        wf.reset()

        assert wf.atoms == {}
        assert wf.context.variables == {}
        assert wf.context.results == {}
        assert wf._component_producers == {}
        assert wf.cache.cache == {}
        assert wf._current_atom is None
        assert wf._is_rerun is False
        assert wf._auto_atom_registry == {}
        assert wf._registered_reactive_atoms == []
