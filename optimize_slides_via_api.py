# -*- coding: utf-8 -*-
"""通过奇元 API 优化 ppt_slides.json 各页文案，增强科技感与商务发布质感。
至少调用 API 5 次，分批优化 15 页。"""
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


async def optimize_one(slide: dict) -> dict:
    user = (
        f"页面类型: {slide.get('type')}\n"
        f"原标题: {slide.get('title')}\n"
        f"原副标题: {slide.get('subtitle')}\n"
        f"原bullets: {json.dumps(slide.get('bullets', []), ensure_ascii=False)}\n"
        "请优化为更具科技感与商务发布规格的文案，保持要点与数据不变，输出 JSON。"
    )
    data = await qiyuan_client.chat(
        [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
        max_tokens=16000,
        temperature=0.6,
    )
    content = data["choices"][0]["message"]["content"].strip()
    # 容错提取 JSON
    if "```" in content:
        content = content.split("```json")[-1].split("```")[0] if "```json" in content else content.split("```")[1].split("```")[0]
    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1:
        content = content[start:end + 1]
    try:
        opt = json.loads(content)
    except Exception:
        opt = {}
    return opt


async def main():
    slides = json.load(open(SLIDES_JSON, encoding="utf-8"))
    total = len(slides)
    print(f"共 {total} 页，开始分批优化（每批 3 页，共 5 次 API 调用）...")

    # 分 5 批：3+3+3+3+3
    batches = [slides[i:i + 3] for i in range(0, total, 3)]
    call_count = 0
    for bi, batch in enumerate(batches, 1):
        print(f"--- 批次 {bi}/{len(batches)}：优化第 {bi*3-2}~{min(bi*3,total)} 页 ---")
        tasks = [optimize_one(s) for s in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for ri, res in enumerate(results):
            idx = (bi - 1) * 3 + ri
            if isinstance(res, Exception) or not res:
                print(f"  页 {idx+1} 优化失败，保留原文")
                continue
            s = slides[idx]
            if res.get("title"):
                s["title"] = res["title"]
            if res.get("subtitle"):
                s["subtitle"] = res["subtitle"]
            if res.get("bullets") and isinstance(res["bullets"], list):
                s["bullets"] = res["bullets"]
            print(f"  页 {idx+1} [{s.get('type')}] 已优化: {s['title'][:20]}")
        call_count += len(batch)
        print(f"  累计 API 调用: {qiyuan_client._call_count}")

    json.dump(slides, open(SLIDES_JSON, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"\n优化完成，已写回 {SLIDES_JSON}")
    print(f"API 总调用次数: {qiyuan_client._call_count}")
    print(f"API 总 tokens: {qiyuan_client._total_tokens}")


if __name__ == "__main__":
    asyncio.run(main())