# Polymarket 自动交易系统

## 项目概述

这是一个用于Polymarket的自动交易系统，通过Webhook触发器自动执行买入交易。系统支持初始级别(level 0)和后续级别(level 1+)的买入操作，会自动计算最优买入金额并执行交易。系统当前配置为**真实交易模式**，请谨慎操作。

## 仓库地址

项目托管在GitHub上: [https://github.com/peter29ljf/poly](https://github.com/peter29ljf/poly)

## 系统架构

系统由以下主要组件构成：

1. **Node.js Webhook服务器** (`apptest.js`): 接收交易信号，并调用相应的Python脚本执行交易
2. **初始买入脚本** (`execute_initial_buy.py`): 执行level 0级别的初始买入
3. **后续买入脚本** (`execute_next_buy.py`): 执行level 1及以上级别的后续买入
4. **市场买入模块** (`market_buy_order.py`): 实际执行市场买单的核心模块
5. **市场卖出模块** (`market_sell_order.py`): 实际执行市场卖单的核心模块
6. **价格查询模块** (`check_price.py`): 查询市场价格
7. **计算工具** (`math_utils.py`): 计算最优买入金额
8. **环境检查模块** (`check_environment.py`): 启动前检查系统环境配置
9. **Py-Clob-Client库** (`py-clob-client/`): Polymarket CLOB API的Python客户端

## 目录结构

```
polymarket/
├── apptest.js              # Webhook服务器
├── execute_initial_buy.py  # 初始买入脚本
├── execute_next_buy.py     # 后续级别买入脚本
├── market_buy_order.py     # 市场买入执行模块
├── market_sell_order.py    # 市场卖出执行模块
├── check_price.py          # 价格查询模块
├── math_utils.py           # 数学计算工具
├── check_environment.py    # 环境检查模块
├── start_server.sh         # 服务器启动脚本
├── requirements.txt        # Python依赖
├── .env.example            # 环境变量配置示例
├── data/                   # 数据目录
│   ├── webhook_record.json # 交易记录
│   ├── webhook_requests.log # 请求日志
│   ├── webhook_last_response.json # 最近响应
│   └── webhook_last_error.json # 最近错误
├── package.json            # Node.js项目配置
├── package-lock.json       # Node.js依赖锁定
└── py-clob-client/         # Polymarket API客户端
```

## 安装步骤

### 1. 克隆仓库

```bash
# 克隆项目仓库
git clone https://github.com/peter29ljf/poly.git
cd poly
```

### 2. 环境要求

**Python版本要求:**
- Python 3.12 或更高版本

**Node.js版本要求:**
- Node.js 18 或更高版本

### 3. 创建Python虚拟环境

```bash
# 创建Python 3.12虚拟环境
python3.12 -m venv venv_py3.12

# 激活虚拟环境
source venv_py3.12/bin/activate  # Linux/Mac
# 或
# venv_py3.12\Scripts\activate    # Windows
```

### 4. 安装依赖

**Node.js依赖:**
```bash
npm install
```

**Python依赖:**
```bash
pip install -r requirements.txt
pip install -r py-clob-client/requirements.txt
```

主要Python依赖包括:
- flask==2.3.3
- flask-cors==4.0.0
- python-dotenv==0.19.2
- requests==2.32.3
- urllib3==2.0.7
- cryptography==41.0.5
- web3==6.11.0
- py_order_utils==0.3.2
- poly_eip712_structs==0.0.1

### 5. 配置文件

将`.env.example`复制为`.env`并填入您的配置:
```bash
cp .env.example .env
# 然后编辑.env文件添加您的API密钥等信息
```

`.env`文件需要包含以下内容：
```
# API配置
CLOB_HOST=https://clob.polymarket.com
CLOB_API_KEY=你的API密钥
CLOB_SECRET=你的API密钥
CLOB_PASS_PHRASE=你的密码
PRIVATE_KEY=你的私钥
WALLET_ADDRESS=你的钱包地址

# 服务器配置
PORT=5002

# 交易配置
MAX_INVESTMENT=1000
MAX_LEVELS=10
```

### 6. 创建数据目录

```bash
# 确保数据目录存在
mkdir -p data
```

## 使用方法

### 启动Webhook服务器

通过启动脚本启动服务器（推荐）:
```bash
chmod +x start_server.sh
./start_server.sh
```

或手动启动:
```bash
source venv_py3.12/bin/activate
npm start
```

服务器会在端口5002上启动，并接受以下格式的Webhook请求：

```json
{
  "tokenid": "123456789...",
  "profit": 20.0,
  "level": 0
}
```

### 手动执行交易

**初始买入:**
```bash
python execute_initial_buy.py <token_id> <profit> [--dry-run] [--market-name NAME] [--data-dir DIR]
```

**后续级别买入:**
```bash
python execute_next_buy.py <token_id> --level <level> --profit <profit> [--dry-run] [--auto-confirm] [--data-dir DIR]
```

**市场卖出:**
```bash
python market_sell_order.py
```

**检查市场价格:**
```bash
python check_price.py <token_id> [--host HOST]
```

**检查系统环境:**
```bash
python check_environment.py
```

## 交易记录格式

交易记录保存在`data/webhook_record.json`文件中，格式如下：

```json
{
  "trades": {
    "pre_totalamount": 33.333333,
    "buy_records": [
      {
        "token_id": "2050604593...",
        "profit": 20.0,
        "price": 0.6,
        "amount": 20.0,
        "level": 1,
        "timestamp": 1745123846
      }
    ]
  }
}
```

## 安全限制

系统内置了安全限制，防止意外触发大额交易：

- 最大利润金额: 50 USDC
- 最大买入级别: 5
- 可选的tokenId白名单

这些限制可在`apptest.js`中的`SAFETY_LIMITS`配置中修改。

## API端点

### Webhook端点
- **POST /webhook**: 接收交易信号并执行相应交易 (`http://localhost:5002/webhook`)
- **GET /status**: 获取服务器状态 (`http://localhost:5002/status`)
- **GET /**: 获取服务器基本状态 (`http://localhost:5002/`)

## 日志和监控

系统自动保存以下日志：
- **server.log**: 服务器主日志
- **webhook_requests.log**: 所有接收到的Webhook请求
- **webhook_last_response.json**: 最近一次成功响应
- **webhook_last_error.json**: 最近一次错误

状态监控:
```bash
curl http://localhost:5002/
curl http://localhost:5002/status
```

## 服务器管理命令

**启动服务器:**
```bash
./start_server.sh
```

**停止服务器:**
```bash
kill $(cat server.pid)
```

**检查服务器状态:**
```bash
ps -p $(cat server.pid)
```

## Python 3.12 兼容性

所有Python脚本已适配Python 3.12，使用了如下技术确保兼容性：
- 明确的shebang行: `#!/usr/bin/env python3.12`
- 使用importlib.util动态导入模块
- 使用现代Python语法特性
- 依赖版本已针对3.12进行调整

## 注意事项

1. **⚠️ 当前系统配置为真实交易模式，所有交易会实际执行**
2. 如需测试，请在脚本命令中添加`--dry-run`参数
3. 服务器启动时会显示明确的警告，标明正在执行真实交易
4. 请定期检查日志，确保系统正常运行
5. 确保`.env`文件中的API密钥和私钥安全保存
6. 建议定期备份data目录下的交易记录

## 必要文件清单

系统运行必须保留以下文件：
- apptest.js
- execute_initial_buy.py
- execute_next_buy.py
- market_buy_order.py
- market_sell_order.py
- check_price.py
- math_utils.py
- check_environment.py
- start_server.sh
- py-clob-client/ (目录)
- requirements.txt
- .env (从.env.example创建)
- data/ (目录)
- package.json
- package-lock.json

## 故障排除

### 常见问题

1. **找不到模块错误**
   ```
   No module named 'xxx'
   ```
   解决方案: 确保已安装所有依赖，包括py-clob-client的依赖:
   ```bash
   pip install -r requirements.txt
   pip install -r py-clob-client/requirements.txt
   ```

2. **导入错误**
   ```
   ImportError: cannot import name 'xxx'
   ```
   解决方案: 检查Python版本是否为3.12，并确保模块路径正确:
   ```bash
   python --version
   ```

3. **API连接错误**
   解决方案: 检查网络连接和代理设置，确保.env文件中的API配置正确 

4. **权限错误**
   ```
   Permission denied: './start_server.sh'
   ```
   解决方案: 确保脚本有执行权限:
   ```bash
   chmod +x start_server.sh
   ```

## 贡献方式

欢迎通过GitHub Issues和Pull Requests提交改进建议和Bug修复。

## 许可

本项目为私有项目，未经授权不得使用或分发。 