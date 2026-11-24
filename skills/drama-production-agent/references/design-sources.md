# 设计来源与取舍

本工作流是基于公开文档及部分源码观察重新编写的编排技能，不是上游代码拼接版。以下是研究来源；上游持续变化，涉及当前接口或安装时重新核实。本地 helper 不调用这些项目或它们的服务。

| 来源 | 吸收的思路 | 本工作流的选择 |
|---|---|---|
| [Drama Skills 制作流程](https://github.com/zenstory-ai/drama-skills/blob/main/docs/comic-drama-workflow.md) | 创作者可读文档；剧本与视觉设定、分镜分工 | 沿用简洁正文，实际生成才增加机器状态，不把事务账本混进创作正文 |
| [火宝短剧](https://github.com/chatfire-AI/huobao-drama) | 改写、提取、分镜、提示词四类职责；资产引用到生成再合成 | 分工保留为逻辑职责，不限定框架或强制子 Agent |
| [魔因漫创工作流](https://github.com/MemeCalculate/moyin-creator/blob/main/docs/WORKFLOW_GUIDE.md) | 场景/分镜/角色校准；逐镜或镜头组；多模态引用 | 按镜头需求校准，参数读取实时能力，返修考虑整组重生成成本 |
| [PureVis](https://github.com/susirial/purevis_ve_cli) | 总导演路由、视觉导演、图像/视频执行与视觉检查 | 生成前检查关键帧，能力缺失明确标记，避免把素材完成当成整集完成 |
| [Wind Comic 编排代码](https://github.com/ChrisChen667788/wind-comic/blob/main/services/hybrid-orchestrator.ts) | 画风基准、角色特征、局部重生 | 占位素材不得验收；视觉检查失败不默认为通过；禁止无限重生 |
| [Comic Drama Workflow](https://github.com/tccnnd/Comic-drama/blob/main/docs/production_pipeline.md) | 2.5D 分支、统一时间线、导演复核与重新渲染 | 静态/动态制作明确区分，追踪依赖和局部失效 |

融合后的关键关系：

```text
原著/创意/已有产物
  → 可拍剧本 → 视觉设定 → 镜头契约
  → 参考图/关键帧 → 视觉检查
  → 静态后期 或 动态视频生成
  → 视频与声音检查 → 剪辑 → 完整播放验收
               ↑ 问题定位 → 最早出错层的局部返修
```

已实现：技能路由、三种制作形态、创作规范、生产状态约定、返修规则、项目初始化与依赖/文件/验收记录检查。

当前图像固定使用 Codex 内置 image_gen；视频生成等待用户后续接入。依赖宿主能力：实际理解/写作、调用媒体工具、文件下载、视频解码检查、视觉查看、音频听检及剪辑。尚未实现独立调度服务、视频供应商连接器、自动计费/预算系统、GUI 或无人值守视频产线。独立 skill 与插件内 skill 保留相同内容。

## Director Skills 融合版本

来源：[kangarooking/director-skills](https://github.com/kangarooking/director-skills)，固定提交 `459debadf91f85b9603f7adb8c071fbdbf7b29e4`，核对日期 2026-10-07。来源采用 MIT；保留 [上游许可证](../assets/licenses/director-skills-MIT.txt)。这些方法已改编为内部参考，无需安装另外六个 Skill。原仓库的可用标记不是星幕的实测出片证据。

| 上游文件/模块 | 星幕内部方法 | 适配边界 |
|---|---|---|
| cinematic-asset-prompts/SKILL.md、tone-presets、prompt-style-guide | visual-assets.md | 保留资产分类、风格/配色；按剧情决定旧化和视角，内置工具不使用 --ar 或虚标 8K |
| emotion-performance-director/SKILL.md | performance-direction.md | 保留潜台词、观察信号、台词前中后；漫剧和静态形态为本地扩展 |
| action-fight-prompt/SKILL.md、scene-patterns、camera-and-impact | action-effects.md | 保留拆拍、因果、接触反馈和身份绑定；移除固定时长、必须失败、禁固定机位与无配乐通则 |
| travel-skill/SKILL.md、source-frame-spatial-audit、camera-motion-library、motivated-lighting-library、transitions-and-continuity、failure-catalog | spatial-camera.md、quality.md | 空间/摄影/布光适配短剧；原文旅地点与多节点确认不成为默认要求 |
| travel-photo-to-video/SKILL.md | light-motion.md | 只取自然运动、稳定性和单一摄影意图；剧情排序和声音由项目决定 |
| miora-video-studio/SKILL.md | generation-reliability.md、production.md | 只取登记、参数、恢复和文件核验原则；不复制 WorkBuddy 路径/认证/历史规格；共享文件扫描不作为归属证据 |

`story-development.md` 是本次星幕新增编剧方法，不冒充上述仓库的现成技能。保留原有详细导演稿标准；各专项结果合入同一镜头契约及正文。没有引入上游可执行脚本或供应商连接器。
