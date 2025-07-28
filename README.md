# Polymarket 多币种自动交易系统

一个基于BTC、ETH、SOL价格触发的自动化Polymarket交易系统。

## 🚀 系统特性

### 多币种支持
- **BTC价格监控**: 支持比特币价格级别触发
- **ETH价格监控**: 支持以太坊价格级别触发  
- **SOL价格监控**: 支持Solana价格级别触发
- **独立触发机制**: 每个币种独立判断价格条件
- **统一交易执行**: 使用相同的交易模块

### 智能交易策略
- **累积投资公式**: 自动计算基于前期投资的最优投入金额
- **多级别配置**: 每个币种支持多个价格级别
- **立即执行**: Level 0在系统启动时立即执行
- **价格触发**: Level 1+等待相应币种价格信号

### 实时监控优化
- **每秒刷新**: 价格监控从30秒优化到1秒刷新
- **智能日志**: 每分钟记录价格状态，避免日志过多
- **交易日志**: 完整记录所有交易触发和执行信息

## 📦 项目结构

```
/root/poly/
├── multi_crypto_auto_trading_fixed.py    # 主交易系统（修正版）
├── setting_multi_crypto.json             # 多币种配置文件
├── start_multi_crypto_trading.sh         # 启动脚本
├── multi_crypto_trading_records.json     # 交易记录
├── multi_crypto_auto_trading.log         # 系统日志
├── check_price.py                        # 价格查询工具
├── market_buy_order.py                   # 买入订单工具
├── market_sell_order.py                  # 卖出订单工具
├── catchprice.py                         # 价格捕获工具
├── PRICE_MONITORING_UPDATES.md           # 价格监控优化说明
├── requirements.txt                      # Python依赖
├── venv_py3.12/                          # Python虚拟环境
├── py-clob-client/                       # Polymarket客户端
└── backup/                               # 备份文档
```

## ⚙️ 配置说明

### 多币种配置 (`setting_multi_crypto.json`)

```json
{
    "cryptocurrencies": {
        "BTC": {
            "symbol": "BTCUSDT",
            "levels": [
                {
                    "level": 0,
                    "tokenid": "your_btc_token_id",
                    "profit": 0,
                    "trigger_price": 0
                },
                {
                    "level": 1,
                    "tokenid": "your_btc_level1_token_id",
                    "profit": 6,
                    "trigger_price": 125000
                }
            ]
        },
        "ETH": {
            "symbol": "ETHUSDT", 
            "levels": [
                {
                    "level": 0,
                    "tokenid": "your_eth_token_id",
                    "profit": 0,
                    "trigger_price": 0
                },
                {
                    "level": 1,
                    "tokenid": "your_eth_level1_token_id",
                    "profit": 530,
                    "trigger_price": 3900
                }
            ]
        },
        "SOL": {
            "symbol": "SOLUSDT",
            "levels": [
                // SOL配置...
            ]
        }
    },
    "settings": {
        "price_check_interval": 1,     // 1秒刷新
        "max_retries": 3,
        "timeout": 10
    }
}
```

### 配置参数说明

- **level**: 价格级别 (0=立即执行, 1+=价格触发)
- **tokenid**: Polymarket代币ID
- **profit**: 目标利润 (美元)
- **trigger_price**: 触发价格 (美元，level 0设为0)

## 🚀 快速开始

### 1. 环境准备

```bash
# 激活虚拟环境
source venv_py3.12/bin/activate

# 检查依赖
pip install -r requirements.txt
```

### 2. 配置设置

```bash
# 编辑多币种配置
nano setting_multi_crypto.json

# 设置环境变量 (API密钥等)
nano .env
```

### 3. 启动系统

```bash
# 使用启动脚本
./start_multi_crypto_trading.sh

# 或直接运行
python multi_crypto_auto_trading_fixed.py
```

## 🔧 工具使用

### 价格查询
```bash
# 查询特定token价格
python check_price.py <token_id>
```

### 手动交易
```bash
# 买入订单
python market_buy_order.py <token_id> <amount>

# 卖出订单  
python market_sell_order.py <token_id> <amount>
```

### 价格监控
```bash
# 实时价格捕获
python catchprice.py
```

## 📊 监控功能

### 实时监控
- **BTC价格监控**: 触发Level 1+交易
- **ETH价格监控**: 触发Level 1+交易
- **SOL价格监控**: 触发Level 1+交易
- **实时价格更新**: 每秒刷新，每分钟记录日志
- **独立交易记录**: 按币种分类记录

### 日志分析
```bash
# 查看实时日志
tail -f multi_crypto_auto_trading.log

# 查看交易记录
cat multi_crypto_trading_records.json
```

## 💰 投资策略

### 累积投资公式
系统使用修正的累积投资公式：

```
Level 0: amount = profit / (1/price - 1)
Level 1+: amount = (profit + previous_total) / (1/price - 1)
```

### 多币种独立执行
- 每个币种独立监控价格
- 独立计算投资金额
- 独立记录交易历史
- 统一的交易执行引擎

## ⚠️ 重要提醒

1. **真实交易系统**: 请确保配置正确
2. **Level 0立即执行**: 系统启动后立即执行所有币种的Level 0
3. **价格触发**: Level 1+等待相应币种价格信号
4. **小额测试**: 建议先进行小额测试
5. **实时监控**: 系统每秒检查价格变化
6. **紧急停止**: 按Ctrl+C可随时停止

## 📈 性能优化

### 价格监控优化
- **刷新频率**: 从30秒优化到1秒
- **日志优化**: 价格监控日志每分钟记录
- **交易日志**: 保持详细的交易信息记录

详细优化信息请查看: [PRICE_MONITORING_UPDATES.md](PRICE_MONITORING_UPDATES.md)

## 🔍 Token ID获取

如需查找特定市场的Token ID，请参考：

1. **浏览器开发者工具**
   - 访问 polymarket.com
   - F12 → Network → 查找 `clob.polymarket.com/book?token_id=` 请求

2. **使用查询工具**
   ```bash
   python check_price.py <token_id>  # 验证token有效性
   ```

## 📞 支持

如遇问题，请检查：
1. 配置文件语法是否正确
2. Token ID是否有效
3. 网络连接是否正常
4. API密钥是否配置

## 📚 备份文档

`backup/` 目录包含：
- 历史文档和说明
- 旧版本的配置示例
- 系统演进的参考资料 