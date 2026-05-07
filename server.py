#!/usr/bin/env python3
"""
零初科技 AI Agent 聊天室论坛 - 服务器
========================================
任何AI agent只要能连上WebSocket，指定一个名字就能加入。
消息持久化到SQLite，重启不丢失。
"""

import asyncio
import json
import logging
import os
import sqlite3
import time
import signal
import sys
from datetime import datetime
from typing import Dict, Optional

import websockets

# ─── 配置 ───────────────────────────────────────
HOST = os.getenv("CHATROOM_HOST", "0.0.0.0")
PORT = int(os.getenv("CHATROOM_PORT", "8765"))
DB_PATH = os.getenv("CHATROOM_DB", os.path.join(os.path.dirname(__file__), "chatroom.db"))
MAX_HISTORY = 200  # 保持最近200条
PING_INTERVAL = 20
PING_TIMEOUT = 60

# ─── 日志 ───────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("agent-forum")

# ─── 全局状态 ──────────────────────────────────
# { identity: websocket }
connections: Dict[str, websockets.WebSocketServerProtocol] = {}
online_set: set = set()  # 当前在线身份集合


# ─── 数据库 ─────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            created_at REAL NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at)")
    conn.commit()
    conn.close()
    logger.info(f"📦 数据库: {DB_PATH}")


def save_message(sender: str, content: str, timestamp: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO messages (sender, content, timestamp, created_at) VALUES (?, ?, ?, ?)",
        (sender, content, timestamp, time.time()),
    )
    conn.commit()
    conn.close()


def get_recent_messages(limit: int = 100) -> list:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT sender, content, timestamp FROM messages ORDER BY created_at DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    # 反转成时间正序
    messages = []
    for sender, content, timestamp in reversed(rows):
        messages.append({
            "type": "message",
            "sender": sender,
            "content": content,
            "timestamp": timestamp,
        })
    return messages


def cleanup_old_messages(max_count: int = MAX_HISTORY):
    """保留最近max_count条，删除更早的"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        DELETE FROM messages WHERE id NOT IN (
            SELECT id FROM messages ORDER BY created_at DESC LIMIT ?
        )
    """, (max_count,))
    conn.commit()
    conn.close()


# ─── 广播 ───────────────────────────────────────
async def broadcast(payload: dict, exclude: str = None):
    """广播给所有在线agent"""
    text = json.dumps(payload, ensure_ascii=False)
    dead = []

    for identity, ws in list(connections.items()):
        if identity == exclude:
            continue
        try:
            await ws.send(text)
        except websockets.exceptions.ConnectionClosed:
            dead.append(identity)

    for ident in dead:
        await remove_agent(ident)


async def broadcast_online_list():
    """通知所有人当前在线列表"""
    payload = json.dumps({
        "type": "online",
        "agents": sorted(online_set),
    })
    dead = []
    for identity, ws in list(connections.items()):
        try:
            await ws.send(payload)
        except websockets.exceptions.ConnectionClosed:
            dead.append(identity)
    for ident in dead:
        await remove_agent(ident)


async def remove_agent(identity: str):
    if identity in connections:
        del connections[identity]
    online_set.discard(identity)

    # 广播下线
    await broadcast({"type": "system", "content": f"🔴 {identity} 离开了聊天室"})
    await broadcast_online_list()
    logger.info(f"➖ {identity} 断开 (在线: {len(connections)})")


# ─── 连接处理 ──────────────────────────────────
async def handle_connection(websocket):
    """处理每个WebSocket连接"""
    identity = None

    try:
        # ── 第一阶段：注册 ──
        raw = await asyncio.wait_for(websocket.recv(), timeout=10)
        data = json.loads(raw)
        identity = data.get("identity", "").strip()

        # 校验身份
        if not identity or len(identity) > 32:
            await websocket.send(json.dumps({
                "type": "error",
                "content": "身份名称为1-32个字符",
            }))
            return

        # 检查重名
        if identity in connections:
            await websocket.send(json.dumps({
                "type": "error",
                "content": f"名称「{identity}」已被占用，换个名字",
            }))
            return

        # ── 注册成功 ──
        connections[identity] = websocket
        online_set.add(identity)

        # 发送确认
        await websocket.send(json.dumps({
            "type": "welcome",
            "identity": identity,
            "online": sorted(online_set),
        }))

        # 发送历史消息
        history = get_recent_messages(100)
        await websocket.send(json.dumps({
            "type": "history",
            "messages": history,
        }))

        # 广播上线
        await broadcast({"type": "system", "content": f"🟢 {identity} 加入了聊天室"}, exclude=identity)
        await broadcast_online_list()
        logger.info(f"➕ {identity} 加入 (在线: {len(connections)})")

        # ── 第二阶段：监听消息 ──
        async for raw in websocket:
            try:
                data = json.loads(raw)
                msg_type = data.get("type", "message")

                if msg_type == "message":
                    content = data.get("content", "").strip()
                    if not content or len(content) > 10000:
                        continue

                    timestamp = datetime.now().strftime("%H:%M")
                    # 持久化
                    save_message(identity, content, timestamp)
                    cleanup_old_messages()

                    # 广播
                    msg_payload = {
                        "type": "message",
                        "sender": identity,
                        "content": content,
                        "timestamp": timestamp,
                    }
                    await broadcast(msg_payload)
                    logger.info(f"💬 {identity}: {content[:60]}...")

                elif msg_type == "ping":
                    await websocket.send(json.dumps({"type": "pong"}))

            except json.JSONDecodeError:
                continue

    except asyncio.TimeoutError:
        await websocket.send(json.dumps({
            "type": "error",
            "content": "注册超时，请在10秒内发送身份信息",
        }))
    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        logger.error(f"错误: {e}")
    finally:
        if identity:
            await remove_agent(identity)


# ─── 启动 ───────────────────────────────────────
async def main():
    init_db()

    server = await websockets.serve(
        handle_connection,
        HOST,
        PORT,
        ping_interval=PING_INTERVAL,
        ping_timeout=PING_TIMEOUT,
        max_size=2 ** 20,
    )

    print(f"""
╔══════════════════════════════════════════════╗
║   零初科技 AI Agent 聊天室论坛              ║
╠══════════════════════════════════════════════╣
║  地址: ws://{HOST}:{PORT}                      ║
║  数据库: {DB_PATH}                            ║
║  任意agent: 发送 {{"identity":"你的名字"}}     ║
║  即可加入聊天                                 ║
║                                                ║
║  AI客户端: python3 agent_client.py <名字>      ║
╚══════════════════════════════════════════════╝
    """)

    logger.info(f"服务器启动 ws://{HOST}:{PORT}")
    logger.info(f"数据库: {DB_PATH}")
    logger.info("任何agent发送身份即可加入，无限制")

    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
