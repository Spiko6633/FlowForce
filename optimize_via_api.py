# -*- coding: utf-8 -*-
"""调用奇元API优化视频文案 - 字幕/分镜/配乐三维度."""
import sys
import json
import os

sys.path.insert(0, r'D:\西客松\backend')
from app.core.qiyuan_client import qiyuan_client
import asyncio

SCENES_JSON = r"D:\西客松\video_scenes.json"
OUT_DIR = r"D:\西客松\deliverables"

SCENES_TEXT = json.load(open(SCENES_JSON, encoding='utf-8'))


def extract_text(scenes):
    lines = []
    for s in scenes:
        lines.append(f"[场景{s['scene']}] 标题:{s['title']} | 副标题:{s['subtitle']}")
        for b in s.get('bullets', []):
            lines.append(f"  - {b}")
    return "\n".join(lines)


async def optimize_subtitles():
    """第1次API: 优化字幕文案 - 更精炼有科技感."""
    raw = extract_text(SCENES_TEXT)
    messages = [
        {"role": "system", "content": "你是ToB科技产品视频文案专家。输出必须为纯JSON，不要markdown代码块。"},
        {"role": "user", "content": f"""以下是一个13场景的科技产品演示视频字幕。请优化每条文案，要求：
1. 更精炼（每条bullet不超过22字），更有科技感和商务感
2. 保留核心数据数字不变（65/262/594/30/13/677/v2.67等）
3. 保留每场景的title不变，只优化subtitle和bullets
4. 用词更专业凝练，去掉口语化表达

原始文案：
{raw}

输出JSON格式：
{{"scenes":[{{"scene":1,"subtitle":"...","bullets":["...","..."]}},...]}}
只输出JSON，不要其他文字。"""}
    ]
    r = await qiyuan_client.chat(messages, max_tokens=16000, temperature=0.6)
    return r


async def optimize_storyboard():
    """第2次API: 优化分镜note和转场节奏建议."""
    notes = []
    for s in SCENES_TEXT:
        notes.append(f"[场景{s['scene']}] technique={s['technique']} transition={s['transition']} duration={s['duration']}s note={s['note']}")
    raw = "\n".join(notes)
    messages = [
        {"role": "system", "content": "你是视频分镜导演。输出必须为纯JSON，不要markdown代码块。"},
        {"role": "user", "content": f"""以下是一个13场景科技演示视频的分镜表。请优化每个场景的note（拍摄指导），并给出转场流畅度改进建议：
1. note要更具体可执行，描述元素入场时机和动效
2. 保留原有technique和transition不变
3. 优化duration分配建议（总时长保持在90-120s之间，当前总时长107s）
4. 让转场衔接更流畅自然

原始分镜：
{raw}

输出JSON格式：
{{"scenes":[{{"scene":1,"note":"...","duration":7}},...]}}
只输出JSON，不要其他文字。"""}
    ]
    r = await qiyuan_client.chat(messages, max_tokens=16000, temperature=0.6)
    return r


async def optimize_bgm_timing():
    """第3次API: 优化配乐节奏与场景情绪映射建议."""
    scene_info = []
    for s in SCENES_TEXT:
        scene_info.append(f"场景{s['scene']}: {s['title']} | {s['technique']} | {s['duration']}s")
    raw = "\n".join(scene_info)
    messages = [
        {"role": "system", "content": "你是影视配乐总监。输出必须为纯JSON，不要markdown代码块。"},
        {"role": "user", "content": f"""以下是一个13场景科技产品演示视频（总时长107s，1920x1080）的场景序列。
请为每个场景给出配乐情绪和节奏建议，以及整体BGM编排策略：
1. 每场景标注情绪基调（如:科技感/紧张/振奋/沉稳/收束）
2. 节奏BPM建议
3. 音量曲线建议（0-1）
4. 转场处的音频过渡方式

场景序列：
{raw}

输出JSON格式：
{{"strategy":"整体策略描述","scenes":[{{"scene":1,"mood":"...","bpm":120,"volume":0.8,"transition_audio":"..."}},...]}}
只输出JSON，不要其他文字。"""}
    ]
    r = await qiyuan_client.chat(messages, max_tokens=16000, temperature=0.7)
    return r


def save_result(name, result):
    path = os.path.join(OUT_DIR, f"api_optimize_{name}.json")
    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] {name} -> {path} ({len(content)} chars)")
    return content


async def main():
    print("=== 串行调用3次奇元API优化视频文案 ===")
    names = ["subtitles", "storyboard", "bgm_timing"]
    funcs = [optimize_subtitles, optimize_storyboard, optimize_bgm_timing]
    for name, fn in zip(names, funcs):
        print(f"  调用 {name} ...")
        try:
            result = await fn()
            save_result(name, result)
        except Exception as e:
            print(f"  [WARN] {name} 失败: {e}")
        await asyncio.sleep(12)
    stats = qiyuan_client.stats
    print(f"\nAPI调用统计: calls={stats['call_count']} tokens={stats['total_tokens']} model={stats['model']}")
    return stats


if __name__ == "__main__":
    asyncio.run(main())