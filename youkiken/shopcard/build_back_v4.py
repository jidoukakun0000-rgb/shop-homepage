"""ショップカード裏面(レビューを受けて直した版)。

back_v2_chara からの変更:
  - 営業時間と定休日の2列をやめ、縦に並べて中心をそろえる
  - 明朝の2行をやめ、名物の一行だけをゴシックで(創業は表面にあるので省く)
  - まんぷくボーイを小さくして店名の横へ。下半分はQRだけにする
  - 雷文の帯は入れない(上下とも不要とのこと)。中身は端から5mm以上内側に置く
  - 帯はカード端から3mm内側(断裁ずれ対策)

要 qrcode[pil]。 使い方: python3 youkiken/shopcard/build_back_v4.py
"""
from pathlib import Path

from PIL import Image, ImageDraw

import build_back_v2 as kit
import build_front_raimon as front_kit
from build_back_v2 import CW, CH, DPI, INK, RED, WHITE, gothic, mm, text_center, pill

HERE = Path(__file__).resolve().parent
OUT = HERE / "back_v4.png"
OUT_BLEED = HERE / "back_v4_bleed3mm.png"

# 小さい文字に灰色を使うと、印刷で4色に分かれたり網点になったりしてぼけるので、文字は墨(K100%)だけにする
BAND_EDGE_MM = 3.0      # カード端から帯まで
BAND_H_MM = 1.8         # 帯(雷文)の高さ。表面の 2.2mm より控えめに
BAND_GAP_MM = 0.3
CONTENT_PAD_MM = 3.0    # 帯から中身まで


TOP_BAND = False        # 上の帯(なしに決定)
BOTTOM_BAND = False     # 下の帯(なしに決定)


def raimon_bands(card):
    """雷文の帯(下、TOP_BAND なら上も)。端から端まで、隙間は一定で敷き詰める。
    上の帯を描かないときは、上の余白を帯があるときと同じ位置から始める。"""
    motif = front_kit.extract_motif(RED)
    th = mm(BAND_H_MM)
    tw0 = round(motif.width * th / motif.height)
    gap = mm(BAND_GAP_MM)
    x0 = mm(BAND_EDGE_MM)
    avail = CW - 2 * x0
    n = max(2, round((avail + gap) / (tw0 + gap)))
    tw = round((avail - (n - 1) * gap) / n)
    top = motif.resize((tw, th), Image.LANCZOS)
    bottom = top.transpose(Image.FLIP_TOP_BOTTOM)
    yt, yb = mm(BAND_EDGE_MM), CH - mm(BAND_EDGE_MM) - th
    for i in range(n):
        x = x0 + round(i * (avail - tw) / (n - 1))
        if TOP_BAND:
            card.paste(top, (x, yt), top)
        if BOTTOM_BAND:
            card.paste(bottom, (x, yb), bottom)
    return (yt + th if TOP_BAND else mm(BAND_EDGE_MM + 2.0)), (yb if BOTTOM_BAND else CH - mm(BAND_EDGE_MM + 2.0))


def main():
    card = Image.new("RGB", (CW, CH), WHITE)
    d = ImageDraw.Draw(card)
    scratch = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    cx = CW // 2
    band_top, band_bottom = raimon_bands(card)

    # ---- 店名: ロゴ + 筆文字 + まんぷくボーイを1行に ----
    lh = mm(6.6)
    logo = Image.open(kit.LOGO).convert("RGB").resize((lh, lh), Image.LANCZOS)
    brush = kit.brush_text(INK)
    bh = round(lh * 1.0)
    brush = brush.resize((round(brush.width * bh / brush.height), bh), Image.LANCZOS)
    boy = Image.open(kit.CHARA).convert("RGBA")
    boy_h = round(lh * 1.12)
    boy = boy.resize((round(boy.width * boy_h / boy.height), boy_h), Image.LANCZOS)
    g1, g2 = mm(1.4), mm(1.2)
    head_w = logo.width + g1 + brush.width + g2 + boy.width
    head_h = max(lh, boy_h)
    if head_w > CW - 2 * mm(5.0):
        raise SystemExit(f"店名の行が広すぎます({head_w / mm(1):.1f}mm)")

    def g_head(y, dd):
        if dd is d:
            x = cx - head_w // 2
            card.paste(logo, (x, y + (head_h - lh) // 2))
            x += logo.width + g1
            card.paste(brush, (x, y + (head_h - bh) // 2), brush)
            x += brush.width + g2
            card.paste(boy, (x, y + head_h - boy_h), boy)
        return head_h

    def g_catch(y, dd):
        return text_center(dd, cx, y, "名物ジャンボ餃子と自家製麺", gothic(6, mm(2.15)), RED)

    def g_tel(y, dd):
        h = text_center(dd, cx, y, "TEL", gothic(6, mm(2.1)), RED) + mm(0.8)
        return h + text_center(dd, cx, y + h, "027-387-7082", gothic(7, mm(4.3)), INK)

    def g_hours(y, dd):
        # 閉店時刻は日によって違うので書かない(店主の案: 11時から品切れまで)
        h = pill(dd, cx, y, "営業時間", gothic(6, mm(2.15)), RED, WHITE) + mm(1.1)
        h += text_center(dd, cx, y + h, "11:00〜 品切れ次第終了", gothic(7, mm(2.9)), INK)
        return h

    def g_closed(y, dd):
        h = pill(dd, cx, y, "定休日", gothic(6, mm(2.15)), RED, WHITE) + mm(1.1)
        return h + text_center(dd, cx, y + h, "毎月15日・26日", gothic(7, mm(2.9)), INK)

    def g_address(y, dd):
        h = text_center(dd, cx, y, "〒370-2134", gothic(5, mm(2.15)), INK) + mm(0.9)
        return h + text_center(dd, cx, y + h, "群馬県高崎市吉井町塩川37-4", gothic(6, mm(2.6)), INK)

    q = mm(13.5)
    lbl_f = gothic(6, mm(2.1))
    q_gap = mm(9.0)

    def g_qr(y, dd):
        b = scratch.textbbox((0, 0), "@youkiken_", font=lbl_f)
        th = b[3] - b[1]
        if dd is d:
            for i, (url, icon, label) in enumerate(((kit.INSTA_URL, kit.icon_instagram_color, "@youkiken_"),
                                                     (kit.HP_URL, kit.icon_home, "youkiken.com"))):
                x = cx - q_gap // 2 - q + i * (q + q_gap)
                card.paste(kit.make_qr(url, q, INK, icon), (x, y))
                ly, qcx = y + q + mm(1.3), x + q // 2
                if icon is kit.icon_instagram_color:
                    lb = d.textbbox((0, 0), label, font=lbl_f)
                    lw = lb[2] - lb[0]
                    isz, igap = round(th * 1.3), mm(0.7)
                    x0 = qcx - (isz + igap + lw) // 2
                    ig = kit.icon_instagram_color(isz)
                    card.paste(ig, (x0, ly + (th - isz) // 2), ig)
                    d.text((x0 + isz + igap - lb[0], ly - lb[1]), label, font=lbl_f, fill=INK)
                else:
                    text_center(d, qcx, ly, label, lbl_f, INK)
        return q + mm(1.3) + th

    groups = [g_head, g_catch, g_tel, g_hours, g_closed, g_address, g_qr]
    # 店名と名物の行はひとまとまり(間は詰める)、それ以外は同じ間隔
    tight = {1}
    heights = [g(0, scratch) for g in groups]
    top = band_top + mm(CONTENT_PAD_MM)
    bottom = band_bottom - mm(CONTENT_PAD_MM)
    tight_gap = mm(1.6)
    n_loose = len(groups) - 1 - len(tight)
    step = (bottom - top - sum(heights) - tight_gap * len(tight)) / n_loose
    if step < mm(2.5):
        raise SystemExit(f"収まりません(まとまりの間隔 {step / mm(1):.1f}mm)")
    y = top
    for i, (g, h) in enumerate(zip(groups, heights)):
        if i:
            y += tight_gap if i in tight else step
        g(round(y), d)
        y += h

    card.save(OUT, dpi=(DPI, DPI))
    bleed = mm(3)
    padded = Image.new("RGB", (CW + 2 * bleed, CH + 2 * bleed), WHITE)
    padded.paste(card, (bleed, bleed))
    padded.save(OUT_BLEED, dpi=(DPI, DPI))
    print(f"saved {OUT.name}  (まとまりの間隔 {step / mm(1):.1f}mm)")


if __name__ == "__main__":
    main()
