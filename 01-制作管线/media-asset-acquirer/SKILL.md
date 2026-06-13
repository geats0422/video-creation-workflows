---
name: media-asset-acquirer
description: Download, verify, transcode, organize, and document licensed media assets for Huanyu video projects. Use when the user needs royalty-free music, sound effects, stock video, local media preparation, `asset_request_list.md` fulfillment, or asset manifests before Filmora, video-use, or Remotion work. Saves assets under `D:\work\OPC\videos\{第X期：视频标题}\assets` and records license provenance; does not create Remotion animations or edit the main video.
---

# Media Asset Acquirer

Acquire and prepare media assets for a Huanyu video project. Do not create Remotion animations, edit the main video, decide final creative direction, bypass access controls, or use unclear-license media.

## Required Inputs

Prefer reading, in order:

- `asset_request_list.md`
- `motion_request_list.md`
- `material_suggestion_doc.md`

If no asset request exists, ask for the needed asset type, purpose, mood, duration, license requirement, and target video project folder.

## Project Path Rules

Use the same video project root convention as `video-use`:

```text
D:\work\OPC\videos\{第X期：视频标题}\
```

Resolve `{第X期：视频标题}` using this priority:

1. Use the explicit project folder if the user provides it.
2. If a request file is under `D:\work\OPC\videos\...\edit\handoff\`, use that parent video project folder.
3. If the user provides only episode number and title, compose `D:\work\OPC\videos\{第X期：视频标题}\`.
4. If the episode number is missing, inspect `D:\work\OPC\videos\`, infer the next `第X期`, and state the inferred project folder before writing files.

Save all acquired assets under:

```text
D:\work\OPC\videos\{第X期：视频标题}\assets\
```

User-shot originals live in:

```text
D:\work\OPC\videos\{第X期：视频标题}\Raw Footage\
```

Raw footage naming rule: `拍摄形式【分镜号范围】.ext`, aligned with `video scripts\storyboard.json`; examples: `实拍【EP001-S01-001到EP001-S04-001】.mp4`, `OBS录屏【EP001-S05-001到EP001-S10-001】.mp4`.

Treat `Raw Footage\` as read-only user originals. If user-provided OBS or facecam recordings need normalization/transcode, write processed copies under `assets\raw\video\` or the consumer workflow's `edit\` directory, and record the command in `assets\logs\ffmpeg_commands.md`. Never overwrite originals.

Use this structure:

```text
assets\
├── requests\
│   └── asset_request_list.md
├── raw\
│   ├── audio\
│   ├── video\
│   └── image\
├── audio\
│   ├── music\
│   └── sfx\
├── video\
│   └── stock\
├── image\
│   └── stock\
├── licenses\
│   └── media_asset_manifest.json
└── logs\
    └── ffmpeg_commands.md
```

Do not save downloaded media in the skill directory, workspace root, Remotion project directory, or arbitrary temp directories.

## Allowed Asset Types

- Royalty-free background music
- Royalty-free sound effects
- Stock video footage
- Stock images when needed for motion graphics
- User-provided local media
- OBS recordings and facecam recordings that need normalization

## License Rules

Before downloading or using any third-party asset, record:

- Source site
- Source page URL
- Download URL when available
- Title
- Creator
- License name
- Whether commercial use is allowed
- Whether attribution is required
- Whether the asset is editorial-only
- Download date
- Attribution text if needed

Do not use assets when license information is unclear.

Do not download or use copyrighted film/TV clips without permission, DRM-protected content, paywalled content, editorial-only footage for commercial/product videos, or content whose license forbids the intended use.

Use accurate wording: `royalty-free`, `commercial use allowed`, `no attribution required`, `CC0`, or the exact Creative Commons license. Do not call third-party media "copyright-free" unless the source explicitly says so.

## yt-dlp Rules

Use `yt-dlp` only when:

- The source page license allows download and reuse.
- The content is not DRM-protected.
- The content is not behind a paywall.
- The use does not violate the source site's terms.
- The source page URL and license details are recorded in `media_asset_manifest.json`.

Never use `yt-dlp` to bypass access controls or download unclear-license film, TV, platform, or creator content.

## Preferred Sources

For music and sound effects, prefer Pixabay, Mixkit, Freesound with per-file Creative Commons review, or YouTube Audio Library when suitable.

For stock video and images, prefer Pexels, Pixabay, Mixkit, or user-created footage.

Always verify the license on the specific asset page, not just the platform reputation.

## ffmpeg Normalization Rules

Use `ffmpeg` to normalize media after download.

Default music output:

```text
assets\audio\music\asset_XXX_name.wav
```

- WAV
- 48kHz
- Stereo
- PCM 16-bit

Default sound effect output:

```text
assets\audio\sfx\asset_XXX_name.wav
```

- WAV
- 48kHz
- Stereo
- PCM 16-bit
- Trimmed to requested duration when specified

Default stock video output:

```text
assets\video\stock\asset_XXX_name.mp4
```

- MP4
- H.264
- `yuv420p`
- 30fps
- 1080p unless otherwise requested
- AAC 48kHz if audio is retained
- `-an` if the video is intended as silent B-roll

Append every command run to:

```text
assets\logs\ffmpeg_commands.md
```

Use `references/ffmpeg-recipes.md` for command templates.

## Required Manifest

Maintain:

```text
assets\licenses\media_asset_manifest.json
```

Use `references/media-asset-manifest-template.md` for the JSON shape. Update the manifest for every asset, including user-provided local media after normalization.

## Required Output Summary

After processing, report:

- Downloaded assets
- Processed file paths
- License summary
- Attribution requirements
- ffmpeg commands used
- Warnings or unresolved license risks
- Handoff notes for Filmora, `video-use`, or Remotion

## Handoff Rules

Filmora and `video-use` can use files directly from `assets\audio\...`, `assets\video\...`, and `assets\image\...`.

Remotion should not download third-party media. If Remotion needs an acquired asset, copy or sync only the needed processed files into that material project's `remotion-project\public\assets\...`, then reference them with `staticFile()`.

Do not let Remotion read raw downloads directly.
