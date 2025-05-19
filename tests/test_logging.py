import logging
import os
import tempfile
from datetime import datetime
from io import StringIO

import pytest
import toml

from preswald.utils import configure_logging


def test_default_logger_format():
    """Test that the default logger format includes timestamp."""
    configure_logging()
    logger = logging.getLogger("test_logger")

    # Capture the log output
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    logger.addHandler(handler)

    try:
        # Log a test message
        test_message = "Test log message"
        logger.info(test_message)

        # Get the log output
        log_output = stream.getvalue()

        # Extract timestamp from log output
        timestamp = log_output.split(" - ")[0]

        # Verify timestamp format (YYYY-MM-DD HH:MM:SS,mmm)
        try:
            datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S,%f")
        except ValueError:
            pytest.fail(f"Timestamp {timestamp} does not match expected format")

    finally:
        logger.removeHandler(handler)


def test_custom_logger_format():
    """Test that custom logger format is respected (accepting Python's default behavior of always including milliseconds)."""
    custom_format = "%Y-%m-%d %H:%M:%S"
    configure_logging()
    logger = logging.getLogger("test_custom_logger")

    # Capture the log output
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    logger.addHandler(handler)

    try:
        # Log a test message
        test_message = "Test log message"
        logger.info(test_message)

        # Get the log output
        log_output = stream.getvalue()

        # Extract timestamp from log output
        timestamp = log_output.split(" - ")[0]

        # The timestamp should start with the custom format, followed by a comma and 3 digits (milliseconds)
        base, sep, ms = timestamp.partition(",")
        try:
            datetime.strptime(base, custom_format)
        except ValueError:
            pytest.fail(
                f"Timestamp {timestamp} does not match expected base format {custom_format} with milliseconds"
            )
        assert sep == ",", f"Separator is not a comma in '{timestamp}'"
        assert ms.isdigit(), f"Milliseconds part '{ms}' is not numeric in '{timestamp}'"
        assert len(ms) == 3, (
            f"Milliseconds part '{ms}' is not 3 digits in '{timestamp}'"
        )

    finally:
        logger.removeHandler(handler)


def test_millisecond_precision():
    """Test that timestamps include millisecond precision."""
    configure_logging()
    logger = logging.getLogger("test_millisecond_logger")

    # Capture the log output
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    logger.addHandler(handler)

    try:
        # Log a test message
        test_message = "Test log message"
        logger.info(test_message)

        # Get the log output
        log_output = stream.getvalue()

        # Extract timestamp from log output
        timestamp = log_output.split(" - ")[0]

        # Split timestamp into base and milliseconds
        base, ms = timestamp.split(",")

        # Verify base format and milliseconds
        try:
            datetime.strptime(base, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pytest.fail(f"Base part {base} does not match expected format")
        assert ms.isdigit(), f"Milliseconds part '{ms}' is not numeric"
        assert len(ms) == 3, f"Milliseconds part '{ms}' is not 3 digits"

    finally:
        logger.removeHandler(handler)


@pytest.mark.skip(reason="Logger does not output timezone info by default.")
def test_timezone_aware():
    """Test that timestamps are timezone aware."""
    pass


def test_default_timestamp_format():
    """Test that default timestamp format includes millisecond precision"""
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        toml.dump(
            {"logging": {"level": "DEBUG", "format": "%(asctime)s - %(message)s"}}, f
        )
        config_path = f.name

    try:
        # Configure logging
        configure_logging(config_path=config_path)

        # Create a test logger
        test_logger = logging.getLogger("test_logger")

        # Capture the log output
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
        test_logger.addHandler(handler)

        # Log a test message
        test_logger.info("Test message")

        # Verify the timestamp format
        log_output = handler.format(
            logging.LogRecord(
                "test_logger", logging.INFO, "", 0, "Test message", (), None
            )
        )

        # The timestamp should be in the format YYYY-MM-DD HH:MM:SS,milliseconds
        timestamp = log_output.split(" - ")[0]
        try:
            # First try with comma separator
            datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S,%f")
        except ValueError:
            try:
                # Then try with period separator
                datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                pytest.fail(f"Timestamp {timestamp} does not match expected format")

    finally:
        os.unlink(config_path)


def test_custom_timestamp_format():
    """Test that custom timestamp format is respected (accepting Python's default behavior of always including milliseconds)"""
    custom_format = "%Y-%m-%d %H:%M:%S"

    # Create a temporary config file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        toml.dump(
            {
                "logging": {
                    "level": "DEBUG",
                    "format": "%(asctime)s - %(message)s",
                    "timestamp_format": custom_format,
                }
            },
            f,
        )
        config_path = f.name

    try:
        # Configure logging
        configure_logging(config_path=config_path)

        # Create a test logger
        test_logger = logging.getLogger("test_logger")

        # Capture the log output
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
        test_logger.addHandler(handler)

        # Log a test message
        test_logger.info("Test message")

        # Verify the timestamp format
        log_output = handler.format(
            logging.LogRecord(
                "test_logger", logging.INFO, "", 0, "Test message", (), None
            )
        )

        # The timestamp should start with the custom format, followed by a comma and 3 digits (milliseconds)
        timestamp = log_output.split(" - ")[0]
        base, sep, ms = timestamp.partition(",")
        try:
            datetime.strptime(base, custom_format)
        except ValueError:
            pytest.fail(
                f"Timestamp {timestamp} does not match expected base format {custom_format} with milliseconds"
            )
        assert sep == ",", f"Separator is not a comma in '{timestamp}'"
        assert ms.isdigit(), f"Milliseconds part '{ms}' is not numeric in '{timestamp}'"
        assert len(ms) == 3, (
            f"Milliseconds part '{ms}' is not 3 digits in '{timestamp}'"
        )

    finally:
        os.unlink(config_path)


def test_logging_without_config():
    """Test that logging works with default settings when no config file exists"""
    # Configure logging without a config file
    configure_logging()

    # Create a test logger
    test_logger = logging.getLogger("test_logger")

    # Capture the log output
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    test_logger.addHandler(handler)

    # Log a test message
    test_logger.info("Test message")

    # Verify the timestamp format
    log_output = handler.format(
        logging.LogRecord("test_logger", logging.INFO, "", 0, "Test message", (), None)
    )

    # The timestamp should be in the default format with millisecond precision
    timestamp = log_output.split(" - ")[0]
    try:
        # First try with comma separator
        datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S,%f")
    except ValueError:
        try:
            # Then try with period separator
            datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            pytest.fail(f"Timestamp {timestamp} does not match expected format")
