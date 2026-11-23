"""插頭:塞子 + 4 爪 + 定位柱(同 B 配合測試片)+ 底盤 Ø72 + 45° 斜面接輪轂 Ø50。

執行:uv run --with build123d python plug.py
產出:build/plug.stl / .step
列印擺法:輪轂頂面(接舵輪那面)貼熱床,往上依序是輪轂 → 45° 斜面 → 底盤 → 塞子 → 定位柱,全部免支撐。
(README 定案設計寫「底盤貼熱床」;底盤上下兩邊都有東西,實際能免支撐的是輪轂頂面貼熱床,見 README。)

傳扭力:輪轂頂面中心的六角槽插 key.py 的六角鍵(鍵另一半插舵輪);3 顆 M2×12 自攻從舵輪那邊鎖進來防脫。
受力:扭力繞 Z,從塞子往上經底盤、輪轂傳到六角鍵,是層間剪力 → 這一件全實心,切片建議 100% 填充。
"""
from math import cos, radians, sin, tan
from pathlib import Path

import build123d as bd

from common import UP, hex_face, revolve_profile, roofed_hole
from dims import (BOWL_D, CLAW_FINGER_BOTTOM, CLAW_WIDE_BOTTOM, CONE_DEG, EMBED, HUB_D, JOINT_Z, KEY_AF, KEY_CLR,
                  KEY_SOCKET_DEPTH, LEAD_IN, PILOT_LEAD_IN, PILOT_TIP, PLUG_BOTTOM, PLUG_CORE_D, PLUG_DISK_D, PLUG_DISK_T, PLUG_GAP,
                  SCREW_BITE, SCREW_N, SCREW_PILOT_D, SCREW_PILOT_EXTRA, SCREW_R, WELL_D, DISK_CHAMFER_TOP)
from test_coupon import lead_in_cutter, plug_faces

BUILD = Path(__file__).parent / "build"
BUILD.mkdir(exist_ok=True)
SCREW_ANGLES = [30 + k * 360 / SCREW_N for k in range(SCREW_N)]   # 對著六角的邊(離六角角最遠)


def plug_use():
    """使用時座標(z = 0 蓋頂,塞子往 -z,輪轂頂面在 JOINT_Z)。"""
    core, wide, finger = plug_faces(PLUG_GAP)
    bowl_r = BOWL_D / 2
    body = bd.Pos(0, 0, PLUG_BOTTOM) * bd.extrude(core, -PLUG_BOTTOM + EMBED)
    body -= lead_in_cutter(bowl_r - PLUG_GAP, PLUG_BOTTOM, LEAD_IN)
    claws = bd.Pos(0, 0, CLAW_WIDE_BOTTOM) * bd.extrude(wide, -CLAW_WIDE_BOTTOM + EMBED)
    claws += bd.Pos(0, 0, CLAW_FINGER_BOTTOM) * bd.extrude(finger, -CLAW_FINGER_BOTTOM + EMBED)
    claws -= lead_in_cutter(bowl_r - PLUG_GAP, CLAW_FINGER_BOTTOM, LEAD_IN)
    pilot_r = WELL_D / 2 - PLUG_GAP
    pilot = bd.Pos(0, 0, PILOT_TIP) * bd.Cylinder(pilot_r, PLUG_BOTTOM - PILOT_TIP + EMBED, align=UP)
    pilot -= lead_in_cutter(pilot_r, PILOT_TIP, PILOT_LEAD_IN)
    # 底盤 + 斜面 + 輪轂(旋轉剖面);斜面離垂直 CONE_DEG,列印時(倒過來)從輪轂往外長
    disk_r, hub_r = PLUG_DISK_D / 2, HUB_D / 2
    cone_h = (disk_r - hub_r) / tan(radians(CONE_DEG))
    upper = revolve_profile([(0, 0), (disk_r - DISK_CHAMFER_TOP, 0), (disk_r, DISK_CHAMFER_TOP), (disk_r, PLUG_DISK_T),
                             (hub_r, PLUG_DISK_T + cone_h), (hub_r, JOINT_Z), (0, JOINT_Z)])
    part = upper + body + claws + pilot
    # 六角鍵槽:從輪轂頂面往下;頂錐在下面(列印時在上面,不懸空)
    sock_af = KEY_AF + KEY_CLR
    part -= bd.Pos(0, 0, JOINT_Z) * bd.Rot(180, 0, 0) * roofed_hole(sock_af / 2 / cos(radians(30)), KEY_SOCKET_DEPTH,
                                                                     hex_face(sock_af))
    # 中心通孔(省料):從定位柱尖穿到鍵槽;軸心剪應力接近 0(使用者 2026-11-20 選)
    part -= bd.Pos(0, 0, PILOT_TIP - 1) * bd.Cylinder(PLUG_CORE_D / 2, JOINT_Z - PILOT_TIP + 2, align=UP)
    # 3 個 M2 自攻預留孔
    for a in SCREW_ANGLES:
        part -= bd.Pos(SCREW_R * cos(radians(a)), SCREW_R * sin(radians(a)), JOINT_Z) * bd.Rot(180, 0, 0) * roofed_hole(
            SCREW_PILOT_D / 2, SCREW_BITE + SCREW_PILOT_EXTRA)
    return part


def to_print(part):
    """使用時 → 列印擺法:繞 X 翻 180°,輪轂頂面落在 z = 0。"""
    return bd.Pos(0, 0, JOINT_Z) * bd.Rot(180, 0, 0) * part


def to_use_pose(part):
    return bd.Rot(180, 0, 0) * (bd.Pos(0, 0, -JOINT_Z) * part)


if __name__ == "__main__":
    p = to_print(plug_use())
    assert p.is_valid and len(p.solids()) == 1
    bd.export_stl(p, str(BUILD / "plug.stl"))
    bd.export_step(p, str(BUILD / "plug.step"))
    print(f"plug: 體積 {p.volume / 1000:.1f} cm³,高 {p.bounding_box().size.Z:.2f}")
