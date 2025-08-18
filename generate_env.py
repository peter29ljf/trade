#!/root/poly/venv/bin/python3
import os
import sys
import secrets

# 添加py-clob-client到路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PY_CLOB_CLIENT_DIR = os.path.join(PROJECT_ROOT, "py-clob-client")
if os.path.exists(PY_CLOB_CLIENT_DIR) and PY_CLOB_CLIENT_DIR not in sys.path:
    sys.path.append(PY_CLOB_CLIENT_DIR)

def derive_api_credentials(private_key):
    """使用私钥派生正确的API凭据"""
    try:
        from py_clob_client.client import ClobClient
        
        host = 'https://clob.polymarket.com'
        chain_id = 137  # Polygon Mainnet
        client = ClobClient(host, key=private_key, chain_id=chain_id)
        
        print("正在派生API凭据...")
        creds = client.derive_api_key()
        
        return creds.api_key, creds.api_secret, creds.api_passphrase
    except Exception as e:
        print(f"派生API凭据失败: {e}")
        print("将使用随机生成的凭据（可能需要手动更新）")
        return generate_random_api_credentials()

def generate_random_api_credentials():
    """生成随机API凭据（备用方案）"""
    api_key = str(secrets.token_hex(16))[:8] + '-' + str(secrets.token_hex(16))[:4] + '-' + str(secrets.token_hex(16))[:4] + '-' + str(secrets.token_hex(16))[:4] + '-' + str(secrets.token_hex(16))[:12]
    # 生成正确的base64格式的secret，确保没有特殊字符
    secret_key = secrets.token_hex(32)  # 使用hex格式，然后转换为base64
    pass_phrase = secrets.token_hex(32)
    return api_key, secret_key, pass_phrase

def generate_env_file(private_key, wallet_address):
    
    api_key, secret_key, pass_phrase = derive_api_credentials(private_key)
    
    env_content = f"""# API 凭据
CLOB_API_KEY={api_key}
CLOB_SECRET={secret_key}
CLOB_PASS_PHRASE={pass_phrase}
PRIVATE_KEY={private_key.replace('0x', '')}
WALLET_ADDRESS={wallet_address}

# Polymarket 节点
CLOB_HOST=https://clob.polymarket.com

# 代理设置
HTTP_PROXY=
HTTPS_PROXY=
NO_PROXY=localhost,127.0.0.1

# 交易配置
# 最大投资额度(USDC)
MAX_INVESTMENT=1000
# 最大买入级别数
MAX_LEVELS=10

# WebSocket配置
WEBSOCKET_PORT=6001
WEBHOOK_SECRET=your_webhook_secret
WEBHOOK_HOST=http://localhost

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=./logs/trading.log

# 环境配置
ENV=development
PORT=5001

# CORS设置
CORS_ORIGINS=http://localhost:3000

# Polymarket API配置
POLYMARKET_API_KEY=
POLYMARKET_API_SECRET=
POLYMARKET_API_PASSPHRASE= 
"""
    
    filename = f".env.{wallet_address[-6:]}"
    filepath = os.path.join('/root/poly', filename)
    
    with open(filepath, 'w') as f:
        f.write(env_content)
    
    print(f"✅ 成功生成环境配置文件: {filepath}")
    print(f"📝 钱包地址: {wallet_address}")
    print(f"🔐 私钥: {private_key.replace('0x', '')}")
    print(f"\n使用方法:")
    print(f"1. 将 {filename} 复制为 .env 文件: cp {filepath} /root/poly/.env")
    print(f"2. 或者直接使用: export $(cat {filepath} | xargs)")
    
    return True

def main():
    print("=== Polymarket 环境配置生成器 ===\n")
    
    # 检查命令行参数
    if len(sys.argv) == 3:
        private_key = sys.argv[1].strip()
        wallet_address = sys.argv[2].strip()
        print(f"使用命令行参数:")
        print(f"私钥: {private_key[:8]}...")
        print(f"钱包地址: {wallet_address}")
    else:
        private_key = input("请输入私钥 (可以带或不带 0x 前缀): ").strip()
        wallet_address = input("请输入钱包地址: ").strip()
    
    if not private_key:
        print("错误：私钥不能为空")
        sys.exit(1)
    
    if not wallet_address:
        print("错误：钱包地址不能为空")
        sys.exit(1)
    
    if len(private_key.replace('0x', '')) != 64:
        print("错误：私钥长度不正确，应该是64个十六进制字符")
        sys.exit(1)
    
    if not wallet_address.startswith('0x') or len(wallet_address) != 42:
        print("错误：钱包地址格式不正确")
        sys.exit(1)
    
    if generate_env_file(private_key, wallet_address):
        print("\n✨ 环境配置文件生成成功！")
    else:
        print("\n❌ 生成失败")
        sys.exit(1)

if __name__ == "__main__":
    main()