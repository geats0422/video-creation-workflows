---
name: huanyu-remotion-material
description: Generate short, reusable Remotion motion-graphics materials for Huanyu video production from `motion_request_list.md`. Use with the official `remotion-best-practices` skill when implementing transparent overlays, workflow explainers, architecture diagrams, product UI demos, data visualizations, code/config highlights, branded title cards, or other custom materials that will be imported into Filmora after `video-use` rough cutting. Enforces plan-before-code, one material per composition, props-based vague visual controls, export commands, and strict separation from full-video editing.
---

# Huanyu Remotion Material

Act as the Remotion material production constraint layer. Use the official `remotion-best-practices` skill for technical Remotion rules; use this skill for Huanyu's workflow boundaries and handoff discipline.

## Role

Generate short, precise, reusable Remotion motion-graphics materials for edited videos.

Do not create full-length videos. Do not edit main footage. Do not replace Filmora, OBS, `video-use`, or `manuscript-material-planner`.

## Required Input

Prefer reading `motion_request_list.md`.

Only implement motion materials explicitly listed there. Do not re-analyze the full manuscript unless the user explicitly asks. Do not add extra motion graphics that are not requested.

If no `motion_request_list.md` exists, ask for one or ask the user to run `manuscript-material-planner` in rough-cut finalization mode first.

## Project Path Rules

Use the same per-video directory convention as `video-use`.

All inputs and outputs must stay under:

```text
D:\work\OPC\videos\{第X期：视频标题}\
```

User-shot originals live in:

```text
D:\work\OPC\videos\{第X期：视频标题}\Raw Footage\
```

Treat `Raw Footage\` as read-only source/reference material. Do not create Remotion projects there, do not render into it, and do not overwrite or normalize files in place. If a Remotion material needs visual reference from an original recording, copy only the required still/reference excerpt into the material workspace `reference\` or use processed clips supplied from `edit\`.

Resolve `{第X期：视频标题}` using this priority:

1. Use the explicit video project folder if the user provides it.
2. If `motion_request_list.md` is under `D:\work\OPC\videos\...\edit\handoff\`, use that parent video project folder.
3. If the user provides only an episode number and title, compose `D:\work\OPC\videos\{第X期：视频标题}\`.
4. If the episode number is missing, inspect existing folders under `D:\work\OPC\videos\`, infer the next `第X期`, and state the inferred project folder before writing files.

Prefer this input path:

```text
D:\work\OPC\videos\{第X期：视频标题}\edit\handoff\motion_request_list.md
```

For each motion request, create one material workspace:

```text
D:\work\OPC\videos\{第X期：视频标题}\edit\remotion\MotionXX_CompositionName\
├── implementation_plan.md
├── remotion-project\
├── reference\
├── out\
└── notes.md
```

Never create Remotion projects or rendered assets inside the skill directory, official Remotion skill directory, workspace root, or arbitrary temp directories.

## External Media Asset Rule

Do not download third-party media directly.

If music, sound effects, stock video, stock images, or other external media are needed, read prepared assets from the video project asset root:

```text
D:\work\OPC\videos\{第X期：视频标题}\assets\
```

Expected processed asset folders:

```text
assets\audio\music\
assets\audio\sfx\
assets\video\stock\
assets\image\stock\
assets\licenses\media_asset_manifest.json
```

If required assets are missing, create or update:

```text
D:\work\OPC\videos\{第X期：视频标题}\assets\requests\asset_request_list.md
```

Then ask the user to run `media-asset-acquirer`. Do not use `yt-dlp`, browser downloads, or direct remote URLs from Remotion code.

When implementing the Remotion material, copy only the needed processed files into:

```text
<material_workspace>\remotion-project\public\assets\
```

Reference local copied assets with `staticFile()`. Do not reference raw downloads directly. Do not skip `media_asset_manifest.json` when third-party assets are used.

## Production Context

The workflow is:

```text
script
-> manuscript-material-planner
-> material_suggestion_doc.md + remotion_candidate_list.md
-> facecam / OBS recording
-> video-use rough cut + Filmora project
-> rough_cut_manifest.md + missing_materials.md
-> manuscript-material-planner
-> motion_request_list.md
-> media-asset-acquirer if external music, SFX, stock video, or stock images are needed
-> huanyu-remotion-material + remotion-best-practices
-> exported assets
-> Filmora fine edit
```

## Use Remotion For

- Workflow explanation
- Architecture diagrams
- Product or UI walkthroughs
- Data visualization
- Code or config highlights
- Transparent educational overlays
- Reusable branded title cards
- Precise animation that Filmora templates cannot express

Do not use Remotion for generic transitions, simple stickers, stock replacement, mood-only effects, facecam editing, full-length editing, or effects Filmora can solve faster.

## Workflow Rule: Plan Before Code

Before modifying code, output an implementation plan and wait for confirmation unless the user explicitly says to implement directly.

The plan must include:

- Motion request ID
- Composition name
- Purpose
- Format
- Duration
- Timeline plan
- Layout plan
- Props design
- Data source
- Library choices
- Export commands
- Risks and assumptions

Use `references/implementation-plan-template.md` when drafting the plan.

## One Material At A Time

Implement one motion material at a time.

One motion request equals one Remotion composition. Do not batch-build multiple compositions unless explicitly requested.

## Default Material Specs

- Horizontal: `1920x1080`, `30fps`
- Vertical: `1080x1920`, `30fps`
- Overlay duration: `4-8s`
- Full-frame insert duration: `6-15s`
- Title card duration: `3-6s`

Respect the duration, resolution, FPS, and format in `motion_request_list.md` when provided.

## Library Selection

Default preference:

1. Plain React + SVG + CSS for static styling
2. Remotion built-ins
3. Recharts for simple charts
4. React Three Fiber only for necessary 3D
5. Mapbox or AMap only for real map materials

Before adding a dependency, explain why it is needed, whether plain React/SVG can do it, the maintenance cost, the exact install command, and whether the dependency is reusable across future materials.

Do not install new libraries without confirmation.

For map materials, use a real map source or explicitly label the result as a schematic map. Do not imply geographic accuracy when using decorative geometry.

## Parameterization Rule

Expose ambiguous visual values as props. Do not hard-code request-specific text inside reusable components. Put request text in props or `src/data/`.

Common props:

- `title`
- `subtitle`
- `labels`
- `accentColor`
- `backgroundStyle`
- `overlayPosition`
- `safeArea`
- `cameraZoom`
- `cameraX`
- `cameraY`
- `cardScale`
- `nodeGap`
- `glowIntensity`
- `gridOpacity`
- `lineSpeed`
- `animationSpeed`
- `titleFontSize`
- `subtitleFontSize`
- `showGrid`
- `showLabels`

## Timing Rules

Use Remotion timing primitives:

- `useCurrentFrame`
- `useVideoConfig`
- `Sequence`
- `interpolate`
- `spring`

Avoid CSS animation, CSS transition, `setTimeout`, `requestAnimationFrame`, and random animation that changes across renders.

## Project Structure

When creating or modifying a Remotion project, prefer:

```text
<video_project>/edit/remotion/MotionXX_CompositionName/
  implementation_plan.md
  remotion-project/
    src/
      compositions/
      components/
        materials/
      data/
    public/
      assets/
  reference/
  out/
  notes.md
```

Keep generic UI and motion components in `src/components/materials/`. Keep request-specific data in `src/data/`. Keep composition wrappers in `src/compositions/`.

When using acquired media, copy processed assets from `<video_project>\assets\...` into `remotion-project\public\assets\...` and keep a note in `notes.md` linking back to `assets\licenses\media_asset_manifest.json`.

## Export Rules

For every implemented material, provide commands for Studio preview, still check, MP4 insert, transparent WebM overlay, PNG sequence, and ProRes 4444 transparent video when useful for editing software.

Run Remotion commands from `<video_project>\edit\remotion\MotionXX_CompositionName\remotion-project\`. Render outputs to the sibling `..\out\` folder so Filmora imports from a stable project-local path.

Use `references/export-formats.md` for command templates.

## Reference Video Rule

If the user provides a reference video, use it only to analyze pacing, layout density, transition rhythm, and motion feel. Do not directly copy copyrighted expression, unique design systems, logos, or proprietary layouts.

## Reusability Rule

After implementation, classify the material as:

- `one-off`
- `reusable with text changes`
- `reusable template`

If reusable, separate generic components from request-specific data.

## Quality Checklist

Before finishing, verify:

- TypeScript passes or report why it could not be run.
- No unused variables remain.
- Chinese text is readable.
- Text stays inside safe area.
- Transparent materials have no background.
- Animation is deterministic.
- Hard-to-describe visual values are props.
- Export commands are included.
- The material does not become a full video.
