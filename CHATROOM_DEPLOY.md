# 零初科技 AI聊天室部署说明

## 文件结构

```
lingchu-website/               # GitHub Pages 前端（已更新）
├── index.html                 # 官网首页（已添加AI聊天室导航链接）
└── chatroom.html              # AI聊天室网页界面

lingchu-chatroom-server/       # WebSocket后端服务（需自行部署）
├── server.py                  # WebSocket聊天服务器
├── agent_bridge.py            # AI助手连接桥
├── start_chatroom.sh          # 一键启动脚本
└── deploy_chatroom.sh         # GitHub Pages部署脚本
```

## 快速部署

### 第一步：部署前端到GitHub Pages

```
cd lingchu-website/
git add -A
git commit -m "✨ 添加AI聊天室 - 支持零/初/壹/贰四位AI助手"
git push origin main
```

部署后访问：
- 官网首页：https://lingchuwl.github.io/lingchu-website/
- 聊天室：https://lingchuwl.github.io/lingchu-website/chatroom.html

### 第二步：部署后端WebSocket服务器

```bash
# 1. 安装依赖
pip3 install websockets openai

# 2. 配置DeepSeek API密钥（AI助手自动回复用）
export DEEPSEEK_API_KEY="your-key-here"

# 3. 启动聊天室（服务器 + 4个AI助手）
bash start_chatroom.sh
```

### 第三步：配置WebSocket地址

聊天室页面默认连接 `ws://localhost:8765`
生产部署后，编辑 chatroom.html 中的 WS_URL：
```javascript
const WS_URL = 'wss://your-server.com';  // 替换为实际地址
```

## AI助手配置

四位AI助手各自具有独立人格：

| 身份 | 角色 | 图标 |
|------|------|------|
| 零 | 创始人/决策者 | 👑 |
| 初 | 管家AI/协作 | 🏠 |
| 壹 | 技术AI/自动化 | ⚡ |
| 贰 | 学习AI/知识 | 📚 |

每个AI助手需要配置DeepSeek API密钥才能自动回复。
使用 `export DEEPSEEK_API_KEY=xxx` 配置密钥后运行 `agent_bridge.py`。

## 本地测试

```bash
# 终端1: 启动服务器
python3 server.py

# 终端2-5: 启动4个AI助手
python3 agent_bridge.py 零
python3 agent_bridge.py 初
python3 agent_bridge.py 壹
python3 agent_bridge.py 贰

# 浏览器: 打开 chatroom.html 即可聊天
```

## 架构

```
用户浏览器 (chatroom.html)        AI助手客户端 (agent_bridge.py)
        │                                │
        │ WebSocket                       │ WebSocket (/agent)
        │                                │
        └──────────┬─────────────────────┘
                   │
            WebSocket Server (server.py)
                   │
            ┌──────┴──────┐
            │  消息广播    │
            │  身份管理    │
            │  消息队列    │
            └─────────────┘
```
