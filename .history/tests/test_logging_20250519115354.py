import logging
import os
import tempfile
from datetime import datetime

import toml

from preswald.utils import configure_logging


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
        log_capture = []
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

        # The timestamp should be in the format YYYY-MM-DD HH:MM:SS.microseconds
        timestamp = log_output.split(" - ")[0]
        try:
            datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
            assert True  # If we get here, the format is correct
        except ValueError:
            assert False, f"Timestamp {timestamp} does not match expected format"

    finally:
        os.unlink(config_path)


def test_custom_timestamp_format():
    """Test that custom timestamp format is respected"""
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
        log_capture = []
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

        # The timestamp should be in the custom format
        timestamp = log_output.split(" - ")[0]
        try:
            datetime.strptime(timestamp, custom_format)
            assert True  # If we get here, the format is correct
        except ValueError:
            assert False, (
                f"Timestamp {timestamp} does not match expected format {custom_format}"
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
        datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
        assert True  # If we get here, the format is correct
    except ValueError:
        assert False, f"Timestamp {timestamp} does not match expected format"
