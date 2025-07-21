#!/usr/bin/env python3.12
"""
简化版自动交易系统 - 不依赖numpy和复杂的嵌入模型
"""

import asyncio
import aiohttp
import json
import logging
import time
import sys
import os
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/root/poly/auto_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('SimplifiedAutoTradingSystem')

# 加载环境变量
load_dotenv()
load_dotenv('.env.agent')


@dataclass
class PriceLevel:
    """价格级别配置"""
    level: int
    tokenid: str
    profit: float
    btcprice: float
    triggered: bool = False


class SimplifiedBTCMonitor:
    """简化版BTC价格监控器"""
    
    def __init__(self, config_path: str = "/root/poly/setting.json"):
        self.config_path = Path(config_path)
        self.price_levels: List[PriceLevel] = []
        self.current_price: float = 0.0
        self.monitoring = False
        self.triggered_levels: Set[int] = set()
        
        # 币安API配置
        self.binance_api_base = "https://api.binance.com"
        self.btc_symbol = "BTCUSDT"
        
        # 加载配置
        self.load_config()
        
        # 回调函数
        self.price_trigger_callback = None
    
    def load_config(self):
        """加载配置文件"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.price_levels = []
                for level_config in config.get('levels', []):
                    level = PriceLevel(
                        level=level_config['level'],
                        tokenid=level_config['tokenid'],
                        profit=level_config['profit'],
                        btcprice=level_config['btcprice']
                    )
                    self.price_levels.append(level)
                
                logger.info(f"加载了 {len(self.price_levels)} 个价格级别配置")
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
    
    def set_price_trigger_callback(self, callback):
        """设置价格触发回调函数"""
        self.price_trigger_callback = callback
    
    async def get_btc_price(self) -> Optional[float]:
        """从币安API获取BTC价格"""
        try:
            url = f"{self.binance_api_base}/api/v3/ticker/price"
            params = {"symbol": self.btc_symbol}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        price = float(data['price'])
                        return price
                    else:
                        logger.error(f"币安API错误: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"获取BTC价格失败: {str(e)}")
            return None
    
    def check_price_triggers(self, current_price: float) -> List[PriceLevel]:
        """检查价格触发条件"""
        triggered_levels = []
        
        for level in self.price_levels:
            if level.level in self.triggered_levels:
                continue
            
            if current_price >= level.btcprice:
                level.triggered = True
                self.triggered_levels.add(level.level)
                triggered_levels.append(level)
                logger.info(f"价格触发! Level {level.level}: BTC ${current_price:,.2f} >= ${level.btcprice:,.2f}")
        
        return triggered_levels
    
    async def monitor_price(self, interval: int = 5):
        """监控价格变化"""
        logger.info(f"开始监控BTC价格，间隔 {interval} 秒")
        self.monitoring = True
        
        while self.monitoring:
            try:
                price = await self.get_btc_price()
                
                if price is not None:
                    self.current_price = price
                    
                    # 检查价格触发
                    triggered_levels = self.check_price_triggers(price)
                    
                    # 处理触发的级别
                    for level in triggered_levels:
                        if self.price_trigger_callback:
                            await self.price_trigger_callback(level, price)
                    
                    if triggered_levels:
                        logger.info(f"BTC价格: ${price:,.2f} - 触发了 {len(triggered_levels)} 个级别")
                    else:
                        logger.debug(f"BTC价格: ${price:,.2f}")
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"价格监控循环错误: {str(e)}")
                await asyncio.sleep(interval)
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False


class SimplifiedKnowledgeBase:
    """简化版知识库"""
    
    def __init__(self, knowledge_file: str = "/root/poly/plan.md"):
        self.knowledge_file = Path(knowledge_file)
        self.knowledge_content = ""
        self.load_knowledge()
    
    def load_knowledge(self):
        """加载知识库"""
        try:
            if self.knowledge_file.exists():
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    self.knowledge_content = f.read()
                logger.info("知识库加载成功")
            else:
                logger.error(f"知识库文件不存在: {self.knowledge_file}")
        except Exception as e:
            logger.error(f"加载知识库失败: {str(e)}")
    
    def get_trading_guidance(self, level: int) -> str:
        """获取交易指导"""
        # 简单的文本匹配
        lines = self.knowledge_content.split('\n')
        for line in lines:
            if f"level {level}" in line.lower():
                return line.strip()
        
        return f"执行Level {level}交易: 查询代币价格 -> 计算投入金额 -> 执行买入"


class SimplifiedAutoTradingSystem:
    """简化版自动交易系统"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.btc_monitor = SimplifiedBTCMonitor()
        self.knowledge_base = SimplifiedKnowledgeBase()
        self.btc_monitor.set_price_trigger_callback(self.handle_price_trigger)
        
        self.system_running = False
        self.trading_enabled = True
        self.last_execution_time = {}
        self.trading_history = []
        
        logger.info("简化版自动交易系统初始化完成")
    
    async def handle_price_trigger(self, level: PriceLevel, current_price: float):
        """处理价格触发事件"""
        logger.info(f"🚨 价格触发事件: Level {level.level}, BTC价格: ${current_price:,.2f}")
        
        try:
            if not self.trading_enabled:
                logger.warning("交易已禁用，跳过执行")
                return
            
            if level.level in self.last_execution_time:
                logger.warning(f"Level {level.level} 已经执行过，跳过")
                return
            
            # 记录执行时间
            self.last_execution_time[level.level] = datetime.now()
            
            # 获取交易指导
            guidance = self.knowledge_base.get_trading_guidance(level.level)
            logger.info(f"交易指导: {guidance}")
            
            # 执行交易
            await self.execute_trading_plan(level, current_price)
            
        except Exception as e:
            logger.error(f"处理价格触发失败: {str(e)}")
    
    async def execute_trading_plan(self, level: PriceLevel, current_price: float):
        """执行交易计划"""
        logger.info(f"开始执行Level {level.level}的交易计划")
        
        try:
            # 步骤1: 查询代币价格
            token_price = await self.get_token_price(level.tokenid)
            if not token_price:
                logger.error(f"无法获取代币价格: {level.tokenid}")
                return
            
            logger.info(f"代币价格: {token_price}")
            
            # 步骤2: 计算购买金额
            if token_price >= 1.0:
                logger.error(f"代币价格异常: {token_price} >= 1.0")
                return
            
            # 计算累积投资金额
            amount = self.calculate_cumulative_amount(level.level, level.profit, token_price)
            logger.info(f"计算的购买金额: {amount:.2f} USDC")
            
            # 步骤3: 执行买入交易
            trade_result = await self.execute_buy_order(level.tokenid, amount)
            
            # 记录交易历史
            trade_record = {
                'timestamp': datetime.now().isoformat(),
                'level': level.level,
                'tokenid': level.tokenid,
                'btc_trigger_price': level.btcprice,
                'btc_current_price': current_price,
                'token_price': token_price,
                'amount': amount,
                'profit_target': level.profit,
                'cumulative_investment_before': self.get_cumulative_investment_up_to_level(level.level - 1),
                'cumulative_investment_after': self.get_cumulative_investment_up_to_level(level.level - 1) + amount,
                'result': trade_result
            }
            
            self.trading_history.append(trade_record)
            await self.save_trading_record(trade_record)
            
            logger.info(f"Level {level.level} 交易执行完成")
            
        except Exception as e:
            logger.error(f"执行交易计划失败: {str(e)}")
    
    async def get_token_price(self, token_id: str) -> Optional[float]:
        """获取代币价格"""
        try:
            cmd = [
                sys.executable,
                str(self.project_root / 'check_price.py'),
                token_id
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_root)
            )
            
            if result.returncode == 0:
                output = result.stdout
                return self._parse_price_from_output(output)
            else:
                logger.error(f"查询价格失败: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"获取代币价格失败: {str(e)}")
            return None
    
    def _parse_price_from_output(self, output: str) -> Optional[float]:
        """从输出中解析价格"""
        import re
        
        # 尝试匹配最低卖价
        ask_match = re.search(r'最低卖价.*?(\d+\.?\d*)\s*USDC', output)
        if ask_match:
            return float(ask_match.group(1))
        
        # 尝试匹配最高买价
        bid_match = re.search(r'最高买价.*?(\d+\.?\d*)\s*USDC', output)
        if bid_match:
            return float(bid_match.group(1))
        
        return None
    
    async def execute_buy_order(self, token_id: str, amount: float) -> Dict[str, Any]:
        """执行买入订单"""
        try:
            cmd = [
                sys.executable,
                str(self.project_root / 'market_buy_order.py'),
                token_id,
                str(amount)
            ]
            
            logger.info(f"执行买入命令: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_root)
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout if result.returncode == 0 else result.stderr,
                'returncode': result.returncode
            }
            
        except Exception as e:
            logger.error(f"执行买入订单失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def save_trading_record(self, record: Dict[str, Any]):
        """保存交易记录"""
        try:
            records_file = self.project_root / 'auto_trading_records.json'
            
            if records_file.exists():
                with open(records_file, 'r', encoding='utf-8') as f:
                    records = json.load(f)
            else:
                records = {'trades': []}
            
            records['trades'].append(record)
            
            with open(records_file, 'w', encoding='utf-8') as f:
                json.dump(records, f, indent=2, ensure_ascii=False)
            
            logger.info(f"交易记录已保存")
            
        except Exception as e:
            logger.error(f"保存交易记录失败: {str(e)}")
    
    def calculate_cumulative_amount(self, current_level: int, profit: float, token_price: float) -> float:
        """计算累积投资金额
        
        公式:
        Level 0: amount0 = profit / (1/price - 1)
        Level 1: amount1 = (profit + amount0) / (1/price - 1)
        Level 2: amount2 = (profit + amount1) / (1/price - 1)
        以此类推...
        """
        if current_level == 0:
            # Level 0 使用原始公式
            amount = profit / (1/token_price - 1)
            logger.info(f"Level 0 公式: amount = {profit} / (1/{token_price} - 1) = {amount:.2f}")
            return amount
        
        # Level 1+ 需要累积前一级别的投资金额
        cumulative_investment = self.get_cumulative_investment_up_to_level(current_level - 1)
        base_amount = profit + cumulative_investment
        amount = base_amount / (1/token_price - 1)
        
        logger.info(f"Level {current_level} 公式: amount = ({profit} + {cumulative_investment:.2f}) / (1/{token_price} - 1) = {amount:.2f}")
        logger.info(f"  其中: profit={profit}, 累积投资={cumulative_investment:.2f}, 代币价格={token_price}")
        
        return amount
    
    def get_cumulative_investment_up_to_level(self, max_level: int) -> float:
        """获取到指定级别为止的累积投资金额"""
        cumulative = 0.0
        
        for trade in self.trading_history:
            if trade['level'] <= max_level and trade['result'].get('success', False):
                cumulative += trade['amount']
        
        return cumulative
    
    def get_cumulative_investment(self, current_level: int) -> float:
        """获取包含当前级别的累积投资"""
        return self.get_cumulative_investment_up_to_level(current_level)
    
    def display_investment_summary(self):
        """显示投资摘要"""
        print("\n💰 投资摘要:")
        print("-" * 40)
        
        total_investment = 0.0
        for level in sorted(set(trade['level'] for trade in self.trading_history)):
            level_investment = sum(
                trade['amount'] for trade in self.trading_history 
                if trade['level'] == level and trade['result'].get('success', False)
            )
            if level_investment > 0:
                total_investment += level_investment
                print(f"Level {level}: ${level_investment:.2f} USDC")
        
        print(f"总投资: ${total_investment:.2f} USDC")
        print("-" * 40)
    
    async def execute_level_0_immediately(self):
        """系统启动时立即执行Level 0交易"""
        logger.info("📋 根据交易计划，启动时立即执行Level 0交易")
        
        # 找到Level 0配置
        level_0 = None
        for level in self.btc_monitor.price_levels:
            if level.level == 0:
                level_0 = level
                break
        
        if not level_0:
            logger.error("❌ 未找到Level 0配置")
            return
        
        try:
            # 获取当前BTC价格（用于记录）
            current_btc_price = await self.btc_monitor.get_btc_price()
            if not current_btc_price:
                current_btc_price = 0.0
            
            logger.info(f"🎯 执行Level 0交易 - 当前BTC价格: ${current_btc_price:,.2f}")
            
            # 标记Level 0已触发（避免重复执行）
            self.btc_monitor.triggered_levels.add(0)
            self.last_execution_time[0] = datetime.now()
            
            # 执行交易计划
            await self.execute_trading_plan(level_0, current_btc_price)
            
            logger.info("✅ Level 0交易执行完成")
            
        except Exception as e:
            logger.error(f"❌ Level 0交易执行失败: {str(e)}")
    
    async def start_system(self):
        """启动系统"""
        logger.info("🚀 启动简化版自动交易系统")
        
        self.system_running = True
        
        # 显示系统状态
        await self.display_system_status()
        
        # 立即执行Level 0交易
        await self.execute_level_0_immediately()
        
        # 显示后续监控提示
        print(f"\n🔄 Level 0交易已完成，现在开始监控BTC价格...")
        print(f"📊 等待触发:")
        for level in self.btc_monitor.price_levels:
            if level.level > 0:
                print(f"   Level {level.level}: BTC价格达到 ${level.btcprice:,.2f}")
        print()
        
        # 启动监控
        monitor_task = asyncio.create_task(self.btc_monitor.monitor_price(interval=5))
        status_task = asyncio.create_task(self.system_status_monitor())
        
        try:
            await asyncio.gather(monitor_task, status_task)
        except KeyboardInterrupt:
            logger.info("收到停止信号")
            await self.stop_system()
        except Exception as e:
            logger.error(f"系统运行错误: {str(e)}")
            await self.stop_system()
    
    async def stop_system(self):
        """停止系统"""
        logger.info("🛑 停止自动交易系统")
        self.system_running = False
        self.btc_monitor.stop_monitoring()
        await self.display_final_status()
    
    async def display_system_status(self):
        """显示系统状态"""
        print("=" * 70)
        print("🤖 Polymarket 简化版自动交易系统")
        print("=" * 70)
        
        print(f"\n📊 系统配置:")
        print(f"• 价格级别: {len(self.btc_monitor.price_levels)} 个")
        print(f"• 交易启用: {'✅' if self.trading_enabled else '❌'}")
        
        print(f"\n🎯 价格级别配置:")
        for level in self.btc_monitor.price_levels:
            if level.level == 0:
                status = "🚀 启动时立即执行"
            else:
                status = "✅ 已触发" if level.level in self.btc_monitor.triggered_levels else "⏳ 等待BTC价格信号"
            print(f"  Level {level.level}: ${level.btcprice:,.2f} - {status}")
        
        current_price = await self.btc_monitor.get_btc_price()
        if current_price:
            print(f"\n💰 当前BTC价格: ${current_price:,.2f}")
        
        print(f"\n📋 交易计划:")
        print(f"• Level 0: 系统启动时立即执行")
        print(f"• Level 1+: 等待BTC价格信号触发")
    
    async def system_status_monitor(self):
        """系统状态监控"""
        while self.system_running:
            try:
                await asyncio.sleep(60)
                if self.system_running:
                    logger.info(f"系统状态: BTC ${self.btc_monitor.current_price:,.2f}, 已触发: {len(self.btc_monitor.triggered_levels)} 个级别")
            except Exception as e:
                logger.error(f"状态监控错误: {str(e)}")
                await asyncio.sleep(10)
    
    async def display_final_status(self):
        """显示最终状态"""
        print("\n" + "=" * 70)
        print("📈 交易执行摘要")
        print("=" * 70)
        
        executed_levels = list(self.last_execution_time.keys())
        if executed_levels:
            print(f"\n✅ 已执行的级别: {executed_levels}")
        else:
            print("\n❌ 没有执行任何交易")
        
        if self.trading_history:
            print(f"\n📊 交易历史: {len(self.trading_history)} 笔")
            for trade in self.trading_history:
                status = "✅ 成功" if trade['result'].get('success') else "❌ 失败"
                print(f"  Level {trade['level']}: {trade['amount']:.2f} USDC - {status}")
        
        # 显示投资摘要
        self.display_investment_summary()
        
        print(f"\n💾 详细记录已保存到: auto_trading_records.json")


async def main():
    """主函数"""
    print("初始化简化版自动交易系统...")
    
    trading_system = SimplifiedAutoTradingSystem()
    
    if not trading_system.btc_monitor.price_levels:
        print("❌ 错误: 未找到价格级别配置")
        return
    
    try:
        await trading_system.start_system()
    except KeyboardInterrupt:
        print("\n系统被用户中断")
    except Exception as e:
        print(f"\n系统运行错误: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())