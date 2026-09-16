---
slug: strong-stock-screener-7400cfba
displayName: A股强势股抓取
name: strong-stock-screener
version: 1.0.0
summary: 基于多维度量化指标从A股全市场筛选强势股票，支持量价异动、技术形态、资金流向等维度
description: >
  A股强势股抓取工具。基于东方财富免费数据，从涨幅动量、量能配合、技术形态、
  换手活跃度、板块强度五个维度综合评分，快速筛选市场中最强势的个股。
  支持全市场扫描、板块筛选、自定义参数、N日新高等多种模式。
  当用户提到"强势股""抓涨停""牛股筛选""量价异动""放量突破""新高股"
  "强势板块""热门股""资金流入""换手活跃""技术选股""量化选股"时使用。
license: MIT
metadata:
  author: user_7400cfba
  tags:
    - stock
    - screener
    - quantitative
    - a-share
    - momentum
---

# A股强势股抓取工具 v1.0

> 数据来源：东方财富免费接口（无需 API Key），仅供参考，不构成投资建议。

## 免责声明

本工具仅供学习研究参考，不构成任何投资建议。股市有风险，投资需谨慎。
数据来源于第三方接口，存在延迟和误差，请以交易所实时数据为准。

## 核心原则

1. **数据驱动**：所有判断基于量化指标，不做主观臆断
2. **多维评分**：单一指标容易误导，综合评分更可靠
3. **透明可复现**：每个维度的计算逻辑公开，结果可验证
4. **风险提示**：强势不等于必涨，必须配合免责声明输出

## 能力路由

| 用户意图 | 工作流 | 依赖资源 |
|---------|--------|----------|
| 全市场扫描强势股 | -> 工作流 A | scripts/strong_stock_screener.py |
| 筛选N日新高个股 | -> 工作流 B | scripts/strong_stock_screener.py --new-high |
| 查看板块强势排名 | -> 工作流 C | scripts/strong_stock_screener.py --sector |
| 自定义筛选条件 | -> 工作流 D | scripts/strong_stock_screener.py --custom |
| 了解指标含义 | -> 参考文档 | references/indicators-guide.md |

## 工作流 A：全市场强势股扫描

### 触发条件
用户要求"找强势股""今天哪些股票最强""帮我筛选强势股"等

### 执行步骤

```bash
# 基础扫描：默认取 Top 30
python scripts/strong_stock_screener.py

# 指定数量 + JSON 输出
python scripts/strong_stock_screener.py --top 50 --json

# 排除 ST / 科创板 / 北交所
python scripts/strong_stock_screener.py --no-st --no-kcb --no-bse
```

### 评分维度（各 20 分，满分 100）

| 维度 | 指标 | 说明 |
|------|------|------|
| 涨幅动量 | 日涨幅 | 短期趋势强度 |
| 量能配合 | 量比 | 放量上涨优于缩量上涨 |
| 换手活跃度 | 换手率 | 适度活跃最优，过高警惕 |
| 技术形态 | 日内强势度 | 收盘在高位得分高 |
| 资金流向 | 主力净流入占比 | 大单净流入方向 |

### 输出格式

```
排名 | 代码   | 名称     | 涨幅%  | 量比  | 换手%  | 评分
 1   | 600xxx | XX股份   |  8.52  | 3.21  |  12.3  | 92.5
 2   | 000xxx | XX科技   |  6.71  | 2.85  |   9.8  | 88.3
```

## 工作流 B：N日新高筛选

### 触发条件
用户要求"找创新高的股票""N日新高""突破前高"等

```bash
python scripts/strong_stock_screener.py --new-high --days 20
python scripts/strong_stock_screener.py --new-high --days 60
```

## 工作流 C：板块强势排名

### 触发条件
用户要求"哪个板块最强""板块排名""行业强度"等

```bash
# 行业板块强势排名
python scripts/strong_stock_screener.py --sector

# 概念板块强势排名
python scripts/strong_stock_screener.py --sector --type concept
```

## 工作流 D：自定义筛选

### 触发条件
用户提出具体筛选条件组合

```bash
# 自定义：涨幅>3% + 量比>2 + 换手>5%
python scripts/strong_stock_screener.py --custom --min-change 3 --min-volume-ratio 2 --min-turnover 5

# 指定市场
python scripts/strong_stock_screener.py --market sh
python scripts/strong_stock_screener.py --market gem
```

## 交互规范

1. **先确认需求**：问清楚用户要全市场扫描还是特定条件筛选
2. **执行脚本**：用 scripts/strong_stock_screener.py 执行，不要让 AI 心算
3. **解读结果**：对 Top 结果做简要分析，说明强势原因
4. **风险提示**：每次输出结果后附加免责声明
5. **JSON 模式**：需要程序化处理时使用 --json

## 运行环境要求

- Python 3.6+（纯标准库，零 pip 依赖）
- 需要网络连接（调用东方财富数据接口）
- 国内直连（数据源为国内接口，代理可能导致失败）
