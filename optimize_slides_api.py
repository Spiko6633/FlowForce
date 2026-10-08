# -*- coding: utf-8 -*-
"""调用奇元 API 优化 ppt_slides.json 各页文案，增强科技感、动画动漫感与商务发布规格。
分 6 组并发调用（≥5 次要求），结果直接写回 ppt_slides.json，并输出报告。
"""
import sys
import json
import asyncio
import logging
import shutil
import os

sys.path.insert(0, r'D:\西客松\backend')
from app.core.qiyuan_client import qiyuan_client

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

SRC = r"D:\西客松\ppt_slides.json"
BACKUP = r"D:\西客松\ppt_slides_backup.json"
REPORT = r"D:\西客松\api_optimize_report.json"

SYS_PROMPT = (
    "你是顶级科技产品发布会 PPT 文案专家，擅长为 AI×Blockchain 产品撰写"
    "充满科技感、未来感、动画动漫冲击力的商务发布规格文案。"
    "风格要求：标题简短有力（≤18字）带科技关键词；副标题点睛（≤26字）点明核心价值；"
    "bullets 每条≤32字，用「关键词＋短描述＋数据」结构，动词开头，科技词汇密集。"
    "必须保留所有关键数据与专有名词（FlowForge AI、BOT Chain、Chain ID 677、v2.67、"
    "Vue3、FastAPI、ArkTS、Solidity、Shadu Team、65 工作流、262 执行、594 评分、"
    "30 模板、13 智能体等），不杜撰新数据。"
    "严格只输出 JSON 数组，不要 markdown 代码块，不要任何解释文字。"
)


def build_user_prompt(chunk, hint):
    lines = [f"优化以下 {len(chunk)} 页 PPT 文案。{hint}"]
    for s in chunk:
        lines.append(f"\n【页类型: {s.get('type')}】")
        lines.append(f"原标题: {s.get('title')}")
        lines.append(f"原副标题: {s.get('subtitle')}")
        lines.append("原要点:")
        for b in s.get('bullets', []):
            lines.append(f"  - {b}")
    lines.append(f"\n对每页输出优化后 JSON，整体输出 JSON 数组，长度={len(chunk)}，顺序对应。")
    lines.append("每项格式: {\"title\":\"\",\"subtitle\":\"\",\"bullets\":[\"\"]}")
    lines.append(f"bullets 数量必须与原页一致。")
    return "\n".join(lines)


def extract_json_array(text):
    t = text.strip()
    if t.startswith("```"):
        t = t.split("```", 2)[1]
        if t.lower().startswith("json"):
            t = t[4:]
        t = t.strip()
        if t.endswith("```"):
            t = t[:-3].strip()
    lo = t.find('[')
    hi = t.rfind(']')
    if lo != -1 and hi != -1 and hi > lo:
        return json.loads(t[lo:hi + 1])
    raise ValueError("无法解析 JSON 数组: %s" % t[:200])


async def optimize_chunk(idx, chunk, hint):
    user = build_user_prompt(chunk, hint)
    try:
        resp = await qiyuan_client.chat(
            [{"role": "system", "content": SYS_PROMPT},
             {"role": "user", "content": user}],
            max_tokens=12000, temperature=0.8,
        )
        content = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
        arr = extract_json_array(content)
        if isinstance(arr, list) and len(arr) == len(chunk):
            logging.info("组#%d 优化成功: %d 页", idx, len(arr))
            return idx, arr
        logging.warning("组#%d 返回数量不匹配 %d!=%d", idx, len(arr) if isinstance(arr, list) else -1, len(chunk))
        return idx, None
    except Exception as e:
        logging.warning("组#%d API 失败: %s", idx, e)
        return idx, None


async def main():
    # 备份原文件
    shutil.copy2(SRC, BACKUP)
    slides = json.load(open(SRC, encoding='utf-8'))

    # 分 6 组（≥5 次调用），每组带专属优化提示
    groups = [
        (slides[0:1], "封面页：突出产品名 FlowForge AI、v2.67、双赛道、全栈技术，要有发布会震撼开场感"),
        (slides[1:3], "痛点与解决方案：痛点要尖锐扎心，解决方案要一一对应且有力，形成对比冲击"),
        (slides[3:5], "架构与核心功能：强调四层解耦、三位一体、真实运行数据，用工程化语言"),
        (slides[5:8], "双赛道契合、竞争优势、链部署：突出真实运行与差异化壁垒，数据即证据"),
        (slides[8:11], "代码证据、版本演进、落地案例：用溯源 ID、交易哈希、评分曲线增强可信度"),
        (slides[11:15], "克服难题、适用范围、项目起源、总结路线图：收尾要有力，展望未来感"),
    ]

    # 并发调用（qiyuan_client 内部信号量控制并发=4）
    tasks = [optimize_chunk(i + 1, chunk, hint) for i, (chunk, hint) in enumerate(groups)]
    results = await asyncio.gather(*tasks)

    call_count = qiyuan_client._call_count
    success = 0
    offsets = [0, 1, 3, 5, 8, 11]  # 每组起始索引
    for idx, arr in results:
        if arr is None:
            continue
        success += 1
        off = offsets[idx - 1]
        for j, opt in enumerate(arr):
            if not isinstance(opt, dict):
                continue
            si = off + j
            if opt.get("title"):
                slides[si]["title"] = opt["title"]
            if opt.get("subtitle"):
                slides[si]["subtitle"] = opt["subtitle"]
            nb = opt.get("bullets")
            if isinstance(nb, list) and nb:
                slides[si]["bullets"] = nb

    # 写回
    json.dump(slides, open(SRC, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    report = {
        "api_call_count": call_count,
        "groups_total": len(groups),
        "groups_success": success,
        "stats": qiyuan_client.stats,
    }
    json.dump(report, open(REPORT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    print(f"API 调用次数: {call_count}")
    print(f"成功优化组数: {success}/{len(groups)}")
    print(f"已写回: {SRC}")


if __name__ == '__main__':
    asyncio.run(main())