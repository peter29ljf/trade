# 🚀 Polymarket 多币种自动交易系统

一个基于Python的智能加密货币交易系统，支持BTC、ETH、SOL的实时价格监控和自动交易。

## ✨ 核心特性

### 🎯 多币种支持
- **Bitcoin (BTC)** - 比特币价格监控和交易
- **Ethereum (ETH)** - 以太坊价格监控和交易  
- **Solana (SOL)** - Solana价格监控和交易

### 📊 智能交易策略
- **分层投资策略** - 基于价格级别的自动投资
- **风险管理** - 智能仓位控制和止损机制
- **累积投资公式** - 优化的资金分配算法

### ⚡ 实时监控
- **每秒价格更新** - 使用Coinbase API实时获取价格
- **详细日志记录** - 完整的交易和价格记录
- **Screen会话管理** - 后台稳定运行

### 🛡️ 稳定性保障
- **API容错机制** - 多重API备选方案
- **自动日志清理** - 防止日志文件过大
- **异常恢复** - 自动处理网络和API错误

## 🔧 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    多币种交易系统                              │
├─────────────────────────────────────────────────────────────┤
│  📊 价格监控模块     │  🎯 交易执行模块     │  📝 日志管理模块   │
│  • 实时价格获取      │  • 智能订单执行      │  • 详细记录        │
│  • 多API支持        │  • 风险控制         │  • 自动清理        │
│  • 并发处理         │  • 分层策略         │  • 状态监控        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     外部API集成                             │
├─────────────────────────────────────────────────────────────┤
│  🏦 Coinbase API    │  📈 Polymarket API  │  🔄 备用API源     │
│  • 实时价格数据      │  • 交易执行         │  • 容错机制       │
│  • 无地区限制       │  • 市场数据         │  • 自动切换       │
└─────────────────────────────────────────────────────────────┘
```

## 📦 安装和配置

### 1. 环境要求
```bash
Python 3.12+
Virtual Environment
GNU Screen (用于后台运行)
```

### 2. 依赖安装
```bash
# 创建虚拟环境
python3.12 -m venv venv_py3.12
source venv_py3.12/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置文件设置
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
nano setting_multi_crypto.json
```

### 4. API密钥配置
在 `.env` 文件中配置你的API密钥：
```env
# Polymarket API配置
POLYMARKET_API_KEY=your_api_key_here
POLYMARKET_SECRET=your_secret_here
POLYMARKET_PASSPHRASE=your_passphrase_here
```

## 🚀 快速启动

### 方法1: 使用启动脚本
```bash
./start_multi_crypto_trading.sh
```

### 方法2: 手动启动
```bash
# 启动Screen会话
screen -S multi_crypto_trading

# 激活虚拟环境
source venv_py3.12/bin/activate

# 启动系统
python multi_crypto_auto_trading_fixed.py
```

### 方法3: 后台运行
```bash
# 在Screen中启动
screen -S multi_crypto_trading -dm bash -c "cd /root/poly && source venv_py3.12/bin/activate && python multi_crypto_auto_trading_fixed.py"
```

## 📊 系统监控

### 实时日志查看
```bash
# 观察价格更新
tail -f multi_crypto_auto_trading.log | grep "价格监控"

# 查看交易活动
tail -f multi_crypto_auto_trading.log | grep "交易"

# 查看系统状态
tail -f multi_crypto_auto_trading.log | grep "系统"
```

### Screen会话管理
```bash
# 连接到运行中的会话
screen -r multi_crypto_trading

# 分离会话 (在screen中)
Ctrl+A, D

# 停止系统 (在screen中)
Ctrl+C
```

## ⚙️ 配置说明

### 主配置文件: `setting_multi_crypto.json`
```json
{
  "BTC": {
    "levels": [
      {"price": 111900, "target_profit": 0, "token_id": "your_btc_token_id"},
      {"price": 115000, "target_profit": 50, "token_id": "your_btc_token_id"}
    ]
  },
  "ETH": {
    "levels": [
      {"price": 3700, "target_profit": 0, "token_id": "your_eth_token_id"}
    ]
  },
  "SOL": {
    "levels": [
      {"price": 183, "target_profit": 0, "token_id": "your_sol_token_id"}
    ]
  },
  "price_check_interval": 1,
  "max_investment_per_level": 100
}
```

### 关键参数说明
- `price`: 触发价格阈值
- `target_profit`: 目标利润金额 (美元)
- `token_id`: Polymarket代币ID
- `price_check_interval`: 价格检查间隔 (秒)
- `max_investment_per_level`: 每级最大投资额

## 📈 交易策略

### 分层投资策略
系统采用智能分层投资策略：

1. **Level 0**: 基础投资 ($1 USDC)
2. **Level 1+**: 基于累积公式的增量投资

### 投资计算公式
```python
当前投资 = 目标总额 - 之前总投资
目标总额 = 目标利润 / (1 - Token价格)
```

### 风险控制
- 每级最大投资限额
- 自动止损机制
- 实时风险评估

## 📝 文件结构

```
poly/
├── multi_crypto_auto_trading_fixed.py  # 主程序
├── setting_multi_crypto.json           # 配置文件
├── start_multi_crypto_trading.sh       # 启动脚本
├── check_price.py                      # 价格检查工具
├── market_buy_order.py                 # 买入订单模块
├── market_sell_order.py                # 卖出订单模块
├── catchprice.py                       # 价格抓取工具
├── requirements.txt                    # Python依赖
├── README.md                           # 项目说明
├── .env                               # 环境变量
├── .gitignore                         # Git忽略文件
└── docs/                              # 文档目录
    ├── API_OPTIMIZATION_UPDATE.md      # API优化记录
    ├── PROJECT_CLEANUP_SUMMARY.md      # 项目清理总结
    ├── REALTIME_LOGGING_UPDATE.md      # 实时日志更新
    └── SCREEN_USAGE_GUIDE.md          # Screen使用指南
```

## 🔄 API优化历程

系统经历了多次API优化以确保稳定性：

1. **CoinGecko API** → 429错误 (请求频率限制)
2. **Binance API** → 451错误 (地区限制)  
3. **Coinbase API** → ✅ 稳定运行 (无地区限制)

## 📊 性能特性

- **响应速度**: < 2秒价格更新
- **API调用**: 每秒3个并发请求
- **内存使用**: ~37MB
- **日志频率**: 每秒记录价格信息
- **稳定性**: 24/7 连续运行能力

## 🛠️ 故障排除

### 常见问题

1. **API连接失败**
   ```bash
   # 检查网络连接
   curl -s "https://api.coinbase.com/v2/exchange-rates?currency=BTC"
   ```

2. **虚拟环境问题**
   ```bash
   # 重新创建虚拟环境
   rm -rf venv_py3.12
   python3.12 -m venv venv_py3.12
   source venv_py3.12/bin/activate
   pip install -r requirements.txt
   ```

3. **Screen会话问题**
   ```bash
   # 查看所有screen会话
   screen -ls
   
   # 终止僵死会话
   screen -S session_name -X quit
   ```

## 📚 更多文档

- [API优化记录](docs/API_OPTIMIZATION_UPDATE.md)
- [实时日志更新](docs/REALTIME_LOGGING_UPDATE.md)  
- [Screen使用指南](docs/SCREEN_USAGE_GUIDE.md)
- [项目清理总结](docs/PROJECT_CLEANUP_SUMMARY.md)

## ⚠️ 免责声明

本软件仅供教育和研究目的使用。加密货币交易存在高风险，请谨慎投资，并仅投资您能够承受损失的金额。作者不对任何投资损失承担责任。

## 📄 许可证

MIT License - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🤝 贡献

欢迎提交 Issues 和 Pull Requests！

---

⭐ 如果这个项目对您有帮助，请给它一个星标！ 