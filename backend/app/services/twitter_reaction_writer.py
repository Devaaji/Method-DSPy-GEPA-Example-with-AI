from __future__ import annotations

import re

from app.models.twitter import TwitterGenerateRequest
from app.prompts.twitter import topic_is_tech_related

REACTION_MARKERS = (
    "agak",
    "jujur",
    "miris",
    "aneh",
    "kocak",
    "lucu",
    "ngaco",
    "parah",
    "sedih",
    "nyeleneh",
)


def is_indonesian_reaction_brief(payload: TwitterGenerateRequest) -> bool:
    if payload.language != "Indonesian":
        return False
    if topic_is_tech_related(payload.topic):
        return False

    normalized = payload.topic.lower()
    return (
        any(marker in normalized for marker in REACTION_MARKERS)
        or '"' in payload.topic
        or "“" in payload.topic
        or "”" in payload.topic
    )


def _extract_quote(topic: str) -> str:
    match = re.search(r'["“](.+?)["”]', topic)
    if match:
        quote = match.group(1).strip()
        return quote[:120]
    compact = re.sub(r"\s+", " ", topic).strip()
    return compact[:120]


def _clean_topic(topic: str) -> str:
    compact = re.sub(r"\s+", " ", topic).strip()
    return compact.strip('"').strip("'").strip()


def _trim_to_limit(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text

    shortened = text[: max_chars - 1].rstrip(" ,.-")
    return f"{shortened}…"


def build_reaction_tweets(payload: TwitterGenerateRequest) -> str:
    quote = _extract_quote(payload.topic)
    topic = _clean_topic(payload.topic)

    candidates = [
        f'Jujur, kalimat "{quote}" kedengarannya simpel, tapi makin dipikir malah bikin miris.',
        f'Agak kocak dengernya, tapi justru itu yang bikin nggak tenang. "{quote}" bukan kalimat yang bisa dianggap enteng.',
        f'Yang bikin aneh bukan cuma ucapan "{quote}", tapi cara mikir di belakangnya.',
        f'Awalnya kedengarannya sepele. Tapi begitu dipikir ulang, "{quote}" malah terasa miris juga.',
        f'Entah ya, {quote.lower()} itu kesannya santai, padahal kalau dicermati justru bikin banyak tanda tanya.',
        f'Kalimat "{quote}" tuh model yang bikin orang ketawa dulu, terus beberapa detik kemudian malah mikir, "loh, serius nih?"',
        f'Buatku yang paling nyangkut justru bukan dramanya, tapi betapa ringannya kalimat "{quote}" dilontarkan.',
        f'Kalau disederhanakan begini: {topic}. Kedengarannya lucu, tapi isi pesannya malah nggak ringan sama sekali.',
    ]

    unique_lines: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        line = _trim_to_limit(candidate, payload.max_chars)
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)

    selected = unique_lines[: payload.count]
    return "\n".join(f"Tweet {index}: {tweet}" for index, tweet in enumerate(selected, start=1))
