from codeinterpreter.utils.log import codeinterpreter_log


def test_error_type():
    codeinterpreter_log.setLevel("INFO")
    codeinterpreter_log.error("codeinterpreter log error.")
    codeinterpreter_log.warning("codeinterpreter log warning.")
    codeinterpreter_log.info("codeinterpreter log info.")
    assert codeinterpreter_log.level == 20
