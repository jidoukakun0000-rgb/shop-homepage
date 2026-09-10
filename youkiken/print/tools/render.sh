#!/bin/zsh
# 使い方: tools/render.sh variants/menu-a3-r5-raimon.html
# HTML → PDF（Chrome旧ヘッドレス。新ヘッドレスは1ページしか出ない不具合あり）→ 確認用PNG（4面）
set -e
IN="$1"; OUT="${IN%.html}.pdf"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=old --disable-gpu --no-pdf-header-footer --virtual-time-budget=6000 --print-to-pdf="$OUT" "$IN" 2>/dev/null
python3 - "$OUT" <<'PY'
import sys, Quartz, CoreFoundation
src = sys.argv[1]; prefix = src[:-4]
url = CoreFoundation.CFURLCreateWithFileSystemPath(None, src, CoreFoundation.kCFURLPOSIXPathStyle, False)
doc = Quartz.CGPDFDocumentCreateWithURL(url); n = Quartz.CGPDFDocumentGetNumberOfPages(doc)
for i in range(1, n+1):
    pg = Quartz.CGPDFDocumentGetPage(doc, i); box = Quartz.CGPDFPageGetBoxRect(pg, Quartz.kCGPDFMediaBox); s = 1.4
    w, h = int(box.size.width*s), int(box.size.height*s)
    ctx = Quartz.CGBitmapContextCreate(None, w, h, 8, 0, Quartz.CGColorSpaceCreateDeviceRGB(), Quartz.kCGImageAlphaPremultipliedLast)
    Quartz.CGContextSetRGBFillColor(ctx, 1, 1, 1, 1); Quartz.CGContextFillRect(ctx, Quartz.CGRectMake(0, 0, w, h))
    Quartz.CGContextScaleCTM(ctx, s, s); Quartz.CGContextDrawPDFPage(ctx, pg)
    img = Quartz.CGBitmapContextCreateImage(ctx)
    out = CoreFoundation.CFURLCreateWithFileSystemPath(None, f'{prefix}-p{i}.png', CoreFoundation.kCFURLPOSIXPathStyle, False)
    d = Quartz.CGImageDestinationCreateWithURL(out, 'public.png', 1, None)
    Quartz.CGImageDestinationAddImage(d, img, None); Quartz.CGImageDestinationFinalize(d)
print('pages', n)
PY
