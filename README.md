# A股强势股抓取工具

基于多维度量化指标从A股全市场筛选强势股票。

## 功能特性

- 全市场强势股扫描（五维评分：涨幅动量/量能配合/换手活跃度/技术形态/资金流向）
- N日新高个股筛选（开发中）
- 板块强势排名（行业/概念）
- 自定义条件筛选

## 快速开始

```bash
python scripts/strong_stock_screener.py                        # 全市场扫描 Top 30
python scripts/strong_stock_screener.py --top 50 --json        # Top 50 JSON 输出
python scripts/strong_stock_screener.py --sector               # 行业板块排名
python scripts/strong_stock_screener.py --sector --type concept # 概念板块排名
python scripts/strong_stock_screener.py --custom --min-change 3 --min-volume-ratio 2
```

## 运行要求

- Python 3.6+（纯标准库，零依赖）
- 需要网络连接（东方财富数据接口）
- 国内直连（代理可能导致失败）

## 免责声明

本工具仅供学习研究，不构成投资建议。
