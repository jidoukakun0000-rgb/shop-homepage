"""ショップカードの入稿用・確認用PDFを作る(アクセア向け)。

アクセアの名刺入稿の条件: CMYK(RGB不可)、塗り足し3mm、350dpi以上、文字6pt以上、QR 12mm以上。
  - shopcard_final_print.pdf   入稿用。塗り足し込み 61×97mm、CMYK、1枚目表・2枚目裏
  - shopcard_final_preview.pdf 画面確認用。仕上がり 55×91mm、RGB
CMYK への変換は macOS の Generic CMYK プロファイルで行う。色味のない部分(白〜灰〜黒)は
K(黒インク)だけで刷るようにし、黒い文字とQRは K100% にする(4色の版ずれでにじまないように)。

要 img2pdf。 使い方: python3 youkiken/shopcard/make_print_pdf.py
"""
import tempfile
from pathlib import Path

import img2pdf
import numpy as np
from PIL import Image, ImageCms

HERE = Path(__file__).resolve().parent
FRONT, BACK = "front_raimon_final", "back_v4"
CMYK_PROFILE = "/System/Library/ColorSync/Profiles/Generic CMYK Profile.icc"


def to_cmyk(path, xf):
    rgb = Image.open(path).convert("RGB")
    c = np.asarray(ImageCms.applyTransform(rgb, xf)).copy()
    a = np.asarray(rgb).astype(int)
    mx, mn = a.max(axis=2), a.min(axis=2)
    neutral = (mx - mn) < 18
    c[neutral] = 0
    c[..., 3][neutral] = np.clip(255 - a.mean(axis=2), 0, 255)[neutral].astype(np.uint8)
    c[..., 3][neutral & (mx < 70)] = 255
    return Image.fromarray(c, "CMYK")


def main():
    mm = img2pdf.mm_to_pt
    srgb = ImageCms.createProfile("sRGB")
    cmyk = ImageCms.getOpenProfile(CMYK_PROFILE)
    xf = ImageCms.buildTransform(srgb, cmyk, "RGB", "CMYK", renderingIntent=ImageCms.Intent.PERCEPTUAL)
    with tempfile.TemporaryDirectory() as tmp:
        pages = []
        for name in (FRONT, BACK):
            p = Path(tmp) / f"{name}_cmyk.tif"
            to_cmyk(HERE / f"{name}_bleed3mm.png", xf).save(
                p, compression="tiff_deflate", dpi=(800, 800), icc_profile=cmyk.tobytes())
            pages.append(str(p))
        (HERE / "shopcard_final_print.pdf").write_bytes(
            img2pdf.convert(pages, layout_fun=img2pdf.get_layout_fun((mm(61), mm(97)))))
    (HERE / "shopcard_final_preview.pdf").write_bytes(
        img2pdf.convert([str(HERE / f"{FRONT}.png"), str(HERE / f"{BACK}.png")],
                        layout_fun=img2pdf.get_layout_fun((mm(55), mm(91)))))
    print("saved shopcard_final_print.pdf (CMYK) / shopcard_final_preview.pdf")


if __name__ == "__main__":
    main()
