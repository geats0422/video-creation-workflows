---
name: jianying-toolkit
description: Create and manipulate 剪映 (JianYing/CapCut) draft files directly via CLI — no server, no ports, no MCP. Generates native 剪映 draft_content.json that opens directly in 剪映专业版. Use when the user needs to automate 剪映 video editing: create drafts, add video/audio/image/text/subtitle/effect/sticker tracks, and save to 剪映's draft folder. Commands map to /create_draft, /add_video, /add_audio, /add_text, /add_subtitle, /add_image, /add_effect, /add_sticker, /save_draft.
---

# JianYing Toolkit

Directly generates 剪映 (JianYing) native draft files via CLI. No HTTP server, no port conflicts, no MCP protocol — just Python script calls.

## Architecture

The skill wraps `pyJianYingDraft` library (located at `D:\work\Huanyu Code\template\capcut-mcp\pyJianYingDraft\`) into a single CLI script. Draft state persists between commands via pickle files in a cache directory.

```
jianying.py CLI command
    ↓
load draft from pickle cache
    ↓
modify via pyJianYingDraft API
    ↓
save draft to pickle cache
    ↓
(save_draft) export to 剪映 draft_content.json + copy media to assets/
```

## Script Location

```
scripts/jianying.py — single CLI entry point for all commands
```

## Commands

### create_draft — Create new 剪映 project

```bash
python scripts/jianying.py create_draft \
  --width 1920 --height 1080 \
  --cache-dir "<video_project>/Rough/.jianying_cache"
```

Returns `{"draft_id": "dfd_jy_...", "width": 1920, "height": 1080}`. Use the `draft_id` for all subsequent commands.

### add_video — Add video clip to timeline

```bash
python scripts/jianying.py add_video \
  --draft-id <id> --cache-dir <dir> \
  --file "D:/path/to/video.mp4" \
  --start 45.0 --end 55.0 \
  --target-start 0 \
  --speed 1.0 \
  --track-name "main"
```

| Parameter | Required | Description |
|---|---|---|
| `--file` | Yes | Video file path (local) |
| `--start` | No | Source in-point (seconds). Default: 0 |
| `--end` | No | Source out-point (seconds). Default: full duration |
| `--target-start` | No | Timeline position (seconds). Default: 0 |
| `--speed` | No | Playback speed. Default: 1.0 |
| `--track-name` | No | Track name. Default: "main" |

### add_audio — Add audio/music track

```bash
python scripts/jianying.py add_audio \
  --draft-id <id> --cache-dir <dir> \
  --file "D:/path/to/music.wav" \
  --start 0 --end 30 \
  --volume 0.8 \
  --track-name "bgm"
```

### add_text — Add text overlay

```bash
python scripts/jianying.py add_text \
  --draft-id <id> --cache-dir <dir> \
  --text "首辅" \
  --start 2 --end 5 \
  --font-size 30 --font-color "#FF0000"
```

`--font-color` uses hex format (`#RRGGBB`). `--font-size` is in 剪映 internal units.

### add_subtitle — Import SRT subtitles

```bash
python scripts/jianying.py add_subtitle \
  --draft-id <id> --cache-dir <dir> \
  --srt "D:/path/to/Sub/master.srt" \
  --time-offset 0 \
  --font-size 5.0 --font-color "#FFFFFF"
```

Uses pyJianYingDraft's `import_srt()` — creates one text segment per SRT entry automatically.

### add_image — Add image/picture

```bash
python scripts/jianying.py add_image \
  --draft-id <id> --cache-dir <dir> \
  --file "D:/path/to/image.png" \
  --width 1920 --height 1080 \
  --start 0 --end 5
```

### add_effect — Add visual effect

```bash
python scripts/jianying.py add_effect \
  --draft-id <id> --cache-dir <dir> \
  --effect "金粉闪闪" \
  --start 0 --end 3
```

See `references/effects_catalog.md` for available effect names.

### add_sticker — Add sticker

```bash
python scripts/jianying.py add_sticker \
  --draft-id <id> --cache-dir <dir> \
  --sticker-id "<resource_id>" \
  --start 0 --end 3
```

### save_draft — Export to 剪映 draft folder

```bash
python scripts/jianying.py save_draft \
  --draft-id <id> --cache-dir <dir> \
  --output "<剪映系统设置里的草稿根路径>"
```

> ⚠️ **`--output` 必须用剪映 GUI 设置里的实际草稿根路径，不要用下面的"默认 Windows 路径"占位符**。很多用户（包括本 skill 维护者）会把剪映草稿位置从默认 C 盘改到 D 盘以节省系统盘空间。如果用了错误的默认路径，save_draft 会把 1GB+ 的草稿+assets 写到 C 盘，剪映 GUI 也看不到。
>
> 如何确认实际路径：剪映专业版 → 全局设置 → 草稿 → "草稿位置"字段就是剪映实际读取的根目录。

Copies template files, writes `draft_content.json`, and copies all referenced media to `assets/`. Open 剪映专业版 and the draft appears in the project list.

**配合 video project 归档**：如果项目目录已建 `Jianying-draft/` 并在剪映草稿根建了 symlink 指向它（详见 [video-folder-schema.md](../../../../.opencode/skill/cheat-on-content/shared-references/video-folder-schema.md) 的 symlink 段），`--output` 直接用剪映草稿根 + `--name "<视频标题>"`（symlink 名字），草稿通过 symlink 自动写入项目目录，剪映正常识别。

## Draft Cache

Between commands, draft state persists as `.pkl` files:
```
<cache-dir>/
└── <draft_id>.pkl    ← pickled Script_file object
```

Use `<video_project>/Rough/.jianying_cache/` as the cache directory for each video project.

## Typical Workflow

```bash
CACHE="<video_project>/Rough/.jianying_cache"
DRAFT="<video_project>/Rough/.jianying_cache"

# 1. Create
DID=$(python jianying.py create_draft --width 1920 --height 1080 --cache-dir $CACHE | jq -r .draft_id)

# 2. Add video segments (from cut decisions)
python jianying.py add_video --draft-id $DID --cache-dir $CACHE --file "obs.mp4" --start 45 --end 55 --target-start 0 --track-name main
python jianying.py add_video --draft-id $DID --cache-dir $CACHE --file "obs.mp4" --start 60 --end 75 --target-start 10 --track-name main
python jianying.py add_video --draft-id $DID --cache-dir $CACHE --file "phone.mp4" --start 1 --end 31 --target-start 25 --track-name main

# 3. Add subtitles (from align_to_manuscript.py output)
python jianying.py add_subtitle --draft-id $DID --cache-dir $CACHE --srt "<video_project>/Sub/master.srt"

# 4. Add background music
python jianying.py add_audio --draft-id $DID --cache-dir $CACHE --file "music.wav" --volume 0.3 --track-name bgm

# 5. Add text overlay
python jianying.py add_text --draft-id $DID --cache-dir $CACHE --text "首辅" --start 2 --end 5 --font-size 30

# 6. Save to 剪映
python jianying.py save_draft --draft-id $DID --cache-dir $CACHE --output "<剪映draft目录>"
```

## 剪映 Draft Folder Location

| Platform | Path |
|---|---|
| Windows (剪映) | `C:\Users\<user>\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft` |
| Mac (剪映) | `~/Movies/JianyingPro/User Data/Projects/com.lveditor.draft` |
| Windows (CapCut) | `C:\Users\<user>\AppData\Local\CapCut\User Data\Projects/com.lveditor.draft` |

## Dependencies

- Python 3.8+
- `pyJianYingDraft` library (at `D:\work\Huanyu Code\template\capcut-mcp\`)
- `ffmpeg` / `ffprobe` (for media duration/dimension probing)
- The script auto-injects a fake `settings` module to satisfy pyJianYingDraft's import without the MCP server

## Integration with Video Production Pipeline

This skill replaces the FCPXML/prproj export path entirely. The workflow becomes:

```
Whisper + AI剪口播 → cut decisions → jianying-toolkit → 剪映 draft → open in 剪映
```

No format conversion, no import failures — the draft is 剪映's native format.
