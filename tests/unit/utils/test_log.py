from gptcode.utils.log import gptcode_log


def test_error_type():
    gptcode_log.setLevel("INFO")
    gptcode_log.error("gptcode log error.")
    gptcode_log.warning("gptcode log warning.")
    gptcode_log.info("gptcode log info.")
    assert gptcode_log.level == 20
