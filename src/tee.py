"""T 型把手(240):輪轂 Ø50 與兩支臂是同一塊(俯視輪廓拉成 18 高)+ 六角對邊 30。

執行:uv run --with build123d python tee.py
產出:build/tee.stl / .step
列印擺法:平躺,臂與輪轂的底在同一個平面貼熱床(= 使用時的 JOINT_Z);臂沿 Y(PRINT_ROT_Z,主噴頭 X 方向放不下 240)。

使用者 2026-11-20 把舵輪換成 T 型 240:雙手各 150 N 約 29 N·m ≥ 原廠 27;單手要 > 360 mm,X2D 單軸只有 256。
接合(回饋單 2026-11-20-5:原本臂只是疊在圓柱上):俯視輪廓一體,臂接輪轂的凹角 R10、臂尖 R6(XY 平面圓角);
輪轂與臂頂面齊平;上緣一圈 45° 倒角 3、下緣防象腳倒角。截面裡沒有圓弧(DfAM:Z 向轉折做倒角)。
受力:手推臂尖 → 臂在 XY 平面彎(層內)→ 輪轂;單邊 200 N 時根部彎曲應力約 14 MPa(手算)。
活動扳手夾六角時扭力繞 Z(層間剪力,建議 100% 填充)。
底面中心是六角鍵槽(key.py),3 個沉頭孔讓 M2×12 自攻往下鎖進插頭。
"""
from math import cos, radians, sin, tan
from pathlib import Path

import build123d as bd

from common import hex_face, roofed_hole
from dims import (EMBED, GRIP_D, HEX_AF, HEX_CHAMFER, HEX_H, HUB_D, KEY_AF, KEY_CLR, KEY_SOCKET_DEPTH,
                  OCT_BOTTOM_DEG, SCREW_BITE, SCREW_CB_D, SCREW_LEN, SCREW_PASS_D, SCREW_R, TEE_BOTTOM_CHAMFER,
                  TEE_JOINT_FILLET, TEE_LEN, TEE_NECK_R, TEE_NECK_W, TEE_ROOT_W, TEE_SEC_H, TEE_TIP_FILLET,
                  TEE_TOP_CHAMFER, WHEEL_HUB_H)
from plug import SCREW_ANGLES

HERE = Path(__file__).parent
BUILD = HERE / "build"
BUILD.mkdir(exist_ok=True)
ARM_ANGLES = (0, 180)   # 兩支臂;M2 孔在 30°、150°、270°,避開臂


def cut_joint(part):
    """底面:六角鍵槽(頂錐自支撐)與 M2×12 穿孔 + 螺絲頭沉孔(螺絲頭坐在 z = SCREW_LEN − SCREW_BITE)。"""
    sock_af = KEY_AF + KEY_CLR
    part -= roofed_hole(sock_af / 2 / cos(radians(30)), KEY_SOCKET_DEPTH, hex_face(sock_af))
    seat_z = SCREW_LEN - SCREW_BITE
    for a in SCREW_ANGLES:
        loc = bd.Pos(SCREW_R * cos(radians(a)), SCREW_R * sin(radians(a)), 0)
        part -= loc * bd.Pos(0, 0, -EMBED) * bd.Cylinder(SCREW_PASS_D / 2, seat_z + 2 * EMBED,
                                                         align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        part -= loc * bd.Pos(0, 0, seat_z) * bd.Cylinder(SCREW_CB_D / 2, WHEEL_HUB_H - seat_z + EMBED,
                                                         align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    return part


def plan_face():
    """俯視輪廓:輪轂圓 + 兩支臂(根部寬 TEE_ROOT_W → 最細 TEE_NECK_W → 尖端 GRIP_D),
    臂接輪轂的凹角做 R TEE_JOINT_FILLET、臂尖外角做 R TEE_TIP_FILLET(都在 XY 平面,噴嘴一筆走出來)。"""
    hub_r = HUB_D / 2
    half = [(hub_r - 5, TEE_ROOT_W / 2), (TEE_NECK_R, TEE_NECK_W / 2), (TEE_LEN / 2, GRIP_D / 2)]
    pts = half + [(x, -y) for x, y in reversed(half)]
    plan = bd.Circle(hub_r)
    for a in ARM_ANGLES:
        plan += bd.Rot(0, 0, a) * bd.make_face(bd.Polyline(*pts, close=True))
    plan = bd.offset(bd.offset(plan, TEE_JOINT_FILLET, kind=bd.Kind.ARC), -TEE_JOINT_FILLET, kind=bd.Kind.ARC)   # 凹角圓角
    plan = bd.offset(bd.offset(plan, -TEE_TIP_FILLET, kind=bd.Kind.ARC), TEE_TIP_FILLET, kind=bd.Kind.ARC)       # 外角圓角
    return plan


def tee_print():
    """一整塊:俯視輪廓拉成 WHEEL_HUB_H 高(輪轂與臂頂面齊平),上緣 45° 倒角、下緣防象腳倒角,六角長在頂面上。"""
    assert TEE_SEC_H == WHEEL_HUB_H
    body = bd.extrude(plan_face(), WHEEL_HUB_H)
    body = bd.chamfer(body.edges().group_by(bd.Axis.Z)[-1], TEE_TOP_CHAMFER)
    bottom = body.faces().sort_by(bd.Axis.Z)[0]
    body = bd.chamfer(body.edges().group_by(bd.Axis.Z)[0], TEE_BOTTOM_CHAMFER,
                      TEE_BOTTOM_CHAMFER / tan(radians(OCT_BOTTOM_DEG)), reference=bottom)
    hexk = bd.Pos(0, 0, WHEEL_HUB_H - EMBED) * bd.extrude(hex_face(HEX_AF), HEX_H + EMBED)
    hexk = bd.chamfer(hexk.edges().group_by(bd.Axis.Z)[-1], HEX_CHAMFER)
    return cut_joint(body + hexk)


PRINT_ROT_Z = 90   # 匯出時轉 90°,臂沿 Y(X2D 主噴頭 X 只有 20.5~256,放不下 240)


def to_print(part):
    return bd.Rot(0, 0, PRINT_ROT_Z) * part


if __name__ == "__main__":
    t = to_print(tee_print())
    assert t.is_valid and len(t.solids()) == 1, len(t.solids())
    bd.export_stl(t, str(BUILD / "tee.stl"))
    bd.export_step(t, str(BUILD / "tee.step"))
    bb = t.bounding_box()
    print(f"tee: 體積 {t.volume / 1000:.1f} cm³,外框 {bb.size.X:.1f} × {bb.size.Y:.1f} × {bb.size.Z:.2f}")
