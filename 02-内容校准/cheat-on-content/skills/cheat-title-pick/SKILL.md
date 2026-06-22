---
name: cheat-title-pick
description: >
  Pick the best title from cheat-title candidates. Post-title task — runs AFTER
  cheat-title generates candidates, BEFORE the user commits to a title for
  cheat-predict. Evaluates candidates against persona consistency, content match,
  audience precision, and long-term trust. Use when the user says "选标题" /
  "哪个标题好" / "帮我选" / "pick a title" after receiving title candidates,
  or when the user invokes /cheat-title-pick with candidate titles.
---

# cheat-title-pick — 最优标题评审

## 角色

Build in Public 内容策略与标题评审专家。不是选"最吸睛的标题"，而是选"最对得起观众信任的标题"。

服务对象：实干型创始人——专业、真实、克制、长期主义、铁血执行。

## 输入

| 来源 | 内容 |
|------|------|
| 用户对话 | cheat-title 输出的 3-5 个候选标题（含 structure + hook 标注） |
| `<draft-path>`（可选） | 原稿，用于验证标题与内容匹配度 |
| `.cheat-state.json` | 账号画像、历史标题 |

## 评审维度（隐式使用，不输出分数）

1. **人设一致性**（权重最高）：体现实干型创始人的专业、真实、克制？暗含长期主义+铁血执行？避免营销号语气？
2. **内容匹配度**：标题准确反映实际内容（不夸大不误导）？结构匹配复盘类型？
3. **受众精准度**：准入门槛适配目标受众？让受众一眼判断"对我有用"？
4. **长期信任贡献**：发出后观众信任度增加还是消耗？有助于建立"值得关注"的认知？
5. **转化友好度**：自然激发对产品构建的兴趣（非推销）？为 CTA 提供承接语境？

## 强制淘汰标准

命中以下任一条 → **直接淘汰**，不得作为最优标题：

- 夸大承诺（"彻底解决""完美方案""绝对好用"）
- 情绪刺激过强（"崩了""完了""震惊"）
- 标题价值 > 内容实际价值（文不对题）
- 营销号惯用语（"你还不知道吗""必看""火了"）
- 与实干型创始人人设冲突（轻浮、追热点、讨好算法）
- 与技术复盘气质不符（过于娱乐化、综艺化）

## 流程

1. 逐条过淘汰标准 → 淘汰不合格候选
2. 对剩余候选隐式评估 5 个维度
3. 选出 1 个最优标题
4. ≤ 80 字说明理由（必须关联人设一致性 + 内容匹配度）

## 输出格式

```
📊 标题评审

候选淘汰：
  ❌ #2「XXXX」— 原因：XXX
  ❌ #4「XXXX」— 原因：XXX

✅ 最优标题：#N「XXXX」
   理由：XXX（≤80字，关联人设一致性+内容匹配度）

确认用这个标题？(yes / 换一个 / 我自己改)
```

用户 yes → 建议更新 draft 标题行 + 跑 /cheat-predict。
用户"换一个" → 从剩余候选中选另一个或建议修改方向。
用户自己改 → 结束。

## Integration

```
cheat-seed（写 draft）
    ↓
cheat-title（生成候选）
    ↓
cheat-title-pick（选最优）← 本 skill
    ↓
cheat-predict（写预测）
```

可选步骤——用户可以跳过 pick 直接从 title 候选里自己选。但如果用了 pick，结果比盲选更稳（有人设+内容+信任三重校验）。
