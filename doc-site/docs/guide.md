---
title: "Guide"
description: Slambda Usage Guide
sidebar_position: 2
---

# Guide

:::tip
You can enable code block warp in this guide by clicking this button
![Code Block Warp Button](/img/code-block-wrap-button.png)
:::

## Concepts

In sLambda, functions are defined by instruction and examples. We create normal python function using only a natural
language instruction, a set of
example input/output pairs. For example:

```python
from slambda import Example, UnaryFunction

fix_grammar = UnaryFunction.from_instruction(
    instruction="Fix grammar and spelling errors for user",
    examples=[
        Example("I eat three applr yesteday.", "I ate three apples yesterday."),
    ]
)

fix_grammar(
    "Schopenhaur did not deny that the external world exists empiracle, but he followed Kant in claimin' that our knowledge and experiense of the world are always indirekt.")
# Output: 'Schopenhauer did not deny that the external world exists empirically, but he followed Kant in claiming that our knowledge and experience of the world are always indirect.'
```

in this guide, we will first introduce the core concepts in sLambda:

1. **Function**
2. **Instruction**
3. **Example**

We hope by looking at the examples we provide in this guide, you will be able to implement your own slambda function for
your own problem.

We will also share some tips for more advanced sLambda usage.

### Function

Funtions in sLambda are standard python functions, it takes an input and map it to an output according to some internal
logic.
But instead of writing python statements inside the function body as the transformation logic, we use **Instruction**
and **Example** to create such logic.

In sLambda, there are 3 types of functions depending on input/output shape:

* Nullary Function
* Unary Function
* Keyword Function

#### Nullary Function

A nullary function takes no arguments. For example, a nullary function `f`, can only be used like this: `f()`.

```python title="Nullary Function Example"
from slambda import NullaryFunction, Example

motivate_me = NullaryFunction.from_instruction(
    instruction='Generate motivational messages.',
    examples=[
        Example(
            output="Embrace each new day as a fresh opportunity to chase your dreams and create the life you envision. Challenges may arise, but remember, they are stepping stones on your path to success. Believe in your abilities, stay focused on your goals, and let your determination shine brighter than any obstacles. You have the power to turn your aspirations into reality – keep moving forward with unwavering courage and a positive spirit. Your journey is unique, and every step you take brings you closer to the extraordinary success that awaits. Keep pushing, keep believing, and keep thriving!"
        )
    ],
    default_message="Generate a motivational message.",
)

motivate_me()
# Output is omitted
```

#### Unary Function

A unary function takes exactly one positional argument. For example, a unary function `f`, can only be used like
this: `f("some value")`.

You can also config a unary function with `allow_no_arg=True`, which allow you to call it with no arguments.

```python title="Unary Function"
from slambda import Example, UnaryFunction

fix_grammar = UnaryFunction.from_instruction(
    instruction="Fix grammar and spelling error for user",
    examples=[
        Example(
            input="I eat three applr yesteday.",
            output="I ate three apples yesterday."
        ),
    ],
    allow_no_arg=False,
    default_message=None,  # If allow_no_arg=true, this will be the default argument, i.e. f() == f(default_message)
)

fix_grammar(
    "Schopenhaur did not deny that the external world exists empiracle, but he followed Kant in claimin' that our knowledge and experiense of the world are always indirekt.")
# Output: 'Schopenhauer did not deny that the external world exists empirically, but he followed Kant in claiming that our knowledge and experience of the world are always indirect.'
```

#### Keyword Function

A keyword function takes only keyword arguments. For example, a keyword function `f`, can only be used like
this: `f(name="jack", age=10)`.

You can also config a keyword function with `allow_no_arg=True`, which allow you to call it with no arguments.

```python title="Keyword Function Example"
from slambda import Example, KeywordFunction

generate_essay = KeywordFunction.from_instruction(
    instruction="Write an grad school application essay about 250 words using the given information",
    examples=[
        Example(
            input={
                "title": " Why I want to apply for master degree in computer science",
                "work_experience": "electrician, financial analyst",
                "education_experience": "Bachelor degree in english",
            },
            output="""
Transitioning from being an electrician to a financial analyst, and equipped with a Bachelor's degree in English, I am driven to undertake a Master's degree in Computer Science. This decision arises from my diverse experiences, revealing the intersecting points between my past and the boundless possibilities of the tech world.
My time as an electrician cultivated problem-solving and precision skills, paralleling the demands of programming. Similarly, my role as a financial analyst exposed me to the potency of data analysis and technology-driven decision-making. Recognizing these common threads, I am keen to meld my existing expertise with the innovation fostered by computer science.
My Bachelor's degree in English endowed me with critical thinking and communication prowess, invaluable assets when navigating interdisciplinary collaborations and explaining intricate technicalities. By pursuing a Master's in Computer Science, I aspire to fuse my linguistic finesse with programming adeptness, enhancing my capacity to innovate and contribute effectively.
The evolving landscape of computer science intrigues my intellectual curiosity, from AI and machine learning to cybersecurity and software engineering. This fervor drives my academic pursuit, aiming to amplify my theoretical knowledge and hands-on skills, positioning me at technology's vanguard.
In conclusion, my journey – from electrician to financial analyst, fortified by a Bachelor's in English – has illuminated the transformative potential of computer science. With a burning desire to challenge and unite my experiences, I am resolute in my commitment to a Master's in Computer Science. This endeavor promises not only personal enrichment but also a chance to meaningfully influence the trajectory of technological advancement.        
            """.strip()),
    ],

    # message_template to render the messages, if provided, the out-going message will be  message_template.format(**kwargs)
    # if message_template is None, "\n".join([f"{k}: {v}" for k, v in kwargs.items()]) will be used.
    message_template=None,

    allow_no_arg=False,
    default_message=None,  # If allow_no_arg=true, this will be the default argument, i.e. f() == f(default_message)
)

generate_essay(
    title=" Why I want to apply for master's degree in computer science",
    work_experience="actor, bartender",
    education_experience="Bachelor's degree in english", 
    age=60  # Yes, you can add more information beyond what is included in the examples. 
)
# Output is omitted
```

if message_template is provided, it will be used to render the out-going message by
running `message_template.format(**kwargs)`
. Otherwise, value of `"\n".join([f"{k}: {v}" for k, v in kwargs.items()])` will be used.

### Instruction

Instructions are simply natural language command, for example:

```python
instruction = "Fix grammar and spelling errors for user"
```

### Example

Example is defined as below and will be served as one/few shots learning examples during inference:

```python
class Example(BaseModel):
    input: Optional[Union[Dict, str]] = None
    output: Union[Dict, List, str] = None

    def __init__(self, input=None, output=None, **kwargs):
        super().__init__(input=input, output=output, **kwargs)
```

The `input` field of `Example` can be one of `None`, a `str` value, or a `dict` object.

The `output` field of `Example` can be either a `str` value, or a `dict`/`list` object.

* For nullary function, the `input` field should be `None`.
* For unary function, the `input` field should be `str`. If `allow_no_arg` is `True`, it can also be `None`.
* For keyword function, the `input` field should be `dict`. If `allow_no_arg` is `True`, it can also be `None`.

If input is a `dict`, all value in `input.values()` must be able to render as a string with f-string i.e. `f"{value}"`

```python title="Input: String Output:String"
from slambda import Example

# String to String
Example("food is great", "positive")

# String to Dict/List
Example("food is great", [{"sentiment": "positive", "aspect": "food"}])

# Empty input to String
Example(output={"aspects": [
    {"sentiment": "positive", "aspect_name": "food"}
]})

# Empty input to String
Example(output={"aspects": [
    {"sentiment": "positive", "aspect_name": "food"}
]})
```

## Tips

### Json Output

By providing Example with `dict`/`list` output, and `json_output=True`, you can make you function return a `dict`.

```python
from slambda import Example, UnaryFunction, GptApiOptions

find_tickers = UnaryFunction.from_instruction(
    instruction="Extract all companies' tickers mention in the news title.",
    examples=[
        Example(
            input="Why Kroger, Albertsons need to merge immediately to compete with Walmart",
            output={
                "tickers": ["KR", "ACI"]
            })
    ],
    json_output=True,
    gpt_opts=GptApiOptions(temperature=0)
)

find_tickers("These Stocks Are Moving the Most Today: Keysight, Farfetch, XPeng, Tesla, Deere, and More")
# Output: {'tickers': ['KEYS', 'FTCH', 'XPEV', 'TSLA', 'DE']}
```

However, LLM will some time generate syntactically incorrect json, in that case, the function will return string
instead.

### Controlling Inference Parameters

You can also control the inference parameters such as `temperature` with `GptApiOptions`

```python
from slambda import NullaryFunction, Example, GptApiOptions

motivate_me = NullaryFunction.from_instruction(
    instruction='Generate motivational messages.',
    examples=[
        Example(
            output="Embrace each new day as a fresh opportunity to chase your dreams and create the life you envision. Challenges may arise, but remember, they are stepping stones on your path to success. Believe in your abilities, stay focused on your goals, and let your determination shine brighter than any obstacles. You have the power to turn your aspirations into reality – keep moving forward with unwavering courage and a positive spirit. Your journey is unique, and every step you take brings you closer to the extraordinary success that awaits. Keep pushing, keep believing, and keep thriving!"
        )
    ],
    gpt_opts=GptApiOptions(temperature=1.5)
)
```

GptApiOptions Args (See [OpenAI's API reference](https://platform.openai.com/docs/api-reference/chat/create)):

* **model**: which model to use, the model must be compatible
  with [OpenAI's chatCompletion API](https://platform.openai.com/docs/models/model-endpoint-compatibility)
* **temperature**: What sampling temperature to use, between 0 and 2.
  See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **n**: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **top_p**: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **stream**: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **stop**: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **max_tokens**: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **presence_penalty**: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **frequency_penalty**: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **logit_bias**: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **user**: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)

### Overriding Inference Parameters

If you wish to override some inference parameters per-call basis, you can use `__override` keyword as following:

```python
from slambda import NullaryFunction, Example, GptApiOptions

motivate_me = NullaryFunction.from_instruction(
    instruction='Generate motivational messages.',
    examples=[
        Example(
            output="Embrace each new day as a fresh opportunity to chase your dreams and create the life you envision. Challenges may arise, but remember, they are stepping stones on your path to success. Believe in your abilities, stay focused on your goals, and let your determination shine brighter than any obstacles. You have the power to turn your aspirations into reality – keep moving forward with unwavering courage and a positive spirit. Your journey is unique, and every step you take brings you closer to the extraordinary success that awaits. Keep pushing, keep believing, and keep thriving!"
        )
    ],
    gpt_opts=GptApiOptions(temperature=1.5)
)
motivate_me(__override={'temperature': 1.0})
motivate_me(return_resp_obj=True)
```

### Access Raw OpenAI Response

You can use `return_resp_obj=True` keyword when calling your slambda function, which will force the function to return
the raw OpenAI response object.

Note that `return_resp_obj=True` by default when `stream=True`.

```python
from slambda import NullaryFunction, Example, GptApiOptions

motivate_me = NullaryFunction.from_instruction(
    instruction='Generate motivational messages.',
    examples=[
        Example(
            output="Embrace each new day as a fresh opportunity to chase your dreams and create the life you envision. Challenges may arise, but remember, they are stepping stones on your path to success. Believe in your abilities, stay focused on your goals, and let your determination shine brighter than any obstacles. You have the power to turn your aspirations into reality – keep moving forward with unwavering courage and a positive spirit. Your journey is unique, and every step you take brings you closer to the extraordinary success that awaits. Keep pushing, keep believing, and keep thriving!"
        )
    ],
    gpt_opts=GptApiOptions(temperature=1.5)
)

motivate_me(return_resp_obj=True)
```

### Temperature Value

`Temperature` control the randomness of output by controlling the sampling temperature during inference.

For generation tasks such as writing, you may want a slightly higher temperature.
For classification and extraction tasks where there exists a correct answer for each input, you should consider using a
lower temperature such as 0.

### Behind the scene

Instruction and Examples are translated into `system` messages similar to this
[Cookbook Recipe](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_format_inputs_to_ChatGPT_models.ipynb).
Our documentation of existing functions contains a visualization of its message stack that may help you understand what
is happening behind the scene, for
example see [writing.essay](/docs/functions/writing/essay).

