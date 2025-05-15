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
9. **Py-Clob-Client库** (`py-clob-client/`): Polymarket CLOB API的Python客户端，已集成到本仓库中

## 目录结构

```
poly/
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
├── package.json            # Node.js项目配置
├── package-lock.json       # Node.js依赖锁定
├── server.log              # 服务器运行日志
├── server.pid              # 服务器进程ID文件
├── data/                   # 数据目录
│   ├── webhook_record.json        # 交易记录
│   ├── webhook_requests.log       # 请求日志
│   ├── webhook_last_response.json # 最近响应
│   └── webhook_last_error.json    # 最近错误
├── node_modules/           # Node.js依赖模块
├── venv_py3.12/            # Python 3.12虚拟环境
└── py-clob-client/         # Polymarket API客户端（已集成到本仓库）
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
```

主要Python依赖包括:
- flask==2.3.3
- flask-cors==4.0.0
- python-dotenv==1.0.0
- requests==2.31.0
- urllib3==2.0.7
- cryptography==41.0.5
- web3==6.11.0
- py-clob-client (从GitHub仓库自动安装)

主要Node.js依赖包括:
- express==4.18.2
- body-parser==1.20.2

### 5. 配置文件

将`.env.example`复制为`.env`并填入您的配置:
```bash
cp .env.example .env
# 然后编辑.env文件添加您的API密钥等信息
```

`.env`文件需要包含以下内容：
```
# API配置
POLYMARKET_HOST=https://clob.polymarket.com
POLYMARKET_API_KEY=你的API密钥
POLYMARKET_PASSWORD=你的密码
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

### 使用Screen保持服务器运行

如果需要在SSH连接断开后保持服务器运行，可以使用Screen:

```bash
# 安装screen
apt install -y screen

# 创建新的screen会话并运行服务器
screen -dmS n8n_session ./start_server.sh

# 查看运行中的screen会话
screen -list

# 重新连接到会话
screen -r n8n_session
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

- 最大利润金额: 2000 USDC
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
./stop_server.sh
```

**防火墙配置:**
如果需要从外部访问服务器，需要开放相应端口:
```bash
# 使用UFW开放端口
ufw allow 5002/tcp
```

## 常见问题排查

1. **服务器无法启动**
   - 检查Python虚拟环境是否正确激活
   - 检查依赖是否完整安装
   - 查看server.log日志文件获取详细错误信息

2. **权限问题**
   - 确保所有Python脚本有执行权限: `chmod +x *.py`
   - 确保启动脚本有执行权限: `chmod +x start_server.sh`

3. **端口冲突**
   - 如果端口5002已被占用，可在package.json中修改端口配置
   - 使用`lsof -i :5002`检查是否有进程占用该端口

4. **安全Cookie问题**
   - 如遇到安全Cookie错误，可设置环境变量: `N8N_SECURE_COOKIE=false`

## 维护与更新

定期检查依赖更新和系统日志，确保系统稳定运行。如有问题，请参考GitHub仓库的Issues部分或提交新的问题报告。 