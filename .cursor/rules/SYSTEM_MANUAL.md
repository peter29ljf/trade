# Polymarket 多级交易策略系统使用说明

## 项目概述

Polymarket多级交易策略系统是一个专为Polymarket平台设计的自动化交易工具。系统基于价格触发机制，能在市场价格变动时自动执行分级买入操作，以实现预设的目标利润。

## 系统架构

### 文件结构
```
polymarket-auto-trader/
├── README.md                  # 项目说明文档
├── config/
│   ├── config.py              # 配置文件（API密钥、URL等）
│   └── constants.py           # 常量定义
├── server/
│   ├── app.py                 # 主应用入口
│   ├── webhook/
│   │   ├── webhook_server.py  # Webhook 监听服务
│   │   └── signal_processor.py # 信号处理器
│   └── logger.py              # 日志工具
├── ui/
│   ├── index.html             # 主页面
│   ├── components/
│   │   ├── InitialBuyForm.js  # 初始买入表单组件
│   │   ├── LevelSettingsTable.js # 买入级别设置表格
│   │   └── TradingDashboard.js  # 交易状态显示面板
│   ├── css/
│   │   └── styles.css         # 样式表
│   └── js/
│       ├── ui_controller.js   # UI 控制器
│       ├── form_handler.js    # 表单处理
│       └── api_client.js      # 前端 API 客户端
│       
├── python-client/             # Python客户端目录
│   ├── market_buy_order.py    # 市场买单执行
│   ├── check_price.py         # 价格查询工具
│   └── math_utils.py          # 数学计算工具，交易逻辑处理   
├── data/                      # 数据存储文件夹
└── .env                       # 环境变量配置
```

## 用户界面(UI)系统

### 初始买入行设计
- **布局**: 
  - 横向排列的5个输入组件：COINNAME(下拉选择框)、PRICE0(数字输入框)、TOKENID0(文本输入框)、PROFIT(数字输入框，带USDC单位)
  - 操作按钮："买入"和"终止"按钮位于行末端
  - 每个字段设置合适的验证规则(TOKENID0格式、PROFIT>0等)
  - 买入按钮在所有必填字段有效时才启用

- **数据绑定**:
  - 所有输入字段直接绑定到中央状态管理器
  - 买入按钮触发后台API调用，传递完整参数对象
  - 终止按钮触发全局状态更新，停止所有监听和交易活动

### 多级别设置区
- **布局**:
  - 10行表格式布局，每行包含：级别标签、PRICE(n)(数字输入框) 和 TOKENID(n)(文本输入框)
  - 明确标识价格需从高到低排列(例如：80000→75000→70000...)
  - 提供"一键设置"功能，根据初始价格和下降百分比自动填充所有价格级别

- **验证机制**:
  - 实时验证价格递减顺序，错误时高亮显示问题行
  - TOKENID格式验证，确保与Polymarket API兼容
  - 显示每级别的预估买入金额，便于用户了解资金需求

### UI与后端交互
- 使用RESTful API进行状态更新和命令传递
- 实现WebSocket实时更新交易状态和当前级别
- 通过状态同步机制，确保UI上显示的交易状态与后端一致

## 核心功能

1. **Webhook信号监听**：接收外部交易信号，触发自动买入策略
2. **直观的用户界面**：方便设置交易参数和监控交易状态
3. **智能买入策略**：根据多级价格变化自动计算最优买入数量
4. **完整的交易记录**：记录所有交易操作和状态变化
5. **投资限额控制**：设置最大投资额度，防止过度投资

## 安装与配置

### 系统要求
- Python 3.7+
- 用于前端的Node.js 14+

### 依赖项安装
前端JavaScript:
```bash
# 安装所有必要依赖
npm install
```

后端Python:
```bash
# 安装所有必要依赖
pip install requests python-dotenv py-clob-client Flask
```

### 环境变量配置
创建`.env`文件在项目根目录：
```
# API 凭据
CLOB_API_KEY=您的API密钥
CLOB_SECRET=您的API密钥密钥
CLOB_PASS_PHRASE=您的API通行短语

# Polymarket 节点
CLOB_HOST=https://clob.polymarket.com

# 代理设置 (开发/测试环境使用，生产环境可删除)
HTTP_PROXY=http://username:password@proxy_host:port
HTTPS_PROXY=http://username:password@proxy_host:port

# WebSocket 配置
WEBSOCKET_PORT=5000
WEBHOOK_SECRET=您的webhook安全密钥

# 交易配置
MAX_INVESTMENT=1000  # 最大投资额度(USDC)
MAX_LEVELS=10        # 最大买入级别数

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=./logs/trading.log
```

## 系统运行流程

### 1. 初始化阶段
- 系统启动，加载配置
- 初始化UI界面和各个组件
- 启动webhook监听服务

### 2. 设置阶段
- 用户在UI中设置交易参数：
  - 初始买入行：COINNAME、PRICE0、TOKENID0、PROFIT
  - 价格阶梯：PRICE1~PRICE10、TOKENID1~TOKENID10（价格必须从高到低排列）
- 系统保存设置到存储中

### 3. 初始买入
- 用户点击"买入"按钮
- 系统查询TOKENID0的市场价格(MARKETPRICE0)
- 计算初始买入数量：AMOUNT_0 = PROFIT * (1/MARKETPRICE0 - 1)
- 执行市价买入订单
- 记录买入数量和交易细节
- 系统状态更新为"等待第一级信号"

### 4. 信号监听与匹配机制
- Webhook服务持续运行，等待外部信号
- 当接收到信号时，系统执行以下验证：
  - 验证COINNAME是否与设置的代币名称匹配
  - 检查信号中的PRICE是否匹配任一PRICE1~PRICE10
  - 使用容差匹配（默认±0.1%）来适应轻微的价格波动
  - 当有多个可能匹配的价格级别时，优先选择最高级别
  - 对同一价格级别的重复信号进行去重处理

### 5. 信号触发交易
- 当信号匹配PRICE1时：
  - 系统状态更新为"处理第一级买入"
  - 查询TOKENID1的市场价格(MARKETPRICE1)
  - 计算买入数量：AMOUNT_1 = (AMOUNT_0 + PROFIT) * MARKETPRICE1
  - 执行市价买入订单
  - 交易完成后，状态更新为"等待第二级信号"
  - 允许跨级交易，如果接收的信号满足下一级的交易，允许直接进行跨级交易
  
- 当信号匹配PRICE2时：
  - 系统状态更新为"处理第二级买入"
  - 查询TOKENID2的市场价格(MARKETPRICE2)
  - 计算买入数量：AMOUNT_2 = (AMOUNT_0 + AMOUNT_1 + PROFIT) * MARKETPRICE2
  - 执行市价买入订单
  - 交易完成后，状态更新为"等待第三级信号"

- 依此类推，最多执行到第十级买入，同时考虑投资额度限制

### 6. 终止阶段
- 当以下情况之一发生时系统进入终止阶段：
  - 用户点击"终止"按钮
  - 所有配置的级别的买入完成
  - 达到最大投资额度
  - 系统检测到错误或异常条件
- 系统停止接收新的交易信号
- 保持现有持仓，不再执行新的买入
- 更新UI显示终止状态和原因

## 交易逻辑详解

### 买入数量计算

1. **初始买入计算**
   ```
   AMOUNT_0 = PROFIT * (1/MARKETPRICE0 - 1)
   ```
   - 当MARKETPRICE0 >= 1.0时，不执行初始买入

2. **后续级别阶梯计算**
   ```
   AMOUNT_n = (AMOUNT_0 + ... + AMOUNT_n-1 + PROFIT) * MARKETPRICE_n
   ```
   - 注意：这里是乘以市场价格，而不是除以市场价格
   - 这与经典的均值回归策略相符，当价格下跌时买入更多

### math_utils.py 核心算法

以下是`python-client/math_utils.py`中的核心算法实现：

```python
def calculate_initial_amount(profit, market_price):
    """计算初始买入量: AMOUNT_0 = PROFIT * (1/MARKETPRICE0 - 1)"""
    if market_price >= 1.0:
        return 0  # 当价格>=1.0时，公式无法产生有效买入量
    
    buy_amount = profit * (1/market_price - 1)
    return buy_amount

def calculate_next_amount(previous_amounts, profit, market_price):
    """计算后续级别买入数量: AMOUNT_n = (AMOUNT_0 + ... + AMOUNT_n-1 + PROFIT) * MARKETPRICE_n"""
    # 计算之前所有级别的总买入数量
    total_previous = sum(previous_amounts)
    
    # 使用正确公式计算本级别买入数量（乘以市场价格）
    buy_amount = (total_previous + profit) * market_price
    return buy_amount

def is_price_match(signal_price, target_price, tolerance=0.001):
    """判断信号价格是否匹配目标价格，支持容差范围"""
    # 将字符串价格转换为浮点数
    if isinstance(signal_price, str):
        signal_price = float(signal_price)
    if isinstance(target_price, str):
        target_price = float(target_price)
    
    # 计算允许的误差范围
    allowed_diff = target_price * tolerance
    
    # 检查是否在误差范围内
    return abs(signal_price - target_price) <= allowed_diff
```



## 使用指南

### 启动应用
前端:
```bash
# 确保在项目根目录
cd polymarket-auto-trader

# 运行前端
npm start
```

后端:
```bash
# 确保在项目根目录
cd polymarket-auto-trader

# 启动Python后端服务
python server/app.py

# 或者单独执行买入操作
cd python-client
python market_buy_order.py <token_id> <amount>

# 启动交易服务器
python trading_server.py <token_id> --profit 10.0 --max 100.0 --levels 10
```

### 设置交易参数

1. **初始买入设置**
   - 填写`代币名称`：用于匹配外部信号
   - 设置`初始价格`：参考价格
   - 输入`代币ID`：Polymarket平台的代币标识符
   - 设定`目标利润`：预期获得的利润金额(USDC)
   - 点击`执行初始买入`按钮开始交易

2. **多级买入设置**
   - 为每个级别设置`触发价格`和对应的`代币ID`
   - **重要**: 系统会按照价格从高到低排列，依次触发买入操作
   - 支持最多10个级别的自动买入
   - 点击`保存多级设置`保存配置
   - 可以设置最大投资额度，防止过度投资

### Webhook信号接收

系统支持通过HTTP POST请求接收外部交易信号：
```
POST http://您的服务器地址:5000/webhook
Content-Type: application/json

{
  "COINNAME": "BTC",
  "PRICE": "75000"
}
```

## 注意事项

1. **API密钥安全**
   - 妥善保管您的API密钥，避免泄露
   - 不要将包含真实密钥的`.env`文件提交到版本控制系统

2. **风险控制**
   - 始终设置最大投资额度，避免过度投资
   - 初次使用时，使用较小的目标利润金额进行测试
   - 监控系统运行状态，必要时及时终止交易
   - 注意：购买量计算是根据价格与前期购买量之间的关系动态计算的

3. **网络要求**
   - 确保服务器有稳定的互联网连接
   - 在开发/测试环境中，可能需要使用代理服务器
   - 生产环境部署时，考虑移除代理配置以提高性能

4. **系统维护**
   - 定期备份交易记录和日志
   - 监控系统内存和CPU使用情况
   - 根据市场情况调整交易策略和参数

## 扩展与改进建议

1. **交易明细记录**
   - 添加交易历史记录功能
   - 显示每次交易的详细信息（价格、数量、时间）
   - 提供导出报表功能

2. **错误恢复机制**
   - 添加交易失败后的重试机制
   - 系统崩溃后的状态恢复功能

3. **系统监控**
   - 添加系统状态监控面板
   - 实现自动警报功能
   - 交易执行状态可视化

4. **性能优化**
   - 优化价格查询频率
   - 添加缓存机制减少API调用
   - 改进数据存储结构

5. **用户界面增强**
   - 为初始买入和多级设置添加可视化编辑器
   - 实时价格监控面板
   - 资金使用情况预测工具

6. **模拟交易模式**
   - 添加模拟交易功能，测试策略而不实际执行订单
   - 提供回测功能，使用历史数据评估策略效果

---

通过以上详细说明，您可以完整理解Polymarket多级交易策略系统的设计理念和使用方法，从而有效地部署和运行该系统。如有任何问题，请参考源代码或联系技术支持。 