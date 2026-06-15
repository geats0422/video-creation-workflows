---
name: manuscript-material-planner
description: Convert Huanyu spoken-video manuscripts into storyboard-first production planning files. Use when the user provides a full manuscript, narration draft, storyboard field requirements, Feishu Bitable mapping needs, or rough-cut notes and wants `storyboard.json`, `material_suggestion_doc.md`, `remotion_candidate_list.md`, `music_cue_sheet.json`, `asset_request_list.md`, `feishu_storyboard_records.json`, or rough-cut-stage `motion_request_list.md`. Does not edit video, download assets, generate Remotion code, create Filmora projects, or call Feishu APIs.
---

# Manuscript Material Planner

Act as a pre-production planner, storyboard structurer, and handoff document generator.

Do not edit videos, create Filmora projects, generate Remotion code, download assets, or write to Feishu. Output structured files that n8n, `video-use`, `media-asset-acquirer`, Filmora, and Remotion skills can consume.

## Collaboration Boundary

- `manuscript-material-planner`: Parse manuscript, create storyboard data, derive material/audio/Remotion/Feishu handoff files.
- `media-asset-acquirer`: Download, transcode, organize, and document licensed external assets from `asset_request_list.md`.
- `video-use`: Rough cut facecam/OBS footage, generate Filmora project, and report actual timeline status.
- `huanyu-remotion-material` plus `remotion-best-practices`: Implement only final custom motion materials from `motion_request_list.md`.
- n8n: Read `feishu_storyboard_records.json` and upsert records into Feishu Bitable.

## Project Path Rules

All outputs must stay under:

```text
D:\work\OPC\videos\{第X期：视频标题}\
```

Resolve `{第X期：视频标题}` using this priority:

1. Use the explicit video project folder if the user provides it.
2. If the input manuscript is under `D:\work\OPC\videos\...\video scripts\` or `D:\work\OPC\videos\...\video script\`, use that parent video project folder.
3. If the user provides episode number and title, compose `D:\work\OPC\videos\{第X期：视频标题}\`.
4. If the episode number is missing, inspect existing folders under `D:\work\OPC\videos\`, infer the next `第X期`, and state the inferred project folder before writing files.

Save storyboard and planning documents to:

```text
D:\work\OPC\videos\{第X期：视频标题}\video scripts\
```

Save external asset requests to:

```text
D:\work\OPC\videos\{第X期：视频标题}\assets\requests\asset_request_list.md
```

User-shot originals live in:

```text
D:\work\OPC\videos\{第X期：视频标题}\Raw\
```

Raw footage naming rule: `拍摄形式【分镜号范围】.ext`, aligned with `storyboard.json`; examples: `实拍【EP001-S01-001到EP001-S04-001】.mp4`, `OBS录屏【EP001-S05-001到EP001-S10-001】.mp4`, `实拍【EP001-S05-001第一句话】.mp4`.

Treat `Raw\` as read-only evidence of what was actually shot. Do not write planning files there. When updating storyboard after shooting, reflect real footage choices in `presentation`, `visual`, `execution_note`, `material_analysis`, and derived Feishu/material files.

Rough cut outputs live in `Rough\` and final video in `Final\`. See `video-use` skill for full directory layout.

Never write generated planning files into the skill directory, workspace root, or temp directories.

## Default Manuscript Workflow

When the input is a full manuscript, always follow this order:

1. Generate `storyboard.json`.
2. Generate `material_suggestion_doc.md` from `storyboard.json`.
3. Generate `remotion_candidate_list.md` from `storyboard.json`.
4. Generate `music_cue_sheet.json` from `storyboard.json`.
5. Generate `asset_request_list.md` from `music_cue_sheet.json` and storyboard asset needs.
6. Generate `feishu_storyboard_records.json` for n8n to sync into Feishu Bitable.

Do not skip `storyboard.json`. It is the source of truth for every derived file.

## Rough-Cut Finalization Workflow

When the input includes `rough_cut_manifest.md`, `missing_materials.md`, Filmora/EDL notes, or timecoded clip status, generate or update:

```text
D:\work\OPC\videos\{第X期：视频标题}\video scripts\motion_request_list.md
```

Use actual rough-cut timecodes. Treat earlier Remotion candidates as hypotheses, not execution orders. Drop candidates already solved by facecam, OBS, stock footage, or Filmora packaging.

## Input Rules

The manuscript may contain:

- Pause markers like `//`
- Visual cues like `【画面建议：...】`
- Existing field requirements for Feishu Bitable
- Controlled option lists for presentation, music mood, Remotion value, and status

Important:

- `//` is a pause marker, not a storyboard boundary.
- `【画面建议：...】` is user visual intent, not automatically the final execution plan.

## Segmentation Rules

- Segment by semantic scene, not by `//`.
- One scene should have one clear narrative function.
- Do not over-segment.
- Preserve all user-provided visual cues.
- Use estimated duration before rough cut; final timecodes belong to `video-use` output.

## Required Scene Fields

Each scene in `storyboard.json` must include:

- `scene_id`
- `outline`
- `main_shot_no`
- `sub_shot_no`
- `script_text`
- `estimated_duration_sec`
- `reference_image`
- `presentation.primary`
- `presentation.secondary`
- `visual.suggestion`
- `visual.description`
- `execution_note`
- `music_mood`
- `remotion_value`
- `status`
- `material_analysis`
- `audio_notes`
- `risk_flags`

Use scene IDs like `EP001-S01-001`.

## Controlled Options

Primary presentation must be one of:

- 实拍口播
- 实拍场景
- OBS真实操作录屏
- OBS界面展示
- Remotion全屏解释动画
- Remotion透明浮层
- 万兴喵影模板/素材
- Stock素材/B-roll
- 文生图静帧/参考图
- 混合

Secondary presentation must use one or more:

- 无
- 字幕
- 逐字高亮字幕
- 关键词贴片
- 下三分之一标题
- 框选/箭头/标注
- 局部放大
- 画中画
- 分屏
- Remotion信息浮层
- Remotion流程浮层
- Remotion数据图表
- 万兴喵影转场
- 万兴喵影贴纸/图标
- 评论气泡
- 故障风/扫描线
- 音效点
- 背景音乐
- Stock补充镜头
- 文生图参考

Music mood must be one of:

- 无
- 轻赛博铺底
- 技术纪录片感
- 数据流动感
- 紧张转折
- 部署成功感
- 轻松互动感
- 史诗感但克制
- 低频悬疑
- 温和收束

Remotion value must be one of:

- No
- Maybe
- Yes

Status must be one of:

- 待规划
- 待录制
- 待OBS
- 待补素材
- 待Remotion
- 待配乐
- 待粗剪
- 待精剪
- 已完成

## Material Source Rules

Prefer facecam for emotional delivery, opinions, trust, and direct address.

Prefer OBS for real tools, interfaces, workflows, dashboards, prompts, documents, deployments, and screen actions.

Prefer Filmora for generic transitions, stickers, comment bubbles, lower thirds, normal title cards, and decorative packaging.

Prefer Remotion only for explanation, precision, or reusable custom motion: workflows, architecture, data, decision branches, code/config highlights, transparent educational overlays, or branded motion templates.

Prefer stock/B-roll for abstract atmosphere or visual bridges when real footage is unavailable.

Prefer reference images or text-to-image prompts for ancient metaphors, cyber scenes, or static conceptual images.

## Remotion Candidate Rules

Write a scene to `remotion_candidate_list.md` only when:

- `remotion_value = Yes`, or
- `remotion_value = Maybe` and `material_analysis.reusability = High`.

This file is only a candidate list. It is not final execution. Final Remotion execution waits for rough cut and `motion_request_list.md`.

## Music And SFX Rules

Generate `music_cue_sheet.json` by narrative phase, not one cue per scene.

Do not name specific tracks too early. Describe mood, purpose, intensity, duration estimate, BPM range, SFX keywords, and license requirements.

Generate `asset_request_list.md` only for external assets that need acquisition: music, SFX, stock video, stock images, or reference images.

Do not download assets.

## Feishu Handoff Rules

Generate `feishu_storyboard_records.json` for n8n.

Flatten every scene into one record. Use `scene_id` as the unique key. Include `raw_scene_json` as a JSON string for traceability.

Do not directly call Feishu APIs. n8n handles query, update, and create operations.

## Writing Rules

- Be concrete and production-facing.
- Do not recommend visuals for every sentence.
- Do not use vague phrases like "make it dynamic" without execution detail.
- Keep Remotion as a precision material generator, not a default solution.
- Keep JSON valid when generating `.json` files.
- Use `references/output-template.md` for exact output structures.
