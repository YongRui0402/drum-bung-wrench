"""共用尺寸:值全部取自 量測/尺寸表.md(行尾註明哪一列),建幾何的程式只 import 這裡的名字。

座標(使用時):z = 0 是蓋頂平邊(= 扳手底盤底面),z < 0 伸進蓋子;蓋子的軸是 Z。
"""
from math import asin, degrees, tan, radians

# ───────────── 蓋子實物(尺寸表上半) ─────────────
FLANGE_D = 73.0          # 尺寸表:法蘭外徑
FLANGE_T = 5.4           # 尺寸表:法蘭厚
BOWL_D = 52.0            # 尺寸表:碗內徑(兩凹槽之間)
BOWL_DEPTH = 12.0        # 尺寸表:碗深
BRK_IN_R = 36.8 / 2      # 尺寸表:對面兩道弧牆內距(÷2 = 弧牆內面半徑)
BRK_T = 3.0              # 尺寸表:弧牆厚
BRK_OUT_R = BRK_IN_R + BRK_T
BRK_CHORD = 12.0         # 尺寸表:弧牆長度(兩端直線距離,端點在碗壁)
BRK_IN_HALF = degrees(asin(BRK_CHORD / 2 / BRK_IN_R))   # 內側弧牆的半角(弦長 12 取在弧牆內面,包絡取大)
POCKET_WALL_DEG = 45.0   # 尺寸表:凹槽在碗壁處的圓周角(1/8 圈;A:print/酒精桶蓋扳手-bung-wrench/2026-11-20-3 實插)
BRK_HALF = POCKET_WALL_DEG / 2   # 「＼＿／」兩端斜到碗壁的半角(回饋單 2026-11-20-2 PF-02:原本當成徑向直牆、只開 ±13.3°)
POCKET_W = 4.0           # 尺寸表:凹槽徑向寬  # B級待實測:配合測試片插進蓋子,爪能否到底
PLAT_DEPTH = 6.0         # 尺寸表:凹槽平台深  # B級待實測:配合測試片底盤是否貼平蓋頂
SLOT_DEPTH = 12.0        # 尺寸表:凹槽窄縫深(貼外側牆)  # B級待實測:同上
SLOT_W = 2.0             # 尺寸表:凹槽窄縫寬  # B級待實測:爪的細段能否插進窄縫
WELL_D = 24.0            # 尺寸表:中心井內牙最窄徑
WELL_DEPTH = 11.0        # 尺寸表:中心井深(從碗底)
RIB_W = 3.0              # 尺寸表:直肋寬
RIB_H = 1.0              # 尺寸表:直肋高  # B級待實測:配合測試片能否插過直肋
RIB_N = 4                # 尺寸表:直肋條數
THREAD_MAJOR = 63.2      # 尺寸表:外牙牙峰外徑
THREAD_MINOR = 57.6      # 尺寸表:外牙牙底徑
THREAD_PITCH = 5.0       # 尺寸表:牙距  # B級待實測:牙環短段 5.0 / 5.08 兩段試轉
THREAD_TURNS = 3         # 尺寸表:牙圈數
CAP_H = 26.6             # 尺寸表:蓋子總高
FLANGE_TO_BOTTOM = 21.0  # 尺寸表:法蘭下緣到蓋底  # B級待實測:牙環短段試轉
BRK_END_T = 1.5          # 尺寸表:弧牆兩端短牆厚(示意件用)  # B級待實測:沒量,只給示意件與干涉檢查

# ───────────── 印表機(Bambu Lab X2D 的規格與限制,2026-11-20) ─────────────
LAYER = 0.20             # 尺寸表:層高(README「關鍵高度與層高」)
EMBED = 0.1              # 規格與限制.md 設計規則:新特徵吃進母體 0.1
CHAMFER_DEG = 45         # 規格與限制.md:self_support_chamfer_deg(實測 A)

# ───────────── B 配合測試片(尺寸表「建模自定」) ─────────────
# 間隙(每邊)三個變體,只差這一個尺寸;讀自 規格與限制.md:fit_clearance_mm.snug/through 是 null
# → reference_b.hole_clearance_mm:grip 0.2、pass 0.5(直徑)= 每邊 0.10、0.25;C 再放大給撬爛的毛邊
FIT_GAP = {"A": 0.10, "B": 0.25, "C": 0.40}   # 尺寸表:配合測試片間隙(每邊)  # B級待實測:三片各插一次,挑最緊而插得到底的
RIB_GROOVE_H = 1.4       # 尺寸表:塞子淺溝深(取直肋高的上限 1.4,不做變體)
CLAW_W = 7.0             # 尺寸表:爪的圓周寬(弦長)  # B級待實測:凹槽圓周寬沒量;8 會撞到示意端牆的內側(「＼＿／」越靠弧牆越窄)
DEPTH_MARGIN = 0.6       # 尺寸表:爪底離平台/窄縫底的餘量(3 層;深度是整數估計)
BOWL_MARGIN = 0.4        # 尺寸表:塞子底離碗底的餘量(2 層)
WELL_MARGIN = 1.0        # 尺寸表:定位柱尖離井底的餘量(不碰 knockout)
COUPON_DISK_D = 72.0     # 尺寸表:測試片底盤外徑(= 插頭底盤,< 法蘭外徑 73)
COUPON_DISK_T = 2.0      # 尺寸表:測試片底盤厚(10 層)
COUPON_SPAN_DEG = 100.0  # 尺寸表:測試片只印 ±50°(約 1/4 圈,使用者 2026-11-20 建議;含一個凹槽與兩側直肋淺溝)
LEAD_IN = 0.8            # 尺寸表:塞子與爪尖的導角(45°)
PILOT_LEAD_IN = 1.0      # 尺寸表:定位柱尖導角
PILOT_WALL = 2.0         # 尺寸表:測試片中心挖空後定位柱管壁(≥ min_wall 0.8;只測試片挖)
DISK_CHAMFER_BED = 0.4   # 尺寸表:底盤貼熱床那一圈倒角(防象腳)
DISK_CHAMFER_TOP = 0.6   # 尺寸表:底盤上緣倒角
MARK_DEPTH = 0.4         # 尺寸表:刻字深(2 層)
MARK_SIZE = 4.0          # 尺寸表:刻字字高

# 由上面算出來的高度(使用時的 z;全部是 0.2 的倍數,下面有 assert)
PLUG_BOTTOM = -(BOWL_DEPTH - BOWL_MARGIN)            # -11.6
CLAW_WIDE_BOTTOM = -(PLAT_DEPTH - DEPTH_MARGIN)      # -5.4
CLAW_FINGER_BOTTOM = -(SLOT_DEPTH - DEPTH_MARGIN)    # -11.4
PILOT_TIP = -(BOWL_DEPTH + WELL_DEPTH - WELL_MARGIN) # -22.0

# ───────────── 牙環短段(尺寸表「建模自定」) ─────────────
RING_PITCHES = {"5.00": THREAD_PITCH}               # 尺寸表:牙距(使用者 量的 5.0;回饋單 2026-11-20-2 後只做一種)
RING_VARIANTS = {"A": 0.7, "B": 1.0}   # 尺寸表:內牙徑向間隙(每邊)兩個變體  # B級待實測:1/2 圈牙環轉得順不順(回饋單 2026-11-20-2 PF-01:0.4 一圈後越轉越緊)
THREAD_RAD_CLR = RING_VARIANTS["B"]   # C 方盒用 B 1.0:回饋單 2026-11-20-3 ring_B 實測轉得順、有貼合(A 沒印)
RING_CREST_W = 0.4       # 尺寸表:內牙牙頂寬(0.6 → 0.4,軸向間隙加大)
RING_SPAN_DEG = 180.0    # 尺寸表:牙環只印 1/2 圈(C 形,使用者 2026-11-20 建議)
LOAD_FLANK_DEG = 7.0     # 尺寸表:承力面角度(從垂直軸的平面量)  # B級待實測:牙型角度卡尺量不到
TRAIL_FLANK_DEG = 50.0   # 尺寸表:內牙另一面角度(從垂直軸的平面量;列印時朝下,離垂直 40° 留 5° 餘量)  # B級待實測:同上
CAP_TRAIL_FLANK_DEG = 45.0   # 尺寸表:蓋子外牙另一面角度(示意件用)  # B級待實測:牙型角度量不到
CAP_CREST_W = 0.6        # 尺寸表:蓋子外牙牙頂寬(示意件用)  # B級待實測:沒量
RING_TURNS = 2           # 尺寸表:牙環短段圈數
RING_OD = 76.0           # 尺寸表:牙環外徑(自定;牆厚約 6)
RING_ENTRY_CHAMFER = 1.0  # 尺寸表:牙環入口導角高(貼熱床那一面,只削牙頂)
ENTRY_DEG = 40.0         # 尺寸表:入口導角面離垂直的角度(< 45 留 5° 餘量)
ENTRY_OVERRUN = 0.5      # 尺寸表:導角圓錐越過牙頂再收尾的距離(避免和牙頂共邊)

THREAD_DEPTH = (THREAD_MAJOR - THREAD_MINOR) / 2     # 2.8
RING_APEX_R = THREAD_MINOR / 2 + THREAD_RAD_CLR       # 內牙牙頂(最內)半徑
RING_ROOT_R = THREAD_MAJOR / 2 + THREAD_RAD_CLR       # 內牙牙根(孔壁)半徑

def layer_ceil(h):
    """往上取到層高的整數倍(進位,和印表機一樣)。"""
    from math import ceil
    return round(ceil(round(h / LAYER, 6)) * LAYER, 4)

RING_H = layer_ceil(RING_TURNS * max(RING_PITCHES.values()))   # 2 × 5.08 = 10.16 → 10.2

# ───────────── 正式三件(尺寸表「建模自定:正式三件」) ─────────────
PLUG_GAP = FIT_GAP["B"]  # 尺寸表:插頭配合間隙(每邊);回饋單 2026-11-20-3 coupon_B 插得進、使用者 可以接受
PLUG_DISK_D = COUPON_DISK_D   # 尺寸表:插頭底盤外徑(< 法蘭外徑 73)
PLUG_DISK_T = 5.0        # 尺寸表:插頭底盤厚(25 層)
PLUG_CORE_D = 16.0       # 尺寸表:插頭中心通孔(省料;軸心剪應力接近 0,抗扭少 < 4%;使用者 2026-11-20 選)
HUB_D = 50.0             # 尺寸表:輪轂外徑(插頭與舵輪共用)
CONE_DEG = 45.0          # 尺寸表:底盤接輪轂斜面離垂直的角度(使用者 定案 45°,免支撐)
JOINT_Z = 35.6           # 尺寸表:舵輪底面(= 插頭頂面)離蓋頂高度(舵輪離蓋頂約 4 cm,輪圈中心 ≈ 42)
TEE_LEN = 240.0          # 尺寸表:T 型把手總長(使用者 2026-11-20:雙手各 150 N 約 29 N·m ≥ 原廠 27)
TEE_SEC_H = 18.0         # 尺寸表:臂高(90 層;= 輪轂高 WHEEL_HUB_H,頂面齊平)
TEE_ROOT_W = 26.0        # 尺寸表:臂接輪轂處寬(XY 加寬分散根部應力)
TEE_NECK_R = 45.0        # 尺寸表:臂最細處半徑(握把起點)
TEE_NECK_W = 20.0        # 尺寸表:臂最細處寬
GRIP_D = 25.0            # 尺寸表:握把尖端寬(XY;沿用舵輪 A 錐形握把)
TEE_TOP_CHAMFER = 4.5    # 尺寸表:T 把上緣一圈 45° 倒角(截面接近八角、看得出錐形;回饋單 2026-11-20-7:3 時像方條)
TEE_BOTTOM_CHAMFER = 4.5 # 尺寸表:T 把下緣一圈倒角水平長(面離垂直 OCT_BOTTOM_DEG,和上緣一起讓截面接近八角)
TEE_JOINT_FILLET = 10.0  # 尺寸表:臂接輪轂的凹角圓角(俯視 XY,分散根部應力)
TEE_TIP_FILLET = 6.0     # 尺寸表:臂尖外角圓角(俯視 XY)
HUB_TOP_CHAMFER = 1.0    # 尺寸表:輪轂頂緣倒角
OCT_BOTTOM_DEG = 40.0    # 尺寸表:八角截面朝下兩個倒角離垂直的角度(< 45 留 5°;45° 的旋轉錐三角化後 45.6°)
WHEEL_HUB_H = 18.0       # 尺寸表:把手本體高(90 層;輪轂與臂頂面齊平,回饋單 2026-11-20-5)
HEX_AF = 30.0            # 尺寸表:輪轂六角對邊(活動扳手)
HEX_H = 14.0             # 尺寸表:六角高(70 層)
HEX_CHAMFER = 0.6        # 尺寸表:六角頂緣倒角
KEY_AF = 24.0            # 尺寸表:六角鍵對邊(舵輪↔插頭傳扭力,另印一件、躺著印)
KEY_SOCKET_DEPTH = 12.0  # 尺寸表:六角鍵插進每一邊的深度(60 層)
KEY_CLR = 0.2            # 尺寸表:六角槽對邊公差;讀自 規格與限制.md:nut_trap_clearance_mm.snug 是 null → reference_b.nut_across_flats_clearance_mm  # B級待實測:鍵能否壓入且不晃
KEY_END_MARGIN = 0.2     # 尺寸表:鍵長比兩槽深度和短(1 層,讓兩件貼平)
SCREW_N = 3              # 尺寸表:M2×12 自攻螺絲數(使用者 有 4~20 各長度)
SCREW_D = 2.0            # 尺寸表:螺絲外徑(M2)
SCREW_LEN = 12.0         # 尺寸表:螺絲長
SCREW_HEAD_D = 3.8       # 尺寸表:M2 盤頭直徑  # B級待實測:沒量,M2 盤頭常見 3.5~4.0
SCREW_R = 18.0           # 尺寸表:螺絲孔所在半徑(六角邊 15 外 0.85;T 把倒角放大到 4.5 後頂面平台到 r 20.5;回饋單 2026-11-20-7)
SCREW_PILOT_D = 1.6      # 尺寸表:自攻預留孔  # B級待實測:鎖得進、不裂
SCREW_PASS_D = SCREW_D + 0.5    # 讀自 規格與限制.md:fit_clearance_mm.through 是 null → reference_b.hole_clearance_mm.pass  # B級待實測
SCREW_CB_D = SCREW_HEAD_D + 0.5 # 同上(螺絲頭沉孔)
SCREW_BITE = 6.0         # 尺寸表:螺絲咬進插頭的長度(另 6 穿過舵輪)
SCREW_PILOT_EXTRA = 1.0  # 尺寸表:預留孔比咬入長度深
ROOF_TOP_D = 0.8         # 尺寸表:盲孔頂錐收尾的小平頂直徑(橋接 0.8 ≤ bridge_max_mm)
SOCKET_ROOF_DEG = 40.0   # 尺寸表:盲孔頂錐面離垂直角度(< 45 留 5°;45 剛好在門檻上時三角化會超過)
BOX_W = 80.0             # 尺寸表:C 方盒外寬(使用者 2026-11-20:90 → 80;四邊最薄處壁厚 7.4)
BOX_H = 26.0             # 尺寸表:C 方盒高(130 層)
BOX_HOLE_D = 2.2         # 尺寸表:四角 M2 插孔直徑(螺絲桿插進去站著、頭露在盒頂;使用者 2026-11-20 選,原 Ø7)  # B級待實測:插得進、倒過來不掉
BOX_HOLE_OFF = 34.0      # 尺寸表:M2 插孔中心離盒中心(X、Y;離外緣 6、在法蘭 Ø73 外)
BOX_HOLE_DEPTH = 13.0    # 尺寸表:插孔直壁深(從盒頂;M2×12 整支插進去,65 層)
BOX_CHAMFER = 0.6        # 尺寸表:方盒邊倒角

WHEEL_FLAT_Z = JOINT_Z   # 輪圈、握把、輻條、輪轂的底都削平在同一個面(列印時貼熱床)

for _name, _z in {"PLUG_BOTTOM": PLUG_BOTTOM, "CLAW_WIDE_BOTTOM": CLAW_WIDE_BOTTOM,
                  "CLAW_FINGER_BOTTOM": CLAW_FINGER_BOTTOM, "PILOT_TIP": PILOT_TIP,
                  "COUPON_DISK_T": COUPON_DISK_T, "RING_H": RING_H, "PLUG_DISK_T": PLUG_DISK_T, "JOINT_Z": JOINT_Z,
                  "TEE_SEC_H": TEE_SEC_H, "WHEEL_HUB_H": WHEEL_HUB_H, "HEX_H": HEX_H, "BOX_H": BOX_H,
                  "KEY_SOCKET_DEPTH": KEY_SOCKET_DEPTH}.items():
    assert abs(_z / LAYER - round(_z / LAYER)) < 1e-6, f"{_name} = {_z} 不是層高的倍數"
