from pathlib import Path
import json

from bs4 import BeautifulSoup


def parse_menu(ul):
    items = []
    for li in ul.find_all("li", recursive=False):
        link = li.find("a")
        label = link.get_text(strip=True)
        url = link.get("href", "").strip()
        submenu = li.find("ul", class_="sub-menu")
        items.append(
            {
                "label": label,
                "url": url,
                "children": parse_menu(submenu) if submenu else [],
            }
        )
    return items


def main():
    source = Path("reference/source.html")
    soup = BeautifulSoup(source.read_text(), "html.parser")

    hero_title = soup.select_one("#intro h1 .fl-heading-text").get_text(strip=True)
    hero_paragraphs = [
        p.get_text(strip=True) for p in soup.select("#intro .fl-rich-text p")
    ]

    nav_root = soup.select_one("#menu-ts-home-menu")
    nav_items = parse_menu(nav_root) if nav_root else []

    achievements = []
    rows = soup.select('.fl-row[data-node="tay0zsb3mqex"] .fl-module-rich-text h3')
    for heading in rows:
        title = heading.get_text("\n", strip=True)

        image = None
        module = heading.find_parent(class_="fl-module")
        if module:
            photo_module = module.find_next_sibling("div", class_="fl-module")
            if photo_module:
                image = photo_module.find("img")

        achievements.append(
            {
                "title": title,
                "image": image.get("src") if image else None,
                "image_alt": image.get("alt") if image else None,
            }
        )

    footer_text = soup.select_one(".fl-page-footer-text span").get_text(strip=True)

    print(
        json.dumps(
            {
                "hero_title": hero_title,
                "hero_paragraphs": hero_paragraphs,
                "nav_items": nav_items,
                "achievements": achievements,
                "footer_text": footer_text,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
