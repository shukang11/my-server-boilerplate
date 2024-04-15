import hashlib
import time


def getmd5(code: str) -> str:
    """return md5 value of incoming code

    get md5 from code

    Args:
        code: str value

    Return:
        return md5 value of code
    """
    md5string = hashlib.md5(code.encode("utf-8"))
    return md5string.hexdigest()


def get_current_time() -> int:
    return int(time.time() * 1000)
