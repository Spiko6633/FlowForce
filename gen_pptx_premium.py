# -*- coding: utf-8 -*-
"""FlowForge AI 精美 PPT 生成器 - 渐变背景 + 图表 + 装饰图形 + 数据可视化
新增: LayoutGuard 边界检测 / ImageEmbedder 精美图像嵌入 / 代码块溢出修复 / 7页新内容渲染
"""
import json
import os
import io
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.oxml.ns import qn
from lxml import etree

# matplotlib 暗色主题
plt.rcParams['figure.facecolor'] = '#0A1628'
plt.rcParams['axes.facecolor'] = '#122A4A'
plt.rcParams['axes.edgecolor'] = '#9AA5B5'
plt.rcParams['axes.labelcolor'] = '#E8EEF7'
plt.rcParams['xtick.color'] = '#E8EEF7'
plt.rcParams['ytick.color'] = '#E8EEF7'
plt.rcParams['text.color'] = '#E8EEF7'
plt.rcParams['axes.titlecolor'] = '#F5B642'
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

SLIDES_JSON = r"D:\西客松\ppt_slides.json"
OUT_PPTX = r"D:\西客松\FlowForgeAI_PitchDeck_CN.pptx"
NOTES_JSON = r"D:\西客松\data\research\notes.json"
REFS_JSON = r"D:\西客松\data\references.json"
IMAGES_DIR = r"D:\西客松\data\images"

# 配色方案：深蓝 + 金色 + 白
C_DEEP = RGBColor(0x0A, 0x16, 0x28)
C_DEEP2 = RGBColor(0x12, 0x2A, 0x4A)
C_ACCENT = RGBColor(0xF5, 0xB6, 0x42)
C_ACCENT2 = RGBColor(0x4F, 0xC3, 0xF7)
C_WHITE = RGBColor(0xFF, 0xFF, 0xFF)
C_LIGHT = RGBColor(0xE8, 0xEE, 0xF7)
C_GRAY = RGBColor(0x9A, 0xA5, 0xB5)
C_GREEN = RGBColor(0x4C, 0xAF, 0x50)
C_RED = RGBColor(0xE5, 0x3E, 0x3E)
C_PURPLE = RGBColor(0x9C, 0x27, 0xB0)
C_CODE_BG = RGBColor(0x1E, 0x1E, 0x2E)
C_CODE_FG = RGBColor(0xD4, 0xD4, 0xD4)
C_CODE_KEY = RGBColor(0x56, 0x9C, 0xD6)
# 科技感霓虹配色
C_NEON_CYAN = RGBColor(0x00, 0xE5, 0xFF)      # 霓虹青
C_NEON_PURPLE = RGBColor(0xB3, 0x88, 0xFF)    # 霓虹紫
C_NEON_BLUE = RGBColor(0x3D, 0x5A, 0xFF)      # 电光蓝
C_NEON_PINK = RGBColor(0xFF, 0x4D, 0xC4)      # 霓虹粉
C_DEEP_PURPLE = RGBColor(0x1A, 0x0B, 0x2E)    # 深紫
C_GRID = RGBColor(0x2A, 0x4A, 0x6E)           # 网格线

EMU_W = Inches(13.333)
EMU_H = Inches(7.5)

# LayoutGuard 统计
_guard_issues = []


def set_gradient_bg(slide, color1=C_DEEP, color2=C_DEEP2):
    """设置渐变背景（通过 XML 注入）- 深蓝→深紫科技感渐变"""
    bg = slide.background
    fill = bg.fill
    fill.gradient()
    fill.gradient_stops[0].color.rgb = color1
    fill.gradient_stops[0].position = 0.0
    fill.gradient_stops[1].color.rgb = C_DEEP_PURPLE
    fill.gradient_stops[1].position = 1.0
    fill.gradient_angle = 45


def add_rect(slide, x, y, w, h, color, alpha=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    shp.line.fill.background()
    if alpha is not None:
        _set_alpha(shp, alpha)
    return shp


def add_round_rect(slide, x, y, w, h, color, alpha=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    shp.line.fill.background()
    if alpha is not None:
        _set_alpha(shp, alpha)
    return shp


def add_oval(slide, x, y, w, h, color, alpha=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, y, w, h)
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    shp.line.fill.background()
    if alpha is not None:
        _set_alpha(shp, alpha)
    return shp


def _set_alpha(shape, alpha_pct):
    sp = shape.fill._xPr
    srgb = sp.find(qn('a:srgbClr'))
    if srgb is not None:
        a = etree.SubElement(srgb, qn('a:alpha'))
        a.set('val', str(int(alpha_pct * 1000)))


def add_text(slide, x, y, w, h, text, size=18, color=C_WHITE, bold=False,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, font='Microsoft YaHei'):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Pt(0)
    tf.margin_right = Pt(0)
    tf.margin_top = Pt(0)
    tf.margin_bottom = Pt(0)
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = 1.3
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    r.font.name = font
    return tb


def add_bullets(slide, x, y, w, h, bullets, size=16, color=C_LIGHT, gap=6):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Pt(0)
    tf.margin_right = Pt(0)
    for i, b in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(gap)
        p.line_spacing = 1.35
        r1 = p.add_run()
        r1.text = "▸ "
        r1.font.size = Pt(size)
        r1.font.color.rgb = C_NEON_CYAN
        r1.font.bold = True
        r1.font.name = 'Microsoft YaHei'
        r2 = p.add_run()
        r2.text = b
        r2.font.size = Pt(size)
        r2.font.color.rgb = color
        r2.font.name = 'Microsoft YaHei'
    return tb


def add_page_footer(slide, idx, total):
    # 进度条背景
    add_rect(slide, Inches(0), Inches(7.18), EMU_W, Inches(0.05), C_DEEP_PURPLE, alpha=65)
    # 进度条填充（霓虹发光）
    progress_w = Emu(int(int(EMU_W) * idx / total))
    add_rect(slide, Inches(0), Inches(7.18), progress_w, Inches(0.05), C_NEON_CYAN, alpha=80)
    add_rect(slide, Inches(0), Inches(7.165), progress_w, Inches(0.012), C_NEON_CYAN, alpha=45)
    # 品牌标识（带霓虹双点）
    add_oval(slide, Inches(0.5), Inches(7.32), Inches(0.08), Inches(0.08), C_NEON_CYAN, alpha=85)
    add_oval(slide, Inches(0.62), Inches(7.34), Inches(0.05), Inches(0.05), C_NEON_PURPLE, alpha=70)
    add_text(slide, Inches(0.75), Inches(7.25), Inches(6), Inches(0.25),
             "FlowForge AI  ·  Shadu Team  ·  v2.67", size=10, color=C_GRAY)
    # 页码（带科技感括号）
    add_text(slide, Inches(11.0), Inches(7.25), Inches(2.0), Inches(0.25),
             f"[ {idx:02d} / {total:02d} ]", size=10, color=C_NEON_CYAN, align=PP_ALIGN.RIGHT)


def add_title_bar(slide, title, subtitle=None):
    # 科技图标符号 + 霓虹竖条
    add_rect(slide, Inches(0.5), Inches(0.4), Inches(0.12), Inches(0.9), C_NEON_CYAN)
    add_rect(slide, Inches(0.62), Inches(0.4), Inches(0.04), Inches(0.9), C_NEON_PURPLE, alpha=60)
    # 图标符号
    add_text(slide, Inches(0.78), Inches(0.42), Inches(0.5), Inches(0.5),
             "◢", size=22, color=C_NEON_CYAN, bold=True)
    add_text(slide, Inches(1.25), Inches(0.38), Inches(11.0), Inches(0.62),
             title, size=32, color=C_WHITE, bold=True)
    if subtitle:
        add_text(slide, Inches(1.25), Inches(1.02), Inches(11.0), Inches(0.38),
                 subtitle, size=15, color=C_NEON_CYAN)
    # 渐变下划线（多段叠加营造渐变感，延长至全宽）
    add_rect(slide, Inches(1.25), Inches(1.42), Inches(3.5), Inches(0.03), C_NEON_CYAN, alpha=85)
    add_rect(slide, Inches(4.75), Inches(1.42), Inches(2.5), Inches(0.03), C_NEON_PURPLE, alpha=65)
    add_rect(slide, Inches(7.25), Inches(1.42), Inches(2.0), Inches(0.03), C_NEON_PINK, alpha=50)
    add_rect(slide, Inches(9.25), Inches(1.42), Inches(1.8), Inches(0.03), C_ACCENT, alpha=40)
    add_rect(slide, Inches(11.05), Inches(1.42), Inches(1.2), Inches(0.03), C_NEON_CYAN, alpha=30)
    # 标题区发光背景
    add_rect(slide, Inches(1.2), Inches(0.38), Inches(11.5), Inches(1.08), C_DEEP_PURPLE, alpha=10)


def add_decor_circles(slide):
    add_oval(slide, Inches(11.8), Inches(-0.6), Inches(2.2), Inches(2.2), C_ACCENT, alpha=8)
    add_oval(slide, Inches(12.2), Inches(-0.2), Inches(1.2), Inches(1.2), C_ACCENT2, alpha=10)
    add_oval(slide, Inches(-0.5), Inches(6.0), Inches(1.8), Inches(1.8), C_ACCENT2, alpha=6)
    add_oval(slide, Inches(12.8), Inches(5.5), Inches(1.0), Inches(1.0), C_ACCENT, alpha=8)


# ============================================================
# 科技感装饰系统：电路板 / 粒子点阵 / 光束 / 霓虹边框 / 叠加层
# ============================================================
def add_circuit_pattern(slide):
    """电路板纹理：细线条 + 节点圆，营造主板电路感"""
    import random
    random.seed(42)
    # 横向电路线
    for _ in range(6):
        y = Inches(random.uniform(0.5, 7.0))
        x1 = Inches(random.uniform(0, 4))
        w = Inches(random.uniform(2, 5))
        add_rect(slide, x1, y, w, Inches(0.012), C_NEON_CYAN, alpha=10)
    # 纵向电路线
    for _ in range(5):
        x = Inches(random.uniform(0.5, 12.8))
        y1 = Inches(random.uniform(0, 4))
        h = Inches(random.uniform(2, 4))
        add_rect(slide, x, y1, Inches(0.012), h, C_NEON_PURPLE, alpha=10)
    # 电路节点（小圆）
    for _ in range(10):
        x = Inches(random.uniform(0.5, 12.5))
        y = Inches(random.uniform(0.5, 6.8))
        add_oval(slide, x, y, Inches(0.06), Inches(0.06), C_NEON_CYAN, alpha=30)
        add_oval(slide, Emu(int(x) - int(Inches(0.02))), Emu(int(y) - int(Inches(0.02))),
                 Inches(0.10), Inches(0.10), C_NEON_CYAN, alpha=12)


def add_particle_grid(slide):
    """粒子点阵：均匀小圆点网格，营造数字空间感"""
    step_x = 0.6
    step_y = 0.6
    y = 0.3
    while y < 7.2:
        x = 0.3
        while x < 13.1:
            add_oval(slide, Inches(x), Inches(y), Inches(0.035), Inches(0.035),
                     C_NEON_CYAN, alpha=8)
            x += step_x
        y += step_y


def add_light_beams(slide):
    """光束线条：斜向渐变光束，营造动感光效"""
    # 左上光束
    add_rect(slide, Inches(0), Inches(0.2), Inches(4.5), Inches(0.02), C_NEON_CYAN, alpha=35)
    add_rect(slide, Inches(0), Inches(0.35), Inches(3.0), Inches(0.015), C_NEON_PURPLE, alpha=25)
    # 右下光束
    add_rect(slide, Inches(8.8), Inches(7.05), Inches(4.5), Inches(0.02), C_NEON_PINK, alpha=30)
    add_rect(slide, Inches(10.3), Inches(6.9), Inches(3.0), Inches(0.015), C_NEON_CYAN, alpha=22)
    # 中部斜光束（用细矩形旋转近似）
    for i in range(3):
        add_rect(slide, Inches(5.5 + i * 0.15), Inches(0), Inches(0.01), Inches(7.5),
                 C_NEON_BLUE, alpha=6)


def add_scanline(slide):
    """扫描线效果：水平细线均匀分布，营造动漫 HUD 扫描感"""
    for i in range(8):
        y = 0.15 + i * 0.92
        add_rect(slide, Inches(0), Inches(y), EMU_W, Inches(0.006), C_NEON_CYAN, alpha=5)


def add_hologram_grid(slide):
    """全息网格：纵向细密半透明线，营造全息投影空间感"""
    for i in range(-2, 16):
        x = i * 0.9
        add_rect(slide, Inches(x), Inches(0), Inches(0.004), Inches(7.5), C_NEON_BLUE, alpha=3)


def add_data_stream(slide):
    """数据流粒子：随机发光小点，营造数据流动漫感"""
    import random
    random.seed(88)
    for _ in range(28):
        x = random.uniform(0.2, 13.0)
        y = random.uniform(0.2, 7.0)
        sz = random.uniform(0.04, 0.11)
        col = random.choice([C_NEON_CYAN, C_NEON_PURPLE, C_NEON_PINK])
        add_oval(slide, Inches(x), Inches(y), Inches(sz), Inches(sz), col, alpha=random.randint(22, 55))


def add_corner_brackets(slide):
    """四角科技感括号：动漫 HUD 风格转角标记"""
    s, t = 0.38, 0.045
    # 左上
    add_rect(slide, Inches(0.15), Inches(0.15), Inches(s), Inches(t), C_NEON_CYAN, alpha=75)
    add_rect(slide, Inches(0.15), Inches(0.15), Inches(t), Inches(s), C_NEON_CYAN, alpha=75)
    # 右上
    rx = Emu(int(EMU_W) - int(Inches(0.15)) - int(Inches(s)))
    add_rect(slide, rx, Inches(0.15), Inches(s), Inches(t), C_NEON_PURPLE, alpha=75)
    add_rect(slide, Emu(int(rx) + int(Inches(s)) - int(Inches(t))), Inches(0.15), Inches(t), Inches(s), C_NEON_PURPLE, alpha=75)
    # 左下
    by = Emu(int(EMU_H) - int(Inches(0.15)) - int(Inches(t)))
    add_rect(slide, Inches(0.15), by, Inches(s), Inches(t), C_NEON_PINK, alpha=75)
    add_rect(slide, Inches(0.15), Emu(int(by) - int(Inches(s)) + int(Inches(t))), Inches(t), Inches(s), C_NEON_PINK, alpha=75)
    # 右下
    add_rect(slide, rx, by, Inches(s), Inches(t), C_NEON_CYAN, alpha=75)
    add_rect(slide, Emu(int(rx) + int(Inches(s)) - int(Inches(t))), Emu(int(by) - int(Inches(s)) + int(Inches(t))), Inches(t), Inches(s), C_NEON_CYAN, alpha=75)


def add_glow_orbs(slide):
    """发光球体：大尺寸低透明度光晕，营造景深与氛围光"""
    add_oval(slide, Inches(-2), Inches(-1), Inches(5), Inches(5), C_NEON_BLUE, alpha=5)
    add_oval(slide, Inches(10), Inches(3), Inches(6), Inches(6), C_NEON_PURPLE, alpha=4)
    add_oval(slide, Inches(4), Inches(-2), Inches(4), Inches(4), C_NEON_PINK, alpha=3)


def add_neon_border(slide):
    """霓虹光效边框：页面四周发光边框，多层叠加营造辉光"""
    # 外层辉光（最淡最宽）
    add_rect(slide, Inches(0.06), Inches(0.06), Emu(int(EMU_W) - int(Inches(0.12))), Inches(0.025), C_NEON_CYAN, alpha=18)
    add_rect(slide, Inches(0.06), Emu(int(EMU_H) - int(Inches(0.085))), Emu(int(EMU_W) - int(Inches(0.12))), Inches(0.025), C_NEON_CYAN, alpha=18)
    add_rect(slide, Inches(0.06), Inches(0.06), Inches(0.025), Emu(int(EMU_H) - int(Inches(0.12))), C_NEON_PURPLE, alpha=18)
    add_rect(slide, Emu(int(EMU_W) - int(Inches(0.085))), Inches(0.06), Inches(0.025), Emu(int(EMU_H) - int(Inches(0.12))), C_NEON_PURPLE, alpha=18)
    # 中层辉光
    add_rect(slide, Inches(0.09), Inches(0.09), Emu(int(EMU_W) - int(Inches(0.18))), Inches(0.018), C_NEON_PURPLE, alpha=28)
    add_rect(slide, Inches(0.09), Emu(int(EMU_H) - int(Inches(0.108))), Emu(int(EMU_W) - int(Inches(0.18))), Inches(0.018), C_NEON_PURPLE, alpha=28)
    # 内层亮线（更亮更细）
    add_rect(slide, Inches(0.12), Inches(0.12), Emu(int(EMU_W) - int(Inches(0.24))), Inches(0.012), C_NEON_CYAN, alpha=55)
    add_rect(slide, Inches(0.12), Emu(int(EMU_H) - int(Inches(0.132))), Emu(int(EMU_W) - int(Inches(0.24))), Inches(0.012), C_NEON_CYAN, alpha=55)
    add_rect(slide, Inches(0.12), Inches(0.12), Inches(0.012), Emu(int(EMU_H) - int(Inches(0.24))), C_NEON_CYAN, alpha=55)
    add_rect(slide, Emu(int(EMU_W) - int(Inches(0.132))), Inches(0.12), Inches(0.012), Emu(int(EMU_H) - int(Inches(0.24))), C_NEON_CYAN, alpha=55)


def add_overlay_layer(slide):
    """半透明叠加层：营造层次感与景深"""
    # 顶部渐隐遮罩
    add_rect(slide, Inches(0), Inches(0), EMU_W, Inches(1.5), C_DEEP_PURPLE, alpha=12)
    # 底部渐隐遮罩
    add_rect(slide, Inches(0), Inches(6.0), EMU_W, Inches(1.5), C_DEEP, alpha=15)
    # 左侧光晕
    add_oval(slide, Inches(-1.5), Inches(2.5), Inches(3.5), Inches(3.5), C_NEON_BLUE, alpha=6)
    # 右侧光晕
    add_oval(slide, Inches(11.5), Inches(2.0), Inches(3.5), Inches(3.5), C_NEON_PURPLE, alpha=6)


def add_tech_decor(slide, is_cover=False):
    """统一科技感装饰入口：叠加层 + 发光球 + 粒子点阵 + 电路板 + 光束 + 扫描线 + 数据流 + HUD括号 + 霓虹边框"""
    add_overlay_layer(slide)
    add_glow_orbs(slide)
    add_hologram_grid(slide)
    add_particle_grid(slide)
    add_circuit_pattern(slide)
    add_light_beams(slide)
    add_scanline(slide)
    add_data_stream(slide)
    add_corner_brackets(slide)
    if not is_cover:
        add_neon_border(slide)


def add_section_badge(slide, num):
    add_oval(slide, Inches(12.3), Inches(0.3), Inches(0.7), Inches(0.7), C_NEON_CYAN, alpha=25)
    add_oval(slide, Inches(12.35), Inches(0.35), Inches(0.6), Inches(0.6), C_DEEP_PURPLE, alpha=50)
    add_text(slide, Inches(12.3), Inches(0.35), Inches(0.7), Inches(0.6),
             f"{num:02d}", size=20, color=C_NEON_CYAN, bold=True, align=PP_ALIGN.CENTER)


def add_stat_card(slide, x, y, w, h, number, label, color=C_ACCENT):
    add_round_rect(slide, x, y, w, h, C_DEEP_PURPLE, alpha=72)
    add_rect(slide, x, y, Inches(0.06), h, color)
    add_rect(slide, x, y, w, Inches(0.02), color, alpha=50)
    add_text(slide, x + Inches(0.2), y + Inches(0.15), w - Inches(0.3), Inches(0.5),
             number, size=28, color=color, bold=True)
    add_text(slide, x + Inches(0.2), y + Inches(0.62), w - Inches(0.3), Inches(0.38),
             label, size=12, color=C_LIGHT)


def add_bar_chart_img(slide, x, y, w, h, cats, vals, title="", color='#F5B642'):
    fig, ax = plt.subplots(figsize=(w / Inches(1), h / Inches(1)), dpi=200)
    bars = ax.bar(cats, vals, color=color, edgecolor='none', width=0.6)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(vals) * 0.02,
                str(v), ha='center', va='bottom', fontsize=10, color='#E8EEF7', fontweight='bold')
    if title:
        ax.set_title(title, fontsize=13, pad=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylim(0, max(vals) * 1.15)
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', facecolor='#0A1628', edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    return slide.shapes.add_picture(buf, x, y, w, h)


def add_radar_chart_img(slide, x, y, w, h, cats, vals, title=""):
    import numpy as np
    angles = np.linspace(0, 2 * np.pi, len(cats), endpoint=False).tolist()
    angles += angles[:1]
    vals_closed = list(vals) + [vals[0]]
    fig, ax = plt.subplots(figsize=(w / Inches(1), h / Inches(1)), dpi=200, subplot_kw=dict(polar=True))
    ax.set_facecolor('#122A4A')
    ax.plot(angles, vals_closed, color='#F5B642', linewidth=2)
    ax.fill(angles, vals_closed, color='#F5B642', alpha=0.3)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(cats, fontsize=11)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=8, color='#9AA5B5')
    if title:
        ax.set_title(title, fontsize=13, pad=15, color='#F5B642')
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', facecolor='#0A1628', edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    return slide.shapes.add_picture(buf, x, y, w, h)


def add_pie_chart_img(slide, x, y, w, h, cats, vals, title=""):
    colors_pie = ['#F5B642', '#4FC3F7', '#4CAF50', '#9C27B0', '#E53E3E', '#FF9800']
    fig, ax = plt.subplots(figsize=(w / Inches(1), h / Inches(1)), dpi=200)
    wedges, texts, autotexts = ax.pie(vals, labels=cats, autopct='%1.0f%%',
                                       colors=colors_pie[:len(cats)],
                                       textprops={'fontsize': 10, 'color': '#E8EEF7'},
                                       startangle=90)
    for at in autotexts:
        at.set_color('#0A1628')
        at.set_fontweight('bold')
    if title:
        ax.set_title(title, fontsize=13, pad=10)
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', facecolor='#0A1628', edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    return slide.shapes.add_picture(buf, x, y, w, h)


def add_line_chart_img(slide, x, y, w, h, cats, vals, title="", color='#4FC3F7'):
    fig, ax = plt.subplots(figsize=(w / Inches(1), h / Inches(1)), dpi=200)
    ax.plot(cats, vals, color=color, linewidth=2.5, marker='o', markersize=6,
            markerfacecolor='#F5B642', markeredgecolor='#F5B642')
    ax.fill_between(range(len(cats)), vals, alpha=0.2, color=color)
    ax.set_xticks(range(len(cats)))
    ax.set_xticklabels(cats, fontsize=10)
    if title:
        ax.set_title(title, fontsize=13, pad=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', facecolor='#0A1628', edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    return slide.shapes.add_picture(buf, x, y, w, h)


# ============================================================
# TASK-023: LayoutGuard 边界检测
# ============================================================
def layout_guard(slide, slide_idx=0):
    """校验页面上所有形状不超出 EMU_W/EMU_H 边界，超出则自动缩放/裁剪"""
    global _guard_issues
    max_w = int(EMU_W)
    max_h = int(EMU_H)
    for shp in slide.shapes:
        try:
            left = int(shp.left) if shp.left is not None else 0
            top = int(shp.top) if shp.top is not None else 0
            width = int(shp.width) if shp.width is not None else 0
            height = int(shp.height) if shp.height is not None else 0
            right = left + width
            bottom = top + height
            # 水平溢出：右移裁剪宽度
            if right > max_w:
                overflow = right - max_w
                if left < 0:
                    shp.left = Emu(0)
                    left = 0
                new_w = max(width - overflow, Inches(0.2))
                shp.width = Emu(int(new_w))
                _guard_issues.append(f"slide {slide_idx}: H-overflow {overflow}EMU -> width adjusted")
            # 垂直溢出：下移裁剪高度
            if bottom > max_h:
                overflow = bottom - max_h
                if top < 0:
                    shp.top = Emu(0)
                    top = 0
                new_h = max(height - overflow, Inches(0.2))
                shp.height = Emu(int(new_h))
                _guard_issues.append(f"slide {slide_idx}: V-overflow {overflow}EMU -> height adjusted")
            # 负坐标修正
            if left < 0:
                shp.left = Emu(0)
            if top < 0:
                shp.top = Emu(0)
        except Exception:
            pass


# ============================================================
# TASK-024: ImageEmbedder 精美图像嵌入
# ============================================================
def add_image_safe(slide, image_name, x, y, max_w, max_h, fallback_color=C_ACCENT2):
    """从 data/images/ 选取图像并等比缩放插入；无文件则用渐变形状替代"""
    img_path = os.path.join(IMAGES_DIR, image_name)
    if os.path.isfile(img_path):
        try:
            from PIL import Image as PILImage
            with PILImage.open(img_path) as im:
                iw, ih = im.size
            # 等比缩放到 max_w/max_h 框内
            ratio = min(int(max_w) / (iw * 9525), int(max_h) / (ih * 9525))
            new_w = Emu(int(iw * 9525 * ratio))
            new_h = Emu(int(ih * 9525 * ratio))
            cx = Emu(int(x) + (int(max_w) - int(new_w)) // 2)
            cy = Emu(int(y) + (int(max_h) - int(new_h)) // 2)
            return slide.shapes.add_picture(img_path, cx, cy, new_w, new_h)
        except Exception:
            pass
    # 无图像文件：用装饰形状替代（渐变圆 + 圆角矩形）
    add_oval(slide, x, y, max_w, max_h, fallback_color, alpha=15)
    add_round_rect(slide, Emu(int(x) + int(max_w) // 4), Emu(int(y) + int(max_h) // 4),
                   Emu(int(max_w) // 2), Emu(int(max_h) // 2), C_DEEP2, alpha=60)
    return None


def add_visual_element(slide, x, y, w, h, color=C_ACCENT2, style='circle'):
    """用 python-pptx 形状创建精美视觉元素替代图像"""
    if style == 'circle':
        add_oval(slide, x, y, w, h, color, alpha=12)
        add_oval(slide, Emu(int(x) + int(w) // 4), Emu(int(y) + int(h) // 4),
                 Emu(int(w) // 2), Emu(int(h) // 2), C_DEEP2, alpha=50)
    elif style == 'gradient_bar':
        add_rect(slide, x, y, w, Inches(0.08), color)
        add_rect(slide, x, Emu(int(y) + int(h) - int(Inches(0.08))), w, Inches(0.08), C_ACCENT, alpha=40)
        add_round_rect(slide, x, y, w, h, C_DEEP2, alpha=40)
    elif style == 'hex':
        shp = slide.shapes.add_shape(MSO_SHAPE.HEXAGON, x, y, w, h)
        shp.fill.solid()
        shp.fill.fore_color.rgb = color
        shp.line.fill.background()
        _set_alpha(shp, 15)


# ============================================================
# TASK-025: 代码块渲染（修复溢出）
# ============================================================
def add_code_block(slide, x, y, w, h, code_lines, title="", lang="python", base_size=11):
    """渲染代码块，超长自动缩小字号保持可读性，不溢出边界"""
    # 计算所需字号：根据行数和宽度自适应
    max_chars_per_line = max(len(line) for line in code_lines) if code_lines else 1
    avail_width_in = w / Inches(1)
    # 估算每行可容纳字符数（等宽字体约 size*0.6 inch/char）
    est_size = base_size
    while est_size > 10:
        chars_fit = int(avail_width_in / (est_size * 0.012))
        if max_chars_per_line <= chars_fit:
            break
        est_size -= 1
    # 行数过多则进一步缩小
    avail_height_in = h / Inches(1)
    line_height_in = est_size * 0.018
    max_lines = int(avail_height_in / line_height_in) - (1 if title else 0)
    display_lines = code_lines[:max_lines] if len(code_lines) > max_lines else code_lines

    # 背景框
    add_round_rect(slide, x, y, w, h, C_CODE_BG, alpha=90)
    add_rect(slide, x, y, Inches(0.06), h, C_ACCENT2)

    # 标题栏
    ty = y
    if title:
        add_text(slide, Emu(int(x) + int(Inches(0.2))), y, w, Inches(0.3),
                 f"  {title}", size=10, color=C_ACCENT, bold=True)
        ty = Emu(int(y) + int(Inches(0.3)))

    # 代码内容
    tb = slide.shapes.add_textbox(Emu(int(x) + int(Inches(0.2))), ty,
                                  Emu(int(w) - int(Inches(0.3))),
                                  Emu(int(h) - int(Inches(0.4)) if title else int(h) - int(Inches(0.2))))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Pt(2)
    tf.margin_right = Pt(2)
    tf.margin_top = Pt(2)
    tf.margin_bottom = Pt(2)
    for i, line in enumerate(display_lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(1)
        p.line_spacing = 1.2
        r = p.add_run()
        r.text = line if line else " "
        r.font.size = Pt(est_size)
        r.font.color.rgb = C_CODE_FG
        r.font.name = 'Consolas'
    return tb


def add_log_block(slide, x, y, w, h, log_text, base_size=10):
    """渲染日志摘要块"""
    add_round_rect(slide, x, y, w, h, C_DEEP2, alpha=85)
    add_rect(slide, x, y, Inches(0.06), h, C_GREEN)
    lines = log_text.split('\n')
    tb = slide.shapes.add_textbox(Emu(int(x) + int(Inches(0.2))), y,
                                  Emu(int(w) - int(Inches(0.3))), h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Pt(2)
    tf.margin_top = Pt(2)
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(2)
        r = p.add_run()
        r.text = line
        r.font.size = Pt(base_size)
        r.font.color.rgb = C_GREEN if '✓' in line or 'OK' in line else C_LIGHT
        r.font.name = 'Consolas'


# ============================================================
# 数据加载
# ============================================================
def load_notes():
    try:
        return json.load(open(NOTES_JSON, encoding='utf-8'))
    except Exception:
        return {}


def load_refs():
    try:
        return json.load(open(REFS_JSON, encoding='utf-8'))
    except Exception:
        return {}


# ============================================================
# 主构建
# ============================================================
def build():
    global _guard_issues
    _guard_issues = []
    slides = json.load(open(SLIDES_JSON, encoding='utf-8'))
    notes = load_notes()
    refs = load_refs()
    prs = Presentation()
    prs.slide_width = EMU_W
    prs.slide_height = EMU_H
    blank = prs.slide_layouts[6]
    total = len(slides)

    for i, s in enumerate(slides):
        stype = s.get('type', 'generic')
        slide = prs.slides.add_slide(blank)
        set_gradient_bg(slide)
        add_decor_circles(slide)
        # 科技感装饰系统：叠加层 + 粒子点阵 + 电路板 + 光束 + 霓虹边框
        add_tech_decor(slide, is_cover=(stype == 'cover'))
        title = s.get('title', '')
        subtitle = s.get('subtitle', '')
        bullets = s.get('bullets', [])

        # 封面
        if stype == 'cover':
            add_neon_border(slide)
            # 顶部产品发布标签
            add_round_rect(slide, Inches(5.4), Inches(0.5), Inches(2.5), Inches(0.4), C_DEEP_PURPLE, alpha=70)
            add_rect(slide, Inches(5.4), Inches(0.5), Inches(0.06), Inches(0.4), C_NEON_CYAN)
            add_text(slide, Inches(5.5), Inches(0.54), Inches(2.3), Inches(0.32),
                     "◆ PRODUCT SPEC RELEASE", size=12, color=C_NEON_CYAN, bold=True, align=PP_ALIGN.CENTER)
            # 霓虹分隔线（多段渐变）
            add_rect(slide, Inches(0), Inches(3.0), Inches(4.5), Inches(0.04), C_NEON_CYAN, alpha=75)
            add_rect(slide, Inches(4.5), Inches(3.0), Inches(4.3), Inches(0.04), C_NEON_PURPLE, alpha=60)
            add_rect(slide, Inches(8.8), Inches(3.0), Inches(4.5), Inches(0.04), C_NEON_PINK, alpha=50)
            add_text(slide, Inches(1), Inches(1.2), Inches(11.3), Inches(1.2),
                     "FlowForge AI", size=64, color=C_WHITE, bold=True, align=PP_ALIGN.CENTER)
            add_text(slide, Inches(1), Inches(2.4), Inches(11.3), Inches(0.6),
                     subtitle, size=24, color=C_NEON_CYAN, align=PP_ALIGN.CENTER)
            add_text(slide, Inches(1), Inches(3.3), Inches(11.3), Inches(0.5),
                     "多智能体工作流编排平台 · 可编排 · 可评分 · 可存证",
                     size=18, color=C_LIGHT, align=PP_ALIGN.CENTER)
            # 中央发光环（动漫全息感）
            add_oval(slide, Inches(4.5), Inches(0.8), Inches(4.3), Inches(4.3), C_NEON_CYAN, alpha=5)
            add_oval(slide, Inches(5.0), Inches(1.3), Inches(3.3), Inches(3.3), C_NEON_PURPLE, alpha=4)
            add_oval(slide, Inches(5.5), Inches(1.8), Inches(2.3), Inches(2.3), C_NEON_PINK, alpha=3)
            # 顶部科技感装饰条
            add_rect(slide, Inches(0), Inches(0.15), Inches(6), Inches(0.015), C_NEON_CYAN, alpha=40)
            add_rect(slide, Inches(7.3), Inches(0.15), Inches(6), Inches(0.015), C_NEON_PURPLE, alpha=40)
            # 底部科技感装饰条
            add_rect(slide, Inches(0), Inches(6.85), Inches(5), Inches(0.015), C_NEON_PINK, alpha=35)
            add_rect(slide, Inches(8.3), Inches(6.85), Inches(5), Inches(0.015), C_NEON_CYAN, alpha=35)
            # 侧边动态光柱
            add_rect(slide, Inches(0.3), Inches(2.0), Inches(0.03), Inches(3.5), C_NEON_CYAN, alpha=30)
            add_rect(slide, Inches(13.0), Inches(2.0), Inches(0.03), Inches(3.5), C_NEON_PURPLE, alpha=30)
            badges = ["AI × Blockchain 主赛道", "GCC 公共物品分赛道", "v2.67 双赛道适配"]
            badge_colors = [C_NEON_CYAN, C_NEON_PURPLE, C_NEON_PINK]
            bx = Inches(2.0)
            for bi_b, b in enumerate(badges):
                w = Inches(3.0)
                col = badge_colors[bi_b]
                add_round_rect(slide, bx, Inches(4.3), w, Inches(0.55), C_DEEP_PURPLE, alpha=75)
                add_rect(slide, bx, Inches(4.3), Inches(0.06), Inches(0.55), col)
                add_text(slide, bx + Inches(0.15), Inches(4.38), w - Inches(0.2), Inches(0.4),
                         b, size=14, color=col, bold=True, align=PP_ALIGN.CENTER)
                bx = Emu(int(bx) + int(Inches(3.2)))
            add_text(slide, Inches(1), Inches(5.5), Inches(11.3), Inches(0.5),
                     "Shadu Team 出品 · 2026 客户松 S1 & ETH Wuhan 参赛作品",
                     size=14, color=C_GRAY, align=PP_ALIGN.CENTER)
            add_text(slide, Inches(1), Inches(6.1), Inches(11.3), Inches(0.4),
                     "Vue3 + FastAPI + ArkTS + Python + Solidity 全栈实现",
                     size=13, color=C_GRAY, align=PP_ALIGN.CENTER)
            add_visual_element(slide, Inches(0.3), Inches(0.3), Inches(1.0), Inches(1.0), C_ACCENT, 'circle')
            add_visual_element(slide, Inches(12.0), Inches(6.0), Inches(1.0), Inches(1.0), C_ACCENT2, 'circle')
            add_page_footer(slide, i + 1, total)
            layout_guard(slide, i + 1)
            _add_note(slide, s)
            continue

        # 通用标题栏
        add_title_bar(slide, title, subtitle)
        add_section_badge(slide, i + 1)

        # ---------- 原有页面类型 ----------
        if stype == 'pain':
            pain_points = [
                ("⚠", "单点生成", "AI 工具单点作战，缺乏协同"),
                ("⚠", "流程割裂", "审查/测试/文档各自为政"),
                ("⚠", "质量黑箱", "AI 产出缺乏量化标准"),
                ("⚠", "不可溯源", "生成内容无链上可信凭证"),
            ]
            cx = Inches(0.8)
            for icon, head, body in pain_points:
                w = Inches(2.9)
                add_round_rect(slide, cx, Inches(1.8), w, Inches(1.6), C_DEEP2, alpha=70)
                add_rect(slide, cx, Inches(1.8), w, Inches(0.06), C_RED)
                add_text(slide, cx + Inches(0.2), Inches(1.95), Inches(0.5), Inches(0.5),
                         icon, size=24, color=C_RED, bold=True)
                add_text(slide, cx + Inches(0.8), Inches(1.95), w - Inches(0.9), Inches(0.4),
                         head, size=16, color=C_WHITE, bold=True)
                add_text(slide, cx + Inches(0.2), Inches(2.5), w - Inches(0.3), Inches(0.8),
                         body, size=14, color=C_LIGHT)
                cx = Emu(int(cx) + int(Inches(3.0)))
            add_bullets(slide, Inches(0.8), Inches(3.7), Inches(11.7), Inches(3.2), bullets, size=15)
            add_visual_element(slide, Inches(11.5), Inches(3.7), Inches(1.2), Inches(1.2), C_RED, 'circle')

        elif stype == 'solution':
            add_bullets(slide, Inches(0.8), Inches(1.7), Inches(6.5), Inches(5.0), bullets, size=15)
            pillars = [("可编排", C_ACCENT), ("可评分", C_ACCENT2), ("可存证", C_GREEN)]
            py = Inches(1.8)
            for name, col in pillars:
                add_round_rect(slide, Inches(8.0), py, Inches(4.5), Inches(1.4), C_DEEP2, alpha=70)
                add_rect(slide, Inches(8.0), py, Inches(0.08), Inches(1.4), col)
                add_text(slide, Inches(8.3), py + Inches(0.15), Inches(4.0), Inches(0.5),
                         name, size=22, color=col, bold=True)
                add_text(slide, Inches(8.3), py + Inches(0.7), Inches(4.0), Inches(0.6),
                         {"可编排": "可视化拖拽多智能体协作",
                          "可评分": "五维评分量化每次执行",
                          "可存证": "链上不可篡改可信凭证"}.get(name, ""),
                         size=14, color=C_LIGHT)
                py = Emu(int(py) + int(Inches(1.55)))
            add_visual_element(slide, Inches(0.3), Inches(5.5), Inches(0.8), Inches(0.8), C_GREEN, 'circle')

        # ---------- 合并页: architecture + tech ----------
        elif stype == 'architecture_tech':
            layers = [
                ("前端层", "Vue3 + ArkTS", "Web 与鸿蒙多端协同", C_ACCENT2),
                ("服务层", "FastAPI", "工作流编排与评分 API", C_ACCENT),
                ("智能体层", "Python", "多智能体协作与工具调用", C_PURPLE),
                ("存证层", "Solidity", "执行哈希写入 BOT Chain", C_GREEN),
            ]
            ly = Inches(1.7)
            for name, tech, desc, col in layers:
                add_round_rect(slide, Inches(0.8), ly, Inches(7.0), Inches(0.85), C_DEEP2, alpha=70)
                add_rect(slide, Inches(0.8), ly, Inches(0.1), Inches(0.85), col)
                add_text(slide, Inches(1.1), ly + Inches(0.1), Inches(1.8), Inches(0.4),
                         name, size=16, color=col, bold=True)
                add_text(slide, Inches(3.0), ly + Inches(0.1), Inches(2.0), Inches(0.4),
                         tech, size=14, color=C_WHITE, bold=True)
                add_text(slide, Inches(5.0), ly + Inches(0.1), Inches(2.6), Inches(0.6),
                         desc, size=12, color=C_LIGHT)
                ly = Emu(int(ly) + int(Inches(0.95)))
            add_text(slide, Inches(0.8), Inches(5.6), Inches(7.0), Inches(0.3),
                     "数据层：工作流、执行记录、评分记录三层结构化沉淀",
                     size=12, color=C_GRAY)
            # 右侧技术栈卡片
            stack = [
                ("Vue3", "前端", C_GREEN), ("ArkTS", "鸿蒙", C_ACCENT2),
                ("FastAPI", "后端", C_ACCENT), ("Python", "智能体", C_PURPLE),
                ("Solidity", "合约", C_RED), ("SQLite", "存储", C_GRAY),
            ]
            sx, sy = Inches(8.2), Inches(1.7)
            for j, (t, d, col) in enumerate(stack):
                x = Emu(int(sx) + (j % 2) * int(Inches(2.3)))
                y = Emu(int(sy) + (j // 2) * int(Inches(1.15)))
                add_round_rect(slide, x, y, Inches(2.1), Inches(1.0), C_DEEP2, alpha=70)
                add_rect(slide, x, y, Inches(2.1), Inches(0.06), col)
                add_text(slide, x + Inches(0.15), y + Inches(0.1), Inches(1.8), Inches(0.4),
                         t, size=16, color=col, bold=True)
                add_text(slide, x + Inches(0.15), y + Inches(0.55), Inches(1.8), Inches(0.35),
                         d, size=11, color=C_LIGHT)
            add_visual_element(slide, Inches(8.2), Inches(5.5), Inches(4.3), Inches(1.2), C_ACCENT, 'gradient_bar')

        # ---------- 合并页: orchestration + score + evidencing ----------
        elif stype == 'core_trio':
            trio = [
                ("编排", "串行/并行/条件分支/人工审批", "13 智能体 · 65 工作流 · 262 执行", C_ACCENT),
                ("评分", "正确性/完整性/及时性/创新性/稳定性", "594 条评分 · 0-100 综合分", C_ACCENT2),
                ("存证", "哈希写入 Solidity 合约", "BOT Chain · Chain ID 677", C_GREEN),
            ]
            ty = Inches(1.7)
            for name, desc, stat, col in trio:
                add_round_rect(slide, Inches(0.8), ty, Inches(6.5), Inches(1.5), C_DEEP2, alpha=70)
                add_rect(slide, Inches(0.8), ty, Inches(0.1), Inches(1.5), col)
                add_text(slide, Inches(1.1), ty + Inches(0.1), Inches(1.5), Inches(0.5),
                         name, size=20, color=col, bold=True)
                add_text(slide, Inches(2.8), ty + Inches(0.1), Inches(4.3), Inches(0.5),
                         desc, size=14, color=C_WHITE, bold=True)
                add_text(slide, Inches(1.1), ty + Inches(0.65), Inches(6.0), Inches(0.7),
                         stat, size=14, color=C_LIGHT)
                ty = Emu(int(ty) + int(Inches(1.65)))
            add_bullets(slide, Inches(0.8), Inches(6.7), Inches(6.5), Inches(0.5), bullets[3:], size=12, gap=2)
            # 右侧雷达图
            add_radar_chart_img(slide, Inches(7.8), Inches(1.7), Inches(5.2), Inches(3.8),
                                ["正确性", "完整性", "及时性", "创新性", "稳定性"],
                                [96.5, 97.0, 95.0, 96.0, 99.2],
                                title="五维评分雷达图")
            add_stat_card(slide, Inches(7.8), Inches(5.7), Inches(1.6), Inches(1.0), "97.0", "平均分", C_GREEN)
            add_stat_card(slide, Inches(9.5), Inches(5.7), Inches(1.6), Inches(1.0), "594", "评分记录", C_ACCENT)
            add_stat_card(slide, Inches(11.2), Inches(5.7), Inches(1.8), Inches(1.0), "677", "Chain ID", C_ACCENT2)

        # ---------- 合并页: track_main + track_gcc ----------
        elif stype == 'track_dual':
            # 左侧主赛道
            add_text(slide, Inches(0.8), Inches(1.6), Inches(5.8), Inches(0.4),
                     "AI×Blockchain 主赛道", size=16, color=C_ACCENT, bold=True)
            add_bullets(slide, Inches(0.8), Inches(2.0), Inches(5.8), Inches(2.5), bullets[:2], size=14, gap=4)
            add_bar_chart_img(slide, Inches(0.8), Inches(4.5), Inches(5.8), Inches(2.5),
                              ["可信凭证", "质量评价", "去中心化", "可追溯", "防篡改"],
                              [95, 90, 88, 92, 96],
                              title="主赛道契合度", color='#F5B642')
            # 右侧分赛道
            add_text(slide, Inches(7.0), Inches(1.6), Inches(5.8), Inches(0.4),
                     "GCC 公共物品分赛道", size=16, color=C_ACCENT2, bold=True)
            add_bullets(slide, Inches(7.0), Inches(2.0), Inches(5.8), Inches(2.0), bullets[2:4], size=14, gap=4)
            add_stat_card(slide, Inches(7.0), Inches(4.0), Inches(1.8), Inches(0.9), "30", "市场模板", C_ACCENT)
            add_stat_card(slide, Inches(8.9), Inches(4.0), Inches(1.8), Inches(0.9), "13", "智能体", C_ACCENT2)
            add_stat_card(slide, Inches(10.8), Inches(4.0), Inches(1.8), Inches(0.9), "免费", "开放", C_GREEN)
            add_text(slide, Inches(7.0), Inches(5.1), Inches(5.8), Inches(0.8),
                     bullets[4], size=14, color=C_LIGHT)
            add_visual_element(slide, Inches(7.0), Inches(6.0), Inches(5.8), Inches(0.8), C_GREEN, 'gradient_bar')

        # ---------- 合并页: competitive + demo ----------
        elif stype == 'competitive_demo':
            add_bullets(slide, Inches(0.8), Inches(1.7), Inches(6.0), Inches(3.0), bullets[:3], size=14, gap=4)
            # 差异化对比
            rows = [("单点生成", "全流程编排"), ("主观质量", "五维评分"),
                    ("无存证", "链上存证"), ("无模板", "模板市场")]
            ry = Inches(1.9)
            add_text(slide, Inches(8.0), Inches(1.7), Inches(2.2), Inches(0.35),
                     "其他 AI 工具", size=14, color=C_RED, bold=True, align=PP_ALIGN.CENTER)
            add_text(slide, Inches(10.3), Inches(1.7), Inches(2.2), Inches(0.35),
                     "FlowForge", size=14, color=C_GREEN, bold=True, align=PP_ALIGN.CENTER)
            for a, b in rows:
                add_round_rect(slide, Inches(8.0), ry, Inches(2.2), Inches(0.6), C_DEEP2, alpha=70)
                add_text(slide, Inches(8.0), ry + Inches(0.12), Inches(2.2), Inches(0.35),
                         a, size=14, color=C_RED, align=PP_ALIGN.CENTER)
                add_round_rect(slide, Inches(10.3), ry, Inches(2.2), Inches(0.6), C_DEEP2, alpha=70)
                add_text(slide, Inches(10.3), ry + Inches(0.12), Inches(2.2), Inches(0.35),
                         b, size=14, color=C_GREEN, bold=True, align=PP_ALIGN.CENTER)
                ry = Emu(int(ry) + int(Inches(0.72)))
            # 真实数据柱状图
            add_bar_chart_img(slide, Inches(0.8), Inches(4.8), Inches(7.0), Inches(2.2),
                              ["工作流", "执行", "评分", "模板", "智能体"],
                              [65, 262, 594, 30, 13],
                              title="真实运行数据", color='#F5B642')
            add_stat_card(slide, Inches(8.0), Inches(4.8), Inches(2.2), Inches(1.0), "594", "评分记录", C_GREEN)
            add_stat_card(slide, Inches(10.3), Inches(4.8), Inches(2.2), Inches(1.0), "262", "执行记录", C_ACCENT2)
            add_text(slide, Inches(8.0), Inches(6.0), Inches(4.5), Inches(0.5),
                     bullets[4], size=14, color=C_LIGHT)

        elif stype == 'chain_deploy':
            add_bullets(slide, Inches(0.8), Inches(1.7), Inches(6.8), Inches(5.0), bullets, size=15)
            info = [
                ("网络", "BOT Chain 主网"), ("Chain ID", "677"),
                ("RPC", "https://rpc.botchain.ai"), ("Scan", "https://scan.botchain.ai"),
                ("Faucet", "https://faucet.botchain.ai"), ("合约", "Solidity 存证合约已部署"),
            ]
            iy = Inches(1.8)
            for k, v in info:
                add_round_rect(slide, Inches(8.0), iy, Inches(4.5), Inches(0.65), C_DEEP2, alpha=70)
                add_rect(slide, Inches(8.0), iy, Inches(0.06), Inches(0.65), C_ACCENT)
                add_text(slide, Inches(8.2), iy + Inches(0.1), Inches(1.5), Inches(0.45),
                         k, size=14, color=C_ACCENT, bold=True)
                add_text(slide, Inches(9.7), iy + Inches(0.1), Inches(2.7), Inches(0.45),
                         v, size=14, color=C_LIGHT)
                iy = Emu(int(iy) + int(Inches(0.75)))
            add_visual_element(slide, Inches(0.3), Inches(5.5), Inches(1.0), Inches(1.0), C_GREEN, 'hex')

        # ============================================================
        # TASK-015: code_evidence 代码证据页
        # ============================================================
        elif stype == 'code_evidence':
            add_bullets(slide, Inches(0.8), Inches(1.6), Inches(11.7), Inches(0.8), bullets, size=14, gap=2)
            # 代码块1: Python 编排引擎
            py_code = [
                "async def orchestrate(workflow, ctx):",
                "    results = {}",
                "    for node in workflow.topo_order():",
                "        agent = AgentRegistry.get(node.agent_id)",
                "        results[node.id] = await agent.run(",
                "            ctx.merge(results, node.inputs))",
                "        ScoreEngine.record(node.id, results[node.id])",
                "    EvidenceChain.commit(workflow.id, results)",
                "    return results",
            ]
            add_code_block(slide, Inches(0.8), Inches(2.6), Inches(6.2), Inches(2.8),
                           py_code, title="orchestrate.py", lang="python", base_size=10)
            # 代码块2: Solidity 存证
            sol_code = [
                "function commit(bytes32 id, bytes32 hash,",
                "    uint8 score, uint256 ts) external {",
                "    require(!stored[id], \"dup\");",
                "    records[id] = Record(hash, score, ts,",
                "        msg.sender);",
                "    stored[id] = true;",
                "    emit Committed(id, hash, score, ts);",
                "}",
            ]
            add_code_block(slide, Inches(7.2), Inches(2.6), Inches(5.5), Inches(2.8),
                           sol_code, title="EvidenceChain.sol", lang="solidity", base_size=10)
            # 日志摘要
            log_text = ("[EXEC] node=reviewer agent=CodeReviewer ✓ 0.82s\n"
                        "[SCORE] correctness=96 completeness=98 → 97.0\n"
                        "[CHAIN] tx=0x4a2f...e91c block=1892043 ✓")
            add_log_block(slide, Inches(0.8), Inches(5.6), Inches(11.9), Inches(1.2), log_text, base_size=10)

        # ============================================================
        # TASK-016: optimization_history 优化历程页
        # ============================================================
        elif stype == 'optimization_history':
            timeline = [
                ("v1.0", "06月", "项目启动，单智能体原型", 62, C_RED),
                ("v1.5", "07月", "五维评分体系上线", 75, C_ACCENT),
                ("v2.0", "08月", "Solidity 存证合约部署主网", 82, C_ACCENT2),
                ("v2.3", "08月", "Vue Flow 可视化编排", 86, C_PURPLE),
                ("v2.5", "09月", "模板市场 30+13", 91, C_ACCENT),
                ("v2.67", "10月", "闭环打磨，稳定性 99.2%", 97, C_GREEN),
            ]
            # 时间轴
            tx = Inches(0.8)
            bar_y = Inches(4.5)
            add_rect(slide, Inches(0.8), bar_y, Inches(11.9), Inches(0.04), C_ACCENT, alpha=40)
            step_w = Inches(11.9 / len(timeline))
            for ver, date, ms, score, col in timeline:
                # 节点圆
                add_oval(slide, Emu(int(tx) + int(step_w) // 2 - int(Inches(0.18))),
                         Emu(int(bar_y) - int(Inches(0.16))), Inches(0.36), Inches(0.36), col)
                # 版本号
                add_text(slide, tx, Inches(3.5), step_w, Inches(0.35),
                         ver, size=14, color=col, bold=True, align=PP_ALIGN.CENTER)
                add_text(slide, tx, Inches(3.85), step_w, Inches(0.25),
                         date, size=11, color=C_GRAY, align=PP_ALIGN.CENTER)
                # 里程碑
                add_text(slide, tx, Inches(5.0), step_w, Inches(1.0),
                         ms, size=12, color=C_LIGHT, align=PP_ALIGN.CENTER)
                # 评分
                add_text(slide, tx, Inches(6.1), step_w, Inches(0.35),
                         f"评分 {score}", size=12, color=col, bold=True, align=PP_ALIGN.CENTER)
                tx = Emu(int(tx) + int(step_w))
            # 顶部折线图
            add_line_chart_img(slide, Inches(0.8), Inches(1.6), Inches(11.9), Inches(1.7),
                               [t[0] for t in timeline], [t[3] for t in timeline],
                               title="评分演进曲线 (62 → 97)", color='#4FC3F7')

        # ============================================================
        # TASK-017: landing 落地页
        # ============================================================
        elif stype == 'landing':
            cases = [
                ("代码审查", "wf_code_review_001", "97.0", "0x4a2f8b3e", C_ACCENT),
                ("测试生成", "wf_test_gen_002", "95.5", "0x7b1c3d5a", C_ACCENT2),
                ("安全扫描", "wf_sec_scan_003", "98.0", "0x9e2f4a8b", C_GREEN),
            ]
            cy = Inches(1.7)
            for name, wf_id, score, tx_hash, col in cases:
                add_round_rect(slide, Inches(0.8), cy, Inches(11.9), Inches(1.3), C_DEEP2, alpha=70)
                add_rect(slide, Inches(0.8), cy, Inches(0.1), Inches(1.3), col)
                add_text(slide, Inches(1.1), cy + Inches(0.1), Inches(2.0), Inches(0.4),
                         name, size=16, color=col, bold=True)
                add_text(slide, Inches(3.2), cy + Inches(0.1), Inches(3.0), Inches(0.4),
                         wf_id, size=14, color=C_LIGHT)
                add_stat_card(slide, Inches(6.5), cy + Inches(0.15), Inches(1.6), Inches(1.0),
                              score, "评分", col)
                add_text(slide, Inches(8.4), cy + Inches(0.15), Inches(4.0), Inches(0.4),
                         f"存证: {tx_hash}", size=14, color=C_ACCENT2, bold=True)
                add_text(slide, Inches(8.4), cy + Inches(0.55), Inches(4.0), Inches(0.35),
                         f"scan.botchain.ai/tx/{tx_hash[:10]}...", size=11, color=C_GRAY)
                cy = Emu(int(cy) + int(Inches(1.45)))
            add_text(slide, Inches(0.8), Inches(6.2), Inches(11.9), Inches(0.6),
                     bullets[3], size=14, color=C_LIGHT)
            add_visual_element(slide, Inches(0.3), Inches(1.7), Inches(0.5), Inches(0.5), C_GREEN, 'circle')

        # ============================================================
        # TASK-018: challenge 克服难题页
        # ============================================================
        elif stype == 'challenge':
            challenges = [
                ("Vue Flow 节点黑框", "CSS 继承冲突", "自定义节点 + scoped 样式 + border:none", C_RED),
                ("拖拽节点失效", "d3-zoom 变换矩阵未同步", "统一 transform 上下文 + onNodesChange 同步", C_ACCENT),
                ("BOT Chain RPC 超时", "主网节点响应慢", "异步提交 + 缓存 + 重试退避 + 批量上链", C_ACCENT2),
                ("多智能体并发竞争", "共享上下文写入冲突", "asyncio.Lock 分段锁 + 独立上下文快照", C_PURPLE),
                ("ArkTS/Vue3 类型不一致", "两端独立建模契约漂移", "共享 .d.ts 类型层 + 自动生成接口", C_GREEN),
            ]
            # 表头
            hy = Inches(1.6)
            add_text(slide, Inches(0.8), hy, Inches(3.0), Inches(0.35), "难题", size=14, color=C_ACCENT, bold=True)
            add_text(slide, Inches(3.9), hy, Inches(3.0), Inches(0.35), "根因", size=14, color=C_ACCENT, bold=True)
            add_text(slide, Inches(7.0), hy, Inches(5.5), Inches(0.35), "解决方案", size=14, color=C_ACCENT, bold=True)
            add_rect(slide, Inches(0.8), Emu(int(hy) + int(Inches(0.35))), Inches(11.9), Inches(0.03), C_ACCENT, alpha=40)
            ry = Inches(2.1)
            for prob, cause, sol, col in challenges:
                add_round_rect(slide, Inches(0.8), ry, Inches(11.9), Inches(0.85), C_DEEP2, alpha=60)
                add_rect(slide, Inches(0.8), ry, Inches(0.06), Inches(0.85), col)
                add_text(slide, Inches(1.0), ry + Inches(0.15), Inches(2.8), Inches(0.55),
                         prob, size=14, color=col, bold=True)
                add_text(slide, Inches(3.9), ry + Inches(0.15), Inches(3.0), Inches(0.55),
                         cause, size=14, color=C_LIGHT)
                add_text(slide, Inches(7.0), ry + Inches(0.15), Inches(5.5), Inches(0.55),
                         sol, size=14, color=C_GREEN)
                ry = Emu(int(ry) + int(Inches(0.95)))
            add_text(slide, Inches(0.8), Inches(6.9), Inches(11.9), Inches(0.3),
                     "✓ 5 个关键难题全部已解决 · 每个难题均定位根因并给出工程化方案",
                     size=14, color=C_GREEN, bold=True, align=PP_ALIGN.CENTER)

        # ============================================================
        # TASK-019: scope 适用范围页
        # ============================================================
        elif stype == 'scope':
            dims = [
                ("适用场景", ["AI 代码审查与质量评估", "自动化测试用例生成", "技术文档自动生成",
                              "缺陷智能诊断", "依赖安全扫描", "工作流模板复用"], C_ACCENT),
                ("目标用户", ["中小开发团队", "开源项目维护者", "AI 工程实践者",
                              "审计与合规人员", "DevOps 工程师"], C_ACCENT2),
                ("应用领域", ["软件工程", "AI 工程化", "区块链存证",
                              "DevOps 自动化", "开源公共物品"], C_GREEN),
            ]
            dx = Inches(0.8)
            col_w = Inches(3.9)
            for name, items, col in dims:
                add_round_rect(slide, dx, Inches(1.7), col_w, Inches(4.2), C_DEEP2, alpha=70)
                add_rect(slide, dx, Inches(1.7), col_w, Inches(0.06), col)
                add_text(slide, dx + Inches(0.2), Inches(1.8), col_w - Inches(0.3), Inches(0.4),
                         name, size=16, color=col, bold=True)
                add_bullets(slide, dx + Inches(0.2), Inches(2.3), col_w - Inches(0.3), Inches(3.5),
                            items, size=14, gap=6)
                dx = Emu(int(dx) + int(Inches(4.05)))
            # 边界范围
            add_round_rect(slide, Inches(0.8), Inches(6.1), Inches(5.8), Inches(0.9), C_DEEP2, alpha=70)
            add_rect(slide, Inches(0.8), Inches(6.1), Inches(0.06), Inches(0.9), C_GREEN)
            add_text(slide, Inches(1.0), Inches(6.15), Inches(5.5), Inches(0.35),
                     "✓ 适用边界", size=14, color=C_GREEN, bold=True)
            add_text(slide, Inches(1.0), Inches(6.5), Inches(5.5), Inches(0.4),
                     "需要多智能体协作的 AI 工程场景、需要可信存证的 AI 产出验证",
                     size=12, color=C_LIGHT)
            add_round_rect(slide, Inches(6.9), Inches(6.1), Inches(5.8), Inches(0.9), C_DEEP2, alpha=70)
            add_rect(slide, Inches(6.9), Inches(6.1), Inches(0.06), Inches(0.9), C_RED)
            add_text(slide, Inches(7.1), Inches(6.15), Inches(5.5), Inches(0.35),
                     "✗ 不适用", size=14, color=C_RED, bold=True)
            add_text(slide, Inches(7.1), Inches(6.5), Inches(5.5), Inches(0.4),
                     "纯模型训练、单点离线推理、非 AI 工作流场景",
                     size=12, color=C_LIGHT)

        # ============================================================
        # TASK-020+021: idea_reference 合并页 (project_idea + reference)
        # ============================================================
        elif stype == 'idea_reference':
            # 左侧：项目起源
            add_text(slide, Inches(0.8), Inches(1.6), Inches(6.0), Inches(0.4),
                     "项目起源：三地 OPC 实地考察", size=15, color=C_ACCENT, bold=True)
            investigations = [
                ("深圳 OPC", "AI 编码工具碎片化，需统一编排平台", C_ACCENT2),
                ("杭州 OPC", "AI 产出缺量化标准，需五维评分体系", C_ACCENT),
                ("西安 OPC", "AI 内容无可信凭证，需链上存证", C_GREEN),
            ]
            iy = Inches(2.1)
            for loc, finding, col in investigations:
                add_round_rect(slide, Inches(0.8), iy, Inches(6.0), Inches(1.0), C_DEEP2, alpha=70)
                add_rect(slide, Inches(0.8), iy, Inches(0.08), Inches(1.0), col)
                add_text(slide, Inches(1.0), iy + Inches(0.1), Inches(2.0), Inches(0.35),
                         loc, size=14, color=col, bold=True)
                add_text(slide, Inches(1.0), iy + Inches(0.45), Inches(5.5), Inches(0.5),
                         finding, size=14, color=C_LIGHT)
                iy = Emu(int(iy) + int(Inches(1.1)))
            add_round_rect(slide, Inches(0.8), Inches(5.5), Inches(6.0), Inches(1.4), C_DEEP2, alpha=80)
            add_rect(slide, Inches(0.8), Inches(5.5), Inches(0.08), Inches(1.4), C_ACCENT)
            add_text(slide, Inches(1.0), Inches(5.6), Inches(5.5), Inches(0.35),
                     "立项推导", size=14, color=C_ACCENT, bold=True)
            add_text(slide, Inches(1.0), Inches(5.95), Inches(5.5), Inches(0.9),
                     "三地共同指向「编排+评分+存证」三位一体公共基础设施。FlowForge AI 由此立项。",
                     size=14, color=C_LIGHT)
            # 右侧：参考文献
            add_text(slide, Inches(7.2), Inches(1.6), Inches(5.5), Inches(0.4),
                     "核心学术参考 (12 篇)", size=15, color=C_ACCENT2, bold=True)
            ref_list = refs.get('references', []) if refs else []
            ref_texts = []
            for r in ref_list[:10]:
                ref_texts.append(f"[{r.get('year','')}] {r.get('title','')[:40]}...")
            add_bullets(slide, Inches(7.2), Inches(2.1), Inches(5.5), Inches(4.8),
                        ref_texts, size=11, gap=4)
            add_text(slide, Inches(7.2), Inches(6.5), Inches(5.5), Inches(0.4),
                     "AutoGen · MetaGPT · LLM-as-a-Judge · ReAct · Ethereum 等",
                     size=11, color=C_GRAY)

        # ---------- 合并页: closing + roadmap ----------
        elif stype == 'closing_roadmap':
            # 左侧：总结
            add_text(slide, Inches(0.8), Inches(1.6), Inches(5.5), Inches(0.4),
                     "核心总结", size=15, color=C_ACCENT, bold=True)
            add_bullets(slide, Inches(0.8), Inches(2.0), Inches(5.5), Inches(2.0), bullets[:1], size=14, gap=6)
            tracks = [("AI×Blockchain 信任", C_ACCENT), ("GCC 公共物品", C_ACCENT2)]
            tx = Inches(0.8)
            for name, col in tracks:
                w = Inches(2.6)
                add_round_rect(slide, tx, Inches(4.2), w, Inches(0.8), C_DEEP2, alpha=80)
                add_rect(slide, tx, Inches(4.2), w, Inches(0.06), col)
                add_text(slide, tx, Inches(4.3), w, Inches(0.4),
                         name, size=14, color=col, bold=True, align=PP_ALIGN.CENTER)
                add_text(slide, tx, Inches(4.65), w, Inches(0.3),
                         "双赛道同源", size=12, color=C_LIGHT, align=PP_ALIGN.CENTER)
                tx = Emu(int(tx) + int(Inches(2.8)))
            add_text(slide, Inches(0.8), Inches(5.3), Inches(5.5), Inches(0.5),
                     "感谢聆听 · 欢迎现场验证 · Shadu Team",
                     size=14, color=C_ACCENT, bold=True)
            # 右侧：路线图
            add_text(slide, Inches(7.0), Inches(1.6), Inches(5.8), Inches(0.4),
                     "路线图", size=15, color=C_ACCENT2, bold=True)
            phases = [
                ("已完成", "v2.67 主网部署\n评分存证闭环", C_GREEN),
                ("近期", "扩展智能体模板\n开放工作流市场", C_ACCENT),
                ("中期", "引入链上激励\n奖励模板贡献者", C_ACCENT2),
                ("长期", "AI 工程质量\n公共评价存证层", C_PURPLE),
            ]
            py = Inches(2.1)
            for name, desc, col in phases:
                add_round_rect(slide, Inches(7.0), py, Inches(5.8), Inches(1.1), C_DEEP2, alpha=70)
                add_rect(slide, Inches(7.0), py, Inches(0.08), Inches(1.1), col)
                add_text(slide, Inches(7.2), py + Inches(0.1), Inches(1.5), Inches(0.35),
                         name, size=14, color=col, bold=True)
                add_text(slide, Inches(8.8), py + Inches(0.1), Inches(3.8), Inches(0.9),
                         desc, size=14, color=C_LIGHT)
                py = Emu(int(py) + int(Inches(1.2)))

        else:
            add_bullets(slide, Inches(0.8), Inches(1.7), Inches(11.7), Inches(5.0), bullets, size=16)

        # 演讲者备注
        _add_note(slide, s)
        add_page_footer(slide, i + 1, total)
        # TASK-023: 每页渲染后校验边界
        layout_guard(slide, i + 1)

    prs.save(OUT_PPTX)
    size_kb = os.path.getsize(OUT_PPTX) / 1024
    print(f"OK: {OUT_PPTX}")
    print(f"  幻灯片数: {len(slides)}")
    print(f"  文件大小: {size_kb:.1f} KB")
    print(f"  LayoutGuard 修复: {len(_guard_issues)} 处")
    if _guard_issues:
        for issue in _guard_issues[:5]:
            print(f"    - {issue}")


def _add_note(slide, s):
    note = s.get('note', '')
    if note:
        notes_tf = slide.notes_slide.notes_text_frame
        notes_tf.text = note


if __name__ == '__main__':
    build()