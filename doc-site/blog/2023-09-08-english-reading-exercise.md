---
slug: english-reading-exercise
title: Using Slambda to turn any article into an English reading exercise
authors:
  - haowu4
tags: [slambda, use-case]
---

# Using slambda to turn any article into an English reading exercise

Reading comprehension is one of the most common type of questions in ESL (English as a second language) learning processes and exams. However, the article itself can be out of interest or dull, reducing one's enthusiasm for practicing english skill.

Learning English might be more enjoyable and effortless if we turn daily news or articles that fit our interests into reading comprehension questions.

To do so, we can use a large language model, such as ChatGPT. However, after experimenting with this idea using simple prompts, we noticed that while the outputs often look impressive at first glance, there are always a few minor issues. For example, the output format may vary from time to time, and occasionally, it will generate mistakes, such as more than one correct answer in a multiple-choice question.

Obviously, this is a complicated task, and in order to resolve the issues we mentioned above, we can try to break it down into several simpler subtasks and then combine the output of each subtask using a high-level algorithmic procedure. In this case, 'slambda' will come in handy as it allows you to define these subtasks as python functions using nothing but natural language instructions and several input/output examples.

For example, after playing around this idea a little bit more, we have made the following observations:

* When given an article, the language model can reliably generate questions.
* When given an article and a question, the language model can accurately answer the question.
* When given an article and a question, the language model can reliably and correctly generate incorrect options for the multiple choice question.

With these observations in mind, we can start to implement a high-level procedure for generating reading comprehension questions given the content of an article, and we will write it as a python function.

## Defining Data Structures

First, we need to define the necessary data structures:

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


## Decomposing the Problem

Then, let's outline the general process for generating reading comprehension exercises in python:


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

In the code above, we will only generate the question bodies for the given article without the answer and options. Then, for each question, we will fill in the correct answer and three more options for each question to make them a valid multiple choice questions.

## Defining slambda Functions

The following functions are still not defined in the body of the function `create_reading_exercise`:

* `create_questions(content)`: Generates some reading comprehension questions for the given article.
* `create_answer(content, question)`: Provides the correct answer for the given article and question.
* `create_wrong_answers(question)`: Generates three incorrect options for the given article and question.


With slambda, implementing these functions is straightforward. We only need to provide natural language instructions and some input/output pairs as examples.


<details><summary>You need Openai API key to use slambda
</summary>

To learn more about how to load openai API key，you can visit <a href="/docs/tips/apikey" target="_blank">our related article</a>

```python title="how to load Openai API key"
import openai
from dotenv import load_dotenv
# This file contains OpenAI API KEY
load_dotenv(dotenv_path='.env.local')

# Load openai.api_key with environmental variable OPENAI_API_KEY
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


exercise = create_reading_exercise(article)

```

In the example above, both `create_questions` and `create_wrong_answers` return a `list[str]`, while `create_answer` returns a single `str`.

## Generating a MS Word Document

Now, with everything defined, we can run the code to create a reading comphrehension exercise. However, its output format is in a pydantic model, which is not very human-readable. So, we need to render this content to a word docx file so we can print it out with Word and use it as real study material. In this case, we can generate a docx file from the `ReadingExercise` instance using another open-source library [python-docx](https://python-docx.readthedocs.io/en/latest/#user-guide).

We can use the following code to generate a word document.

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

You can now print out `output.docs` and use it as an ESL learning material.

## The complete source code

### Install dependencies

```bash
pip install slambda python-docx openai pydantic python-dotenv
```

### Code

```python
import os
import openai

from docx import Document
from docx.shared import Inches
from dotenv import load_dotenv
from slambda import Example, LmFunction, GptApiOptions
from pydantic import BaseModel, Field
from random import shuffle

# This file contains the OpenAI API KEY

load_dotenv(dotenv_path='.env.local')

# Read OPENAI_API_KEY from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

if openai.api_key is None:
    print("OPENAI_API_KEY is missing")
    raise ValueError('OPENAI_API_KEY is missing')

# Define Data Structures

class ReadingExerciseQuestion(BaseModel):
    question: str
    correct_answer: str = ''
    wrong_answers: list[str] = Field(default_factory=list)

class ReadingExercise(BaseModel):
    content: str = ''
    questions: list[ReadingExerciseQuestion] = Field(default_factory=list)


# Define Slambda functions

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


# Generate Questions and Options

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


# Generate docx related Functions

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


# We have everything now, let's test them.

article = """
As house prices have climbed, saving for a down payment is out of reach for many Canadians, particularly young people. Today, the Honourable Marc Miller, Minister of Immigration, Refugees and Citizenship, shared how the new tax-free First Home Savings Account is available and helping put home ownership back within reach of Canadians across the country.
The new tax-free First Home Savings Account is a registered savings account that helps Canadians become first-time home buyers by contributing up to $8,000 per year (up to a lifetime limit of $40,000) for their first down payment within 15 years. To help Canadians reach their savings goals, First Home Savings Account contributions are tax deductible on annual income tax returns, like a Registered Retirement Savings Plan (RRSP). Like a Tax‑Free Savings Account, withdrawals to purchase a first home, including any investment income on contributions, are non-taxable. Tax-free in; tax-free out.
Financial institutions have been offering the First Home Savings Account to Canadians since April 1, 2023, and it’s now available at 7 financial institutions, with more set to offer it soon.
""".strip()

# Generate a reading exercise
exercise = create_reading_exercise(article)

# Convert it to docx and write to './output.docx'
generate_worddoc(exercise)

```

You can now print out `output.docs` and use it as an ESL learning material.