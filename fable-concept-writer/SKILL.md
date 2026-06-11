---
name: fable-concept-writer
description: Use this skill when the user asks to write, draft, revise, or generate a Chinese fable that indirectly explains an advanced concept from cognitive science, behavioral economics, game theory, social psychology, systems science, complexity science, learning science, organizational behavior, communication/pragmatics, moral philosophy, evolutionary psychology, ecology, statistics/causal inference, psychoanalysis/attachment theory, or anthropology. Triggers include "寓言", "寓言写作", "用寓言解释概念", "每日寓言", "今天写一个概念寓言", or requests that match the provided fable-writing prompt.
---

# Fable Concept Writer

把一个研究生水平概念写成真正像寓言的短故事：先让故事成立，再让概念在结尾附近浮现。默认中文。

## Workflow

1. 选题：若用户未指定概念，按今天日期在领域池中轮换选一个领域，再选一个研究生水平概念；避免重复最近 `outputs/` 中已写过的概念。
2. 写作：正文 1000 字以内；不出现概念名、学科名或领域术语；不让角色解释道理。
3. 自检：先避开黑名单，再检查故事是否靠一个核心场景和一两次转折承载意义。
4. 交付：正式结果写入 `outputs/{YYYY-MM-DD}_{概念名}_寓言.md`；聊天里只简要说明文件路径。若用户明确要直接看正文，可同时贴出三部分内容。

## Domain Pool

按日期轮换使用这些领域：认知科学、行为经济学、博弈论、社会心理学、系统科学、复杂性科学、学习科学、组织行为学、传播学/语用学、道德哲学、进化心理学、生态学、统计学/因果推断、精神分析/依恋理论、人类学。

选概念时优先挑“能被一个具体互动场景完整包住”的概念；不要选只能靠定义解释的概念。

## Story Rules

- 角色不超过 3 个，最好 2 个；关系或互动本身承载寓意。
- 可用非人类视角：工具、动物、植物、器物、机构。
- 优先现代具体场景：理赔、维修、门诊、分拣、外卖站、菜市场、二手房、夜班等。
- 优先微观切口：一次交易、一次电话、一次拆卸、一次交接、一次排队。
- 直接进入场景，不用传统寓言开场。
- 接近结尾时只让读者隐约意识到讲的是什么，不要点破。

## Avoid

意象黑名单：钟、河流、镜子、迷宫、织布机、地图、灯塔、棋盘、回声、影子、沙漏、风、蜡烛、种子、桥、星辰、蝴蝶、蛛网。

地名黑名单：不要写“回声城”“记忆之村”“遗忘之海”“寂静谷”这类文艺化地名；用普通地理名词，或不命名。

结构黑名单：旅行者求教智者；村庄异象后众人顿悟；孩童一句话点醒大人；师徒辩难；临终遗言。

角色黑名单：钟表匠、图书管理员、隐士、说书人、老船夫、酿酒师、铁匠、抄经人。

开头黑名单：不要用“从前有个地方”“某天某人遇见某事”“在很远的山里”等起手式。

## Output Contract

文件内容固定三部分：

```markdown
## 寓言正文

（直接写故事，不加标题、不加引导语。）

## 概念解析

1. 概念名、所属学科/流派、核心定义。
2. 逐一对应故事元素与概念结构。

## 检验问题

1. 理解检验：一个具体可答的问题，检验是否理解概念核心。
2. 迁移检验：一个具体可答的问题，要求用户把概念迁移到相关领域并举例。
```

检验问题不能写成“你怎么看待这个概念”这类空泛开放题。
