## 一、什么是 Agent 设计模式

Agent 设计模式，是指让大模型按照某种固定工作流完成任务的方法。  
它解决的核心问题通常有三个：

1. **怎么组织任务**
   - 先规划再执行
   - 边做边想边调整

2. **怎么提高结果质量**
   - 做完后自我检查
   - 多试几次再选更稳的结果
   - 同时探索多条思路

3. **怎么扩展能力**
   - 调工具
   - 接知识库
   - 多角色协作

---

## 二、最常见的几种模式

### 1. ReAct

**全称**：Reason + Act  
**核心思想**：边推理，边行动，边根据结果调整下一步。

### 基本流程
1. 思考下一步做什么
2. 调用工具或执行动作
3. 观察结果
4. 继续下一轮判断与行动

### 特点
- 很灵活
- 适合动态环境
- 擅长工具调用和多跳查询

### 典型场景
- 搜索信息
- 调 API
- 多步问答
- 环境探索

### 一句话理解
> ReAct 就是“边做边想”。

---

### 2. Plan-and-Execute

**核心思想**：先把任务拆成计划，再逐步执行。

### 基本流程
1. 理解目标
2. 生成计划
3. 拆分子任务
4. 按顺序执行
5. 汇总结果

### 特点
- 全局性更强
- 适合长流程任务
- 可控性较高

### 典型场景
- 写报告
- 做竞品分析
- 项目型工作流
- 多步骤自动化任务

### 一句话理解
> Plan-and-Execute 就是“先想清楚路线，再出发”。

---

### 3. Reflection

**核心思想**：先生成结果，再检查，再修正。

### 基本流程
1. 产出第一版
2. 检查错误、遗漏、逻辑问题
3. 修改答案
4. 必要时继续迭代

### 特点
- 提高正确率和完整性
- 对代码、分析、写作很有效
- 成本比单次生成更高

### 典型场景
- 代码生成
- 数学与逻辑推理
- 高质量文案
- 分析报告

### 一句话理解
> Reflection 就是“先做，再审，再改”。

---

### 4. Self-Consistency

**核心思想**：对同一问题生成多份独立答案，再选更一致的结果。

### 特点
- 能降低偶然错误
- 适合明确答案的问题
- 比较耗资源

### 典型场景
- 数学题
- 逻辑题
- 标准答案型推理任务

### 一句话理解
> Self-Consistency 就是“多做几次，选更稳的”。

---

### 5. Tree of Thoughts

**核心思想**：把推理过程看成一棵搜索树，同时探索多条思路。

### 特点
- 会尝试多条路径
- 会对路径做评估和剪枝
- 更适合复杂规划问题

### 典型场景
- 复杂决策
- 多约束规划
- 搜索类问题

### 一句话理解
> Tree of Thoughts 就是“不只走一条路，而是边探索边筛选”。

---

### 6. Multi-Agent

**核心思想**：多个 Agent 分工合作。

### 常见角色
- Planner：负责规划
- Researcher：负责搜集信息
- Executor：负责执行
- Critic：负责检查
- Writer：负责整理输出

### 特点
- 分工清晰
- 适合复杂任务
- 协调成本较高

### 典型场景
- 大型研究任务
- 长流程业务任务
- 多角色协作系统

### 一句话理解
> Multi-Agent 就是“把一个复杂任务交给多个角色配合完成”。

---

### 7. Tool-Using Agent

**核心思想**：重点不是推理流程，而是可靠地调用外部工具。

### 常见工具
- 搜索
- 数据库
- 浏览器
- 代码执行器
- 邮件、日历、业务系统 API

### 特点
- 实用性强
- 能连接真实世界系统
- 工程要求高

### 一句话理解
> Tool-Using Agent 的重点是“会正确用工具”。

---

### 8. Retrieval-Augmented Agent

**核心思想**：先检索知识，再结合检索结果继续推理与行动。

### 和普通 RAG 的区别
- 普通 RAG：通常检索一次后回答
- Retrieval-Augmented Agent：可能多轮检索、改写查询、比较来源

### 典型场景
- 企业知识库问答
- 文档分析
- 法务、金融、科研辅助

### 一句话理解
> Retrieval-Augmented Agent 就是“先补知识，再做判断”。

---

## 三、最容易混淆的几组模式对比

### 1. ReAct vs Plan-and-Execute

#### 相同点
- 都解决多步任务
- 都可以配合工具使用

#### 不同点
**ReAct**
- 边做边想
- 每一步根据当前结果临场决定
- 更灵活

**Plan-and-Execute**
- 先规划再执行
- 更强调全局结构
- 更适合长流程

#### 记忆方法
- ReAct：边走边看
- Plan-and-Execute：先看路线图再走

---

### 2. Reflection vs Self-Consistency

#### 相同点
- 都是为了提升答案质量
- 都不是只生成一次就结束

#### 不同点
**Reflection**
- 针对同一份答案做检查和修正
- 属于“改答案”

**Self-Consistency**
- 独立生成多份答案再比较
- 属于“选答案”

#### 记忆方法
- Reflection：审稿
- Self-Consistency：投票

---

### 3. Self-Consistency vs Tree of Thoughts

#### 相同点
- 都不只走一条推理路径

#### 不同点
**Self-Consistency**
- 多条路径彼此独立
- 看最终答案的一致性

**Tree of Thoughts**
- 多条路径会继续展开
- 中途会评估、保留、剪枝

#### 记忆方法
- Self-Consistency：多做几次看谁更一致
- Tree of Thoughts：把思路当成搜索树来筛选

---

### 4. Reflection vs Critic Agent

#### 相同点
- 都负责检查问题和挑错

#### 不同点
**Reflection**
- 自己检查自己
- 属于单 Agent 内部迭代

**Critic Agent**
- 单独分出一个评审角色
- 属于多 Agent 协作

#### 记忆方法
- Reflection：自我复盘
- Critic Agent：别人审你

---

### 5. Retrieval-Augmented Agent vs 普通 RAG

#### 相同点
- 都依赖外部知识检索

#### 不同点
**普通 RAG**
- 一次检索，一次回答

**Retrieval-Augmented Agent**
- 可多轮检索
- 可继续行动
- 可根据中间结果改写查询

#### 记忆方法
- 普通 RAG：查一次资料就回答
- Retrieval-Augmented Agent：边查边补边判断

---

## 四、这些模式常怎么组合

### 1. Plan-and-Execute + ReAct
先做全局规划，再让每个子任务用 ReAct 完成。

**适合**：长流程、每一步又需要灵活探索的任务。

---

### 2. ReAct + Reflection
先边查边做，再进行结果审查和修正。

**适合**：写作、研究、代码生成。

---

### 3. Planner + Executor + Critic
把规划、执行、评审拆成不同角色。

**本质上**：就是多 Agent 版的  
**Plan-and-Execute + Reflection**

---

### 4. Retrieval + ReAct
先检索，再行动；信息不足时继续检索。

**适合**：知识密集型 Agent。

---

## 五、如何选择设计模式

### 任务短、环境动态、需要频繁查工具
优先选：
- **ReAct**
- **Tool-Using Agent**

---

### 任务长、步骤明确、需要拆解
优先选：
- **Plan-and-Execute**

---

### 对准确性要求高
在原有模式上加：
- **Reflection**

---

### 推理难、答案明确、希望更稳
考虑：
- **Self-Consistency**

---

### 需要探索多个方案或复杂路径
考虑：
- **Tree of Thoughts**

---

### 任务天然适合分工
考虑：
- **Multi-Agent**

---

### 问题主要卡在知识不足
加入：
- **Retrieval-Augmented Agent**

---

## 六、学习时最该记住的框架

可以把这些模式分成三大类来记：

### 1. 任务组织类
- ReAct
- Plan-and-Execute

### 2. 结果优化类
- Reflection
- Self-Consistency
- Tree of Thoughts

### 3. 能力扩展类
- Tool-Using Agent
- Retrieval-Augmented Agent
- Multi-Agent

---

## 七、最实用的工程起点

如果是从零开始搭 Agent，最常见、最实用的起点是：

### 推荐起步方案
**ReAct + Tool Calling + Reflection**

### 原因
- 足够灵活
- 容易落地
- 工程复杂度适中
- 效果通常已经不错

等任务变复杂后，再逐步加入：
- Plan-and-Execute
- Retrieval
- Memory
- Multi-Agent

---

## 九、一张总表

| 模式 | 核心问题 | 关键词 | 最适合的场景 |
|---|---|---|---|
| ReAct | 如何边行动边调整 | 边做边想 | 动态任务、工具调用 |
| Plan-and-Execute | 如何组织长任务 | 先规划后执行 | 长流程任务 |
| Reflection | 如何修正已有结果 | 审查与修正 | 高质量输出 |
| Self-Consistency | 如何提高稳定性 | 多次采样 | 数学、逻辑题 |
| Tree of Thoughts | 如何探索多种方案 | 搜索树 | 规划、决策 |
| Multi-Agent | 如何分工协作 | 多角色 | 复杂系统任务 |
| Tool-Using Agent | 如何连接外部系统 | 工具调用 | 自动化、系统集成 |
| Retrieval-Augmented Agent | 如何补充知识 | 检索增强 | 知识密集任务 |
