# -*- coding: utf-8 -*-
"""串行优化剩余页面文案，避免 429 限流。"""
import sys
import json
import asyncio

sys.path.insert(0, r'D:\西客松\backend')
from app.core.qiyuan_client import qiyuan_client

SLIDES_JSON = r"D:\西客松\ppt_slides.json"

SYSTEM = (
    "你是顶级科技发布会 PPT 文案专家，擅长为 AI×Blockchain 商务发布产品规格 PPT 撰写充满科技感、"
    "动漫感、未来感的文案。要求：标题简短有力（≤18字）带科技关键词；副标题点睛（≤24字）；"
    "bullets 每条≤30字，用数据/动词/结果三段式，避免冗长。保持原意，不要编造新数据。"
    "严格输出 JSON：{\"title\":\"\",\"subtitle\":\"\",\"bullets\":[]}，不要任何额外文字。"
)

# 待优化页索引（0-based）
TARGETS = [0, 3, 4, 8, 9, 10, 11, 12, 13, 14]


async def optimize_one(slide: dict) -> dict:
    user = (
        f"页面类型: {slide.get('type')}\n"
        f"原标题: {slide.get('title')}\n"
        f"原副标题: {slide.get('subtitle')}\n"
        f"原bullets: {json.dumps(slide.get('bullets', []), ensure_ascii=False)}\n"
        "请优化为更具科技感与商务发布规格的文案，保持要点与数据不变，输出 JSON。"
    )
    data = await qiyuan_client.chat(
        [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
        max_tokens=16000, temperature=0.6,
    )
    content = data["choices"][0]["message"]["content"].strip()
    if "```" in content:
        content = content.split("```json")[-1].split("```")[0] if "```json" in content else content.split("```")[1].split("```")[0]
    s = content.find("{")
    e = content.rfind("}")
    if s != -1 and e != -1:
        content = content[s:e + 1]
    try:
        return json.loads(content)
    except Exception:
        return {}


async def main():
    slides = json.load(open(SLIDES_JSON, encoding="utf-8"))
    print(f"串行优化 {len(TARGETS)} 页，每页间隔 3 秒...")
    ok = 0
    for idx in TARGETS:
        s = slides[idx]
        try:
            opt = await optimize_one(s)
        except Exception as ex:
            print(f"  页 {idx+1} 失败: {ex}")
            await asyncio.sleep(3)
            continue
        if opt.get("title"):
            s["title"] = opt["title"]
        if opt.get("subtitle"):
            s["subtitle"] = opt["subtitle"]
        if opt.get("bullets") and isinstance(opt["bullets"], list):
            s["bullets"] = opt["bullets"]
        ok += 1
        print(f"  页 {idx+1} [{s.get('type')}] OK: {s['title'][:24]}")
        await asyncio.sleep(3)
    json.dump(slides, open(SLIDES_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\n完成，成功优化 {ok}/{len(TARGETS)} 页")
    print(f"API 总调用次数: {qiyuan_client._call_count}")


if __name__ == "__main__":
    asyncio.run(main())