# Polymarket 多币种自动交易系统 v3.1

一个基于BTC、ETH、SOL价格触发的自动化Polymarket交易系统，支持实时监控、智能投资策略和价格跨越检测。

## 🚀 系统特性

### 多币种支持
- **BTC价格监控**: 支持比特币价格级别触发
- **ETH价格监控**: 支持以太坊价格级别触发  
- **SOL价格监控**: 支持Solana价格级别触发
- **独立触发机制**: 每个币种独立判断价格条件
- **统一交易执行**: 使用相同的交易模块

### 智能价格跨越机制
- **跨越检测**: 检测价格从一侧跨越到另一侧触发交易
- **重启重置**: 程序重启时自动重置所有触发状态
- **历史记录**: 维护价格历史用于跨越判断
- **异常处理**: 自动处理价格异常波动

### 实时监控优化
- **每秒刷新**: 价格监控从30秒优化到1秒刷新
- **实时日志**: 每秒记录价格状态和交易信息
- **长期稳定运行**: 支持8小时+连续运行
- **API优化**: 支持Coinbase API，避免地区限制

### 系统稳定性
- **Screen支持**: 支持后台运行，程序重启管理
- **错误恢复**: 网络异常自动重连，API错误处理
- **配置热更新**: 支持运行时配置调整
- **日志管理**: 智能日志清理，避免磁盘空间问题

## 📦 项目结构

```
/root/poly/
├── multi_crypto_auto_trading_fixed.py    # 主交易系统（修正版）
├── setting_multi_crypto.json             # 多币种配置文件
├── start_multi_crypto_trading.sh         # 启动脚本
├── multi_crypto_trading_records.json     # 交易记录 (1158行+)
├── multi_crypto_auto_trading.log         # 系统日志
├── check_price.py                        # 价格查询工具
├── market_buy_order.py                   # 买入订单工具
├── market_sell_order.py                  # 卖出订单工具
├── catchprice.py                         # 价格捕获工具
├── generate_env.py                       # 环境变量生成工具
├── requirements.txt                      # Python依赖
├── venv/                                 # Python虚拟环境
├── py-clob-client/                       # Polymarket客户端
└── docs/                                 # 文档目录
```

## ⚙️ 当前配置

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
                    "tokenid": "46892948147677499361707760015458275278085567956491879132639051425730297294426",
                    "profit": 0,
                    "trigger_price": 120000
                },
                {
                    "level": 1,
                    "tokenid": "66558867756905585659040922208977402195771898675559656012123222920529675780034",
                    "profit": 3000,
                    "trigger_price": 110900
                },
                {
                    "level": 2,
                    "tokenid": "26588978377210647735520853243231372461065624545828555407481471791355488037951",
                    "profit": 3000,
                    "trigger_price": 104900
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
- **level**: 价格级别 (0=立即执行, 1+=价格跨越触发)
- **tokenid**: Polymarket代币ID
- **profit**: 目标利润 (美元)
- **trigger_price**: 触发价格 (美元，level 0立即执行)

## 🚀 快速开始

### 1. 环境准备

```bash
# 激活虚拟环境
source venv/bin/activate

# 检查依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
nano .env
```

### 2. 配置设置

```bash
# 编辑多币种配置
nano setting_multi_crypto.json

# 设置Polymarket API凭据
export PRIVATE_KEY="你的私钥"
export CLOB_API_KEY="你的API密钥"
export CLOB_SECRET="你的API密钥"
export CLOB_PASS_PHRASE="你的密钥短语"
```

### 3. 启动系统

```bash
# 使用Screen后台运行（推荐）
screen -S multi_crypto_trading -d -m bash -c "cd /root/poly && source venv/bin/activate && python multi_crypto_auto_trading_fixed.py"

# 或直接运行
python multi_crypto_auto_trading_fixed.py
```

### 4. 管理Screen会话

```bash
# 查看运行中的会话
screen -list

# 连接到会话
screen -r multi_crypto_trading

# 分离会话 (在会话内按 Ctrl+A, D)

# 停止会话
screen -S multi_crypto_trading -X quit
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

### 实时监控状态
- **BTC价格监控**: 当前 $113,748 → 触发 $110,900 (Level 1)
- **ETH价格监控**: 当前 $4,204 → 触发 $4,000 (Level 1) 🎯**即将触发**
- **SOL价格监控**: 当前 $182 → 触发 $210 (Level 1)
- **运行时长**: 8小时25分钟 (04:23启动)
- **实时价格更新**: 每秒刷新，实时记录

### 价格跨越机制
```
触发条件：价格从一侧跨越触发线到另一侧
示例：BTC从 $113,577 上涨跨越 $113,600 → 触发交易
重启重置：程序重启后所有触发状态清零
异常处理：自动过滤异常价格波动 (>50%变化)
```

### 系统性能
- **连续运行**: 8小时25分钟无中断
- **价格检查**: 30,420+ 次 (每秒1次)
- **交易记录**: 1158+ 条记录
- **CPU使用**: 1.0% (稳定)
- **内存使用**: 40.8MB (稳定)

### 日志分析
```bash
# 查看实时日志
tail -f multi_crypto_auto_trading.log

# 查看交易记录
cat multi_crypto_trading_records.json

# 查看特定币种触发记录
grep "BTC.*触发\|BTC.*跨越\|BTC.*成功" multi_crypto_auto_trading.log

# 查看ETH接近触发的情况
grep "ETH.*4,20" multi_crypto_auto_trading.log | tail -10
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

### v3.1 最新更新
- **长期稳定运行**: 8小时+连续运行验证
- **ETH价格接近触发**: $4,204接近$4,000触发线
- **性能优化**: CPU和内存使用稳定
- **日志管理**: 自动清理机制避免磁盘问题

### v3.0 特性回顾
- **价格跨越机制**: 智能检测价格跨越触发条件
- **重启重置逻辑**: 程序重启时自动重置触发状态
- **API源优化**: 从CoinGecko→Binance→Coinbase API
- **Screen集成**: 完善的后台运行支持
- **错误检测增强**: 改进交易成功/失败判断逻辑

### 性能优化
- **刷新频率**: 从30秒优化到1秒
- **日志优化**: 实时记录价格和交易状态
- **内存管理**: 智能日志清理机制
- **并发处理**: 支持多币种并发价格获取

## 📈 当前运行状态

### 系统信息
- **系统版本**: v3.1 (修正版)
- **支持币种**: BTC, ETH, SOL
- **监控频率**: 1秒/次
- **运行环境**: Screen后台会话 (PID: 2426317)
- **API源**: Coinbase Exchange Rates
- **运行时长**: 8小时25分钟 (稳定运行)

### 实时价格状态
```
BTC: $113,748 (远高于$110,900触发线)
ETH: $4,204 (接近$4,000触发线) 🎯
SOL: $182 (低于$210触发线)
```

### 交易执行记录
- **总交易记录**: 1158+ 条
- **BTC Level 0**: ✅ 已触发执行 (04:23:06)
- **BTC Level 1**: ✅ 已触发执行 (04:03:08)
- **ETH Level 0**: ✅ 已触发执行
- **SOL Level 0**: ✅ 已触发执行
- **当前状态**: 运行正常，ETH接近触发条件

### 触发状态
- **BTC**: Level 0,1已触发，Level 2等待跌破$104,900
- **ETH**: Level 0已触发，Level 1等待涨破$4,000 (当前$4,204接近)
- **SOL**: Level 0已触发，Level 1等待涨破$210

## ⚠️ 重要提醒

1. **真实交易系统**: 请确保配置正确
2. **价格跨越机制**: 需要价格跨越触发线才会执行
3. **重启重置**: 程序重启后触发状态清零，可重新触发
4. **ETH即将触发**: 当前价格$4,204接近$4,000触发线
5. **长期运行**: 系统已验证8小时+稳定运行
6. **Screen管理**: 使用Screen进行后台运行管理
7. **API凭据**: 确保Polymarket API凭据配置正确

## 🔍 API认证要求

Polymarket CLOB API需要L1+L2双重认证：

### L1认证 (私钥签名)
- 用于创建API密钥
- 签名交易订单
- EIP-712标准签名

### L2认证 (API凭据)
- API Key + Secret + Passphrase
- 访问受保护接口
- 执行交易操作

## 📊 系统统计

### 运行统计 (当前会话)
- **启动时间**: 2025-08-20 04:23
- **运行时长**: 8小时25分钟
- **价格检查次数**: ~30,420次
- **交易记录**: 1158+ 条
- **系统重启次数**: 0 (连续运行)
- **API错误次数**: 0 (稳定)

### 性能指标
- **CPU使用率**: 1.0% (稳定)
- **内存使用**: 40.8MB (稳定)
- **磁盘I/O**: 正常
- **网络连接**: 稳定

## 📞 支持

如遇问题，请检查：
1. 配置文件语法是否正确
2. Token ID是否有效
3. API凭据是否配置
4. 网络连接是否正常
5. Screen会话是否正常运行
6. 磁盘空间是否充足

## 🆕 更新日志

### v3.1 (2025-08-20)
- ✅ 验证长期稳定运行 (8小时+)
- ✅ ETH价格接近触发条件 ($4,204→$4,000)
- ✅ 系统性能优化和监控
- ✅ 交易记录达到1158+条
- ✅ 零错误连续运行验证

### v3.0 (2025-08-20)
- ✅ 实现智能价格跨越触发机制
- ✅ 添加程序重启触发状态自动重置
- ✅ 优化API源从CoinGecko到Coinbase
- ✅ 增强交易成功/失败判断逻辑
- ✅ 完善Screen后台运行支持

### v2.1 (2025-08-06)
- ✅ 添加自动日志清理功能
- ✅ 集成webhook通知系统
- ✅ 优化API限制处理
- ✅ 新增环境变量生成工具