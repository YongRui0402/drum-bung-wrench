"""幾個件共用的幾何:六角盲孔(頂部錐面自支撐)、圓盲孔、旋轉剖面。"""
from math import cos, floor, radians, tan

import build123d as bd

from dims import EMBED, LAYER, ROOF_TOP_D, SOCKET_ROOF_DEG

UP = (bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)


def revolve_profile(pts):
    """(r, z) 折線繞 Z 轉一圈成實體。"""
    return bd.revolve(bd.make_face(bd.Plane.XZ * bd.Polyline(*pts, close=True)), bd.Axis.Z)


def roofed_hole(r_circ, depth, polygon=None):
    """從 z = 0 往 +z 開的盲孔:深 depth 的柱(六角或圓),頂上接離垂直 SOCKET_ROOF_DEG 的錐(列印時不懸空)。

    r_circ:孔的外接半徑(錐從這個半徑往上收);polygon:2D 截面,None 時是圓。
    孔口往 -z 多開 EMBED,切的時候不和母體表面共面。
    """
    face = polygon if polygon is not None else bd.Circle(r_circ)
    prism = bd.Pos(0, 0, -EMBED) * bd.extrude(face, depth + EMBED)
    # 錐不收到尖點(尖點會讓 STL 非流形),留一個小平頂靠橋接;錐高往下取到層高倍數(小平頂的 Z 才是層高倍數),
    # 小平頂因此略大於 ROOF_TOP_D
    k = tan(radians(SOCKET_ROOF_DEG))
    r_min = min(ROOF_TOP_D / 2, r_circ / 2)
    roof_h = floor(round((r_circ - r_min) / k / LAYER, 6)) * LAYER
    r_top = r_circ - roof_h * k
    roof = bd.Pos(0, 0, depth) * bd.Cone(r_circ, r_top, roof_h, align=UP)
    return prism + roof


def hex_face(af):
    """對邊 af 的正六角(角在 0°、60°…,邊在 30°、90°…)。"""
    return bd.RegularPolygon(af / 2 / cos(radians(30)), 6)
