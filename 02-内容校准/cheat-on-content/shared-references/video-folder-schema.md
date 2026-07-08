# Video Folder Schema（视频目录标准结构）

> **被 cheat-seed Phase 3 引用**。cheat-seed 输出 draft 前必须按此 schema 初始化视频目录，避免后续产物散落到错误位置。
>
> **强制约束**：每期视频的所有产物（draft / prediction / brief / cover prompt / 发布文案 / 封面图 / 字幕 / 成片等）必须落到对应子目录，禁止散落到工作目录根。

---

## 路径约定

```
videos/<视频标题>/          # 文件夹名用工作标题，最终发布后可改名
├── scripts/               # 视频脚本（cheat-seed Phase 4 输出）
├── predictions/           # 盲预测文件（cheat-predict 输出）
├── audience-brief.md      # 受众档案（cheat-who-for 输出）
├── prompt/                # 统一 prompt 管理（cheat-cover / 其他生成工具的 prompt）
│   ├── cover/             # 三平台封面 prompt（cheat-cover 输出）
│   │   ├── prompt-bilibili.md
│   │   ├── prompt-xhs.md
│   │   └── prompt-douyin.md
│   ├── video/             # AI 视频片段 prompt（Kling/Vidu/Veo 等）
│   ├── audio/             # 配音/音效/音乐 prompt（ElevenLabs/Suno/Udio）
│   ├── animation/         # Remotion / HyperFrames 等动画 prompt
│   └── _README.md         # prompt 管理规范
├── Raw/                   # 原始素材（实拍录屏/OBS 录像/外部素材）
├── Rough/                 # 粗剪第一版
├── Polished/              # 精剪调色音后
├── Jianying-draft/        # 剪映工程文件
├── Final/                 # 最终导出视频（mp4 等）
├── assets/                # 第三方资源（音乐/音效/视频片段），登记许可证
├── Sub/                   # 字幕文件
├── Thumb/                 # 三平台封面图（生成后从 prompt/cover 出图存这）
├── video scripts/         # 实拍相关脚本（与 scripts/ 区分：scripts 是口播脚本，video scripts 是分镜/拍摄指引）
└── ProjectFolder/         # 项目综合文件夹（按需使用）
```

## 命名约定

### 文件夹名（视频标题）
- 用**工作标题**（cheat-seed 讨论确定的角度），不要等最终标题再命名
- 最终发布后允许改文件夹名追溯发布版标题
- 例：`EP004_古人培养人才我给AI大臣培养才能/` 或 `EP004_女娲蒸馏实操/`（工作版）→ `古人培养人才，我给AI大臣培养才能/`（发布版）

### 文件名
- `<YYYY-MM-DD>_<id>_<short-title>.md` —— scripts/ 和 predictions/ 一致
- `prompt-<平台>.md` —— prompt/cover/ 等子目录
- `preview-<平台>.jpg` —— Thumb/ 下的封面预览图

### ID 稳定性
- 视频文件夹 ID 用 candidate id（12 位 hash），与 script/prediction 文件名一致
- 重命名文件夹不影响追溯（git history + 内部文件 ID 关联）

## 与 cheat-on-content 各阶段产物的对应

| 阶段产物 | 输出路径 |
|---|---|
| 脚本 draft | `scripts/<id>.md` |
| 改稿 v2 | `scripts/<id>_who-for-v2.md`（或 `_open-source-v2.md`）|
| 受众档案 | `audience-brief.md`（video folder 根） |
| 预测 v1 | `predictions/<id>.md` |
| 预测 v2 | `predictions/<id>.md`（append ## 预测 v2 段）|
| 封面 prompt | `prompt/cover/prompt-<平台>.md` |
| 视频片段 prompt | `prompt/video/prompt-<tool>.md` |
| 字幕文件 | `Sub/<id>.<format>` |
| 封面图 | `Thumb/<id>-<platform>.<ext>` |
| 最终视频 | `Final/<id>-<platform>.<ext>` |
| 草稿视频 | `Rough/<id>-rough.<ext>` |
| 精剪视频 | `Polished/<id>-polished.<ext>` |
| 原始素材 | `Raw/<id>-<scene>.<ext>` |
| 第三方资源 | `assets/<category>/<name>.<ext>` + 许可证登记 |

## Jianying-draft/ 的 symlink 机制（剪映草稿根映射）

**问题**：剪映专业版只识别"草稿根目录"下的文件夹。草稿直接放项目目录的 `Jianying-draft/`，剪映 GUI 看不到。

**方案**：用 symlink（符号链接）在剪映草稿根下建一个"假入口"指向项目的 `Jianying-draft/`。剪映通过 symlink 识别草稿，文件实际存在项目目录。

```
剪映草稿根\                          ← 剪映设置里的"草稿位置"
└── EP004_女娲蒸馏实操\              ← symlink（假入口，剪映以为在自己地盘）
    └── draft_content.json           ← 实际内容 ↓ 指向
        D:\work\OPC\videos\EP004_女娲蒸馏实操\Jianying-draft\
        ├── draft_content.json       ← 真实文件
        ├── assets\
        └── ...
```

**效果**：
- 剪映正常识别、编辑、保存（透明，剪映不知道这是 symlink）
- 文件实际在项目目录（便于版本管理、git 追踪、跨期归档）
- 双向同步：剪映改 = 项目目录改；直接改项目目录 = 剪映看到也变了

**前提**：Windows 开发者模式已开启（不用管理员权限建 symlink）。检查：`Get-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock -Name AllowDevelopmentWithoutDevLicense`（值为 1 = 已开）

**建 symlink 命令**（cheat-seed Phase 3 执行）：

```powershell
$jianYingRoot = "<剪映草稿根路径>"  # 从剪映设置读取，或默认 C:\Users\<user>\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft
$videoFolder = "videos/<视频标题>"
New-Item -ItemType SymbolicLink `
  -Path "$jianYingRoot\<视频标题或EP编号>" `
  -Target "$videoFolder\Jianying-draft" `
  -Force
```

**jianying-toolkit 配合**：执行 `save_draft` 时：

```bash
# ⚠️ --output 必须用剪映 GUI 设置里的实际草稿根路径（不是默认 Windows 路径）
# 本 skill 维护者的剪映草稿根是 D 盘：
python scripts/jianying.py save_draft \
  --draft-id <id> \
  --cache-dir "<video_project>/Rough/.jianying_cache" \
  --output "D:\剪映\draft\JianyingPro Drafts" \
  --name "EP00X_<视频标题>"  # 跟 symlink 名字一致
```

草稿通过 symlink 直接写入项目目录的 `Jianying-draft/`，剪映正常识别+编辑。

**执行前必查**：剪映专业版 → 全局设置 → 草稿 → "草稿位置"字段——如果跟你的脚本不一致，jianying-toolkit 会写到错误路径，剪映看不到且占用错位置磁盘空间。

**多版本草稿**：如需保留粗剪+精剪多版本，用 `Jianying-draft-v1/`、`Jianying-draft-v2/` 平级目录，每个对应一个 symlink。

---

## 与 cheat-on-content 全局文件的关系

部分全局文件**不放在 video folder**，而是放在项目根的 cheat-init 时指定位置：

| 全局文件 | 位置 |
|---|---|
| `.cheat-state.json` | 项目根（cheat-init 时建） |
| `rubric_notes.md` | 项目根（cheat-init 时建） |
| `script_patterns.md` | 项目根（cheat-init 时建） |
| `candidates.md` | 项目根（cheat-trends/cheat-seed 累积） |

这些是跨期的元数据，每期视频共享。**video folder 只放本期视频的产物**。

## cheat-seed Phase 3 执行步骤

cheat-seed 在 Phase 3 落候选池后，**立即**初始化视频目录：

```powershell
# 工作标题作为文件夹名（用户确认后）
$title = "EP004_工作标题"
$base = "videos/$title"

# 标准子目录（一次性全建）
$dirs = @(
    "$base/scripts",
    "$base/predictions",
    "$base/prompt/cover",
    "$base/Raw",
    "$base/Rough",
    "$base/Polished",
    "$base/Jianying-draft",
    "$base/Final",
    "$base/assets",
    "$base/Sub",
    "$base/Thumb",
    "$base/video scripts",
    "$base/ProjectFolder"
)

foreach ($d in $dirs) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
```

后续所有产物按本 schema 落到对应子目录。

## 演进原则

- 本 schema 是**当前约定**，不是绝对真理
- 新增工具/新阶段产物时，扩展 `prompt/` 或新增顶层子目录
- 旧期视频目录结构差异**不改**（retro 时如发现某期漏建目录，单独补即可）
- schema 修订走 git commit + 在 changelog 段记录

## Changelog

- 2026-07-06：初版。基于 EP001-03 实操经验 + EP004 完整初始化流程沉淀。