# Motion Graphics Decision Framework

## HyperFrames vs Remotion — 选哪个？

### 核心区别

| 维度 | HyperFrames | Remotion |
|---|---|---|
| **编写** | 纯 HTML + CSS + GSAP | React 组件 + TypeScript |
| **构建** | 无（index.html 直接播放） | 需要 bundler |
| **AI 友好** | HTML 是 AI 天然产出格式 | JSX/React 项目结构更复杂 |
| **动画** | GSAP timeline（seekable） | useCurrentFrame + interpolate + spring |
| **组件复用** | HTML 模板 + CSS 类 | React props + 组件组合 + TypeScript 类型 |
| **许可** | Apache 2.0（完全开源） | Source-available（公司用有限制） |
| **目录** | `npx hyperframes add <block>` 预制块 | `remotion-best-practices` rules |
| **适合场景** | 快速原型、一次性动效、字幕同步 | 可复用模板、复杂数据可视化、参数化图表 |

### 决策树

```
动效需求进来
    │
    ├─ 需要复用同一个模板（改文字/数据就能用）？
    │   ├─ 是，且需要 props 类型安全 → Remotion
    │   └─ 否 → 继续
    │
    ├─ 复杂数据可视化（图表/架构图/多层级节点）？
    │   ├─ 是，需要 Recharts/d3/多组件 → Remotion
    │   └─ 否 → 继续
    │
    ├─ 需要快速原型 + 浏览器即时预览？
    │   ├─ 是 → HyperFrames
    │   └─ 否 → 继续
    │
    ├─ 字幕/歌词同步到音频？
    │   ├─ 是 → HyperFrames（captions 内置）
    │   └─ 否 → 继续
    │
    ├─ 场景转场（shader/crossfade/wipe）？
    │   ├─ 是 → HyperFrames（shader-transitions catalog）
    │   └─ 否 → 继续
    │
    ├─ 品牌标题卡 / 片头片尾？
    │   ├─ 是 → HyperFrames（HTML 模板快）
    │   └─ 否 → 继续
    │
    └─ 默认 → HyperFrames（除非明确需要 React 组件化）
```

### 快速对照表

| 动效类型 | 推荐 | 原因 |
|---|---|---|
| **标题卡 / 片头片尾** | HyperFrames | HTML+CSS+GSAP，秒级产出 |
| **关键词贴片 / 浮层标注** | HyperFrames | 纯 HTML 叠加 |
| **字幕同步（逐字高亮/karaoke）** | HyperFrames | captions 内置支持 |
| **场景转场（shader/wipe/crossfade）** | HyperFrames | shader-transitions catalog |
| **品牌频道统一包装** | HyperFrames | frame.md 设计系统 + HTML 模板 |
| **架构图（多层级节点+连接线）** | Remotion | 参数化 props + SVG 组件复用 |
| **数据图表（柱状图/折线图/饼图）** | Remotion | Recharts 集成 + 数据驱动 |
| **流程演变动画（状态机/决策树）** | Remotion | 组件状态管理 + 多阶段切换 |
| **可复用模板（跨视频品牌一致）** | Remotion | React 组件 + TypeScript props |
| **代码/配置高亮动画** | HyperFrames | HTML `<pre>` + CSS marker |
| **产品 UI 演示 / mockup-to-video** | HyperFrames | HTML 天然适配 UI |
| **3D / WebGL 效果** | HyperFrames | Three.js adapter |

### EP002 具体推荐

| 场景 | 需求 | 推荐 | 理由 |
|---|---|---|---|
| **S01** 开场黑屏→宫殿亮起 | 简单 fade + title | **HyperFrames** | HTML overlay |
| **S03-002** 八部命名仪式感 | 逐字高亮 + SFX | **HyperFrames** | caption sync |
| **S04-001** 朝代演变图 | 三阶段架构变形 | **Remotion** | 参数化节点 + SVG 变形 |
| **S05-001** 部门信息浮层 | 关键词标注 | **HyperFrames** | HTML 浮层 |
| **S06-002** 递归概念动画 | 循环箭头 + 两层嵌套 | **HyperFrames** | SVG + GSAP |
| **S07** 片尾 CTA | 品牌 endcard | **HyperFrames** | HTML 模板 |

### 工作流中的路径

```
motion_request_list.md（每条动效请求）
    │
    ├─ AI 按决策树推荐工具
    │
    ├─→ HyperFrames 路径:
    │    Rough\animations\slot_<id>\
    │    ├── index.html (HTML + GSAP)
    │    └── render.mp4 (npx hyperframes render)
    │
    └─→ Remotion 路径:
         Polished\Remotion\MotionXX_Name\
         ├── implementation_plan.md
         ├── remotion-project\
         ├── out\
         └── notes.md
```

### 何时用两个一起

| 混合场景 | HyperFrames 做 | Remotion 做 |
|---|---|---|
| 带图表的解说视频 | 标题/转场/字幕 | 数据图表 |
| 产品发布视频 | UI mockup 动画 | 功能流程图 |
| 教程视频 | 代码高亮 + 标注 | 概念架构图 |
