"""FlowForge AI 涓枃楂樿川閲廝PT鐢熸垚鍣?- 瑕嗙洊鍏ㄩ儴涓夎禌閬?"""
import os
import sys
_VENV_SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'venv', 'Lib', 'site-packages')
if os.path.isdir(_VENV_SITE):
    sys.path.insert(0, _VENV_SITE)

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
import os

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

BG_DARK = RGBColor(0x0D, 0x11, 0x17)
BG_CARD = RGBColor(0x16, 0x1B, 0x22)
BLUE = RGBColor(0x58, 0xA6, 0xFF)
GREEN = RGBColor(0x3F, 0xB9, 0x50)
ORANGE = RGBColor(0xF0, 0x88, 0x3E)
RED = RGBColor(0xF8, 0x51, 0x4D)
PURPLE = RGBColor(0xBC, 0x8C, 0xFF)
WHITE = RGBColor(0xE6, 0xED, 0xF3)
GRAY = RGBColor(0x8B, 0x94, 0x9E)
CYAN = RGBColor(0x39, 0xC5, 0xCF)

def add_bg(slide, color=BG_DARK):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_textbox(slide, left, top, width, height, text, size=18, color=WHITE, bold=False, align=PP_ALIGN.LEFT, font='Microsoft YaHei'):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = font
    p.alignment = align
    return txBox

def add_shape(slide, left, top, width, height, color, shape_type=MSO_SHAPE.ROUNDED_RECTANGLE):
    shape = slide.shapes.add_shape(shape_type, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape

def add_card(slide, left, top, width, height, title, content, title_color=BLUE, accent=BLUE):
    card = add_shape(slide, left, top, width, height, BG_CARD)
    bar = add_shape(slide, left, top, Inches(0.06), height, accent)
    add_textbox(slide, left + Inches(0.25), top + Inches(0.15), width - Inches(0.4), Inches(0.5), title, size=16, color=title_color, bold=True)
    add_textbox(slide, left + Inches(0.25), top + Inches(0.65), width - Inches(0.4), height - Inches(0.8), content, size=12, color=GRAY)
    return card

def slide_blank():
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide)
    return slide

# ===== Slide 1: 灏侀潰 =====
s = slide_blank()
add_shape(s, Inches(0), Inches(0), Inches(13.333), Inches(0.08), BLUE)
add_shape(s, Inches(0), Inches(7.42), Inches(13.333), Inches(0.08), BLUE)
add_textbox(s, Inches(1), Inches(1.5), Inches(11.333), Inches(1.2), 'FlowForge AI', size=54, color=BLUE, bold=True, align=PP_ALIGN.CENTER)
add_textbox(s, Inches(1), Inches(2.8), Inches(11.333), Inches(0.6), 'AI椹卞姩鐨勫叏娴佺▼杞欢宸ョ▼骞冲彴', size=28, color=WHITE, align=PP_ALIGN.CENTER)
add_textbox(s, Inches(1), Inches(3.6), Inches(11.333), Inches(0.5), '澶氭櫤鑳戒綋鍗忎綔 路 DAG宸ヤ綔娴佺紪鎺?路 瀹炴椂璇勫垎浼樺寲', size=18, color=GRAY, align=PP_ALIGN.CENTER)
badges = ['AI脳Blockchain', 'BOT Chain BUILD BEYOND 2026', '鍏叡鐗╁搧']
bx = Inches(3.5)
for b in badges:
    w = Inches(2.1)
    sh = add_shape(s, bx, Inches(4.6), w, Inches(0.5), BG_CARD)
    add_textbox(s, bx, Inches(4.65), w, Inches(0.4), b, size=13, color=CYAN, align=PP_ALIGN.CENTER)
    bx += w + Inches(0.2)
add_textbox(s, Inches(1), Inches(6.2), Inches(11.333), Inches(0.4), '娌欏害鍥㈤槦 (Shadu Team)  |  2026骞?0鏈? |  v2.55', size=14, color=GRAY, align=PP_ALIGN.CENTER)

# ===== Slide 2: 椤圭洰姒傝堪 =====
s = slide_blank()
add_textbox(s, Inches(0.6), Inches(0.3), Inches(12), Inches(0.6), '椤圭洰姒傝堪', size=32, color=BLUE, bold=True)
add_shape(s, Inches(0.6), Inches(0.95), Inches(2), Inches(0.05), BLUE)
add_textbox(s, Inches(0.6), Inches(1.2), Inches(12), Inches(0.8),
    'FlowForge AI 鏄竴涓熀浜庡鏅鸿兘浣撳崗浣滅殑鍏ㄦ祦绋婣I杞欢宸ョ▼骞冲彴锛岃鐩栭渶姹傚垎鏋愩€佷唬鐮佺敓鎴愩€佹祴璇曘€佸畨鍏ㄦ壂鎻忋€佹枃妗ｇ敓鎴愩€侀儴缃插叏閾捐矾銆傞€氳繃DAG宸ヤ綔娴佺紪鎺?3绉嶄笓涓氭櫤鑳戒綋锛屽疄鐜颁粠闇€姹傚埌浜や粯鐨勭鍒扮鑷姩鍖栵紝閰嶅悎瀹炴椂浜旂淮璇勫垎绯荤粺鎸佺画浼樺寲杈撳嚭璐ㄩ噺銆?,
    size=15, color=WHITE)
cards = [
    ('鏍稿績鑳藉姏', '13绉嶄笓涓氭櫤鑳戒綋\n22绉嶅伐浣滄祦妯℃澘\nDAG骞惰璋冨害\n瀹炴椂SSE鎺ㄩ€?, BLUE),
    ('鎶€鏈灦鏋?, 'FastAPI + Vue3 + SQLite\n178涓狝PI绔偣\n500+婧愭枃浠禱n寰湇鍔″寲璁捐', GREEN),
    ('璐ㄩ噺淇濋殰', '浜旂淮璇勫垎寮曟搸\n鐡堕绐佺牬寤鸿\n鍚堣瀹夊叏妫€鏌nEVM閾句笂瀛樿瘉', ORANGE),
    ('浜や粯鎴愭灉', '瀹屾暣鍙繍琛孌emo\n涓枃PPT婕旂ず\n楂樻竻瑙嗛浠嬬粛\n涓夎禌閬撳叏瑕嗙洊', PURPLE),
]
cx = Inches(0.6)
for title, content, color in cards:
    add_card(s, cx, Inches(3.2), Inches(2.9), Inches(3.5), title, content, title_color=color, accent=color)
    cx += Inches(3.1)

# ===== Slide 3: 绯荤粺鏋舵瀯 =====
s = slide_blank()
add_textbox(s, Inches(0.6), Inches(0.3), Inches(12), Inches(0.6), '绯荤粺鏋舵瀯', size=32, color=BLUE, bold=True)
add_shape(s, Inches(0.6), Inches(0.95), Inches(2), Inches(0.05), BLUE)
layers = [
    ('鍓嶇灞曠ず灞?, 'Vue 3 + Naive UI + Vue Flow + ECharts\n宸ヤ綔娴佺敾甯?路 瀹炴椂鐩戞帶 路 璇勫垎浠〃鐩?路 鎵ц鏃堕棿绾?, BLUE, Inches(1.2)),
    ('API缃戝叧灞?, 'FastAPI 路 178涓猂EST绔偣 路 SSE瀹炴椂鎺ㄩ€?路 WebSocket鏃ュ織娴乗n璁よ瘉閴存潈 路 闄愭祦閰嶉 路 瀹¤鏃ュ織', GREEN, Inches(2.4)),
    ('涓氬姟鏈嶅姟灞?, 'DAG璋冨害鍣?路 鏅鸿兘浣撹繍琛屾椂 路 璇勫垎寮曟搸 路 鐡堕鍒嗘瀽\n鎴愭湰璁＄畻 路 鍚堣妫€鏌?路 妯″瀷閫夋嫨 路 鑷姩淇', ORANGE, Inches(3.6)),
    ('鍩虹璁炬柦灞?, 'SQLite鎸佷箙鍖?路 妯″瀷瀹㈡埛绔?路 閰嶇疆涓績 路 SSE缃戝叧\n瀹¤鏃ュ織 路 鎬ц兘鑱氬悎 路 閾句笂瀛樿瘉 路 缂撳瓨', PURPLE, Inches(4.8)),
]
for title, content, color, top in layers:
    sh = add_shape(s, Inches(0.6), top, Inches(12.1), Inches(1.0), BG_CARD)
    add_shape(s, Inches(0.6), top, Inches(0.08), Inches(1.0), color)
    add_textbox(s, Inches(0.9), top + Inches(0.1), Inches(3), Inches(0.4), title, size=16, color=color, bold=True)
    add_textbox(s, Inches(0.9), top + Inches(0.5), Inches(11.5), Inches(0.5), content, size=12, color=GRAY)
add_textbox(s, Inches(0.6), Inches(6.2), Inches(12), Inches(0.5), '鍥涘眰鏋舵瀯 路 娓呮櫚鍒嗙 路 楂樺唴鑱氫綆鑰﹀悎 路 鏄撴墿灞曟槗缁存姢', size=14, color=CYAN, align=PP_ALIGN.CENTER)

# ===== Slide 4: 13绉嶆櫤鑳戒綋 =====
s = slide_blank()
add_textbox(s, Inches(0.6), Inches(0.3), Inches(12), Inches(0.6), '13绉嶄笓涓氭櫤鑳戒綋', size=32, color=BLUE, bold=True)
add_shape(s, Inches(0.6), Inches(0.95), Inches(2), Inches(0.05), BLUE)
agents = [
    ('浠ｇ爜瀹℃煡', 'code-reviewer', '娣卞害浠ｇ爜璐ㄩ噺鍒嗘瀽\n瀹夊叏婕忔礊路鎬ц兘路鍙淮鎶ゆ€?, BLUE),
    ('娴嬭瘯鐢熸垚', 'test-generator', '鑷姩鐢熸垚鍗曞厓娴嬭瘯\n瑕嗙洊鐜囨渶澶у寲', GREEN),
    ('鏂囨。鐢熸垚', 'doc-generator', 'API鏂囨。路鐢ㄦ埛鎵嬪唽\n鍙樻洿鏃ュ織鑷姩鐢熸垚', ORANGE),
    ('缂洪櫡璇婃柇', 'defect-diagnostician', '鏍瑰洜鍒嗘瀽路淇寤鸿\n鍘嗗彶缂洪櫡妯″紡鍖归厤', RED),
    ('瀹夊叏鎵弿', 'security-scanner', 'OWASP Top 10\n渚濊禆婕忔礊路浠ｇ爜娉ㄥ叆', PURPLE),
    ('CI/CD娴佹按绾?, 'cicd-pipeline', '鑷姩鍖栨瀯寤洪儴缃瞈n璐ㄩ噺闂ㄧ路鐏板害鍙戝竷', CYAN),
    ('API璁捐', 'api-designer', 'RESTful璁捐瑙勮寖\nOpenAPI鑷姩鐢熸垚', BLUE),
    ('鎬ц兘浼樺寲', 'performance-optimizer', '鐡堕瀹氫綅路绠楁硶浼樺寲\n璧勬簮鍒╃敤鐜囨彁鍗?, GREEN),
    ('浠ｇ爜閲嶆瀯', 'refactoring-agent', '璁捐妯″紡搴旂敤\n鎶€鏈€烘秷闄?, ORANGE),
    ('渚濊禆鍒嗘瀽', 'dependency-analyzer', '鍐茬獊妫€娴嬄风増鏈崌绾n瀹夊叏婕忔礊鎵弿', RED),
    ('浠ｇ爜鎼滅储', 'code-searcher', '璇箟鍖栦唬鐮佹绱n璺ㄤ粨搴撲緷璧栬拷韪?, PURPLE),
    ('璐ㄩ噺闂ㄧ', 'quality-gate', '澶氱淮搴﹁川閲忚瘎浼癨n鍑嗗叆鍑嗗嚭鏍囧噯', CYAN),
    ('鍏ㄦ爤瀹℃煡', 'fullstack-reviewer', '鍓嶅悗绔竴浣撳寲瀹℃煡\n鏋舵瀯鍚堢悊鎬ц瘎浼?, BLUE),
]
cols = 4
for i, (name, aid, desc, color) in enumerate(agents):
    r, c = divmod(i, cols)
    cx = Inches(0.6 + c * 3.1)
    cy = Inches(1.2 + r * 1.95)
    sh = add_shape(s, cx, cy, Inches(2.9), Inches(1.75), BG_CARD)
    add_shape(s, cx, cy, Inches(2.9), Inches(0.06), color)
    add_textbox(s, cx + Inches(0.15), cy + Inches(0.12), Inches(2.6), Inches(0.35), name, size=14, color=color, bold=True)
    add_textbox(s, cx + Inches(0.15), cy + Inches(0.5), Inches(2.6), Inches(0.25), aid, size=10, color=GRAY)
    add_textbox(s, cx + Inches(0.15), cy + Inches(0.8), Inches(2.6), Inches(0.85), desc, size=10, color=WHITE)

# ===== Slide 5: 浜旂淮璇勫垎寮曟搸 =====
s = slide_blank()
add_textbox(s, Inches(0.6), Inches(0.3), Inches(12), Inches(0.6), '浜旂淮璇勫垎寮曟搸', size=32, color=BLUE, bold=True)
add_shape(s, Inches(0.6), Inches(0.95), Inches(2), Inches(0.05), BLUE)
add_textbox(s, Inches(0.6), Inches(1.1), Inches(12), Inches(0.5), '鐙垱浜旂淮璐ㄩ噺璇勪及浣撶郴锛屽疄鏃堕噺鍖栨瘡娆℃墽琛岀殑缁煎悎璐ㄩ噺锛岄┍鍔ㄦ寔缁紭鍖栭棴鐜?, size=14, color=GRAY)
dims = [
    ('姝ｇ‘鎬?Correctness', '鏉冮噸 25%', '鍔熻兘瀹炵幇鏄惁绗﹀悎闇€姹傝鏍糪n杈圭晫鏉′欢路寮傚父澶勭悊路閫昏緫瀹屾暣鎬?, BLUE),
    ('瀹屾暣鎬?Completeness', '鏉冮噸 20%', '闇€姹傝鐩栫▼搴β峰姛鑳界己澶辨娴媆n鎺ュ彛瀹屽鎬锋枃妗ｉ綈鍏ㄥ害', GREEN),
    ('鍙婃椂鎬?Timeliness', '鏉冮噸 20%', '浜や粯閫熷害路鍝嶅簲寤惰繜\n杩唬鏁堢巼路SLA杈炬垚鐜?, ORANGE),
    ('鍒涙柊鎬?Innovation', '鏉冮噸 15%', '鏂规鍒涢€犳€锋妧鏈厛杩涙€n鏋舵瀯鍚堢悊鎬峰彲鎵╁睍鎬?, PURPLE),
    ('绋冲畾鎬?Stability', '鏉冮噸 20%', '閿欒鐜嚶锋垚鍔熺巼路娉㈠姩搴n璧勬簮鍗犵敤路鎭㈠鑳藉姏', RED),
]
for i, (name, weight, desc, color) in enumerate(dims):
    cx = Inches(0.6 + i * 2.5)
    sh = add_shape(s, cx, Inches(1.8), Inches(2.3), Inches(4.5), BG_CARD)
    add_shape(s, cx, Inches(1.8), Inches(2.3), Inches(0.06), color)
    add_textbox(s, cx + Inches(0.15), Inches(1.95), Inches(2), Inches(0.35), name, size=13, color=color, bold=True)
    add_textbox(s, cx + Inches(0.15), Inches(2.35), Inches(2), Inches(0.25), weight, size=11, color=CYAN)
    add_textbox(s, cx + Inches(0.15), Inches(2.7), Inches(2), Inches(3), desc, size=11, color=WHITE)
add_textbox(s, Inches(0.6), Inches(6.5), Inches(12), Inches(0.5), '璇勫垎 鈫?鐡堕璇嗗埆 鈫?绐佺牬寤鸿 鈫?鑷姩浼樺寲 鈫?鍐嶈瘎鍒? 闂幆椹卞姩璐ㄩ噺鎸佺画鎻愬崌', size=13, color=CYAN, align=PP_ALIGN.CENTER)

# ===== Slide 6: AI脳Blockchain 璧涢亾 =====
s = slide_blank()
add_textbox(s, Inches(0.6), Inches(0.3), Inches(12), Inches(0.6), '璧涢亾涓€锛欰I脳Blockchain', size=32, color=BLUE, bold=True)
add_shape(s, Inches(0.6), Inches(0.95), Inches(2), Inches(0.05), BLUE)
add_textbox(s, Inches(0.6), Inches(1.1), Inches(12), Inches(0.5), 'AI鏅鸿兘浣撳崗浣滄垚鏋滀笂閾惧瓨璇侊紝鏋勫缓鍙俊鍘讳腑蹇冨寲杞欢宸ョ▼鍗忚', size=14, color=GRAY)
features = [
    ('閾句笂瀛樿瘉', '姣忔AI鏅鸿兘浣撴墽琛岀粨鏋淺n鐢熸垚鍞竴鍝堝笇涓婇摼瀛樿瘉\n涓嶅彲绡℃敼路鍙拷婧峰彲楠岃瘉', BLUE, Inches(0.6), Inches(1.8)),
    ('EVM鍏煎', '鏀寔BOT Chain EVM\nSolidity鏅鸿兘鍚堢害浜や簰\nWeb3.py闆嗘垚路ABI鑷姩鐢熸垚', GREEN, Inches(6.8), Inches(1.8)),
    ('鍘讳腑蹇冨寲璇勫垎', '浜旂淮璇勫垎缁撴灉涓婇摼\n绀惧尯鍏辫瘑路閫忔槑鍙璁n璇勫垎鏉冮噸鍘讳腑蹇冨寲娌荤悊', ORANGE, Inches(0.6), Inches(4.2)),
    ('璺ㄩ摼妗ユ帴', 'BOT Chain 鈫?Ethereum\n璧勪骇璺ㄩ摼路鏁版嵁璺ㄩ摼\n澶氶摼鏅鸿兘浣撳崗浣?, PURPLE, Inches(6.8), Inches(4.2)),
]
for title, content, color, left, top in features:
    add_card(s, left, top, Inches(5.9), Inches(2.2), title, content, title_color=color, accent=color)
add_textbox(s, Inches(0.6), Inches(6.7), Inches(12), Inches(0.4), '鎶€鏈爤锛歐eb3.py 路 Solidity 路 EVM 路 BOT Chain SDK 路 閾句笂浜嬩欢鐩戝惉', size=12, color=CYAN)

# ===== Slide 7: BOT Chain 璧涢亾 =====
s = slide_blank()
add_textbox(s, Inches(0.6), Inches(0.3), Inches(12), Inches(0.6), '璧涢亾浜岋細BOT Chain BUILD BEYOND 2026', size=28, color=GREEN, bold=True)
add_shape(s, Inches(0.6), Inches(0.95), Inches(2), Inches(0.05), GREEN)
add_textbox(s, Inches(0.6), Inches(1.1), Inches(12), Inches(0.5), '鍦˙OT Chain涓荤綉閮ㄧ讲FlowForge AI锛屼负鐢熸€佹彁渚汚I椹卞姩鐨勫紑鍙戝伐鍏?, size=14, color=GRAY)
items = [
    ('涓荤綉閮ㄧ讲', 'RPC: rpc.botchain.ai\nScan: scan.botchain.ai\nDEX/Wallet/Bridge鍏ㄩ泦鎴?, GREEN),
    ('EVM杩佺Щ瀹屾垚', 'EVM鍏煎閾惧崌绾n鏅鸿兘鍚堢害Solidity鏀寔\nMetaMask閽卞寘杩炴帴', BLUE),
    ('AI寮€鍙戝伐鍏?, 'BOT Chain鏅鸿兘鍚堢害\nAI杈呭姪缂栧啓路瀹夊叏瀹¤\nGas浼樺寲寤鸿', ORANGE),
    ('鐢熸€佽础鐚?, '寮€婧怱DK路寮€鍙戣€呮枃妗n鎶€鏈垎浜风ぞ鍖哄缓璁綷n鍏叡鐗╁搧鎹愯禒', PURPLE),
]
for i, (title, content, color) in enumerate(items):
    r, c = divmod(i, 2)
    cx = Inches(0.6 + c * 6.2)
    cy = Inches(1.8 + r * 2.5)
    add_card(s, cx, cy, Inches(5.9), Inches(2.2), title, content, title_color=color, accent=color)

# ===== Slide 8: 鍏叡鐗╁搧璧涢亾 =====
s = slide_blank()
add_textbox(s, Inches(0.6), Inches(0.3), Inches(12), Inches(0.6), '璧涢亾涓夛細鍏叡鐗╁搧', size=32, color=ORANGE, bold=True)
add_shape(s, Inches(0.6), Inches(0.95), Inches(2), Inches(0.05), ORANGE)
add_textbox(s, Inches(0.6), Inches(1.1), Inches(12), Inches(0.5), '寮€婧怉I杞欢宸ョ▼骞冲彴锛屼负寮€鍙戣€呯ぞ鍖烘彁渚涘厤璐广€侀€忔槑銆佸彲澶嶇敤鐨勫叕鍏卞熀纭€璁炬柦', size=14, color=GRAY)
publics = [
    ('寮€婧愬紑鏀?, '鏍稿績寮曟搸瀹屽叏寮€婧怽nMIT璁稿彲璇伮锋棤鍟嗕笟闄愬埗\n绀惧尯椹卞姩路閫忔槑娌荤悊', ORANGE),
    ('鍏嶈垂鍙敤', '鍦ㄧ嚎Demo鍏嶈垂浣撻獙\n鏈湴閮ㄧ讲闆舵垚鏈琝n鏃燗PI璐圭敤路鏃燭oken闂ㄦ', GREEN),
    ('鐭ヨ瘑鍏变韩', '瀹屾暣鎶€鏈枃妗n鏋舵瀯璁捐路鏈€浣冲疄璺礬nAPI鏂囨。路閮ㄧ讲鎸囧崡', BLUE),
    ('鍙鐢ㄦ€?, '妯″潡鍖栬璁÷峰嵆鎻掑嵆鐢╘n鏀寔浜屾寮€鍙慭n鏍囧噯鎺ュ彛路鐢熸€佸吋瀹?, PURPLE),
]
for i, (title, content, color) in enumerate(publics):
    r, c = divmod(i, 2)
    cx = Inches(0.6 + c * 6.2)
    cy = Inches(1.8 + r * 2.5)
    add_card(s, cx, cy, Inches(5.9), Inches(2.2), title, content, title_color=color, accent=color)

# ===== Slide 9: Demo鍔熻兘灞曠ず =====
s = slide_blank()
add_textbox(s, Inches(0.6), Inches(0.3), Inches(12), Inches(0.6), 'Demo鍔熻兘灞曠ず', size=32, color=BLUE, bold=True)
add_shape(s, Inches(0.6), Inches(0.95), Inches(2), Inches(0.05), BLUE)
demos = [
    ('宸ヤ綔娴佺紪鎺?, '鍙鍖朌AG鐢诲竷\n鎷栨嫿缂栨帓路瀹炴椂棰勮\n22绉嶆ā鏉夸竴閿垱寤?),
    ('鎵ц鐩戞帶', '瀹炴椂SSE鎺ㄩ€乗n鑺傜偣鐘舵€伮疯繘搴︽潯\n鏃ュ織娴伮锋椂闂寸嚎'),
    ('璇勫垎浠〃鐩?, '浜旂淮闆疯揪鍥綷n瓒嬪娍鏇茬嚎\n鐡堕鍛婅路浼樺寲寤鸿'),
    ('鎴愭湰鍒嗘瀽', 'Token鐢ㄩ噺缁熻\n妯″瀷鎴愭湰鏄庣粏\n30澶╄秼鍔柯烽绠楀憡璀?),
    ('瀹夊叏鍚堣', '鏁忔劅璇嶆娴媆n鍚堣妫€鏌ヂ峰璁℃棩蹇梊nOWASP Top 10鎵弿'),
    ('妯℃澘甯傚満', '15涓競鍦烘ā鏉縗n鍒嗙被绛涢€壜疯瘎鍒嗘帓搴廫n涓€閿垱寤哄伐浣滄祦'),
]
for i, (title, content) in enumerate(demos):
    r, c = divmod(i, 3)
    cx = Inches(0.6 + c * 4.1)
    cy = Inches(1.3 + r * 2.7)
    sh = add_shape(s, cx, cy, Inches(3.9), Inches(2.4), BG_CARD)
    add_shape(s, cx, cy, Inches(3.9), Inches(0.06), BLUE)
    add_textbox(s, cx + Inches(0.2), cy + Inches(0.15), Inches(3.5), Inches(0.4), title, size=15, color=BLUE, bold=True)
    add_textbox(s, cx + Inches(0.2), cy + Inches(0.6), Inches(3.5), Inches(1.7), content, size=12, color=WHITE)

# ===== Slide 10: 绔炰簤浼樺娍 =====
s = slide_blank()
add_textbox(s, Inches(0.6), Inches(0.3), Inches(12), Inches(0.6), '绔炰簤浼樺娍', size=32, color=BLUE, bold=True)
add_shape(s, Inches(0.6), Inches(0.95), Inches(2), Inches(0.05), BLUE)
advantages = [
    ('绔埌绔叏娴佺▼', '浠庨渶姹傚埌閮ㄧ讲鍏ㄩ摼璺鐩栵紝闈炲崟鐐瑰伐鍏?, '鉁?, GREEN),
    ('澶氭櫤鑳戒綋鍗忎綔', '13绉嶄笓涓氭櫤鑳戒綋DAG缂栨帓锛岄潪鍗曚竴妯″瀷', '鉁?, GREEN),
    ('瀹炴椂璇勫垎浼樺寲', '浜旂淮璇勫垎椹卞姩闂幆浼樺寲锛岄潪涓€娆℃€ц緭鍑?, '鉁?, GREEN),
    ('閾句笂瀛樿瘉鍙俊', 'AI鎴愭灉涓婇摼涓嶅彲绡℃敼锛岄潪绂荤嚎榛戠洅', '鉁?, GREEN),
    ('涓枃鍘熺敓鏀寔', '涓枃鐣岄潰路涓枃鏂囨。路涓枃PPT', '鉁?, GREEN),
    ('寮€绠卞嵆鐢?, '涓€閿惎鍔烽浂閰嶇疆路瀹屾暣Demo', '鉁?, GREEN),
]
for i, (title, desc, mark, color) in enumerate(advantages):
    cy = Inches(1.3 + i * 0.95)
    sh = add_shape(s, Inches(0.6), cy, Inches(12.1), Inches(0.8), BG_CARD)
    add_shape(s, Inches(0.6), cy, Inches(0.08), Inches(0.8), color)
    add_textbox(s, Inches(0.9), cy + Inches(0.1), Inches(3.5), Inches(0.5), title, size=16, color=BLUE, bold=True)
    add_textbox(s, Inches(4.5), cy + Inches(0.1), Inches(7), Inches(0.5), desc, size=14, color=WHITE)
    add_textbox(s, Inches(11.8), cy + Inches(0.1), Inches(0.5), Inches(0.5), mark, size=20, color=GREEN, bold=True)

# ===== Slide 11: 鎶€鏈寚鏍?=====
s = slide_blank()
add_textbox(s, Inches(0.6), Inches(0.3), Inches(12), Inches(0.6), '鎶€鏈寚鏍?, size=32, color=BLUE, bold=True)
add_shape(s, Inches(0.6), Inches(0.95), Inches(2), Inches(0.05), BLUE)
metrics = [
    ('500+', '婧愭枃浠?, BLUE),
    ('178', 'API绔偣', GREEN),
    ('13', '涓撲笟鏅鸿兘浣?, ORANGE),
    ('22', '宸ヤ綔娴佹ā鏉?, PURPLE),
    ('5缁?, '璇勫垎浣撶郴', RED),
    ('30澶?, '婕旂ず鏁版嵁', CYAN),
]
for i, (num, label, color) in enumerate(metrics):
    cx = Inches(0.6 + i * 2.1)
    sh = add_shape(s, cx, Inches(1.3), Inches(1.9), Inches(2.0), BG_CARD)
    add_textbox(s, cx, Inches(1.5), Inches(1.9), Inches(0.8), num, size=40, color=color, bold=True, align=PP_ALIGN.CENTER)
    add_textbox(s, cx, Inches(2.5), Inches(1.9), Inches(0.4), label, size=14, color=GRAY, align=PP_ALIGN.CENTER)
quality = [
    '鍚庣锛歅ython 3.12 + FastAPI + SQLModel + SQLite',
    '鍓嶇锛歏ue 3 + TypeScript + Naive UI + Vue Flow + ECharts',
    'AI灞傦細澶氭ā鍨嬮€夋嫨 路 鑷姩闄嶇骇 路 杈撳嚭濂戠害楠岃瘉 路 鑷姩淇',
    '杩愮淮锛歋SE瀹炴椂鎺ㄩ€?路 瀹¤鏃ュ織 路 鎬ц兘鑱氬悎 路 閾句笂瀛樿瘉',
]
for i, q in enumerate(quality):
    add_textbox(s, Inches(0.6), Inches(3.8 + i * 0.6), Inches(12), Inches(0.5), f'鈥?{q}', size=14, color=WHITE)

# ===== Slide 12: 璺嚎鍥?=====
s = slide_blank()
add_textbox(s, Inches(0.6), Inches(0.3), Inches(12), Inches(0.6), '璺嚎鍥?, size=32, color=BLUE, bold=True)
add_shape(s, Inches(0.6), Inches(0.95), Inches(2), Inches(0.05), BLUE)
phases = [
    ('Phase 1 路 宸插畬鎴?, '鏍稿績骞冲彴鎼缓', '澶氭櫤鑳戒綋杩愯鏃禱nDAG璋冨害鍣╘n浜旂淮璇勫垎寮曟搸\n22绉嶅伐浣滄祦妯℃澘', GREEN, '鉁?宸蹭氦浠?),
    ('Phase 2 路 宸插畬鎴?, '鍓嶇鍙鍖?, 'Vue3绠＄悊鎺у埗鍙癨n宸ヤ綔娴佺敾甯僜n瀹炴椂鐩戞帶浠〃鐩榎nSSE瀹炴椂鎺ㄩ€?, GREEN, '鉁?宸蹭氦浠?),
    ('Phase 3 路 杩涜涓?, '鍖哄潡閾鹃泦鎴?, 'BOT Chain涓荤綉閮ㄧ讲\nEVM鍏煎杩佺Щ\n閾句笂瀛樿瘉\n璺ㄩ摼妗ユ帴', ORANGE, '鈿?杩涜涓?),
    ('Phase 4 路 瑙勫垝涓?, '鐢熸€佹墿灞?, '鎻掍欢甯傚満\n寮€鍙戣€匰DK\n绀惧尯娌荤悊\n澶氶摼鏀寔', GRAY, '鈼?瑙勫垝涓?),
]
for i, (phase, title, content, color, status) in enumerate(phases):
    cx = Inches(0.6 + i * 3.1)
    sh = add_shape(s, cx, Inches(1.3), Inches(2.9), Inches(5.0), BG_CARD)
    add_shape(s, cx, Inches(1.3), Inches(2.9), Inches(0.08), color)
    add_textbox(s, cx + Inches(0.15), Inches(1.45), Inches(2.6), Inches(0.35), phase, size=12, color=color, bold=True)
    add_textbox(s, cx + Inches(0.15), Inches(1.85), Inches(2.6), Inches(0.4), title, size=15, color=WHITE, bold=True)
    add_textbox(s, cx + Inches(0.15), Inches(2.4), Inches(2.6), Inches(2.5), content, size=12, color=GRAY)
    add_textbox(s, cx + Inches(0.15), Inches(5.5), Inches(2.6), Inches(0.4), status, size=13, color=color, bold=True)

# ===== Slide 13: 鍥㈤槦浠嬬粛 =====
s = slide_blank()
add_textbox(s, Inches(0.6), Inches(0.3), Inches(12), Inches(0.6), '鍥㈤槦浠嬬粛', size=32, color=BLUE, bold=True)
add_shape(s, Inches(0.6), Inches(0.95), Inches(2), Inches(0.05), BLUE)
add_textbox(s, Inches(0.6), Inches(1.2), Inches(12), Inches(0.5), '娌欏害鍥㈤槦 (Shadu Team)', size=22, color=WHITE, bold=True)
add_textbox(s, Inches(0.6), Inches(1.8), Inches(12), Inches(0.8),
    '涓€鏀笓娉ㄤ簬AI杞欢宸ョ▼鐨勫垱鏂板洟闃燂紝鑷村姏浜庡皢澶氭櫤鑳戒綋鍗忎綔鐞嗗康钀藉湴涓哄彲宸ョ▼鍖栥€佸彲浜や粯銆佸彲澶嶇敤鐨勪骇鍝併€俓n鎴戜滑鐩镐俊AI涓嶅簲璇ュ彧鏄唬鐮佽ˉ鍏ㄥ伐鍏凤紝鑰屽簲璇ユ垚涓鸿疮绌胯蒋浠跺叏鐢熷懡鏈熺殑鏅鸿兘鍗忎綔浼欎即銆?,
    size=14, color=GRAY)
values = [
    ('宸ョ▼鍔″疄', '涓嶅仛绌轰腑妤奸榿\n姣忎釜鍔熻兘閮藉彲杩愯\n姣忎釜Demo閮藉彲楠岃瘉', BLUE),
    ('鎶€鏈繁搴?, '娣卞叆鐞嗚ВAI妯″瀷\n绮鹃€氬垎甯冨紡绯荤粺\n鐔熸倝鍖哄潡閾惧崗璁?, GREEN),
    ('浜у搧鎬濈淮', '鐢ㄦ埛浣撻獙浼樺厛\n涓枃鍘熺敓鏀寔\n寮€绠卞嵆鐢ㄨ璁?, ORANGE),
    ('寮€婧愮簿绁?, '鎷ユ姳寮€鏀剧敓鎬乗n璐＄尞鍏叡鐗╁搧\n绀惧尯椹卞姩鍙戝睍', PURPLE),
]
for i, (title, content, color) in enumerate(values):
    cx = Inches(0.6 + i * 3.1)
    add_card(s, cx, Inches(3.2), Inches(2.9), Inches(3.2), title, content, title_color=color, accent=color)

# ===== Slide 14: 鎰熻阿椤?=====
s = slide_blank()
add_shape(s, Inches(0), Inches(0), Inches(13.333), Inches(0.08), BLUE)
add_shape(s, Inches(0), Inches(7.42), Inches(13.333), Inches(0.08), BLUE)
add_textbox(s, Inches(1), Inches(2.2), Inches(11.333), Inches(1), '鎰熻阿鑱嗗惉', size=48, color=BLUE, bold=True, align=PP_ALIGN.CENTER)
add_textbox(s, Inches(1), Inches(3.5), Inches(11.333), Inches(0.5), 'FlowForge AI 鈥?AI椹卞姩鐨勫叏娴佺▼杞欢宸ョ▼骞冲彴', size=20, color=WHITE, align=PP_ALIGN.CENTER)
add_textbox(s, Inches(1), Inches(4.2), Inches(11.333), Inches(0.4), '澶氭櫤鑳戒綋鍗忎綔 路 DAG宸ヤ綔娴佺紪鎺?路 瀹炴椂璇勫垎浼樺寲 路 閾句笂瀛樿瘉', size=16, color=GRAY, align=PP_ALIGN.CENTER)
links = [
    'GitHub: github.com/flowforge-ai',
    'Demo: localhost:5173 (涓€閿惎鍔?',
    '鏂囨。: docs/Demo_Operation_Guide.md',
]
for i, link in enumerate(links):
    add_textbox(s, Inches(1), Inches(5.2 + i * 0.45), Inches(11.333), Inches(0.4), link, size=14, color=CYAN, align=PP_ALIGN.CENTER)
add_textbox(s, Inches(1), Inches(6.8), Inches(11.333), Inches(0.4), '娌欏害鍥㈤槦  |  2026骞?0鏈? |  v2.55', size=14, color=GRAY, align=PP_ALIGN.CENTER)

out_path = r'D:\瑗垮鏉綷FlowForgeAI_PitchDeck_CN.pptx'
prs.save(out_path)
size_kb = os.path.getsize(out_path) / 1024
print(f'PPT generated: {out_path}')
print(f'Size: {size_kb:.1f} KB')
print(f'Slides: {len(prs.slides)}')