---
slug: english-reading-exercise
title: 使用slambda把任意文章变成英语阅读练习
authors:
  - haowu4
tags: [slambda, use-case]
---

# 使用slambda把任意文章变成英语阅读练习

阅读理解类题目是英语考试中经常出现的题型，但是有时因为文章实在过于无聊或者自己不感兴趣，降低了自己练习阅读理解的积极性。

如果我们能把每天读的新闻，或者自己感兴趣的文章变成阅读理解题目，可能能让学英语的过程更加轻松有趣。

直接使用大语言模型，比如chatgpt生成英语练习题目，在我们的实验中，虽然可以生成出看起来格式正确的回复，但是生成出的题目选项经常出现多个答案均为正确答案。

这时我们可以考虑将生成阅读理解题目这一过程分解成更简单的一系列子任务， 再通过程序把这些子任务组合起来。这种情况下，`slambda`可以非常方便的让你把这些子任务定义成可以直接使用的python函数。

比如我们在进行了一些小实验后有了如下的观察：
1. 当给定一篇文章后，语言模型能够比较可靠的生成问题
2. 当给定一篇文章后和一个问题后，语言模型能够比较准确的回答问题
2. 当给定一篇文章后和一个问题后，语言模型能够比较可靠的生成错误选项。

有了这些观察，我们就可以开始写一套完整的流程来生成阅读理解题目了。

## 定义数据结构

首先，我们使用`pydantic`定义我们所需要的数据结构：

```python
from pydantic import BaseModel, Field

class ReadingExeceriseQuestion(BaseModel):
    question: str
    correct_answer: str = ''
    wrong_answers: list[str] = Field(default_factory=list)

class ReadingExecerise(BaseModel):
    content: str = ''
    questions: list[ReadingExeceriseQuestion] = Field(default_factory=list)
```

## 分解问题

然后让我们写下来生成阅读理解的大体流程：

```python
def create_reading_execerise(reading_content):
    e = ReadingExecerise(content=reading_content)
    questions = create_questions(reading_content)
    for question in questions:
        q = ReadingExeceriseQuestion(question=question)
        correct_answer = create_answer(content=reading_content, question=question)
        q.correct_answer = correct_answer
        wrong_answers = create_wrong_answers(content=reading_content, question=question)
        for wrong_answer in wrong_answers:
            q.wrong_answers.append(wrong_answer)
        e.questions.append(q)
    return e

```

在上面的代码中，我们首先针对文章生成生成几个阅读理解问题的题干，但是不要求语言模型给出问题的答案。然后再单独针对每个问题分别生成正确答案和错误答案。

## 定义slambda函数

为了让上面的函数可以真的被执行并返回我们想要的信息，我们还需要定义下面几个函数
* `create_questions(content)`: 对给定文章生成n个阅读理解问题
* `create_answer(content, question)`: 对给定文章和问题，给出正确答案
* `create_wrong_answers(question)`: 对给定文章和问题，给出3个错误选项

有了语言模型和slambda，实现上面这些函数就很简单了, 我们只需要给出自然语言指令和一些输入输出例子，slambda可以直接通过这两个信息创建一个python函数。

```python
from slambda import Example, LmFunction, GptApiOptions

create_questions = LmFunction.create(
    instruction="Create 5 toefl reading questions for given article, return in json array format",
    examples=[
        Example(
            input="""
Starting in July, the Test of English as a Foreign Language (TOEFL) will be reduced by one hour, becoming a two-hour exam. This change is aimed at increasing the competitiveness of TOEFL, which has faced competition from Duolingo, a language testing provider with a one-hour test. While many colleges have adopted test-optional policies for admissions, they still require English proficiency tests for non-native English speakers. The change will not affect the shorter TOEFL Essentials Test introduced in 2021 and will not impact the pricing of the longer TOEFL iBT exam. TOEFL representatives argue that their test remains superior to Duolingo's.
Specific changes to the new TOEFL iBT include a shorter reading section, a more concise writing task, and the removal of unscored test questions. Duolingo, however, remains confident in its own approach and widespread acceptance among U.S. colleges. TOEFL's executive director reports growing test volumes in recent years, particularly in key markets like China and India, emphasizing their commitment to innovation and maintaining high standards of validity, reliability, security, and fairness.            
            """,
            output=[
"What is the primary reason for the reduction in the duration of the TOEFL exam?",
"How long will the TOEFL exam be after the reduction in July?",
"Which language testing provider has posed competition to TOEFL with a one-hour test?",
"Why do colleges with test-optional policies still require English proficiency tests for non-native English speakers?",
"What is the TOEFL Essentials Test, and how is it related to the TOEFL iBT exam?",
            ],
        )
    ]
)


create_answer = LmFunction.create(
    instruction="Answer the question base on the given article",
    examples=[
        Example(
            input={
                'content': """
Starting in July, the Test of English as a Foreign Language (TOEFL) will be reduced by one hour, becoming a two-hour exam. This change is aimed at increasing the competitiveness of TOEFL, which has faced competition from Duolingo, a language testing provider with a one-hour test. While many colleges have adopted test-optional policies for admissions, they still require English proficiency tests for non-native English speakers. The change will not affect the shorter TOEFL Essentials Test introduced in 2021 and will not impact the pricing of the longer TOEFL iBT exam. TOEFL representatives argue that their test remains superior to Duolingo's.
Specific changes to the new TOEFL iBT include a shorter reading section, a more concise writing task, and the removal of unscored test questions. Duolingo, however, remains confident in its own approach and widespread acceptance among U.S. colleges. TOEFL's executive director reports growing test volumes in recent years, particularly in key markets like China and India, emphasizing their commitment to innovation and maintaining high standards of validity, reliability, security, and fairness.                
                """.strip(),
                'question': 'How long will the TOEFL exam be after the reduction in July?'
            },
            output='After the reduction in July, the TOEFL exam will be two hours long.',
        )
    ]
)

create_wrong_answers = LmFunction.create(
    instruction="Give 3 wrong answers for the question base on the given article, in json array format",
    examples=[
        Example(
            input={
                'content': """
Starting in July, the Test of English as a Foreign Language (TOEFL) will be reduced by one hour, becoming a two-hour exam. This change is aimed at increasing the competitiveness of TOEFL, which has faced competition from Duolingo, a language testing provider with a one-hour test. While many colleges have adopted test-optional policies for admissions, they still require English proficiency tests for non-native English speakers. The change will not affect the shorter TOEFL Essentials Test introduced in 2021 and will not impact the pricing of the longer TOEFL iBT exam. TOEFL representatives argue that their test remains superior to Duolingo's.
Specific changes to the new TOEFL iBT include a shorter reading section, a more concise writing task, and the removal of unscored test questions. Duolingo, however, remains confident in its own approach and widespread acceptance among U.S. colleges. TOEFL's executive director reports growing test volumes in recent years, particularly in key markets like China and India, emphasizing their commitment to innovation and maintaining high standards of validity, reliability, security, and fairness.                
                """.strip(),
                'question': 'How long will the TOEFL exam be after the reduction in July?'
            },
            output=[
                'After the reduction in July, the TOEFL exam will be 24 hours long.',
                'The TOEFL exam will become a 30-minute test after the reduction in July.',
                'TOEFL exam duration will increase to 5 hours after the reduction in July.',
            ],
        )
    ]
)
```

在上面的例子中，`create_questions` 和 `create_wrong_answers`返回的都是一个`list[str]`，`create_answer`返回的是单个`str`。

## 生成可打印的PDF

加上上面的三个slambda函数之后， 之前写好的`create_reading_execerise`函数可以返回一个我们定义的`ReadingExecerise`实例。但是这个格式对普通英语学习者非常不友好，所以我们想把这个内容渲染到PDF，变成一个可打印的阅读练习。这里我们可以通过生成markdown文档，再使用pandoc生成pdf。

我们可以使用如下代码生成markdown。

```python
from random import shuffle

def shuffle_options(correct_option, wrong_options):
    l = [*wrong_options, correct_option]
    shuffle(l)
    return l, l.index(correct_option)
    
def question_to_markdown(q):
    ([oa, ob, oc, od], ans_idx) = shuffle_options(q.correct_answer, q.wrong_answers)
    ans_key = chr(ord('A') + ans_idx)
    return f"""
{q.question}

[ ] A. {oa}

[ ] B. {ob}

[ ] C. {oc}

[ ] D. {od}

    """.strip(), ans_key


def execerise_to_markdown(e):
    
    questions_and_key = [question_to_markdown(x) for x in e.questions]
    questions = ''
    answers = '# Ansers:\n\n'
    content = '\n\n'.join(e.content.split('\n'))
    for i, (q, k) in enumerate(questions_and_key):
        questions += f"## Question {i + 1 }\n\n"
        questions += q
        questions += '\n\n\n'
        
        answers += f"* Question {i + 1 :<2} : {k}\n\n"        
    
    main = f"""
# Article

{content}


# Questions

{questions}
    """.strip()
    
    
    return main + "\n\pagebreak\n" + answers
```

当有了Markdown文件后，我们可以使用开源工具[Pandoc](https://pandoc.org/)把markdown渲染成pdf， 以方便我们阅读或者打印。您可以参考[Pandoc官网](https://pandoc.org/)来安装pandoc。

Pandoc的使用方式如下。
```bash
pandoc name.md  -o name.pdf
```

## 完整代码

```python
import os
import openai

from dotenv import load_dotenv
from slambda import Example, LmFunction, GptApiOptions
from pydantic import BaseModel, Field
from random import shuffle

# 该文件包含了OpenAI API KEY，
load_dotenv(dotenv_path=os.path.expanduser('.env.local'))

# 通过环境变量读取 OPENAI_API_KEY
openai.api_key = os.getenv('OPENAI_API_KEY')

if openai.api_key is None:
    print("您需要载入OPENAI_API_KEY")
    raise ValueError('找不到OPENAI_API_KEY')

# 定义数据结构
class ReadingExeceriseQuestion(BaseModel):
    question: str
    correct_answer: str = ''
    wrong_answers: list[str] = Field(default_factory=list)

class ReadingExecerise(BaseModel):
    content: str = ''
    questions: list[ReadingExeceriseQuestion] = Field(default_factory=list)


# 定义slambda函数

create_questions = LmFunction.create(
    instruction="Create 5 toefl reading questions for given article, return in json array format",
    examples=[
        Example(
            input="""
Starting in July, the Test of English as a Foreign Language (TOEFL) will be reduced by one hour, becoming a two-hour exam. This change is aimed at increasing the competitiveness of TOEFL, which has faced competition from Duolingo, a language testing provider with a one-hour test. While many colleges have adopted test-optional policies for admissions, they still require English proficiency tests for non-native English speakers. The change will not affect the shorter TOEFL Essentials Test introduced in 2021 and will not impact the pricing of the longer TOEFL iBT exam. TOEFL representatives argue that their test remains superior to Duolingo's.
Specific changes to the new TOEFL iBT include a shorter reading section, a more concise writing task, and the removal of unscored test questions. Duolingo, however, remains confident in its own approach and widespread acceptance among U.S. colleges. TOEFL's executive director reports growing test volumes in recent years, particularly in key markets like China and India, emphasizing their commitment to innovation and maintaining high standards of validity, reliability, security, and fairness.            
            """,
            output=[
"What is the primary reason for the reduction in the duration of the TOEFL exam?",
"How long will the TOEFL exam be after the reduction in July?",
"Which language testing provider has posed competition to TOEFL with a one-hour test?",
"Why do colleges with test-optional policies still require English proficiency tests for non-native English speakers?",
"What is the TOEFL Essentials Test, and how is it related to the TOEFL iBT exam?",
            ],
        )
    ]
)


create_answer = LmFunction.create(
    instruction="Answer the question base on the given article",
    examples=[
        Example(
            input={
                'content': """
Starting in July, the Test of English as a Foreign Language (TOEFL) will be reduced by one hour, becoming a two-hour exam. This change is aimed at increasing the competitiveness of TOEFL, which has faced competition from Duolingo, a language testing provider with a one-hour test. While many colleges have adopted test-optional policies for admissions, they still require English proficiency tests for non-native English speakers. The change will not affect the shorter TOEFL Essentials Test introduced in 2021 and will not impact the pricing of the longer TOEFL iBT exam. TOEFL representatives argue that their test remains superior to Duolingo's.
Specific changes to the new TOEFL iBT include a shorter reading section, a more concise writing task, and the removal of unscored test questions. Duolingo, however, remains confident in its own approach and widespread acceptance among U.S. colleges. TOEFL's executive director reports growing test volumes in recent years, particularly in key markets like China and India, emphasizing their commitment to innovation and maintaining high standards of validity, reliability, security, and fairness.                
                """.strip(),
                'question': 'How long will the TOEFL exam be after the reduction in July?'
            },
            output='After the reduction in July, the TOEFL exam will be two hours long.',
        )
    ]
)

create_wrong_answers = LmFunction.create(
    instruction="Give 3 wrong answers for the question base on the given article, in json array format",
    examples=[
        Example(
            input={
                'content': """
Starting in July, the Test of English as a Foreign Language (TOEFL) will be reduced by one hour, becoming a two-hour exam. This change is aimed at increasing the competitiveness of TOEFL, which has faced competition from Duolingo, a language testing provider with a one-hour test. While many colleges have adopted test-optional policies for admissions, they still require English proficiency tests for non-native English speakers. The change will not affect the shorter TOEFL Essentials Test introduced in 2021 and will not impact the pricing of the longer TOEFL iBT exam. TOEFL representatives argue that their test remains superior to Duolingo's.
Specific changes to the new TOEFL iBT include a shorter reading section, a more concise writing task, and the removal of unscored test questions. Duolingo, however, remains confident in its own approach and widespread acceptance among U.S. colleges. TOEFL's executive director reports growing test volumes in recent years, particularly in key markets like China and India, emphasizing their commitment to innovation and maintaining high standards of validity, reliability, security, and fairness.                
                """.strip(),
                'question': 'How long will the TOEFL exam be after the reduction in July?'
            },
            output=[
                'After the reduction in July, the TOEFL exam will be 24 hours long.',
                'The TOEFL exam will become a 30-minute test after the reduction in July.',
                'TOEFL exam duration will increase to 5 hours after the reduction in July.',
            ],
        )
    ]
)


# 生成题目和选项
def create_reading_execerise(reading_content):
    e = ReadingExecerise(content=reading_content)
    questions = create_questions(reading_content)
    for question in questions:
        q = ReadingExeceriseQuestion(question=question)
        correct_answer = create_answer(content=reading_content, question=question)
        q.correct_answer = correct_answer
        wrong_answers = create_wrong_answers(content=reading_content, question=question)
        for wrong_answer in wrong_answers:
            q.wrong_answers.append(wrong_answer)
        e.questions.append(q)
    return e


# 生成Markdown相关函数

def shuffle_options(correct_option, wrong_options):
    l = [*wrong_options, correct_option]
    shuffle(l)
    return l, l.index(correct_option)

def question_to_markdown(q):
    ([oa, ob, oc, od], ans_idx) = shuffle_options(q.correct_answer, q.wrong_answers)
    ans_key = chr(ord('A') + ans_idx)
    return f"""
{q.question}

[ ] A. {oa}

[ ] B. {ob}

[ ] C. {oc}

[ ] D. {od}

    """.strip(), ans_key


def execerise_to_markdown(e):
    
    questions_and_key = [question_to_markdown(x) for x in e.questions]
    questions = ''
    answers = '# Ansers:\n\n'
    content = '\n\n'.join(e.content.split('\n'))
    for i, (q, k) in enumerate(questions_and_key):
        questions += f"## Question {i + 1 }\n\n"
        questions += q
        questions += '\n\n\n'
        
        answers += f"* Question {i + 1 :<2} : {k}\n\n"        
    
    main = f"""
# Article

{content}

# Questions

{questions}
    """.strip()

    return main + "\n\pagebreak\n" + answers




# 函数定义完了，让我们来测试一下

article = """
As house prices have climbed, saving for a down payment is out of reach for many Canadians, particularly young people. Today, the Honourable Marc Miller, Minister of Immigration, Refugees and Citizenship, shared how the new tax-free First Home Savings Account is available and helping put home ownership back within reach of Canadians across the country.
The new tax-free First Home Savings Account is a registered savings account that helps Canadians become first-time home buyers by contributing up to $8,000 per year (up to a lifetime limit of $40,000) for their first down payment within 15 years. To help Canadians reach their savings goals, First Home Savings Account contributions are tax deductible on annual income tax returns, like a Registered Retirement Savings Plan (RRSP). Like a Tax‑Free Savings Account, withdrawals to purchase a first home, including any investment income on contributions, are non-taxable. Tax-free in; tax-free out.
Financial institutions have been offering the First Home Savings Account to Canadians since April 1, 2023, and it’s now available at 7 financial institutions, with more set to offer it soon.
""".strip()

# 生成阅读练习
response = create_reading_execerise(article)

# 转换成Markdown， 并写入`./output.md`
md_output = execerise_to_markdown(response)

with open('./output.md', 'w') as out:
    out.write(md_output)
```

现在我们可以回到命令行，执行以上代码，然后使用pandoc把刚刚生成的markdown文件转换成pdf格式。

```bash
pandoc output.md  -o output.pdf
```

现在你就可以打印`output.pdf`，开始你的英语练习了。