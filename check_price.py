#!/usr/bin/env python3.12
# -*- coding: utf-8 -*-
"""
check_price.py - Polymarket代币价格查询工具

此工具用于查询Polymarket代币的当前市场价格，支持Python 3.12+版本。
它使用直接HTTP请求获取订单簿信息，不依赖于py-clob-client库。

使用方法:
    python check_price.py <token_id> [--host HOST] [--env-file ENV_FILE]

依赖项:
    - python-dotenv>=1.0.0
    - urllib3>=2.4.0
    - requests>=2.32.3

该工具用于查询Polymarket代币的当前市场价格，包括最低卖价、最高买价和价差信息。
通过直接HTTP请求或py-clob-client库查询Polymarket API获取订单簿数据。

使用方法：
    python check_price.py <token_id> [--host HOST] [--env-file ENV_FILE]

参数：
    token_id: 要查询的代币ID
    --host: API主机地址(可选，默认使用.env中的CLOB_HOST)
    --env-file: 环境变量文件路径(可选，默认为当前目录的.env)
"""

import os
import sys
import json
import argparse
import urllib3
import requests
from dotenv import load_dotenv
try:
    from py_clob_client.client import ClobClient
    from py_clob_client.clob_types import ApiCreds
    HAS_CLOB_CLIENT = True
except ImportError:
    HAS_CLOB_CLIENT = False

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_token_price(token_id, host=None, proxies=None, use_clob_client=False):
    """
    获取代币价格信息
    
    Args:
        token_id: 代币ID
        host: API主机地址(可选)
        proxies: 代理设置(可选)
        use_clob_client: 是否使用py-clob-client库(可选)
        
    Returns:
        包含价格信息的字典
    """
    # 初始化结果字典
    result = {
        "success": False,
        "lowest_ask": None,
        "lowest_ask_quantity": None,
        "highest_bid": None,
        "highest_bid_quantity": None,
        "spread": None,
        "spread_percentage": None,
        "asks": [],
        "bids": [],
        "error": None
    }
    
    try:
        # 设置API主机地址
        clob_host = host if host else os.getenv("CLOB_HOST", "https://clob.polymarket.com")
        
        # 设置代理
        if not proxies:
            http_proxy = os.getenv("HTTP_PROXY")
            https_proxy = os.getenv("HTTPS_PROXY")
            
            if http_proxy or https_proxy:
                proxies = {}
                if http_proxy:
                    proxies["http"] = http_proxy
                    os.environ['HTTP_PROXY'] = http_proxy
                if https_proxy:
                    proxies["https"] = https_proxy
                    os.environ['HTTPS_PROXY'] = https_proxy
                
                print(f"使用代理: HTTP={http_proxy}, HTTPS={https_proxy}")
        
        # 判断是否使用py-clob-client库
        if use_clob_client and HAS_CLOB_CLIENT:
            print(f"使用py-clob-client库获取价格信息...")
            result = get_price_with_clob_client(token_id, clob_host)
        else:
            print(f"使用HTTP请求获取价格信息...")
            result = get_price_with_http(token_id, clob_host, proxies)
        
    except Exception as e:
        import traceback
        result["error"] = f"查询价格时出错: {str(e)}"
        print(f"错误: {str(e)}")
        traceback.print_exc()
    
    return result

def get_price_with_http(token_id, host, proxies=None):
    """使用直接HTTP请求获取价格"""
    result = {
        "success": False,
        "lowest_ask": None,
        "lowest_ask_quantity": None,
        "highest_bid": None,
        "highest_bid_quantity": None,
        "spread": None,
        "spread_percentage": None,
        "asks": [],
        "bids": [],
        "error": None
    }
    
    try:
        # 构建请求URL
        book_url = f"{host}/book?token_id={token_id}"
        print(f"请求URL: {book_url}")
        
        # 发送请求
        response = requests.get(book_url, proxies=proxies)
        
        # 检查响应状态
        if response.status_code == 200:
            book_data = response.json()
            
            # 提取asks和bids数据
            asks = book_data.get("asks", [])
            bids = book_data.get("bids", [])
            
            # 处理asks (卖单)
            if asks and len(asks) > 0:
                # 排序asks (从低价到高价)
                sorted_asks = sorted(asks, key=lambda x: float(x.get("price", 0)))
                result["asks"] = sorted_asks[:5]  # 只获取前5个
                
                # 获取最低卖价
                lowest_ask = sorted_asks[0]
                result["lowest_ask"] = float(lowest_ask.get("price", 0))
                result["lowest_ask_quantity"] = float(lowest_ask.get("amount", 0))
            
            # 处理bids (买单)
            if bids and len(bids) > 0:
                # 排序bids (从高价到低价)
                sorted_bids = sorted(bids, key=lambda x: float(x.get("price", 0)), reverse=True)
                result["bids"] = sorted_bids[:5]  # 只获取前5个
                
                # 获取最高买价
                highest_bid = sorted_bids[0]
                result["highest_bid"] = float(highest_bid.get("price", 0))
                result["highest_bid_quantity"] = float(highest_bid.get("amount", 0))
            
            # 计算价差
            if result["lowest_ask"] is not None and result["highest_bid"] is not None:
                result["spread"] = round(result["lowest_ask"] - result["highest_bid"], 4)
                if result["lowest_ask"] > 0:
                    result["spread_percentage"] = round(result["spread"] / result["lowest_ask"] * 100, 2)
            
            result["success"] = True
        else:
            result["error"] = f"HTTP错误: {response.status_code}, {response.text}"
    
    except Exception as e:
        result["error"] = f"获取价格时出错: {str(e)}"
        import traceback
        traceback.print_exc()
    
    return result

def get_price_with_clob_client(token_id, host):
    """使用py-clob-client库获取价格"""
    result = {
        "success": False,
        "lowest_ask": None,
        "lowest_ask_quantity": None,
        "highest_bid": None,
        "highest_bid_quantity": None,
        "spread": None,
        "spread_percentage": None,
        "asks": [],
        "bids": [],
        "error": None
    }
    
    try:
        # 设置API凭据
        creds = ApiCreds(
            api_key=os.getenv("CLOB_API_KEY"),
            api_secret=os.getenv("CLOB_SECRET"),
            api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
        )
        
        # 初始化客户端
        chain_id = 137  # Polygon Mainnet
        client = ClobClient(host, chain_id=chain_id, creds=creds)
        
        # 获取订单簿
        book = client.get_order_book(token_id)
        
        # 处理asks和bids
        if isinstance(book, dict):
            # 处理字典格式的响应
            asks = book.get("asks", [])
            bids = book.get("bids", [])
        else:
            # 处理对象格式的响应
            asks = book.asks if hasattr(book, 'asks') else []
            bids = book.bids if hasattr(book, 'bids') else []
        
        # 处理asks (卖单)
        if asks and len(asks) > 0:
            # 获取asks列表
            result["asks"] = asks[:5]  # 只获取前5个
            
            # 获取最低卖价
            lowest_ask = asks[0]
            if isinstance(lowest_ask, dict):
                result["lowest_ask"] = float(lowest_ask.get("price", 0))
                result["lowest_ask_quantity"] = float(lowest_ask.get("amount", 0))
            else:
                result["lowest_ask"] = float(lowest_ask.price if hasattr(lowest_ask, 'price') else 0)
                result["lowest_ask_quantity"] = float(lowest_ask.amount if hasattr(lowest_ask, 'amount') else 0)
        
        # 处理bids (买单)
        if bids and len(bids) > 0:
            # 获取bids列表
            result["bids"] = bids[:5]  # 只获取前5个
            
            # 获取最高买价
            highest_bid = bids[0]
            if isinstance(highest_bid, dict):
                result["highest_bid"] = float(highest_bid.get("price", 0))
                result["highest_bid_quantity"] = float(highest_bid.get("amount", 0))
            else:
                result["highest_bid"] = float(highest_bid.price if hasattr(highest_bid, 'price') else 0)
                result["highest_bid_quantity"] = float(highest_bid.amount if hasattr(highest_bid, 'amount') else 0)
        
        # 计算价差
        if result["lowest_ask"] is not None and result["highest_bid"] is not None:
            result["spread"] = round(result["lowest_ask"] - result["highest_bid"], 4)
            if result["lowest_ask"] > 0:
                result["spread_percentage"] = round(result["spread"] / result["lowest_ask"] * 100, 2)
        
        result["success"] = True
        
    except Exception as e:
        result["error"] = f"使用py-clob-client获取价格时出错: {str(e)}"
        import traceback
        traceback.print_exc()
    
    return result

def display_price_info(result):
    """显示价格信息"""
    if result["success"]:
        print("\n======= 价格信息 =======")
        if result["lowest_ask"] is not None:
            print(f"最低卖价(Ask): {result['lowest_ask']} USDC, 数量: {result['lowest_ask_quantity']}")
        else:
            print("无可用卖单")
        
        if result["highest_bid"] is not None:
            print(f"最高买价(Bid): {result['highest_bid']} USDC, 数量: {result['highest_bid_quantity']}")
        else:
            print("无可用买单")
        
        if result["spread"] is not None:
            print(f"价差: {result['spread']} USDC ({result['spread_percentage']}%)")
        
        # 显示卖单列表
        if result["asks"]:
            print("\n--- 卖单列表(从低到高) ---")
            for i, ask in enumerate(result["asks"]):
                if isinstance(ask, dict):
                    price = ask.get("price", "N/A")
                    amount = ask.get("amount", "N/A")
                else:
                    price = ask.price if hasattr(ask, 'price') else "N/A"
                    amount = ask.amount if hasattr(ask, 'amount') else "N/A"
                print(f"{i+1}. 价格: {price} USDC, 数量: {amount}")
        
        # 显示买单列表
        if result["bids"]:
            print("\n--- 买单列表(从高到低) ---")
            for i, bid in enumerate(result["bids"]):
                if isinstance(bid, dict):
                    price = bid.get("price", "N/A")
                    amount = bid.get("amount", "N/A")
                else:
                    price = bid.price if hasattr(bid, 'price') else "N/A"
                    amount = bid.amount if hasattr(bid, 'amount') else "N/A"
                print(f"{i+1}. 价格: {price} USDC, 数量: {amount}")
    else:
        print("\n======= 查询失败 =======")
        print(f"错误: {result['error']}")

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="查询Polymarket代币价格")
    parser.add_argument("token_id", help="代币ID")
    parser.add_argument("--host", help="API主机地址")
    parser.add_argument("--env-file", help=".env文件路径")
    parser.add_argument("--clob-client", action="store_true", help="使用py-clob-client库")
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_arguments()
    
    # 加载环境变量
    env_file = args.env_file if args.env_file else ".env"
    load_dotenv(env_file)
    
    print(f"=== Polymarket 价格查询 ===")
    print(f"代币ID: {args.token_id}")
    
    # 获取价格信息
    result = get_token_price(args.token_id, args.host, use_clob_client=args.clob_client)
    
    # 显示价格信息
    display_price_info(result)
    
    return 0 if result["success"] else 1

if __name__ == "__main__":
    sys.exit(main()) 