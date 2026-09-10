"""r5 に縁の雷文をインラインSVGで書き込む。variants/ 内で実行する。

雷文の形は依頼主の見本画像（reference/raimon-sample.png）を
ピクセル解析してトレースしたもの。見本から実測した値:
  線幅6 : 平行線の芯間隔11（＝線6＋隙間5） : 帯幅28 : 1組の周期77 : 組間の切れ目5
1組（PAIR）は渦2つが1本の線で繋がった連続ストロークで、中央の縦棒を軸に
180度回転対称。組と組の間だけ切れる。角は帯を繋がず、見本どおり
上下の帯を角まで通し、左右の帯をその内側に隙間を空けて置く。
"""
import os
import pathlib

RED = '#B0261A'
PW, PH = 420.0, 297.0        # A3横（mm）

STROKE, BAND, PERIOD, GAP = 6.0, 28.0, 77.0, 5.0
# 1組の中心線。y=3 が帯の外側の縁、y=25 が内側。x は左の渦→中央の縦棒→右の渦
PAIR = [(11, 14), (25, 14), (25, 25), (3, 25), (3, 3), (36, 3),
        (36, 25), (69, 25), (69, 3), (47, 3), (47, 14), (61, 14)]

# 採用値: 帯7.13mm・21x14組。r4と同じ枠の占有面積に収まるので本文レイアウトが変わらない
NH, NV = int(os.environ.get('RAIMON_NH', 21)), int(os.environ.get('RAIMON_NV', 14))
MX = float(os.environ.get('RAIMON_MX', 4.9))    # 紙の左右端から枠までの余白（mm）
S = (PW - 2*MX) / (NH * PERIOD - GAP)           # 倍率
B = BAND * S                                    # 帯の幅（mm）
FW, FH = (NH*PERIOD - GAP) * S, (2*BAND + GAP + NV*PERIOD) * S
X0, Y0 = (PW - FW) / 2, (PH - FH) / 2           # 枠の外側インクの左上

def path(place):
    p = [place(x, y) for x, y in PAIR]
    return '<path d="M' + 'L'.join(f'{x:.3f} {y:.3f}' for x, y in p) + '"/>'

parts = []
for i in range(NH):                             # 上辺・下辺（角まで通す）
    ox = X0 + i * PERIOD * S
    parts.append(path(lambda x, y, ox=ox: (ox + x*S, Y0 + y*S)))
    parts.append(path(lambda x, y, ox=ox: (ox + x*S, Y0 + FH - y*S)))
for j in range(NV):                             # 左辺・右辺（上下の帯の内側に納める）
    oy = Y0 + (BAND + GAP) * S + j * PERIOD * S
    parts.append(path(lambda x, y, oy=oy: (X0 + y*S, oy + x*S)))
    parts.append(path(lambda x, y, oy=oy: (X0 + FW - y*S, oy + x*S)))

svg = (f'<svg class="raimon" viewBox="0 0 {PW:g} {PH:g}" xmlns="http://www.w3.org/2000/svg" '
       f'preserveAspectRatio="none" aria-hidden="true">'
       f'<g fill="none" stroke="{RED}" stroke-width="{STROKE*S:.3f}" '
       f'stroke-linecap="butt" stroke-linejoin="miter">' + ''.join(parts) + '</g></svg>')

CLR = float(os.environ.get('RAIMON_CLR', 3.0))  # 帯の内側と本文のあき（mm）
pad_x = X0 + B + CLR
pad_y = Y0 + B + CLR

p = pathlib.Path('menu-a3-r5-raimon.html')
h = p.read_text()
start = h.index('  .raimon {'); end = h.index('  .page-inner {')
h = h[:start] + '''  /* 縁の雷文：印刷でぼやけないようインラインSVGで直接描く */
  .raimon { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
''' + h[end:]
h = h.replace('<div class="raimon"></div>', svg, 1)
h = h.replace('inset: 15mm 15mm 14mm;',
              f'inset: {pad_y:.1f}mm {pad_x:.1f}mm {max(pad_y-1,0):.1f}mm;', 1)
p.write_text(h)
print(f'frame ok  {NH}x{NV} kumi  band={B:.2f}mm  stroke={STROKE*S:.2f}mm  '
      f'frame={FW:.1f}x{FH:.1f}mm  margin={X0:.1f}/{Y0:.1f}mm  inner pad={pad_x:.1f}/{pad_y:.1f}mm')
