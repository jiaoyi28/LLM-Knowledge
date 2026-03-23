
## 基本概念
教 AI 按固定流程做事的操作说明书，一旦写好，就能像函数一样反复调用。

我们可以把 Skills 看成把 某类事情应该怎么专业做 这件事，封装成一个可复用、可自动触发的能力模块。

Skills 以 Markdown 文件形式存在，不执行功能，而是通过按需、渐进式加载，实现高效且可复用的经验传递。

**Skills 和传统 Prompt 最大的区别是：按需加载 + 渐进式披露（只在需要时才把厚厚的 SOP 塞进上下文，极大节省 token）。**

## 和MCP的区别
![[file-20260311145543800.png]]
## Skills的核心机制
Skill的核心就是渐进式披露，将一个Skill的信息分为三层结构，按需、逐步的依次加载到上下文。三层分别为：skill.md中的 header、skill.md全文、skill.md中的文件引用
![[file-20260311150152936.png]]

下图是在 Claude Code中，Skills是如何加载到上下文的，并通过 Bash(cat xxxx/SKILL.md）加载全文
![[file-20260311145840282.png]]

## Skill的结构
Skills 的核心就是：一个文件夹 + 一个 SKILL.md 文件。

**SKILL.md 文件包含：**
- 元数据（至少要有名称和描述），或者叫 header
- 告诉 AI 如何完成某一特定任务的指令

一个 Skill 本质上就是一个 Markdown 文件（文件名固定为 SKILL.md）
```
my-skill/
└── SKILL.md   （唯一必需）
```

SKILL.md 基本模板:
```
---
name: pdf-processing
description: 从 PDF 中提取文本和表格，填写表单，并合并文档
---

# PDF 处理

## 使用场景
当需要对 PDF 文件进行操作时使用，例如：

- 提取 PDF 文本或表格数据
- 填写 PDF 表单
- 合并多个 PDF 文件

## 提取文本
- 使用 `pdfplumber` 提取文本型 PDF 内容  
- 扫描版 PDF 需配合 OCR 工具  

## 填写表单
- 读取 PDF 表单字段  
- 按输入数据填充并生成新文件
```
最小必填示例:
```
---
name: skill-name
description: 说明该 Skill 的功能以及适用场景
---
```
含可选字段示例:
```
---
name: pdf-processing
description: 从 PDF 中提取文本和表格，填写表单，并合并文档
license: Apache-2.0
metadata:
  author: example-org
  version: "1.0"
---
```
如果你需要一些参考资料，参考实例，执行脚本，可以使用更复杂的 Skill 的目录结构：
```
my-skill/
├── SKILL.md      # 必需：指令 + 元数据
├── scripts/      # 可选：可执行代码
├── references/   # 可选：文档资料
└── assets/       # 可选：模板、资源
```

## Skills的安装使用
当前Skills主流使用在 cursor、claude code、codex、opencode、openclaw 中，且通常都会分为三个级别，Agent会按个人级、项目级、插件级的顺序进行查找加载，越具体的位置使用优先级越高。

Skills的安装也非常的简单，最简单的方法就是直接将Skill目录粘贴到对应的应用目录下面，就可以自动加载了。每个 Skill 就是一个文件夹，文件夹名即技能标识（推荐 kebab-case 小写+连字符），如"code-comment-expert"

### claude code

| 级别  | 路径                                       | 生效范围     |
| --- | ---------------------------------------- | -------- |
| 企业级 | 通过管理控制台配置（managed settings）              | 组织内所有用户  |
| 个人级 | `~/.claude/skills/<skill-name>/SKILL.md` | 你所有项目    |
| 项目级 | `.claude/skills/<skill-name>/SKILL.md`   | 仅当前项目    |
| 插件级 | `<plugin>/skills/<skill-name>/SKILL.md`  | 启用该插件的环境 |


### cursor
cursor对claude code和code进行了兼容，会自动从这些位置加载：

|位置|级别|
|---|---|
|`.agents/skills/`|项目级|
|`.cursor/skills/`|项目级|
|`~/.cursor/skills-cursor/`|用户级 (全局)|

出于兼容性考虑，Cursor 也会从 Claude 和 Codex 的目录中加载技能：`.claude/skills/`、`.codex/skills/`、`~/.claude/skills/` 和 `~/.codex/skills/`。

对于windows系统来说 `~`就是`C:\Users\username\`

### opencode
OpenCode 会搜索以下位置：‘
|位置|级别|
|---|---|
|`~/.config/opencode/skills`|用户级|
|`~/.claude/skills`|用户级|
|`~/.agents/skills`|用户级|
|`.opencode/skills`|项目级|
|`.claude/skills`|项目级|
|`.agents/skills`|项目级|

同样对 claude code 进行了兼容

### openclaw

### Skills的快捷安装
除了使用下载Skills源码，放到目录的方法进行安装。社区还有两种主流的安装方法：1. 通过[skills.sh](https://skills.sh/)；2. 通过[openSkills](https://openskills.cc/zh); 3. [Anthropic官方skills仓]([https://github.com/anthropics/skills](https://github.com/anthropics/skills))

推荐使用 skills.sh，最全最方便

### 使用skills.sh安装Skill
直接执行 `npx skills add` 命令，例如
```
npx skills add https://github.com/anthropics/skills --skill skill-creator
```
其中的 url 可以到[skills.sh](https://skills.sh/)查找，也可以通过 `npx skills find` 来交互式查找，具体进行项目级或者全局安装，可以自选

更多用法（更新、list、options），可以执行 `npx skills --help` 查看

## 推荐Skills
|Skill|核心作用|安装命令|
|---|---|---|
|find-skills (vercel-labs)|技能搜索与推荐中心|`npx skills add vercel-labs/skills`|
|vercel-react-best-practices|React / Next 性能优化规范|`npx skills add vercel-labs/agent-skills --skill vercel-react-best-practices`|
|frontend-design (anthropics)|高质量 UI 设计能力|`npx skills add anthropics/skills --skill frontend-design`|
|web-design-guidelines|Web 可访问性与 UX 规范|`npx skills add vercel-labs/agent-skills --skill web-design-guidelines`|
|remotion-best-practices|React 视频制作最佳实践|`npx skills add remotion-dev/skills --skill remotion-best-practices`|
|brainstorming (superpowers)|结构化思考与规划能力|`npx skills add obra/superpowers --skill brainstorming`|
|agent-browser|浏览器自动化控制|`npx skills add vercel-labs/agent-browser`|
|browser-use|高性能浏览器交互|`npx skills add browser-use/browser-use`|
|supabase-postgres-best-practices|Supabase / PostgreSQL 优化|`npx skills add supabase/agent-skills --skill supabase-postgres-best-practices`|
|azure-cost-optimization|Azure 云成本优化|`npx skills add microsoft/github-copilot-for-azure --skill azure-cost-optimization`|
|cloudflare/skills|Workers 与边缘计算实践|`npx skills add cloudflare/skills`|
|redis/agent-skills|Redis 高级模式与反模式|`npx skills add redis/agent-skills`|
|vercel-composition-patterns|React 组合模式规范|`npx skills add vercel-labs/agent-skills --skill vercel-composition-patterns`|
|vercel-react-native-skills|React Native 官方最佳实践|`npx skills add vercel-labs/agent-skills --skill vercel-react-native-skills`|
|sleek-design-mobile-apps|现代移动 App 设计指南|`npx skills add sleekdotdesign/agent-skills --skill sleek-design-mobile-apps`|
|ui-skills|设计师级 UI 与交互实践|`npx skills add ibelick/ui-skills`|
|pdf (anthropics)|PDF 生成与解析能力|`npx skills add anthropics/skills --skill pdf`|
|seo-audit|SEO 审计与优化|`npx skills add coreyhaines31/marketingskills --skill seo-audit`|
|skill-creator|自定义 Skill 构建能力|`npx skills add anthropics/skills --skill skill-creator`|
|code-review-expert|专业级代码审查能力|`npx skills add sanyuan0704/code-review-expert`|