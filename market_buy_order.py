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
    from py_clob_client.order_builder.constants import BUY
    print("成功导入py-clob-client模块")
except ImportError as e:
    print(f"导入py-clob-client模块失败: {str(e)}")
    print("尝试使用备用导入方式...")
    try:
        # 尝试直接导入子模块
        sys.path.append(os.path.join(PY_CLOB_CLIENT_DIR, "py_clob_client"))
        from client import ClobClient
        from clob_types import ApiCreds, MarketOrderArgs, OrderType
        from order_builder.constants import BUY
        print("使用备用方式成功导入py-clob-client模块")
    except ImportError as e:
        print(f"备用导入方式也失败: {str(e)}")
        sys.exit(1)

def execute_market_buy(token_id, amount, host=None, level=None, profit=None):
    """
    执行市场买单
    
    Args:
        token_id: 代币ID
        amount: 要投入的USDC金额
        host: API主机地址(可选)
        level: 交易级别(可选)
        profit: 目标利润(可选)
    
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
        
        client = ClobClient(
            clob_host, 
            key=private_key,
            chain_id=chain_id, 
            creds=creds,
            funder=funder_wallet,  # 指定提供资金的钱包地址
            signature_type=1  # 使用Email/Magic账户关联的签名类型
        )
        
        print(f"正在创建市场买单...")
        print(f"买入金额: {amount:.4f} USDC (由math_utils.py计算得出)")
        
        # 创建买单参数
        order_args = MarketOrderArgs(
            token_id=token_id,
            amount=float(amount),
            side=BUY,
        )
        
        # 创建并签名订单
        signed_order = client.create_market_order(order_args)
        
        print(f"正在提交FOK买单...")
        
        # 发送FOK买单
        resp = client.post_order(signed_order, orderType=OrderType.FOK)
        
        print(f"订单响应:")
        print(resp)
        
        if resp.get("success") == True:
            print(f"订单执行成功!")
            print(f"订单ID: {resp.get('orderID')}")
            print(f"状态: {resp.get('status')}")
            print(f"买入数量: {resp.get('makingAmount')}")
            print(f"花费金额: {resp.get('takingAmount')}")
            if 'transactionsHashes' in resp:
                print(f"交易哈希: {resp.get('transactionsHashes')}")
                
            # 如果提供了级别，则记录交易信息
            try:
                if level is not None and hasattr(sys.modules, 'trade_records'):
                    import trade_records
                    
                    # 提取买入金额
                    taking_amount = resp.get('takingAmount')
                    if isinstance(taking_amount, str):
                        taking_amount = float(taking_amount)
                    
                    # 获取当前市场价格（可能需要额外调用）
                    market_price = taking_amount / float(amount) if amount else 0
                    
                    # 创建交易记录
                    market_name = f"Market-{token_id[-6:]}"  # 使用代币ID后6位作为市场名称
                    trade = trade_records.create_trade(token_id, market_name, profit, market_price, amount)
                    
                    if trade:
                        print(f"交易记录已保存，ID: {trade.get('trade_id')}")
                    else:
                        print(f"警告: 无法保存交易记录")
            except Exception as e:
                print(f"记录交易信息时出错: {str(e)}")
        else:
            error_msg = resp.get("errorMsg", resp.get("error", "未知错误"))
            print(f"订单执行失败: {error_msg}")
        
        return resp
    except Exception as e:
        import traceback
        print(f"执行市场买单时出错: {str(e)}")
        traceback.print_exc()
        return {"error": str(e)}

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="执行Polymarket市场买单")
    parser.add_argument("token_id", help="代币ID")
    parser.add_argument("amount", type=float, help="要投入的USDC金额")
    parser.add_argument("--host", help="API主机地址")
    parser.add_argument("--env-file", help=".env文件路径")
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_arguments()
    
    # 加载环境变量
    env_file = args.env_file if args.env_file else ".env"
    load_dotenv(env_file)
    
    print(f"=== Polymarket 市场买单 ===")
    print(f"代币ID: {args.token_id}")
    print(f"USDC金额: {args.amount} USDC")
    
    # 执行市场买单
    result = execute_market_buy(args.token_id, args.amount, args.host)
    
    if "error" in result and "not enough balance" in str(result.get("error", "")):
        print(f"注意: 账户余额不足。这是测试环境中的预期行为。")
    
    print(f"完成!")

if __name__ == "__main__":
    print(f"=== Polymarket 交易程序 ===")
    main() 