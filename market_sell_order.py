#!/usr/bin/env python3.12
import os
import json
import time
from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrderType, MarketOrderArgs, BalanceAllowanceParams, AssetType
from py_clob_client.order_builder.constants import BUY, SELL
from pprint import pprint

# 加载环境变量
load_dotenv()

def main():
    """
    使用 py-clob-client 库创建和提交市价卖单
    """
    # 读取环境变量
    host = os.getenv("CLOB_HOST")
    
    # 设置私钥 (L1认证)
    private_key = "301638e633936d355596b6335e40b2dac3c4e01464565a27b7c5d45aef410114"
    
    # 设置API凭据 (L2认证)
    api_creds = ApiCreds(
        api_key=os.getenv("CLOB_API_KEY"),
        api_secret=os.getenv("CLOB_SECRET"),
        api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
    )
    
    print("正在初始化 Polymarket 客户端...")
    
    # 真正持有资金的地址
    actual_funding_address = "0xCE1001c32c78b62348Ba0EE9d21238F1Fe0b51d4"
    
    # 初始化 ClobClient
    chain_id = 137  # Polygon Mainnet
    
    # 设置签名类型
    # 0: EOA (普通钱包)
    # 1: POLY_PROXY (Polymarket代理钱包)
    # 2: POLY_GNOSIS_SAFE (Polymarket Gnosis安全钱包)
    signature_type = 1  # POLY_PROXY类型
    
    # 使用实际持仓地址作为funder参数
    client = ClobClient(
        host, 
        key=private_key, 
        chain_id=chain_id, 
        signature_type=signature_type,
        funder=actual_funding_address  # 指定实际持有资金的地址
    )
    client.set_api_creds(api_creds)
    
    # 显示基本信息
    print("\n基本信息:")
    print(f"签名地址: {client.get_address()}")
    print(f"资金地址: {actual_funding_address}")
    print(f"签名类型: {signature_type} (1=POLY_PROXY, 2=POLY_GNOSIS_SAFE)")
    print(f"Polymarket Exchange 地址: {client.get_exchange_address()}")
    print(f"Collateral 地址: {client.get_collateral_address()}")
    print(f"Conditional 地址: {client.get_conditional_address()}")
    
    # 检查服务器连接
    print("\n检查服务器连接...")
    server_time = client.get_server_time()
    print(f"服务器时间: {server_time}")
    
    # 构建订单参数
    token_id = "20506045937918217025865257873797843323032020594282910234400200695646887456893"
    order_amount = 20.0  # 卖出20个shares
    order_side = SELL    # 卖单
    
    # 检查授权状态
    print("\n检查授权状态...")
    try:
        # 检查条件代币授权
        print(f"检查条件代币授权 (Token ID: {token_id})...")
        token_info = client.get_balance_allowance(
            params=BalanceAllowanceParams(
                asset_type=AssetType.CONDITIONAL,
                token_id=token_id
            )
        )
        print("条件代币授权信息:")
        pprint(token_info)
        
        if float(token_info.get('balance', '0')) < order_amount:
            print(f"\n警告：您的账户没有足够的条件代币余额！需要至少 {order_amount} 个代币。")
            print(f"当前余额: {token_info.get('balance', '0')}")
            print("请先获取足够的条件代币。")
            print(f"资金地址: {actual_funding_address}")
            return
        
        token_allowance = float(token_info.get('allowances', {}).get(client.get_exchange_address(), '0'))
        if token_allowance < order_amount:
            # 设置条件代币授权
            print("\n设置条件代币授权...")
            update_result = client.update_balance_allowance(
                params=BalanceAllowanceParams(
                    asset_type=AssetType.CONDITIONAL,
                    token_id=token_id
                )
            )
            print("条件代币授权更新结果:")
            pprint(update_result)
            
            # 等待授权生效
            print("\n等待授权生效...")
            time.sleep(20)  # 等待20秒让区块链确认交易
            
            # 重新检查授权
            print("重新检查条件代币授权...")
            updated_token = client.get_balance_allowance(
                params=BalanceAllowanceParams(
                    asset_type=AssetType.CONDITIONAL,
                    token_id=token_id
                )
            )
            print("更新后的条件代币授权信息:")
            pprint(updated_token)
    except Exception as e:
        print(f"检查或设置授权时出错: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 获取市场价格参考
    try:
        print("\n获取市场价格信息...")
        price_info = client.get_price(token_id=token_id, side="buy")  # 查询买方价格作为卖出参考
        print("市场价格信息:")
        pprint(price_info)
        market_price = float(price_info.get('price', 0))
        if market_price <= 0:
            print("无法获取有效的市场价格，可能没有足够的流动性。")
            return
        print(f"当前市场价格: {market_price}")
    except Exception as e:
        print(f"获取市场价格时出错: {e}")
        market_price = None  # 如果无法获取价格，让系统自动决定
    
    print("\n正在创建市价卖单...")
    
    # 创建市价订单参数
    order_args = MarketOrderArgs(
        token_id=token_id,
        amount=order_amount,  # 卖出20个shares的数量
        side=order_side,      # 卖单
        price=market_price,   # 市场价格，可能会被自动调整
        taker="0x0000000000000000000000000000000000000000",  # 任何人都可以接受订单
        fee_rate_bps=0,       # 无费用
    )
    
    # 创建并签名订单
    signed_order = client.create_market_order(order_args)
    
    print("订单详情:")
    order_dict = signed_order.dict()
    pprint(order_dict)
    
    # 将订单转换为 JSON 格式
    order_json = json.dumps(order_dict)
    print("\n订单 JSON:")
    print(order_json)
    
    print("\n正在提交 FOK 市价卖单...")
    
    # 提交订单
    try:
        # 使用 client.post_order 方法提交订单
        # OrderType.FOK = 0 (Fill-Or-Kill)：要么全部成交，要么全部取消
        response = client.post_order(signed_order, OrderType.FOK)
        
        print("订单提交响应:")
        pprint(response)
        
        if "success" in response and response["success"] == True:
            print("\n订单提交成功!")
            print(f"订单ID: {response.get('orderID', 'N/A')}")
            print(f"订单状态: {response.get('status', 'N/A')}")
            
            # 如果有成交金额信息
            if response.get('makingAmount') or response.get('takingAmount'):
                print(f"成交maker金额: {response.get('makingAmount', 'N/A')}")
                print(f"成交taker金额: {response.get('takingAmount', 'N/A')}")
        else:
            print("\n订单提交失败:", response.get("errorMsg", "未知错误"))
    except Exception as e:
        print(f"\n提交订单时出错: {e}")
    
    print("完成!")

if __name__ == "__main__":
    print("=== Polymarket 市价卖单程序 ===")
    main() 