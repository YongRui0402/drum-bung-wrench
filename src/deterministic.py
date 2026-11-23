"""讓螺牙的建置可重現。

2026-11-20 實測:螺牙(bd_warehouse Thread)用 build123d 的 `&` 切齊,同一份程式每次建出的 STL 雜湊都不同
(在同一個行程連建四次也不同;把 build123d 布林的平行與 clean 關掉也一樣),試印 tag 上重建對不回雜湊,
3d-print-publish 就沒辦法證明發布的是試印過的那一版。直接呼叫 OCP 的 BRepAlgoAPI_Common(關平行、不 clean)
四次都相同 → 螺牙切齊改用這裡的 serial_common。其他件(只有一般布林)跨行程連建三次雜湊相同,不改。
"""
import build123d


def serial_common(a, b):
    """a ∩ b,直接用 OCP 的 BRepAlgoAPI_Common、關平行、不做 clean;回傳 build123d 的 Compound。"""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
    from OCP.collections import List_TopoDS_Shape

    op = BRepAlgoAPI_Common()
    args, tools = List_TopoDS_Shape(), List_TopoDS_Shape()
    args.Append(a.wrapped)
    tools.Append(b.wrapped)
    op.SetArguments(args)
    op.SetTools(tools)
    op.SetRunParallel(False)
    op.Build()
    assert op.IsDone()
    return build123d.Compound(op.Shape())
