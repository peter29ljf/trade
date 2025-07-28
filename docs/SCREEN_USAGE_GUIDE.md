# Screen 会话管理指南

## 🎯 当前状态
多币种交易系统已在screen会话中运行：

```
会话名称: multi_crypto_trading
会话ID: 725799
状态: Attached (已连接)
```

## 🔧 Screen 基本操作

### 查看所有screen会话
```bash
screen -ls
```

### 连接到交易系统会话
```bash
# 连接到具体会话
screen -r multi_crypto_trading

# 或使用会话ID
screen -r 725799
```

### 在screen会话内的操作
当您连接到screen会话后，可以：

1. **查看系统运行状态**
   - 系统会显示实时日志
   - 可以看到价格监控信息
   - 可以看到交易触发和执行信息

2. **分离会话（让程序继续后台运行）**
   ```
   按键组合: Ctrl + A, 然后按 D
   ```

3. **停止交易系统**
   ```
   按键组合: Ctrl + C
   ```

### 从外部管理会话

#### 分离会话（如果当前已连接）
```bash
screen -d multi_crypto_trading
```

#### 重新连接会话
```bash
screen -r multi_crypto_trading
```

#### 强制连接（如果会话显示已连接但无法访问）
```bash
screen -D -r multi_crypto_trading
```

#### 终止会话
```bash
screen -S multi_crypto_trading -X quit
```

## 🚀 启动交易系统

### 在screen会话中启动系统
连接到screen会话后，运行：

```bash
cd /root/poly
source venv_py3.12/bin/activate
./start_multi_crypto_trading.sh
```

### 或直接运行Python脚本
```bash
cd /root/poly
source venv_py3.12/bin/activate
python multi_crypto_auto_trading_fixed.py
```

## 📊 监控系统状态

### 从外部查看日志（不干扰screen会话）
```bash
# 查看实时日志
tail -f /root/poly/multi_crypto_auto_trading.log

# 查看最近的日志
tail -n 50 /root/poly/multi_crypto_auto_trading.log

# 查看交易记录
cat /root/poly/multi_crypto_trading_records.json
```

### 检查系统进程
```bash
ps aux | grep multi_crypto
ps aux | grep python
```

## 🔄 重启系统

### 方法1: 在screen会话内重启
1. 连接到screen: `screen -r multi_crypto_trading`
2. 停止当前程序: `Ctrl + C`
3. 重新启动: `./start_multi_crypto_trading.sh`
4. 分离会话: `Ctrl + A, D`

### 方法2: 完全重启screen会话
```bash
# 终止当前会话
screen -S multi_crypto_trading -X quit

# 创建新会话并启动系统
screen -S multi_crypto_trading -d -m bash -c "cd /root/poly && source venv_py3.12/bin/activate && python multi_crypto_auto_trading_fixed.py"
```

## ⚠️ 注意事项

1. **不要关闭终端**
   - Screen会话可以在SSH断开后继续运行
   - 但要确保服务器不重启

2. **定期检查系统状态**
   ```bash
   screen -ls  # 检查会话是否还在运行
   tail -f /root/poly/multi_crypto_auto_trading.log  # 查看系统日志
   ```

3. **系统监控**
   - 查看 `multi_crypto_auto_trading.log` 了解系统运行状态
   - 查看 `multi_crypto_trading_records.json` 了解交易记录
   - 系统每分钟记录价格监控信息

4. **紧急停止**
   ```bash
   # 如果需要立即停止系统
   screen -S multi_crypto_trading -X stuff "^C"
   
   # 或者终止整个会话
   screen -S multi_crypto_trading -X quit
   ```

## 📋 常用命令组合

### 快速检查系统状态
```bash
echo "=== Screen 会话状态 ==="
screen -ls

echo "=== 系统进程 ==="
ps aux | grep -E "(multi_crypto|python)" | grep -v grep

echo "=== 最新日志 ==="
tail -n 10 /root/poly/multi_crypto_auto_trading.log
```

### 快速重启系统
```bash
# 停止当前会话
screen -S multi_crypto_trading -X quit

# 等待2秒
sleep 2

# 重新启动
screen -S multi_crypto_trading -d -m bash -c "cd /root/poly && source venv_py3.12/bin/activate && python multi_crypto_auto_trading_fixed.py"

# 检查状态
screen -ls
```

## 🎯 推荐工作流程

1. **日常检查**
   ```bash
   screen -ls  # 确认会话运行中
   tail -f /root/poly/multi_crypto_auto_trading.log  # 查看实时日志
   ```

2. **连接查看**
   ```bash
   screen -r multi_crypto_trading  # 连接查看详细状态
   # 查看后按 Ctrl+A, D 分离
   ```

3. **系统维护**
   ```bash
   screen -r multi_crypto_trading  # 连接会话
   # 按需停止/重启系统
   # Ctrl+A, D 分离会话
   ``` 