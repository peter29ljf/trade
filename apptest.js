// apptest.js - Polymarket webhook 测试服务器
const express = require('express');
const bodyParser = require('body-parser');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// 创建 Express 应用
const app = express();
const PORT = process.env.PORT || 5002;

// 确保数据目录存在
const dataDir = path.join(__dirname, 'data');
if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
    console.log(`创建数据目录: ${dataDir}`);
}

// 交易安全限制配置
const SAFETY_LIMITS = {
    maxProfit: 2000.0,              // 最大允许利润金额(USDC)
    maxLevel: 5,                  // 最大允许买入级别
    allowedTokenIds: [],          // 允许的tokenId列表 (空数组表示不限制)
    enableSafetyChecks: true      // 是否启用安全检查
};

// 中间件
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// 安全检查函数
const performSafetyChecks = (profit, level, tokenid) => {
    if (!SAFETY_LIMITS.enableSafetyChecks) {
        console.log('安全检查已禁用');
        return { pass: true };
    }
    
    // 检查利润限制
    if (parseFloat(profit) > SAFETY_LIMITS.maxProfit) {
        return {
            pass: false,
            reason: `利润金额 ${profit} USDC 超过安全限制 ${SAFETY_LIMITS.maxProfit} USDC`
        };
    }
    
    // 检查级别限制
    if (parseInt(level) > SAFETY_LIMITS.maxLevel) {
        return {
            pass: false,
            reason: `买入级别 ${level} 超过安全限制 ${SAFETY_LIMITS.maxLevel}`
        };
    }
    
    // 检查tokenId限制(如果有配置)
    if (SAFETY_LIMITS.allowedTokenIds.length > 0 && !SAFETY_LIMITS.allowedTokenIds.includes(tokenid)) {
        return {
            pass: false,
            reason: `TokenID ${tokenid} 不在允许列表中`
        };
    }
    
    return { pass: true };
};

// 执行 Python 脚本的函数
const executePythonScript = (scriptName, args) => {
    return new Promise((resolve, reject) => {
        console.log(`执行脚本: ${scriptName} 参数: ${args.join(' ')}`);
        
        const pythonProcess = spawn('python3.12', [scriptName, ...args]);
        
        let output = '';
        let errorOutput = '';
        
        // 收集标准输出
        pythonProcess.stdout.on('data', (data) => {
            const dataStr = data.toString();
            output += dataStr;
            console.log(`Python输出: ${dataStr}`);
        });
        
        // 收集错误输出
        pythonProcess.stderr.on('data', (data) => {
            const dataStr = data.toString();
            errorOutput += dataStr;
            console.error(`Python错误: ${dataStr}`);
        });
        
        // 设置超时检测(10分钟)
        const timeout = setTimeout(() => {
            pythonProcess.kill();
            reject({
                success: false,
                error: '脚本执行超时(10分钟)',
                output
            });
        }, 10 * 60 * 1000);
        
        // 处理结束事件
        pythonProcess.on('close', (code) => {
            clearTimeout(timeout);
            console.log(`Python进程退出，代码: ${code}`);
            
            if (code === 0) {
                resolve({
                    success: true,
                    output
                });
            } else {
                reject({
                    success: false,
                    error: errorOutput || `进程退出代码 ${code}`,
                    output
                });
            }
        });
        
        pythonProcess.on('error', (err) => {
            clearTimeout(timeout);
            reject({
                success: false,
                error: `启动进程错误: ${err.message}`,
                output
            });
        });
    });
};

// 记录请求到文件
const logRequestToFile = (req) => {
    const logFile = path.join(dataDir, 'webhook_requests.log');
    const timestamp = new Date().toISOString();
    const logEntry = `${timestamp} - ${JSON.stringify(req.body, null, 2)}\n\n`;
    
    fs.appendFileSync(logFile, logEntry);
    console.log(`请求已记录到: ${logFile}`);
};

// Webhook 接收端点
app.post('/webhook', async (req, res) => {
    // 获取请求体内容
    const { profit, level, tokenid } = req.body;
    
    // 打印收到的信息到终端
    console.log('收到 Webhook 请求:');
    console.log('profit:', profit);
    console.log('level:', level);
    console.log('tokenid:', tokenid);
    console.log('完整请求体:', JSON.stringify(req.body, null, 2));
    console.log('\n⚠️ 注意: 当前配置为执行真实交易，不是干运行模式 ⚠️\n');
    
    // 记录请求到文件
    logRequestToFile(req);
    
    // 验证必要的参数
    if (!profit || level === undefined || !tokenid) {
        return res.status(400).json({
            success: false,
            message: '缺少必要参数: profit, level 或 tokenid'
        });
    }
    
    // 执行安全检查
    const safetyCheck = performSafetyChecks(profit, level, tokenid);
    if (!safetyCheck.pass) {
        console.error(`安全检查失败: ${safetyCheck.reason}`);
        return res.status(403).json({
            success: false,
            message: '安全检查失败',
            reason: safetyCheck.reason
        });
    }
    
    try {
        // 根据 level 决定执行哪个脚本
        let scriptName, args;
        
        if (parseInt(level) === 0) {
            // 执行初始买入
            scriptName = 'execute_initial_buy.py';
            args = [
                tokenid,
                profit.toString(),
                '--market-name', 'BTC',
                '--data-dir', dataDir
            ];
            
            console.log(`执行初始买入脚本: ${scriptName} (真实交易模式)`);
        } else {
            // 执行后续级别买入
            scriptName = 'execute_next_buy.py';
            args = [
                tokenid,
                '--level', level.toString(),
                '--profit', profit.toString(),
                '--auto-confirm',
                '--data-dir', dataDir
            ];
            
            console.log(`执行后续级别买入脚本: ${scriptName} (真实交易模式)`);
        }
        
        // 执行 Python 脚本
        const result = await executePythonScript(scriptName, args);
        
        // 创建响应记录
        const responseData = {
            success: true,
            message: '已收到请求并处理',
            script_executed: scriptName,
            script_result: result.success ? '执行成功' : '执行失败',
            parameters: {
                tokenid: tokenid,
                profit: profit,
                level: level
            },
            mode: '真实交易',
            timestamp: new Date().toISOString()
        };
        
        // 保存响应记录
        const responseFile = path.join(dataDir, 'webhook_last_response.json');
        fs.writeFileSync(responseFile, JSON.stringify(responseData, null, 2));
        
        // 返回成功响应
        res.status(200).json(responseData);
    } catch (error) {
        console.error('执行脚本错误:', error);
        
        const errorResponse = {
            success: false,
            message: '执行脚本时出错',
            error: error.error || '未知错误',
            parameters: {
                tokenid: tokenid,
                profit: profit,
                level: level
            },
            mode: '真实交易',
            timestamp: new Date().toISOString()
        };
        
        // 保存错误响应记录
        const errorFile = path.join(dataDir, 'webhook_last_error.json');
        fs.writeFileSync(errorFile, JSON.stringify(errorResponse, null, 2));
        
        res.status(500).json(errorResponse);
    }
});

// 状态端点
app.get('/status', (req, res) => {
    const statusData = {
        server: '运行中',
        mode: '真实交易',
        safety_limits: SAFETY_LIMITS,
        timestamp: new Date().toISOString()
    };
    
    res.json(statusData);
});

// 根路由
app.get('/', (req, res) => {
    res.send('Polymarket Webhook 服务器正在运行 (真实交易模式)');
});

// 启动服务器
app.listen(PORT, () => {
    console.log(`Webhook 服务器运行在端口 ${PORT} (真实交易模式)`);
    console.log(`访问 http://localhost:${PORT} 查看服务器状态`);
    console.log(`POST 请求发送至 http://localhost:${PORT}/webhook`);
    console.log(`\n⚠️ 警告: 服务器配置为执行真实交易! ⚠️\n`);
}); 