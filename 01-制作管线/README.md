# 01-制作管线

> 从终稿到成片的全流程：规划分镜 → 获取素材 → 拍摄 → 粗剪 → 动效 → 精剪 → 成片。
> 上游衔接内容管线（cheat-on-content），下游产出可发布的成片。
> 本文件是制作管线的**总入口 + 路由表**。各工具的内部细节见各自的 SKILL.md。

---

## 端到端完整流程（内容管线 + 制作管线）

```
【内容管线 cheat-on-content】 拍前内容准备
  1. cheat-seed（选题写稿）
  2. who-for / open-source（诊断 + Phase 5 改稿）
  3. predict v1（初稿）
  4. title → title-pick → description → cover（发布物料）
  5. 补 TODO + 打磨 → 终稿
  6. predict v2（终稿锁定）
  ═══════════ ═══════════ ═══════════
  衔接点①：终稿交接 → 终稿落到 video scripts\ 目录
  ═══════════ ═══════════ ═══════════
【制作管线 01-制作管线】 本目录管的内容
  Phase 1：拍摄前规划    manuscript-material-planner（第1次）
  Phase 2：素材获取      media-asset-acquirer
  Phase 3：拍摄          用户按 storyboard 拍 → Raw\
  ═══════════ ═══════════ ═══════════
  衔接点②：拍摄交汇 → cheat-shoot 登记拍摄（内容管线侧，buffer+1）
  ═══════════ ═══════════ ═══════════
  Phase 4：粗剪          video-use（转录 + 粗剪 + 字幕）
  Phase 5：动效规划      manuscript-material-planner（第2次，基于粗剪时间码）
  Phase 6：动效生成      huanyu-remotion-material
  Phase 7：精剪成片      合成动效 + 粗剪 → Final\video_final.mp4
  ═══════════ ═══════════ ═══════════
  衔接点③：成片交接 → 成片 + 物料（标题/简介/封面）齐了
  ═══════════ ═══════════ ═══════════
【内容管线 cheat-on-content】 发布 + 复盘
  9. cheat-publish（登记发布 URL，buffer-1）
  10. cheat-retro（T+3d/T+30d 复盘，含双角度验证）
  11. 攒够盲区 → cheat-bump（rubric 升级）
```

---

## 制作管线 7 个 Phase 详解

### Phase 1：拍摄前规划

| 项 | 内容 |
|---|---|
| 做什么 | 读终稿，产出分镜 + 物料清单 + 音乐表 + 飞书记录，指导后续拍摄和素材获取 |
| 工具 | `manuscript-material-planner`（第 1 次执行，Default Manuscript Workflow） |
| 输入 | 终稿文稿（video scripts\ 下的 .md） |
| 产出 | `video scripts\storyboard.json`（分镜，source of truth）<br>`video scripts\material_suggestion_doc.md`（物料建议）<br>`video scripts\remotion_candidate_list.md`（候选动效，待粗剪后定稿）<br>`video scripts\music_cue_sheet.json`（音乐情绪表）<br>`assets\requests\asset_request_list.md`（外部素材请求）<br>`video scripts\feishu_storyboard_records.json`（n8n 同步飞书用） |
| 注意 | `//` 是停顿标记不是分镜边界；`【画面建议】`是用户意图不是执行令；按语义场景切分，不要过碎 |

### Phase 2：素材获取

| 项 | 内容 |
|---|---|
| 做什么 | 按 asset_request_list 下载、转码、整理带许可的外部素材（音乐/音效/stock 视频/图片） |
| 工具 | `media-asset-acquirer` |
| 输入 | `assets\requests\asset_request_list.md`（优先）+ music_cue_sheet + material_suggestion_doc |
| 产出 | `assets\` 下的素材文件 + 许可文档（license provenance） |
| 注意 | 只下载带许可的；不明许可不用；Raw\ 是只读用户原片，不在里面写文件 |

### Phase 3：拍摄

| 项 | 内容 |
|---|---|
| 做什么 | 用户按 storyboard 拍摄，素材进 Raw\ |
| 工具 | 用户手动（手机/相机/OBS） |
| 命名规则 | `拍摄形式【分镜号范围】.ext`，对齐 storyboard.json（如 `实拍【EP003-S01-001到EP003-S04-001】.mp4`） |
| 拍摄后 | 立即跑 `cheat-shoot` 登记拍摄（内容管线侧，buffer+1） |

### Phase 4：粗剪

| 项 | 内容 |
|---|---|
| 做什么 | 转录 Raw\ + 口误识别 + 粗剪 + 生成字幕 + 输出剪辑项目 |
| 工具 | `video-use`（核心编辑器，集成 ai-jian-koubo 口播处理 + jianying-toolkit 剪映项目生成） |
| 输入 | `Raw\`（原始素材）+ 终稿文稿 + `assets\`（外部素材） |
| 产出 | `Rough\`（粗剪工作目录：edl.json + takes_packed.md + rough_cut_manifest.md + missing_materials.md）<br>`Sub\master.srt`（文稿校准字幕）<br>`ProjectFolder\`（剪映/Filmora 项目） |
| 关键 | 字幕在粗剪**后**生成（不是先字幕再剪，否则时间码全错）；口播处理用 ai-jian-koubo 的精确剪切算法 |
| 交接 | `rough_cut_manifest.md` + `missing_materials.md` 是给 Phase 5 planner 的交接文件 |

### Phase 5：动效规划

| 项 | 内容 |
|---|---|
| 做什么 | 基于粗剪的**实际时间码**，产出最终动效请求清单（哪些地方要动效、多长、什么类型） |
| 工具 | `manuscript-material-planner`（第 2 次执行，Rough-Cut Finalization Workflow） |
| 输入 | `Rough\rough_cut_manifest.md` + `Rough\missing_materials.md` + 粗剪时间码 |
| 产出 | `video scripts\motion_request_list.md`（基于实际时间码，不是预估值） |
| 关键 | Phase 1 的 remotion_candidate_list 只是"候选"——Phase 5 才是"执行令"。已用 facecam/OBS/stock 解决的候选要 drop 掉 |

### Phase 6：动效生成

| 项 | 内容 |
|---|---|
| 做什么 | 按 motion_request_list 生成 Remotion 自定义动效（透明浮层/架构图/数据图表/标题卡等） |
| 工具 | `huanyu-remotion-material`（约束层）+ `remotion-best-practices`（技术规则层） |
| 输入 | `video scripts\motion_request_list.md` |
| 产出 | `Polished\Remotion\MotionXX_Name\`（每个动效一个工作目录：implementation_plan + remotion-project + out\render.mp4） |
| 注意 | 只实现 motion_request_list 里明确列出的动效，不自行添加；技术规则查 remotion-best-practices/rules/ |

#### 动效工具选择（HyperFrames vs Remotion）

见 `motion-graphics-decision-framework.md`。快速规则：
- **HyperFrames**（HTML+CSS+GSAP）：标题卡/字幕同步/转场/浮层/UI 演示——快速原型
- **Remotion**（React+TS）：数据图表/架构图/可复用模板——参数化复杂动效

### Phase 7：精剪成片

| 项 | 内容 |
|---|---|
| 做什么 | 把粗剪 + 动效 + 字幕 + 音乐合成最终成片 |
| 工具 | `video-use`（再跑，加 overlay）或在剪映/Filmora 里手动合成 |
| 输入 | `Rough\edl.json` + `Polished\Remotion\*\out\render.mp4` + `Sub\master.srt` + `assets\`（音乐） |
| 产出 | `Final\video_final.mp4`（可发布） |
| 交接 | 成片齐了 → 回内容管线跑 `cheat-publish` 登记发布 |

---

## 工具速查表

| 触发场景 | 工具 | 阶段 |
|---|---|---|
| "规划分镜"/"出物料清单"/"终稿转 storyboard" | `manuscript-material-planner` | Phase 1（拍摄前）/ Phase 5（粗剪后） |
| "下载素材"/"找音乐"/"asset_request_list" | `media-asset-acquirer` | Phase 2 |
| "粗剪"/"转录"/"剪这个视频"/"剪映项目" | `video-use` | Phase 4 / Phase 7 |
| "生成动效"/"motion_request_list"/"Remotion 动画" | `huanyu-remotion-material` | Phase 6 |
| 口播口误处理（被 video-use 集成，不直接调） | `ai-jian-koubo` | Phase 4 内部 |
| 剪映 draft 生成（被 video-use 集成，不直接调） | `jianying-toolkit` | Phase 4 内部 |
| Remotion 技术规则（参考库，不直接调） | `remotion-best-practices` | Phase 6 内部 |

---

## 工具交接协议

每个工具的输入来自上游、输出给下游。**交接文件是契约**：

| 上游工具 | 交接文件 | 下游工具 |
|---|---|---|
| 内容管线（终稿） | `video scripts\<终稿>.md` | manuscript-material-planner |
| manuscript-material-planner | `assets\requests\asset_request_list.md` | media-asset-acquirer |
| manuscript-material-planner | `video scripts\storyboard.json` | 用户（指导拍摄）+ n8n（飞书） |
| 用户拍摄 | `Raw\*.mp4` | video-use |
| video-use | `Rough\rough_cut_manifest.md` + `missing_materials.md` | manuscript-material-planner（第2次） |
| manuscript-material-planner | `video scripts\motion_request_list.md` | huanyu-remotion-material |
| huanyu-remotion-material | `Polished\Remotion\*\out\render.mp4` | video-use（精剪）或手动合成 |
| video-use / 手动 | `Final\video_final.mp4` | 内容管线 cheat-publish |

---

## 三个衔接点（跟内容管线）

| 衔接点 | 内容管线侧 | 制作管线侧 | 交接物 |
|---|---|---|---|
| ① 终稿交接 | predict v2 确认（Step 6） | Phase 1 planner 开始 | 终稿落到 `video scripts\` |
| ② 拍摄交汇 | cheat-shoot 登记（Step 8） | Phase 3 拍摄 | Raw\ 素材 + 拍摄登记 |
| ③ 成片交接 | cheat-publish 登记（Step 9） | Phase 7 成片 | `Final\video_final.mp4` + 标题/简介/封面物料 |

---

## 每期视频的目录结构

```text
D:\work\OPC\videos\{第X期：视频标题}\
├── video scripts\              ← 终稿 + planner 产出（storyboard/物料清单/motion_request）
├── assets\                     ← media-asset-acquirer 下载的素材 + 许可
├── Raw\                        ← 用户拍摄原片（只读）
├── Rough\                      ← video-use 粗剪工作目录
├── Polished\Remotion\          ← huanyu-remotion-material 动效
├── Final\                      ← 成片
├── Sub\                        ← 字幕
├── Thumb\                      ← 封面
└── ProjectFolder\              ← 剪映/Filmora 项目文件
```

---

## 常见混淆澄清

| 容易混淆 | 正确理解 |
|---|---|
| video-use 和 jianying-toolkit 谁负责剪映项目 | video-use 是核心编辑器；jianying-toolkit 是它调用的"剪映 draft 生成器"，不直接调 |
| ai-jian-koubo 和 video-use 谁负责口播处理 | video-use 集成 ai-jian-koubo 的口误识别 + 精确剪切算法；ai-jian-koubo 不单独跑 |
| huanyu-remotion-material 和 remotion-best-practices | huanyu-remotion-material 是工作流约束层（plan-before-code + 交接纪律）；remotion-best-practices 是技术规则层（怎么写 Remotion 代码） |
| manuscript-material-planner 跑几次 | 两次：Phase 1（拍摄前，出 storyboard 指导拍摄）+ Phase 5（粗剪后，出 motion_request_list 指导动效） |
| remotion_candidate_list 和 motion_request_list 区别 | candidate_list 是 Phase 1 的"候选"（可能用可能不用）；motion_request_list 是 Phase 5 的"执行令"（基于实际粗剪时间码，确定要做） |
