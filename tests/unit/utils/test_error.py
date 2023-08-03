from codeinterpreter.utils.error import CodeInterpreterError, PipInstallError


def test_error_type():
    pip_install_error = PipInstallError("openai")
    assert issubclass(type(pip_install_error), CodeInterpreterError)
