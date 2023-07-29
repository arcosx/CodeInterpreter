from gptcode.utils.error import GPTCodeError, PipInstallError


def test_error_type():
    pip_install_error = PipInstallError("openai")
    assert issubclass(type(pip_install_error), GPTCodeError)
