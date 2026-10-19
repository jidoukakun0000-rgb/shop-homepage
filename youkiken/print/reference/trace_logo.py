"""陽気軒の笑顔ロゴを看板の写真から正方形・3色ベタ塗りに起こす。

入力: logo-yohkiken-photo.jpg（看板の写真）  出力: logo-yohkiken-traced.png（1200×1200）
写真の台形歪みを透視変換で正方形にし、照明ムラを除いて臙脂・黄金・白の3色に分ける。
要 opencv-python-headless。 使い方: python3 youkiken/print/reference/trace_logo.py
"""
import sys, os, tempfile
import numpy as np, cv2
from PIL import Image, ImageOps

S = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(S, 'logo-yohkiken-photo.jpg')
OUT = os.path.join(S, 'logo-yohkiken-traced.png')
# 途中経過と比較画像はリポジトリを汚さないよう一時フォルダへ
DEBUG = os.path.join(tempfile.gettempdir(), 'trace_logo_debug')
os.makedirs(DEBUG, exist_ok=True)
PREVIEW = os.path.join(DEBUG, 'logo-yohkiken-traced-preview.png')

pil = ImageOps.exif_transpose(Image.open(SRC)).convert('RGB')
rgb = np.array(pil)
bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
H, W = rgb.shape[:2]

def classify(warp, tag):
    # ---- 2. illumination flattening ----
    # Global Gaussian illumination estimate. To avoid the red/gold mix biasing the
    # estimate, it is computed by normalized convolution over the dominant gold ground.
    f = warp.astype(np.float32)
    lab0 = cv2.cvtColor(warp, cv2.COLOR_BGR2LAB).astype(np.float32)
    chroma0 = np.hypot(lab0[..., 1] - 128, lab0[..., 2] - 128)
    gold0 = (lab0[..., 2] > 165) & (lab0[..., 1] < 150) & (lab0[..., 0] > 100)
    gold0 = cv2.erode(gold0.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(np.float32)
    SIG = 120
    den = cv2.GaussianBlur(gold0, (0, 0), SIG) + 1e-6
    illum = np.stack([cv2.GaussianBlur(f[..., k] * gold0, (0, 0), SIG) / den for k in range(3)], -1)
    ref = np.array([np.median(f[..., k][gold0 > 0]) for k in range(3)], np.float32)
    # use luminance-only gain so hue is preserved
    Ill = illum.mean(-1, keepdims=True); gain = ref.mean() / np.maximum(Ill, 1)
    flat = np.clip(f * gain, 0, 255).astype(np.uint8)
    cv2.imwrite(os.path.join(DEBUG, f'step3_flat_{tag}.png'), flat)

    lab = cv2.cvtColor(flat, cv2.COLOR_BGR2LAB).astype(np.float32)
    chroma = np.hypot(lab[..., 1] - 128, lab[..., 2] - 128)
    pal_rgb = np.array([[172, 29, 32], [240, 187, 41], [253, 251, 247]], np.uint8)
    red_m = (lab[..., 1] > 160) & (lab[..., 0] < 110)
    gold_m = (lab[..., 2] > 165) & (lab[..., 1] < 150)
    white_m = (chroma < 25) & (lab[..., 0] > 150)
    centers = np.array([np.median(lab[m], 0) for m in (red_m, gold_m, white_m)], np.float32)
    print('class pixel counts:', [int(m.sum()) for m in (red_m, gold_m, white_m)])
    print('Lab centers:', centers.round(1).tolist())

    dist = np.stack([np.sqrt(((lab - centers[k]) ** 2).sum(-1)) for k in range(3)], -1)
    dist = np.stack([cv2.GaussianBlur(dist[..., k], (0, 0), 2.0) for k in range(3)], -1)
    cls = dist.argmin(-1).astype(np.uint8)

    # ---- small component removal ----
    MINA = 350
    for it in range(2):
        for k in range(3):
            m = (cls == k).astype(np.uint8)
            n, lab_cc, stats, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
            for j in range(1, n):
                if stats[j, cv2.CC_STAT_AREA] < MINA:
                    x, y, w, h, a = stats[j]
                    x0, y0 = max(x - 3, 0), max(y - 3, 0)
                    x1, y1 = min(x + w + 3, N), min(y + h + 3, N)
                    comp = lab_cc[y0:y1, x0:x1] == j
                    ring = cv2.dilate(comp.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & ~comp
                    vals = cls[y0:y1, x0:x1][ring]
                    vals = vals[vals != k] if (vals != k).any() else vals
                    cls[y0:y1, x0:x1][comp] = np.bincount(vals, minlength=3).argmax()
    cv2.imwrite(os.path.join(DEBUG, f'step4_cls_{tag}.png'), pal_rgb[cls][..., ::-1])

    return cls

# ---- 1. corner detection ----
hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
sat = (hsv[..., 1] > 90).astype(np.uint8) * 255
sat = cv2.morphologyEx(sat, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
sat = cv2.morphologyEx(sat, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
cnts, _ = cv2.findContours(sat, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
c = max(cnts, key=cv2.contourArea)
hull = cv2.convexHull(c)
peri = cv2.arcLength(hull, True)
quad = None
for eps in np.linspace(0.005, 0.1, 200):
    a = cv2.approxPolyDP(hull, eps * peri, True)
    if len(a) == 4:
        quad = a.reshape(4, 2).astype(np.float32)
        break
assert quad is not None
# order TL, TR, BR, BL
s = quad.sum(1); d = quad[:, 0] - quad[:, 1]
tl = quad[np.argmin(s)]; br = quad[np.argmax(s)]
tr = quad[np.argmax(d)]; bl = quad[np.argmin(d)]
pts = np.array([tl, tr, br, bl], np.float32)
names = ['top', 'right', 'bottom', 'left']
for i, n in enumerate(names):
    print(f'{n}: {np.linalg.norm(pts[(i+1)%4]-pts[i]):.1f}px')
print('corners TL,TR,BR,BL:', pts.round(1).tolist())

dbg = bgr.copy()
cv2.polylines(dbg, [pts.astype(np.int32)], True, (255, 0, 0), 8)
for p in pts:
    cv2.circle(dbg, tuple(int(v) for v in p), 30, (0, 255, 0), 6)
cv2.imwrite(os.path.join(DEBUG, 'step1_corners.png'), cv2.resize(dbg, (W // 4, H // 4)))

N = 2400
dst = np.array([[0, 0], [N - 1, 0], [N - 1, N - 1], [0, N - 1]], np.float32)
M = cv2.getPerspectiveTransform(pts, dst)

pal_rgb = np.array([[172, 29, 32], [240, 187, 41], [253, 251, 247]], np.uint8)
warp = cv2.warpPerspective(bgr, M, (N, N), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
cv2.imwrite(os.path.join(DEBUG, 'step2_warp_pass1.png'), warp)
cls1 = classify(warp, 'pass1')

# ---- 1b. refine homography with the inner frame bars ----
# The outer edge in the photo includes the plate's visible side at the bottom, which
# skews the 4-corner homography. The long inner frame bars are straight and (by design)
# equidistant from all four outer edges, so fit their outer edges and square them up.
def fit_edge(cls, horizontal, rng, scan, before, after):
    pts = []
    for t in rng:
        v = cls[scan[0]:scan[1], t] if horizontal else cls[t, scan[0]:scan[1]]
        idx = np.where((v[:-1] == before) & (v[1:] == after))[0]
        if len(idx):
            pts.append((t, scan[0] + idx[0] + 1))
    q = np.array(pts, float)
    for _ in range(3):  # robust refit
        a_, b_ = np.polyfit(q[:, 0], q[:, 1], 1)
        r = q[:, 1] - (a_ * q[:, 0] + b_)
        q = q[np.abs(r) < max(2.0, 2.5 * r.std())]
    return a_, b_, len(q)
R_, G_ = 0, 1
xs = [x for x in range(450, 1950, 8) if not 1120 < x < 1300]
ys = [y for y in range(450, 1950, 8) if not 1080 < y < 1300]
top = fit_edge(cls1, True, xs, (130, 260), G_, R_)      # y = a x + b
bot = fit_edge(cls1, True, xs, (2140, 2290), R_, G_)
lef = fit_edge(cls1, False, ys, (130, 260), G_, R_)     # x = a y + b
rig = fit_edge(cls1, False, ys, (2140, 2290), R_, G_)
print('inner-bar edge fits (slope, offset, n):', [tuple(round(v, 4) for v in e) for e in (top, bot, lef, rig)])
def isect(h, v):
    # y = ah x + bh ; x = av y + bv
    ah, bh, _ = h; av, bv, _ = v
    y = (ah * bv + bh) / (1 - ah * av); x = av * y + bv
    return [x, y]
src = np.array([isect(top, lef), isect(top, rig), isect(bot, rig), isect(bot, lef)], np.float32)
d = np.mean([src[0, 0], src[0, 1], N - src[2, 0], N - src[2, 1], src[3, 0], N - src[3, 1], N - src[1, 0], src[1, 1]])
print('inner frame corners (pass1):', src.round(1).tolist(), 'target inset', round(float(d), 1))
dst2 = np.array([[d, d], [N - d, d], [N - d, N - d], [d, N - d]], np.float32)
H2 = cv2.getPerspectiveTransform(src, dst2)
M2 = H2 @ M
pts_ref = cv2.perspectiveTransform(dst.reshape(-1, 1, 2), np.linalg.inv(M2)).reshape(-1, 2)
print('refined outer corners in photo TL,TR,BR,BL:', pts_ref.round(1).tolist())
for i, n in enumerate(names):
    print(f'  refined {n}: {np.linalg.norm(pts_ref[(i+1)%4]-pts_ref[i]):.1f}px')
dbg2 = bgr.copy()
cv2.polylines(dbg2, [pts.astype(np.int32)], True, (255, 0, 0), 6)
cv2.polylines(dbg2, [pts_ref.astype(np.int32)], True, (0, 200, 0), 6)
cv2.imwrite(os.path.join(DEBUG, 'step1b_corners_refined.png'), cv2.resize(dbg2, (W // 4, H // 4)))

warp = cv2.warpPerspective(bgr, M2, (N, N), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
cv2.imwrite(os.path.join(DEBUG, 'step2_warp.png'), warp)
cls = classify(warp, 'final')

# ---- glare removal inside the face ----
# A specular highlight on the glossy face survives as a gold/white island > 350px.
# Islands of non-red that are fully enclosed by red and lie inside the face disc
# (except the three big white strokes: eyes and mouth) are reset to red.
gold = (cls == G_)
pts_c = []
for ang in np.radians(np.r_[125:270:1.0, -90:-62:1.0]):
    for r in range(400, 800):
        x = int(round(990 + r * np.cos(ang))); y = int(round(1000 + r * np.sin(ang)))
        if gold[y, x]:
            pts_c.append((x, y)); break
q = np.array(pts_c, float)
A = np.c_[2 * q[:, 0], 2 * q[:, 1], np.ones(len(q))]
fx, fy, k = np.linalg.lstsq(A, (q ** 2).sum(1), rcond=None)[0]; FR = np.sqrt(k + fx * fx + fy * fy)
(ex, ey), (ew, eh), eang = cv2.fitEllipse(q.astype(np.float32))
print(f'face circle c=({fx:.1f},{fy:.1f}) R={FR:.1f}; ellipse axes {ew:.1f} x {eh:.1f} (ratio {max(ew,eh)/min(ew,eh):.4f})')
yy, xx = np.mgrid[0:N, 0:N]
disc = (xx - fx) ** 2 + (yy - fy) ** 2 < (0.92 * FR) ** 2
nonred = (cls != R_).astype(np.uint8)
n, lab_cc, stats, _ = cv2.connectedComponentsWithStats(nonred, connectivity=8)
for j in range(1, n):
    comp = lab_cc == j
    if stats[j, cv2.CC_STAT_AREA] < 60000 and disc[comp].all():
        whites = (cls[comp] == 2).mean()
        if stats[j, cv2.CC_STAT_AREA] > 20000 and whites > 0.9:
            continue  # eye / mouth stroke
        print('  glare island removed: area', stats[j, cv2.CC_STAT_AREA], 'bbox', stats[j, :4].tolist())
        cls[comp] = R_
cv2.imwrite(os.path.join(DEBUG, 'step5_cls_clean.png'), pal_rgb[cls][..., ::-1])

# ---- aspect correction of the central art ----
# Camera-calibrated check (iPhone EXIF focal length) shows the physical plate is
# ~6.4% wider than tall, while the face on it is round. Squaring the frame therefore
# makes the face ~6% taller than wide. Keep the frame square and compress only the
# central art (face, cloud, lettering) vertically so the face is a true circle again.
ASPECT = 1.0645
red_u8 = (cls == R_).astype(np.uint8)
n, lab_cc, stats, _ = cv2.connectedComponentsWithStats(red_u8, connectivity=4)
frame = lab_cc == lab_cc[5, 5]
interior = np.zeros((N, N), bool); interior[280:2140, 280:2140] = True
print('white px outside interior:', int(((cls == 2) & ~interior).sum()))
art_red = (cls == R_) & ~frame & interior
art_white = (cls == 2) & interior
art_any = art_red | art_white
ys_, xs_ = np.where(art_any)
ay0, ay1 = ys_.min(), ys_.max()
acy = (ay0 + ay1) / 2.0
print(f'art bbox y {ay0}-{ay1}, x {xs_.min()}-{xs_.max()}; compress y by 1/{ASPECT} about y={acy:.1f}')
Ma = np.float32([[1, 0, 0], [0, 1 / ASPECT, acy * (1 - 1 / ASPECT)]])
r2 = cv2.warpAffine(art_red.astype(np.float32), Ma, (N, N), flags=cv2.INTER_LINEAR)
w2 = cv2.warpAffine(art_white.astype(np.float32), Ma, (N, N), flags=cv2.INTER_LINEAR)
g2 = 1 - r2 - w2
cls = np.stack([r2, g2, w2], -1).argmax(-1).astype(np.uint8)
cls[frame] = R_
# frame cleanup: no white exists in the frame zone by design; tidy bar edges with a
# square-kernel open/close (keeps axis-aligned bars, removes nubs/notches), and make
# the outer bar run cleanly to the canvas edge.
cls[(cls == 2) & ~interior] = G_
fr = (cls == R_) & ~interior
fr_u8 = fr.astype(np.uint8)
kern = np.ones((15, 15), np.uint8)
fr2 = cv2.morphologyEx(cv2.morphologyEx(fr_u8, cv2.MORPH_OPEN, kern), cv2.MORPH_CLOSE, kern).astype(bool)
band = np.zeros((N, N), bool); band[:60] = band[-60:] = True; band[:, :60] = band[:, -60:] = True
fr2 |= band
cls[~interior & fr2] = R_
cls[~interior & ~fr2 & (cls == R_)] = G_

# bottom band regularisation: the plate's visible lower side adds ~9px to the bottom
# outer bar and compresses the bottom band. Re-space the rows below the lettering so
# the bottom band mirrors the top band (row remap only, frame region only).
def runs_of_red(col):
    v = (col == R_).astype(int); dlt = np.diff(np.r_[0, v, 0])
    return list(zip(np.where(dlt == 1)[0], np.where(dlt == -1)[0]))
tops, bots = [], []
for x in (600, 800, 1600, 1800):
    r = runs_of_red(cls[:, x])
    tops.append((r[0][1], r[1][0], r[1][1]))                # outer end, inner bar start/end
    bots.append((r[-2][0], r[-2][1], r[-1][0]))              # inner bar start/end, outer start
tops = np.median(np.array(tops), 0); bots = np.median(np.array(bots), 0)
print('top band edges', tops.tolist(), 'bottom band edges', bots.tolist())
src_k = [0, 2090, bots[0], bots[1], bots[2], N]
dst_k = [0, 2090, N - tops[2], N - tops[1], N - tops[0], N]
print('bottom band remap src', [round(float(v), 1) for v in src_k], '-> dst', [round(float(v), 1) for v in dst_k])
src_rows = np.clip(np.round(np.interp(np.arange(N), dst_k, src_k)).astype(int), 0, N - 1)
cls = cls[src_rows]
cv2.imwrite(os.path.join(DEBUG, 'step7_cls_final.png'), pal_rgb[cls][..., ::-1])
cv2.imwrite(os.path.join(DEBUG, 'step6_cls_aspect.png'), pal_rgb[cls][..., ::-1])
gold = (cls == G_)
pts_c = []
for ang in np.radians(np.r_[125:270:1.0, -90:-62:1.0]):
    for r in range(350, 800):
        x = int(round(990 + r * np.cos(ang))); y = int(round(1000 + r * np.sin(ang)))
        if gold[y, x]:
            pts_c.append((x, y)); break
q = np.array(pts_c, float)
A = np.c_[2 * q[:, 0], 2 * q[:, 1], np.ones(len(q))]
fx, fy, k = np.linalg.lstsq(A, (q ** 2).sum(1), rcond=None)[0]; FR = np.sqrt(k + fx * fx + fy * fy)
res = np.hypot(q[:, 0] - fx, q[:, 1] - fy) - FR
(ex, ey), (ew, eh), eang = cv2.fitEllipse(q.astype(np.float32))
print(f'after correction: face circle R={FR:.1f} resid std {res.std():.2f}px; ellipse {ew:.1f} x {eh:.1f} (ratio {max(ew,eh)/min(ew,eh):.4f})')

# ---- anti-aliased composite ----
masks = np.stack([cv2.GaussianBlur((cls == k).astype(np.float32), (0, 0), 1.2) for k in range(3)], -1)
masks /= masks.sum(-1, keepdims=True)
out = (masks @ pal_rgb.astype(np.float32))
out = np.clip(out + 0.5, 0, 255).astype(np.uint8)
final = Image.fromarray(out).resize((1200, 1200), Image.LANCZOS)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
final.save(OUT, dpi=(300, 300))

orig = pil.copy(); orig.thumbnail((900, 1200))
canvas = Image.new('RGB', (orig.width + 1200 + 60, 1240), (255, 255, 255))
canvas.paste(orig, (20, (1240 - orig.height) // 2))
canvas.paste(final, (orig.width + 40, 20))
canvas.save(PREVIEW)
print('saved', OUT, final.size, final.mode)
