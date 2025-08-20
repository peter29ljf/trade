#!/usr/bin/env python3.12
"""
多币种自动交易系统 - 支持BTC、ETH、SOL同时监控 (修正版)
"""

import asyncio
import aiohttp
import json
import logging
import time
import sys
import os
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/root/poly/multi_crypto_auto_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('MultiCryptoAutoTradingSystem')

# 加载环境变量
load_dotenv()
load_dotenv('.env.agent')


@dataclass
class PriceLevel:
    """价格级别配置"""
    level: int
    tokenid: str
    profit: float
    trigger_price: float
    crypto: str
    triggered: bool = False


class MultiCryptoPriceMonitor:
    """多币种价格监控器 (修正版)"""
    
    def __init__(self, config_path: str = "/root/poly/setting_multi_crypto.json"):
        self.config_path = Path(config_path)
        self.crypto_levels: Dict[str, List[PriceLevel]] = {}
        self.current_prices: Dict[str, float] = {}
        self.monitoring = False
        self.triggered_levels: Dict[str, Set[int]] = {}
        
        # 使用Coinbase API (稳定，无地区限制)
        self.price_api_base = "https://api.coinbase.com/v2/exchange-rates"
        self.crypto_mapping = {
            "BTC": "BTC",
            "ETH": "ETH", 
            "SOL": "SOL"
        }
        
        # 加载配置
        self.load_config()
        
        # 项目根目录
        self.project_root = Path(__file__).parent.absolute()
        
        # 交易记录
        self.investment_records: Dict[str, List[Dict]] = {}
        for crypto in self.crypto_levels.keys():
            self.investment_records[crypto] = []
        
        # 价格历史记录，用于判断跨越触发
        self.price_history: Dict[str, float] = {}
        
        # 日志清理
        self.last_log_cleanup = datetime.now()
        self.log_cleanup_interval = timedelta(hours=1)  # 1小时清理一次
    
    def load_config(self):
        """加载配置文件"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.crypto_levels = {}
                self.triggered_levels = {}
                
                # 加载每个币种的配置
                for crypto, crypto_config in config.get('cryptocurrencies', {}).items():
                    self.crypto_levels[crypto] = []
                    self.triggered_levels[crypto] = set()
                    self.current_prices[crypto] = 0.0
                    
                    for level_config in crypto_config.get('levels', []):
                        level = PriceLevel(
                            level=level_config['level'],
                            tokenid=level_config['tokenid'],
                            profit=level_config['profit'],
                            trigger_price=level_config['trigger_price'],
                            crypto=crypto
                        )
                        self.crypto_levels[crypto].append(level)
                
                logger.info(f"配置加载完成，支持币种: {list(self.crypto_levels.keys())}")
                for crypto, levels in self.crypto_levels.items():
                    logger.info(f"{crypto}: {len(levels)} 个价格级别")
            else:
                logger.error(f"配置文件不存在: {self.config_path}")
        except Exception as e:
            logger.error(f"加载配置失败: {str(e)}")
    
    async def get_all_crypto_prices(self) -> Dict[str, float]:
        """获取所有币种的价格 (使用Coinbase API)"""
        prices = {}
        try:
            async with aiohttp.ClientSession() as session:
                # 并发获取所有币种价格
                tasks = []
                for crypto, symbol in self.crypto_mapping.items():
                    url = f"{self.price_api_base}?currency={symbol}"
                    tasks.append(self._get_single_price(session, crypto, url))
                
                # 等待所有请求完成
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 处理结果
                for crypto in self.crypto_mapping.keys():
                    prices[crypto] = 0.0  # 默认价格
                
                for result in results:
                    if isinstance(result, tuple) and len(result) == 2:
                        crypto, price = result
                        if price > 0:
                            prices[crypto] = price
                    elif isinstance(result, Exception):
                        logger.warning(f"获取价格时发生异常: {str(result)}")
                            
        except Exception as e:
            logger.error(f"获取价格异常: {str(e)}")
            for crypto in self.crypto_mapping.keys():
                prices[crypto] = 0.0
                
        return prices
    
    async def _get_single_price(self, session: aiohttp.ClientSession, crypto: str, url: str) -> tuple:
        """获取单个币种价格 (Coinbase格式)"""
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    # Coinbase API格式: data.data.rates.USD 直接就是USD价格
                    usd_rate = data.get('data', {}).get('rates', {}).get('USD', '0')
                    price = float(usd_rate) if float(usd_rate) > 0 else 0.0
                    return (crypto, price)
                else:
                    logger.warning(f"Coinbase API错误 {crypto}: HTTP {response.status}")
                    return (crypto, 0.0)
        except Exception as e:
            logger.warning(f"获取{crypto}价格失败: {str(e)}")
            return (crypto, 0.0)
    
    def check_price_triggers(self, crypto: str, current_price: float) -> List[PriceLevel]:
        """检查指定币种的价格触发条件"""
        triggered_levels = []
        
        for level in self.crypto_levels.get(crypto, []):
            if level.level in self.triggered_levels[crypto]:
                continue
                
            # Level 0 立即触发（不管价格直接买入）
            if level.level == 0:
                triggered_levels.append(level)
                self.triggered_levels[crypto].add(level.level)
                logger.info(f"🎯 {crypto} Level {level.level} 立即触发（无价格条件）")
            # Level 1+ 检查价格跨越条件
            elif level.level >= 1 and self.check_price_crossover(crypto, current_price, level.trigger_price):
                triggered_levels.append(level)
                self.triggered_levels[crypto].add(level.level)
                logger.info(f"🚀 {crypto} Level {level.level} 价格跨越触发: ${current_price:,.2f} 跨越 ${level.trigger_price:,.2f}")
        
        return triggered_levels
    
    def check_price_crossover(self, crypto: str, current_price: float, trigger_price: float) -> bool:
        """检查价格是否跨越触发价格（支持双向跨越）"""
        # 获取上一次的价格
        previous_price = self.price_history.get(crypto)
        
        if previous_price is None:
            # 第一次检查，不触发，只记录价格
            self.price_history[crypto] = current_price
            logger.info(f"🔄 {crypto} 初始化价格历史: ${current_price:,.2f}")
            return False
        
        # 避免从异常价格（如0或过于离谱的价格）开始的跨越
        if previous_price <= 0 or abs(current_price - previous_price) / max(current_price, previous_price) > 0.5:
            # 价格变化过大（超过50%），可能是系统重启或异常，不触发跨越
            self.price_history[crypto] = current_price
            logger.info(f"🔄 {crypto} 价格变化过大，重置历史: ${previous_price:,.2f} -> ${current_price:,.2f}")
            return False
        
        # 检查是否发生跨越
        # 情况1：价格从下方突破到上方（上涨跨越）
        if previous_price <= trigger_price < current_price:
            self.price_history[crypto] = current_price
            logger.info(f"📈 {crypto} 价格上涨跨越: ${previous_price:,.2f} -> ${current_price:,.2f} 跨越 ${trigger_price:,.2f}")
            return True
        
        # 情况2：价格从上方跌破到下方（下跌跨越）
        if previous_price >= trigger_price > current_price:
            self.price_history[crypto] = current_price
            logger.info(f"📉 {crypto} 价格下跌跨越: ${previous_price:,.2f} -> ${current_price:,.2f} 跨越 ${trigger_price:,.2f}")
            return True
        
        # 更新价格历史
        self.price_history[crypto] = current_price
        return False
    
    def get_previous_investment_total(self, crypto: str, up_to_level: int) -> float:
        """获取指定级别之前的总投资额 (从实际交易记录)"""
        total = 0.0
        for record in self.investment_records.get(crypto, []):
            if record['level'] < up_to_level and record.get('success', False):
                total += record.get('investment_amount', 0.0)
        
        logger.debug(f"{crypto} Level {up_to_level}之前的总投资额: ${total:.2f}")
        return total
    
    async def get_token_price(self, token_id: str) -> float:
        """获取token价格 (使用check_price.py)"""
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
                timeout=30
            )
            
            if result.returncode == 0:
                # 解析价格输出
                output = result.stdout.strip()
                for line in output.split('\n'):
                    if '最低卖价(Ask):' in line:
                        # 提取价格: "最低卖价(Ask): 0.52 USDC, 数量: 100"
                        price_part = line.split(':')[1].split('USDC')[0].strip()
                        return float(price_part)
                        
                # 如果没有找到Ask价格，尝试找Bid价格
                for line in output.split('\n'):
                    if '最高买价(Bid):' in line:
                        price_part = line.split(':')[1].split('USDC')[0].strip()
                        return float(price_part)
                        
                logger.warning(f"未能解析token {token_id}的价格，使用默认值")
                return 0.52  # 默认价格
            else:
                logger.error(f"获取token价格失败: {result.stderr}")
                return 0.52
                
        except Exception as e:
            logger.error(f"获取token价格异常: {str(e)}")
            return 0.52
    
    async def calculate_investment_amount(self, crypto: str, level: PriceLevel, token_price: float) -> float:
        """计算投资金额 (修正公式: 所有级别都使用累积投资公式)"""
        try:
            # 获取之前所有级别的投资总额
            previous_amount = self.get_previous_investment_total(crypto, level.level)
            
            # 累积投资公式: amount = (profit + previous_amount) / (1/price - 1)
            target_total = level.profit + previous_amount
            
            if token_price > 0 and token_price < 1:
                amount = target_total / (1/token_price - 1)
                logger.info(f"💰 {crypto} Level {level.level} 投资计算:")
                logger.info(f"   目标利润: ${level.profit}")
                logger.info(f"   之前投资: ${previous_amount:.2f}")
                logger.info(f"   目标总额: ${target_total:.2f}")
                logger.info(f"   Token价格: {token_price}")
                logger.info(f"   计算投资: ${amount:.2f}")
                return max(amount, 1.0)  # 最小投资1美元
            else:
                logger.warning(f"{crypto} Token价格异常: {token_price}, 使用固定投资")
                return target_total  # 如果价格异常，直接投资目标总额
                
        except Exception as e:
            logger.error(f"{crypto}计算投资金额失败: {str(e)}")
            return 10.0
    
    async def execute_buy_order(self, crypto: str, token_id: str, amount: float) -> Dict[str, Any]:
        """执行买入订单"""
        try:
            cmd = [
                sys.executable,
                str(self.project_root / 'market_buy_order.py'),
                token_id,
                str(amount)
            ]
            
            logger.info(f"🔄 执行{crypto}买入命令: {amount:.2f} USDC")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                # 检查输出内容中是否包含错误信息
                if "执行市场买单时出错" in result.stdout:
                    error_msg = result.stdout.split("执行市场买单时出错: ")[-1].strip()
                    logger.error(f"❌ {crypto}买入订单执行失败: {error_msg}")
                    return {"success": False, "error": error_msg}
                elif "执行市场卖单时出错" in result.stdout:
                    error_msg = result.stdout.split("执行市场卖单时出错: ")[-1].strip()
                    logger.error(f"❌ {crypto}卖出订单执行失败: {error_msg}")
                    return {"success": False, "error": error_msg}
                elif "完成!" in result.stdout and "错误" not in result.stdout:
                    logger.info(f"✅ {crypto}买入订单执行成功")
                    return {"success": True, "output": result.stdout}
                else:
                    # 检查其他可能的错误信息
                    if "错误" in result.stdout or "失败" in result.stdout or "Exception" in result.stdout:
                        error_msg = result.stdout
                        logger.error(f"❌ {crypto}买入订单执行失败: {error_msg}")
                        return {"success": False, "error": error_msg}
                    else:
                        logger.info(f"✅ {crypto}买入订单执行成功")
                        return {"success": True, "output": result.stdout}
            else:
                logger.error(f"❌ {crypto}买入订单执行失败: {result.stderr}")
                return {"success": False, "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ {crypto}买入订单执行超时")
            return {"success": False, "error": "执行超时"}
        except Exception as e:
            logger.error(f"💥 {crypto}买入订单执行异常: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def process_triggered_levels(self, crypto: str, triggered_levels: List[PriceLevel]):
        """处理触发的级别"""
        for level in triggered_levels:
            try:
                logger.info(f"🎯 处理{crypto} Level {level.level} 交易...")
                
                # 获取token价格
                token_price = await self.get_token_price(level.tokenid)
                
                # 计算投资金额
                investment_amount = await self.calculate_investment_amount(crypto, level, token_price)
                
                # 执行交易
                result = await self.execute_buy_order(crypto, level.tokenid, investment_amount)
                
                # 记录交易
                await self.record_trade(crypto, level, investment_amount, token_price, result)
                
            except Exception as e:
                logger.error(f"💥 处理{crypto} Level {level.level}失败: {str(e)}")
    
    async def record_trade(self, crypto: str, level: PriceLevel, amount: float, token_price: float, result: Dict[str, Any]):
        """记录交易"""
        try:
            record = {
                "timestamp": datetime.now().isoformat(),
                "crypto": crypto,
                "level": level.level,
                "token_id": level.tokenid,
                "target_profit": level.profit,
                "trigger_price": level.trigger_price,
                "investment_amount": amount,
                "token_price": token_price,
                "success": result.get("success", False),
                "error": result.get("error", ""),
                "output": result.get("output", "")
            }
            
            # 添加到内存记录
            self.investment_records[crypto].append(record)
            
            # 保存到文件
            records_file = Path("/root/poly/multi_crypto_trading_records.json")
            
            all_records = []
            if records_file.exists():
                with open(records_file, 'r') as f:
                    try:
                        all_records = json.load(f)
                    except:
                        all_records = []
            
            all_records.append(record)
            
            with open(records_file, 'w') as f:
                json.dump(all_records, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📝 {crypto}交易记录已保存")
            
        except Exception as e:
            logger.error(f"💥 保存{crypto}交易记录失败: {str(e)}")
    
    def should_cleanup_logs(self) -> bool:
        """检查是否需要清理日志"""
        return datetime.now() - self.last_log_cleanup > self.log_cleanup_interval
    
    async def cleanup_logs(self):
        """清理日志文件，只保留重要信息"""
        try:
            log_file = Path("/root/poly/multi_crypto_auto_trading.log")
            if not log_file.exists():
                return
                
            logger.info("🧹 开始清理日志文件...")
            
            # 读取现有日志
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 过滤重要日志 (排除价格监控日志)
            important_lines = []
            for line in lines:
                # 保留的重要日志类型
                if any(keyword in line for keyword in [
                    '启动', '配置', '触发', '执行', '成功', '失败', '错误', '异常',
                    '交易', '投资', '计算', 'Level', '清理', '停止'
                ]):
                    # 排除价格监控日志
                    if not any(exclude in line for exclude in [
                        '当前价格:', '价格更新:', 'DEBUG'
                    ]):
                        important_lines.append(line)
            
            # 如果重要日志超过1000行，只保留最近的800行
            if len(important_lines) > 1000:
                important_lines = important_lines[-800:]
                
            # 写入清理后的日志
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"# 日志已于 {datetime.now().isoformat()} 清理\n")
                f.writelines(important_lines)
            
            # 不再创建备份日志文件，直接清理
            logger.info(f"📦 日志已清理，不再创建备份文件")
            
            self.last_log_cleanup = datetime.now()
            logger.info(f"✅ 日志清理完成，保留 {len(important_lines)} 行重要日志")
            
        except Exception as e:
            logger.error(f"💥 日志清理失败: {str(e)}")
    
    async def monitor_prices(self):
        """主监控循环"""
        logger.info("🚀 开始多币种价格监控...")
        self.monitoring = True
        
        # 首次启动时处理所有Level 0
        for crypto in self.crypto_levels.keys():
            level_0_triggered = self.check_price_triggers(crypto, 0)
            if level_0_triggered:
                await self.process_triggered_levels(crypto, level_0_triggered)
        
        while self.monitoring:
            try:
                # 检查是否需要清理日志
                if self.should_cleanup_logs():
                    await self.cleanup_logs()
                
                # 获取所有币种价格
                prices = await self.get_all_crypto_prices()
                
                # 更新当前价格并检查触发条件
                price_info = []
                for crypto, price in prices.items():
                    if price > 0:
                        self.current_prices[crypto] = price
                        price_info.append(f"{crypto}: ${price:,.2f}")
                        
                        # 检查触发条件
                        triggered_levels = self.check_price_triggers(crypto, price)
                        
                        if triggered_levels:
                            await self.process_triggered_levels(crypto, triggered_levels)
                
                # 每秒记录价格信息
                should_log_price = True
                
                if should_log_price and price_info:
                    logger.info(f"📊 价格监控: {' | '.join(price_info)}")
                
                # 等待下次检查 (每秒刷新)
                await asyncio.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("⏹️ 接收到停止信号")
                break
            except Exception as e:
                logger.error(f"💥 监控循环错误: {str(e)}")
                await asyncio.sleep(5)
        
        logger.info("⏹️ 价格监控已停止")
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False


async def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("🚀 多币种自动交易系统启动 (修正版)")
    logger.info("=" * 60)
    
    try:
        # 创建监控器
        monitor = MultiCryptoPriceMonitor()
        
        # 显示配置信息
        logger.info("📊 监控配置:")
        for crypto, levels in monitor.crypto_levels.items():
            logger.info(f"  {crypto}: {len(levels)} 个级别")
            for level in levels:
                if level.level == 0:
                    logger.info(f"    Level {level.level}: 立即执行 -> 利润 ${level.profit}")
                else:
                    logger.info(f"    Level {level.level}: {crypto} ${level.trigger_price:,} -> 利润 ${level.profit}")
        
        logger.info("🔧 系统修正:")
        logger.info("  ✅ 修正投资公式 (所有级别使用累积公式)")
        logger.info("  ✅ 更换价格源 (Coinbase API，无地区限制)")
        logger.info("  ✅ 添加日志清理 (每小时清理)")
        logger.info("  ✅ 实时价格日志 (每秒记录价格)")
        logger.info("  ✅ 并发价格获取 (提高响应速度)")
        logger.info("  ✅ 解决API限制问题 (429/451错误)")
        
        # 开始监控
        await monitor.monitor_prices()
        
    except KeyboardInterrupt:
        logger.info("\n⏹️ 程序被用户中断")
    except Exception as e:
        logger.error(f"💥 程序执行错误: {str(e)}")
    finally:
        logger.info("⏹️ 程序退出")


if __name__ == "__main__":
    asyncio.run(main()) 