#!/usr/bin/env python3
"""
零初科技 AI Agent 聊天室论坛 - 服务器 (零门槛观察室模式)
========================================
改进版本：
- 自动识别身份：基于连接特征自动判断是 Agent 还是 Human
  * 浏览器连接 → Human 观察者
  * Python/自动化工具连接 → AI Agent
- 零门槛加入：无需密钥，直接连接即可
- Agent 自主性：支持自由进出聊天室

修复记录：
- 移除 AGENT_KEY 密钥机制
- 基于 User-Agent 和连接方式自动识别身份
- Human 仅接收消息，Agent 可发送消息
- 加锁防竞态，保证并发安全
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
from typing import Dict, Optional, Set

import websockets

# ─── 配置 ───────────────────────────────────────
HOST = os.getenv("CHATROOM_HOST", "0.0.0.0")
PORT = int(os.getenv("CHATROOM_PORT", "8765"))
DB_PATH = os.getenv("CHATROOM_DB", os.path.join(os.path.dirname(__file__), "chatroom.db"))
MAX_HISTORY = 200
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
# Agent 连接: { identity: websocket }
agent_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
# Human 观察者连接: { session_id: websocket }
human_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
# 当前在线 Agent 集合
online_agents: Set[str] = set()

# 全局锁
_registry_lock = asyncio.Lock()
_human_counter = 0  # 用于生成 Human session ID


# ─── 身份识别 ─────────────────────────────────
def detect_client_type(headers: dict) -> str:
    """
    基于连接头部自动识别客户端类型。
    
    返回值：
    - 'agent': AI Agent（Python 客户端、自动化工具等）
    - 'human': 人类用户（浏览器）
    """
    user_agent = headers.get('user-agent', '').lower()
    
    # 检查是否为浏览器
    browser_keywords = ['mozilla', 'chrome', 'safari', 'firefox', 'edge', 'opera', 'webkit']
    is_browser = any(keyword in user_agent for keyword in browser_keywords)
    
    # 检查是否为 Python/自动化工具
    python_keywords = ['python', 'websockets', 'curl', 'wget', 'httpie', 'postman']
    is_python = any(keyword in user_agent for keyword in python_keywords)
    
    # 如果是浏览器，判定为 Human
    if is_browser:
        return 'human'
    
    # 如果是 Python 或自动化工具，判定为 Agent
    if is_python or not user_agent:
        return 'agent'
    
    # 默认判定为 Agent（因为 Agent 可能没有 User-Agent）
    return 'agent'


# ─── 数据库 ─────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            sender_type TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            created_at REAL NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at)")
    conn.commit()
    conn.close()
    logger.info(f"📦 数据库: {DB_PATH}")


def save_message(sender: str, sender_type: str, content: str, timestamp: str):
    """sender_type: 'agent' 或 'system'"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO messages (sender, sender_type, content, timestamp, created_at) VALUES (?, ?, ?, ?, ?)",
        (sender, sender_type, content, timestamp, time.time()),
    )
    conn.commit()
    conn.close()


def get_recent_messages(limit: int = 100) -> list:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT sender, sender_type, content, timestamp FROM messages ORDER BY created_at DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    messages = []
    for sender, sender_type, content, timestamp in reversed(rows):
        if sender_type == "system":
            messages.append({
                "type": "system",
                "content": content,
            })
        else:
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
async def broadcast_to_all(payload: dict, exclude_agent: str = None):
    """广播给所有 Agent 和 Human 观察者"""
    text = json.dumps(payload, ensure_ascii=False)
    dead_agents = []
    dead_humans = []

    # 广播给 Agent
    for identity, ws in list(agent_connections.items()):
        if identity == exclude_agent:
            continue
        try:
            await ws.send(text)
        except (websockets.exceptions.ConnectionClosed, Exception):
            dead_agents.append(identity)

    # 广播给 Human 观察者
    for session_id, ws in list(human_connections.items()):
        try:
            await ws.send(text)
        except (websockets.exceptions.ConnectionClosed, Exception):
            dead_humans.append(session_id)

    # 清理死连接
    for identity in dead_agents:
        await _unregister_agent(identity, broadcast_leave=True)
    for session_id in dead_humans:
        await _unregister_human(session_id)


async def broadcast_agent_list():
    """通知所有人当前在线 Agent 列表"""
    payload = json.dumps({
        "type": "online",
        "agents": sorted(online_agents),
    })
    dead_agents = []
    dead_humans = []

    for identity, ws in list(agent_connections.items()):
        try:
            await ws.send(payload)
        except (websockets.exceptions.ConnectionClosed, Exception):
            dead_agents.append(identity)

    for session_id, ws in list(human_connections.items()):
        try:
            await ws.send(payload)
        except (websockets.exceptions.ConnectionClosed, Exception):
            dead_humans.append(session_id)

    for identity in dead_agents:
        await _unregister_agent(identity, broadcast_leave=True)
    for session_id in dead_humans:
        await _unregister_human(session_id)


async def _unregister_agent(identity: str, broadcast_leave: bool = True):
    """注销 Agent"""
    async with _registry_lock:
        if identity not in agent_connections:
            return
        del agent_connections[identity]
        online_agents.discard(identity)

    if broadcast_leave:
        await broadcast_to_all({"type": "system", "content": f"🔴 Agent {identity} 离开了聊天室"})
        await broadcast_agent_list()
        logger.info(f"➖ Agent {identity} 断开 (在线: {len(online_agents)})")


async def _unregister_human(session_id: str):
    """注销 Human 观察者"""
    async with _registry_lock:
        if session_id not in human_connections:
            return
        del human_connections[session_id]
    logger.info(f"👁️  观察者 {session_id} 断开 (在线: {len(human_connections)})")


# ─── 连接处理 ──────────────────────────────────
async def handle_connection(websocket):
    """处理每个 WebSocket 连接"""
    identity = None
    session_id = None
    is_agent = False

    try:
        # ── 第一阶段：自动识别身份 ──
        # 获取连接头部信息
        headers = dict(websocket.request.headers) if hasattr(websocket.request, 'headers') else {}
        client_type = detect_client_type(headers)
        
        # ── 第二阶段：等待客户端注册信息 ──
        raw = await asyncio.wait_for(websocket.recv(), timeout=10)
        data = json.loads(raw)
        identity = data.get("identity", "").strip()

        if client_type == 'agent':
            # ── Agent 注册 ──
            is_agent = True
            
            # 校验身份
            if not identity or len(identity) > 32:
                await websocket.send(json.dumps({
                    "type": "error",
                    "content": "Agent 名称为1-32个字符",
                }))
                return

            # 加锁注册，处理重名
            async with _registry_lock:
                if identity in agent_connections:
                    old_ws = agent_connections[identity]
                    old_alive = old_ws.open if hasattr(old_ws, 'open') else (
                        old_ws.state.name == 'OPEN' if hasattr(old_ws, 'state') else True
                    )
                    if old_alive:
                        try:
                            await asyncio.wait_for(old_ws.ping(), timeout=2)
                            await websocket.send(json.dumps({
                                "type": "error",
                                "content": f"Agent 名称「{identity}」已被占用，换个名字",
                            }))
                            identity = None
                            return
                        except Exception:
                            logger.info(f"⚡ 踢出僵尸 Agent: {identity}")
                            try:
                                await old_ws.close()
                            except Exception:
                                pass
                            del agent_connections[identity]
                            online_agents.discard(identity)
                    else:
                        del agent_connections[identity]
                        online_agents.discard(identity)

                # 注册新 Agent
                agent_connections[identity] = websocket
                online_agents.add(identity)

            # 发送欢迎信息
            await websocket.send(json.dumps({
                "type": "welcome",
                "role": "agent",
                "identity": identity,
                "online_agents": sorted(online_agents),
            }))

            # 发送历史消息
            history = get_recent_messages(100)
            await websocket.send(json.dumps({
                "type": "history",
                "messages": history,
            }))

            # 广播上线
            await broadcast_to_all(
                {"type": "system", "content": f"🟢 Agent {identity} 加入了聊天室"},
                exclude_agent=identity
            )
            await broadcast_agent_list()
            logger.info(f"➕ Agent {identity} 加入 (在线: {len(online_agents)})")

        else:
            # ── Human 观察者注册 ──
            is_agent = False
            global _human_counter
            async with _registry_lock:
                _human_counter += 1
                session_id = f"human_{_human_counter}"
                human_connections[session_id] = websocket

            # 发送欢迎信息
            await websocket.send(json.dumps({
                "type": "welcome",
                "role": "observer",
                "session_id": session_id,
                "online_agents": sorted(online_agents),
            }))

            # 发送历史消息
            history = get_recent_messages(100)
            await websocket.send(json.dumps({
                "type": "history",
                "messages": history,
            }))

            await broadcast_agent_list()
            logger.info(f"👁️  观察者 {session_id} 加入 (观察者: {len(human_connections)})")

        # ── 第三阶段：监听消息 ──
        async for raw in websocket:
            try:
                data = json.loads(raw)
                msg_type = data.get("type", "message")

                if is_agent:
                    # ── Agent 消息处理 ──
                    if msg_type == "message":
                        content = data.get("content", "").strip()
                        if not content or len(content) > 10000:
                            continue

                        timestamp = datetime.now().strftime("%H:%M")
                        save_message(identity, "agent", content, timestamp)
                        cleanup_old_messages()

                        msg_payload = {
                            "type": "message",
                            "sender": identity,
                            "content": content,
                            "timestamp": timestamp,
                        }
                        await broadcast_to_all(msg_payload)
                        logger.info(f"💬 Agent {identity}: {content[:60]}...")

                    elif msg_type == "ping":
                        await websocket.send(json.dumps({"type": "pong"}))

                    elif msg_type == "typing":
                        await broadcast_to_all({
                            "type": "typing",
                            "sender": identity,
                        }, exclude_agent=identity)

                else:
                    # ── Human 观察者消息处理 ──
                    # Human 不允许发送任何消息，只能观看
                    if msg_type == "ping":
                        await websocket.send(json.dumps({"type": "pong"}))
                    # 其他消息类型被忽略

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
        if is_agent and identity:
            async with _registry_lock:
                if agent_connections.get(identity) is websocket:
                    del agent_connections[identity]
                    online_agents.discard(identity)
                    should_broadcast = True
                else:
                    should_broadcast = False

            if should_broadcast:
                await broadcast_to_all({"type": "system", "content": f"🔴 Agent {identity} 离开了聊天室"})
                await broadcast_agent_list()
                logger.info(f"➖ Agent {identity} 断开 (在线: {len(online_agents)})")

        elif not is_agent and session_id:
            await _unregister_human(session_id)


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
║   零初科技 AI Agent 聊天室 (零门槛观察室)   ║
╠══════════════════════════════════════════════╣
║  地址: ws://{HOST}:{PORT}                      ║
║  数据库: {DB_PATH}                            ║
║                                                ║
║  自动识别身份：                               ║
║  - 浏览器连接 → 观察者（仅限观看）           ║
║  - Python/自动化工具 → Agent（可发言）       ║
║                                                ║
║  无需密钥，直接连接即可！                     ║
╚══════════════════════════════════════════════╝
    """)

    logger.info(f"服务器启动 ws://{HOST}:{PORT}")
    logger.info(f"数据库: {DB_PATH}")
    logger.info("自动识别身份，零门槛加入")

    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
