import secrets
import string

import pytest

from preswald.utils import validate_slug


def test_validate_slug_when_slug_len_more_2_and_less_64():
    # arrange
    test_slug = "test-slug-123"
    expected_validation = True

    # act
    actual_validation = validate_slug(test_slug)

    # assert
    assert expected_validation == actual_validation


def test_validate_slug_when_slug_2_letters():
    # arrange
    test_slug = "ab"
    expected_validation = False

    # act
    actual_validation = validate_slug(test_slug)

    # assert
    assert expected_validation == actual_validation


def test_validate_slug_when_slug_1_digit_as_string():
    # arrange
    test_slug = "1"
    expected_validation = False

    # act
    actual_validation = validate_slug(test_slug)

    # assert
    assert expected_validation == actual_validation


def test_validate_slug_when_slug_64_symbols():
    # arrange
    max_slug_len = 63
    alphabet = string.ascii_letters + string.digits
    random_str_with_len_64 = "".join(
        secrets.choice(alphabet) for _ in range(max_slug_len + 1)
    )
    expected_validation = False

    # act
    actual_validation = validate_slug(random_str_with_len_64)

    # assert
    assert expected_validation == actual_validation


def test_validate_slug_when_slug_4_symbols_and_sign_of_any_special_symbols():
    # arrange
    special_symbols = "[!@#$%^&*()_+=-`~[]{}|;':\",.\\/<>?]"

    for special_char in special_symbols:
        # arrange
        test_slug = "abc" + special_char
        expected_validation = False

        # act
        actual_validation = validate_slug(test_slug)

        # assert
        assert expected_validation == actual_validation


def test_validate_slug_when_slug_1_digit_then_raise_exception():
    # arrange
    test_slug = 1

    # act
    with pytest.raises(TypeError) as excinfo:
        validate_slug(test_slug)

    # assert
    assert str(excinfo.value) == "expected string or bytes-like object, got 'int'"
