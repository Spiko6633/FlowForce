"""丰富市场模板数据 - 匹配真实表结构."""
import sqlite3, json
from datetime import datetime

DB = r'D:\西客松\backend\data\flowforge.db'
conn = sqlite3.connect(DB)
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM marketplace_items")
print(f"Current marketplace items: {c.fetchone()[0]}")

c.execute("DELETE FROM marketplace_items")

items = [
    ('workflow_template', 'wf-code-review', '代码审查流水线', '自动化PR审查: 5 Agent并行', 'code-review', 'code-review', 'v1.0', 'FlowForge', 128, 4.8, ['code-review', 'pr', 'automation'], True),
    ('workflow_template', 'wf-test-gen', '测试生成器', '自动生成单元测试,覆盖率90%+', 'test-generation', 'test-gen', 'v1.0', 'FlowForge', 95, 4.6, ['test', 'coverage', 'qa'], True),
    ('workflow_template', 'wf-doc-gen', '文档生成器', '自动生成API文档-多语言', 'doc-generation', 'doc-gen', 'v1.0', 'FlowForge', 76, 4.5, ['docs', 'api', 'multilingual'], True),
    ('workflow_template', 'wf-defect-diag', '缺陷诊断', 'AI驱动缺陷定位,根因分析', 'bug-diagnosis', 'defect-diag', 'v1.0', 'FlowForge', 64, 4.3, ['bug', 'diagnosis', 'root-cause'], True),
    ('workflow_template', 'wf-security-scan', '安全扫描', 'SAST+依赖检查+合规审计', 'security-scan', 'security-scan', 'v1.0', 'FlowForge', 112, 4.7, ['security', 'sast', 'compliance'], True),
    ('workflow_template', 'wf-refactor', '代码重构流水线', 'AI驱动的代码腐化检测与重构,同时保留行为', 'refactoring', 'refactoring', 'v1.0', 'FlowForge', 8, 4.0, ['refactor', 'tech-debt'], True),
    ('workflow_template', 'wf-perf-opt', '性能优化器', '通过基准测试分析、分析并优化应用性能', 'performance', 'perf-opt', 'v1.0', 'FlowForge', 33, 4.2, ['performance', 'benchmark'], True),
    ('workflow_template', 'wf-migration', '代码迁移助手', '通过模式转换在不同框架间迁移代码库', 'refactoring', 'migration', 'v1.0', 'FlowForge', 15, 4.1, ['migration', 'framework'], True),
    ('workflow_template', 'wf-dep-upgrade', '依赖升级机器人', '安全依赖升级,包含变更分析和回归测试', 'tech-debt', 'dep-upgrade', 'v1.0', 'FlowForge', 22, 4.0, ['dependency', 'upgrade'], True),
    ('workflow_template', 'wf-security-audit', '安全审计套件', '全面安全审计:SAST+DAST+OWASP+合规检查', 'security-scan', 'security-audit', 'v1.0', 'FlowForge', 45, 4.4, ['security', 'audit', 'owasp'], True),
    ('workflow_template', 'wf-api-test', 'API测试生成器', '根据带有边缘情况的OpenAPI规范生成全面的API测试', 'api-design', 'api-test', 'v1.0', 'FlowForge', 28, 4.2, ['api', 'test', 'openapi'], True),
    ('workflow_template', 'wf-doc-review', '文档审核员', '审查技术文档以确保其准确性和代码一致性', 'doc-generation', 'doc-review', 'v1.0', 'FlowForge', 19, 4.0, ['docs', 'review'], True),
    ('workflow_template', 'wf-cicd', 'CI/CD流水线', '完整CI/CD:lint->test->build->scan->deploy.带质量门', 'ci-cd', 'cicd', 'v1.0', 'FlowForge', 67, 4.5, ['cicd', 'devops', 'automation'], True),
    ('workflow_template', 'wf-contract-audit', '智能合约审计', '区块链智能合约审计,结合气体优化和形式验证', 'security-scan', 'contract-audit', 'v1.0', 'FlowForge', 12, 4.3, ['blockchain', 'solidity', 'audit'], True),
    ('workflow_template', 'wf-content-moderation', 'AI内容审核', '多阶段内容审核:毒性、偏见、PII、合规性', 'security-scan', 'content-moderation', 'v1.0', 'FlowForge', 18, 4.1, ['ai', 'moderation', 'compliance'], True),
    ('workflow_template', 'wf-fullstack-review', '全栈代码审查', '前后端一体化审查,架构合理性评估', 'code-review', 'fullstack-review', 'v1.0', 'FlowForge', 41, 4.4, ['fullstack', 'architecture'], True),
    ('workflow_template', 'wf-microservice-split', '微服务拆分助手', '单体应用拆分为微服务,领域驱动设计', 'refactoring', 'microservice-split', 'v1.0', 'FlowForge', 9, 3.9, ['microservice', 'ddd'], True),
    ('workflow_template', 'wf-db-optimizer', '数据库优化器', 'SQL优化、索引建议、查询性能分析', 'performance', 'db-optimizer', 'v1.0', 'FlowForge', 26, 4.2, ['database', 'sql', 'optimization'], True),
    ('workflow_template', 'wf-api-gateway', 'API网关设计', 'RESTful API设计规范,OpenAPI自动生成', 'api-design', 'api-gateway', 'v1.0', 'FlowForge', 35, 4.3, ['api', 'gateway', 'openapi'], True),
    ('workflow_template', 'wf-frontend-gen', '前端组件生成', 'Vue/React组件自动生成,Storybook文档', 'code-review', 'frontend-gen', 'v1.0', 'FlowForge', 52, 4.5, ['frontend', 'vue', 'react'], True),
    ('workflow_template', 'wf-backend-gen', '后端服务生成', 'FastAPI/Spring Boot服务自动生成', 'api-design', 'backend-gen', 'v1.0', 'FlowForge', 38, 4.4, ['backend', 'fastapi', 'spring'], True),
    ('workflow_template', 'wf-security-harden', '代码安全加固', '输入验证、SQL注入防护、XSS防护', 'security-scan', 'security-harden', 'v1.0', 'FlowForge', 57, 4.6, ['security', 'hardening'], True),
    ('workflow_template', 'wf-tech-debt-assess', '技术债评估', '代码腐化度量化、技术债报告生成', 'tech-debt', 'tech-debt-assess', 'v1.0', 'FlowForge', 14, 3.8, ['tech-debt', 'assessment'], True),
    ('workflow_template', 'wf-code-search', '代码搜索助手', '语义化代码检索,跨仓库依赖追踪', 'code-review', 'code-search', 'v1.0', 'FlowForge', 31, 4.2, ['search', 'semantic'], True),
    ('workflow_template', 'wf-contract-gen', '区块链合约生成', 'Solidity合约自动生成,ERC20/721模板', 'api-design', 'contract-gen', 'v1.0', 'FlowForge', 16, 4.3, ['blockchain', 'solidity', 'erc20'], True),
    ('workflow_template', 'wf-model-eval', 'AI模型评估', '模型性能评估,准确率/召回率/F1分析', 'performance', 'model-eval', 'v1.0', 'FlowForge', 23, 4.1, ['ai', 'evaluation', 'metrics'], True),
    ('workflow_template', 'wf-data-pipeline', '数据管道构建', 'ETL管道自动构建,数据质量检查', 'ci-cd', 'data-pipeline', 'v1.0', 'FlowForge', 11, 3.9, ['etl', 'data', 'pipeline'], True),
    ('workflow_template', 'wf-monitor-config', '监控告警配置', 'Prometheus/Grafana监控自动配置', 'ci-cd', 'monitor-config', 'v1.0', 'FlowForge', 17, 4.0, ['monitoring', 'prometheus'], True),
    ('workflow_template', 'wf-log-analysis', '日志分析助手', '日志模式识别,异常检测,根因定位', 'bug-diagnosis', 'log-analysis', 'v1.0', 'FlowForge', 24, 4.2, ['logs', 'anomaly'], True),
    ('workflow_template', 'wf-lint-config', '代码规范检查', 'ESLint/Prettier/Black自动配置', 'code-review', 'lint-config', 'v1.0', 'FlowForge', 89, 4.7, ['lint', 'eslint', 'prettier'], True),
]

now = datetime.now().isoformat()
for item in items:
    item_type, source_id, name, desc, category, scenario, version, publisher, dl_count, rating, tags, is_active = item
    item_id = f"market-{source_id}"
    c.execute("""INSERT OR REPLACE INTO marketplace_items 
        (id, item_type, source_id, name, description, category, scenario, version, publisher,
         content, download_count, rating, tags, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (item_id, item_type, source_id, name, desc, category, scenario, version, publisher,
         json.dumps({"description": desc}), dl_count, rating, json.dumps(tags), 1 if is_active else 0, now, now))

conn.commit()
print(f"Added {len(items)} marketplace items")

# 检查报告模板表
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='report_templates'")
if c.fetchone():
    c.execute("PRAGMA table_info(report_templates)")
    cols = [col[1] for col in c.fetchall()]
    print(f"report_templates columns: {cols}")
    c.execute("SELECT COUNT(*) FROM report_templates")
    print(f"Current report templates: {c.fetchone()[0]}")

# 检查审计日志表
for t in ['compliance_audit_logs', 'audit_logs', 'security_audit_logs']:
    c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{t}'")
    if c.fetchone():
        c.execute(f"PRAGMA table_info({t})")
        cols = [col[1] for col in c.fetchall()]
        c.execute(f"SELECT COUNT(*) FROM {t}")
        cnt = c.fetchone()[0]
        print(f"  {t}: {cnt} records, cols: {cols}")

# 检查评分数据
c.execute("SELECT e.id, e.workflow_id, COUNT(s.id) as score_count FROM executions e LEFT JOIN score_records s ON s.execution_id = e.id GROUP BY e.id ORDER BY e.started_at DESC LIMIT 5")
for row in c.fetchall():
    print(f"  exec {row[0][:20]}... wf={row[1][:20]}... scores={row[2]}")

conn.close()
print("Done!")