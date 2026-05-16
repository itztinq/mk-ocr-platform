import re


MACEDONIAN_LETTERS = "АБВГДЃЕЖЗЅИЈКЛЉМНЊОПРСТЌУФХЦЧЏШабвгдѓежзѕијклљмнњопрстќуфхцчџш"
MACEDONIAN_WORD_CHARS_PATTERN = rf"^[{MACEDONIAN_LETTERS}]+(?:-[{MACEDONIAN_LETTERS}]+)*$"


def normalize_ocr_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)

    text = re.sub(
        r"([A-Za-zА-Ша-шЃѓЅѕЈјЉљЊњЌќЏџ])-\n([A-Za-zА-Ша-шЃѓЅѕЈјЉљЊњЌќЏџ])",
        r"\1\2",
        text,
    )

    text = re.sub(r"(?<![.!?:;…])\n(?!\n)", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)

    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)

    return text.strip()


def apply_safe_macedonian_fixes(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r"[“”„‟«»]", "\"", text)
    text = re.sub(r"[‘’‚‛`]", "'", text)
    text = re.sub(r"…", "...", text)

    text = re.sub(r"[ \t]+([,.;:!?])", r"\1", text)
    text = re.sub(r"([(\[\{])\s+", r"\1", text)
    text = re.sub(r"\s+([)\]\}])", r"\1", text)

    return text.strip()


def looks_like_macedonian_word(token: str) -> bool:
    return bool(re.fullmatch(MACEDONIAN_WORD_CHARS_PATTERN, token))


def is_suspicious_token(token: str, conf_value: float, conf_threshold: float = 55.0) -> bool:
    if not token:
        return False

    if 0 <= conf_value < conf_threshold:
        return True

    if re.search(r"[A-Za-z]+\d|\d+[A-Za-z]+", token):
        return True

    if re.search(rf"[{MACEDONIAN_LETTERS}]+\d|\d+[{MACEDONIAN_LETTERS}]+", token):
        return True

    if re.search(r"[A-Za-z]", token) and re.search(rf"[{MACEDONIAN_LETTERS}]", token):
        return True

    if len(token) > 2 and re.search(r"[^\w\-–—.,!?;:()\"'„“”‘’/]", token):
        return True

    if re.search(rf"[{MACEDONIAN_LETTERS}]", token):
        stripped = token.strip(".,!?;:()[]{}\"'„“”‘’/-–—")
        if stripped and not looks_like_macedonian_word(stripped):
            return True

    return False


def detect_suspicious_tokens(data: dict, conf_threshold: float = 55.0) -> list[str]:
    suspicious = set()

    texts = data.get("text", [])
    confs = data.get("conf", [])

    for token, conf in zip(texts, confs):
        token = (token or "").strip()
        if not token:
            continue

        try:
            conf_value = float(conf)
        except (TypeError, ValueError):
            conf_value = -1

        if is_suspicious_token(token, conf_value, conf_threshold):
            suspicious.add(token)

    return sorted(suspicious)


def average_confidence(data: dict) -> float | None:
    confs = []

    for conf in data.get("conf", []):
        try:
            value = float(conf)
        except (TypeError, ValueError):
            continue

        if value >= 0:
            confs.append(value)

    if not confs:
        return None

    return round(sum(confs) / len(confs), 2)