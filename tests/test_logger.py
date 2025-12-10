import logging
def test_logs_warning_message(caplog):
    logger = logging.getLogger("test_logger")
    with caplog.at_level(logging.WARNING):
        logger.warning("This is a warning message")
    assert "This is a warning message" in caplog.text
    assert caplog.records[0].levelname == "WARNING"
