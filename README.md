# remotion-studio

基于 **FastAPI + Remotion 4.0.532 (Latest) + MCP** 的企业级通用视频生成与动效引擎。

深度融合并吸收社区主流 Remotion 实践精髓，提供两种核心视频制作模式：
1. **声明式场景模式 (`create_video_from_spec`)**：输入 JSON Spec，系统自动结合 8 大专业主题色彩、全平台画幅自适应与 10 大商业级动画组件库（标题、数据图表、代码打字机、竞品对比、KPI看板、时间轴路线图、特性网格、引言、片尾等），支持背景音乐（BGM）与自动音量淡出，一键出片；
2. **自由式代码模式 (`create_video_from_code`)**：直接提供 React / Remotion TSX 源码多文件字典，预装并全面开放 Remotion 4.x 官方全生态扩展包（`@remotion/shapes`, `@remotion/paths`, `@remotion/media-utils`, `@remotion/google-fonts`, `@remotion/transitions`, `lucide-react`），支持任何自定义高难度物理动效；
3. **企业级高并发与稳定性架构**：
   - **Tini Init 守护**：容器级自动回收无头 Chromium 僵尸进程，彻底杜绝进程泄露；
   - **2GB 共享内存 (`shm_size: 2gb`)**：彻底避免高分辨率/多光栅线程下 Chromium 崩溃；
   - **异步信号量限流**：后台渲染与视频点播完全解耦，播放/下载采用 HTTP 206 异步流式分段加载，绝对不堵塞 MCP 工具响应与多客户端并发；
   - **智能编译加速**：Remotion `--bundle-cache` 与 `--x264-preset=veryfast` 结合，构建与编码提速 30%~50%；
   - **智能入口桥接**：自由代码模式支持任意入口文件名与默认/具名组件导出，自动生成转接适配层。

生成后自动返回 **可在线播放与分段加载的视频 URL、直接下载链接、逐帧提取的高清封面图与排版良好的 Markdown**，并内置现代化管理后台（SPA）。


---

## 🚀 快速开始

### 方式一：Docker Compose（推荐，内置 Chromium、FFmpeg 与中文字体）

```bash
docker compose up -d --build
```
- 服务端点：`http://127.0.0.1:48001`
- MCP 端点：`http://127.0.0.1:48001/mcp`
- 管理后台：`http://127.0.0.1:48001/admin` 或 `/manage`
- API 文档：`http://127.0.0.1:48001/docs`

### 方式二：本地运行

```bash
# 1. 安装 Python 依赖
pip install -r requirements.txt

# 2. 安装 Remotion Node 依赖
cd remotion_engine
npm install
cd ..

# 3. 启动服务
uvicorn app:app --host 0.0.0.0 --port 48001 --reload
```

---

## 🔌 MCP 客户端配置（Cherry Studio / Claude Desktop / Cursor）

在客户端 MCP 配置中添加：

```json
{
  "mcpServers": {
    "remotion-studio": {
      "type": "http",
      "url": "http://<你的服务器IP或域名>:48001/mcp"
    }
  }
}
```

若配置了 `AUTH_KEY`，添加鉴权 Header：

```json
{
  "mcpServers": {
    "remotion-studio": {
      "type": "http",
      "url": "http://<你的服务器IP或域名>:48001/mcp",
      "headers": {
        "Authorization": "Bearer 你的AUTH_KEY"
      }
    }
  }
}
```

---

## 🛠️ 核心 MCP 工具与规范

| 工具名 | 类型 | 说明 |
| --- | --- | --- |
| `create_video_from_spec` | 制作 | 依据 JSON Spec 生成视频，返回播放/下载链接与封面图 Markdown |
| `create_video_from_code` | 制作 | 依据 React 源码多文件字典编译渲染视频 |
| `get_video_guide` | 指南 | 获取 8 大主题色彩、全平台画幅、场景组件与设计系统总览 |
| `get_themes_and_templates` | 模板 | 获取 8 套行业主题色彩（科技、赛博、金融、极简等）与示例模板 |
| `list_videos` | 资产 | 查看与检索已生成的视频资产清单 |
| `delete_video` | 资产 | 删除指定的视频实体及其封面图 |
| `rule_react_code` | 规范 | Remotion 多文件 React 项目结构与代码规范 |
| `rule_remotion_animations` | 规范 | 基于帧（useCurrentFrame）驱动的动画核心原理 |
| `rule_remotion_timing` | 规范 | interpolate, spring 物理弹簧阻尼与缓动时序控制指南 |
| `rule_remotion_sequencing` | 规范 | Sequence 多场景分幕、嵌套与时间轴编排指南 |
| `rule_remotion_transitions` | 规范 | Fade, Slide, Wipe 等平滑转场动画指南 |
| `rule_remotion_text_animations` | 规范 | 打字机字效与动态文本效果指南 |
| `rule_remotion_trimming` | 规范 | 利用 Sequence 负偏移裁剪素材指南 |

---

## 🧩 10 大声明式商业场景组件

`create_video_from_spec` 内置涵盖主流视频制作场景的动画组件：

| 组件名称 (`type`) | 典型用途 | 核心入参 (Props) |
| --- | --- | --- |
| `TitleScene` | 片头震撼定场与章节过渡 | `title`, `subtitle`, `badge`, `variant(gradient/centered/left/bold)`, `animation` |
| `BarChart` | 垂直数据柱状图升活动效 | `title`, `subtitle`, `data: [{label, value}]` |
| `HorizontalBarChart` | 横向排行榜与进度条对比 | `title`, `subtitle`, `data: [{label, value}]` |
| `PieChart` / `DonutChart` | 环形/饼图占比分布看板 | `title`, `subtitle`, `data: [{label, value}]` |
| `LineChart` | 高质感发光折线走势图 | `title`, `subtitle`, `data: [{label, value}]` |
| `CodeBlock` | macOS 风格代码打字机视窗 | `title`, `filename`, `language`, `code`, `isTyping` |
| `ComparisonCard` | 双栏竞品对比、VS、Before-After | `title`, `subtitle`, `vsBadge`, `left: {...}`, `right: {...}` |
| `MetricCard` | 商业 KPI 大数字滚动卡片与增减标识 | `title`, `subtitle`, `metrics: [{label, value, prefix, suffix, change, changeLabel, isPositive, helperText}]` |
| `Timeline` | 里程碑演进与霓虹发光节点路线图 | `title`, `subtitle`, `items: [{date, title, description, badge, active}]` |
| `FeatureList` | 核心特性矩阵卡片与矢量图标徽章 | `title`, `subtitle`, `columns`, `features: [{title, description, badge, icon}]` |
| `QuoteCard` | 权威引述、名言与客户证言卡片 | `quote`, `author`, `title`, `avatar`, `company` |
| `TextOverlay` | 核心观点大字报与金句加粗高亮 | `headline`, `subheadline`, `style(badge/quote/minimal)` |
| `EndScreen` | 片尾关注号召、订阅呼吸按钮 | `title`, `channel`, `cta`, `social` |

> 🎵 **背景音乐 (BGM)**：在 Spec 根节点设置 `audioUrl`（或 `bgm`）及可选的 `audioVolume: 0.3`，系统自动完成音频循环混音并在视频结尾前自动平滑淡出。

---

## 🎨 8 大主题色彩与画幅体系


### 色彩主题
- `tech`: 前沿科技（深板岩蓝底、电光青与冷光蓝高亮）
- `cyberpunk`: 赛博霓虹（暗紫底、霓虹粉与青紫双色碰撞）
- `finance`: 金融商业（深海藏青底、翡翠绿与琥珀金）
- `minimal`: 极简高级黑（炭黑底、纯白文字与银灰层次）
- `business`: 商务深蓝（企业宝蓝、纯白与天青色）
- `education`: 知识学院（深青绿底、薄荷绿与明黄）
- `lifestyle`: 活力潮流（日落暗红底、珊瑚粉与暖橙）
- `gaming`: 电竞先锋（黑曜石底、荧光绿与烈焰红）

### 画幅平台
- `youtube` / `landscape`: 标准横屏 `1920x1080` (16:9)
- `tiktok` / `shorts` / `portrait`: 标准竖屏短视频 `1080x1920` (9:16)
- `instagram_square` / `square`: 社交正方形 `1080x1080` (1:1)

---

## 🖥️ 在线视频资产管理后台

访问 `http://<服务器IP或域名>:48001/admin` 或 `/manage` 即可进入管理中心：
- 🕒 **时间倒序呈现**：最新生成的视频展示在首位；
- ▶️ **内置 HTML5 全功能播放器**：支持进度拖拽（HTTP 206 毫秒级寻道）、倍速、音量与全屏播放；
- 💻 **源码 / Spec 在线查看器**：可一键切换查看生成该视频的完整 React 源码或 JSON Spec；
- 🔗 **一键直链复制**：支持一键复制在线播放链接、下载链接以及适配 GitHub / 知识库的 Markdown 语法；
- 🗑️ **批量彻底删除**：支持多选勾选、全选并安全彻底清理视频实体文件及封面图；
- 🔒 **安全凭证支持**：配置 `AUTH_KEY` 时自动激活密码验证锁。

---

## 📋 环境变量

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `PORT` | `48001` | 服务监听端口 |
| `BASE_URL` | *(自动识别)* | 外部访问 Base URL（留空则从每次 HTTP 请求头识别） |
| `AUTH_KEY` | *(留空)* | 访问鉴权密钥。留空免密放行；非空时 `/mcp` 与后台启用 Bearer 凭证 |
| `REMOTION_WORKSPACE` | `/app/data` | 工作目录（挂载数据持久化） |
| `REMOTION_OUTPUT_DIR` | `/app/data/output` | MP4 视频与封面图存储路径 |
| `REMOTION_STORE_DIR` | `/app/data/store` | 视频资产元数据索引路径 |
| `PUPPETEER_EXECUTABLE_PATH` | `/usr/bin/chromium` | 无头浏览器可执行路径（Linux/Docker） |
| `RENDER_TIMEOUT` | `120` | 单个视频渲染超时秒数（可通过环境变量全局配置，也支持 MCP 工具参数单独指定） |
| `REMOTION_CONCURRENCY` | `50%` | Remotion 内部并发渲染标签数（支持百分比如 `50%` 或具体数值如 `8`） |
| `MAX_CONCURRENT_RENDERS` | `2` | 异步信号量允许的最大并行渲染任务数（防止多客户端打爆 CPU/内存） |


---

## 🌐 Nginx 反向代理配置

若通过 Nginx 反向代理，需开启 **Streamable HTTP / SSE 流式传输** 并关闭缓冲：

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name _;

    client_max_body_size 100m;

    location / {
        proxy_pass http://127.0.0.1:48001;

        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $http_host;

        # MCP 流式传输核心配置（必须关闭缓冲）
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding on;

        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }
}
```
