"""ショップカード表面に、メニュー表と同じ雷文の枠を付けた版を作る。

元デザイン（front_final_hq.png）はそのまま使い、
- メニュー表 print/variants/menu-a3-r5-raimon-p1.png の雷文を切り出して四辺に敷き詰める
- 下部の「陽気軒」ロックアップ（タグライン・笑顔ロゴ・筆文字）を80%にして上下の余白を揃える
- 笑顔ロゴはトレース済みの print/reference/logo-yohkiken-traced.png があれば差し替える

使い方: python3 youkiken/shopcard/build_front_raimon.py [枠の色 #RRGGBB] [出力名の接尾辞]
  例: python3 youkiken/shopcard/build_front_raimon.py "#1A1A1A" black  → front_raimon_black.png
3つ目以降は key=値 で指定できる:
  edge=3.0   カード端から枠までの距離(mm、既定 1.3。断裁ずれに備えるなら 3.0)
  pad=2.4    枠から中身までの距離(mm、既定 1.4)
  lockup=1.0 下の店名(ロゴ+陽気軒)の大きさ(既定 0.8)
  tag=1.4    ロゴ横のタグラインだけを何倍にするか(既定 1.0。1.4 で約6.5pt。アクセアの推奨は6pt以上)
  tagtype    タグラインをスキャンではなくヒラギノ明朝W6で打ち直す(印刷でぼけないように)
  notag      ロゴ横の小さいタグライン「笑顔こぼれる幸せメニュー」を消す(本文と重複するため)
  例: python3 youkiken/shopcard/build_front_raimon.py "#AC1D20" final edge=3.0 pad=2.4 notag
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
YOUKIKEN = HERE.parent
FRONT = HERE / "front_final_hq.png"
MENU = YOUKIKEN / "print/variants/menu-a3-r5-raimon-p1.png"
LOGO = YOUKIKEN / "print/reference/logo-yohkiken-traced.png"

DPI = 800
DPMM = DPI / 25.4
CW, CH = 1732, 2866            # 55×91mm @800dpi
DEFAULT_FRAME_HEX = "#D66420"
MOTIF_H_MM = 2.2               # 雷文の帯の高さ
MOTIF_GAP_MM = 0.37            # 雷文同士の隙間（メニュー表と同じ比率）
EDGE_MM = 1.3                  # カード端から帯まで
INNER_PAD_MM = 1.4             # 帯から中身まで
LOCKUP_SCALE = 0.8
LOCKUP_TOP_PX = 2430           # front_final_hq.png でロックアップが始まる高さ
OLD_LOGO_BOX = (180, 2490, 525, 2815)  # front_final_hq.png の旧ロゴ領域 (x0, y0, x1, y1)
BODY_LOCKUP_GAP_PX = 170
TAGLINE_BOX = (560, 2445, 1520, 2535)  # front_final_hq.png のロゴ横タグライン
BLEED_MM = 3


def extract_motif(color):
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
    rgb[...] = color
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


TAGLINE = "笑顔こぼれる幸せメニュー"
# 明朝は横線が細く、6pt だとアクセア推奨の線幅 0.1mm を下回るのでゴシックにする
TAG_FONT = ("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc", 0)


def typeset_tagline(ink_height):
    """タグラインを、文字の黒い部分の高さが ink_height px になる大きさで描いて返す(白地)。
    灰色のにじみが出ないよう、白と黒の2値にする(800dpi なのでギザギザは見えない)。"""
    probe = ImageFont.truetype(TAG_FONT[0], 200, index=TAG_FONT[1])
    b = probe.getbbox(TAGLINE)
    size = round(200 * ink_height / (b[3] - b[1]))
    f = ImageFont.truetype(TAG_FONT[0], size, index=TAG_FONT[1])
    b = f.getbbox(TAGLINE)
    im = Image.new("RGB", (b[2] - b[0] + 4, b[3] - b[1] + 4), "white")
    ImageDraw.Draw(im).text((2 - b[0], 2 - b[1]), TAGLINE, font=f, fill=(0, 0, 0))
    return im.convert("L").point(lambda v: 0 if v < 128 else 255).convert("RGB")


def hex_to_rgb(h):
    return tuple(int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))


def main():
    global EDGE_MM, INNER_PAD_MM, LOCKUP_SCALE
    color = hex_to_rgb(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FRAME_HEX)
    opts = sys.argv[3:]
    no_tagline = "notag" in opts
    tag_scale = 1.0
    tag_type = "tagtype" in opts
    tag_box = None
    for o in opts:
        if o.startswith("tag="):
            tag_scale = float(o[4:])
        if o.startswith("edge="):
            EDGE_MM = float(o[5:])
        elif o.startswith("pad="):
            INNER_PAD_MM = float(o[4:])
        elif o.startswith("lockup="):
            LOCKUP_SCALE = float(o[7:])
        elif o.replace(".", "", 1).isdigit():
            EDGE_MM = float(o)
    suffix = f"_{sys.argv[2]}" if len(sys.argv) > 2 else ""
    out = HERE / f"front_raimon{suffix}.png"
    out_bleed = HERE / f"front_raimon{suffix}_bleed3mm.png"
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
    if no_tagline:
        f = f.copy()
        x0, y0, x1, y1 = TAGLINE_BOX
        f[y0:y1, x0:x1] = 255

    body = f.copy()
    body[LOCKUP_TOP_PX:] = 255
    r0, r1, c0, c1 = ink_bbox(body, 200)
    art = Image.fromarray(body[r0:r1 + 1, c0:c1 + 1])

    if tag_scale != 1.0 and not no_tagline:
        # タグラインだけ切り出して拡大し、筆文字「陽気軒」の上に中央そろえで置き直す
        f = f.copy()
        x0, y0, x1, y1 = TAGLINE_BOX
        tg = f[y0:y1, x0:x1]
        tr0, tr1, tc0, tc1 = ink_bbox(tg, 200)
        tag = Image.fromarray(tg[tr0:tr1 + 1, tc0:tc1 + 1].copy())
        f[y0:y1, x0:x1] = 255
        lk = f[LOCKUP_TOP_PX:]
        r0, r1, c0, c1 = ink_bbox(lk, 250)
        base = Image.fromarray(lk[r0 - 3:r1 + 4, c0 - 3:c1 + 4])
        bx0 = OLD_LOGO_BOX[2] - (c0 - 3)          # 筆文字の始まり(ロゴの右)
        bw = base.width - bx0
        th_target = round(tag.height * tag_scale)
        if tag_type:
            # スキャンの文字は輪郭がにじんで印刷でぼけるので打ち直す。ここでは場所だけ空けておき、
            # カードに貼ったあと最終の大きさで直接描く(縮小すると輪郭に灰色が出るため)
            tag = typeset_tagline(th_target)
            tag_box = (bx0 + (bw - tag.width) // 2, 0, tag.width, tag.height)
            tag = Image.new("RGB", tag.size, "white")
        else:
            tag = tag.resize((round(tag.width * tag_scale), th_target), Image.LANCZOS)
        gap = round(tag.height * 0.35)
        lockup = Image.new("RGB", (max(base.width, bx0 + (bw + tag.width) // 2), tag.height + gap + base.height), "white")
        lockup.paste(tag, (bx0 + (bw - tag.width) // 2, 0))
        lockup.paste(base, (0, tag.height + gap))
    else:
        lk = f[LOCKUP_TOP_PX:]
        r0, r1, c0, c1 = ink_bbox(lk, 250)
        lockup = Image.fromarray(lk[r0 - 3:r1 + 4, c0 - 3:c1 + 4])

    frame, inset = build_frame(extract_motif(color))
    inner_w, inner_h = CW - 2 * inset, CH - 2 * inset

    sc = inner_w / art.width
    aw, ah = round(art.width * sc), round(art.height * sc)
    lw, lh = round(lockup.width * sc * LOCKUP_SCALE), round(lockup.height * sc * LOCKUP_SCALE)
    outer = (inner_h - ah - lh - BODY_LOCKUP_GAP_PX) // 2
    ay = inset + outer

    card = Image.new("RGB", (CW, CH), (255, 255, 255))
    card.paste(art.resize((aw, ah), Image.LANCZOS), ((CW - aw) // 2, ay))
    lx, ly = (CW - lw) // 2, ay + ah + BODY_LOCKUP_GAP_PX
    card.paste(lockup.resize((lw, lh), Image.LANCZOS), (lx, ly))
    if tag_box:
        k = sc * LOCKUP_SCALE
        tx, ty, tw, th = tag_box
        sharp = typeset_tagline(round((th - 4) * k))
        card.paste(sharp, (round(lx + (tx + tw / 2) * k - sharp.width / 2), round(ly + (ty + th / 2) * k - sharp.height / 2)))
    card.paste(frame, (0, 0), frame)
    card.save(out, dpi=(DPI, DPI))

    bleed = round(BLEED_MM * DPMM)
    padded = Image.new("RGB", (CW + 2 * bleed, CH + 2 * bleed), (255, 255, 255))
    padded.paste(card, (bleed, bleed))
    padded.save(out_bleed, dpi=(DPI, DPI))
    print(f"saved {out.name} / {out_bleed.name}  (logo {'traced' if LOGO.exists() else 'original'})")


if __name__ == "__main__":
    main()
