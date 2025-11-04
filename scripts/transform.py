from pathlib import Path
from urllib.parse import urlparse
import json
import textwrap


REPLACEMENTS = [
    ("Vancouver Community", "Vancouver Minor"),
    ("Mounties", "Expos"),
]

ASCII_MAP = {
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2013": "-",
    "\u2014": "-",
    "\u2026": "...",
    "\u00a0": " ",
}


def apply_branding(value: str) -> str:
    if not isinstance(value, str):
        return value
    for old, new in REPLACEMENTS:
        value = value.replace(old, new)
    for key, replacement in ASCII_MAP.items():
        value = value.replace(key, replacement)
    return value


def normalize_url(url: str) -> str:
    if not url or url == "#":
        return "#"
    parsed = urlparse(url)
    if parsed.scheme or parsed.netloc:
        return parsed.path or "/"
    return url


def transform_nav(items):
    transformed = []
    for item in items:
        transformed.append(
            {
                "label": apply_branding(item["label"]),
                "url": normalize_url(item["url"]),
                "children": transform_nav(item.get("children", [])),
            }
        )
    return transformed


def transform_achievements(items):
    transformed = []
    for idx, item in enumerate(items, start=1):
        transformed.append(
            {
                "slug": f"achievement-{idx:02d}",
                "title": apply_branding(item["title"]),
                "image_alt": apply_branding(item.get("image_alt") or ""),
            }
        )
    return transformed


def main():
    data = json.loads(Path("reference/content.json").read_text())

    hero = {
        "title": apply_branding(data["hero_title"]),
        "paragraphs": [apply_branding(p) for p in data["hero_paragraphs"]],
    }

    nav = transform_nav(data["nav_items"])
    achievements = transform_achievements(data["achievements"])
    footer = apply_branding(data["footer_text"])

    output = textwrap.dedent(
        f"""\
HERO = {hero!r}

NAVIGATION = {nav!r}

ACHIEVEMENTS = {achievements!r}

FOOTER_TEXT = {footer!r}
"""
    )
    print(output)


if __name__ == "__main__":
    main()
