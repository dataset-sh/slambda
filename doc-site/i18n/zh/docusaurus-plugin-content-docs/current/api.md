---
title: API 参考
description: Slambda API 参考
sidebar_position: 4
---


# API 参考

## 核心内容

### LmOutputCastingError

```python
class LmOutputCastingError(Exception):
    """
    如果使用 json.loads 无法解析语言模型输出，并且 cast_to_json 为 True，则会引发此异常提示语言模型输出类型转换错误。
    """

    def __init__(self, llm_output, message="无法转换语言模型输出"):
        """

        :param llm_output: 语言模型的文本输出
        :param message: 错误消息
        """
        self.llm_output = llm_output
        self.message = message
        super().__init__(self.message)
```

### FunctionInputType

```python
class FunctionInputType(str, Enum):
    """
    TextFunctionMode 控制文本函数的调用方式和函数输入类型。
    """
    KEYWORD = 'keyword'
    """
    KEYWORD 允许使用关键字参数进行调用，例如 f(a=10).
    """
    UNARY = 'unary'
    """
    UNARY 允许使用一个位置参数进行调用(一元函数)，例如 f(10).
    """
```

### Example

```python

FunctionInput = Union[str, Dict]
FunctionOutput = Union[str, List, Dict]
```

```python

class Example(BaseModel):
    """
    这个类输入(input)和输出(output)配对组成。
    Example 的 input 字段可以是 None、一个 str 值或一个 dict 对象。
    Example 的 output 字段可以是一个 str 值，也可以是一个 dict/list 对象。

    如果输入是一个dict(字典)，则输入中所有的值（input.values()）都必须能够使用 f-string 渲染为字符串，例如 f"{value}"。

    参数(Args)：
        input：None、str 值或 dict 对象。
        output：str 值或 dict/list 对象。
    """
    input: Optional[FunctionInput] = None
    output: FunctionOutput
```

### FunctionInputConfig

```python
class FunctionInputConfig(BaseModel):
    """
    这个类决定了函数允许使用什么类型的输入参数
    参数(Args)：
        input_type：Keyword或UNARY。
        allow_none：如果为 True，则允许输入为 None。
        strict_no_args：如果为 True，则函数将成为无参数函数（nullary function）。
    """
    input_type: FunctionInputType
    allow_none: bool = False
    strict_no_args: bool = False
```

### FunctionOutputConfig

```python
class FunctionOutputConfig(BaseModel):
    """
    这个类确定了函数应该返回哪种类型的输出结果
    参数(Args)：
        cast_to_json：将输出字符串转换为 JSON 格式。
    """
    cast_to_json: bool = False
```

### Definition

```python
class Definition(BaseModel):
    """
    这个类确定文本函数的定义。

    在执行调用时，所有来自 init_messages 的消息将被附加到消息列表中，然后：
        * 如果没有提供参数，则默认消息将被附加到消息列表
        * 如果提供了位置参数，则所有位置参数将被附加到消息列表
        * 如果提供了关键字参数，则将使用 message_template 进行渲染，并附加到消息列表。

    参数(Args)：
        name：此模板的可选名称。
        input_config：允许的调用模式。详见 (TextFunctionMode)[#TextFunctionMode]。
        message_template：如果提供了kwargs，则将使用keyword参数对该消息进行渲染。
        required_args：所需的keyword参数列表。
        examples：调用示例。
        gpt_opts：ChatCompletion API 的inference参数。
    """
    instruction: str
    examples: List[Example]

    message_stack: List[Message]

    input_config: FunctionInputConfig
    output_config: FunctionOutputConfig

    default_args: Optional[FunctionInput] = None

    # 对于keyword函数
    message_template: Optional[str] = None
    required_args: Optional[List[str]] = None

    # OpenAI 参数
    gpt_opts: GptApiOptions = Field(default_factory=GptApiOptions)

    name: Optional[str] = None
```

### LmFunction

```python
class LmFunction:
    """
    一个可以被调用的文本函数，创建这种函数的首选方式是使用 NullaryFunction、UnaryFunction 或 KeywordFunction 中的一个。
    """

    RESERVED_KEYWORDS = ['return_json', 'extra_messages', '__override', 'return_resp_obj']
    """
    RESERVED_KEYWORDS: 保留的关键词（keywords）：
    return_json: 将输出解析为 JSON。
    extra_messages: 额外的消息，将在模板的 init_messages 之后但最终消息之前附加。
    __override: 任何要覆盖的参数，目前可以覆盖以下参数：
                    * n
                    * top_p
                    * stream
                    * stop
                    * max_tokens
                    * presence_penalty
                    * frequency_penalty
                    * logit_bias
                    * user
                （详情请参阅此处）[https://platform.openai.com/docs/api-reference/chat/create]
    return_resp_obj: 如果设置为 true，则将直接返回 ChatCompletion API 返回的响应。                
    """

    definition: Definition
```

### LmFunction.create

```python
class LmFunction:
    @staticmethod
    def create(
            instruction: str,
            examples: List[Example],

            name: Optional[str] = None,
            strict_no_args: Optional[bool] = None,

            default_args: Optional[FunctionInput] = None,
            message_template: Optional[str] = None,
            required_args: Optional[List[str]] = None,
            gpt_opts: Optional[GptApiOptions] = None,
    ):
        """
        基于instruction和example创建一个LmFunction。

        :param instruction: 此函数将执行什么操作。
        :param examples: example的输入/输出。
        :param name: 此函数的可选名称。
        :param strict_no_args: 如果为True，则此函数将是一个无参数函数，但如果示例包含非None的输入，则此值将被忽略。
        :param default_args: 如果此值不为None，则可以无参数调用此函数，并将提供的值用作默认参数。
        :param message_template: 如果提供了kwargs，则将使用keyword参数呈现此消息。
        :param required_args: 需要的keyword参数列表。如果缺少此值且提供了message_template，则我们将基于message_template计算required_args。
        :param gpt_opts: ChatCompletion API的inference参数。
        :return: 创建的函数。
        """

```

## OpenAI API 相关
### Role
```python


class Role(str, Enum):
    """
    聊天消息的角色（在 OpenAI API 中，"role" 通常用于指定聊天模型中不同参与者的角色或身份。在聊天互动中，可以定义一个或多个角色，每个角色都有其独特的职责、行为和语境。通过指定角色，您可以模拟多个参与者之间的对话交流。

    例如，如果您希望使用 OpenAI API 模拟一个客户与客服代表的对话，您可以指定一个 "user" 角色和一个 "assistant" 角色。这样，您可以为每个角色提供不同的输入和指令，使模型根据不同角色的要求生成响应。

    在使用 OpenAI API 创建对话时，通过为每个角色提供相应的输入消息，您可以控制模型在对话中扮演不同的角色，从而实现更具交互性的应用场景。）

    详情请参见
    https://platform.openai.com/docs/api-reference/chat/create#chat/create-role
    """
    system = 'system'
    user = 'user'
    assistant = 'assistant'
    function = 'function'
```
### Message
```python
class Message(BaseModel):
    """Chat模型消息

    参数：
        role：(聊天消息的角色)[https://platform.openai.com/docs/api-reference/chat/create#chat/create-role]
        content：(消息的内容)[https://platform.openai.com/docs/api-reference/chat/create#chat/create-content]
        name：(此消息作者的名字)[https://platform.openai.com/docs/api-reference/chat/create#chat/create-name]"
    """
    role: Role
    content: str
    name: Optional[str] = None
```
### GptApiOptions
```python
class GptApiOptions(BaseModel):
    """
    在 OpenAI 的 ChatCompletion API 中使用GptApiOptions,
    请参见 [OpenAI 的 API 参考](https://platform.openai.com/docs/api-reference/chat/create)

    参数：
        model: 要使用的模型，该模型必须与 OpenAI 的 chatCompletion API 兼容 [OpenAI's chatCompletion API](https://platform.openai.com/docs/models/model-endpoint-compatibility)
        temperature: 要使用的采样温度，介于 0 和 2 之间。详见 OpenAI 的 API 参考 [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        n: 详见[OpenAI 的 API 参考](https://platform.openai.com/docs/api-reference/chat/create)
        top_p: 详见[OpenAI 的 API 参考](https://platform.openai.com/docs/api-reference/chat/create)
        stream: 详见[OpenAI 的 API 参考](https://platform.openai.com/docs/api-reference/chat/create)
        stop: 详见[OpenAI 的 API 参考](https://platform.openai.com/docs/api-reference/chat/create)
        max_tokens: 详见[OpenAI 的 API 参考](https://platform.openai.com/docs/api-reference/chat/create)
        presence_penalty: 详见[OpenAI 的 API 参考](https://platform.openai.com/docs/api-reference/chat/create)
        frequency_penalty: 详见[OpenAI 的 API 参考](https://platform.openai.com/docs/api-reference/chat/create)
        logit_bias: 详见[OpenAI 的 API 参考](https://platform.openai.com/docs/api-reference/chat/create)
        user: 详见[OpenAI 的 API 参考](https://platform.openai.com/docs/api-reference/chat/create)
    """
    model: str = 'gpt-3.5-turbo'
    temperature: Optional[float] = None
    n: Optional[int] = None
    top_p: Optional[float] = None
    stream: Optional[bool] = None
    stop: Optional[Union[str, List[str]]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    logit_bias: Optional[Dict[int, int]] = None
    user: Optional[str] = None
```