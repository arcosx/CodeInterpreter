import subprocess
from gptcode.utils.log import gptcode_log
from gptcode.utils.error import PipInstallError


def pip_install(package: str, warn: bool = False):
    """
    Use subprocess execute `pip install`
    """
    cmd = f"pip install -q {package}"
    try:
        if warn and input(f"Install {package}? Y/n:") != "Y":
            raise ModuleNotFoundError(f"No module named {package}")
        print(f"start to install package: {package}")
        subprocess.check_call(cmd, shell=True)
        print(f"successfully installed package: {package}")
        gptcode_log.info("%s installed successfully!", package)

    except subprocess.CalledProcessError as e:
        raise PipInstallError(package) from e
