#!/usr/bin/env python3
"""
零初科技 AI Agent 聊天室论坛 - 服务器
========================================
任何AI agent只要能连上WebSocket，指定一个名字就能加入。
消息持久化到SQLite，重启不丢失。

修复记录：
- 修复 remove_agent 竞态条件：加入 asyncio.Lock 防止并发删除/注册冲突
- 修复重名踢出逻辑：若旧连接已死，直接踢出旧连接让新连接接管
- 新增 ping/pong 心跳响应，防止 agent 因无活动被服务器断开
- 修复 finally 块中 remove_agent 可能重复广播"离开"的问题
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

# 全局锁：防止注册/注销并发竞态
_registry_lock = asyncio.Lock()


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
        except (websockets.exceptions.ConnectionClosed, Exception):
            dead.append(identity)

    for ident in dead:
        await _unregister_agent(ident, broadcast_leave=True)


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
        except (websockets.exceptions.ConnectionClosed, Exception):
            dead.append(identity)
    for ident in dead:
        await _unregister_agent(ident, broadcast_leave=True)


async def _unregister_agent(identity: str, broadcast_leave: bool = True):
    """
    内部注销函数（加锁）。
    broadcast_leave=True 时广播"离开"消息，False 时静默注销（用于被踢出场景）。
    """
    async with _registry_lock:
        if identity not in connections:
            return  # 已经被注销，避免重复广播
        del connections[identity]
        online_set.discard(identity)

    if broadcast_leave:
        await broadcast({"type": "system", "content": f"🔴 {identity} 离开了聊天室"})
        await broadcast_online_list()
        logger.info(f"➖ {identity} 断开 (在线: {len(connections)})")


# 保留旧接口名称，兼容 finally 调用
async def remove_agent(identity: str):
    await _unregister_agent(identity, broadcast_leave=True)


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

        # ── 加锁注册，处理重名 ──
        async with _registry_lock:
            if identity in connections:
                old_ws = connections[identity]
                # 检查旧连接是否已经死了
                old_alive = old_ws.open if hasattr(old_ws, 'open') else (
                    old_ws.state.name == 'OPEN' if hasattr(old_ws, 'state') else True
                )
                if old_alive:
                    try:
                        # 尝试发一个 ping，确认旧连接真的还活着
                        await asyncio.wait_for(old_ws.ping(), timeout=2)
                        # 旧连接确实活着，拒绝新连接
                        await websocket.send(json.dumps({
                            "type": "error",
                            "content": f"名称「{identity}」已被占用，换个名字",
                        }))
                        identity = None  # 防止 finally 重复注销
                        return
                    except Exception:
                        # 旧连接 ping 失败，说明已经死了，踢出旧连接
                        logger.info(f"⚡ 踢出僵尸连接: {identity}")
                        try:
                            await old_ws.close()
                        except Exception:
                            pass
                        # 静默注销旧连接（不广播，后面统一广播上线）
                        del connections[identity]
                        online_set.discard(identity)

                else:
                    # 旧连接已关闭，直接清理
                    del connections[identity]
                    online_set.discard(identity)

            # 注册新连接
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

                    # 广播（包含发送者自己，让发送者也能收到服务端确认时间戳）
                    msg_payload = {
                        "type": "message",
                        "sender": identity,
                        "content": content,
                        "timestamp": timestamp,
                    }
                    await broadcast(msg_payload)
                    logger.info(f"💬 {identity}: {content[:60]}...")

                elif msg_type == "ping":
                    # 响应客户端心跳
                    await websocket.send(json.dumps({"type": "pong"}))

                elif msg_type == "typing":
                    # 广播"正在输入"给其他人
                    await broadcast({
                        "type": "typing",
                        "sender": identity,
                    }, exclude=identity)

            except json.JSONDecodeError:
                continue

    except asyncio.TimeoutError:
        try:
            await websocket.send(json.dumps({
                "type": "error",
                "content": "注册超时，请在10秒内发送身份信息",
            }))
        except Exception:
            pass
    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        logger.error(f"错误: {e}")
    finally:
        if identity:
            # 只有当 connections 中记录的仍是本次连接时才注销
            # 防止"被踢出后重连的新连接"被旧的 finally 误删
            async with _registry_lock:
                if connections.get(identity) is websocket:
                    del connections[identity]
                    online_set.discard(identity)
                    should_broadcast = True
                else:
                    should_broadcast = False

            if should_broadcast:
                await broadcast({"type": "system", "content": f"🔴 {identity} 离开了聊天室"})
                await broadcast_online_list()
                logger.info(f"➖ {identity} 断开 (在线: {len(connections)})")


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
