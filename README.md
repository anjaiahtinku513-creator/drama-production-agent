# 星幕 · 短剧与漫剧制作 Agent

面向 Codex 的中文制作工作流。从故事、小说或已有剧本推进到分集、视觉设定、分镜、逐拍导演稿和制作验收。支持真人短剧、动态漫剧和静态漫剧。

- **剧本与分镜**　梳理角色目标、阻碍与选择，为每拍编排表演、摄影、动作与声音，并记录镜头间的起止状态。
- **资产与关键帧**　为角色、场景、道具建立可复用的参考和造型，按宿主提供的内置图像工具生成与检查。
- **导演稿与返修**　输出完整审核稿和独立镜头提示词，跟踪真实素材、交付依赖和局部返修范围。
- **本地项目检查**　用 Python 脚本初始化项目，查询动作、依赖、素材文件哈希及已记录的验收结果。

## 安装

在克隆后的仓库根目录执行下列命令。 [Codex 插件文档](https://developers.openai.com/plugins/build/plugins)

```bash
codex plugin marketplace add .
codex plugin add drama-production-agent@xingmu
```

也可只安装独立技能。在仓库根目录将技能目录复制到 Codex 的用户技能目录，再打开新对话。使用一种安装方式即可。 [Codex 技能文档](https://learn.chatgpt.com/docs/build-skills)

```bash
mkdir -p ~/.agents/skills
cp -R skills/drama-production-agent ~/.agents/skills/
```

## 使用

在 Codex 新对话中选择星幕插件或输入 `$drama-production-agent`，附上故事、制作要求或已有素材。例如

> 用 $drama-production-agent 把下面的故事改成 60 秒竖屏动态漫剧，先交付剧本、视觉设定、分镜和完整导演提示词。

> 用 $drama-production-agent 继续这个项目，只修第 4 镜的道具换手，并检查前后镜的交接。

图像生成由 Codex 会话提供的内置 `image_gen` 执行。仓库当前提供视频提示词和接入流程，实际视频生成须由用户配置兼容工具。配音、音乐与剪辑依赖当前项目可用的媒体工具。 [视频接入说明](skills/drama-production-agent/references/video-integration.md)

## 本地项目脚本

需要 Python 3.9 或更新版本，使用标准库。以下命令会在示例目录创建 `project.json`，随后读取其中的交付记录。空项目的 `status` 退出码为 `2`，表示尚无通过检查的交付记录。

```bash
python3 -X utf8 skills/drama-production-agent/scripts/project.py init ./demo-project --title "停雨前" --mode motion-comic
python3 -X utf8 skills/drama-production-agent/scripts/project.py status ./demo-project
python3 -m unittest discover -s skills/drama-production-agent/scripts -v
```

脚本检查记录、文件存在性和哈希。素材的视觉、听音和完整播放验收由制作人员通过实际素材完成。

## 工作流与许可

- [技能入口](skills/drama-production-agent/SKILL.md)
- [导演提示词模板](skills/drama-production-agent/assets/director-prompt-template.md)
- [原创虚构项目示例《停雨前》](skills/drama-production-agent/references/director-prompt-example.md)
- [设计来源](skills/drama-production-agent/references/design-sources.md)
- [MIT License](LICENSE) · [第三方声明](THIRD_PARTY_NOTICES.md)
