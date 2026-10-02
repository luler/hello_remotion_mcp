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
      justify-content: center;
      gap: 0.45rem;
      padding: 0.45rem 0.9rem;
      border-radius: var(--radius);
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
      border: 1px solid transparent;
      transition: all 0.2s ease;
      text-decoration: none;
      white-space: nowrap;
      word-break: keep-all;
      flex-shrink: 0;
      line-height: 1.2;
      user-select: none;
      -webkit-user-select: none;
    }
    .btn-sm {
      padding: 0.35rem 0.7rem;
      font-size: 0.8rem;
      border-radius: var(--radius-sm);
      gap: 0.35rem;
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
      background: rgba(239, 68, 68, 0.16);
      border-color: rgba(239, 68, 68, 0.45);
      color: #fca5a5;
    }
    .btn-danger:hover {
      background: var(--danger);
      color: #fff;
      box-shadow: 0 0 12px rgba(239, 68, 68, 0.4);
    }
    .btn-refresh .refresh-icon {
      display: inline-block;
      transition: transform 0.3s ease;
    }
    .btn-refresh.loading .refresh-icon {
      animation: spin 0.8s linear infinite;
    }
    @keyframes spin {
      100% { transform: rotate(360deg); }
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

    /* 顶部操作与批量管理工具栏 */
    .action-toolbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 0.85rem;
      padding: 0.85rem 1.75rem;
      background: #1e293b;
      border-bottom: 1px solid var(--border);
      position: sticky;
      top: 56px;
      z-index: 35;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }
    .toolbar-group {
      display: flex;
      align-items: center;
      gap: 0.65rem;
      flex-wrap: wrap;
    }
    .selection-badge {
      font-size: 0.8rem;
      color: var(--primary-light);
      background: rgba(56, 189, 248, 0.12);
      border: 1px solid rgba(56, 189, 248, 0.3);
      padding: 0.35rem 0.75rem;
      border-radius: 9999px;
      font-weight: 600;
      display: none;
      align-items: center;
      gap: 0.3rem;
      white-space: nowrap;
      word-break: keep-all;
      flex-shrink: 0;
      line-height: 1.2;
    }
    .page-size-selector {
      display: flex;
      align-items: center;
      gap: 0.4rem;
      font-size: 0.82rem;
      color: var(--text-muted);
    }
    .page-size-select {
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 0.3rem 0.6rem;
      border-radius: var(--radius-sm);
      font-size: 0.82rem;
      outline: none;
      cursor: pointer;
    }
    .page-size-select:focus {
      border-color: var(--border-focus);
    }

    /* 分页导航控制条 */
    .pagination-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 1rem;
      margin-top: 2rem;
      padding: 1.25rem 0;
      border-top: 1px solid var(--border);
    }
    .pagination-info {
      font-size: 0.85rem;
      color: var(--text-muted);
    }
    .pagination-info strong {
      color: var(--text);
    }
    .pagination-nav {
      display: flex;
      align-items: center;
      gap: 0.35rem;
    }
    .page-btn {
      min-width: 34px;
      height: 34px;
      padding: 0 0.55rem;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border);
      background: var(--surface);
      color: var(--text);
      font-size: 0.82rem;
      font-weight: 500;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.2s;
    }
    .page-btn:hover:not(:disabled) {
      border-color: var(--primary-light);
      color: var(--primary-light);
      background: var(--surface-hover);
    }
    .page-btn.active {
      background: var(--primary);
      border-color: var(--primary-light);
      color: #fff;
      font-weight: 700;
      box-shadow: 0 0 10px rgba(56, 189, 248, 0.35);
    }
    .page-btn:disabled {
      opacity: 0.35;
      cursor: not-allowed;
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
    .video-card.selected {
      border-color: var(--primary-light);
      background: rgba(56, 189, 248, 0.05);
      box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.4), 0 12px 30px rgba(0, 0, 0, 0.5);
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

    /* =========================================================================
       移动端自适应响应式优化 (Mobile & Tablet Responsiveness)
       ========================================================================= */
    @media (max-width: 768px) {
      header {
        padding: 0.75rem 1rem;
        flex-direction: column;
        align-items: stretch;
        gap: 0.75rem;
      }
      .brand-title {
        font-size: 1.05rem;
      }
      .brand-subtitle {
        font-size: 0.7rem;
      }
      .header-actions {
        width: 100%;
        display: flex;
        align-items: center;
        gap: 0.5rem;
      }
      .search-box {
        flex: 1;
        min-width: 0;
      }
      .search-input {
        width: 100%;
        padding: 0.45rem 0.75rem 0.45rem 2rem;
        font-size: 0.8rem;
      }

      .stat-bar {
        padding: 0.5rem 1rem;
        gap: 0.85rem;
        overflow-x: auto;
        white-space: nowrap;
        font-size: 0.76rem;
        -webkit-overflow-scrolling: touch;
      }
      .stat-pill {
        flex-shrink: 0;
      }

      .action-toolbar {
        padding: 0.65rem 1rem;
        position: static;
        gap: 0.65rem;
        flex-direction: column;
        align-items: stretch;
      }
      .action-toolbar .toolbar-group {
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: flex-start;
        flex-wrap: wrap;
        gap: 0.5rem;
      }

      main {
        padding: 1rem 0.85rem;
      }
      .video-grid {
        grid-template-columns: 1fr;
        gap: 1rem;
      }

      .pagination-bar {
        flex-direction: column;
        align-items: center;
        gap: 0.75rem;
        margin-top: 1.5rem;
        padding: 1rem 0;
      }
      .pagination-nav {
        flex-wrap: wrap;
        justify-content: center;
        gap: 0.25rem;
      }
      .page-btn {
        min-width: 32px;
        height: 32px;
        font-size: 0.78rem;
        padding: 0 0.45rem;
      }

      .modal-backdrop {
        padding: 0.5rem;
      }
      .modal-dialog {
        width: 100%;
        max-height: 96vh;
        border-radius: 12px;
      }
      .modal-header {
        padding: 0.75rem 1rem;
      }
      .modal-title {
        font-size: 0.95rem;
      }
      .modal-content {
        padding: 0.85rem;
      }
      .modal-footer {
        flex-direction: column;
        align-items: stretch;
        gap: 0.6rem;
        padding: 0.75rem 1rem;
      }
      .modal-footer > div {
        width: 100%;
        display: flex;
        justify-content: space-between;
      }
      .modal-footer .btn {
        flex: 1;
        text-align: center;
      }
      .card-actions {
        flex-wrap: wrap;
      }
      .toast-box {
        bottom: 12px;
        right: 12px;
        left: 12px;
      }
      .toast {
        text-align: center;
        font-size: 0.8rem;
        padding: 0.6rem 1rem;
      }
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
      <button class="btn btn-secondary btn-refresh" id="refreshBtn" onclick="handleManualRefresh()" title="手动刷新视频列表">
        <span class="refresh-icon">🔄</span> 刷新列表
      </button>
      <button class="btn btn-secondary" id="authBtn" onclick="openAuthModal()">🔑 凭据验证</button>
    </div>
  </header>

  <!-- 统计指标栏 -->
  <div class="stat-bar">
    <div class="stat-pill">🎬 已生成视频：<span class="stat-val" id="statCount">0</span> 部</div>
    <div class="stat-pill">💾 占用磁盘：<span class="stat-val" id="statSize">0 MB</span></div>
    <div class="stat-pill">⚡ 渲染引擎：<span class="stat-val">Remotion 4.x + Chromium</span></div>
  </div>

  <!-- 操作与批量控制工具栏 -->
  <div class="action-toolbar" id="actionToolbar">
    <div class="toolbar-group">
      <button class="btn btn-secondary btn-sm" onclick="selectAll()" title="勾选所有视频">
        ☑️ 全选
      </button>
      <button class="btn btn-secondary btn-sm" onclick="deselectAll()" title="取消已勾选的所有视频">
        ⬜ 取消全选
      </button>
      <button class="btn btn-danger btn-sm" id="batchDeleteBtn" style="display:none;" onclick="batchDeleteSelected()">
        🗑️ 批量删除 (<span id="batchDeleteCount">0</span>)
      </button>
    </div>
    <div class="toolbar-group">
      <div class="page-size-selector">
        <span>每页显示:</span>
        <select class="page-size-select" id="pageSizeSelect" onchange="changePageSize(Number(this.value))">
          <option value="12" selected>12 部</option>
          <option value="24">24 部</option>
          <option value="48">48 部</option>
          <option value="0">全部</option>
        </select>
      </div>
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

    <!-- 分页导航控制条 -->
    <div class="pagination-bar" id="paginationBar" style="display:none;">
      <div class="pagination-info" id="paginationInfo">
        共 <strong id="pgTotal">0</strong> 部视频 · 第 <strong id="pgCurrent">1</strong> / <strong id="pgTotalPages">1</strong> 页
      </div>
      <div class="pagination-nav">
        <button class="page-btn" id="btnFirst" onclick="goToPage(1)" title="第一页">⏮</button>
        <button class="page-btn" id="btnPrev" onclick="goToPage(currentPage - 1)" title="上一页">◀</button>
        <div id="pageNumberButtons" style="display:flex; gap:0.35rem;"></div>
        <button class="page-btn" id="btnNext" onclick="goToPage(currentPage + 1)" title="下一页">▶</button>
        <button class="page-btn" id="btnLast" onclick="goToPage(totalPages)" title="最后一页">⏭</button>
      </div>
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
    let currentFiles = [];
    let currentPage = 1;
    let pageSize = 12;
    let totalPages = 1;
    let totalItems = 0;
    let searchQuery = "";
    let searchTimer = null;
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
        const q = encodeURIComponent(searchQuery);
        const url = `/api/admin/files?page=${currentPage}&page_size=${pageSize}&search=${q}`;
        const res = await fetch(url, { headers });
        if (res.status === 401) {
          openAuthModal();
          return;
        }
        const data = await res.json();
        currentFiles = data.files || [];
        totalItems = data.total || 0;
        totalPages = data.total_pages || 1;

        if (currentPage > totalPages && totalPages >= 1) {
          currentPage = totalPages;
          return loadFiles(isManual);
        }

        document.getElementById("statCount").innerText = totalItems;
        document.getElementById("statSize").innerText = (data.total_disk_bytes / (1024 * 1024)).toFixed(1) + " MB";

        renderGrid(currentFiles);
        renderPagination();
        updateSelectionUI();

        if (isManual) showToast("已刷新视频列表");
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
        const safeId = escapeHtml(item.id);
        const safeTitle = escapeHtml(item.title || item.id);
        const isChecked = selectedIds.has(item.id);

        card.className = "video-card" + (isChecked ? " selected" : "");
        card.id = "card-" + safeId;

        const posterSrc = item.poster_url || "/api/poster/" + item.id + ".jpg";
        const videoSrc = item.video_url || "/api/video/" + item.id + ".mp4";

        card.innerHTML = `
          <div class="card-checkbox-wrap" onclick="event.stopPropagation()">
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
              ${item.render_time_seconds ? `<span class="badge" title="渲染总耗时">⏳ ${item.render_time_seconds}s</span>` : ''}
            </div>
          </div>
          <div class="card-body">
            <div>
              <div class="card-title" title="${safeTitle}">${safeTitle}</div>
              <div class="card-meta">
                <span>🕒 ${escapeHtml(item.created_at || '')}</span>
                <span>💾 ${item.size_mb || 0} MB</span>
                ${item.render_time_seconds ? `<span>⏳ 耗时 ${item.render_time_seconds}s</span>` : ''}
              </div>
            </div>
            <div class="card-actions">
              <button class="btn btn-secondary btn-sm" onclick="openPlayerModal('${safeId}')">▶ 播放</button>
              <button class="btn btn-secondary btn-sm" onclick="copyLink('${videoSrc}')">🔗 链接</button>
              <a class="btn btn-primary btn-sm" href="/api/download/${safeId}.mp4" download>📥 下载</a>
              <button class="btn btn-danger btn-sm" style="flex:0.5;" onclick="deleteSingle('${safeId}')" title="彻底删除此视频">🗑️</button>
            </div>
          </div>
        `;
        grid.appendChild(card);
      });
    }

    function toggleSelect(id, checked) {
      if (checked) selectedIds.add(id);
      else selectedIds.delete(id);
      updateSelectionUI();
      const card = document.getElementById("card-" + id);
      if (card) card.classList.toggle("selected", checked);
    }

    function selectAll() {
      if (!currentFiles || currentFiles.length === 0) return;
      currentFiles.forEach(f => selectedIds.add(f.id));
      updateSelectionUI();
      renderGrid(currentFiles);
      showToast(`已全选 ${currentFiles.length} 部视频`);
    }

    function deselectAll() {
      selectedIds.clear();
      updateSelectionUI();
      renderGrid(currentFiles);
      showToast("已取消全选");
    }

    function updateSelectionUI() {
      const count = selectedIds.size;
      const delBtn = document.getElementById("batchDeleteBtn");
      const delCount = document.getElementById("batchDeleteCount");

      if (delCount) delCount.innerText = count;

      if (count > 0) {
        if (delBtn) delBtn.style.display = "inline-flex";
      } else {
        if (delBtn) delBtn.style.display = "none";
      }
    }

    async function batchDeleteSelected() {
      if (selectedIds.size === 0) return;
      const count = selectedIds.size;
      if (!confirm(`确定彻底删除选中的 ${count} 部视频及其关联文件吗？此操作无法撤销！`)) return;

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
        showToast(`已成功删除 ${d.deleted_count || count} 部视频`);
        selectedIds.clear();
        await loadFiles();
      } catch (e) {
        alert("批量删除失败: " + e.message);
      }
    }

    async function deleteSingle(id) {
      if (!confirm("确定彻底删除此视频及其关联文件吗？")) return;
      const key = getAuthKey();
      const headers = { "Content-Type": "application/json" };
      if (key) headers["Authorization"] = `Bearer ${key}`;

      try {
        const res = await fetch("/api/admin/delete", {
          method: "POST",
          headers,
          body: JSON.stringify({ ids: [id] }),
        });
        const d = await res.json();
        showToast("已成功删除该视频");
        selectedIds.delete(id);
        await loadFiles();
      } catch (e) {
        alert("删除失败: " + e.message);
      }
    }

    function renderPagination() {
      const bar = document.getElementById("paginationBar");
      if (totalItems === 0 || pageSize === 0) {
        bar.style.display = "none";
        return;
      }
      bar.style.display = "flex";

      document.getElementById("pgTotal").innerText = totalItems;
      document.getElementById("pgCurrent").innerText = currentPage;
      document.getElementById("pgTotalPages").innerText = totalPages;

      document.getElementById("btnFirst").disabled = currentPage <= 1;
      document.getElementById("btnPrev").disabled = currentPage <= 1;
      document.getElementById("btnNext").disabled = currentPage >= totalPages;
      document.getElementById("btnLast").disabled = currentPage >= totalPages;

      const container = document.getElementById("pageNumberButtons");
      container.innerHTML = "";

      let startPage = Math.max(1, currentPage - 2);
      let endPage = Math.min(totalPages, currentPage + 2);
      if (currentPage <= 3) endPage = Math.min(totalPages, 5);
      if (currentPage >= totalPages - 2) startPage = Math.max(1, totalPages - 4);

      for (let i = startPage; i <= endPage; i++) {
        const btn = document.createElement("button");
        btn.className = "page-btn" + (i === currentPage ? " active" : "");
        btn.innerText = i;
        btn.onclick = () => goToPage(i);
        container.appendChild(btn);
      }
    }

    function goToPage(p) {
      p = Math.max(1, Math.min(p, totalPages));
      if (p === currentPage) return;
      currentPage = p;
      window.scrollTo({ top: 0, behavior: 'smooth' });
      loadFiles();
    }

    function changePageSize(newSize) {
      pageSize = newSize;
      currentPage = 1;
      loadFiles();
    }

    function openPlayerModal(id) {
      const item = currentFiles.find(f => f.id === id);
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
        <p><strong>渲染总耗时:</strong> ${item.render_time_seconds ? item.render_time_seconds + ' 秒' : '未知'}</p>
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

    // 搜索过滤（防抖 300ms，重置到第一页请求后端过滤）
    document.getElementById("searchInput").addEventListener("input", (e) => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        searchQuery = e.target.value.trim();
        currentPage = 1;
        loadFiles();
      }, 300);
    });

    // 手动刷新处理
    async function handleManualRefresh() {
      const btn = document.getElementById("refreshBtn");
      if (btn) btn.classList.add("loading");
      await loadFiles(true);
      setTimeout(() => {
        if (btn) btn.classList.remove("loading");
      }, 400);
    }

    // 快捷键 Esc 关闭弹窗
    window.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        closePlayerModal();
        closeAuthModal();
      }
    });

    // 仅在初次进入页面时加载一次列表，不进行任何后台定时轮询刷新
    loadFiles();
  </script>
</body>
</html>
"""
