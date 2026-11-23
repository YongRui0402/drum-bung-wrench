"""牙環短段:模擬桶口的 2 圈內牙(BUTTRESS),只印 1/2 圈(C 形),徑向間隙 A 0.7 / B 1.0 兩個變體,牙距 5.0。

執行:uv run --with build123d --with bd_warehouse python thread_ring.py
產出:build/ring_5.00.stl / .step、build/ring_5.08.stl / .step
列印擺法(同 C 方盒):使用時的頂面(蓋子從這面轉進去)貼熱床;承力面(7°)列印時朝上、45° 那面朝下(自支撐)。

怎麼用:把蓋子從刻字的背面(貼熱床那面,有入口倒角)轉進去,兩段各試一次,
記下哪一段轉得順、轉到法蘭碰到環頂時晃不晃。轉得順的那一個牙距就是 C 方盒的牙距。

牙型:右旋、單頭;蓋子的牙底徑/牙峰徑(尺寸表)各加 THREAD_RAD_CLR 當內牙的牙頂/牙根。
牙型角度量不到 → 承力面 7°、另一面 50°(列印時朝下,離垂直 40°,比自支撐門檻 45° 留 5°),兩者都是 B 級,試轉驗證。
"""
from math import radians, tan
from pathlib import Path

import build123d as bd
from bd_warehouse.thread import Thread

from deterministic import serial_common

from dims import (EMBED, ENTRY_DEG, ENTRY_OVERRUN, LOAD_FLANK_DEG, MARK_DEPTH, MARK_SIZE, RING_APEX_R, RING_CREST_W, RING_ENTRY_CHAMFER,
                  RING_H, RING_OD, RING_PITCHES, RING_ROOT_R, RING_VARIANTS, THREAD_DEPTH, THREAD_MAJOR, THREAD_MINOR, TRAIL_FLANK_DEG, DISK_CHAMFER_BED,
                  DISK_CHAMFER_TOP)

BUILD = Path(__file__).parent / "build"
BUILD.mkdir(exist_ok=True)


def buttress_tooth(apex_r, root_r, crest_w, pitch, length, trail_deg=TRAIL_FLANK_DEG, entry_chamfer=0.0):
    """一條 BUTTRESS 牙,z 0 ~ length;apex_offset 為正時 +z 那面是 7° 承力面(2026-11-20 切片實測確認)。

    apex_r < root_r 是內牙(牙從孔壁往內長),反之是外牙。牙根吃進母體 EMBED。
    收尾:牙做長一個牙距、兩端不收(raw),再用圓柱切齊到 0 ~ length。bd_warehouse 的 square 收尾
    會在端面留下 46°~52° 的碎三角形(回饋單 2026-11-20 PF-01、PF-02),切齊的不會(2026-11-20 實測 0 mm²)。
    """
    h = abs(root_r - apex_r) + EMBED
    run_load, run_trail = h * tan(radians(LOAD_FLANK_DEG)), h * tan(radians(trail_deg))
    root_r = root_r + EMBED if root_r > apex_r else root_r - EMBED
    t = Thread(apex_radius=apex_r, apex_width=crest_w, root_radius=root_r, root_width=crest_w + run_load + run_trail,
               pitch=pitch, length=length + pitch, apex_offset=(run_trail - run_load) / 2, end_finishes=("raw", "raw"))
    big = max(apex_r, root_r) + 1
    if entry_chamfer:   # 內牙入口(z = 0)牙頂削導角,和切齊在同一次交集裡做(分開做差集會讓實體失效)
        # 導角面離垂直 ENTRY_DEG(< 45 留餘量;剛好 45° 時三角化後有面超過門檻);
        # 圓錐越過牙頂 ENTRY_OVERRUN 才收,收尾的水平面落在牙頂以內的空處,不和牙頂共邊
        k = tan(radians(ENTRY_DEG))
        r0 = apex_r + entry_chamfer * k
        r1 = apex_r - ENTRY_OVERRUN
        z1 = (r0 - r1) / k
        pts = [(r0, 0), (big, 0), (big, length), (0, length), (0, z1), (r1, z1)]
    else:
        pts = [(0, 0), (big, 0), (big, length), (0, length)]
    clip = bd.revolve(bd.make_face(bd.Plane.XZ * bd.Polyline(*pts, close=True)), bd.Axis.Z)
    return serial_common(bd.Pos(0, 0, -pitch / 2) * t, clip)   # 不用 `&`:build123d 的布林建不出同一個 STL


def ring(variant):
    """1/2 圈牙環(C 形,只留 y ≥ 0 那半);variant 決定徑向間隙(RING_VARIANTS)。"""
    clr = RING_VARIANTS[variant]
    pitch = RING_PITCHES["5.00"]
    apex_r, root_r = THREAD_MINOR / 2 + clr, THREAD_MAJOR / 2 + clr
    r_out = RING_OD / 2
    # 環身剖面(列印擺法):z = 0 貼熱床(= 使用時頂面、蓋子的入口)
    prof = bd.Polyline((root_r, 0), (r_out - DISK_CHAMFER_BED, 0), (r_out, DISK_CHAMFER_BED),
                       (r_out, RING_H - DISK_CHAMFER_TOP), (r_out - DISK_CHAMFER_TOP, RING_H), (root_r, RING_H),
                       close=True)
    body = bd.revolve(bd.make_face(bd.Plane.XZ * prof), bd.Axis.Z)
    # 刻記號:朝上那面(使用時的底面)、留下的那半(+Y);刻在環身上,碰不到牙
    text = bd.Text(f"{variant} R{clr:.1f}", MARK_SIZE, align=(bd.Align.CENTER, bd.Align.CENTER))
    mark_r = (root_r + r_out) / 2
    body -= bd.Pos(0, mark_r, RING_H - MARK_DEPTH) * bd.extrude(text, MARK_DEPTH + EMBED)
    tooth = buttress_tooth(apex_r, root_r, RING_CREST_W, pitch, RING_H, entry_chamfer=RING_ENTRY_CHAMFER)
    part = body.fuse(*tooth.solids())   # 切齊後的牙是幾段實體,逐一融合進環身
    # 只留 1/2 圈(使用者 2026-11-20 建議);切面是直立的,不懸空
    half = bd.Pos(0, r_out + 1, 0) * bd.Box(2 * r_out + 2, 2 * r_out + 2, RING_H + 2,
                                             align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    part = serial_common(part, bd.Pos(0, 0, -1) * half)
    assert len(part.solids()) == 1, f"牙環應該是 1 個實體,得到 {len(part.solids())}"
    return part.solids()[0]


def to_use_pose(part):
    """列印擺法 → 使用時座標(環頂 z = 0、往 -z)。"""
    return bd.Rot(180, 0, 0) * part


if __name__ == "__main__":
    assert THREAD_DEPTH > 0
    for v in RING_VARIANTS:
        p = ring(v)
        assert p.is_valid, v
        bd.export_stl(p, str(BUILD / f"ring_{v}.stl"))
        bd.export_step(p, str(BUILD / f"ring_{v}.step"))
        print(f"ring_{v}: 體積 {p.volume / 1000:.1f} cm³,高 {p.bounding_box().size.Z:.2f}")
