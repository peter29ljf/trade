import asyncio
import websockets
import json
import time
import requests
import os
import sys
import logging

# 使用当前工作目录（兼容交互环境）
base_dir = os.getcwd()

# 日志配置
LOG_FILE = os.path.join(base_dir, "btc_monitor.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

WS_URL = "wss://ws.bitget.com/v2/ws/public"
SETTING_FILE = os.path.join(base_dir, "setting.json")

# 读取配置文件
with open(SETTING_FILE, "r") as f:
    settings_raw = f.read().replace("```", "")
    settings = json.loads(settings_raw)

WEBHOOK_URL = settings["webhook"].strip("[]()")  # 去掉多余字符
target_levels = {
    float(level["price"]): {
        "level": level["level"],
        "tokenid": level["tokenid"],
        "profit": level["profit"]
    }
    for level in settings["levels"]
    if level["level"] != 0
}

# 保证每个价格最多发一次
notified_prices = set()

SUBSCRIBE_MSG = {
    "op": "subscribe",
    "args": [
        {
            "instType": "USDT-FUTURES",
            "channel": "ticker",
            "instId": "BTCUSDT"
        }
    ]
}


async def monitor_btc_price():
    while True:
        try:
            async with websockets.connect(WS_URL) as websocket:
                await websocket.send(json.dumps(SUBSCRIBE_MSG))
                logging.info("✅ 已订阅 BTCUSDT ticker 数据")

                last_pong_time = time.time()
                pong_logged = False          # 是否收到过 pong
                verbose_pinglog = True       # 是否打印 ping/pong 日志

                # ping 发送任务
                async def send_ping():
                    nonlocal verbose_pinglog
                    while True:
                        await asyncio.sleep(1)
                        try:
                            await websocket.send("ping")
                            if verbose_pinglog:
                                logging.info("📤 已发送 ping")
                        except Exception as e:
                            logging.error(f"❌ Ping 错误: {e}")
                            break

                ping_task = asyncio.create_task(send_ping())

                while True:
                    if len(notified_prices) == len(target_levels):
                        logging.info("🎉 所有目标价格已触发，程序退出")
                        await asyncio.sleep(1)
                        sys.exit(0)

                    try:
                        msg = await asyncio.wait_for(websocket.recv(), timeout=60)
                        if msg == "pong":
                            last_pong_time = time.time()
                            if not pong_logged:
                                logging.info("📥 收到第一次 pong")
                                pong_logged = True
                                verbose_pinglog = False  # 开始静默
                            continue

                        data = json.loads(msg)
                        if "arg" in data and "data" in data:
                            if data["arg"].get("channel") == "ticker":
                                price = float(data["data"][0]["lastPr"])
                                for target_price in target_levels:
                                    if abs(price - target_price) < 0.01 and target_price not in notified_prices:
                                        logging.info(f"🎯 当前价格 {price} ≈ 目标 {target_price}，发送 webhook")
                                        send_webhook(target_levels[target_price])
                                        notified_prices.add(target_price)

                        # 超过 35 秒未收到 pong，恢复日志打印
                        if time.time() - last_pong_time > 35:
                            verbose_pinglog = True
                            logging.warning("⚠️ 超过 35 秒未收到 pong，准备重连")
                            break

                    except asyncio.TimeoutError:
                        verbose_pinglog = True
                        logging.warning("⚠️ 接收超时，准备重连")
                        break
                    except Exception as e:
                        logging.error(f"❌ 错误: {e}")
                        break

                ping_task.cancel()
        except Exception as e:
            logging.error(f"❌ 连接错误: {e}")
        logging.info("🔁 5 秒后重连...")
        await asyncio.sleep(5)



def send_webhook(payload):
    try:
        res = requests.post(WEBHOOK_URL, json=payload)
        logging.info(f"✅ Webhook 已发送: level={payload['level']}, 状态码={res.status_code}")
    except Exception as e:
        logging.error(f"❌ Webhook 发送失败: {e}")


# 手动测试函数：发送指定 level 的 webhook
def test_send_level(level_num):
    for level in settings["levels"]:
        if level["level"] == level_num:
            logging.info(f"🧪 测试发送 level {level_num}")
            send_webhook({
                "level": level["level"],
                "tokenid": level["tokenid"],
                "profit": level["profit"]
            })
            return
    logging.warning(f"⚠️ level {level_num} 未找到")


if __name__ == "__main__":
    # 修改这里可以手动测试某个 level
    # test_send_level(1)

    asyncio.run(monitor_btc_price())
