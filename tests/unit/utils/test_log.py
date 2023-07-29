from gptcode.utils.log import gptcode_log


def test_error_type():
    gptcode_log.setLevel("INFO")
    gptcode_log.error("Cache log error.")
    gptcode_log.warning("Cache log warning.")
    gptcode_log.info("Cache log info.")
    assert gptcode_log.level == 20
