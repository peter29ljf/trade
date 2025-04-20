#!/usr/bin/env python3.12
# -*- coding: utf-8 -*-
"""
execute_initial_buy.py - Polymarket初始买入执行脚本

该脚本自动化执行初始买入的完整流程，包括：
1. 查询当前市场价格
2. 计算最优买入数量
3. 执行市场买单
4. 记录交易信息到webhook_record.json

使用方法:
    python execute_initial_buy.py <token_id> <profit> [--host HOST] [--env-file ENV_FILE]

参数:
    token_id: 代币ID
    profit: 目标利润(USDC)
    --host: API主机地址(可选)
    --env-file: 环境变量文件路径(可选)
"""

import os
import sys
import argparse
import urllib3
from dotenv import load_dotenv
import uuid
import json
import time

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

# 导入自定义模块
try:
    # 导入自定义工具和核心模块
    from check_price import get_token_price, display_price_info
    from math_utils import calculate_initial_amount
    
    # 由于无法直接导入market_buy_order，先跳过此模块，仅在干运行模式使用
    # 实际交易时需要确保此模块存在
    if not "--dry-run" in sys.argv:
        print("警告: 实际执行交易需要market_buy_order模块")
except ImportError as e:
    print(f"错误: 无法导入必要模块 - {str(e)}")
    print("请确保已安装所有依赖项: pip install -r requirements.txt")
    sys.exit(1)

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="执行Polymarket初始买入")
    parser.add_argument("token_id", help="代币ID")
    parser.add_argument("profit", type=float, help="目标利润(USDC)")
    parser.add_argument("--host", help="API主机地址")
    parser.add_argument("--env-file", help=".env文件路径")
    parser.add_argument("--dry-run", action="store_true", help="仅计算，不执行实际交易")
    parser.add_argument("--market-name", help="市场名称")
    parser.add_argument("--data-dir", help="数据目录路径")
    return parser.parse_args()

def execute_initial_buy_process(token_id, profit, host=None, env_file=None, dry_run=True, market_name=None, data_dir=None):
    """
    执行初始买入流程
    :param token_id: 代币ID
    :param profit: 目标利润（USDC）
    :param host: API主机地址
    :param env_file: 环境变量文件
    :param dry_run: 是否为模拟运行（不执行实际交易）
    :param market_name: 市场名称
    :param data_dir: 数据目录路径
    :return: 成功返回True，失败返回False
    """
    print("\n======== 执行初始买入流程 ========")
    print(f"接收参数: token_id={token_id}, profit={profit}")
    
    try:
        # 获取当前市场价格
        price_info = get_token_price(token_id, host=host)
        if not price_info or 'lowest_ask' not in price_info:
            print(f"错误: 无法获取代币 {token_id} 的价格信息")
            return False
            
        # 修复: 处理 lowest_ask 可能是浮点数的情况
        lowest_ask = price_info['lowest_ask']
        if isinstance(lowest_ask, dict):
            market_price = lowest_ask.get('price', 0)
        else:
            # 如果 lowest_ask 直接是浮点数
            market_price = lowest_ask
            
        print(f"当前市场价格: {market_price:.4f} USDC")
        
        # 计算初始买入金额(USDC)
        amount = calculate_initial_amount(market_price, profit)
        print(f"计算得出的买入金额: {amount:.4f} USDC")
        
        # 如果是干运行模式，则不执行实际交易
        if dry_run:
            print("\n[干运行模式] 不执行实际交易")
            
            # 创建测试交易记录
            if market_name is None:
                market_name = f"Market-{token_id[-6:]}"  # 使用代币ID后6位作为市场名称
            
            # 如果指定了数据目录，确保目录存在
            if data_dir and not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
                print(f"创建数据目录: {data_dir}")
            
            # 生成唯一订单ID
            order_id = f"dry-run-{uuid.uuid4().hex[:8]}"
            print(f"创建测试订单ID: {order_id}")
            
            # 保存一份简单的记录到data目录
            if data_dir:
                simple_record = {
                    "trades": {
                        "pre_totalamount": amount,
                        "buy_records": {
                            "token_id": token_id,
                            "profit": profit,
                            "price": market_price,
                            "amount": amount,
                            "level": 0,
                            "timestamp": int(time.time())
                        }
                    }
                }
                
                simple_record_file = os.path.join(data_dir, "webhook_record.json")
                
                # 清理旧记录文件
                if os.path.exists(simple_record_file):
                    print(f"清理旧记录文件: {simple_record_file}")
                    # 方法1: 直接删除文件重新创建
                    # os.remove(simple_record_file)
                    
                    # 方法2: 清空文件内容
                    with open(simple_record_file, 'w') as f:
                        f.truncate(0)
                
                # 写入新记录
                with open(simple_record_file, 'w') as f:
                    json.dump(simple_record, f, indent=2)
                print(f"简易记录已保存到: {simple_record_file}")
            
            return True
            
        # 直接执行市场买入，无需用户确认
        print("\n直接执行市场买入订单...")
        if market_name is None:
            market_name = f"Market-{token_id[-6:]}"  # 使用代币ID后6位作为市场名称
            
        # 确保市场买入模块已导入
        if "execute_market_buy" not in globals():
            try:
                # 尝试通过绝对路径导入市场买入模块
                market_buy_order_path = os.path.join(PROJECT_ROOT, "market_buy_order.py")
                if os.path.exists(market_buy_order_path):
                    print(f"找到market_buy_order.py: {market_buy_order_path}")
                    
                    # 使用importlib动态导入模块
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("market_buy_order", market_buy_order_path)
                    market_buy_order = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(market_buy_order)
                    execute_market_buy = market_buy_order.execute_market_buy
                    print("已成功导入market_buy_order模块")
                else:
                    # 如果找不到文件，则尝试常规导入
                    print("未找到market_buy_order.py文件，尝试常规导入...")
                    from market_buy_order import execute_market_buy
            except ImportError as e:
                print(f"错误: 无法导入market_buy_order模块，无法执行实际交易 - {str(e)}")
                print("请确保market_buy_order.py在当前目录或PYTHONPATH中")
                sys.exit(1)
        
        # 使用market_buy_order模块执行买入并自动记录交易
        result = execute_market_buy(
            token_id, 
            amount, 
            host=host, 
            level=0,  # 初始买入为0级别
            profit=profit  # 传递目标利润值
        )
        
        if result and result.get("success") == True:
            order_id = result.get('orderID')
            print(f"买入成功! 订单ID: {order_id}")
            
            # 正确处理字符串类型的数值
            taking_amount = result.get('takingAmount')
            if isinstance(taking_amount, str):
                taking_amount = float(taking_amount)
            
            # 保存记录到webhook_record.json
            if data_dir:
                simple_record = {
                    "trades": {
                        "pre_totalamount": amount,
                        "buy_records": {
                            "token_id": token_id,
                            "profit": profit,
                            "price": market_price,
                            "amount": amount,
                            "level": 0,
                            "timestamp": int(time.time())
                        }
                    }
                }
                
                simple_record_file = os.path.join(data_dir, "webhook_record.json")
                
                # 清理旧记录文件
                if os.path.exists(simple_record_file):
                    print(f"清理旧记录文件: {simple_record_file}")
                    with open(simple_record_file, 'w') as f:
                        f.truncate(0)
                
                # 写入新记录
                with open(simple_record_file, 'w') as f:
                    json.dump(simple_record, f, indent=2)
                print(f"简易记录已保存到: {simple_record_file}")
                
            print(f"支付金额: {taking_amount:.4f} USDC")
            return True
        else:
            error_msg = result.get("errorMsg", result.get("error", "未知错误")) if result else "API请求失败"
            print(f"买入失败: {error_msg}")
            return False
            
    except Exception as e:
        print(f"执行初始买入过程时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    args = parse_arguments()
    
    print("收到参数:")
    print(f"- token_id: {args.token_id}")
    print(f"- profit: {args.profit}")
    print(f"- market_name: {args.market_name or '未指定'}")
    print(f"- dry_run: {args.dry_run}")
    
    # 加载环境变量
    if args.env_file:
        load_dotenv(args.env_file)
    else:
        load_dotenv()
    
    # 设置数据目录
    data_dir = args.data_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
        print(f"创建数据目录: {data_dir}")

    try:
        # 执行初始买入流程
        result = execute_initial_buy_process(
            token_id=args.token_id,
            profit=args.profit,
            host=args.host,
            env_file=args.env_file,
            dry_run=args.dry_run,
            market_name=args.market_name,
            data_dir=data_dir
        )
        
        if result:
            print("\n✅ 初始买入流程执行成功")
            sys.exit(0)
        else:
            print("\n❌ 初始买入流程执行失败")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n发生未知错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    print(f"=== Polymarket 初始买入执行工具 ===")
    main() 