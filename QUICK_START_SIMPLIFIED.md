# 简化版自动交易系统快速启动指南

## 🚀 问题解决

由于复杂依赖包（numpy）安装问题，我已经创建了一个简化版的自动交易系统，不依赖复杂的机器学习库。

## 📋 简化版功能

### ✅ 保留的核心功能：
- BTC价格实时监控（币安API）
- 基于setting.json的价格级别触发
- 自动执行Polymarket交易
- 完整的交易记录和日志
- 基于plan.md的交易指导

### ❌ 简化的功能：
- 不使用Google嵌入模型（避免numpy依赖）
- 不使用复杂的RAG检索
- 简化的知识库匹配

## 🛠️ 快速启动

### 1. 启动简化版系统
```bash
./start_simplified_trading.sh
```

### 2. 或者直接运行
```bash
source venv_py3.12/bin/activate
python simplified_auto_trading.py
```

## 📊 系统工作流程

1. **价格监控**: 每5秒检查BTC价格
2. **触发检测**: 当达到设定级别时触发交易
3. **价格查询**: 查询目标代币当前价格
4. **金额计算**: 使用公式 `amount = profit/(1/price-1)`
5. **执行交易**: 调用market_buy_order.py执行买入
6. **记录保存**: 保存到auto_trading_records.json

## 🔧 配置文件

### setting.json (当前配置)
```json
{
  "levels": [
    {
      "level": 0,
      "tokenid": "30962849301395034865691297877166366190057226558979258784219057690978861378316",
      "profit": 15,
      "btcprice": 125000
    },
    {
      "level": 1,
      "tokenid": "85166522335179474776871910026024275251172545371734719891846488022601938005114",
      "profit": 15,
      "btcprice": 130000
    },
    {
      "level": 2,
      "tokenid": "61312557535411044174078716902537497533470723177739593226047128539006706238224",
      "profit": 15,
      "btcprice": 140000
    }
  ]
}
```

### plan.md (交易计划)
```
交易计划
1 我先按照level 0 的tokenid，查询一下目前这个id的价格，然后按照这个公式计算购买股份使用的usdc的amount=profit/(1/price-1)，然后发送level 0 的tokenid 和 amount 进行交易。
2 当我接收到btcprice 到125000 的时候，按照level 1 的tokenid，查询一下目前这个id的价格，按照这个公式计算购买股份使用的usdc的amount=profit/(1/price-1),然后发送level 1 的tokenid 和 amount 进行交易。
3 当我接收到btcprice 到130000 的时候，按照level 2 的tokenid，查询一下目前这个id的价格，按照这个公式计算购买股份使用的usdc的amount=profit/(1/price-1),然后发送level 2 的tokenid 和 amount 进行交易。
```

## 📱 实时监控

### 查看日志
```bash
tail -f auto_trading.log
```

### 查看交易记录
```bash
cat auto_trading_records.json
```

### 停止系统
按 `Ctrl+C` 即可停止系统

## ⚠️ 重要提醒

1. **真实交易**: 这是真实的资金交易，请谨慎操作
2. **价格触发**: 每个级别只触发一次，避免重复交易
3. **网络连接**: 需要稳定的网络连接访问币安和Polymarket API
4. **余额检查**: 确保账户有足够的USDC余额

## 🐛 如果还有问题

1. 检查网络连接
2. 确认API密钥配置正确
3. 查看日志文件获取详细错误信息
4. 确保账户余额充足

## 📈 系统优势

- **轻量级**: 不依赖复杂的机器学习库
- **可靠性**: 简化的架构更稳定
- **易维护**: 代码结构清晰，易于调试
- **高效率**: 快速响应价格变化

现在您可以使用简化版系统进行自动交易了！🚀