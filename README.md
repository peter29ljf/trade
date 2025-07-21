# 🤖 Polymarket 自动交易系统

一个基于BTC价格触发的Polymarket自动交易系统，支持多级别交易策略和累积投资模式。

## 📋 目录

- [功能特性](#功能特性)
- [系统架构](#系统架构)
- [安装指南](#安装指南)
- [配置说明](#配置说明)
- [使用方法](#使用方法)
- [交易策略](#交易策略)
- [安全提醒](#安全提醒)
- [故障排除](#故障排除)
- [贡献指南](#贡献指南)

## ✨ 功能特性

- 🎯 **多级别交易策略**: 基于BTC价格设定多个交易触发点
- 📊 **实时价格监控**: 持续监控BTC价格变化
- 💰 **累积投资模式**: 根据数学公式计算最优投资金额
- 🔄 **自动交易执行**: 触发条件满足时自动执行交易
- 📝 **详细日志记录**: 完整的交易记录和系统日志
- 🛡️ **安全机制**: 多重安全检查和错误处理
- 🎛️ **灵活配置**: JSON配置文件，易于调整参数

## 🏗️ 系统架构

```
简化版自动交易系统
├── 价格监控模块 (SimplifiedBTCMonitor)
├── 交易执行模块 (market_buy_order.py)
├── 价格检查模块 (check_price.py)
└── 配置管理模块 (setting.json)
```

**核心组件:**
- `simplified_auto_trading.py` - 主控制系统
- `market_buy_order.py` - 交易执行器
- `market_sell_order.py` - 卖出执行器
- `check_price.py` - 价格查询器
- `start_simplified_trading.sh` - 启动脚本

## 🚀 安装指南

### 环境要求

- Python 3.12+
- Linux/Unix 系统
- 网络连接

### 1. 克隆项目

```bash
git clone <repository-url>
cd polymarket-auto-trading
```

### 2. 创建虚拟环境

```bash
python3.12 -m venv venv_py3.12
source venv_py3.12/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

创建 `.env` 文件并配置以下参数：

```bash
# Polymarket API配置
POLYMARKET_API_KEY=your_api_key
POLYMARKET_SECRET=your_secret
POLYMARKET_PASSPHRASE=your_passphrase

# 代理设置 (可选)
HTTP_PROXY=your_proxy_if_needed
HTTPS_PROXY=your_proxy_if_needed
```

## ⚙️ 配置说明

### setting.json 配置文件

```json
{
    "webhook": "http://your-server:port/webhook",
    "levels": [
        {
            "level": 0,
            "tokenid": "token_id_for_immediate_trade",
            "profit": 5,
            "btcprice": 0
        },
        {
            "level": 1,
            "tokenid": "token_id_for_125k_btc",
            "profit": 6,
            "btcprice": 125000
        },
        {
            "level": 2,
            "tokenid": "token_id_for_130k_btc",
            "profit": 7,
            "btcprice": 130000
        }
    ]
}
```

**参数说明:**
- `level`: 交易级别 (0为立即执行，1+为价格触发)
- `tokenid`: Polymarket代币ID
- `profit`: 目标利润金额 (USDC)
- `btcprice`: BTC触发价格 (0表示立即执行)

### plan.md 交易计划

详细说明了各级别的交易策略和计算公式：
- Level 0: 启动时立即执行
- Level 1+: 等待BTC价格达到触发点

## 🎮 使用方法

### 快速启动

```bash
# 给启动脚本执行权限
chmod +x start_simplified_trading.sh

# 启动系统
./start_simplified_trading.sh
```

### 手动启动

```bash
# 激活虚拟环境
source venv_py3.12/bin/activate

# 直接运行
python simplified_auto_trading.py
```

### 后台运行

```bash
# 使用screen后台运行
screen -S trading
./start_simplified_trading.sh
# Ctrl+A+D 分离会话

# 重新连接
screen -r trading
```

## 📈 交易策略

### 累积投资公式

系统使用以下公式计算每级别的投资金额：

```
amount = (profit + previous_amount) / (1/price - 1)
```

其中：
- `profit`: 当前级别目标利润
- `previous_amount`: 之前级别投资总额
- `price`: 当前代币价格

### 触发机制

1. **Level 0**: 系统启动后立即执行
2. **Level 1+**: 监控BTC价格，达到设定价格时触发
3. **价格检查**: 每30秒检查一次BTC价格
4. **交易执行**: 满足条件时自动计算并执行交易

## 🔒 安全提醒

⚠️ **重要安全提示:**

- 这是真实交易系统，涉及实际资金
- 开始前请进行小额测试
- 确保API密钥安全
- 定期检查交易记录
- 保持足够的USDC余额
- 建议设置合理的止损机制

## 📊 监控和日志

### 日志文件

- `auto_trading.log` - 系统运行日志
- `auto_trading_records.json` - 交易记录

### 实时监控

```bash
# 查看实时日志
tail -f auto_trading.log

# 检查交易记录
cat auto_trading_records.json | jq .
```

## 🛠️ 故障排除

### 常见问题

**1. 虚拟环境未找到**
```bash
python3.12 -m venv venv_py3.12
source venv_py3.12/bin/activate
```

**2. 依赖安装失败**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**3. API连接失败**
- 检查`.env`文件配置
- 验证API密钥有效性
- 检查网络连接

**4. 价格获取失败**
- 检查price API端点
- 验证代理设置
- 检查防火墙配置

### 调试模式

```bash
# 开启详细日志
export PYTHONPATH=.
python simplified_auto_trading.py --debug
```

## 📁 项目结构

```
polymarket-auto-trading/
├── README.md                    # 项目说明
├── requirements.txt             # 依赖包
├── setting.json                 # 配置文件
├── plan.md                      # 交易计划
├── .env                         # 环境变量
├── start_simplified_trading.sh  # 启动脚本
├── simplified_auto_trading.py   # 主程序
├── market_buy_order.py          # 买入模块
├── market_sell_order.py         # 卖出模块
├── check_price.py               # 价格查询
├── py-clob-client/              # Polymarket客户端
├── venv_py3.12/                 # Python虚拟环境
├── auto_trading.log             # 运行日志
├── auto_trading_records.json    # 交易记录
└── backup/                      # 备份文件
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目仅供学习和研究使用。使用时请遵守相关法律法规和平台条款。

## ⚠️ 免责声明

- 本软件仅供教育和研究目的
- 使用本软件进行实际交易的风险由用户自行承担
- 开发者不对任何交易损失负责
- 请在充分了解风险的情况下使用

---

**联系方式**: 如有问题或建议，请提交Issue或Pull Request。

**最后更新**: 2024年7月 