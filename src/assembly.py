"""組裝與爆炸 STEP(只給預覽與干涉檢查用,不是列印用的檔)。

執行(先跑過 test_coupon.py、thread_ring.py、plug.py、key.py、tee.py、box.py):
  uv run --with build123d --with bd_warehouse --with trimesh --with manifold3d python assembly.py
產出:build/assembly.step、build/exploded.step(正式件的使用情境)、build/mock/cap_mock.stl(示意件網格,給 量測匯出檔.py 求交集)

示意件 cap_mock:照尺寸表建的蓋子(法蘭、碗、4 道弧牆 + 兩端短牆、平台、直肋、中心井、外牙)。
外牙的牙型角度與牙頂寬沒量(B),假設 7° / 45°(內牙是 7° / 50°);牙起點的相位不知道,
牙環在組裝裡轉到和示意外牙交集最小的角度(實物轉進去時自己會找到這個相位)。
"""
from math import cos, radians, sin
from pathlib import Path

import build123d as bd
import numpy as np
import trimesh

from dims import (BOWL_D, BOWL_DEPTH, BRK_END_T, BRK_HALF, BRK_IN_HALF, BRK_IN_R, BRK_OUT_R, CAP_CREST_W, CAP_TRAIL_FLANK_DEG, CAP_H, EMBED, FIT_GAP,
                  FLANGE_D, FLANGE_T, PLAT_DEPTH, RIB_H, RIB_N, RIB_W, RING_PITCHES, SLOT_W, THREAD_MAJOR,
                  THREAD_MINOR, THREAD_PITCH, THREAD_TURNS, WELL_D, WELL_DEPTH)
from test_coupon import BRACKET_ANGLES, RIB_ANGLES, bracket_envelope, wedge
from thread_ring import buttress_tooth

HERE = Path(__file__).parent
BUILD = HERE / "build"
C = (bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
RING_TOP_Z = -(CAP_H - THREAD_TURNS * THREAD_PITCH) - 0.4   # 牙環套在外牙中段(試轉時蓋子整段穿過,不靠法蘭定位)
EXPLODE_GAP = 40.0


def cap_mock():
    bowl_r, root_r, crest_r = BOWL_D / 2, THREAD_MINOR / 2, THREAD_MAJOR / 2
    thread_len = THREAD_TURNS * THREAD_PITCH
    cap = bd.Pos(0, 0, -FLANGE_T) * bd.Cylinder(FLANGE_D / 2, FLANGE_T, align=C)
    cap += bd.Pos(0, 0, -CAP_H) * bd.Cylinder(root_r, CAP_H - FLANGE_T + EMBED, align=C)
    cap = cap.fuse(*(bd.Pos(0, 0, -CAP_H) * buttress_tooth(crest_r, root_r, CAP_CREST_W, THREAD_PITCH, thread_len,
                                                         CAP_TRAIL_FLANK_DEG)).solids()).clean()
    cap -= bd.Pos(0, 0, -BOWL_DEPTH) * bd.Cylinder(bowl_r, BOWL_DEPTH + 1, align=C)
    cap -= bd.Pos(0, 0, -BOWL_DEPTH - WELL_DEPTH) * bd.Cylinder(WELL_D / 2, WELL_DEPTH + EMBED, align=C)
    for c in BRACKET_ANGLES:
        env_far = bracket_envelope(c)           # 包絡延伸到碗壁外,內縮之後碗壁那一圈才不會多出一道牆
        env = env_far & bd.Circle(bowl_r + EMBED)
        # 弧牆(內側弧)+ 兩端斜牆(厚 BRK_END_T,整片在包絡以內,斜到碗壁 1/8 圈)
        band = (env_far - bd.offset(env_far, amount=-BRK_END_T, kind=bd.Kind.INTERSECTION)) & bd.Circle(bowl_r + EMBED)
        walls = wedge(BRK_IN_R, BRK_OUT_R, BRK_IN_HALF, c) + band
        cap += bd.Pos(0, 0, -BOWL_DEPTH) * bd.extrude(walls, BOWL_DEPTH)
        # 平台以下是實的(弧牆外面到窄縫之間,在包絡以內)
        plat = env & (bd.Circle(bowl_r - SLOT_W) - bd.Circle(BRK_OUT_R - EMBED))
        cap += bd.Pos(0, 0, -BOWL_DEPTH) * bd.extrude(plat, BOWL_DEPTH - PLAT_DEPTH)
    for c in RIB_ANGLES:
        cap += bd.Pos(0, 0, -BOWL_DEPTH) * bd.Rot(0, 0, c) * bd.Pos(bowl_r - RIB_H / 2 + EMBED / 2, 0, 0) * bd.Box(
            RIB_H + EMBED, RIB_W, BOWL_DEPTH, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    return cap


def best_ring_angle(cap_m, ring_stl, top_z=None, step=10):
    """牙環(匯出的 STL 擺回使用位置)繞 Z 轉 0~360,回傳和示意外牙交集體積最小的角度與體積(manifold 布林)。

    用匯出的 STL 而不是 tessellate():後者拼出來的網格不封閉,manifold 不收(2026-11-20)。
    """
    ring_m = trimesh.load(ring_stl)
    ring_m.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))   # = thread_ring.to_use_pose
    ring_m.apply_translation([0, 0, RING_TOP_Z if top_z is None else top_z])
    best = None
    for deg in np.arange(0, 360, step):
        m = ring_m.copy()
        m.apply_transform(trimesh.transformations.rotation_matrix(radians(deg), [0, 0, 1]))
        v = trimesh.boolean.intersection([cap_m, m], engine="manifold").volume
        if best is None or v < best[1]:
            best = (float(deg), float(v))
    return best


def labeled(shape, name):
    shape.label = name
    return shape


if __name__ == "__main__":
    import plug as plug_mod
    import box as box_mod
    import key as key_mod
    from dims import JOINT_Z
    (BUILD / "mock").mkdir(exist_ok=True)
    cap = labeled(cap_mock(), "cap_mock")
    bd.export_stl(cap, str(BUILD / "mock" / "cap_mock.stl"))
    cap_m = trimesh.load(BUILD / "mock" / "cap_mock.stl")
    # 使用情境:蓋子鎖在 C 方盒(法蘭擱在盒頂)、插頭插進蓋子、六角鍵與 T 型把手在上面
    box_top = -FLANGE_T
    deg, vol = best_ring_angle(cap_m, BUILD / "box.stl", top_z=box_top)
    box = labeled(bd.Rot(0, 0, deg) * bd.Pos(0, 0, box_top) * box_mod.to_use_pose(bd.import_step(str(BUILD / "box.step"))), "box")
    plug = labeled(plug_mod.to_use_pose(bd.import_step(str(BUILD / "plug.step"))), "plug")
    key_use = bd.Pos(0, 0, JOINT_Z) * key_mod.key_use()
    key = labeled(key_use, "key")
    wheel = labeled(bd.Pos(0, 0, JOINT_Z) * bd.import_step(str(BUILD / "tee.step")), "tee")
    bd.export_step(bd.Compound([cap, box, plug, key, wheel]), str(BUILD / "assembly.step"))
    ex = []
    for shp, dz in ((box, -EXPLODE_GAP), (plug, EXPLODE_GAP), (key, 2 * EXPLODE_GAP), (wheel, 3 * EXPLODE_GAP)):
        ex.append(labeled(bd.Pos(0, 0, dz) * shp, shp.label))
    bd.export_step(bd.Compound([cap] + ex), str(BUILD / "exploded.step"))
    print(f"✓ build/assembly.step(cap_mock、box、plug、key、tee;方盒轉 {deg:.0f}°,和示意外牙交集 {vol:.2f} mm³)")
    print("✓ build/exploded.step(測試件不放進組裝)")
