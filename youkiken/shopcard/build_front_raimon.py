"""ショップカード表面に、メニュー表と同じ雷文の枠を付けた版を作る。

元デザイン（front_final_hq.png）はそのまま使い、
- メニュー表 print/variants/menu-a3-r5-raimon-p1.png の雷文を切り出して四辺に敷き詰める
- 下部の「陽気軒」ロックアップ（タグライン・笑顔ロゴ・筆文字）を80%にして上下の余白を揃える
- 笑顔ロゴはトレース済みの print/reference/logo-yohkiken-traced.png があれば差し替える

使い方: python3 youkiken/shopcard/build_front_raimon.py [枠の色 #RRGGBB] [出力名の接尾辞]
  例: python3 youkiken/shopcard/build_front_raimon.py "#1A1A1A" black  → front_raimon_black.png
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
YOUKIKEN = HERE.parent
FRONT = HERE / "front_final_hq.png"
MENU = YOUKIKEN / "print/variants/menu-a3-r5-raimon-p1.png"
LOGO = YOUKIKEN / "print/reference/logo-yohkiken-traced.png"
SUFFIX = f"_{sys.argv[2]}" if len(sys.argv) > 2 else ""
OUT = HERE / f"front_raimon{SUFFIX}.png"
OUT_BLEED = HERE / f"front_raimon{SUFFIX}_bleed3mm.png"

DPI = 800
DPMM = DPI / 25.4
CW, CH = 1732, 2866            # 55×91mm @800dpi
FRAME_HEX = sys.argv[1] if len(sys.argv) > 1 else "#D66420"
FRAME_COLOR = tuple(int(FRAME_HEX.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
MOTIF_H_MM = 2.2               # 雷文の帯の高さ
MOTIF_GAP_MM = 0.37            # 雷文同士の隙間（メニュー表と同じ比率）
EDGE_MM = 1.3                  # カード端から帯まで
INNER_PAD_MM = 1.4             # 帯から中身まで
LOCKUP_SCALE = 0.8
LOCKUP_TOP_PX = 2430           # front_final_hq.png でロックアップが始まる高さ
OLD_LOGO_BOX = (180, 2490, 525, 2815)  # front_final_hq.png の旧ロゴ領域 (x0, y0, x1, y1)
BODY_LOCKUP_GAP_PX = 170
BLEED_MM = 3


def extract_motif():
    """メニュー表の上辺の帯から雷文を1つ切り出し、紙色を透明にして返す。"""
    menu = np.asarray(Image.open(MENU).convert("RGB"))
    r, g, b = (menu[..., i].astype(int) for i in range(3))
    red = (r > 130) & (r - b > 50) & (g < 150)
    rows = red[:400].sum(axis=1)
    band_rows = np.where(rows > 50)[0]
    y0 = band_rows[0]
    y1 = y0
    while y1 + 1 < 400 and rows[y1 + 1] > 50:
        y1 += 1
    cols = np.where(red[y0:y1 + 1].sum(axis=0) > 0)[0]
    segs, start, prev = [], cols[0], cols[0]
    for x in cols[1:]:
        if x - prev > 3:
            segs.append((start, prev))
            start = x
        prev = x
    segs.append((start, prev))
    x0, x1 = segs[len(segs) // 2]
    tile = menu[y0:y1 + 1, x0:x1 + 1].astype(float)
    paper = menu[y0 - 15, (x0 + x1) // 2].astype(float)
    alpha = np.clip(np.abs(tile - paper).sum(axis=2) * 1.2, 0, 255).astype(np.uint8)
    rgb = np.empty(tile.shape, np.uint8)
    rgb[...] = FRAME_COLOR
    return Image.fromarray(np.dstack([rgb, alpha]))


def build_frame(motif):
    th = round(MOTIF_H_MM * DPMM)
    tw0 = round(motif.width * th / motif.height)
    edge = round(EDGE_MM * DPMM)
    gap = round(MOTIF_GAP_MM * DPMM)

    def fit(avail):
        n = max(2, round((avail + gap) / (tw0 + gap)))
        return n, round((avail - (n - 1) * gap) / n)

    frame = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    avail = CW - 2 * edge
    n, tw = fit(avail)
    top = motif.resize((tw, th), Image.LANCZOS)
    bottom = top.transpose(Image.FLIP_TOP_BOTTOM)
    for i in range(n):
        x = edge + round(i * (avail - tw) / (n - 1))
        frame.paste(top, (x, edge), top)
        frame.paste(bottom, (x, CH - edge - th), bottom)

    vstart = edge + th + gap
    availv = CH - 2 * vstart
    nv, twv = fit(availv)
    side = motif.resize((twv, th), Image.LANCZOS)
    left = side.transpose(Image.ROTATE_90)
    right = side.transpose(Image.ROTATE_270)
    for i in range(nv):
        y = vstart + round(i * (availv - twv) / (nv - 1))
        frame.paste(left, (edge, y), left)
        frame.paste(right, (CW - edge - th, y), right)
    return frame, edge + th + round(INNER_PAD_MM * DPMM)


def ink_bbox(arr, thresh):
    g = arr.min(axis=2)
    rows = np.where((g < thresh).sum(axis=1) > 2)[0]
    cols = np.where((g < thresh).sum(axis=0) > 2)[0]
    return rows[0], rows[-1], cols[0], cols[-1]


def main():
    front = Image.open(FRONT).convert("RGB")
    if LOGO.exists():
        x0, y0, x1, y1 = OLD_LOGO_BOX
        arr = np.asarray(front).copy()
        arr[y0:y1, x0:x1] = 255
        front = Image.fromarray(arr)
        size = 315
        logo = Image.open(LOGO).convert("RGB").resize((size, size), Image.LANCZOS)
        front.paste(logo, ((x0 + x1) // 2 - size // 2, (y0 + y1) // 2 - size // 2))
    f = np.asarray(front)

    body = f.copy()
    body[LOCKUP_TOP_PX:] = 255
    r0, r1, c0, c1 = ink_bbox(body, 200)
    art = Image.fromarray(body[r0:r1 + 1, c0:c1 + 1])

    lk = f[LOCKUP_TOP_PX:]
    r0, r1, c0, c1 = ink_bbox(lk, 250)
    lockup = Image.fromarray(lk[r0 - 3:r1 + 4, c0 - 3:c1 + 4])

    frame, inset = build_frame(extract_motif())
    inner_w, inner_h = CW - 2 * inset, CH - 2 * inset

    sc = inner_w / art.width
    aw, ah = round(art.width * sc), round(art.height * sc)
    lw, lh = round(lockup.width * sc * LOCKUP_SCALE), round(lockup.height * sc * LOCKUP_SCALE)
    outer = (inner_h - ah - lh - BODY_LOCKUP_GAP_PX) // 2
    ay = inset + outer

    card = Image.new("RGB", (CW, CH), (255, 255, 255))
    card.paste(art.resize((aw, ah), Image.LANCZOS), ((CW - aw) // 2, ay))
    card.paste(lockup.resize((lw, lh), Image.LANCZOS), ((CW - lw) // 2, ay + ah + BODY_LOCKUP_GAP_PX))
    card.paste(frame, (0, 0), frame)
    card.save(OUT, dpi=(DPI, DPI))

    bleed = round(BLEED_MM * DPMM)
    padded = Image.new("RGB", (CW + 2 * bleed, CH + 2 * bleed), (255, 255, 255))
    padded.paste(card, (bleed, bleed))
    padded.save(OUT_BLEED, dpi=(DPI, DPI))
    print(f"saved {OUT.name} / {OUT_BLEED.name}  (logo {'traced' if LOGO.exists() else 'original'})")


if __name__ == "__main__":
    main()
