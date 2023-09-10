---
slug: english-reading-exercise
title: 使用slambda把任意文章变成英语阅读练习
authors:
  - haowu4
tags: [slambda, use-case]
---

:::tip
你可以通过点击此按钮在这个指南中启用代码自动换好功能来查看过长的代码行数。
![Code Block Warp Button](/img/code-block-wrap-button.png)
:::

# 使用slambda把任意文章变成英语阅读练习

阅读理解类题目是英语考试中经常出现的题型，但是我们非常容易因为文章实在过于无聊或者自己不感兴趣，降低了自己练习阅读理解的积极性。

如果我们能把每天读的新闻，或者自己感兴趣的文章变成阅读理解题目，可能能让学英语的过程更加轻松有趣。

我们可以直接使用大语言模型，比如chatgpt来生成英语练习题。在我们的实验中，虽然生成出来的内容一眼望去非常不错，但是仔细观察观察还是能看到一些小错误， 比如格式不统一，或者单选题中可能可能包含多个正确答案。

这时我们可以考虑将生成阅读理解题目这一过程分解成一系列更简单的子任务， 再通过程序把这些子任务组合起来。这种情况下，`slambda`可以非常方便的让你把这些子任务定义成可以直接使用的python函数。

比如我们在进行了一些小实验后有了如下的观察：
1. 当给定一篇文章后，语言模型能够比较可靠的生成问题
2. 当给定一篇文章后和一个问题后，语言模型能够比较准确的回答问题
2. 当给定一篇文章后和一个问题后，语言模型能够比较可靠的生成错误选项。

有了这些观察，我们就可以开始写一套完整的流程来生成阅读理解题目了。

## 定义数据结构

首先，我们使用`pydantic`定义我们所需要的数据结构：

```python
from pydantic import BaseModel, Field

class ReadingExerciseQuestion(BaseModel):
    question: str
    correct_answer: str = ''
    wrong_answers: list[str] = Field(default_factory=list)

class ReadingExercise(BaseModel):
    content: str = ''
    questions: list[ReadingExerciseQuestion] = Field(default_factory=list)
```

## 分解问题

然后让我们写下来生成阅读理解的大体流程：

```python
def create_reading_exercise(reading_content):
    e = ReadingExercise(content=reading_content)
    questions = create_questions(reading_content)
    for question in questions:
        q = ReadingExerciseQuestion(question=question)
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

为了让上面的函数可以真的被执行并返回我们想要的信息，我们还需要定义下面几个函数：
* `create_questions(content)`: 对给定文章生成n个阅读理解问题
* `create_answer(content, question)`: 对给定文章和问题，给出正确答案
* `create_wrong_answers(question)`: 对给定文章和问题，给出3个错误选项

有了语言模型和slambda，实现上面这些函数就很简单了, 我们只需要给出自然语言指令和一些输入输出例子，slambda可以直接通过这两个信息创建一个python函数。


<details><summary>您需要Openai API key才能使用slambda
</summary>

关于如何加载Openai API key，可以阅读我们的<a href="/zh/docs/tips/apikey" target="_blank">相关文档</a>

```python title="加载Openai API key"
import os
import openai
from dotenv import load_dotenv
# 该文件包含了OpenAI API KEY
load_dotenv(dotenv_path='.env.local')

# 通过环境变量读取 OPENAI_API_KEY
openai.api_key = os.getenv('OPENAI_API_KEY')

```

</details>


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
    instruction="Answer the question base on the given articl in one sentence",
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


def create_reading_exercise(reading_content):
    e = ReadingExercise(content=reading_content)
    questions = create_questions(reading_content)
    for question in questions:
        q = ReadingExerciseQuestion(question=question)
        correct_answer = create_answer(content=reading_content, question=question)
        q.correct_answer = correct_answer
        wrong_answers = create_wrong_answers(content=reading_content, question=question)
        for wrong_answer in wrong_answers:
            q.wrong_answers.append(wrong_answer)
        e.questions.append(q)
    return e

```

在上面的例子中，`create_questions` 和 `create_wrong_answers`返回的都是一个`list[str]`，`create_answer`返回的是单个`str`。

我们现在把复制一篇维基百科文章的一部分来试一试，比如[这篇文章](https://en.wikipedia.org/wiki/Large_language_model)

```python
article = """
A large language model (LLM) is a language model characterized by its large size. Their size is enabled by AI accelerators, which are able to process vast amounts of text data, mostly scraped from the Internet. The artificial neural networks which are built can contain from tens of millions and up to billions of weights and are (pre-)trained using self-supervised learning and semi-supervised learning. Transformer architecture contributed to faster training. Alternative architectures include the mixture of experts (MoE), which has been proposed by Google, starting with sparsely-gated ones in 2017, Gshard in 2021 to GLaM in 2022.
As language models, they work by taking an input text and repeatedly predicting the next token or word. Up to 2020, fine tuning was the only way a model could be adapted to be able to accomplish specific tasks. Larger sized models, such as GPT-3, however, can be prompt-engineered to achieve similar results. They are thought to acquire embodied knowledge about syntax, semantics and "ontology" inherent in human language corpora, but also inaccuracies and biases present in the corpora.
""".strip()

exercise = create_reading_exercise(article)
print(exercise)
```




## 生成可打印的Word文档

加上上面的三个slambda函数之后， 之前写好的`create_reading_exercise`函数可以返回一个我们定义的`ReadingExercise`实例。这个格式虽然在python里面非常方便，但开发者以外的的普通英语学习者使用起来会非常不方便。所以我们想把这个内容渲染到一个Word文档，变成一个可打印的阅读练习。这里我们可以另外一个开源库[python-docx](https://python-docx.readthedocs.io/en/latest/#user-guide)。

我们可以使用如下代码生成word文档。

```python
from docx import Document
from docx.shared import Inches
from random import shuffle

def shuffle_options(correct_option, wrong_options):
    l = [*wrong_options, correct_option]
    shuffle(l)
    return l, l.index(correct_option)

def generate_worddoc(exercise):
    document = Document()
    
    document.add_heading('文章', level=1)

    document.add_paragraph('')

    for p in exercise.content.split('\n'):
        p = document.add_paragraph(p)
    
    document.add_heading('问题', level=1)
    
    ans = []
    
    for qid, question in enumerate(exercise.questions):
        document.add_paragraph(f'Question {qid + 1}:')
        document.add_paragraph(f'{question.question}')

        (options, ans_idx) = shuffle_options(question.correct_answer, question.wrong_answers)

        ans_key = chr(ord('A') + ans_idx)
        ans.append(ans_key)
        
        for i, op in enumerate(options):
            op_key = chr(ord('A') + i)
            document.add_paragraph(f'    {op_key}. {op}')
        document.add_paragraph('')


    document.add_page_break()
    document.add_heading('答案', level=1)

    for qid, ans_key in enumerate(ans):
        document.add_paragraph(f'Question {qid + 1}: {ans_key}')
        
    document.save('./output.docx')
    print(f'Exercise has been saved to {os.path.abspath("./output.docx")}')

generate_worddoc(exercise)
```
现在你就可以打印`output.docx`，开始你的英语练习了。

## 完整代码

### 依赖库

```bash
pip install slambda python-docx openai pydantic python-dotenv
```
### 代码

```python
import os
import openai

from docx import Document
from docx.shared import Inches
from dotenv import load_dotenv
from slambda import Example, LmFunction, GptApiOptions
from pydantic import BaseModel, Field
from random import shuffle

# 该文件包含了OpenAI API KEY，
load_dotenv(dotenv_path='.env.local')

# 通过环境变量读取 OPENAI_API_KEY
openai.api_key = os.getenv('OPENAI_API_KEY')

if openai.api_key is None:
    print("您需要载入OPENAI_API_KEY")
    raise ValueError('找不到OPENAI_API_KEY')

# 定义数据结构
class ReadingExerciseQuestion(BaseModel):
    question: str
    correct_answer: str = ''
    wrong_answers: list[str] = Field(default_factory=list)

class ReadingExercise(BaseModel):
    content: str = ''
    questions: list[ReadingExerciseQuestion] = Field(default_factory=list)


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
    instruction="Answer the question base on the given article in one sentence",
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
def create_reading_exercise(reading_content):
    e = ReadingExercise(content=reading_content)
    questions = create_questions(reading_content)
    for question in questions:
        q = ReadingExerciseQuestion(question=question)
        correct_answer = create_answer(content=reading_content, question=question)
        q.correct_answer = correct_answer
        wrong_answers = create_wrong_answers(content=reading_content, question=question)
        for wrong_answer in wrong_answers:
            q.wrong_answers.append(wrong_answer)
        e.questions.append(q)
    return e


# 生成Word文档相关函数

def shuffle_options(correct_option, wrong_options):
    l = [*wrong_options, correct_option]
    shuffle(l)
    return l, l.index(correct_option)

def generate_worddoc(exercise):
    document = Document()
    
    document.add_heading('文章', level=1)
    
    document.add_paragraph('')

    for p in exercise.content.split('\n'):
        p = document.add_paragraph(p)
    
    document.add_heading('问题', level=1)
    
    ans = []
    
    for qid, question in enumerate(exercise.questions):
        document.add_paragraph(f'Question {qid + 1}:')
        document.add_paragraph(f'{question.question}')

        (options, ans_idx) = shuffle_options(question.correct_answer, question.wrong_answers)

        ans_key = chr(ord('A') + ans_idx)
        ans.append(ans_key)
        
        for i, op in enumerate(options):
            op_key = chr(ord('A') + i)
            document.add_paragraph(f'    {op_key}. {op}')
        document.add_paragraph('')


    document.add_page_break()
    document.add_heading('答案', level=1)

    for qid, ans_key in enumerate(ans):
        document.add_paragraph(f'Question {qid + 1}: {ans_key}')

    document.save('./output.docx')
    print(f'Exercise has been saved to {os.path.abspath("./output.docx")}')




# 函数定义完了，让我们来测试一下

article = """
A large language model (LLM) is a language model characterized by its large size. Their size is enabled by AI accelerators, which are able to process vast amounts of text data, mostly scraped from the Internet. The artificial neural networks which are built can contain from tens of millions and up to billions of weights and are (pre-)trained using self-supervised learning and semi-supervised learning. Transformer architecture contributed to faster training. Alternative architectures include the mixture of experts (MoE), which has been proposed by Google, starting with sparsely-gated ones in 2017, Gshard in 2021 to GLaM in 2022.
As language models, they work by taking an input text and repeatedly predicting the next token or word. Up to 2020, fine tuning was the only way a model could be adapted to be able to accomplish specific tasks. Larger sized models, such as GPT-3, however, can be prompt-engineered to achieve similar results. They are thought to acquire embodied knowledge about syntax, semantics and "ontology" inherent in human language corpora, but also inaccuracies and biases present in the corpora.
""".strip()

# 生成阅读练习
exercise = create_reading_exercise(article)
print(exercise)

# 转换成word格式， 并写入`./output.docx`
generate_worddoc(exercise)
```

现在你就可以打印`output.docx`，开始你的英语练习了。