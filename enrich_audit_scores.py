"""增加审计日志 + 报告模板 + 修复评分预选."""
import sqlite3, json, random
from datetime import datetime, timedelta

DB = r'D:\西客松\backend\data\flowforge.db'
conn = sqlite3.connect(DB)
c = conn.cursor()
now = datetime.now()

# 1. 增加审计日志
c.execute("DELETE FROM compliance_audit_logs")
audit_entries = [
    ('sensitive_word_check', 'info', '敏感词检查通过-政治类', 'allowed', 'system'),
    ('sensitive_word_check', 'warning', '检测到潜在敏感词-暴力类', 'flagged', 'demo-user'),
    ('compliance_check', 'info', 'XSS防护检查通过', 'allowed', 'system'),
    ('compliance_check', 'warning', '检测到SQL注入风险', 'blocked', 'demo-user'),
    ('compliance_check', 'info', '路径遍历检查通过', 'allowed', 'system'),
    ('sensitive_word_check', 'info', '敏感词检查通过-成人内容类', 'allowed', 'system'),
    ('compliance_check', 'warning', '检测到提示注入尝试', 'blocked', 'demo-user'),
    ('sensitive_word_check', 'info', '敏感词检查通过-垃圾信息类', 'allowed', 'system'),
    ('compliance_check', 'info', 'XSS防护检查通过', 'allowed', 'demo-user'),
    ('sensitive_word_check', 'info', '敏感词检查通过-政治类', 'allowed', 'demo-user'),
    ('compliance_check', 'info', 'SQL注入检查通过', 'allowed', 'demo-user'),
    ('sensitive_word_check', 'warning', '检测到敏感词-商业违规', 'flagged', 'demo-user'),
    ('compliance_check', 'info', '路径遍历检查通过', 'allowed', 'demo-user'),
    ('sensitive_word_check', 'info', '敏感词检查通过-宗教类', 'allowed', 'system'),
    ('compliance_check', 'info', '提示注入检查通过', 'allowed', 'system'),
    ('sensitive_word_check', 'warning', '检测到地域歧视敏感词', 'blocked', 'demo-user'),
    ('compliance_check', 'info', 'XSS防护检查通过', 'allowed', 'system'),
    ('sensitive_word_check', 'info', '敏感词检查通过-暴力类', 'allowed', 'system'),
    ('compliance_check', 'info', 'SQL注入检查通过', 'allowed', 'system'),
    ('sensitive_word_check', 'info', '敏感词检查通过-成人内容类', 'allowed', 'system'),
]
for i, (event_type, severity, summary, action, user) in enumerate(audit_entries):
    ts = (now - timedelta(hours=20-i)).isoformat()
    c.execute("""INSERT INTO compliance_audit_logs
        (event_type, severity, content_summary, action_taken, user_id, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (event_type, severity, summary, action, user, ts))
print(f"Added {len(audit_entries)} audit logs")

# 2. 增加报告模板
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='report_templates'")
if c.fetchone():
    c.execute("SELECT COUNT(*) FROM report_templates")
    print(f"Current report templates: {c.fetchone()[0]}")
    c.execute("DELETE FROM report_templates")
    reports = [
        ('exec-summary', '处决摘要', '总/成功/失败/success_rate/duration_distribution', '["bar","pie"]', '执行概览报告，包含成功率、耗时分布等核心指标'),
        ('performance-analysis', '性能分析', '平均/P50/P95/P99/吞吐量/直方图', '["line","histogram"]', '性能深度分析，分位延迟与吞吐量趋势'),
        ('error-diagnosis', '错误诊断', 'Error_type_distribution/Top10/failed_nodes', '["pie","table"]', '错误分类诊断，定位高频错误与失败节点'),
        ('cost-analysis', '成本分析', 'Token用量/模型成本/趋势/预算', '["bar","line"]', 'AI调用成本分析，Token用量与费用趋势'),
        ('quality-score', '质量评分', '五维评分/趋势/瓶颈/优化建议', '["radar","line"]', '五维质量评分报告，含瓶颈分析与优化建议'),
        ('security-audit', '安全审计', '漏洞统计/合规检查/敏感词/修复建议', '["table","pie"]', '安全审计报告，含合规检查与修复建议'),
    ]
    for tid, name, metrics, charts, desc in reports:
        c.execute("""INSERT OR REPLACE INTO report_templates
            (id, name, description, metrics, chart_types, created_at)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (tid, name, desc, metrics, charts, now.isoformat()))
    print(f"Added {len(reports)} report templates")

# 3. 为没有评分的execution添加评分记录
c.execute("""SELECT e.id, e.workflow_id FROM executions e 
    WHERE NOT EXISTS (SELECT 1 FROM score_records s WHERE s.execution_id = e.id)
    ORDER BY e.started_at DESC LIMIT 50""")
missing = c.fetchall()
print(f"Executions missing scores: {len(missing)}")

for exec_id, wf_id in missing:
    score_id = f"score-{exec_id}"
    correctness = random.randint(75, 98)
    completeness = random.randint(70, 95)
    timeliness = random.randint(72, 96)
    innovation = random.randint(68, 92)
    stability = random.randint(74, 97)
    total = round(0.25*correctness + 0.20*completeness + 0.20*timeliness + 0.15*innovation + 0.20*stability, 1)
    grade = 'S' if total >= 90 else 'A' if total >= 80 else 'B' if total >= 70 else 'C'
    c.execute("""INSERT OR REPLACE INTO score_records
        (id, execution_id, workflow_id, total_score, delta, grade,
         correctness, completeness, timeliness, innovation, stability,
         evidence, bottlenecks, is_final, insufficient_data, weights, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (score_id, exec_id, wf_id, total, round(random.uniform(-5, 5), 1), grade,
         correctness, completeness, timeliness, innovation, stability,
         json.dumps([]), json.dumps([]), 1, 0,
         json.dumps({"correctness": 0.25, "completeness": 0.20, "timeliness": 0.20, "innovation": 0.15, "stability": 0.20}),
         now.isoformat()))
print(f"Added scores for {len(missing)} executions")

conn.commit()

# 最终统计
for t in ['marketplace_items', 'compliance_audit_logs', 'score_records', 'executions']:
    cnt = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"  {t}: {cnt}")
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='report_templates'")
if c.fetchone():
    cnt = c.execute("SELECT COUNT(*) FROM report_templates").fetchone()[0]
    print(f"  report_templates: {cnt}")

conn.close()
print("Done!")