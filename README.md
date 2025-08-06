# Polymarket 多币种自动交易系统 v2.1

一个基于BTC、ETH、SOL价格触发的自动化Polymarket交易系统，支持实时监控、智能投资策略和webhook通知。

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
- **自动日志清理**: 每小时自动清理日志文件，保留重要信息

### 系统稳定性
- **API限制处理**: 解决429/451错误，自动重试机制
- **错误恢复**: 网络异常自动重连
- **webhook通知**: 集成外部通知系统
- **配置热更新**: 支持运行时配置调整

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
├── generate_env.py                       # 环境变量生成工具
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
    "webhook": "http://205.198.88.142:5002/webhook",
    "cryptocurrencies": {
        "BTC": {
            "symbol": "BTCUSDT",
            "levels": [
                {
                    "level": 0,
                    "tokenid": "75548853773826042938037269403961620968895595455588421031754896226233782822511",
                    "profit": 500,
                    "trigger_price": 0
                },
                {
                    "level": 1,
                    "tokenid": "59927336947705179086643351156863294391159498317821945309659158441498874763255",
                    "profit": 2500,
                    "trigger_price": 116900
                },
                {
                    "level": 2,
                    "tokenid": "106480746132572789966336636468021047738054338780537897234069209863392176627209",
                    "profit": 2500,
                    "trigger_price": 119900
                }
            ]
        },
        "ETH": {
            "symbol": "ETHUSDT", 
            "levels": [
                {
                    "level": 0,
                    "tokenid": "105791433475323333629828730054141182108160839660710998828282462799800527904171",
                    "profit": 0,
                    "trigger_price": 0
                },
                {
                    "level": 1,
                    "tokenid": "67239982686669653395417056430548630433746454326537117349191453387395681002890",
                    "profit": 0,
                    "trigger_price": 4000
                },
                {
                    "level": 2,
                    "tokenid": "64909678168877653527079423463285253591168081473039735614680342725105856605418",
                    "profit": 0,
                    "trigger_price": 4200
                }
            ]
        },
        "SOL": {
            "symbol": "SOLUSDT",
            "levels": [
                {
                    "level": 0,
                    "tokenid": "30962849301395034865691297877166366190057226558979258784219057690978861378316",
                    "profit": 0,
                    "trigger_price": 0
                },
                {
                    "level": 1,
                    "tokenid": "33039082675389444678548505109797392589580419211438503001664746644922565319121",
                    "profit": 0,
                    "trigger_price": 210
                },
                {
                    "level": 2,
                    "tokenid": "28486276220133254885492384356574149099253843153294121025024787140615897724466",
                    "profit": 0,
                    "trigger_price": 220
                }
            ]
        }
    },
    "settings": {
        "price_check_interval": 1,
        "max_retries": 3,
        "timeout": 10
    }
}
```

### 配置参数说明

- **webhook**: 外部通知系统URL
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

# 生成环境变量
python generate_env.py
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

### 环境配置
```bash
# 生成环境变量模板
python generate_env.py
```

## 📊 监控功能

### 实时监控
- **BTC价格监控**: 触发Level 1+交易
- **ETH价格监控**: 触发Level 1+交易
- **SOL价格监控**: 触发Level 1+交易
- **实时价格更新**: 每秒刷新，每分钟记录日志
- **独立交易记录**: 按币种分类记录
- **webhook通知**: 交易事件实时通知

### 日志分析
```bash
# 查看实时日志
tail -f multi_crypto_auto_trading.log

# 查看交易记录
cat multi_crypto_trading_records.json

# 查看日志清理状态
grep "日志清理" multi_crypto_auto_trading.log
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

## 🔄 系统优化

### v2.1 最新更新
- **自动日志清理**: 每小时自动清理日志文件，保留重要信息
- **webhook集成**: 支持外部通知系统
- **API限制处理**: 优化429/451错误处理
- **配置热更新**: 支持运行时配置调整
- **环境变量工具**: 新增环境配置生成工具

### 性能优化
- **刷新频率**: 从30秒优化到1秒
- **日志优化**: 价格监控日志每分钟记录
- **交易日志**: 保持详细的交易信息记录
- **内存管理**: 自动清理过期日志数据

详细优化信息请查看: [PRICE_MONITORING_UPDATES.md](PRICE_MONITORING_UPDATES.md)

## ⚠️ 重要提醒

1. **真实交易系统**: 请确保配置正确
2. **Level 0立即执行**: 系统启动后立即执行所有币种的Level 0
3. **价格触发**: Level 1+等待相应币种价格信号
4. **小额测试**: 建议先进行小额测试
5. **实时监控**: 系统每秒检查价格变化
6. **紧急停止**: 按Ctrl+C可随时停止
7. **日志管理**: 系统自动清理日志，无需手动维护

## 📈 系统状态

### 当前运行状态
- **系统版本**: v2.1 (修正版)
- **支持币种**: BTC, ETH, SOL
- **监控频率**: 1秒/次
- **日志清理**: 每小时自动清理
- **webhook通知**: 已集成

### 最新交易记录
系统已成功执行多次交易，包括：
- BTC Level 0-2 交易
- ETH Level 0-2 交易  
- SOL Level 0-2 交易

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
5. webhook URL是否可访问

## 📚 备份文档

`backup/` 目录包含：
- 历史文档和说明
- 旧版本的配置示例
- 系统演进的参考资料

## 🆕 更新日志

### v2.1 (2025-08-06)
- ✅ 添加自动日志清理功能
- ✅ 集成webhook通知系统
- ✅ 优化API限制处理
- ✅ 新增环境变量生成工具
- ✅ 改进错误恢复机制

### v2.0 (2025-07-28)
- ✅ 修正投资公式
- ✅ 优化价格监控频率
- ✅ 添加多币种支持
- ✅ 实现智能日志管理 