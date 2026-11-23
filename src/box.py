"""C 模擬桶口:方盒 90×90×26,內牙(和牙環短段同一套牙型)、底部開放、四角 Ø7 M2 收納孔。

執行:uv run --with build123d --with bd_warehouse python box.py
產出:build/box.stl / .step
列印擺法:使用時的頂面(蓋子從這面轉進去、法蘭擱在這面)貼熱床;承力面 7° 列印時朝上(同 thread_ring.py)。
牙距:THREAD_PITCH(使用者 量的 5.0;牙環短段回填後若改成 5.08 就改這裡)。牙做滿整個盒高,蓋子 3 圈牙轉到哪都咬得到。
"""
from pathlib import Path

import build123d as bd

from common import UP, roofed_hole
from dims import (BOX_CHAMFER, BOX_H, BOX_HOLE_D, BOX_HOLE_DEPTH, BOX_HOLE_OFF, BOX_W, EMBED, RING_APEX_R, RING_CREST_W,
                  RING_ENTRY_CHAMFER, RING_ROOT_R, THREAD_PITCH)
from thread_ring import buttress_tooth

BUILD = Path(__file__).parent / "build"
BUILD.mkdir(exist_ok=True)


def box_print():
    body = bd.Box(BOX_W, BOX_W, BOX_H, align=UP)
    body = bd.chamfer(body.edges(), BOX_CHAMFER)
    body -= bd.Pos(0, 0, -EMBED) * bd.Cylinder(RING_ROOT_R, BOX_H + 2 * EMBED, align=UP)
    for sx in (-1, 1):
        for sy in (-1, 1):
            body -= bd.Pos(sx * BOX_HOLE_OFF, sy * BOX_HOLE_OFF, 0) * roofed_hole(BOX_HOLE_D / 2, BOX_HOLE_DEPTH)
    tooth = buttress_tooth(RING_APEX_R, RING_ROOT_R, RING_CREST_W, THREAD_PITCH, BOX_H, entry_chamfer=RING_ENTRY_CHAMFER)
    part = body.fuse(*tooth.solids())
    assert len(part.solids()) == 1, len(part.solids())
    return part


def to_use_pose(part):
    """列印擺法 → 使用時(盒頂 z = 0、往 -z)。"""
    return bd.Rot(180, 0, 0) * part


if __name__ == "__main__":
    p = box_print()
    assert p.is_valid
    bd.export_stl(p, str(BUILD / "box.stl"))
    bd.export_step(p, str(BUILD / "box.step"))
    print(f"box: 體積 {p.volume / 1000:.1f} cm³,高 {p.bounding_box().size.Z:.2f}")
