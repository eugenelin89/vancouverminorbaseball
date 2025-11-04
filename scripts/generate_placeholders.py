from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from home.content import ACHIEVEMENTS

IMAGE_DIR = BASE_DIR / "static" / "images"

PALETTE = [
    "#1b4f91",
    "#0a1f44",
    "#f7b733",
    "#e1efff",
]


def create_image(path: Path, size: tuple[int, int], lines: list[str], fill: str, text_color: str):
    image = Image.new("RGB", size, color=fill)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    heights = []
    widths = []
    for line in lines:
        left, top, right, bottom = font.getbbox(line)
        widths.append(right - left)
        heights.append(bottom - top)

    total_height = sum(heights) + (len(lines) - 1) * 12
    y = (size[1] - total_height) // 2

    for line, height, width in zip(lines, heights, widths):
        x = (size[0] - width) // 2
        draw.text((x, y), line, font=font, fill=text_color)
        y += height + 12

    image.save(path)


def main():
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    hero_lines = ["Hero Banner", "hero-banner.jpg", "Replace with feature photo"]
    create_image(
        IMAGE_DIR / "hero-banner.jpg",
        (1600, 600),
        hero_lines,
        PALETTE[0],
        "#ffffff",
    )

    create_image(
        IMAGE_DIR / "logo.png",
        (400, 400),
        ["Team Logo", "logo.png"],
        PALETTE[2],
        "#0a1f44",
    )

    for index, achievement in enumerate(ACHIEVEMENTS, start=1):
        slug = achievement["slug"]
        filename = f"{slug}.png"
        lines = [
            f"{slug}.png",
            "Replace with highlight photo",
        ]
        palette_index = index % len(PALETTE)
        create_image(
            IMAGE_DIR / filename,
            (1024, 768),
            lines,
            PALETTE[palette_index],
            "#0a1f44" if palette_index in {0, 3} else "#ffffff",
        )


if __name__ == "__main__":
    main()
