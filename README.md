# Video Creation Workflows

视频创作两套完整工作流的 skill 集合，基于 opencode 技能框架构建。

## 目录结构

```
video-creation-workflows/
├── 01-制作管线/          逐字稿 → 分镜 → 拍摄 → 剪辑 → 动效 → 飞书同步
└── 02-内容校准/          写稿 → 打分 → 预测 → 拍摄 → 发布 → 复盘
```

---

## 01 - 制作管线

从视频逐字稿到成片的全流程生产管线。

```
逐字稿 ──→ manuscript-material-planner ──→ 分镜 + 素材清单 + 飞书JSON
                                           │
        ┌──────────────────────────────────┤
        ↓                                  ↓
  video-use                         media-asset-acquirer
  (拍摄/粗剪/调色/字幕)              (外部素材采购/许可证管理)
        │                                  │
        ↓                                  ↓
  huanyu-remotion-material ←── remotion-best-practices
  (Remotion 精确动效)            (Remotion 技术规范)
        │
        ↓
  n8n ──→ 飞书多维表格同步
```

### 各 skill 职责

| Skill | 职责 |
|---|---|
| **manuscript-material-planner** | 解析逐字稿，生成 `storyboard.json`（核心数据源）、`material_suggestion_doc.md`、`remotion_candidate_list.md`、`music_cue_sheet.json`、`asset_request_list.md`、`feishu_storyboard_records.json` |
| **video-use** | 视频转录、多 take 选择、粗剪、调色、字幕、Filmora 项目生成 |
| **huanyu-remotion-material** | 粗剪后按 `motion_request_list.md` 制作 Remotion 动效（流程图/架构图/数据可视化等） |
| **media-asset-acquirer** | 下载免版税音乐/SFX/Stock 视频，ffmpeg 标准化转码，记录许可证 |
| **remotion-best-practices** | Remotion 技术规范与最佳实践 |

### 数据流核心文件

- `storyboard.json` — 全局数据源，每个场景含分镜号、脚本、时长、拍摄形式、配乐情绪
- `feishu_storyboard_records.json` — n8n 消费，upsert 到飞书多维表格
- `motion_request_list.md` — 粗剪后的动效执行清单（非早期候选列表）
- `asset_request_list.md` — 外部素材采购清单

---

## 02 - 内容校准

基于 rubric 评分体系的内容预测闭环，将"感觉"变成可校准的预测。

```
写稿 ──→ 打分 ──→ 盲预测 ──→ 拍摄 ──→ 发布 ──→ T+3天复盘
  ↑                                              │
  └──────── rubric 进化 ←─────────────────────────┘
```

### 子 skill

| Skill | 命令 | 职责 |
|---|---|---|
| **cheat-init** | `/cheat-init` | 首次 onboarding，创建脚手架 |
| **cheat-seed** | `/cheat-seed` | 选题 brainstorm，提炼角度写初稿 |
| **cheat-score** | `/cheat-score <file>` | 打分（只读输出，不写文件） |
| **cheat-predict** | `/cheat-predict <file>` | 写 immutable 盲预测日志 |
| **cheat-shoot** | `/cheat-shoot <file>` | 登记已拍摄，创建视频工作目录 |
| **cheat-publish** | `/cheat-publish <url>` | 登记已发布，记录链接和时间 |
| **cheat-retro** | `/cheat-retro <path>` | T+N 天数据回收 + 复盘 |
| **cheat-bump** | `/cheat-bump` | 升级 rubric 公式或 bucket 边界 |
| **cheat-recommend** | `/cheat-recommend` | 按 rubric 排序推荐选题 |
| **cheat-trends** | `/cheat-trends` | 从热点源抓话题写入候选池 |
| **cheat-learn-from** | `/cheat-learn-from` | 导入对标账号，拆 pattern 派生 rubric 信号 |
| **cheat-status** | `/cheat-status` | 状态看板 |
| **cheat-migrate** | `/cheat-migrate` | `.cheat-state.json` schema 升级 |

### 辅助模块

- `adapters/` — 数据抓取适配器（B站/抖音/YouTube/Whisper）
- `templates/` — rubric 模板
- `starter-rubrics/` — 初始 rubric 参考
- `hooks/` — 预测文件 immutable 保护 hook

---

## 使用方式

这些 skill 设计用于 [opencode](https://opencode.ai) 框架。将对应 skill 目录配置到 opencode 的 skill 路径中即可调用。

## 项目路径约定

所有视频项目文件统一存放于：

```
D:\work\OPC\videos\{第X期：视频标题}\
├── Raw Footage\          原始拍摄素材（只读）
├── video scripts\        逐字稿 + 分镜规划文件
├── assets\               外部素材 + 许可证
├── edit\                 剪辑工作区
├── picture\              封面/截图
└── ProjectFolder\        Filmora 项目
```
