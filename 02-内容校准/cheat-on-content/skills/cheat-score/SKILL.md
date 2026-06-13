---
name: cheat-score
description: 给单篇稿子打 rubric 分。**只在控制台输出，不写文件，不预测**。触发词："打分这篇 [path]"/"score this [path]"/"给这稿子打分"/"先打分看看"。是 cheat-predict 之前的轻量探索动作。
argument-hint: <draft-path>
allowed-tools: Read, Glob, Grep
---

# /cheat-score — 单稿打分

打分但**不预测**。用户用它快速看稿子的 composite，决定是否值得进入正式预测流程。

## Overview

```
[用户：打分这篇 draft.md]
  ↓
[读 draft.md + rubric_notes.md]
  ↓
[逐维度打 0-5 + 写一行理由 + 算 composite]
  ↓
[控制台输出：评分 + composite + 推荐下一步]
  ↓
[结束 — 不写任何文件]
```

## Constants

- **RUBRIC_PATH = rubric_notes.md** — 当前 rubric 来源
- **OUTPUT_DETAIL = full** — full: 含每维度理由；compact: 仅分数表

> 💡 调用时覆盖：`/cheat-score draft.md — OUTPUT_DETAIL: compact`

## Inputs

| 必填 | 来源 |
|---|---|
| `<draft-path>` | 用户作为参数传入；如缺失则在对话里询问 |
| `rubric_notes.md` | 用户项目根 |
| `.cheat-state.json` | 用户项目根（用于读当前 `rubric_version` 与 mode） |

## Workflow

### Step 1：前置检查

1. 读 `.cheat-state.json` → 不存在则提示用户先跑 `/cheat-init`，停止
2. 读 `<draft-path>` → 不存在或无内容 → 报错并停止
3. 读 `rubric_notes.md` 找到当前生效的公式段（一般在"当前评分维度"或"综合分公式"位置）

### Step 2：识别公式与维度

从 `rubric_notes.md` 解析出：
- 当前 rubric_version
- 维度列表与权重（如 `ER×1.5 + SR×1.5 + HP×1.5 + QL + NA + AB + SAT`）
- 归一化常数（如 `/ 8.5 × 2.0`）
- 每个维度的 0-5 含义（从"当前评分维度"段表格读）

如果 `rubric_notes.md` 格式与预期不符（用户手改过结构）→ 询问用户当前公式是哪一行，**不要自己猜**。

### Step 3：**Claude 自己**逐维度打分

**Claude 主动打分**——不让用户来打。这是工具的核心价值（"作弊器"——AI 帮你判断，不是 AI 当你的格式化器）。

对每个维度：
1. 读维度定义 + 0-5 含义
2. 在脑里 anchor 到 0/3/5 的样本对照
3. 选择一个 **整数**（0/1/2/3/4/5——不允许 4.5 之类）
4. 写一行理由（≤ 30 字，引用稿子里的具体词或场景）

**打分速度纪律**（参考 starter-rubrics/opinion-video.md 的 cheat sheet）：
- 每个维度 ≤ 30 秒思考时间。超过就是在合理化，不是在打分
- **相信第一个整数**
- **不查锚点**——先盲打，再对比锚点（避免被锚定）

输出后用户可以挑刺（"AB 给 3 不是 4"），Claude 改值并重新展示。

### Step 4：算 composite + 输出

按当前公式算综合分。控制台输出（OUTPUT_DETAIL=full）：

```
📊 [draft.md 短标题] — 打分（rubric: v2）

| 维度 | 分 | 理由 |
|---|---|---|
| ER (情感共鸣)        | 5 | "半夜三点翻聊天记录" 极端具象 |
| HP (钩子强度)        | 5 | IS 句一句锁定受众 |
| QL (金句密度)        | 5 | MVP 句"间歇性希望"独立可传 |
| NA (叙事性)          | 3 | 平铺直叙，弱弧线 |
| AB (受众广度)        | 5 | 暗恋/前任普适 |
| SR (社会议题共振)    | 2 | 纯个人情感，无社会托底 |
| SAT (讽刺深度)       | 4 | 致谢段自指反讽 |

公式：(ER×1.5 + SR×1.5 + HP×1.5 + QL + NA + AB + SAT) / 8.5 × 2.0
composite = (5×1.5 + 2×1.5 + 5×1.5 + 5 + 3 + 5 + 4) / 8.5 × 2.0 = **8.24**

📍 落在 30-100w 桶（基于 starter-rubrics 的 bucket 边界）

下一步建议：
- 如果你已写定最终稿、准备发布 → 说 "启动预测"
- 如果想再改稿子 → 改完再打一次（多次打分不留痕迹）
- 如果想看历史相近 composite 的样本 → 说 "找 composite 8.0-8.5 的锚点"
```

OUTPUT_DETAIL=compact 时仅输出分数表 + composite，不附理由列。

### Step 5：**绝不**做的事

- ❌ 写任何文件（包括 predictions/、rubric_notes.md、candidates.md）
- ❌ 给 bucket 概率分布（那是 cheat-predict 的活）
- ❌ 触发"已发布"或"复盘"逻辑
- ❌ 提议 rubric 升级（即使打分时发现明显异常也只在控制台提示，不动 rubric）

## Key Rules

1. **整数分**。不允许 4.5、3.7。如果犹豫 → 选低值 + 备注
2. **盲打优先**。打分前不读 anchors（当前样本附近 composite 的旧作品的实绩），避免被实绩锚定
3. **理由是诊断工具**。每个维度的 1-30 字理由不是装饰——复盘时用来找出哪个维度判断错了
4. **不写文件**。这是 score 与 predict 的核心区别。score 是探索，predict 是承诺
5. **不算 candidate composite**。candidates.md 里的 composite 字段在 cheat-trends/cheat-recommend 里写——score 只服务"已写好的具体稿子"

## Refusals

- 「打分顺便预测一下」 → 拒绝。请改用 `/cheat-predict`。原因：predict 必须走 blind check + 写 immutable 日志，score 跳过这些
- 「打完分把分数写进 rubric_notes.md 的观察段」 → 拒绝。observation lifecycle 规定观察必须有"实绩 vs 预测"对比，光有打分不构成观察
- 「能不能直接告诉我会不会爆」 → 拒绝。给具体 composite + bucket 的判定要求走 predict 流程；score 只输出当前 rubric 下的机械计算

## Integration

- 是 `cheat-predict` 的前置探索：用户可以反复 score 不同稿子版本，确定一份再 predict
- score 不更新 `.cheat-state.json`——这是无副作用操作
- 如果用户连续 score 同一稿子 ≥3 次 → 控制台温和提示"反复打分会引入决策疲劳，差不多可以决定了"
