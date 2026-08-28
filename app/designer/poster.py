from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from itertools import pairwise
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from app.schemas import ComponentStatus, DesignPackage, DesignRenderManifest

PAPER = (241, 237, 226)
PAPER_LIGHT = (250, 248, 241)
INK = (20, 29, 42)
INDIGO = (24, 43, 68)
INDIGO_LIGHT = (49, 70, 95)
THREAD_RED = (188, 55, 49)
THREAD_WHITE = (236, 230, 213)
MUTED = (102, 105, 106)
LINE = (202, 195, 179)
METAL = (74, 80, 84)


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf" if bold else "C:/Windows/Fonts/simsun.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" if bold else "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default(size=size)


def _text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> float:
    return draw.textlength(text, font=font)


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in str(text).splitlines() or [""]:
        current = ""
        for character in paragraph:
            candidate = current + character
            if current and _text_width(draw, candidate, font) > width:
                lines.append(current.rstrip())
                current = character.lstrip()
            else:
                current = candidate
        if current:
            lines.append(current.rstrip())
        elif not paragraph:
            lines.append("")
    return lines


def _draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    width: int,
    line_height: int,
    max_lines: int | None = None,
) -> int:
    lines = _wrap(draw, text, font, width)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while last and _text_width(draw, last + "…", font) > width:
            last = last[:-1]
        lines[-1] = last + "…"
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height
    return y


def _panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fill: tuple[int, int, int] = PAPER_LIGHT,
    outline: tuple[int, int, int] = LINE,
    radius: int = 24,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2)


def _section_label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], index: str, title: str) -> None:
    x, y = xy
    title_font = _font(28, True)
    title_width = int(_text_width(draw, title, title_font))
    draw.rounded_rectangle(
        (x + 68, y - 3, x + 96 + title_width, y + 45),
        radius=18,
        fill=PAPER_LIGHT,
    )
    draw.rounded_rectangle((x, y, x + 64, y + 42), radius=20, fill=THREAD_RED)
    draw.text((x + 17, y + 7), index, font=_font(20, True), fill=PAPER_LIGHT)
    draw.text((x + 82, y + 2), title, font=title_font, fill=INK)


def _paste_hero(canvas: Image.Image, package: DesignPackage, box: tuple[int, int, int, int], hero: Path | None) -> None:
    x1, y1, x2, y2 = box
    if hero and hero.exists():
        source = Image.open(hero).convert("RGB")
        fitted = ImageOps.fit(source, (x2 - x1, y2 - y1), method=Image.Resampling.LANCZOS)
        mask = Image.new("L", fitted.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle((0, 0, fitted.width, fitted.height), radius=34, fill=255)
        canvas.paste(fitted, (x1, y1), mask)
        return
    _draw_placeholder_product(canvas, package, box)


def _draw_placeholder_product(
    canvas: Image.Image,
    package: DesignPackage,
    box: tuple[int, int, int, int],
) -> None:
    x1, y1, x2, y2 = box
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    cx = (x1 + x2) // 2
    body_w = min(500, (x2 - x1) * 3 // 5)
    body_h = min(670, (y2 - y1) * 3 // 4)
    body_x1 = cx - body_w // 2
    body_y1 = y1 + (y2 - y1 - body_h) // 2 + 35
    body_box = (body_x1, body_y1, body_x1 + body_w, body_y1 + body_h)
    shadow = (body_x1 - 25, body_y1 + body_h - 20, body_x1 + body_w + 25, body_y1 + body_h + 35)
    draw.ellipse(shadow, fill=(10, 20, 30, 45))
    draw.rounded_rectangle(body_box, radius=body_w // 2, fill=INDIGO + (255,), outline=INDIGO_LIGHT + (255,), width=5)
    loop_x = cx - 34
    draw.rounded_rectangle((loop_x, body_y1 - 70, loop_x + 68, body_y1 + 20), radius=26, outline=METAL + (255,), width=18)
    draw.arc((cx - 52, body_y1 - 130, cx + 52, body_y1 - 30), 190, 350, fill=METAL + (255,), width=16)
    panel = (
        body_x1 + 75,
        body_y1 + 125,
        body_x1 + body_w - 75,
        body_y1 + body_h - 125,
    )
    draw.rounded_rectangle(panel, radius=42, fill=(31, 52, 76, 255), outline=THREAD_WHITE + (255,), width=4)
    px1, py1, px2, py2 = panel
    for offset in range(5):
        y = py1 + 65 + offset * 52
        draw.line((px1 + 45, y, px2 - 45, y + (18 if offset % 2 else -12)), fill=THREAD_RED + (255,), width=9)
    for offset in range(4):
        x = px1 + 70 + offset * 65
        draw.line((x, py1 + 50, x + 24, py2 - 50), fill=THREAD_WHITE + (255,), width=5)
    layer = layer.filter(ImageFilter.GaussianBlur(0.35))
    canvas.alpha_composite(layer)
    draw_canvas = ImageDraw.Draw(canvas)
    label = "本地结构预览" if "毛绒" in package.product.product_type else "概念结构预览"
    draw_canvas.rounded_rectangle((x1 + 28, y2 - 66, x1 + 218, y2 - 24), radius=18, fill=PAPER_LIGHT + (230,))
    draw_canvas.text((x1 + 48, y2 - 58), label, font=_font(20, True), fill=INK)


def _draw_exploded(
    draw: ImageDraw.ImageDraw,
    package: DesignPackage,
    box: tuple[int, int, int, int],
) -> None:
    x1, y1, x2, _ = box
    colors = [INDIGO, (40, 62, 86), THREAD_RED, (221, 216, 203), METAL, (55, 55, 58)]
    parts = package.manufacturing.bill_of_materials[:6]
    gap = (x2 - x1 - 120) // max(1, len(parts))
    base_y = y1 + 125
    centers: list[tuple[int, int]] = []
    for index, item in enumerate(parts):
        cx = x1 + 70 + index * gap
        cy = base_y + (index % 2) * 45
        centers.append((cx, cy))
        width = 112 if index < 3 else 76
        height = 142 if index < 3 else 88
        draw.rounded_rectangle(
            (cx - width // 2, cy - height // 2, cx + width // 2, cy + height // 2),
            radius=width // 3,
            fill=colors[index % len(colors)],
            outline=PAPER_LIGHT,
            width=3,
        )
        if index == 2:
            for stripe in range(3):
                yy = cy - 34 + stripe * 30
                draw.line((cx - 35, yy, cx + 35, yy + 8), fill=THREAD_WHITE, width=5)
        draw.ellipse((cx - 22, y1 + 250, cx + 22, y1 + 294), fill=THREAD_RED)
        draw.text((cx - 11, y1 + 258), str(index + 1), font=_font(18, True), fill=PAPER_LIGHT)
        _draw_wrapped(
            draw,
            (cx - 56, y1 + 307),
            f"{item.part_id}\n{item.component}",
            _font(18, True),
            INK,
            112,
            27,
            3,
        )
    for start, end in pairwise(centers):
        draw.line((start[0] + 55, start[1], end[0] - 55, end[1]), fill=THREAD_RED, width=3)


def _draw_bom(draw: ImageDraw.ImageDraw, package: DesignPackage, box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, _ = box
    col_x = [x1 + 24, x1 + 105, x1 + 340, x1 + 690]
    header_height = 34
    row_height = 36
    draw.rectangle((x1, y1, x2, y1 + header_height), fill=INDIGO)
    headers = ("ID", "部件", "材料 / 规格", "首样目标")
    for x, header in zip(col_x, headers):
        draw.text((x, y1 + 5), header, font=_font(15, True), fill=PAPER_LIGHT)
    row_y = y1 + header_height
    for index, item in enumerate(package.manufacturing.bill_of_materials[:6]):
        fill = PAPER_LIGHT if index % 2 == 0 else (244, 241, 232)
        draw.rectangle(
            (x1, row_y, x2, row_y + row_height),
            fill=fill,
            outline=LINE,
            width=1,
        )
        values = (item.part_id, item.component, f"{item.material}；{item.specification}", item.tolerance_or_target)
        widths = (70, 220, 330, x2 - col_x[3] - 18)
        for x, value, width in zip(col_x, values, widths):
            _draw_wrapped(draw, (x, row_y + 3), value, _font(11), INK, width, 15, 2)
        row_y += row_height


def render_design_poster(
    package: DesignPackage,
    output_path: Path,
    hero_asset_path: Path | None = None,
) -> tuple[DesignRenderManifest, ComponentStatus]:
    width = package.poster_request.canvas_width_px
    height = package.poster_request.canvas_height_px
    canvas = Image.new("RGBA", (width, height), PAPER + (255,))
    draw = ImageDraw.Draw(canvas)

    # A subtle counted-thread grid is a generic layout device, not a copied motif.
    for x in range(0, width, 48):
        draw.line((x, 0, x, height), fill=(224, 219, 205, 95), width=1)
    for y in range(0, height, 48):
        draw.line((0, y, width, y), fill=(224, 219, 205, 95), width=1)

    draw.rectangle((0, 0, width, 250), fill=INDIGO)
    draw.rectangle((90, 74, 105, 184), fill=THREAD_RED)
    draw.text((140, 62), package.product.product_name.split("｜")[0], font=_font(76, True), fill=PAPER_LIGHT)
    subtitle = package.poster_request.exact_copy.get("subtitle", package.product.product_type)
    draw.text((144, 164), subtitle, font=_font(28), fill=THREAD_WHITE)
    draw.text((width - 390, 70), "QIANCRAFT / DESIGN 01", font=_font(22, True), fill=THREAD_WHITE)
    draw.text((width - 390, 110), package.design_id, font=_font(17), fill=(178, 188, 196))

    hero_box = (90, 320, 1120, 1390)
    _panel(draw, hero_box, fill=(230, 226, 214), outline=LINE, radius=34)
    _paste_hero(canvas, package, (110, 340, 1100, 1370), hero_asset_path)
    draw = ImageDraw.Draw(canvas)
    _section_label(draw, (120, 360), "01", "成品主视觉")

    culture_box = (1160, 320, 1710, 775)
    _panel(draw, culture_box)
    _section_label(draw, (1190, 350), "02", "文化元素 / 风格")
    element = package.cultural_elements[0]
    y = 425
    y = _draw_wrapped(draw, (1190, y), element.name, _font(34, True), INDIGO, 470, 44, 2) + 12
    y = _draw_wrapped(draw, (1190, y), f"地域｜{element.region}", _font(19, True), THREAD_RED, 470, 29, 2) + 10
    y = _draw_wrapped(draw, (1190, y), element.transformation_rule, _font(20), INK, 470, 31, 5) + 12
    _draw_wrapped(draw, (1190, y), "风格｜" + " / ".join(package.product.visual_style), _font(18), MUTED, 470, 28, 4)

    spec_box = (1160, 815, 1710, 1390)
    _panel(draw, spec_box)
    _section_label(draw, (1190, 845), "03", "尺寸 / 用料")
    y = 925
    for item in package.product.dimensions[:5]:
        draw.ellipse((1193, y + 8, 1203, y + 18), fill=THREAD_RED)
        y = _draw_wrapped(
            draw,
            (1220, y),
            f"{item.item}  {item.value_mm:g}±{item.tolerance_mm:g} mm",
            _font(18),
            INK,
            450,
            28,
            2,
        ) + 7
    y += 8
    _draw_wrapped(draw, (1190, y), f"重量｜{package.product.target_weight_g}", _font(18, True), INDIGO, 470, 28, 2)
    y += 58
    _draw_wrapped(
        draw,
        (1190, y),
        "材料｜" + " / ".join(item.material for item in package.manufacturing.bill_of_materials[:5]),
        _font(18),
        MUTED,
        470,
        28,
        5,
    )

    explode_box = (90, 1450, 1120, 1940)
    _panel(draw, explode_box)
    _section_label(draw, (120, 1480), "04", "爆炸拆解 / COMPONENTS")
    _draw_exploded(draw, package, (130, 1540, 1080, 1910))

    process_box = (1160, 1450, 1710, 1940)
    _panel(draw, process_box)
    _section_label(draw, (1190, 1480), "05", "工艺路径")
    y = 1550
    for index, step in enumerate(package.manufacturing.assembly_steps[:6], 1):
        draw.ellipse((1190, y, 1224, y + 34), fill=INDIGO)
        draw.text((1200, y + 5), str(index), font=_font(15, True), fill=PAPER_LIGHT)
        y = _draw_wrapped(draw, (1240, y), step, _font(17), INK, 430, 25, 2) + 12

    bom_box = (90, 2000, 1710, 2390)
    _panel(draw, bom_box, radius=22)
    _section_label(draw, (120, 2025), "06", "BOM / 首样规格（前6项，完整表见JSON）")
    _draw_bom(draw, package, (120, 2085, 1680, 2390))

    footer_y = height - 42
    footer = "概念视觉与工厂首样/报价输入｜不是量产定稿｜社区授权、工程与合规复核未完成"
    draw.rectangle((0, footer_y - 14, width, height), fill=INK)
    draw.text((90, footer_y), footer, font=_font(17), fill=PAPER_LIGHT, anchor="lm")
    draw.text((width - 90, footer_y), package.input_contract.source_sha256[:12], font=_font(15), fill=(174, 181, 186), anchor="rm")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    rgb = canvas.convert("RGB")
    rgb.save(output_path, format="PNG", optimize=True, dpi=(150, 150))
    hero_path = hero_asset_path.resolve() if hero_asset_path and hero_asset_path.exists() else None
    engine = (
        "QianCraft exact-text compositor + generated hero asset"
        if hero_path
        else "QianCraft exact-text local concept renderer"
    )
    manifest = DesignRenderManifest(
        design_id=package.design_id,
        rendered_at=datetime.now(UTC),
        engine=engine,
        poster_path=str(output_path.resolve()),
        poster_sha256=_hash(output_path),
        hero_asset_path=str(hero_path) if hero_path else "",
        hero_asset_sha256=_hash(hero_path) if hero_path else "",
        width_px=width,
        height_px=height,
        notes=[
            "Chinese labels are rendered locally for exact spelling.",
            "Museum reference-only images were not used.",
            "Dimensions are prototype targets, not production drawings.",
        ],
    )
    status = ComponentStatus(
        component="poster_renderer",
        mode="live" if hero_path else "cache",
        engine=engine,
        ok=True,
        detail=(
            "已合成成品主视觉、文化元素、爆炸拆解、BOM和工艺路径；"
            + ("使用项目内生成式主视觉素材。" if hero_path else "当前使用本地结构预览。")
        ),
    )
    return manifest, status
