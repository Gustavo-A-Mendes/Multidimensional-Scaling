import pyperclip


def copy(text):
    try:
        pyperclip.copy(text)
        return True
    except Exception:
        return False