#!/bin/bash
# start_server.sh - Polymarket自动交易系统启动脚本

# 设置环境变量
export NODE_ENV=production

# 输出启动信息
echo "===== Polymarket自动交易系统启动 ====="
echo "启动时间: $(date)"
echo "使用Python版本: $(./venv_py3.12/bin/python -V)"
echo "⚠️  警告: 服务器将以真实交易模式运行! ⚠️"
echo

# 激活Python 3.12虚拟环境
source ./venv_py3.12/bin/activate

# 检查环境配置
echo "执行环境检查..."
python check_environment.py
if [ $? -ne 0 ]; then
  echo "❌ 环境检查失败，请修复问题后重试"
  exit 1
fi

# 启动Node.js服务器
echo
echo "启动Webhook服务器..."
echo "日志将保存到: server.log"
npm start > server.log 2>&1 &

# 保存进程ID
SERVER_PID=$!
echo $SERVER_PID > server.pid
echo "服务器进程ID: $SERVER_PID"

# 等待服务器启动
echo "等待服务器启动..."
sleep 3

# 检查服务器状态
if ps -p $SERVER_PID > /dev/null; then
  echo "✅ 服务器已成功启动"
  echo "可以通过以下URL访问服务器:"
  echo "- 状态页面: http://localhost:5001/status"
  echo "- Webhook: http://localhost:5001/webhook"
  echo
  echo "要停止服务器，请运行: ./stop_server.sh"
else
  echo "❌ 服务器启动失败，请检查日志文件: server.log"
  exit 1
fi 