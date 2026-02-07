# 黄金交易分析系统

## 项目概述

这是一个专业的黄金交易分析系统，集成了技术指标分析、AI驱动的市场分析和实时交易信号推送功能。系统采用现代化的暗色主题设计，提供直观的数据可视化和智能交易建议。

## 核心功能

### 1. 实时数据监控
- **实时黄金价格**：自动获取黄金现货价格（USD/盎司）
- **价格走势图**：7天历史价格趋势可视化
- **自动刷新**：每30秒自动更新数据
- **价格变化追踪**：显示价格变化和百分比

### 2. 技术指标分析
系统集成了多种专业技术指标：

- **RSI（相对强弱指数）**：14周期RSI，识别超买超卖状态
- **MACD（移动平均收敛散度）**：捕捉价格动量变化
- **布林带（Bollinger Bands）**：20周期布林带，识别价格波动范围
- **ATR（平均真实波幅）**：评估市场波动性
- **随机震荡指标（Stochastic）**：短期超买超卖信号
- **移动平均线（MA）**：SMA20、SMA50、EMA20

每个指标都提供：
- 实时数值
- 买卖信号（BUY/SELL/HOLD）
- 信心度评分（0-100%）

### 3. AI驱动分析

使用OpenAI GPT-5.2进行智能市场分析：

#### 新闻情绪分析
- 分析近期金融市场新闻
- 评估新闻对黄金价格的影响
- 提供看涨/看跌/中性的情绪判断

#### K线图形态识别
- AI识别图表形态（头肩顶、双底、三角形等）
- 提供基于形态的交易信号
- 形态置信度评估

#### 市场情绪分析
- 综合考虑VIX恐慌指数
- 美元指数走势
- 避险情绪
- 社交媒体舆论

### 4. 综合交易信号

系统整合所有技术指标和AI分析，生成综合交易信号：

- **信号类型**：买涨/买跌/观望
- **信心度**：综合评分（0-100%）
- **详细建议**：基于信号强度的交易建议
- **信号历史**：保存所有历史信号供复盘分析

### 5. 通知设置

- **邮件通知**：配置接收交易信号的邮箱
- **信号阈值**：设置触发通知的信心度阈值（50-100%）
- **开关控制**：灵活启用/禁用通知功能

## 技术架构

### 后端
- **框架**：FastAPI
- **数据库**：MongoDB
- **AI集成**：Emergent LLM（支持OpenAI GPT-5.2）
- **数据分析**：Pandas, NumPy
- **技术指标**：自定义技术分析引擎

### 前端
- **框架**：React 19
- **UI库**：Shadcn/UI + Tailwind CSS
- **图表**：Recharts
- **动画**：Framer Motion
- **路由**：React Router v7

### 设计风格
- **主题**：暗色专业金融主题
- **主色调**：金色（#D4AF37）
- **字体**：
  - 标题：Barlow Condensed
  - 正文：Manrope
  - 数据：JetBrains Mono

## API端点

### 价格相关
- `GET /api/price/current` - 获取实时黄金价格
- `GET /api/price/history?days=30` - 获取历史价格数据

### 分析相关
- `GET /api/analysis/technical` - 获取技术指标分析
- `GET /api/analysis/ai` - 获取AI分析结果

### 信号相关
- `GET /api/signals/current` - 获取当前交易信号
- `GET /api/signals/history?limit=50` - 获取历史信号

### 设置相关
- `POST /api/settings` - 保存用户设置
- `GET /api/settings/{email}` - 获取用户设置

### 仪表盘
- `GET /api/dashboard/summary` - 获取仪表盘概览数据

## 数据流程

1. **数据获取**：从Kitco网站爬取实时黄金价格（当前为模拟数据）
2. **技术分析**：基于历史数据计算各项技术指标
3. **AI分析**：使用LLM分析市场新闻、图表形态和整体情绪
4. **信号生成**：综合所有指标和AI分析结果，生成交易信号
5. **数据存储**：所有价格、指标、信号数据存储到MongoDB
6. **实时展示**：前端定时刷新显示最新数据

## 环境变量

### 后端 (.env)
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=test_database
CORS_ORIGINS=*
EMERGENT_LLM_KEY=sk-emergent-xxx
```

### 前端 (.env)
```
REACT_APP_BACKEND_URL=your-backend-url
```

## 部署说明

系统使用Supervisor管理服务：

```bash
# 重启服务
sudo supervisorctl restart backend frontend

# 查看状态
sudo supervisorctl status

# 查看日志
tail -f /var/log/supervisor/backend.out.log
tail -f /var/log/supervisor/frontend.out.log
```

## 未来扩展方向

### 已规划功能
1. **MT5集成**：连接MT5交易平台实现自动交易
2. **真实数据源**：集成Alpha Vantage等API获取真实市场数据
3. **资金流分析**：添加基于实时资金流的分析方法
4. **更多通知方式**：支持短信、Telegram等多种通知渠道
5. **策略回测**：历史数据回测和策略优化
6. **多币种支持**：扩展到其他贵金属和货币对

### 数据增强
- 集成真实新闻API（Reuters、Bloomberg）
- 实时K线图生成和AI分析
- 社交媒体情绪实时抓取
- 宏观经济数据集成

## 安全与免责声明

⚠️ **重要提示**：
- 本系统提供的分析和信号仅供参考，不构成投资建议
- 投资有风险，入市需谨慎
- 请勿盲目跟随交易信号进行实盘操作
- AI分析结果可能存在误差，需结合实际情况判断
- 建议在模拟环境中充分测试后再考虑实盘应用

## 许可证

本项目由Emergent Labs提供技术支持。

---

**Powered by AI** | **Made with Emergent**
