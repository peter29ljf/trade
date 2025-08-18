#!/usr/bin/env python3.12
import os
import sys
import argparse
import urllib3
from dotenv import load_dotenv

# 设置项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
print(f"项目根目录: {PROJECT_ROOT}")

# 确保项目根目录在Python路径中
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
    print(f"添加根目录到Python路径: {PROJECT_ROOT}")

# 添加py-clob-client目录到Python路径
PY_CLOB_CLIENT_DIR = os.path.join(PROJECT_ROOT, "py-clob-client")
if os.path.exists(PY_CLOB_CLIENT_DIR) and PY_CLOB_CLIENT_DIR not in sys.path:
    sys.path.append(PY_CLOB_CLIENT_DIR)
    print(f"添加模块路径: {PY_CLOB_CLIENT_DIR}")

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 导入py-clob-client相关模块
try:
    from py_clob_client.client import ClobClient
    from py_clob_client.clob_types import ApiCreds, MarketOrderArgs, OrderType
    from py_clob_client.order_builder.constants import SELL
    print("成功导入py-clob-client模块")
except ImportError as e:
    print(f"导入py-clob-client模块失败: {str(e)}")
    print("尝试使用备用导入方式...")
    try:
        # 尝试直接导入子模块
        sys.path.append(os.path.join(PY_CLOB_CLIENT_DIR, "py_clob_client"))
        from client import ClobClient
        from clob_types import ApiCreds, MarketOrderArgs, OrderType
        from order_builder.constants import SELL
        print("使用备用方式成功导入py-clob-client模块")
    except ImportError as e:
        print(f"备用导入方式也失败: {str(e)}")
        sys.exit(1)

def execute_market_sell(token_id, amount, host=None):
    """
    执行市场卖单
    
    Args:
        token_id: 代币ID
        amount: 要卖出的shares数量
        host: API主机地址(可选)
    
    Returns:
        订单响应
    """
    # 读取环境变量
    clob_host = host if host else os.getenv("CLOB_HOST")
    private_key = os.getenv("PRIVATE_KEY")
    
    # 设置API凭据
    creds = ApiCreds(
        api_key=os.getenv("CLOB_API_KEY"),
        api_secret=os.getenv("CLOB_SECRET"),
        api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
    )
    
    # 确保代理设置正确应用
    http_proxy = os.getenv("HTTP_PROXY")
    https_proxy = os.getenv("HTTPS_PROXY")
    
    if http_proxy and https_proxy:
        # 设置环境变量以便全局使用
        os.environ['HTTP_PROXY'] = http_proxy
        os.environ['HTTPS_PROXY'] = https_proxy
        
        # 打印代理设置
        print(f"使用HTTP代理: {http_proxy}")
        print(f"使用HTTPS代理: {https_proxy}")
    
    print(f"正在初始化Polymarket客户端...")
    print(f"主机: {clob_host}")
    
    try:
        # 初始化客户端
        chain_id = 137  # Polygon Mainnet
        # 资金钱包地址
        funder_wallet = os.getenv("WALLET_ADDRESS")
        print(f"使用资金钱包: {funder_wallet}")
        
        # 尝试不使用API凭据，只使用L1认证
        client = ClobClient(
            clob_host, 
            key=private_key,
            chain_id=chain_id, 
            creds=creds,  # 使用API凭据
            funder=funder_wallet,  # 指定提供资金的钱包地址
            signature_type=1  # 使用Email/Magic账户关联的签名类型
        )
        
        print(f"正在创建市场卖单...")
        print(f"卖出数量: {amount:.4f} shares")
        
        # 创建卖单参数
        order_args = MarketOrderArgs(
            token_id=token_id,
            amount=float(amount),
            side=SELL,
        )
        
        # 创建并签名订单
        signed_order = client.create_market_order(order_args)
        
        print(f"正在提交FOK卖单...")
        
        # 发送FOK卖单
        resp = client.post_order(signed_order, orderType=OrderType.FOK)
        
        print(f"订单响应:")
        print(resp)
        
        if resp.get("success") == True:
            print(f"订单执行成功!")
            print(f"订单ID: {resp.get('orderID')}")
            print(f"状态: {resp.get('status')}")
            print(f"卖出数量: {resp.get('makingAmount')}")
            print(f"获得金额: {resp.get('takingAmount')}")
            if 'transactionsHashes' in resp:
                print(f"交易哈希: {resp.get('transactionsHashes')}")
        else:
            error_msg = resp.get("errorMsg", resp.get("error", "未知错误"))
            print(f"订单执行失败: {error_msg}")
        
        return resp
    except Exception as e:
        import traceback
        print(f"执行市场卖单时出错: {str(e)}")
        traceback.print_exc()
        return {"error": str(e)}

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="执行Polymarket市场卖单")
    parser.add_argument("token_id", help="代币ID")
    parser.add_argument("amount", type=float, help="要卖出的shares数量")
    parser.add_argument("--host", help="API主机地址")
    parser.add_argument("--env-file", help=".env文件路径")
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_arguments()
    
    # 加载环境变量
    env_file = args.env_file if args.env_file else ".env"
    load_dotenv(env_file)
    
    print(f"=== Polymarket 市场卖单 ===")
    print(f"代币ID: {args.token_id}")
    print(f"卖出数量: {args.amount} shares")
    
    # 执行市场卖单
    result = execute_market_sell(args.token_id, args.amount, args.host)
    
    if "error" in result:
        print(f"卖单执行失败: {result.get('error')}")
    else:
        print(f"卖单执行完成!")
    
    print(f"完成!")

if __name__ == "__main__":
    print(f"=== Polymarket 卖单程序 ===")
    main() 