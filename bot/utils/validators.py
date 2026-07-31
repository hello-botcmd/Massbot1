import re

POST_RE = re.compile(r"t\.me/([^/\s?]+)/(\d+)")


def parse_post(text):
    m = POST_RE.search(text)
    return (m.group(1), int(m.group(2))) if m else (None, None)


def clean_chat_input(text):
    text = text.strip().strip("@")
    if "t.me/" in text:
        text = text.split("t.me/", 1)[1]
    return text.split("?")[0].strip("/")


def invite_hash(text):
    text = clean_chat_input(text)
    if text.startswith("joinchat/"):
        text = text[len("joinchat/"):]
    return text.lstrip("+")


def is_public(text):
    return not (text.startswith("+") or text.startswith("joinchat/"))


def parse_int(text):
    try:
        return int(str(text).strip())
    except (ValueError, AttributeError):
        return None
