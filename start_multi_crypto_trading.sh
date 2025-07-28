#!/bin/bash

# 多币种自动交易系统启动脚本

echo "============================================"
echo "🚀 Polymarket 多币种自动交易系统启动脚本"
echo "============================================"

# 检查Python版本
python_version=$(python3 --version 2>&1)
echo "Python版本: $python_version"

# 激活虚拟环境
if [ -d "venv_py3.12" ]; then
    echo "激活Python虚拟环境..."
    source venv_py3.12/bin/activate
else
    echo "错误: 未找到虚拟环境目录 venv_py3.12"
    echo "请先创建虚拟环境: python3.12 -m venv venv_py3.12"
    exit 1
fi

# 安装基本依赖
echo "检查并安装基本依赖..."
pip install aiohttp requests python-dotenv

# 检查必要文件
echo "检查必要文件..."

if [ ! -f "setting_multi_crypto.json" ]; then
    echo "❌ 错误: 未找到 setting_multi_crypto.json 文件"
    echo "请确保多币种配置文件存在"
    exit 1
fi

if [ ! -f "multi_crypto_auto_trading.py" ]; then
    echo "❌ 错误: 未找到 multi_crypto_auto_trading.py 文件"
    echo "请确保多币种交易系统文件存在"
    exit 1
fi

# 检查权限
echo "检查脚本权限..."
chmod +x *.py

# 显示配置信息
echo ""
echo "📊 多币种系统配置信息:"
echo "--------------------------------"

# 读取配置内容
if [ -f "setting_multi_crypto.json" ]; then
    echo "支持的币种及价格级别:"
    python3 -c "
import json
with open('setting_multi_crypto.json', 'r') as f:
    data = json.load(f)
    for crypto, config in data.get('cryptocurrencies', {}).items():
        print(f'\\n🪙 {crypto} ({config[\"symbol\"]}):')
        for level in config.get('levels', []):
            if level['level'] == 0:
                print(f'  Level {level[\"level\"]}: 启动时立即执行 -> Profit \${level[\"profit\"]}')
            else:
                print(f'  Level {level[\"level\"]}: {crypto} \${level[\"trigger_price\"]:,} -> Profit \${level[\"profit\"]}')
"
fi

echo ""
echo "⚠️  重要提醒:"
echo "• 这是真实的多币种交易系统，请确保配置正确"
echo "• 系统启动后会立即执行所有币种的Level 0交易"
echo "• Level 1+等待相应币种价格信号触发"
echo "• 同时监控 BTC、ETH、SOL 三种币种"
echo "• 建议先进行小额测试"
echo "• 按 Ctrl+C 可以随时停止系统"

echo ""
echo "📈 监控功能:"
echo "• BTC价格监控 (触发Level 1+)"
echo "• ETH价格监控 (触发Level 1+)"  
echo "• SOL价格监控 (触发Level 1+)"
echo "• 实时价格更新 (每秒刷新，每秒记录日志)"
echo "• 独立交易记录 (按币种分类)"

echo ""
read -p "确认启动多币种自动交易系统吗？(y/N): " confirm

if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
    echo ""
    echo "🚀 启动多币种自动交易系统..."
    echo "日志文件: multi_crypto_auto_trading.log"
    echo "交易记录: multi_crypto_trading_records.json"
    echo ""
    echo "💡 系统功能:"
    echo "  - 同时监控 BTC、ETH、SOL 价格"
    echo "  - 独立触发机制 (每个币种独立判断)"
    echo "  - 统一交易执行 (使用相同的trading模块)"
    echo "  - 详细日志记录 (按币种分类记录)"
    echo ""
    
    # 启动系统
    python multi_crypto_auto_trading.py
else
    echo "已取消启动"
fi 