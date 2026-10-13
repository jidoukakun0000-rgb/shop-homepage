"""ショップカード裏面に、ホームページ(youkiken.com)のQRコードを足した版を作る。

back_final_hq.png の既存のInstagram QR(ラベル込み)を左へ寄せ、
右に同じ大きさでホームページのQRと「youkiken.com」のラベルを並べる。
上の文章(電話・営業時間・定休日・住所)は動かさない。

要 qrcode[pil]。 使い方: python3 youkiken/shopcard/build_back_qr.py
"""
from pathlib import Path

import numpy as np
import qrcode
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SRC = HERE / "back_final_hq.png"
OUT = HERE / "back_qr2.png"
OUT_BLEED = HERE / "back_qr2_bleed3mm.png"

DPI = 800
DPMM = DPI / 25.4
HP_URL = "https://youkiken.com/"
HP_LABEL = "youkiken.com"
BROWN = (93, 63, 62)           # 裏面の文字の茶色(実測)
FONT = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"

# back_final_hq.png 上のInstagram QRブロック(QR本体とラベル)
INSTA_BOX = (610, 2228, 1110, 2810)   # x0, y0, x1, y1
INSTA_QR = (626, 2237, 1092, 2703)    # QR本体の外接矩形
COL_GAP_MM = 5.0
BLEED_MM = 3


def make_hp_qr(size):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=0, box_size=10)
    qr.add_data(HP_URL)
    qr.make(fit=True)
    img = qr.make_image(fill_color=BROWN, back_color="white").convert("RGB")
    return img.resize((size, size), Image.NEAREST)


def main():
    card = Image.open(SRC).convert("RGB")
    cw, ch = card.size
    insta = card.crop(INSTA_BOX)

    # 既存のQRブロックがあった帯(と左右の細かいゴミ)を白で消す
    ImageDraw.Draw(card).rectangle((0, INSTA_BOX[1], cw, INSTA_BOX[3]), fill="white")

    qr_size = INSTA_QR[2] - INSTA_QR[0]
    gap = round(COL_GAP_MM * DPMM)
    # QR本体どうしの間隔を gap にして、2つの組をカード中央に置く
    qr_offset = INSTA_QR[0] - INSTA_BOX[0]
    total = qr_size * 2 + gap
    left_qr_x = (cw - total) // 2
    right_qr_x = left_qr_x + qr_size + gap
    top = INSTA_BOX[1]
    card.paste(insta, (left_qr_x - qr_offset, top))

    qr_y = INSTA_QR[1]
    card.paste(make_hp_qr(qr_size), (right_qr_x, qr_y))

    # ラベル: Instagram側のラベルと同じ高さ帯・同じくらいの字の大きさで中央揃え
    draw = ImageDraw.Draw(card)
    font = ImageFont.truetype(FONT, 62)
    bbox = draw.textbbox((0, 0), HP_LABEL, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    label_mid_y = (2744 + 2800) // 2
    draw.text((right_qr_x + (qr_size - tw) // 2 - bbox[0], label_mid_y - th // 2 - bbox[1]),
              HP_LABEL, font=font, fill=BROWN)

    card.save(OUT, dpi=(DPI, DPI))
    bleed = round(BLEED_MM * DPMM)
    padded = Image.new("RGB", (cw + 2 * bleed, ch + 2 * bleed), "white")
    padded.paste(card, (bleed, bleed))
    padded.save(OUT_BLEED, dpi=(DPI, DPI))
    print(f"saved {OUT.name} / {OUT_BLEED.name}  (QR {qr_size}px = {qr_size / DPMM:.1f}mm, gap {COL_GAP_MM}mm)")


if __name__ == "__main__":
    main()
