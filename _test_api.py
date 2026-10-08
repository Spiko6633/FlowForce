# -*- coding: utf-8 -*-
import sys, time, asyncio
sys.path.insert(0, r'D:\西客松\backend')
from app.core.qiyuan_client import qiyuan_client
qiyuan_client.timeout_ms = 120000
qiyuan_client.max_retries = 2

async def t():
    s = time.time()
    r = await qiyuan_client.chat(
        [{"role": "system", "content": "你是PPT文案专家,输出JSON数组"},
         {"role": "user", "content": '优化3页PPT文案,每页输出{"title","subtitle","bullets":[3条]}\n页1: 流程割裂\n页2: 可编排可评分\n页3: 四层架构'}],
        max_tokens=4000, temperature=0.6)
    print('耗时 %.1fs' % (time.time() - s))
    print(r.get('choices', [{}])[0].get('message', {}).get('content', '')[:400])

asyncio.run(t())