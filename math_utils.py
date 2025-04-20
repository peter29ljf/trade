#!/usr/bin/env python3.12
# -*- coding: utf-8 -*-
"""
math_utils.py - 计算买入数量的工具函数

此模块包含计算初始买入和后续买入数量的算法，支持最多10级买入策略
"""

try:
    import trade_records
    TRADE_RECORDS_AVAILABLE = True
except ImportError:
    TRADE_RECORDS_AVAILABLE = False

def calculate_initial_amount(market_price, profit):
    """
    计算初始买入数量: AMOUNT_0 = PROFIT / (1/MARKETPRICE0 - 1)
    
    Args:
        market_price (float): 当前市场价格
        profit (float): 目标利润(USDC)
        
    Returns:
        float: 应该买入的数量
    """
    if market_price >= 1.0:
        return 0  # 当前价格>=1.0时，公式无法产生有效买入量
    
    buy_amount = profit / (1/market_price - 1)
    return buy_amount

def calculate_next_amount(previous_amounts, profit, market_price):
    """
    计算后续级别买入数量: AMOUNT_n = (AMOUNT_0 + ... + AMOUNT_n-1 + PROFIT) * MARKETPRICE_n
    
    Args:
        previous_amounts (list): 之前所有级别的买入数量列表
        profit (float): 目标利润(USDC)
        market_price (float): 当前市场价格
        
    Returns:
        float: 应该买入的数量
    """
    # 计算之前所有级别的总买入数量
    total_previous = sum(previous_amounts)
    
    # 使用正确公式计算本级别买入数量（乘以市场价格）
    buy_amount = (total_previous + profit) * market_price
    return buy_amount

def calculate_next_amount_v2(trade_id, profit, market_price):
    """
    计算后续级别买入数量: AMOUNT_n = (total_suggested_amount + PROFIT) / (1/MARKETPRICE_n)
    直接从trade_records.json中读取total_suggested_amount
    
    Args:
        trade_id (str): 交易ID，用于查找total_suggested_amount
        profit (float): 目标利润(USDC)
        market_price (float): 当前市场价格
        
    Returns:
        float: 应该买入的数量，如果交易不存在返回None
    """
    if not TRADE_RECORDS_AVAILABLE:
        return None
        
    try:
        # 获取交易记录
        trade = trade_records.get_trade_by_id(trade_id)
        if not trade:
            print(f"错误: 无法找到交易ID {trade_id}")
            return None
        
        # 直接从交易记录中获取total_suggested_amount
        # 排除level=0的记录，因为它是虚拟记录
        total_suggested_amount = 0
        if "buy_records" in trade:
            for record in trade["buy_records"]:
                # 只累加非0级记录的amount
                if record.get("level", 0) > 0:
                    total_suggested_amount += record.get("amount", 0)
        else:
            total_suggested_amount = trade.get("total_suggested_amount", 0)
        
        # 使用修正的公式计算本级别买入数量
        buy_amount = (total_suggested_amount + profit) / (1/market_price)
        
        print(f"计算买入量: ({total_suggested_amount} + {profit}) / (1/{market_price}) = {buy_amount}")
        return buy_amount
    except Exception as e:
        print(f"计算下一级别买入数量时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def get_previous_buy_amounts(trade_id):
    """
    从交易记录中获取之前所有级别的买入数量
    
    Args:
        trade_id (str): 交易ID
        
    Returns:
        list: 之前所有级别的买入数量列表
        float: 交易的目标利润
        None: 如果交易不存在或trade_records模块不可用
    """
    if not TRADE_RECORDS_AVAILABLE:
        return None, None
        
    # 获取交易记录
    trade = trade_records.get_trade_by_id(trade_id)
    if not trade:
        return None, None
        
    # 提取买入记录的数量
    buy_amounts = [record['amount'] for record in trade['buy_records']]
    target_profit = trade['target_profit']
    
    return buy_amounts, target_profit

def calculate_next_amount_for_trade(trade_id, market_price):
    """
    根据交易记录计算下一级别的买入数量
    
    Args:
        trade_id (str): 交易ID
        market_price (float): 当前市场价格
        
    Returns:
        tuple: (下一级别买入数量, 下一级别编号), 如果出错则返回(None, None)
    """
    try:
        # 获取交易记录
        trade = trade_records.get_trade_by_id(trade_id)
        if not trade:
            print(f"错误: 无法找到交易ID {trade_id}")
            return None, None
        
        # 获取当前级别和目标利润
        current_level = trade['current_level']
        next_level = current_level + 1
        profit = trade['target_profit']
        
        # 使用新的直接读取方法计算买入数量
        next_amount = calculate_next_amount_v2(trade_id, profit, market_price)
        
        return next_amount, next_level
    except Exception as e:
        print(f"计算下一级别买入数量时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

def calculate_amount_for_specific_level(trade_id, market_price, target_level, price_levels=None):
    """
    计算指定级别的买入数量，即使缺少中间级别的买入记录
    
    Args:
        trade_id (str): 交易ID
        market_price (float): 当前市场价格
        target_level (int): 目标级别
        price_levels (list, optional): 各级别价格列表，如果不提供，将使用市场价格
        
    Returns:
        float: 目标级别的建议买入数量，如果出错则返回None
    """
    try:
        # 获取交易记录
        trade = trade_records.get_trade_by_id(trade_id)
        if not trade:
            print(f"错误: 无法找到交易ID {trade_id}")
            return None
        
        # 获取当前级别和目标利润
        current_level = trade['current_level']
        profit = trade['target_profit']
        
        # 检查目标级别是否有效
        if target_level <= current_level:
            print(f"警告: 目标级别 {target_level} 小于或等于当前级别 {current_level}")
        
        # 获取实际买入记录
        actual_amounts = []
        for record in trade['buy_records']:
            level = record.get('level', -1)
            amount = record.get('amount', 0)
            actual_amounts.append((level, amount))
        
        # 按级别排序
        actual_amounts.sort(key=lambda x: x[0])
        
        # 创建买入量映射并获取最高已有级别
        level_to_amount = {}
        max_level = -1
        for level, amount in actual_amounts:
            if level != -1:  # 有效级别
                level_to_amount[level] = amount
                max_level = max(max_level, level)
        
        # 如果没有找到有效的级别或买入记录，使用初始价格计算初始级别
        if max_level == -1:
            initial_price = trade['initial_price']
            initial_amount = calculate_initial_amount(initial_price, profit)
            level_to_amount[0] = initial_amount
            max_level = 0
        
        # 准备价格列表 - 如果提供了price_levels就使用它，否则使用market_price
        if price_levels is None:
            # 创建一个仅包含目标级别市场价格的列表
            effective_price_levels = [market_price]
        else:
            # 使用提供的价格列表
            effective_price_levels = price_levels
        
        # 准备累计买入量列表，按级别顺序包含所有已有记录
        buy_amounts = []
        for i in range(max_level + 1):
            amount = level_to_amount.get(i, 0)  # 如果没有该级别的记录，默认为0
            buy_amounts.append(amount)
        
        # 从当前最高级别开始，计算到目标级别
        for i in range(max_level + 1, target_level + 1):
            # 确定这个级别应该使用的价格
            level_index = i - max_level - 1  # 价格列表索引
            
            # 如果索引超出价格列表长度，使用最后一个价格
            if level_index >= len(effective_price_levels):
                level_price = effective_price_levels[-1]
            else:
                level_price = effective_price_levels[level_index]
            
            # 计算这个级别的买入量
            level_amount = calculate_next_amount(buy_amounts, profit, level_price)
            buy_amounts.append(level_amount)
            
            # 如果这是目标级别，返回结果
            if i == target_level:
                return level_amount
        
        # 如果循环结束后还没有返回，说明目标级别不在计算范围内
        print(f"错误: 目标级别 {target_level} 超出计算范围")
        return None
    except Exception as e:
        print(f"计算指定级别买入数量时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def calculate_all_levels(profit, initial_price, price_levels, max_levels=10):
    """
    计算所有级别的买入数量和投资金额
    
    Args:
        profit (float): 目标利润(USDC)
        initial_price (float): 初始市场价格
        price_levels (list): 后续级别的价格列表 [price1, price2, ...]
        max_levels (int): 最大买入级别数，默认为10
        
    Returns:
        list: 买入级别信息列表，每项包含级别、价格、数量和投资金额
    """
    buy_levels = []
    previous_amounts = []
    
    # 计算初始买入
    initial_amount = calculate_initial_amount(initial_price, profit)
    initial_investment = initial_amount * initial_price
    
    buy_levels.append({
        'level': 0,
        'price': initial_price,
        'amount': initial_amount,
        'investment': initial_investment
    })
    previous_amounts.append(initial_amount)
    
    # 计算后续级别
    for i, price in enumerate(price_levels[:max_levels-1]):  # 最多处理到max_levels-1
        next_amount = calculate_next_amount(previous_amounts, profit, price)
        next_investment = next_amount * price
        
        buy_levels.append({
            'level': i + 1,
            'price': price,
            'amount': next_amount,
            'investment': next_investment
        })
        previous_amounts.append(next_amount)
    
    return buy_levels

def calculate_all_levels_for_trade(trade_id, price_levels):
    """
    为指定交易计算所有级别的买入数量和投资金额
    
    Args:
        trade_id (str): 交易ID
        price_levels (list): 后续级别的价格列表 [price1, price2, ...]
        
    Returns:
        list: 买入级别信息列表，每项包含级别、价格、数量和投资金额
        None: 如果交易不存在
    """
    if not TRADE_RECORDS_AVAILABLE:
        return None
        
    # 获取交易记录
    trade = trade_records.get_trade_by_id(trade_id)
    if not trade:
        return None
        
    # 从交易记录中提取信息
    profit = trade['target_profit']
    current_level = trade['current_level']
    
    # 如果没有买入记录，使用初始价格
    if not trade['buy_records']:
        initial_price = trade['initial_price']
        return calculate_all_levels(profit, initial_price, price_levels)
    
    # 获取已执行的买入记录
    executed_levels = []
    for record in trade['buy_records']:
        executed_levels.append({
            'level': record['level'],
            'price': record['price'],
            'amount': record['amount'],
            'investment': record['investment'],
            'executed': True
        })
    
    # 计算后续级别
    previous_amounts = [record['amount'] for record in trade['buy_records']]
    
    # 为剩余级别计算买入量
    remaining_levels = []
    for i, price in enumerate(price_levels):
        next_level = current_level + i + 1
        next_amount = calculate_next_amount(previous_amounts, profit, price)
        next_investment = next_amount * price
        
        level_info = {
            'level': next_level,
            'price': price,
            'amount': next_amount,
            'investment': next_investment,
            'executed': False
        }
        
        remaining_levels.append(level_info)
        previous_amounts.append(next_amount)  # 添加到previous_amounts以便计算下一级
    
    # 合并已执行和未执行的级别
    all_levels = executed_levels + remaining_levels
    
    # 按级别排序
    all_levels.sort(key=lambda x: x['level'])
    
    return all_levels

def is_price_match(signal_price, target_price, tolerance=0.001):
    """
    判断信号价格是否匹配目标价格
    
    Args:
        signal_price (float): 信号中的价格
        target_price (float): 目标价格
        tolerance (float): 容忍误差比例
        
    Returns:
        bool: 是否匹配
    """
    # 将字符串价格转换为浮点数
    if isinstance(signal_price, str):
        signal_price = float(signal_price)
    if isinstance(target_price, str):
        target_price = float(target_price)
    
    # 计算误差范围
    allowed_diff = target_price * tolerance
    
    # 检查是否在误差范围内
    return abs(signal_price - target_price) <= allowed_diff

def apply_investment_limit(buy_levels, max_investment):
    """
    应用投资限额，返回符合最大投资额度的买入级别
    
    Args:
        buy_levels (list): 买入级别信息列表
        max_investment (float): 最大投资额度(USDC)
        
    Returns:
        list: 调整后的买入级别列表
    """
    if not buy_levels:
        return []
        
    adjusted_levels = []
    total_investment = 0
    
    for level in buy_levels:
        # 检查添加这一级别后是否超过最大投资额度
        if total_investment + level['investment'] <= max_investment:
            adjusted_levels.append(level)
            total_investment += level['investment']
        else:
            # 计算可用的剩余投资额度
            remaining = max_investment - total_investment
            if remaining > 0:
                # 按比例缩减最后一级的买入量
                ratio = remaining / level['investment']
                adjusted_amount = level['amount'] * ratio
                adjusted_investment = remaining
                
                # 添加调整后的级别
                adjusted_level = level.copy()
                adjusted_level['amount'] = adjusted_amount
                adjusted_level['investment'] = adjusted_investment
                adjusted_level['adjusted'] = True  # 标记为已调整
                
                adjusted_levels.append(adjusted_level)
                total_investment = max_investment
            break
    
    return adjusted_levels

def get_investment_summary(buy_levels):
    """
    计算投资摘要信息
    
    Args:
        buy_levels (list): 买入级别信息列表
        
    Returns:
        dict: 包含总投资额、总买入数量等信息
    """
    if not buy_levels:
        return {"total_investment": 0, "total_amount": 0, "levels_count": 0}
    
    total_investment = sum(level['investment'] for level in buy_levels)
    total_amount = sum(level['amount'] for level in buy_levels)
    
    return {
        "total_investment": total_investment,
        "total_amount": total_amount,
        "levels_count": len(buy_levels),
        "average_price": total_investment / total_amount if total_amount > 0 else 0
    }

def get_investment_summary_for_trade(trade_id):
    """
    获取特定交易的投资摘要信息
    
    Args:
        trade_id (str): 交易ID
        
    Returns:
        dict: 包含总投资额、总买入数量等信息
        None: 如果交易不存在
    """
    if not TRADE_RECORDS_AVAILABLE:
        return None
        
    # 获取交易记录
    trade = trade_records.get_trade_by_id(trade_id)
    if not trade:
        return None
        
    # 从交易记录中提取信息
    return {
        "trade_id": trade['trade_id'],
        "market_name": trade['market_name'],
        "total_investment": trade['total_investment'],
        "total_amount": trade['total_amount'],
        "average_price": trade['average_price'],
        "current_price": trade['current_price'],
        "estimated_profit": trade['estimated_profit'],
        "current_level": trade['current_level']
    }

def estimate_profit_at_price(buy_levels, target_price):
    """
    估算在目标价格下的利润
    
    Args:
        buy_levels (list): 买入级别信息列表
        target_price (float): 目标价格
        
    Returns:
        float: 预计利润(USDC)
    """
    if not buy_levels:
        return 0
        
    total_amount = sum(level['amount'] for level in buy_levels)
    total_investment = sum(level['investment'] for level in buy_levels)
    
    estimated_value = total_amount * target_price
    profit = estimated_value - total_investment
    
    return profit

def estimate_profit_for_trade(trade_id, target_price):
    """
    为特定交易估算在目标价格下的利润
    
    Args:
        trade_id (str): 交易ID
        target_price (float): 目标价格
        
    Returns:
        float: 预计利润(USDC)
        None: 如果交易不存在
    """
    if not TRADE_RECORDS_AVAILABLE:
        return None
        
    # 获取交易记录
    trade = trade_records.get_trade_by_id(trade_id)
    if not trade:
        return None
        
    # 计算预计利润
    estimated_value = trade['total_amount'] * target_price
    profit = estimated_value - trade['total_investment']
    
    return profit

# 简单测试函数
def test_calculations():
    """测试计算逻辑是否正确"""
    # 测试计算所有级别
    initial_price = 0.6
    price_levels = [0.5, 0.4, 0.3, 0.2, 0.1]
    profit = 100
    
    # 计算初始买入
    amount0 = calculate_initial_amount(initial_price, profit)
    investment0 = amount0 * initial_price
    print(f"\n初始买入(Level 0):")
    print(f"价格: {initial_price} USDC")
    print(f"数量: {amount0:.4f}")
    print(f"投资: {investment0:.4f} USDC")
    
    # 计算全部买入级别
    levels = calculate_all_levels(profit, initial_price, price_levels)
    
    # 打印每个级别
    print("\n所有买入级别详情:")
    for level in levels:
        print(f"Level {level['level']}:")
        print(f"  价格: {level['price']}")
        print(f"  数量: {level['amount']:.2f}")
        print(f"  投资: {level['investment']:.2f} USDC")
    
    # 打印投资摘要
    summary = get_investment_summary(levels)
    print("\n投资摘要:")
    print(f"  总买入数量: {summary['total_amount']:.2f}")
    print(f"  总投资金额: {summary['total_investment']:.2f} USDC")
    print(f"  平均买入价格: {summary['average_price']:.6f} USDC")
    
    # 应用投资限额
    max_investment = 1000
    adjusted_levels = apply_investment_limit(levels, max_investment)
    adjusted_summary = get_investment_summary(adjusted_levels)
    
    print(f"\n应用投资限额 ({max_investment} USDC) 后:")
    print(f"  可执行级别数: {adjusted_summary['levels_count']}")
    print(f"  总投资金额: {adjusted_summary['total_investment']:.2f} USDC")
    
    # 估算利润
    target_price = 1.0
    estimated_profit = estimate_profit_at_price(adjusted_levels, target_price)
    print(f"\n目标价格 {target_price} 时的预计利润: {estimated_profit:.2f} USDC")

    # 测试交易记录功能（如果可用）
    if TRADE_RECORDS_AVAILABLE:
        print("\n测试交易记录功能:")
        try:
            # 创建测试交易
            test_token_id = "12345"
            test_market = "测试市场-功能测试"
            # 使用正确的参数格式创建交易记录
            test_trade = trade_records.create_trade(test_token_id, test_market, profit, initial_price)
            trade_id = test_trade["trade_id"]
            print(f"创建测试交易: {trade_id}")
            
            # 添加买入记录
            trade_records.add_buy_record(trade_id, 0, initial_price, 66.67, "test-order-1")
            
            # 计算下一级买入量
            next_amount, next_level = calculate_next_amount_for_trade(trade_id, 0.5)
            print(f"下一级别({next_level})买入量: {next_amount:.2f}")
            
            # 计算所有级别
            all_levels = calculate_all_levels_for_trade(trade_id, price_levels)
            print("\n交易的所有买入级别:")
            for level in all_levels:
                status = "已执行" if level.get('executed', False) else "未执行"
                print(f"Level {level['level']}: 价格 {level['price']}, 数量 {level['amount']:.2f} ({status})")
            
            # 测试跨级计算
            print("\n测试跨级计算功能:")
            for target_level in [2, 3, 5]:
                amt = calculate_amount_for_specific_level(trade_id, 0.3, target_level, price_levels)
                print(f"直接计算级别{target_level}的买入量: {amt:.2f}")
                
            # 测试估算利润
            profit_at_1 = estimate_profit_for_trade(trade_id, 1.0)
            print(f"\n价格为1.0时的预计利润: {profit_at_1:.2f} USDC")
            
            # 获取投资摘要
            trade_summary = get_investment_summary_for_trade(trade_id)
            print("\n交易投资摘要:")
            print(f"  总投资: {trade_summary['total_investment']:.2f} USDC")
            print(f"  总数量: {trade_summary['total_amount']:.2f}")
            
            # 清理测试数据
            trade_records.delete_trade(trade_id)
            print("\n测试交易记录已删除")
            
        except Exception as e:
            print(f"测试交易记录功能时出错: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("=== Polymarket 买入策略计算工具 ===")
    test_calculations() 