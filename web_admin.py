# -*- coding: utf-8 -*-
"""现代化 Remotion 视频资产在线管理后台单页应用 (SPA)。

无需任何外部 CDN 依赖，纯内置原生 HTML5 + CSS3 + Vanilla JS，
支持：
- 严格按时间倒序展示已生成视频列表；
- 视频高清播放灯箱（带时间轴、播放/暂停、倍速、全屏）；
- 源码 / Spec 在线查看器；
- 批量勾选与一键批量删除；
- 复制播放链接、下载链接与 Markdown 代码；
- AUTH_KEY 访问凭证安全验证与本地持久化。
"""

def get_admin_html() -> str:
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>Remotion Studio · 视频资产管理中心</title>
  <style>
    :root {
      --bg: #0b0f19;
      --surface: #111827;
      --surface-subtle: #1f2937;
      --surface-hover: #283548;
      --border: #374151;
      --border-focus: #38bdf8;
      --primary: #0284c7;
      --primary-hover: #0369a1;
      --primary-light: #38bdf8;
      --accent: #818cf8;
      --danger: #ef4444;
      --danger-hover: #dc2626;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --badge-bg: #1e293b;
      --radius: 12px;
      --shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      background-color: var(--bg);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    /* 顶部导航 */
    header {
      background: rgba(17, 24, 39, 0.85);
      backdrop-filter: blur(14px);
      border-bottom: 1px solid var(--border);
      position: sticky;
      top: 0;
      z-index: 40;
      padding: 0.85rem 1.75rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 0.85rem;
      text-decoration: none;
      color: inherit;
    }
    .brand-icon {
      width: 2.3rem;
      height: 2.3rem;
      background: linear-gradient(135deg, #0284c7, #818cf8);
      border-radius: 9px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      font-size: 1.25rem;
      color: #fff;
      box-shadow: 0 0 14px rgba(56, 189, 248, 0.45);
    }
    .brand-title {
      font-size: 1.15rem;
      font-weight: 700;
      letter-spacing: -0.02em;
    }
    .brand-subtitle {
      font-size: 0.75rem;
      color: var(--text-muted);
    }
    .header-actions {
      display: flex;
      align-items: center;
      gap: 0.85rem;
    }
    .search-box {
      position: relative;
    }
    .search-input {
      background: var(--surface-subtle);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 0.45rem 0.85rem 0.45rem 2.2rem;
      border-radius: var(--radius);
      font-size: 0.85rem;
      width: 220px;
      transition: all 0.2s ease;
    }
    .search-input:focus {
      outline: none;
      border-color: var(--border-focus);
      width: 280px;
      box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2);
    }
    .search-icon {
      position: absolute;
      left: 0.75rem;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-dim);
      font-size: 0.85rem;
      pointer-events: none;
    }
    .btn {
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
      padding: 0.45rem 0.9rem;
      border-radius: var(--radius);
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
      border: 1px solid transparent;
      transition: all 0.2s ease;
      text-decoration: none;
    }
    .btn-secondary {
      background: var(--surface-subtle);
      border-color: var(--border);
      color: var(--text);
    }
    .btn-secondary:hover {
      background: var(--surface-hover);
      border-color: var(--border-focus);
    }
    .btn-primary {
      background: var(--primary);
      color: #fff;
    }
    .btn-primary:hover {
      background: var(--primary-hover);
      box-shadow: 0 0 12px rgba(56, 189, 248, 0.4);
    }
    .btn-danger {
      background: rgba(239, 68, 68, 0.15);
      border-color: rgba(239, 68, 68, 0.4);
      color: #f87171;
    }
    .btn-danger:hover {
      background: var(--danger);
      color: #fff;
    }

    /* 状态与统计栏 */
    .stat-bar {
      display: flex;
      align-items: center;
      gap: 1.25rem;
      padding: 0.75rem 1.75rem;
      background: rgba(17, 24, 39, 0.5);
      border-bottom: 1px solid rgba(55, 65, 81, 0.5);
      font-size: 0.82rem;
      color: var(--text-muted);
    }
    .stat-pill {
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }
    .stat-val {
      color: var(--primary-light);
      font-weight: 700;
    }

    /* 批量操作浮条 */
    .batch-bar {
      position: sticky;
      top: 56px;
      z-index: 35;
      background: #1e293b;
      border-bottom: 1px solid var(--border-focus);
      padding: 0.65rem 1.75rem;
      display: none;
      align-items: center;
      justify-content: space-between;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
      animation: slideDown 0.25s ease-out;
    }
    .batch-bar.active { display: flex; }
    @keyframes slideDown {
      from { transform: translateY(-100%); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }

    /* 主体容器 */
    main {
      flex: 1;
      padding: 1.5rem 1.75rem;
      max-width: 1440px;
      margin: 0 auto;
      width: 100%;
    }

    /* 视频卡片网格 */
    .video-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 1.35rem;
    }

    .video-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: hidden;
      display: flex;
      flex-direction: column;
      position: relative;
      transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
      box-shadow: var(--shadow);
    }
    .video-card:hover {
      transform: translateY(-4px);
      border-color: var(--border-focus);
      box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5), 0 0 15px rgba(56, 189, 248, 0.2);
    }

    /* 封面预览区域 */
    .card-preview {
      position: relative;
      width: 100%;
      aspect-ratio: 16 / 9;
      background: #000;
      overflow: hidden;
      cursor: pointer;
    }
    .card-img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      transition: transform 0.3s ease;
    }
    .video-card:hover .card-img {
      transform: scale(1.04);
    }

    /* 浮动勾选框 */
    .card-checkbox-wrap {
      position: absolute;
      top: 10px;
      left: 10px;
      z-index: 10;
    }
    .card-checkbox {
      width: 20px;
      height: 20px;
      cursor: pointer;
      accent-color: var(--primary-light);
    }

    /* 播放按钮浮层 */
    .play-overlay {
      position: absolute;
      inset: 0;
      background: rgba(0, 0, 0, 0.35);
      display: flex;
      align-items: center;
      justify-content: center;
      opacity: 0;
      transition: opacity 0.2s ease;
    }
    .video-card:hover .play-overlay {
      opacity: 1;
    }
    .play-circle {
      width: 52px;
      height: 52px;
      border-radius: 50%;
      background: rgba(56, 189, 248, 0.9);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      font-size: 22px;
      padding-left: 4px;
      box-shadow: 0 0 20px rgba(56, 189, 248, 0.6);
      transform: scale(0.9);
      transition: transform 0.2s ease;
    }
    .video-card:hover .play-circle {
      transform: scale(1);
    }

    /* 标签徽章 */
    .card-badges {
      position: absolute;
      bottom: 8px;
      right: 8px;
      display: flex;
      gap: 6px;
      z-index: 5;
    }
    .badge {
      background: rgba(15, 23, 42, 0.85);
      border: 1px solid rgba(255, 255, 255, 0.15);
      backdrop-filter: blur(8px);
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 0.72rem;
      font-weight: 700;
      color: #fff;
    }
    .badge-mode {
      background: rgba(2, 132, 199, 0.8);
      border-color: rgba(56, 189, 248, 0.4);
    }

    /* 卡片内容信息 */
    .card-body {
      padding: 1rem 1.15rem;
      display: flex;
      flex-direction: column;
      flex: 1;
      justify-content: space-between;
    }
    .card-title {
      font-size: 0.98rem;
      font-weight: 700;
      line-height: 1.35;
      margin-bottom: 0.4rem;
      overflow: hidden;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      color: var(--text);
    }
    .card-meta {
      font-size: 0.78rem;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: 0.5rem;
      padding-top: 0.5rem;
      border-top: 1px solid rgba(55, 65, 81, 0.4);
    }

    /* 卡片底栏操作按钮 */
    .card-actions {
      display: flex;
      align-items: center;
      gap: 0.4rem;
      margin-top: 0.75rem;
    }
    .btn-sm {
      padding: 0.35rem 0.65rem;
      font-size: 0.76rem;
      border-radius: 8px;
      flex: 1;
      text-align: center;
      justify-content: center;
    }

    /* 空状态 */
    .empty-state {
      text-align: center;
      padding: 5rem 1rem;
      color: var(--text-muted);
    }
    .empty-icon {
      font-size: 3.5rem;
      margin-bottom: 1rem;
      opacity: 0.6;
    }

    /* 灯箱播放弹窗 */
    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.85);
      backdrop-filter: blur(10px);
      z-index: 100;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 1.5rem;
      animation: fadeIn 0.2s ease-out;
    }
    .modal-backdrop.active { display: flex; }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

    .modal-dialog {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 16px;
      width: 100%;
      max-width: 960px;
      max-height: 92vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.7);
    }

    .modal-header {
      padding: 1rem 1.35rem;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .modal-title {
      font-size: 1.1rem;
      font-weight: 700;
      color: var(--text);
    }
    .modal-close {
      background: none;
      border: none;
      color: var(--text-muted);
      font-size: 1.5rem;
      cursor: pointer;
      line-height: 1;
      padding: 0.2rem;
    }
    .modal-close:hover { color: #fff; }

    .modal-tabs {
      display: flex;
      border-bottom: 1px solid var(--border);
      background: var(--surface-subtle);
      padding: 0 1rem;
    }
    .tab-btn {
      background: none;
      border: none;
      color: var(--text-muted);
      padding: 0.75rem 1.25rem;
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
      border-bottom: 2px solid transparent;
      transition: all 0.2s ease;
    }
    .tab-btn.active {
      color: var(--primary-light);
      border-bottom-color: var(--primary-light);
    }

    .modal-content {
      padding: 1.25rem;
      overflow-y: auto;
      flex: 1;
    }

    /* 播放器容器 */
    .video-player-wrap {
      width: 100%;
      aspect-ratio: 16 / 9;
      background: #000;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    .video-player-wrap video {
      width: 100%;
      height: 100%;
      display: block;
    }

    .code-viewer {
      background: #0d1117;
      color: #e6edf3;
      padding: 1rem;
      border-radius: 10px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 0.82rem;
      line-height: 1.5;
      overflow-x: auto;
      max-height: 520px;
      white-space: pre-wrap;
      word-break: break-all;
    }

    .modal-footer {
      padding: 0.85rem 1.25rem;
      border-top: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.75rem;
      background: var(--surface);
    }

    /* Toast 提示浮窗 */
    .toast-box {
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 200;
      display: flex;
      flex-direction: column;
      gap: 10px;
      pointer-events: none;
    }
    .toast {
      background: #1e293b;
      border: 1px solid var(--primary-light);
      color: #fff;
      padding: 0.75rem 1.25rem;
      border-radius: 10px;
      font-size: 0.85rem;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
      animation: toastIn 0.25s ease-out;
    }
    @keyframes toastIn {
      from { transform: translateY(20px); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }
  </style>
</head>
<body>
  <!-- 顶部导航 -->
  <header>
    <a href="#" class="brand">
      <div class="brand-icon">🎬</div>
      <div>
        <div class="brand-title">Remotion Studio</div>
        <div class="brand-subtitle">视频资产在线管理中心</div>
      </div>
    </a>
    <div class="header-actions">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input type="text" id="searchInput" class="search-input" placeholder="搜索视频标题或 ID..." />
      </div>
      <button class="btn btn-secondary" onclick="loadFiles(true)">🔄 刷新</button>
      <button class="btn btn-secondary" id="authBtn" onclick="openAuthModal()">🔑 凭据验证</button>
    </div>
  </header>

  <!-- 统计指标栏 -->
  <div class="stat-bar">
    <div class="stat-pill">🎬 已生成视频：<span class="stat-val" id="statCount">0</span> 部</div>
    <div class="stat-pill">💾 占用磁盘：<span class="stat-val" id="statSize">0 MB</span></div>
    <div class="stat-pill">⚡ 渲染引擎：<span class="stat-val">Remotion 4.x + Chromium</span></div>
  </div>

  <!-- 批量操作栏 -->
  <div class="batch-bar" id="batchBar">
    <div style="display:flex; align-items:center; gap: 1rem;">
      <span style="font-weight: 700; color: #fff;">已选择 <span id="selectedCount" style="color:var(--primary-light)">0</span> 个视频</span>
      <button class="btn btn-secondary btn-sm" onclick="selectAll(false)">取消全选</button>
    </div>
    <div style="display:flex; gap: 0.75rem;">
      <button class="btn btn-danger btn-sm" onclick="batchDeleteSelected()">🗑️ 彻底批量删除</button>
    </div>
  </div>

  <!-- 主体卡片网格 -->
  <main>
    <div class="video-grid" id="videoGrid"></div>
    <div class="empty-state" id="emptyState" style="display:none;">
      <div class="empty-icon">🎬</div>
      <h3>暂无已渲染视频</h3>
      <p style="margin-top:0.5rem; font-size:0.85rem;">请通过 MCP 客户端（Cherry Studio / Claude）调用 <code>create_video_from_spec</code> 或 <code>create_video_from_code</code> 生成视频。</p>
    </div>
  </main>

  <!-- 视频详情与播放灯箱弹窗 -->
  <div class="modal-backdrop" id="playerModal">
    <div class="modal-dialog">
      <div class="modal-header">
        <div class="modal-title" id="modalTitle">视频详情</div>
        <button class="modal-close" onclick="closePlayerModal()">&times;</button>
      </div>
      <div class="modal-tabs">
        <button class="tab-btn active" id="tabVideoBtn" onclick="switchModalTab('video')">▶ 视频播放</button>
        <button class="tab-btn" id="tabCodeBtn" onclick="switchModalTab('code')">&lt;/&gt; 源码 / Spec</button>
        <button class="tab-btn" id="tabMetaBtn" onclick="switchModalTab('meta')">ℹ️ 元数据</button>
      </div>
      <div class="modal-content">
        <div id="tabVideoContent">
          <div class="video-player-wrap">
            <video id="mainVideoPlayer" controls preload="metadata" playsinline></video>
          </div>
        </div>
        <div id="tabCodeContent" style="display:none;">
          <pre class="code-viewer" id="codeViewerContent"></pre>
        </div>
        <div id="tabMetaContent" style="display:none; font-size:0.85rem; line-height: 1.8;">
          <div id="metaInfoContent"></div>
        </div>
      </div>
      <div class="modal-footer">
        <div style="display:flex; gap:0.5rem; flex-wrap:wrap;">
          <button class="btn btn-secondary btn-sm" onclick="copyCurrentVideoUrl()">🔗 复制视频链接</button>
          <button class="btn btn-secondary btn-sm" onclick="copyCurrentPosterUrl()">🖼️ 复制封面链接</button>
          <button class="btn btn-secondary btn-sm" onclick="copyCurrentMarkdown()">📝 复制 Markdown</button>
        </div>
        <div style="display:flex; gap:0.5rem;">
          <a class="btn btn-primary btn-sm" id="modalDownloadBtn" href="#" download>📥 下载 MP4</a>
          <button class="btn btn-danger btn-sm" onclick="deleteCurrentModalVideo()">🗑️ 删除</button>
        </div>
      </div>
    </div>
  </div>

  <!-- AUTH_KEY 输入弹窗 -->
  <div class="modal-backdrop" id="authModal">
    <div class="modal-dialog" style="max-width: 440px;">
      <div class="modal-header">
        <div class="modal-title">🔑 输入管理后台访问密钥</div>
        <button class="modal-close" onclick="closeAuthModal()">&times;</button>
      </div>
      <div class="modal-content" style="padding: 1.5rem;">
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem;">
          若服务端环境变量配置了 <code>AUTH_KEY</code>，请输入凭证解锁管理后台与接口权限：
        </p>
        <input type="password" id="authKeyInput" class="search-input" style="width:100%; font-size:0.95rem; padding:0.6rem 0.8rem;" placeholder="请输入 AUTH_KEY" />
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="closeAuthModal()">取消</button>
        <button class="btn btn-primary" onclick="saveAuthKey()">确认并保存</button>
      </div>
    </div>
  </div>

  <div class="toast-box" id="toastBox"></div>

  <script>
    let allFiles = [];
    let currentModalItem = null;
    let selectedIds = new Set();

    function getAuthKey() {
      return localStorage.getItem("REMOTION_AUTH_KEY") || "";
    }

    function setAuthKey(k) {
      if (k) localStorage.setItem("REMOTION_AUTH_KEY", k);
      else localStorage.removeItem("REMOTION_AUTH_KEY");
    }

    function showToast(msg) {
      const box = document.getElementById("toastBox");
      const el = document.createElement("div");
      el.className = "toast";
      el.innerText = msg;
      box.appendChild(el);
      setTimeout(() => { el.remove(); }, 3000);
    }

    async function loadFiles(isManual = false) {
      const key = getAuthKey();
      const headers = key ? { "Authorization": `Bearer ${key}` } : {};
      try {
        const res = await fetch("/api/admin/files", { headers });
        if (res.status === 401) {
          openAuthModal();
          return;
        }
        const data = await res.json();
        allFiles = data.files || [];
        document.getElementById("statCount").innerText = allFiles.length;
        document.getElementById("statSize").innerText = (data.total_disk_bytes / (1024 * 1024)).toFixed(1) + " MB";
        renderGrid(allFiles);
        if (isManual) showToast("已刷新列表");
      } catch (e) {
        console.error("加载文件列表失败", e);
      }
    }

    function escapeHtml(str) {
      if (!str) return "";
      return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
    }

    function handlePosterError(img) {
      img.onerror = null;
      img.src = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='320' height='180' viewBox='0 0 320 180'><rect width='320' height='180' fill='%23111827'/><text x='50%' y='50%' fill='%2394a3b8' font-size='16' text-anchor='middle' dominant-baseline='middle'>🎬 视频封面</text></svg>";
    }

    function renderGrid(files) {
      const grid = document.getElementById("videoGrid");
      const empty = document.getElementById("emptyState");
      grid.innerHTML = "";

      if (!files || files.length === 0) {
        empty.style.display = "block";
        return;
      }
      empty.style.display = "none";

      files.forEach(item => {
        const card = document.createElement("div");
        card.className = "video-card";

        const posterSrc = item.poster_url || "/api/poster/" + item.id + ".jpg";
        const videoSrc = item.video_url || "/api/video/" + item.id + ".mp4";
        const isChecked = selectedIds.has(item.id);
        const safeTitle = escapeHtml(item.title || item.id);
        const safeId = escapeHtml(item.id);

        card.innerHTML = `
          <div class="card-checkbox-wrap">
            <input type="checkbox" class="card-checkbox" ${isChecked ? 'checked' : ''} onchange="toggleSelect('${safeId}', this.checked)" />
          </div>
          <div class="card-preview" onclick="openPlayerModal('${safeId}')">
            <img class="card-img" src="${posterSrc}" alt="${safeTitle}" onerror="handlePosterError(this)"/>
            <div class="play-overlay">
              <div class="play-circle">▶</div>
            </div>
            <div class="card-badges">
              <span class="badge badge-mode">${item.mode === 'spec' ? 'Spec 模式' : 'React 源码'}</span>
              <span class="badge">${item.duration_seconds || 0}s</span>
              <span class="badge">${item.resolution || '1080p'}</span>
            </div>
          </div>
          <div class="card-body">
            <div>
              <div class="card-title" title="${safeTitle}">${safeTitle}</div>
              <div class="card-meta">
                <span>🕒 ${escapeHtml(item.created_at || '')}</span>
                <span>💾 ${item.size_mb || 0} MB</span>
              </div>
            </div>
            <div class="card-actions">
              <button class="btn btn-secondary btn-sm" onclick="openPlayerModal('${safeId}')">▶ 播放</button>
              <button class="btn btn-secondary btn-sm" onclick="copyLink('${videoSrc}')">🔗 链接</button>
              <a class="btn btn-primary btn-sm" href="/api/download/${safeId}.mp4" download>📥 下载</a>
              <button class="btn btn-danger btn-sm" style="flex:0.5;" onclick="deleteSingle('${safeId}')">🗑️</button>
            </div>
          </div>
        `;
        grid.appendChild(card);
      });
    }

    function toggleSelect(id, checked) {
      if (checked) selectedIds.add(id);
      else selectedIds.delete(id);
      updateBatchBar();
    }

    function selectAll(val) {
      if (val) {
        allFiles.forEach(f => selectedIds.add(f.id));
      } else {
        selectedIds.clear();
      }
      updateBatchBar();
      renderGrid(allFiles);
    }

    function updateBatchBar() {
      const bar = document.getElementById("batchBar");
      const countEl = document.getElementById("selectedCount");
      if (selectedIds.size > 0) {
        bar.classList.add("active");
        countEl.innerText = selectedIds.size;
      } else {
        bar.classList.remove("active");
      }
    }

    async function batchDeleteSelected() {
      if (selectedIds.size === 0) return;
      if (!confirm(`确定彻底删除选中的 ${selectedIds.size} 部视频及其关联文件吗？`)) return;

      const key = getAuthKey();
      const headers = { "Content-Type": "application/json" };
      if (key) headers["Authorization"] = `Bearer ${key}`;

      try {
        const res = await fetch("/api/admin/delete", {
          method: "POST",
          headers,
          body: JSON.stringify({ ids: Array.from(selectedIds) }),
        });
        const d = await res.json();
        showToast(`已成功删除 ${d.deleted_count || selectedIds.size} 个视频`);
        selectedIds.clear();
        updateBatchBar();
        loadFiles();
      } catch (e) {
        alert("删除失败: " + e.message);
      }
    }

    async function deleteSingle(id) {
      if (!confirm("确定删除此视频文件吗？")) return;
      selectedIds.add(id);
      await batchDeleteSelected();
    }

    function openPlayerModal(id) {
      const item = allFiles.find(f => f.id === id);
      if (!item) return;
      currentModalItem = item;

      document.getElementById("modalTitle").innerText = item.title || item.id;
      const player = document.getElementById("mainVideoPlayer");
      player.src = item.video_url || `/api/video/${item.id}.mp4`;
      player.play().catch(() => {});

      document.getElementById("modalDownloadBtn").href = `/api/download/${item.id}.mp4`;

      // Code view
      const codeViewer = document.getElementById("codeViewerContent");
      if (item.spec) {
        codeViewer.innerText = JSON.stringify(item.spec, null, 2);
      } else if (item.files) {
        codeViewer.innerText = Object.entries(item.files).map(([k, v]) => `// === ${k} ===\n${v}`).join(String.fromCharCode(10, 10));
      } else {
        codeViewer.innerText = "// 无源码或 Spec 记录";
      }

      // Meta view
      document.getElementById("metaInfoContent").innerHTML = `
        <p><strong>视频唯一 ID:</strong> <code>${item.id}</code></p>
        <p><strong>主标题:</strong> ${item.title}</p>
        <p><strong>生成模式:</strong> ${item.mode === 'spec' ? '声明式 Spec 模式' : '自由式 React 源码模式'}</p>
        <p><strong>时长:</strong> ${item.duration_seconds || 0} 秒 (${item.duration_frames || 0} 帧)</p>
        <p><strong>帧率:</strong> ${item.fps || 30} FPS</p>
        <p><strong>分辨率:</strong> ${item.resolution || '1920x1080'}</p>
        <p><strong>文件大小:</strong> ${item.size_mb || 0} MB</p>
        <p><strong>生成时间:</strong> ${item.created_at || ''}</p>
      `;

      switchModalTab("video");
      document.getElementById("playerModal").classList.add("active");
    }

    function closePlayerModal() {
      const player = document.getElementById("mainVideoPlayer");
      player.pause();
      player.src = "";
      document.getElementById("playerModal").classList.remove("active");
      currentModalItem = null;
    }

    function switchModalTab(tab) {
      document.getElementById("tabVideoBtn").classList.toggle("active", tab === "video");
      document.getElementById("tabCodeBtn").classList.toggle("active", tab === "code");
      document.getElementById("tabMetaBtn").classList.toggle("active", tab === "meta");

      document.getElementById("tabVideoContent").style.display = tab === "video" ? "block" : "none";
      document.getElementById("tabCodeContent").style.display = tab === "code" ? "block" : "none";
      document.getElementById("tabMetaContent").style.display = tab === "meta" ? "block" : "none";
    }

    function copyLink(url) {
      const full = window.location.origin + url;
      navigator.clipboard.writeText(full).then(() => showToast("已复制视频播放链接"));
    }

    function copyCurrentVideoUrl() {
      if (!currentModalItem) return;
      copyLink(currentModalItem.video_url || `/api/video/${currentModalItem.id}.mp4`);
    }

    function copyCurrentPosterUrl() {
      if (!currentModalItem) return;
      copyLink(currentModalItem.poster_url || `/api/poster/${currentModalItem.id}.jpg`);
    }

    function copyCurrentMarkdown() {
      if (!currentModalItem) return;
      const vUrl = window.location.origin + (currentModalItem.video_url || `/api/video/${currentModalItem.id}.mp4`);
      const pUrl = window.location.origin + (currentModalItem.poster_url || `/api/poster/${currentModalItem.id}.jpg`);
      const md = `[![${currentModalItem.title}](${pUrl})](${vUrl})\n\n[▶ 点击播放 ${currentModalItem.title}](${vUrl})`;
      navigator.clipboard.writeText(md).then(() => showToast("已复制 Markdown 语法"));
    }

    async function deleteCurrentModalVideo() {
      if (!currentModalItem) return;
      const id = currentModalItem.id;
      closePlayerModal();
      await deleteSingle(id);
    }

    function openAuthModal() {
      document.getElementById("authKeyInput").value = getAuthKey();
      document.getElementById("authModal").classList.add("active");
    }
    function closeAuthModal() {
      document.getElementById("authModal").classList.remove("active");
    }
    function saveAuthKey() {
      const val = document.getElementById("authKeyInput").value.trim();
      setAuthKey(val);
      closeAuthModal();
      showToast("已保存凭证，正在刷新...");
      loadFiles();
    }

    // 搜索过滤
    document.getElementById("searchInput").addEventListener("input", (e) => {
      const q = e.target.value.toLowerCase().trim();
      if (!q) {
        renderGrid(allFiles);
        return;
      }
      const filtered = allFiles.filter(it =>
        (it.title && it.title.toLowerCase().includes(q)) ||
        (it.id && it.id.toLowerCase().includes(q))
      );
      renderGrid(filtered);
    });

    // 快捷键 Esc 关闭弹窗
    window.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        closePlayerModal();
        closeAuthModal();
      }
    });

    // 初始化加载与前台 4 秒自动增量同步
    loadFiles();
    setInterval(() => {
      if (!document.hidden && !currentModalItem) {
        loadFiles();
      }
    }, 4000);
  </script>
</body>
</html>
"""
