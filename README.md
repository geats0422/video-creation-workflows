# Video Creation Workflows

视频创作两套完整工作流的 skill 集合，基于 [opencode](https://opencode.ai) 技能框架构建。

> **关于本项目**：这不是一个从零原创的项目。作者参考并整合了多个优秀开源项目的实现思路与能力，按自己的视频创作流程把它们拼接成一套连贯的工作流。各 skill 的原始来源见文末[致谢](#致谢)。

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
                 ┌─────────────────────────┤
                 ↓                           ↓
          ai-jian-koubo                media-asset-acquirer
       (口播转录/口误识别)            (外部素材采购/许可证)
                 │                           │
                 ↓                           │
            video-use                        │
       (粗剪/调色/字幕)                       │
                 │                           │
                 ↓                           │
   huanyu-remotion-material ← remotion-best-practices
   (Remotion 精确动效)        (Remotion 技术规范)
                 │
                 ↓
   jianying-toolkit / Filmora ──→ 成片
                 │
                 ↓
          n8n ──→ 飞书多维表格同步
```

### 各 skill 职责

| Skill | 职责 |
|---|---|
| **manuscript-material-planner** | 解析逐字稿，生成 `storyboard.json`（核心数据源）、`material_suggestion_doc.md`、`remotion_candidate_list.md`、`music_cue_sheet.json`、`asset_request_list.md`、`feishu_storyboard_records.json` |
| **ai-jian-koubo** | 口播视频转录（火山引擎）+ AI 口误/口癖识别 + 本地网页审核，导出 FCPXML 给剪辑软件完成最后一刀 |
| **video-use** | 视频转录、多 take 选择、粗剪、调色、字幕、Filmora 项目生成 |
| **huanyu-remotion-material** | 粗剪后按 `motion_request_list.md` 制作 Remotion 动效（流程图/架构图/数据可视化等） |
| **remotion-best-practices** | Remotion 技术规范与最佳实践 |
| **media-asset-acquirer** | 下载免版税音乐/SFX/Stock 视频，ffmpeg 标准化转码，记录许可证 |
| **jianying-toolkit** | 通过 CLI 直接生成剪映（JianYing/CapCut）原生 draft：`/create_draft`、`/add_video`、`/add_subtitle`、`/add_audio`、`/add_effect`、`/save_draft` |

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

这些 skill 的本质是「带 `SKILL.md` 的目录」——任何支持读取 skill 目录、能跑 shell 的 coding agent 都能用，**不绑定特定框架**。

### 支持的 Agent

| Agent | Skill 目录 | 说明 |
|---|---|---|
| **opencode** | `.opencode/skill/`（项目级）或 `~/.config/opencode/skills/`（用户级） | 作者本人主力环境 |
| **Claude Code** | `.claude/skills/` 或 `~/.claude/skills/` | |
| **Codex** | `~/.codex/skills/` | |
| **Cursor / VS Code** | 项目根 `skills/`（加入 include 列表） | |
| **Trae** | `.trae/skills/` | |
| **Antigravity / Gemini** | `.agent/skills/` | |

把对应 skill 目录（如 `01-制作管线/video-use/`）复制或软链到你所用 agent 的 skill 路径下即可调用；各 agent 的具体注册方式略有差异，参考其官方文档。

> 注：本仓库的项目路径约定（`D:\work\OPC\videos\...`）是作者在 opencode 下的实际配置，迁移到其他 agent 时按需调整 `videos_dir`。

## 项目路径约定

所有视频项目文件统一存放于：

```
D:\work\OPC\videos\{第X期：视频标题}\
├── Raw\                原始拍摄素材（只读，禁止改名/覆盖）
├── Rough\              粗剪工作区（转录缓存、EDL、调色片段、preview.mp4…）
├── Polished\           精剪（含 Remotion 动效素材）
├── Final\              成片（确认发布的最终渲染 video_final.mp4）
├── Sub\                字幕（master.srt）
├── Thumb\              封面/截图
├── Backup\             归档备份
├── video scripts\      逐字稿 + 分镜规划文件
├── assets\             外部素材 + 许可证
└── ProjectFolder\      Filmora / 剪映 项目文件
```

---

## 致谢

本项目站在以下项目的肩膀上。每个 skill 的核心能力都可追溯到它们的原始实现：

| 对应本项目 | 致敬项目 | 贡献 |
|---|---|---|
| **video-use** | [browser-use/video-use](https://github.com/browser-use/video-use) | 「转录 → 粗剪 → 调色 → 烧字幕 → 自评」整个范式的来源 |
| **video-use**（粗剪思路） | [DayadaUP/claude-code-auto-video-edit](https://github.com/DayadaUP/claude-code-auto-video-edit) | Whisper 转写 + 口头标记识别好坏 take + 字幕对齐时间线 |
| **ai-jian-koubo** | [lcbuaaliu/ai-jian-koubo](https://github.com/lcbuaaliu/ai-jian-koubo) | 火山引擎转录 + AI 口误识别 + 网页审核 + FCPXML 导出 |
| **jianying-toolkit** | [luoluoluo22/jianying-editor-skill](https://github.com/luoluoluo22/jianying-editor-skill) | 剪映草稿自动化的整体范式 |
| **jianying-toolkit**（API 设计） | [fancyboi999/capcut-mcp](https://github.com/fancyboi999/capcut-mcp) | `add_video / add_audio / add_subtitle / add_effect / save_draft` 等命令设计 |
| **02-内容校准/cheat-on-content** | [XBuilderLAB/cheat-on-content](https://github.com/XBuilderLAB/cheat-on-content) | 评分 → 盲预测 → 复盘 → rubric 进化的整个内容校准闭环 |

感谢以下项目的开发者：

- **luoluoluo22**（B站：我老罗卜）— https://github.com/luoluoluo22/jianying-editor-skill
- **fancyboi999** — https://github.com/fancyboi999/capcut-mcp
- **lcbuaaliu**（B站：栗氪聊AI）— https://github.com/lcbuaaliu/ai-jian-koubo
- **browser-use** — https://github.com/browser-use/video-use
- **DayadaUP**（抖音：大牙大）— https://github.com/DayadaUP/claude-code-auto-video-edit
- **XBuilderLAB**（抖音：他们都叫我蜗牛学长）— https://github.com/XBuilderLAB/cheat-on-content

---

## License

[MIT](./LICENSE) — 随便用、改、分发。所有致敬项目同样采用 MIT 许可证。
