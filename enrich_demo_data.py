"""丰富市场模板数据 + 报告模板 + 审计日志 + 评分预选."""
import sqlite3, json, hashlib, random, os
from datetime import datetime, timedelta

DB = r'D:\西客松\backend\data\flowforge.db'
conn = sqlite3.connect(DB)
c = conn.cursor()

# 1. 丰富市场模板 - 分区域分类别
c.execute("SELECT COUNT(*) FROM marketplace_items")
current_count = c.fetchone()[0]
print(f"Current marketplace items: {current_count}")

new_items = [
    ('代码审查流水线', '自动化PR审查: 5 Agent并行', 'code-review', 'low', 5, 128, 4.8, '中国区', 'DevOps'),
    ('测试生成器', '自动生成单元测试,覆盖率90%+', 'test-generation', 'low', 3, 95, 4.6, '中国区', 'QA'),
    ('文档生成器', '自动生成API文档-多语言', 'doc-generation', 'low', 2, 76, 4.5, '中国区', 'Docs'),
    ('缺陷诊断', 'AI驱动缺陷定位,根因分析', 'bug-diagnosis', 'medium', 4, 64, 4.3, '中国区', 'QA'),
    ('安全扫描', 'SAST+依赖检查+合规审计', 'security-scan', 'medium', 3, 112, 4.7, '中国区', 'Security'),
    ('代码重构流水线', 'AI驱动的代码腐化检测与重构,同时保留行为', 'refactoring', 'high', 6, 8, 4.0, '亚太区', 'DevOps'),
    ('性能优化器', '通过基准测试分析、分析并优化应用性能', 'performance', 'medium', 4, 0, 0.0, '亚太区', 'Performance'),
    ('代码迁移助手', '通过模式转换在不同框架间迁移代码库', 'refactoring', 'high', 5, 0, 0.0, '亚太区', 'Migration'),
    ('依赖升级机器人', '安全依赖升级,包含变更分析和回归测试', 'tech-debt', 'medium', 3, 0, 0.0, '亚太区', 'DevOps'),
    ('安全审计套件', '全面安全审计:SAST+DAST+OWASP+合规检查', 'security-scan', 'high', 7, 0, 0.0, '亚太区', 'Security'),
    ('API测试生成器', '根据带有边缘情况的OpenAPI规范生成全面的API测试', 'api-design', 'medium', 4, 0, 0.0, '亚太区', 'QA'),
    ('文档审核员', '审查技术文档以确保其准确性和代码一致性', 'doc-generation', 'low', 2, 0, 0.0, '亚太区', 'Docs'),
    ('CI/CD流水线', '完整CI/CD:lint->test->build->scan->deploy.带质量门', 'ci-cd', 'high', 8, 0, 0.0, '亚太区', 'DevOps'),
    ('智能合约审计', '区块链智能合约审计,结合气体优化和形式验证', 'security-scan', 'high', 6, 0, 0.0, '全球区', 'Blockchain'),
    ('AI内容审核', '多阶段内容审核:毒性、偏见、个人身份信息(PII)、合规性', 'security-scan', 'medium', 5, 0, 0.0, '全球区', 'AI'),
    ('全栈代码审查', '前后端一体化审查,架构合理性评估', 'code-review', 'high', 8, 45, 4.4, '全球区', 'DevOps'),
    ('微服务拆分助手', '单体应用拆分为微服务,领域驱动设计', 'refactoring', 'high', 6, 12, 4.1, '全球区', 'Architecture'),
    ('数据库优化器', 'SQL优化、索引建议、查询性能分析', 'performance', 'medium', 3, 28, 4.2, '中国区', 'Database'),
    ('API网关设计', 'RESTful API设计规范,OpenAPI自动生成', 'api-design', 'medium', 4, 35, 4.3, '中国区', 'API'),
    ('前端组件生成', 'Vue/React组件自动生成,Storybook文档', 'code-review', 'low', 3, 52, 4.5, '中国区', 'Frontend'),
    ('后端服务生成', 'FastAPI/Spring Boot服务自动生成', 'api-design', 'medium', 5, 41, 4.4, '中国区', 'Backend'),
    ('代码安全加固', '输入验证、SQL注入防护、XSS防护', 'security-scan', 'medium', 4, 67, 4.6, '亚太区', 'Security'),
    ('技术债评估', '代码腐化度量化、技术债报告生成', 'tech-debt', 'low', 2, 19, 4.0, '亚太区', 'QA'),
    ('代码搜索助手', '语义化代码检索,跨仓库依赖追踪', 'code-review', 'low', 2, 33, 4.2, '全球区', 'DevOps'),
    ('区块链合约生成', 'Solidity合约自动生成,ERC20/721模板', 'api-design', 'high', 5, 15, 4.3, '全球区', 'Blockchain'),
    ('AI模型评估', '模型性能评估,准确率/召回率/F1分析', 'performance', 'medium', 3, 22, 4.1, '全球区', 'AI'),
    ('数据管道构建', 'ETL管道自动构建,数据质量检查', 'ci-cd', 'high', 6, 9, 3.9, '全球区', 'Data'),
    ('监控告警配置', 'Prometheus/Grafana监控自动配置', 'ci-cd', 'medium', 4, 17, 4.0, '亚太区', 'DevOps'),
    ('日志分析助手', '日志模式识别,异常检测,根因定位', 'bug-diagnosis', 'medium', 3, 26, 4.2, '亚太区', 'QA'),
    ('代码规范检查', 'ESLint/Prettier/Black自动配置', 'code-review', 'low', 2, 89, 4.7, '中国区', 'DevOps'),
]

if current_count < 30:
    c.execute("DELETE FROM marketplace_items")
    for i, (name, desc, scene, complexity, agent_count, usage, rating, region, category) in enumerate(new_items):
        item_id = f"market-{i+1:03d}"
        c.execute("""INSERT OR REPLACE INTO marketplace_items 
            (id, name, description, scene, complexity, agent_count, usage_count, rating, region, category, version, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (item_id, name, desc, scene, complexity, agent_count, usage, rating, region, category, 'v1.0', datetime.now().isoformat()))
    print(f"Added {len(new_items)} marketplace items with region/category")

# 2. 增加报告模板
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='report_templates'")
if c.fetchone():
    c.execute("SELECT COUNT(*) FROM report_templates")
    rpt_count = c.fetchone()[0]
    print(f"Current report templates: {rpt_count}")
    if rpt_count < 6:
        c.execute("DELETE FROM report_templates")
        reports = [
            ('exec-summary', '处决摘要', '总/成功/失败/success_rate/duration_distribution', json.dumps(['bar', 'pie']), '执行概览报告，包含成功率、耗时分布等核心指标'),
            ('performance-analysis', '性能分析', '平均/P50/P95/P99/吞吐量/直方图', json.dumps(['line', 'histogram']), '性能深度分析，分位延迟与吞吐量趋势'),
            ('error-diagnosis', '错误诊断', 'Error_type_distribution/Top10/failed_nodes', json.dumps(['pie', 'table']), '错误分类诊断，定位高频错误与失败节点'),
            ('cost-analysis', '成本分析', 'Token用量/模型成本/趋势/预算', json.dumps(['bar', 'line']), 'AI调用成本分析，Token用量与费用趋势'),
            ('quality-score', '质量评分', '五维评分/趋势/瓶颈/优化建议', json.dumps(['radar', 'line']), '五维质量评分报告，含瓶颈分析与优化建议'),
            ('security-audit', '安全审计', '漏洞统计/合规检查/敏感词/修复建议', json.dumps(['table', 'pie']), '安全审计报告，含合规检查与修复建议'),
        ]
        for tid, name, metrics, charts, desc in reports:
            c.execute("""INSERT OR REPLACE INTO report_templates
                (id, name, description, metrics, chart_types, created_at)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (tid, name, desc, metrics, charts, datetime.now().isoformat()))
        print(f"Added {len(reports)} report templates")

# 3. 增加审计日志
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='compliance_audit_logs'")
if c.fetchone():
    c.execute("SELECT COUNT(*) FROM compliance_audit_logs")
    audit_count = c.fetchone()[0]
    print(f"Current audit logs: {audit_count}")
    if audit_count < 20:
        audit_entries = [
            ('sensitive-word-check', 'politics', True, '检查通过，未发现敏感词', 'system'),
            ('sensitive-word-check', 'violence', True, '检查通过', 'system'),
            ('sensitive-word-check', 'adult', False, '发现敏感词: [redacted]', 'demo-user'),
            ('compliance-check', 'xss', True, 'XSS检查通过', 'system'),
            ('compliance-check', 'sql_injection', True, 'SQL注入检查通过', 'system'),
            ('compliance-check', 'prompt_injection', False, '检测到提示注入尝试', 'demo-user'),
            ('compliance-check', 'path_traversal', True, '路径遍历检查通过', 'system'),
            ('sensitive-word-check', 'spam', True, '检查通过', 'system'),
            ('compliance-check', 'xss', True, 'XSS检查通过', 'demo-user'),
            ('sensitive-word-check', 'politics', True, '检查通过', 'demo-user'),
            ('compliance-check', 'sql_injection', True, 'SQL注入检查通过', 'demo-user'),
            ('sensitive-word-check', 'adult', True, '检查通过', 'system'),
            ('compliance-check', 'prompt_injection', True, '提示注入检查通过', 'system'),
            ('sensitive-word-check', 'violence', False, '发现敏感词: [redacted]', 'demo-user'),
            ('compliance-check', 'path_traversal', True, '路径遍历检查通过', 'demo-user'),
            ('sensitive-word-check', 'spam', True, '检查通过', 'demo-user'),
            ('compliance-check', 'xss', True, 'XSS检查通过', 'system'),
            ('sensitive-word-check', 'politics', True, '检查通过', 'system'),
            ('compliance-check', 'sql_injection', True, 'SQL注入检查通过', 'system'),
            ('sensitive-word-check', 'adult', True, '检查通过', 'system'),
        ]
        for action, category, passed, detail, user in audit_entries:
            c.execute("""INSERT INTO compliance_audit_logs
                (action, category, passed, detail, user_id, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (action, category, 1 if passed else 0, detail, user, datetime.now().isoformat()))
        print(f"Added {len(audit_entries)} audit logs")

# 4. 确保评分仪表盘有预选数据 - 获取最新execution的score
c.execute("SELECT e.id, e.workflow_id FROM executions e ORDER BY e.started_at DESC LIMIT 1")
latest_exec = c.fetchone()
if latest_exec:
    print(f"Latest execution: {latest_exec[0]} (workflow: {latest_exec[1]})")
    c.execute("SELECT COUNT(*) FROM score_records WHERE execution_id = ?", (latest_exec[0],))
    score_count = c.fetchone()[0]
    print(f"  Score records for this execution: {score_count}")

conn.commit()

# 最终统计
for t in ['marketplace_items', 'report_templates', 'compliance_audit_logs', 'score_records', 'executions']:
    try:
        cnt = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t}: {cnt}")
    except Exception:
        pass

conn.close()
print("Done!")