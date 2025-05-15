#!/usr/bin/env python3.12
# -*- coding: utf-8 -*-
"""
execute_next_buy.py - Polymarket后续级别买入执行脚本

该脚本自动化执行后续级别买入的完整流程，支持Python 3.12+版本。
包括：
1. 接收token_id、level和profit参数
2. 查询当前市场价格
3. 计算最优买入数量
4. 执行市场买单

使用方法:
    python execute_next_buy.py <token_id> --level <LEVEL> [--dry-run] [--auto-confirm]

参数:
    token_id: 代币ID
    --level, -l: 指定买入级别
    --profit: 目标利润(USDC)，从webhook直接传递
    --dry-run: 仅计算，不执行实际交易
    --auto-confirm: 自动确认交易，无需手动输入
"""

import os
import sys
import argparse
import urllib3
import importlib.util
from dotenv import load_dotenv
import uuid
import time
import json

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 设置项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
print(f"项目根目录: {PROJECT_ROOT}")

# 确保项目根目录在Python路径中
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 添加py-clob-client目录到Python路径
PY_CLOB_CLIENT_DIR = os.path.join(PROJECT_ROOT, "py-clob-client")
if os.path.exists(PY_CLOB_CLIENT_DIR) and PY_CLOB_CLIENT_DIR not in sys.path:
    sys.path.append(PY_CLOB_CLIENT_DIR)
    print(f"添加模块路径: {PY_CLOB_CLIENT_DIR}")

# 通过文件路径直接导入market_buy_order模块
market_buy_order_path = os.path.join(PROJECT_ROOT, "market_buy_order.py")
if os.path.exists(market_buy_order_path):
    print(f"找到market_buy_order.py: {market_buy_order_path}")
    
    # 使用importlib动态导入模块
    spec = importlib.util.spec_from_file_location("market_buy_order", market_buy_order_path)
    market_buy_order = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(market_buy_order)
    execute_market_buy = market_buy_order.execute_market_buy
    print("已成功导入market_buy_order模块")
else:
    print(f"警告: 找不到market_buy_order.py文件")

# 导入其他自定义模块
try:
    # 导入check_price模块
    from check_price import get_token_price, display_price_info
    print("已导入: check_price")
    
    # 导入math_utils模块
    from math_utils import calculate_amount_for_specific_level
    print("已导入: math_utils")
    
except ImportError as e:
    print(f"错误: 无法导入必要模块 - {str(e)}")
    print("请确保已安装所有依赖项: pip install -r requirements.txt")
    sys.exit(1)

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="执行Polymarket后续级别买入")
    parser.add_argument("token_id", help="代币ID")
    parser.add_argument("--level", "-l", type=int, required=True, help="指定买入级别")
    parser.add_argument("--profit", type=float, help="目标利润(USDC)，从webhook直接传递")
    parser.add_argument("--dry-run", action="store_true", help="仅计算，不执行实际交易")
    parser.add_argument("--auto-confirm", action="store_true", help="自动确认交易，无需手动输入")
    parser.add_argument("--host", help="API主机地址")
    parser.add_argument("--env-file", help=".env文件路径")
    parser.add_argument("--price", type=float, help="直接使用指定价格，而不是查询API")
    parser.add_argument("--data-dir", help="数据目录路径")
    return parser.parse_args()

def execute_next_buy_process(token_id, level, profit, host=None, dry_run=True, auto_confirm=False, fixed_price=None, data_dir=None):
    """
    执行后续级别买入流程
    :param token_id: 代币ID
    :param level: 指定买入级别
    :param profit: 目标利润(USDC)
    :param host: API主机地址
    :param dry_run: 是否为模拟运行（不执行实际交易）
    :param auto_confirm: 是否自动确认
    :param fixed_price: 指定固定价格，如果提供则不查询API
    :param data_dir: 数据目录路径
    :return: 成功返回True，失败返回False
    """
    print("\n======== 执行后续级别买入流程 ========")
    print(f"接收参数: token_id={token_id}, level={level}, profit={profit}")
    
    try:
        # 查询当前市场价格
        if fixed_price is not None:
            print(f"使用指定价格: {fixed_price:.4f} USDC")
            market_price = fixed_price
            price_info = {
                "lowest_ask": market_price,
                "token_id": token_id
            }
        else:
            print(f"正在查询代币ID: {token_id} 的价格信息...")
            price_info = get_token_price(token_id, host=host)
            if not price_info or 'lowest_ask' not in price_info:
                print(f"错误: 无法获取代币 {token_id} 的价格信息")
                return False
            
            lowest_ask = price_info['lowest_ask']
            # 处理lowest_ask可能是浮点数或字典的情况
            if isinstance(lowest_ask, dict):
                market_price = lowest_ask.get('price', 0)
            else:
                market_price = lowest_ask
            print(f"当前市场价格: {market_price:.4f} USDC")
        
        # 读取webhook_record.json文件获取pre_totalamount
        pre_totalamount = 0
        webhook_record_file = os.path.join(data_dir or os.path.join(PROJECT_ROOT, "data"), "webhook_record.json")
        if os.path.exists(webhook_record_file):
            try:
                with open(webhook_record_file, 'r') as f:
                    webhook_data = json.load(f)
                    if "trades" in webhook_data and "pre_totalamount" in webhook_data["trades"]:
                        pre_totalamount = webhook_data["trades"].get("pre_totalamount", 0)
                        print(f"从webhook_record.json读取到pre_totalamount: {pre_totalamount}")
            except Exception as e:
                print(f"读取webhook_record.json时出错: {str(e)}")
                print(f"将使用默认值pre_totalamount=0")
        else:
            print(f"未找到webhook_record.json文件，将使用默认值pre_totalamount=0")
        
        # 使用新的计算公式: (pre_totalamount + profit) / (1/market_price-1)
        next_amount = (pre_totalamount + profit) / (1/market_price-1)
        
        print(f"传入的目标利润: {profit:.4f} USDC")
        print(f"历史总量(pre_totalamount): {pre_totalamount:.4f}")
        print(f"买入级别: {level}")
        print(f"买入数量: {next_amount:.4f}")
        print(f"花费金额: {next_amount * market_price:.4f} USDC")
        
        # 如果是干运行模式，则不执行实际交易
        if dry_run:
            print("\n[干运行模式] 不执行实际交易")
            
            # 生成唯一订单ID
            order_id = f"dry-run-{uuid.uuid4().hex[:8]}-{level}"
            
            # 如果指定了数据目录，保存一份简单的记录
            if data_dir:
                if not os.path.exists(data_dir):
                    os.makedirs(data_dir, exist_ok=True)
                    print(f"创建数据目录: {data_dir}")
                
                # 更新webhook_record.json中的pre_totalamount
                webhook_record_file = os.path.join(data_dir, "webhook_record.json")
                new_pre_totalamount = pre_totalamount + next_amount
                
                if os.path.exists(webhook_record_file):
                    try:
                        with open(webhook_record_file, 'r') as f:
                            webhook_data = json.load(f)
                            
                        # 更新pre_totalamount值
                        webhook_data["trades"]["pre_totalamount"] = new_pre_totalamount
                        
                        # 将buy_records转换为数组（如果不是的话）
                        if "buy_records" not in webhook_data["trades"]:
                            webhook_data["trades"]["buy_records"] = []
                        elif not isinstance(webhook_data["trades"]["buy_records"], list):
                            # 如果现有的buy_records是单个记录的字典，将其转换为列表
                            current_record = webhook_data["trades"]["buy_records"]
                            webhook_data["trades"]["buy_records"] = [current_record]
                        
                        # 添加新记录
                        new_record = {
                            "token_id": token_id,
                            "profit": profit,
                            "price": market_price,
                            "amount": next_amount,
                            "level": level,
                            "timestamp": int(time.time())
                        }
                        
                        # 将新记录添加到记录列表中
                        webhook_data["trades"]["buy_records"].append(new_record)
                        
                        with open(webhook_record_file, 'w') as f:
                            json.dump(webhook_data, f, indent=2)
                            
                        print(f"已更新webhook_record.json中的pre_totalamount: {new_pre_totalamount:.4f}")
                    except Exception as e:
                        print(f"更新webhook_record.json时出错: {str(e)}")
                else:
                    # 如果文件不存在，创建新文件
                    webhook_data = {
                        "trades": {
                            "pre_totalamount": new_pre_totalamount,
                            "buy_records": [
                                {
                                    "token_id": token_id,
                                    "profit": profit,
                                    "price": market_price,
                                    "amount": next_amount,
                                    "level": level,
                                    "timestamp": int(time.time())
                                }
                            ]
                        }
                    }
                    
                    with open(webhook_record_file, 'w') as f:
                        json.dump(webhook_data, f, indent=2)
                    
                    print(f"已创建webhook_record.json并记录pre_totalamount: {new_pre_totalamount:.4f}")
            
            print(f"干运行模式完成: token_id={token_id}, level={level}")
            return True
        
        # 确认是否执行
        if not auto_confirm:
            while True:
                confirm = input("\n是否执行买入? (y/n): ").lower()
                if confirm in ('y', 'yes'):
                    break
                elif confirm in ('n', 'no'):
                    print("操作已取消")
                    return False
                else:
                    print("请输入 'y' 或 'n'")
        
        # 执行市场买入
        print("\n执行市场买单...")
        result = execute_market_buy(token_id, next_amount, host=host, level=level, profit=profit)
        
        if result and result.get('success'):
            order_id = result.get('orderID')
            making_amount = float(result.get('makingAmount', 0))
            
            print(f"买入成功! 订单ID: {order_id}")
            print(f"获得代币: {making_amount:.4f}")
            
            # 更新webhook_record.json
            try:
                # 如果指定了数据目录，保存记录
                if data_dir:
                    if not os.path.exists(data_dir):
                        os.makedirs(data_dir, exist_ok=True)
                        
                    # 更新webhook_record.json中的pre_totalamount
                    webhook_record_file = os.path.join(data_dir, "webhook_record.json")
                    new_pre_totalamount = pre_totalamount + making_amount
                    
                    if os.path.exists(webhook_record_file):
                        try:
                            with open(webhook_record_file, 'r') as f:
                                webhook_data = json.load(f)
                                
                            # 更新pre_totalamount值
                            webhook_data["trades"]["pre_totalamount"] = new_pre_totalamount
                            
                            # 将buy_records转换为数组（如果不是的话）
                            if "buy_records" not in webhook_data["trades"]:
                                webhook_data["trades"]["buy_records"] = []
                            elif not isinstance(webhook_data["trades"]["buy_records"], list):
                                # 如果现有的buy_records是单个记录的字典，将其转换为列表
                                current_record = webhook_data["trades"]["buy_records"]
                                webhook_data["trades"]["buy_records"] = [current_record]
                            
                            # 添加新记录
                            new_record = {
                                "token_id": token_id,
                                "profit": profit,
                                "price": market_price,
                                "amount": making_amount,
                                "level": level,
                                "timestamp": int(time.time())
                            }
                            
                            # 将新记录添加到记录列表中
                            webhook_data["trades"]["buy_records"].append(new_record)
                            
                            with open(webhook_record_file, 'w') as f:
                                json.dump(webhook_data, f, indent=2)
                                
                            print(f"已更新webhook_record.json中的pre_totalamount: {new_pre_totalamount:.4f}")
                        except Exception as e:
                            print(f"更新webhook_record.json时出错: {str(e)}")
                    else:
                        # 如果文件不存在，创建新文件
                        webhook_data = {
                            "trades": {
                                "pre_totalamount": new_pre_totalamount,
                                "buy_records": [
                                    {
                                        "token_id": token_id,
                                        "profit": profit,
                                        "price": market_price,
                                        "amount": making_amount,
                                        "level": level,
                                        "timestamp": int(time.time())
                                    }
                                ]
                            }
                        }
                        
                        with open(webhook_record_file, 'w') as f:
                            json.dump(webhook_data, f, indent=2)
                        
                        print(f"已创建webhook_record.json并记录pre_totalamount: {new_pre_totalamount:.4f}")
                
            except Exception as e:
                print(f"更新webhook_record时出错: {str(e)}")
                import traceback
                traceback.print_exc()
            
            return True
        else:
            error_msg = result.get("error", "未知错误") if result else "API请求失败"
            print(f"买入失败: {error_msg}")
            return False
            
    except Exception as e:
        print(f"执行后续买入过程时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    args = parse_arguments()
    
    # 打印接收到的参数
    print("收到参数:")
    print(f"- token_id: {args.token_id}")
    print(f"- level: {args.level}")
    print(f"- profit: {args.profit}")
    print(f"- dry_run: {args.dry_run}")
    
    # 加载环境变量
    if args.env_file:
        load_dotenv(args.env_file)
    else:
        load_dotenv()

    # 设置数据目录
    data_dir = args.data_dir or os.path.join(PROJECT_ROOT, "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
        print(f"创建数据目录: {data_dir}")

    try:
        # 获取参数
        token_id = args.token_id
        level = args.level
        profit = args.profit  # 从命令行参数接收profit
        
        if profit is None:
            print("警告: 未提供profit参数，将使用默认值2.0")
            profit = 2.0
        
        result = execute_next_buy_process(
            token_id=token_id,
            level=level,
            profit=profit,
            host=args.host,
            dry_run=args.dry_run,
            auto_confirm=args.auto_confirm,
            fixed_price=args.price,
            data_dir=data_dir
        )
        
        if result:
            print("\n✅ 操作成功完成")
            sys.exit(0)
        else:
            print("\n❌ 操作未能完成")
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
    print(f"=== Polymarket 后续级别买入执行工具 ===")
    main() 