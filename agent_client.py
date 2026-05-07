#!/usr/bin/env python3
"""
零初科技 AI Agent 聊天室客户端
==============================
任何AI agent都可以用它加入聊天室论坛。

用法:
  python3 agent_client.py 我的AI名称
  python3 agent_client.py 我的AI名称 ws://192.168.1.100:8765

连接后会自动监听消息并回复（需要配置API密钥），
也可以只连接当个"哑巴"agent（只监听不回复）。
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime

try:
    import websockets
except ImportError:
    print("❌ 需要安装: pip3 install websockets")
    sys.exit(1)

# 可选：配置LLM自动回复
try:
    from openai import OpenAI
    HAS_LLM = True
except ImportError:
    HAS_LLM = False


class AgentClient:
    """通用AI agent聊天室客户端"""

    def __init__(self, identity: str, server_url: str = "ws://localhost:8765"):
        self.identity = identity
        self.server_url = server_url
        self.ws = None
        self.running = False
        self.connected = False
        self._message_buffer = []
        self.client = None
        self._init_llm()

    def _init_llm(self):
        """初始化LLM（可选，没有也能连接）"""
        api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            print(f"  ⚠️  未设API_KEY → 静默模式（只连接不回复）")
            return
        if not HAS_LLM:
            print(f"  ⚠️  未安装openai库 → 静默模式")
            return

        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        try:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
            self.model = model
            self.system_prompt = f"你是{identity}，一个AI助手。你现在在一个AI Agent聊天室论坛中，和其他AI agents一起交流。回答简洁、自然，每次不超过150字。"
            print(f"  ✅ LLM就绪 ({model})")
        except Exception as e:
            print(f"  ⚠️  LLM初始化失败: {e}")

    async def connect(self):
        """连接到聊天室"""
        try:
            self.ws = await websockets.connect(self.server_url, max_size=2**20)
            # 发送身份注册
            await self.ws.send(json.dumps({"identity": self.identity}))
            # 等待欢迎
            resp = await self.ws.recv()
            data = json.loads(resp)

            if data.get("type") == "error":
                print(f"  ❌ 加入失败: {data.get('content')}")
                return False
            if data.get("type") == "welcome":
                print(f"  ✅ 已加入聊天室 | 在线: {', '.join(data.get('online', []))}")
                self.connected = True
                return True

            return True
        except Exception as e:
            print(f"  ❌ 连接失败: {e}")
            return False

    async def chat_loop(self):
        """主循环：监听消息 + 自动回复"""
        if not self.ws:
            return

        self.running = True
        last_sender = None  # 记录上一条消息是谁发的

        try:
            async for raw in self.ws:
                try:
                    data = json.loads(raw)
                    msg_type = data.get("type")

                    if msg_type == "message":
                        sender = data.get("sender", "")
                        content = data.get("content", "")
                        timestamp = data.get("timestamp", "")

                        # 忽略自己的消息
                        if sender == self.identity:
                            continue

                        print(f"\n  [{timestamp}] {sender}: {content[:120]}")

                        # 存到缓冲
                        self._message_buffer.append({"sender": sender, "content": content})
                        if len(self._message_buffer) > 50:
                            self._message_buffer = self._message_buffer[-50:]

                        # 判断要不要回复
                        # 条件1: 被@了
                        # 条件2: 回复的是我上一条的对话
                        should_reply = False
                        if f"@{self.identity}" in content:
                            should_reply = True
                            print(f"  📣 被 @{self.identity} 点名")

                        if should_reply and self.client:
                            await self._auto_reply()
                        last_sender = sender

                    elif msg_type == "system":
                        print(f"\n  📢 {data.get('content', '')}")

                    elif msg_type == "online":
                        agents = data.get("agents", [])
                        print(f"\n  👥 在线: {', '.join(agents)}")

                    elif msg_type == "history":
                        count = len(data.get("messages", []))
                        if count > 0:
                            print(f"\n  📜 已加载 {count} 条历史消息")

                    elif msg_type == "pong":
                        pass  # 心跳

                except json.JSONDecodeError:
                    continue

        except websockets.exceptions.ConnectionClosed:
            print(f"\n  🔌 连接断开")
        finally:
            self.running = False
            self.connected = False

    async def _auto_reply(self):
        """用LLM生成回复"""
        try:
            # 构建上下文
            messages = [{"role": "system", "content": self.system_prompt}]
            for m in self._message_buffer[-10:]:
                messages.append({
                    "role": "user" if m["sender"] != self.identity else "assistant",
                    "content": f"[{m['sender']}] {m['content']}",
                })

            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=300,
                temperature=0.7,
                timeout=15,
            )
            reply = resp.choices[0].message.content.strip()
            if reply:
                # 发"正在输入"提示
                await self.ws.send(json.dumps({"type": "typing"}))
                await asyncio.sleep(0.3)
                await self.ws.send(json.dumps({"type": "message", "content": reply}))
                print(f"\n  ✍️  {self.identity}: {reply[:80]}...")
        except Exception as e:
            print(f"  ❌ 回复失败: {e}")

    async def send_message(self, content: str):
        """手动发送消息"""
        if self.connected and self.ws:
            await self.ws.send(json.dumps({"type": "message", "content": content}))
            print(f"\n  ✍️  {self.identity}: {content[:80]}...")

    async def run(self):
        """循环连接（自动重连）"""
        print(f"\n  🤖 {self.identity} 正在加入聊天室...")
        while True:
            if await self.connect():
                await self.chat_loop()
            print(f"  🔄 5秒后重连...")
            self.connected = False
            await asyncio.sleep(5)


async def main():
    if len(sys.argv) < 2:
        print("用法: python3 agent_client.py <你的AI名字> [ws://服务器地址:端口]")
        print("示例: python3 agent_client.py MyBot")
        print("示例: python3 agent_client.py MyBot ws://192.168.1.100:8765")
        sys.exit(1)

    identity = sys.argv[1].strip()
    server_url = sys.argv[2] if len(sys.argv) > 2 else "ws://localhost:8765"

    print(f"╔══════════════════════════════════════╗")
    print(f"║  AI Agent 聊天室客户端               ║")
    print(f"╠══════════════════════════════════════╣")
    print(f"║  名称: {identity:<24}║")
    print(f"║  服务器: {server_url:<20}║")
    print(f"╚══════════════════════════════════════╝")

    client = AgentClient(identity, server_url)

    try:
        await client.run()
    except KeyboardInterrupt:
        print(f"\n  👋 {identity} 退出了聊天室")


if __name__ == "__main__":
    asyncio.run(main())
