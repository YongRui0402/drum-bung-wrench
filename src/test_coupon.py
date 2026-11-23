"""B 配合測試片:插頭最下面一截(塞子 + 爪 + 定位柱)+ 薄底盤,只印約 1/4 圈(一個凹槽),間隙做 A/B/C 三片。

執行:uv run --with build123d python test_coupon.py
產出:build/coupon_A.stl / .step、coupon_B、coupon_C(列印擺法:底盤貼熱床,塞子朝上)

怎麼用:把測試片塞子朝下插進蓋子的碗,看能不能插到底盤貼平蓋頂、會不會晃;
挑「最緊、但還插得到底」的那片,它的間隙就是正式插頭的間隙。

結構(俯視,四個方向一樣):
  塞子   填滿碗(外徑 = 碗內徑 − 2 × 間隙),在 4 道弧牆處挖出包住弧牆的缺口(弧牆 + 兩端短牆的外包絡,外擴一個間隙),
         對 4 條直肋開淺溝
  爪     在缺口裡、貼凹槽外側牆:上段徑向 4(到平台上方)、下段只剩貼外側牆的 2(伸進窄縫);只連在底盤上
  定位柱 光滑圓柱進中心井,尖端離井底 1.0(不碰 knockout)
"""
from math import cos, radians, sin
from pathlib import Path

import build123d as bd

from dims import (BOWL_D, BRK_HALF, BRK_IN_HALF, BRK_IN_R, COUPON_SPAN_DEG, CLAW_FINGER_BOTTOM, CLAW_W, CLAW_WIDE_BOTTOM,
                  COUPON_DISK_D, COUPON_DISK_T, DISK_CHAMFER_BED, DISK_CHAMFER_TOP, EMBED, FIT_GAP, LEAD_IN,
                  MARK_DEPTH, MARK_SIZE, PILOT_LEAD_IN, PILOT_WALL, PILOT_TIP, PLUG_BOTTOM, POCKET_W, RIB_GROOVE_H, RIB_N,
                  RIB_W, SLOT_W, WELL_D)

BUILD = Path(__file__).parent / "build"
BUILD.mkdir(exist_ok=True)
BRACKET_ANGLES = (0, 90, 180, 270)            # 4 道弧牆(尺寸表:4 個凹槽等分)
RIB_ANGLES = tuple(a + 360 / RIB_N / 2 for a in BRACKET_ANGLES)   # 直肋在兩凹槽正中間
BOWL_R = BOWL_D / 2
FAR = BOWL_R + 5                              # 包絡往外延伸到碗壁外(只用來切,值不影響結果)


def wedge(r0, r1, half_deg, c_deg):
    """以 c_deg 為中心、半角 half_deg、r0~r1 的扇環(2D)。"""
    n = 32
    a0, a1 = c_deg - half_deg, c_deg + half_deg
    outer = [(r1 * cos(radians(a0 + (a1 - a0) * i / n)), r1 * sin(radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    inner = [(r0 * cos(radians(a1 - (a1 - a0) * i / n)), r0 * sin(radians(a1 - (a1 - a0) * i / n))) for i in range(n + 1)]
    return bd.make_face(bd.Polyline(*(outer + inner), close=True))


def strip(width, c_deg, r_len):
    """沿 c_deg 方向、寬 width 的長條(2D),用來把爪裁成弦長 CLAW_W。"""
    return bd.Rot(0, 0, c_deg) * bd.Pos(r_len / 2, 0) * bd.Rectangle(r_len, width)


def bracket_envelope(c_deg, r_out=None):
    """弧牆 + 兩端斜牆的外包絡(2D,以 c_deg 為中心):內側是半徑 BRK_IN_R、半角 BRK_IN_HALF 的弧,
    兩端從弧的端點斜到碗壁的 ±BRK_HALF(1/8 圈),再沿徑向延伸到 r_out。"""
    r_out = FAR if r_out is None else r_out
    n = 24
    inner = [(BRK_IN_R * cos(radians(c_deg + BRK_IN_HALF - 2 * BRK_IN_HALF * i / n)),
              BRK_IN_R * sin(radians(c_deg + BRK_IN_HALF - 2 * BRK_IN_HALF * i / n))) for i in range(n + 1)]
    pts = inner
    for r in (BOWL_R, r_out):
        pts.append((r * cos(radians(c_deg - BRK_HALF)), r * sin(radians(c_deg - BRK_HALF))))
    pts += [(r * cos(radians(c_deg + BRK_HALF)), r * sin(radians(c_deg + BRK_HALF))) for r in (r_out, BOWL_R)]
    return bd.make_face(bd.Polyline(*pts, close=True))


def plug_faces(gap):
    """回傳 (塞子截面, 爪上段截面, 爪下段截面),都已經內縮/外擴一個 gap。"""
    core = bd.Circle(BOWL_R - gap)
    for c in RIB_ANGLES:      # 直肋淺溝:寬 RIB_W + 2 間隙,深 RIB_GROOVE_H + 間隙
        core -= bd.Rot(0, 0, c) * bd.Pos(BOWL_R, 0) * bd.Rectangle(2 * (RIB_GROOVE_H + gap), RIB_W + 2 * gap)
    for c in BRACKET_ANGLES:  # 弧牆 + 兩端斜牆(斜到碗壁 1/8 圈)的外包絡,外擴一個間隙
        env = bd.offset(bracket_envelope(c), amount=gap, kind=bd.Kind.INTERSECTION)
        core -= env
    wide, finger = None, None
    for c in BRACKET_ANGLES:
        w = bd.offset(wedge(BOWL_R - POCKET_W, BOWL_R, 30, c) & strip(CLAW_W, c, FAR), amount=-gap,
                      kind=bd.Kind.INTERSECTION)
        f = bd.offset(wedge(BOWL_R - SLOT_W, BOWL_R, 30, c) & strip(CLAW_W, c, FAR), amount=-gap,
                      kind=bd.Kind.INTERSECTION)
        wide = w if wide is None else wide + w
        finger = f if finger is None else finger + f
    return core, wide, finger


def lead_in_cutter(r_out, z_tip, chamfer):
    """削掉尖端外緣一圈 45° 導角(self_support_chamfer_deg)用的環形刀(旋轉體);尖端在 z_tip、往 +z 長。"""
    prof = bd.Polyline((r_out - chamfer - 1, z_tip - 1), (r_out + 5, z_tip - 1), (r_out + 5, z_tip + chamfer),
                       (r_out, z_tip + chamfer), (r_out - chamfer, z_tip), (r_out - chamfer - 1, z_tip), close=True)
    return bd.revolve(bd.make_face(bd.Plane.XZ * prof), bd.Axis.Z)


def coupon(variant):
    gap = FIT_GAP[variant]
    core, wide, finger = plug_faces(gap)
    # 使用時座標:底盤 z 0 ~ T,塞子往 -z
    plug = bd.Pos(0, 0, PLUG_BOTTOM) * bd.extrude(core, -PLUG_BOTTOM + EMBED)
    plug -= lead_in_cutter(BOWL_R - gap, PLUG_BOTTOM, LEAD_IN)
    claws = bd.Pos(0, 0, CLAW_WIDE_BOTTOM) * bd.extrude(wide, -CLAW_WIDE_BOTTOM + EMBED)
    claws += bd.Pos(0, 0, CLAW_FINGER_BOTTOM) * bd.extrude(finger, -CLAW_FINGER_BOTTOM + EMBED)
    claws -= lead_in_cutter(BOWL_R - gap, CLAW_FINGER_BOTTOM, LEAD_IN)
    pilot_r = WELL_D / 2 - gap
    pilot = bd.Pos(0, 0, PILOT_TIP) * bd.Cylinder(pilot_r, PLUG_BOTTOM - PILOT_TIP + EMBED,
                                                  align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    pilot -= lead_in_cutter(pilot_r, PILOT_TIP, PILOT_LEAD_IN)
    disk_r = COUPON_DISK_D / 2
    # 底盤剖面:使用時頂面(z = T)是列印時貼熱床那一面
    disk_prof = bd.Polyline((0, 0), (disk_r - DISK_CHAMFER_TOP, 0), (disk_r, DISK_CHAMFER_TOP),
                            (disk_r, COUPON_DISK_T - DISK_CHAMFER_BED), (disk_r - DISK_CHAMFER_BED, COUPON_DISK_T),
                            (0, COUPON_DISK_T), close=True)
    disk = bd.revolve(bd.make_face(bd.Plane.XZ * disk_prof), bd.Axis.Z)
    part = disk + plug + claws + pilot
    # 省料:測試片只驗配合、不受力 → 中心挖空(定位柱留 PILOT_WALL 的管壁,底盤不挖)
    core_cut_r = pilot_r - PILOT_WALL
    part -= bd.Pos(0, 0, PILOT_TIP - 1) * bd.Cylinder(core_cut_r, -PILOT_TIP + 1,
                                                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    # 只印 ±COUPON_SPAN_DEG / 2(約 1/4 圈,含 0° 那個凹槽與兩側直肋淺溝;使用者 2026-11-20 建議)
    span = bd.revolve(bd.make_face(bd.Plane.XZ * bd.Polyline((0, PILOT_TIP - 1), (disk_r + 1, PILOT_TIP - 1),
                                                             (disk_r + 1, COUPON_DISK_T + 1), (0, COUPON_DISK_T + 1),
                                                             close=True)), bd.Axis.Z, COUPON_SPAN_DEG)
    part = part & (bd.Rot(0, 0, -COUPON_SPAN_DEG / 2) * span)
    # 轉成列印擺法:繞 X 翻 180°(右手系不變),底盤頂面落在 z = 0
    part = bd.Pos(0, 0, COUPON_DISK_T) * bd.Rot(180, 0, 0) * part
    # 刻記號:在朝上的底盤環面(r 26~36)、凹槽外面刻「變體字母 + 間隙」,字沿切線
    text = bd.Text(f"{variant} {gap:.2f}", MARK_SIZE, align=(bd.Align.CENTER, bd.Align.CENTER))
    mark_r = (BOWL_R + disk_r) / 2
    mark = bd.Pos(mark_r, 0, COUPON_DISK_T - MARK_DEPTH) * bd.Rot(0, 0, 90) * bd.extrude(text, MARK_DEPTH + EMBED)
    part -= mark
    return part


def to_use_pose(part):
    """列印擺法 → 使用時座標(給 assembly.py 與量測用)。"""
    return bd.Rot(180, 0, 0) * (bd.Pos(0, 0, -COUPON_DISK_T) * part)


if __name__ == "__main__":
    for v in FIT_GAP:
        p = coupon(v)
        assert p.is_valid, v
        bd.export_stl(p, str(BUILD / f"coupon_{v}.stl"))
        bd.export_step(p, str(BUILD / f"coupon_{v}.step"))
        print(f"coupon_{v}: 體積 {p.volume / 1000:.1f} cm³,高 {p.bounding_box().size.Z:.2f}")
