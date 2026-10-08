# -*- coding: utf-8 -*-
"""FlowForge AI 精美视频生成器 - 1080p + 多转场 + 多展现手法 + H.264/AAC."""
import json
import os
import math
import random
import subprocess
import shutil
import tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SCENES_JSON = r"D:\西客松\video_scenes.json"
OUT_VIDEO = r"D:\西客松\deliverables\FlowForgeAI_Demo.mp4"
BGM_WAV = r"D:\西客松\deliverables\FlowForgeAI_BGM.wav"

W, H = 1920, 1080
FPS = 30

C_DEEP = (10, 22, 40)
C_DEEP2 = (18, 42, 74)
C_ACCENT = (245, 182, 66)
C_ACCENT2 = (79, 195, 247)
C_WHITE = (255, 255, 255)
C_LIGHT = (232, 238, 247)
C_GRAY = (154, 165, 181)
C_GREEN = (76, 175, 80)
C_RED = (229, 62, 62)
C_PURPLE = (156, 39, 176)
C_BLUE = (33, 150, 243)

FONT_DIR = r"C:\Windows\Fonts"
FONT_BOLD = os.path.join(FONT_DIR, "msyhbd.ttc")
FONT_REG = os.path.join(FONT_DIR, "msyh.ttc")
FONT_MONO = os.path.join(FONT_DIR, "consola.ttf")
if not os.path.exists(FONT_MONO):
    FONT_MONO = FONT_REG


def get_font(size, bold=True):
    path = FONT_BOLD if bold else FONT_REG
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.truetype(FONT_REG, size)


def get_mono(size):
    try:
        return ImageFont.truetype(FONT_MONO, size)
    except Exception:
        return get_font(size, bold=False)


def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def draw_gradient_bg_fast(img, frame_idx, total_frames, c1=C_DEEP, c2=C_DEEP2):
    shift = (frame_idx / max(total_frames, 1)) * 0.2
    pixels = bytearray(W * H * 3)
    for y in range(H):
        t = (y / H) * 0.8 + shift
        if t > 1:
            t = 1
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        row = bytes([r, g, b]) * W
        off = y * W * 3
        pixels[off:off + W * 3] = row
    img.frombytes(bytes(pixels))


def draw_particles(draw, frame_idx, count=30):
    for i in range(count):
        seed = i * 137
        x = (seed * 7 + frame_idx * 3) % W
        y = (seed * 11 + frame_idx * 2) % H
        size = 2 + (seed % 4)
        col = C_ACCENT if i % 3 == 0 else C_ACCENT2
        r = size + int(2 * math.sin(frame_idx * 0.05 + i))
        if r > 0:
            draw.ellipse([x - r, y - r, x + r, y + r], fill=col)


def draw_rounded_rect(draw, xy, radius, fill, outline=None, width=1):
    x0, y0, x1, y1 = xy
    if x1 <= x0 or y1 <= y0:
        return
    r = min(radius, (x1 - x0) // 2, (y1 - y0) // 2)
    if r <= 0:
        draw.rectangle(xy, fill=fill)
        return
    draw.rectangle([x0 + r, y0, x1 - r, y1], fill=fill)
    draw.rectangle([x0, y0 + r, x1, y1 - r], fill=fill)
    draw.pieslice([x0, y0, x0 + 2 * r, y0 + 2 * r], 180, 270, fill=fill)
    draw.pieslice([x1 - 2 * r, y0, x1, y0 + 2 * r], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - 2 * r, x0 + 2 * r, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - 2 * r, y1 - 2 * r, x1, y1], 0, 90, fill=fill)
    if outline:
        draw.rounded_rectangle(xy, radius=r, outline=outline, width=width)


def draw_progress_bar(draw, x, y, w, h, progress, color=C_ACCENT):
    draw_rounded_rect(draw, [x, y, x + w, y + h], h // 2, fill=(30, 50, 80))
    if progress > 0:
        fw = int(w * min(progress, 1.0))
        draw_rounded_rect(draw, [x, y, x + fw, y + h], h // 2, fill=color)


def draw_bar_chart_anim(draw, x, y, w, h, cats, vals, progress, title=""):
    if title:
        f = get_font(36)
        draw.text((x, y - 55), title, font=f, fill=C_ACCENT)
    n = len(cats)
    bar_w = w // (n * 2)
    gap = (w - bar_w * n) // (n + 1)
    max_v = max(vals) if vals else 1
    f_cat = get_font(26)
    f_val = get_font(30, bold=True)
    for i, (cat, val) in enumerate(zip(cats, vals)):
        bx = x + gap + i * (bar_w + gap)
        bh = max(1, int((h - 80) * val / max_v * progress))
        by = y + h - 50 - bh
        col = [C_ACCENT, C_ACCENT2, C_GREEN, C_PURPLE, C_RED][i % 5]
        draw_rounded_rect(draw, [bx, by, bx + bar_w, by + bh], 10, fill=col)
        draw.text((bx + bar_w // 2, y + h - 40), cat, font=f_cat, fill=C_LIGHT, anchor='mm')
        if progress > 0.5:
            draw.text((bx + bar_w // 2, by - 30), str(val), font=f_val, fill=col, anchor='mm')


def draw_radar_anim(draw, cx, cy, r, cats, vals, progress, title=""):
    if title:
        f = get_font(36)
        draw.text((cx - 200, cy - r - 80), title, font=f, fill=C_ACCENT)
    n = len(cats)
    f_cat = get_font(28)
    for ring in [0.25, 0.5, 0.75, 1.0]:
        pts = []
        for i in range(n):
            ang = -math.pi / 2 + 2 * math.pi * i / n
            px = cx + r * ring * math.cos(ang)
            py = cy + r * ring * math.sin(ang)
            pts.append((px, py))
        draw.polygon(pts, outline=(60, 80, 110))
    for i in range(n):
        ang = -math.pi / 2 + 2 * math.pi * i / n
        draw.line([cx, cy, cx + r * math.cos(ang), cy + r * math.sin(ang)], fill=(60, 80, 110))
    pts = []
    for i in range(n):
        ang = -math.pi / 2 + 2 * math.pi * i / n
        val = vals[i] / 100 * progress
        px = cx + r * val * math.cos(ang)
        py = cy + r * val * math.sin(ang)
        pts.append((px, py))
    if len(pts) >= 3:
        draw.polygon(pts, fill=(*C_ACCENT, 80), outline=C_ACCENT)
    for i, cat in enumerate(cats):
        ang = -math.pi / 2 + 2 * math.pi * i / n
        lx = cx + (r + 50) * math.cos(ang)
        ly = cy + (r + 50) * math.sin(ang)
        draw.text((lx, ly), cat, font=f_cat, fill=C_LIGHT, anchor='mm')


def draw_scene_header(draw, title, subtitle=None):
    draw.text((140, 90), title, font=get_font(64), fill=C_WHITE)
    draw.line([140, 180, 280, 180], fill=C_ACCENT, width=7)
    if subtitle:
        draw.text((140, 200), subtitle, font=get_font(30), fill=C_GRAY)


def apply_transition(img, frame_idx, total_frames, transition):
    """分镜转场效果：fadein/fadeout/slide_left/zoom_in/zoom_out/dissolve."""
    tl = 18
    if transition == 'fadein':
        if frame_idx < tl:
            a = 1 - frame_idx / tl
            ov = Image.new('RGB', img.size, C_DEEP)
            return Image.blend(img, ov, a)
    elif transition == 'fadeout':
        if frame_idx > total_frames - tl:
            a = (frame_idx - (total_frames - tl)) / tl
            ov = Image.new('RGB', img.size, C_DEEP)
            return Image.blend(img, ov, a)
    elif transition == 'slide_left':
        if frame_idx < tl:
            t = frame_idx / tl
            t = 1 - (1 - t) ** 3
            off = int((1 - t) * W * 0.25)
            new = Image.new('RGB', img.size, C_DEEP)
            new.paste(img, (off, 0))
            return new
    elif transition == 'zoom_in':
        if frame_idx < tl:
            t = frame_idx / tl
            scale = 0.88 + 0.12 * t
            sw, sh = int(W * scale), int(H * scale)
            small = img.resize((sw, sh))
            new = Image.new('RGB', img.size, C_DEEP)
            new.paste(small, ((W - sw) // 2, (H - sh) // 2))
            return new
    elif transition == 'zoom_out':
        if frame_idx > total_frames - tl:
            t = (frame_idx - (total_frames - tl)) / tl
            scale = 1.0 - 0.12 * t
            sw, sh = int(W * scale), int(H * scale)
            small = img.resize((sw, sh))
            new = Image.new('RGB', img.size, C_DEEP)
            new.paste(small, ((W - sw) // 2, (H - sh) // 2))
            return new
    elif transition == 'dissolve':
        if frame_idx < tl:
            a = 1 - frame_idx / tl
            ov = Image.new('RGB', img.size, C_DEEP)
            return Image.blend(img, ov, a * 0.7)
        if frame_idx > total_frames - tl:
            a = (frame_idx - (total_frames - tl)) / tl
            ov = Image.new('RGB', img.size, C_DEEP)
            return Image.blend(img, ov, a * 0.7)
    return img


def draw_pip_terminal(draw, x, y, w, h, frame_idx, lines_pool):
    """画中画终端日志窗口，模拟滚动日志."""
    draw_rounded_rect(draw, [x, y, x + w, y + h], 14, fill=(8, 14, 26), outline=C_GREEN, width=3)
    draw.rectangle([x, y, x + w, y + 36], fill=(20, 30, 48))
    draw.ellipse([x + 16, y + 12, x + 28, y + 24], fill=(255, 95, 86))
    draw.ellipse([x + 36, y + 12, x + 48, y + 24], fill=(255, 189, 46))
    draw.ellipse([x + 56, y + 12, x + 68, y + 24], fill=(39, 201, 63))
    draw.text((x + w - 120, y + 8), "terminal", font=get_mono(18), fill=C_GRAY)
    f = get_mono(20)
    visible = (h - 50) // 24
    start = (frame_idx // 2) % max(1, len(lines_pool) - visible)
    for i in range(visible):
        idx = start + i
        if idx >= len(lines_pool):
            break
        line = lines_pool[idx]
        col = C_LIGHT
        if line.startswith("[OK]"):
            col = C_GREEN
        elif line.startswith("[REQ]"):
            col = C_ACCENT2
        elif line.startswith("[TOK]"):
            col = C_ACCENT
        elif line.startswith("[ERR]"):
            col = C_RED
        draw.text((x + 14, y + 44 + i * 24), line[:68], font=f, fill=col)


def render_scene(scene, scene_idx, total_scenes, tmp_dir):
    duration = scene.get('duration', 7)
    title = scene.get('title', '')
    subtitle = scene.get('subtitle', '')
    bullets = scene.get('bullets', [])
    technique = scene.get('technique', 'text_only')
    transition = scene.get('transition', 'fadein')
    total_frames = duration * FPS
    frames = []

    for fi in range(total_frames):
        img = Image.new('RGB', (W, H), C_DEEP)
        draw_gradient_bg_fast(img, fi, total_frames)
        draw = ImageDraw.Draw(img, 'RGBA')
        draw_particles(draw, fi, count=18)
        draw.ellipse([W - 420, -140, W + 140, 420], fill=(*C_ACCENT, 15))
        draw.ellipse([-140, H - 280, 280, H + 140], fill=(*C_ACCENT2, 15))

        progress = fi / total_frames

        if scene_idx == 0:
            f_title = get_font(130)
            f_sub = get_font(52)
            f_tag = get_font(36)
            t_in = min(1.0, fi / 22)
            draw.text((W // 2, H // 2 - 100), "FlowForge AI",
                      font=f_title, fill=C_WHITE, anchor='mm')
            if fi > 16:
                draw.text((W // 2, H // 2 + 40), subtitle or "多智能体工作流编排平台",
                          font=f_sub, fill=C_ACCENT2, anchor='mm')
            if fi > 32:
                tags = ["可编排", "可评分", "可存证"]
                for i, tag in enumerate(tags):
                    tx = W // 2 - 300 + i * 300
                    draw_rounded_rect(draw, [tx - 110, H // 2 + 160, tx + 110, H // 2 + 230], 35, fill=(*C_DEEP2, 220))
                    draw.text((tx, H // 2 + 195), tag, font=f_tag, fill=C_ACCENT, anchor='mm')
            if fi > 48:
                draw.text((W // 2, H - 130), "Shadu Team · v2.67 · 汉客松S1 & ETH Wuhan 2026",
                          font=get_font(30), fill=C_GRAY, anchor='mm')

        elif scene_idx == 1:
            draw_scene_header(draw, title, subtitle)
            pains = [
                ("单点生成", "AI 工具单点作战，缺乏协同", C_RED),
                ("流程割裂", "审查/测试/文档各自为政", C_RED),
                ("质量黑箱", "AI 产出缺乏量化标准", C_RED),
                ("不可溯源", "生成内容无链上凭证", C_RED),
            ]
            for i, (h, b, col) in enumerate(pains):
                slide_t = max(0, min(1, (fi - i * 10) / 15))
                if slide_t <= 0:
                    continue
                x = 140 + int((1 - slide_t) * -400)
                y = 280 + i * 170
                draw_rounded_rect(draw, [x, y, x + 1100, y + 130], 14, fill=(*C_DEEP2, 210))
                draw.rectangle([x, y, x + 10, y + 130], fill=col)
                draw.text((x + 40, y + 18), h, font=get_font(44, bold=True), fill=col)
                draw.text((x + 40, y + 78), b, font=get_font(34), fill=C_LIGHT)

        elif scene_idx == 2:
            draw_scene_header(draw, title, subtitle)
            nodes = [("输入", 320, 620), ("审查", 720, 460), ("测试", 720, 780),
                     ("文档", 1120, 380), ("安全", 1120, 860), ("输出", 1520, 620)]
            for i, (name, nx, ny) in enumerate(nodes):
                appear = max(0, min(1, (fi - i * 8) / 12))
                if appear <= 0:
                    continue
                r = int(75 * appear)
                col = [C_ACCENT, C_ACCENT2, C_ACCENT2, C_GREEN, C_GREEN, C_ACCENT][i]
                pulse = 1 + 0.08 * math.sin(fi * 0.15 + i) if fi > i * 8 + 12 else 1
                rr = int(r * pulse)
                draw.ellipse([nx - rr, ny - rr, nx + rr, ny + rr], fill=(*col, 180), outline=col, width=4)
                draw.text((nx, ny), name, font=get_font(30), fill=C_WHITE, anchor='mm')
            if fi > 30:
                lines = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 5), (4, 5)]
                line_prog = min(1.0, (fi - 30) / 20)
                for a, b in lines:
                    x1, y1 = nodes[a][1], nodes[a][2]
                    x2, y2 = nodes[b][1], nodes[b][2]
                    ex = int(x1 + (x2 - x1) * line_prog)
                    ey = int(y1 + (y2 - y1) * line_prog)
                    draw.line([x1, y1, ex, ey], fill=(*C_ACCENT, 120), width=3)
            if fi > 44:
                stats = [("13", "智能体模板"), ("65", "工作流"), ("262", "执行记录")]
                for i, (num, label) in enumerate(stats):
                    sx = 1680
                    sy = 320 + i * 130
                    draw.text((sx, sy), num, font=get_font(60, bold=True), fill=C_ACCENT)
                    draw.text((sx, sy + 70), label, font=get_font(28), fill=C_LIGHT)

        elif scene_idx == 3:
            draw_scene_header(draw, title, subtitle)
            radar_progress = min(1.0, fi / 42)
            draw_radar_anim(draw, 640, 620, 340,
                            ["正确性", "完整性", "及时性", "创新性", "稳定性"],
                            [96.5, 97.0, 95.0, 98.0, 96.0],
                            radar_progress, title="五维评分雷达图")
            if fi > 30:
                dims = [("正确性", 96.5), ("完整性", 97.0), ("及时性", 95.0), ("创新性", 98.0), ("稳定性", 96.0)]
                for i, (name, val) in enumerate(dims):
                    y = 280 + i * 110
                    draw_rounded_rect(draw, [1180, y, 1820, y + 90], 12, fill=(*C_DEEP2, 210))
                    draw.text((1210, y + 12), name, font=get_font(34), fill=C_LIGHT)
                    draw.text((1740, y + 12), f"{val}", font=get_font(40, bold=True), fill=C_ACCENT)
                    draw_progress_bar(draw, 1210, y + 62, 560, 10, val / 100, C_ACCENT)

        elif scene_idx == 4:
            draw_scene_header(draw, title, subtitle)
            steps = ["执行结果", "生成哈希", "打包存证", "写入合约", "链上可查"]
            step_w = 320
            for i, step in enumerate(steps):
                appear = max(0, min(1, (fi - i * 10) / 12))
                if appear <= 0:
                    continue
                sx = 140 + i * 350
                col = [C_ACCENT, C_ACCENT2, C_PURPLE, C_GREEN, C_ACCENT][i]
                draw_rounded_rect(draw, [sx, 460, sx + step_w, 560], 16, fill=(*C_DEEP2, 230))
                draw.rectangle([sx, 460, sx + step_w, 470], fill=col)
                draw.text((sx + step_w // 2, 510), step, font=get_font(34), fill=col, anchor='mm')
                if i < len(steps) - 1 and appear > 0.5:
                    draw.text((sx + step_w + 12, 510), "→", font=get_font(44, bold=True), fill=C_ACCENT)
            if fi > 44:
                info = [("Chain ID", "677"), ("RPC", "rpc.botchain.ai"), ("Scan", "scan.botchain.ai")]
                for i, (k, v) in enumerate(info):
                    y = 640 + i * 110
                    draw_rounded_rect(draw, [140, y, 1100, y + 90], 12, fill=(*C_DEEP2, 210))
                    draw.text((180, y + 14), k, font=get_font(34, bold=True), fill=C_ACCENT)
                    draw.text((500, y + 14), v, font=get_font(34), fill=C_LIGHT)
                draw.text((140, 1000), "任何人都可通过 BOT Chain Scan 独立验证结果真实性",
                          font=get_font(32), fill=C_ACCENT2)

        elif scene_idx == 5:
            draw_scene_header(draw, title, subtitle)
            chart_progress = min(1.0, fi / 42)
            draw_bar_chart_anim(draw, 140, 320, 1200, 620,
                                ["可信凭证", "质量评价", "去中心化", "可追溯", "防篡改"],
                                [95, 90, 88, 92, 96],
                                chart_progress, title="赛道契合度")
            if fi > 30:
                texts = ["AI 产生可信凭证", "链上不可篡改", "可审计可追溯"]
                for i, t in enumerate(texts):
                    y = 380 + i * 130
                    draw.text((1480, y), "▸", font=get_font(44, bold=True), fill=C_ACCENT)
                    draw.text((1540, y), t, font=get_font(36), fill=C_LIGHT)

        elif scene_idx == 6:
            draw_scene_header(draw, title, subtitle)
            attrs = [
                ("开放性", "30 模板 + 13 智能体免费开放", C_ACCENT),
                ("可复用", "模板可组合，评分可对标", C_GREEN),
                ("非排他", "使用不排他，多人可贡献", C_ACCENT2),
                ("社会价值", "降低 AI 工程门槛，统一质量基准", C_PURPLE),
            ]
            for i, (k, v, col) in enumerate(attrs):
                appear = max(0, min(1, (fi - i * 8) / 12))
                if appear <= 0:
                    continue
                y = 290 + i * 160
                x = 140 + int((1 - appear) * -300)
                draw_rounded_rect(draw, [x, y, x + 1640, y + 130], 14, fill=(*C_DEEP2, 210))
                draw.rectangle([x, y, x + 12, y + 130], fill=col)
                draw.text((x + 50, y + 20), k, font=get_font(40, bold=True), fill=col)
                draw.text((x + 420, y + 28), v, font=get_font(36), fill=C_LIGHT)
            if fi > 40:
                draw.text((140, 1000), "✓ 使用人数越多，公共价值越高",
                          font=get_font(36, bold=True), fill=C_GREEN)

        elif scene_idx == 7:
            draw_scene_header(draw, title, subtitle)
            tracks = [
                ("AI × Blockchain 主赛道", "多智能体编排 + 链上存证解决 AI 可信度", C_ACCENT),
                ("GCC 公共物品分赛道", "开放模板与评分标准赋能全行业", C_GREEN),
                ("双赛道同源", "同一套代码、数据、信任体系", C_ACCENT2),
            ]
            for i, (name, desc, col) in enumerate(tracks):
                appear = max(0, min(1, (fi - i * 12) / 15))
                if appear <= 0:
                    continue
                y = 300 + i * 220
                x = 140 + int((1 - appear) * -400)
                draw_rounded_rect(draw, [x, y, x + 1640, y + 170], 16, fill=(*C_DEEP2, 210))
                draw.rectangle([x, y, x + 14, y + 170], fill=col)
                draw.text((x + 60, y + 30), name, font=get_font(48, bold=True), fill=col)
                draw.text((x + 60, y + 100), desc, font=get_font(36), fill=C_LIGHT)
            if fi > 50:
                draw.text((W // 2, H - 120), "FlowForge AI v2.67 · Shadu Team",
                          font=get_font(36, bold=True), fill=C_ACCENT, anchor='mm')

        elif scene_idx == 8:
            draw_scene_header(draw, title, subtitle)
            chart_progress = min(1.0, fi / 42)
            draw_bar_chart_anim(draw, 140, 320, 1200, 580,
                                ["工作流", "执行记录", "评分记录", "市场模板", "智能体模板"],
                                [65, 262, 594, 30, 13],
                                chart_progress, title="真实运行数据统计")
            stats = [("65", "工作流", C_ACCENT), ("262", "执行", C_ACCENT2), ("594", "评分", C_GREEN)]
            for i, (num, label, col) in enumerate(stats):
                appear = max(0, min(1, (fi - 30 - i * 6) / 12))
                if appear <= 0:
                    continue
                y = 360 + i * 170
                x = 1480
                draw_rounded_rect(draw, [x, y, x + 380, y + 130], 14, fill=(*C_DEEP2, 210))
                draw.rectangle([x, y, x + 12, y + 130], fill=col)
                draw.text((x + 50, y + 18), num, font=get_font(60, bold=True), fill=col)
                draw.text((x + 50, y + 88), label, font=get_font(30), fill=C_LIGHT)
            if fi > 55:
                draw.text((140, 1000), "这些都是真实沉淀 · 欢迎现场验证",
                          font=get_font(36, bold=True), fill=C_ACCENT2)

        elif scene_idx == 9:
            draw_scene_header(draw, title, subtitle)
            draw_rounded_rect(draw, [140, 290, 820, 980], 16, fill=(*C_DEEP2, 210))
            draw.text((170, 310), "▌ 任务输入", font=get_font(30, bold=True), fill=C_ACCENT2)
            draw_rounded_rect(draw, [170, 360, 790, 440], 10, fill=(30, 50, 80))
            draw.text((190, 378), "完成一份带链上存证的竞品分析报告",
                      font=get_font(28), fill=C_WHITE)
            if fi > 10:
                draw.text((170, 470), "▌ Planner 拆解", font=get_font(30, bold=True), fill=C_ACCENT2)
                subtasks = ["1. 竞品清单调研", "2. 功能对比矩阵", "3. 差异分析报告", "4. 链上存证打包", "5. 评分自检"]
                for i, st in enumerate(subtasks):
                    appear = max(0, min(1, (fi - 14 - i * 6) / 10))
                    if appear <= 0:
                        continue
                    draw.text((190, 510 + i * 44), st, font=get_font(26), fill=C_LIGHT)
            draw.text((170, 920), "全程零人工干预", font=get_font(30, bold=True), fill=C_GREEN)
            tx, ty, tw, th = 880, 290, 920, 690
            draw_rounded_rect(draw, [tx, ty, tx + tw, ty + th], 16, fill=(8, 14, 26))
            draw.rectangle([tx, ty, tx + tw, ty + 44], fill=(20, 30, 48))
            draw.text((tx + 20, ty + 10), "Agent 执行轨迹", font=get_font(26), fill=C_ACCENT)
            agents = [
                ("Planner", "拆解任务 → 5 子任务", C_ACCENT, 0),
                ("Researcher", "调用 web_search × 3", C_ACCENT2, 8),
                ("Coder", "生成对比矩阵代码", C_GREEN, 16),
                ("Reviewer", "审查报告完整性 96.5", C_PURPLE, 24),
                ("Coder", "打包存证 → hash 0x3f..a2", C_GREEN, 32),
                ("Reviewer", "五维评分通过 ✓", C_GREEN, 40),
            ]
            for i, (agent, action, col, start_f) in enumerate(agents):
                appear = max(0, min(1, (fi - start_f) / 10))
                if appear <= 0:
                    continue
                ny = ty + 70 + i * 100
                pulse = 1 + 0.1 * math.sin(fi * 0.2 + i) if appear >= 1 else appear
                draw.ellipse([tx + 40, ny + 10, tx + 80, ny + 50], fill=(*col, 200), outline=col, width=3)
                draw.text((tx + 60, ny + 30), str(i + 1), font=get_font(24, bold=True), fill=C_WHITE, anchor='mm')
                draw.text((tx + 110, ny + 8), agent, font=get_font(30, bold=True), fill=col)
                draw.text((tx + 110, ny + 48), action, font=get_font(26), fill=C_LIGHT)
                if i > 0 and appear > 0.3:
                    draw.line([tx + 60, ny - 50, tx + 60, ny + 10], fill=(*col, 120), width=3)

        elif scene_idx == 10:
            draw_scene_header(draw, title, subtitle)
            draw_rounded_rect(draw, [140, 290, 1780, 720], 16, fill=(*C_DEEP2, 210))
            draw.text((180, 310), "FlowForge AI · 多模型路由控制台", font=get_font(30), fill=C_ACCENT2)
            models = [
                ("deepseek-v4.1", "竞品分析 · 8421 tok", C_GREEN, 0),
                ("qwen3-coder", "代码生成 · 3150 tok", C_ACCENT2, 8),
                ("glm-4.6", "报告润色 · 5210 tok", C_ACCENT, 16),
                ("deepseek-v4.1", "存证摘要 · 1280 tok", C_GREEN, 24),
            ]
            for i, (model, task, col, start_f) in enumerate(models):
                appear = max(0, min(1, (fi - start_f) / 10))
                if appear <= 0:
                    continue
                y = 380 + i * 80
                draw_rounded_rect(draw, [180, y, 1740, y + 65], 10, fill=(30, 50, 80))
                draw.rectangle([180, y, 190, y + 65], fill=col)
                draw.text((210, y + 12), model, font=get_mono(28), fill=col)
                draw.text((620, y + 12), task, font=get_font(28), fill=C_LIGHT)
                bar_p = min(1.0, (fi - start_f - 4) / 12)
                draw_progress_bar(draw, 1100, y + 24, 580, 14, max(0, bar_p), col)
            total_tok = 8421 + 3150 + 5210 + 1280
            tok_disp = int(total_tok * min(1.0, fi / 40))
            draw.text((180, 740), f"累计 Token: {tok_disp:,}", font=get_font(34, bold=True), fill=C_ACCENT)
            draw.text((700, 740), "平均延迟 1.2s · 成功率 100%", font=get_font(34), fill=C_LIGHT)
            log_lines = [
                "[REQ] POST /v1/chat/completions model=deepseek-v4.1",
                "[TOK] stream chunk 1/24 elapsed=0.3s",
                "[TOK] stream chunk 12/24 elapsed=0.7s",
                "[OK] 200 usage.total_tokens=8421 latency=1.1s",
                "[REQ] POST /v1/chat/completions model=qwen3-coder",
                "[TOK] stream chunk 1/18 elapsed=0.2s",
                "[OK] 200 usage.total_tokens=3150 latency=0.9s",
                "[REQ] POST /v1/chat/completions model=glm-4.6",
                "[ERR] 503 timeout, retry 1/3",
                "[OK] 200 usage.total_tokens=5210 latency=1.5s",
                "[REQ] POST /v1/chat/completions model=deepseek-v4.1",
                "[OK] 200 usage.total_tokens=1280 latency=0.8s",
                "[OK] all tasks completed, chain hash 0x3f7c..a2e1",
            ]
            draw_pip_terminal(draw, 140, 800, 1640, 230, fi, log_lines)

        elif scene_idx == 11:
            draw_scene_header(draw, title, subtitle)
            layers = [
                ("存证层", "哈希摘要写入链上合约 · Chain ID 677", C_GREEN, 0),
                ("评分层", "五维评分引擎 · 594 条记录", C_ACCENT, 8),
                ("执行层", "工具调用 · 模型路由 · 上下文记忆", C_ACCENT2, 16),
                ("编排层", "任务图调度 · 智能体生命周期", C_PURPLE, 24),
            ]
            for i, (name, desc, col, start_f) in enumerate(layers):
                appear = max(0, min(1, (fi - start_f) / 12))
                if appear <= 0:
                    continue
                y = 820 - i * 140
                x = 140 + int((1 - appear) * 300)
                draw_rounded_rect(draw, [x, y, x + 1640, y + 110], 16, fill=(*C_DEEP2, 220))
                draw.rectangle([x, y, x + 1640, y + 14], fill=col)
                draw.text((x + 50, y + 28), name, font=get_font(42, bold=True), fill=col)
                draw.text((x + 50, y + 78), desc, font=get_font(30), fill=C_LIGHT)
            if fi > 36:
                flow_t = min(1.0, (fi - 36) / 30)
                for i in range(3):
                    y_from = 820 - (i + 1) * 140 + 55
                    y_to = 820 - i * 140 + 55
                    cur_y = int(y_from + (y_to - y_from) * flow_t)
                    col = lerp_color(C_BLUE, C_GREEN, flow_t)
                    draw.ellipse([1780, cur_y - 12, 1804, cur_y + 12], fill=col)
                    draw.line([1792, y_from, 1792, cur_y], fill=col, width=5)
            if fi > 60:
                draw.text((W // 2, 1000), "数据自上而下流动 · 颜色由蓝转绿 · 可信闭环",
                          font=get_font(30), fill=C_ACCENT2, anchor='mm')

        elif scene_idx == 12:
            draw_scene_header(draw, title, subtitle)
            cards = [
                ("技术亮点", "可验证的多智能体协作\n结果可量化 · 可追溯 · 可复现", C_ACCENT, 0),
                ("赛道契合", "AI×Blockchain 主赛道\nGCC 公共物品分赛道双线命中", C_GREEN, 12),
                ("落地状态", "已跑通真实运行数据\n非概念原型 · 具备开源潜力", C_ACCENT2, 24),
            ]
            card_w = 520
            gap = 60
            total_w = card_w * 3 + gap * 2
            start_x = (W - total_w) // 2
            for i, (h, b, col, start_f) in enumerate(cards):
                appear = max(0, min(1, (fi - start_f) / 14))
                if appear <= 0:
                    continue
                ease = 1 - (1 - appear) ** 3
                y_off = int((1 - ease) * 80)
                cx = start_x + i * (card_w + gap)
                cy = 360 + y_off
                draw_rounded_rect(draw, [cx, cy, cx + card_w, cy + 360], 20, fill=(*C_DEEP2, 230))
                draw.rectangle([cx, cy, cx + card_w, cy + 16], fill=col)
                draw.text((cx + card_w // 2, cy + 70), h, font=get_font(44, bold=True), fill=col, anchor='mm')
                for j, line in enumerate(b.split('\n')):
                    draw.text((cx + card_w // 2, cy + 160 + j * 56), line,
                              font=get_font(30), fill=C_LIGHT, anchor='mm')
                draw.ellipse([cx + card_w // 2 - 30, cy + 300, cx + card_w // 2 + 30, cy + 360],
                             fill=(*col, 80), outline=col, width=3)
            if fi > 56:
                merge_t = min(1.0, (fi - 56) / 20)
                alpha = int(255 * merge_t)
                draw.text((W // 2, 820), "FlowForge AI",
                          font=get_font(72, bold=True), fill=C_ACCENT, anchor='mm')
                draw.text((W // 2, 910), "Shadu Team · 汉客松S1 & ETH Wuhan 2026",
                          font=get_font(34), fill=C_GRAY, anchor='mm')

        if fi % 2 == 0:
            random.seed(fi)
            for _ in range(4000):
                nx = random.randint(0, W - 1)
                ny = random.randint(0, H - 1)
                nc = random.randint(15, 80)
                draw.point((nx, ny), fill=(nc, nc, nc))

        draw_progress_bar(draw, 140, H - 40, W - 280, 8, progress, C_ACCENT)
        draw.text((W - 200, H - 80), f"{scene_idx + 1} / {total_scenes}",
                  font=get_font(28), fill=C_GRAY)

        img = apply_transition(img, fi, total_frames, transition)

        fp = os.path.join(tmp_dir, f"s{scene_idx}_f{fi:05d}.jpg")
        img.save(fp, 'JPEG', quality=92)
        frames.append(fp)

    return frames


def build():
    scenes = json.load(open(SCENES_JSON, encoding='utf-8'))
    total_scenes = len(scenes)
    total_duration = sum(s.get('duration', 7) for s in scenes)
    techniques = sorted({s.get('technique', 'text_only') for s in scenes})
    transitions = sorted({s.get('transition', 'fadein') for s in scenes})
    print(f"场景数: {total_scenes} | 总时长: {total_duration}s | 分辨率: {W}x{H} | FPS: {FPS}")
    print(f"展现手法({len(techniques)}): {techniques}")
    print(f"转场({len(transitions)}): {transitions}")

    tmp_dir = tempfile.mkdtemp(prefix='ffvideo_')
    print(f"临时目录: {tmp_dir}")

    all_frames = []
    for si, scene in enumerate(scenes):
        print(f"渲染场景 {si + 1}/{total_scenes}: {scene.get('title', '')} [{scene.get('technique')}]...")
        frames = render_scene(scene, si, total_scenes, tmp_dir)
        all_frames.extend(frames)

    print(f"总帧数: {len(all_frames)}")

    list_file = os.path.join(tmp_dir, 'frames.txt')
    with open(list_file, 'w', encoding='utf-8') as f:
        for fp in all_frames:
            f.write(f"file '{fp}'\n")

    has_bgm = os.path.exists(BGM_WAV)
    cmd = [
        'ffmpeg', '-y', '-r', str(FPS), '-f', 'concat', '-safe', '0',
        '-i', list_file,
    ]
    if has_bgm:
        cmd += ['-stream_loop', '-1', '-i', BGM_WAV, '-shortest']
    cmd += [
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-crf', '8', '-preset', 'slow', '-b:v', '12M', '-maxrate', '18M', '-bufsize', '24M',
    ]
    if has_bgm:
        cmd += ['-c:a', 'aac', '-b:a', '192k', '-ar', '44100', '-ac', '2']
    cmd += ['-movflags', '+faststart', OUT_VIDEO]

    print("合成视频..." + (" (含BGM/AAC音频)" if has_bgm else " (无音频)"))
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    if r.returncode != 0:
        print("ffmpeg stderr:", r.stderr[-3000:])
        raise RuntimeError("ffmpeg failed")

    size_mb = os.path.getsize(OUT_VIDEO) / (1024 * 1024)
    print(f"OK: {OUT_VIDEO}")
    print(f"  帧数: {len(all_frames)} | 大小: {size_mb:.1f} MB | 时长: {total_duration}s")

    shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == '__main__':
    build()