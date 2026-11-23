"""六角鍵:舵輪 ↔ 插頭傳扭力。另印一件,**躺著印**(一個邊貼熱床)。

執行:uv run --with build123d python key.py
產出:build/key.stl / .step(列印擺法:軸沿 Y、一個平邊貼熱床)

為什麼另外做一支鍵、躺著印:扭力繞鍵的軸;直立印的柱子,扭轉剪力落在層與層之間(最弱);
躺著印,剪力的截面橫跨層、沿著線材,強很多。直接在插頭頂上長一根柱子,插頭與舵輪都沒辦法免支撐印。
"""
from pathlib import Path

import build123d as bd

from common import hex_face
from dims import KEY_AF, KEY_END_MARGIN, KEY_SOCKET_DEPTH

BUILD = Path(__file__).parent / "build"
BUILD.mkdir(exist_ok=True)
KEY_LEN = 2 * KEY_SOCKET_DEPTH - KEY_END_MARGIN


def key_use():
    """使用時座標:軸沿 Z、中心在 z = 0(組裝時移到 JOINT_Z)。"""
    # 兩端不倒角:躺著印時端面倒角被 3d-qc 判成 Z 向緩坡(2026-11-20);鍵靠 KEY_CLR 壓入
    return bd.extrude(hex_face(KEY_AF), KEY_LEN / 2, both=True)


def to_print(part):
    """軸轉到 Y、一個平邊朝下貼 z = 0(hex_face 的角在 0°,邊在 90° / 270°)。"""
    p = bd.Rot(90, 0, 0) * part   # 邊在 270°(−Y)的那一面轉到 −Z
    return bd.Pos(0, 0, -p.bounding_box().min.Z) * p


if __name__ == "__main__":
    p = to_print(key_use())
    assert p.is_valid
    bb = p.bounding_box()
    bd.export_stl(p, str(BUILD / "key.stl"))
    bd.export_step(p, str(BUILD / "key.step"))
    print(f"key: 體積 {p.volume / 1000:.1f} cm³,外框 {bb.size.X:.2f} × {bb.size.Y:.2f} × {bb.size.Z:.2f}")
