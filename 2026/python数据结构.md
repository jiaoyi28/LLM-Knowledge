
本文整理了**Python 列表最实用、最常用**的操作，包含**创建、增删改查、排序、推导式**等，全部带可直接运行的样例代码，方便快速查阅。
# List
## 一、创建列表

python

运行

```
# 1. 空列表
empty_list = []

# 2. 普通列表（可存任意类型：数字、字符串、布尔、列表等）
my_list = [1, 2, "Python", True, [3, 4]]

# 3. 使用 list() 函数创建
list2 = list("abc")  # 结果：['a', 'b', 'c']
```

## 二、访问 / 修改元素（索引、切片）

### 1. 按索引访问（正索引 / 负索引）

python

运行

```
my_list = ["苹果", "香蕉", "橙子"]

# 正索引：从 0 开始
print(my_list[0])  # 苹果

# 负索引：从末尾 -1 开始
print(my_list[-1])  # 橙子
```

### 2. 切片（截取一段）

python

运行

```
my_list = [0, 1, 2, 3, 4, 5]

# [起始:结束] 不包含结束位置
print(my_list[1:4])  # [1,2,3]

# 从头取到末尾
print(my_list[2:])  # [2,3,4,5]
```

### 3. 修改元素

python

运行

```
my_list = [1, 2, 3]
my_list[0] = 100  # 把第 1 个元素改成 100
print(my_list)  # [100, 2, 3]
```

## 三、添加元素

python

运行

```
my_list = [1, 2]

# 1. 末尾添加一个元素
my_list.append(3)  # [1,2,3]

# 2. 末尾添加多个元素（合并列表）
my_list.extend([4, 5])  # [1,2,3,4,5]

# 3. 指定位置插入元素
my_list.insert(1, "Python")  # 在索引 1 插入
# 结果：[1, 'Python', 2, 3, 4, 5]
```

## 四、删除元素

python

运行

```
my_list = ["a", "b", "c", "d", "b"]

# 1. 根据值删除（删除第一个匹配项）
my_list.remove("b")  # ['a', 'c', 'd', 'b']

# 2. 根据索引删除
del my_list[0]  # 删除索引 0

# 3. 弹出元素（删除并返回该元素）
last = my_list.pop()  # 删除最后一个
my_list.pop(1)  # 删除索引 1

# 4. 清空列表
my_list.clear()  # []
```

## 五、查找与统计

python

运行

```
my_list = [1, 2, 2, 3, 2]

# 1. 获取长度
print(len(my_list))  # 5

# 2. 获取第一个匹配元素的索引
print(my_list.index(2))  # 1

# 3. 统计元素出现次数
print(my_list.count(2))  # 3

# 4. 判断元素是否存在
print(3 in my_list)  # True
```

## 六、排序与反转

python

运行

```
nums = [3, 1, 4, 2]

# 1. 升序排序（直接修改原列表）
nums.sort()  # [1,2,3,4]

# 2. 降序排序
nums.sort(reverse=True)  # [4,3,2,1]

# 3. 反转列表
nums.reverse()  # [2,4,1,3]

# 4. 生成新列表（不修改原列表）
new_nums = sorted(nums)
```

## 七、遍历列表

python

运行

```
my_list = ["苹果", "香蕉", "橙子"]

# 1. 普通遍历
for item in my_list:
    print(item)

# 2. 带索引遍历
for idx, item in enumerate(my_list):
    print(idx, item)
```

## 八、列表推导式（快速生成列表）

python

运行

```
# 生成 0~4 的平方列表
squares = [x**2 for x in range(5)]
print(squares)  # [0,1,4,9,16]

# 带条件筛选
even_squares = [x**2 for x in range(5) if x % 2 == 0]
print(even_squares)  # [0,4,16]
```

## 九、复制列表

python

运行

```
a = [1,2,3]

# 方法 1
b = a.copy()

# 方法 2
b = a[:]
```

---

# String
整理了 Python 字符串**最常用、最实用**的操作，包含**创建、查找、替换、切割、拼接、格式化、判断**等，全部带可直接运行的样例代码，方便快速查阅。

## 一、创建字符串

python

运行

```
# 1. 单引号
s1 = 'hello'

# 2. 双引号
s2 = "python"

# 3. 三引号（多行字符串）
s3 = '''第一行
第二行
第三行'''

# 4. 转义字符 \n 换行 \t 制表
s4 = "hello\nworld"
```

## 二、访问与切片（和 list 用法很像）

python

运行

```
s = "abcdef"

# 1. 按索引取字符
print(s[0])   # a
print(s[-1])  # f

# 2. 切片 [起始:结束:步长]
print(s[1:4])   # bcd
print(s[:3])    # abc
print(s[::2])   # ace（隔一个取一个）
print(s[::-1])  # fedcba（反转字符串）
```

## 三、字符串长度

python

运行

```
s = "hello"
print(len(s))  # 5
```

## 四、查找与判断

python

运行

```
s = "hello python"

# 1. 是否包含子串
print("python" in s)  # True

# 2. 查找子串索引（找不到返回 -1）
print(s.find("python"))  # 6

# 3. 查找子串索引（找不到报错）
print(s.index("python"))  # 6

# 4. 以...开头 / 结尾
print(s.startswith("hello"))  # True
print(s.endswith("python"))   # True
```

## 五、替换

python

运行

```
s = "hello world world"

# 替换所有匹配项
new_s = s.replace("world", "python")
print(new_s)  # hello python python

# 指定替换次数
new_s = s.replace("world", "python", 1)
print(new_s)  # hello python world
```

## 六、切割与拼接

### 1. 切割（字符串 → 列表）

python

运行

```
s = "a,b,c,d"

# 按指定分隔符切割
print(s.split(","))  # ['a', 'b', 'c', 'd']

s2 = "hello world"
print(s2.split())    # ['hello', 'world']（默认按空格切）
```

### 2. 拼接（列表 → 字符串）

python

运行

```
lst = ["a", "b", "c"]

# 用连接符拼接
print("-".join(lst))  # a-b-c
print("".join(lst))   # abc
```

## 七、大小写转换

python

运行

```
s = "Hello Python"

print(s.upper())        # HELLO PYTHON（全大写）
print(s.lower())        # hello python（全小写）
print(s.capitalize())   # Hello python（首字母大写）
print(s.title())        # Hello Python（每个单词首字母大写）
print(s.swapcase())     # hELLO pYTHON（大小写互换）
```

## 八、去除空白

python

运行

```
s = "  hello world  \n"

print(s.strip())   # hello world（去除两边空白）
print(s.lstrip())  # hello world  \n（去除左边）
print(s.rstrip())  #   hello world（去除右边）
```

## 九、判断类型（常用）


```
s1 = "12345"
s2 = "abc123"
s3 = "ABC"

print(s1.isdigit())    # True（是否全数字）
print(s2.isalpha())    # False（是否全字母）
print(s3.isupper())    # True（是否全大写）
print(s2.islower())    # False（是否全小写）
print(s2.isalnum())    # True（是否字母+数字）
```

## 十、格式化输出（最常用）

### 1. f-string（推荐）


```
name = "小明"
age = 20
print(f"我是{name}，今年{age}岁")  # 我是小明，今年20岁
```

### 2. format


```
print("我是{}，今年{}岁".format(name, age))
```

## 十一、常用统计


```
s = "hello hello python"

# 子串出现次数
print(s.count("hello"))  # 2
```

---
# Dict
整理了 Python 字典**最核心、最常用**的操作，包含**创建、增删改查、遍历、获取键值、合并、推导式**等，全部带可直接运行的样例代码，方便快速查阅。

## 一、创建字典


```
# 1. 空字典
empty_dict = {}

# 2. 普通字典（键值对：key: value）
person = {"name": "小明", "age": 20, "city": "北京"}

# 3. 使用 dict() 函数创建
student = dict(name="小红", age=18)

# 查看大小
len(student)
```

## 二、访问 / 修改元素

### 1. 按键访问


```
person = {"name": "小明", "age": 20}

# 方法1：推荐（键不存在会报错）
print(person["name"])  # 小明

# 方法2：安全访问（键不存在返回 None 或默认值）
print(person.get("age"))       # 20
print(person.get("gender", "未知"))  # 未知
```

### 2. 修改 / 添加元素

```
person = {"name": "小明"}

# 修改已有键的值
person["age"] = 21

# 添加新键值对
person["city"] = "上海"

# 结果：{'name': '小明', 'age': 21, 'city': '上海'}
```

## 三、删除元素

```
person = {"name": "小明", "age": 20, "city": "北京"}

# 1. 根据键删除
del person["age"]

# 2. 弹出键值对（删除并返回值）
city = person.pop("city")

# 3. 清空字典
person.clear()
```

## 四、判断键是否存在

```
person = {"name": "小明", "age": 20}

print("name" in person)   # True
print("gender" in person) # False
```

## 五、获取所有键、值、键值对

```
person = {"name": "小明", "age": 20}

# 1. 获取所有键
print(person.keys())    # dict_keys(['name', 'age'])

# 2. 获取所有值
print(person.values())  # dict_values(['小明', 20])

# 3. 获取所有键值对（最常用）
print(person.items())   # dict_items([('name', '小明'), ('age', 20)])
```

## 六、遍历字典

```
person = {"name": "小明", "age": 20, "city": "北京"}

# 1. 遍历键
for key in person:
    print(key)

# 2. 遍历键值对（推荐）
for key, value in person.items():
    print(f"{key}: {value}")
```

## 七、合并字典

```
dict1 = {"a": 1, "b": 2}
dict2 = {"b": 3, "c": 4}

# 方法1：Python 3.5+ 推荐
dict3 = {**dict1, **dict2}  # {'a':1, 'b':3, 'c':4}（后面覆盖前面）

# 方法2：原地更新
dict1.update(dict2)
```

## 八、字典推导式（快速生成）

```
# 生成 {0:0, 1:1, 2:4, 3:9}
squares = {x: x**2 for x in range(4)}
print(squares)

# 带条件筛选
even_squares = {x: x**2 for x in range(4) if x % 2 == 0}
```

## 九、复制字典

```
person = {"name": "小明"}

# 浅复制（推荐）
new_person = person.copy()
```

---

# OrderedDict
`OrderedDict` 是 Python `collections` 模块中的字典子类，**核心特性：保留键值对的插入顺序**（Python 3.7+ 普通 dict 也默认保留顺序，但 OrderedDict 仍有专属优势：支持移动元素、逆序迭代等）。

## 1. 基础导入与创建

```
from collections import OrderedDict

# 1. 空 OrderedDict
od1 = OrderedDict()

# 2. 直接初始化键值对
od2 = OrderedDict([("name", "张三"), ("age", 20), ("gender", "男")])

# 3. 关键字参数初始化
od3 = OrderedDict(name="李四", age=25)

print(od2)
# 输出：OrderedDict([('name', '张三'), ('age', 20), ('gender', '男')])
```

## 2. 增 / 删 / 改 / 查元素（和普通字典一致）

OrderedDict 完全兼容普通字典的操作语法：

```
from collections import OrderedDict

od = OrderedDict(name="张三", age=20)

# 1. 新增元素
od["gender"] = "男"

# 2. 修改元素
od["age"] = 21

# 3. 查找元素（通过键）
print(od["name"])  # 输出：张三
print(od.get("age"))  # 输出：21

# 4. 删除元素
del od["gender"]  # 删除指定键
od.pop("age")     # 弹出指定键
od.popitem(last=True)      # 弹出最后一个插入的键值对
od.popitem(last=False)     # 弹出第一个插入的键值对

print(od)  # 输出：OrderedDict()
```

## 3. 移动元素位置（OrderedDict 独有）

`move_to_end(key, last=True)`：将指定键的元素移动到**末尾**（last=True）或**开头**（last=False），普通字典不支持！

```
from collections import OrderedDict

od = OrderedDict(a=1, b=2, c=3)

# 移动到末尾
od.move_to_end("a")
print(od)  # OrderedDict([('b', 2), ('c', 3), ('a', 1)])

# 移动到开头
od.move_to_end("c", last=False)
print(od)  # OrderedDict([('c', 3), ('b', 2), ('a', 1)])
```

## 4. 逆序迭代（OrderedDict 独有）

使用 `reversed()` 逆序遍历键、值或键值对：

```
from collections import OrderedDict

od = OrderedDict(a=1, b=2, c=3)

# 逆序遍历键
for key in reversed(od):
    print(key, end=" ")  # 输出：c b a

print()

# 逆序遍历键值对
for k, v in reversed(od.items()):
    print(f"{k}:{v}", end=" ")  # 输出：c:3 b:2 a:1
```

## 5. 排序后生成 OrderedDict

手动控制顺序，将普通字典排序后转为 OrderedDict：

```
from collections import OrderedDict

# 普通字典
normal_dict = {"banana": 3, "apple": 1, "orange": 2}

# 按键排序
sorted_od = OrderedDict(sorted(normal_dict.items()))
print(sorted_od)  # OrderedDict([('apple', 1), ('banana', 3), ('orange', 2)])

# 按值排序
sorted_od_by_value = OrderedDict(sorted(normal_dict.items(), key=lambda x: x[1]))
print(sorted_od_by_value)  # OrderedDict([('apple', 1), ('orange', 2), ('banana', 3)])
```

## 6. 与普通字典互转

```
from collections import OrderedDict

# OrderedDict 转 普通字典
od = OrderedDict(a=1, b=2)
normal_dict = dict(od)

# 普通字典 转 OrderedDict
normal_dict = {"x": 10, "y": 20}
od = OrderedDict(normal_dict)
```

## 7. 判等特性（OrderedDict 专属）

OrderedDict **比较时会校验顺序**，顺序不同则不相等；普通字典只比较内容：

```
from collections import OrderedDict

# 普通字典：顺序不同，仍相等
dict1 = {"a":1, "b":2}
dict2 = {"b":2, "a":1}
print(dict1 == dict2)  # True

# OrderedDict：顺序不同，不相等
od1 = OrderedDict(a=1, b=2)
od2 = OrderedDict(b=2, a=1)
print(od1 == od2)  # False
```

## 8. 清空 OrderedDict

```
from collections import OrderedDict

od = OrderedDict(a=1, b=2)
od.clear()
print(od)  # 输出：OrderedDict()
```

---

# range () 函数

### 作用

生成**整数序列**，常用于 `for` 循环控制循环次数、生成连续数字，**不占用大量内存**（惰性生成）。

### 语法

```python
range(stop)                 # 从 0 开始，到 stop-1 结束
range(start, stop)          # 从 start 开始，到 stop-1 结束
range(start, stop, step)    # 从 start 开始，步长 step，到 stop-1 结束
```

### 常用用法 + 样例代码

#### 1. 基础用法：从 0 开始循环

```python
# 循环 5 次：0,1,2,3,4
for i in range(5):
    print(i, end=" ")  # 输出：0 1 2 3 4
```

#### 2. 指定起始值 + 结束值

```python
# 从 2 开始，到 6 结束（不包含 6）
for i in range(2, 6):
    print(i, end=" ")  # 输出：2 3 4 5
```

#### 3. 指定步长（间隔）

```python
# 从 1 开始，到 10 结束，步长 2（奇数）
for i in range(1, 10, 2):
    print(i, end=" ")  # 输出：1 3 5 7 9

# 步长为负数：倒序生成
for i in range(5, 0, -1):
    print(i, end=" ")  # 输出：5 4 3 2 1
```

#### 4. 配合 list () 生成数字列表

python

运行

```
# 把 range 转为列表
nums = list(range(1, 6))
print(nums)  # 输出：[1, 2, 3, 4, 5]
```

#### 5. 控制循环次数（不使用循环变量）

python

运行

```
# 只需要执行 3 次操作，不需要 i
for _ in range(3):
    print("执行操作")
```

---

# enumerate () 函数

### 作用

**遍历可迭代对象（列表 / 字符串 / 元组）时，同时获取 索引 + 元素值**，替代手动维护索引变量。

### 语法

python

运行

```
enumerate(iterable, start=0)
# iterable：列表、字符串、元组等可迭代对象
# start：索引起始值（默认 0，可自定义）
```

### 常用用法 + 样例代码

#### 1. 基础用法：默认索引从 0 开始

python

运行

```
fruits = ["苹果", "香蕉", "橙子"]

# 同时获取 索引、元素
for idx, fruit in enumerate(fruits):
    print(f"索引：{idx}，元素：{fruit}")
```

**输出**：

plaintext

```
索引：0，元素：苹果
索引：1，元素：香蕉
索引：2，元素：橙子
```

#### 2. 自定义索引起始值（高频实用）

python

运行

```
fruits = ["苹果", "香蕉", "橙子"]

# 索引从 1 开始（适合展示序号）
for idx, fruit in enumerate(fruits, start=1):
    print(f"第{idx}名：{fruit}")
```

**输出**：

plaintext

```
第1名：苹果
第2名：香蕉
第3名：橙子
```

#### 3. 遍历字符串（索引 + 字符）

python

运行

```
s = "Python"
for idx, char in enumerate(s):
    print(f"索引{idx}：{char}")
```

#### 4. 转换为列表（查看索引 + 元素结构）

python

运行

```
fruits = ["苹果", "香蕉"]
res = list(enumerate(fruits))
print(res)  # 输出：[(0, '苹果'), (1, '香蕉')]
```

#### 5. 配合 range () 实现带索引的数字循环

python

运行

```
# 循环数字，同时获取索引
for idx, num in enumerate(range(10, 13)):
    print(f"索引：{idx}，数字：{num}")
# 输出：
# 索引：0，数字：10
# 索引：1，数字：11
# 索引：2，数字：12
```

---

## 三、核心区别总结