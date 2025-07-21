#!/bin/bash

# 简化版自动交易系统启动脚本

echo "============================================"
echo "🤖 Polymarket 简化版自动交易系统启动脚本"
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

if [ ! -f "setting.json" ]; then
    echo "❌ 错误: 未找到 setting.json 文件"
    echo "请确保配置文件存在"
    exit 1
fi

if [ ! -f "plan.md" ]; then
    echo "❌ 错误: 未找到 plan.md 文件"
    echo "请确保交易计划文件存在"
    exit 1
fi

# 检查权限
echo "检查脚本权限..."
chmod +x *.py

# 显示配置信息
echo ""
echo "📊 系统配置信息:"
echo "--------------------------------"

# 读取setting.json内容
if [ -f "setting.json" ]; then
    echo "价格级别配置:"
    python3 -c "
import json
with open('setting.json', 'r') as f:
    data = json.load(f)
    for level in data.get('levels', []):
        if level['level'] == 0:
            print(f'  Level {level[\"level\"]}: 启动时立即执行 -> Profit \${level[\"profit\"]}')
        else:
            print(f'  Level {level[\"level\"]}: BTC \${level[\"btcprice\"]:,} -> Profit \${level[\"profit\"]}')
"
fi

echo ""
echo "⚠️  重要提醒:"
echo "• 这是真实交易系统，请确保配置正确"
echo "• 系统启动后会立即执行Level 0交易"
echo "• Level 1+等待BTC价格信号触发"
echo "• 建议先进行小额测试"
echo "• 按 Ctrl+C 可以随时停止系统"

echo ""
read -p "确认启动简化版自动交易系统吗？(y/N): " confirm

if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
    echo ""
    echo "🚀 启动简化版自动交易系统..."
    echo "日志文件: auto_trading.log"
    echo "交易记录: auto_trading_records.json"
    echo ""
    
    # 启动系统
    python simplified_auto_trading.py
else
    echo "已取消启动"
fi