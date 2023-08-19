---
title: API Reference
sidebar_position: 4
---

# API Reference

```python
class Role(str, Enum):
    """
    Role for chat message
    https://platform.openai.com/docs/api-reference/chat/create#chat/create-role
    """
    system = 'system'
    user = 'user'
    assistant = 'assistant'
    function = 'function'
```


```python
class Message(BaseModel):
    """Chat Model Message

    Args:
        role: (Role for chat message)[https://platform.openai.com/docs/api-reference/chat/create#chat/create-role]
        content: (The contents of the message)[https://platform.openai.com/docs/api-reference/chat/create#chat/create-content]
        name: (The name of the author of this message)[https://platform.openai.com/docs/api-reference/chat/create#chat/create-name]
    """
    role: Role
    content: str
    name: Optional[str] = None
```

```python
class TextFunctionMode(str, Enum):
    """
    TextFunctionMode control how a text function can be called.
    """
    KEYWORD = 'keyword'
    """
    KEYWORD allows calling with keyword arguments, e.g. f(a=10)
    """
    POS = 'pos'
    """
    POS allows calling with positional arguments, e.g. f(10)
    """
    NO_ARGS = 'no_args'
    """
    NO_ARGS allows calling with no arguments, e.g. f()
    """
```


```python
class Example(BaseModel):
    input: Optional[Union[Dict, str]] = None
    output: Union[Dict, str] = None
```

```python
class GptApiOptions(BaseModel):
    """
    GptApiOptions used in OpenAI's ChatCompletion API.
    See [OpenAI's API reference](https://platform.openai.com/docs/api-reference/chat/create)

    Args:
        model: which model to use, the model must be compatible with [OpenAI's chatCompletion API](https://platform.openai.com/docs/models/model-endpoint-compatibility)
        temperature: What sampling temperature to use, between 0 and 2. See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        n: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        top_p: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        stream: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        stop: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        max_tokens: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        presence_penalty: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        frequency_penalty: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        logit_bias: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        user: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
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

```python
class Definition(BaseModel):
    """
    Definition is an ChatGPT API call template.

    When executing the call, all message from init_messages will be appended to the message list, and then
        * if no arguments is provided, the default message will be appended to the message list
        * if positional arguments is provided, all the positional arguments will be appended to the message list
            if multiple positional arguments are provided, they will be joined by a comma.
        * if keyword arguments is provided, message_template will be rendered and appended to the message list

    Args:
        name: optional name of this template.
        description: an optional description for the template.
        mode: what call modes are allowed. See (TextFunctionMode)[#TextFunctionMode] for detail.
        init_messages: A list of messages comprising the conversation so far, this can be used for providing.
        default_message: this message will be sent if no args are provided.
        message_template: this message will be rendered with keyword arguments if kwargs are provided.
        required_args: list of required keyword args.
        json_output: if output is in json format or string.
        examples: call examples.
        gpt_opts: Inference parameters for ChatCompletion API.
    """
    # Template Information
    name: Optional[str] = None
    description: str = ''
    mode: List[TextFunctionMode] = Field(default_factory=list)

    # Message Config
    init_messages: List[Message] = Field(default_factory=list)
    default_message: Optional[str] = None
    message_template: Optional[str] = None
    required_args: Optional[List[str]] = None
    json_output: bool = False

    examples: List[Example] = Field(default_factory=list)

    # OpenAI parameters
    gpt_opts: GptApiOptions = Field(default_factory=GptApiOptions)
```

```python
class TextFunction:
    RESERVED_KEYWORDS = ['return_json', 'extra_messages', '__override', 'return_resp_obj']
    """
    RESERVED_KEYWORDS: reserved keywords:
    return_json: parse output as json.
    extra_messages: extra messages to be carried over, it will be appended after init_messages from template but 
                    before the final message
    __override: any parameters to be override, currently you can override the following:
                    * n
                    * top_p
                    * stream
                    * stop
                    * max_tokens
                    * presence_penalty
                    * frequency_penalty
                    * logit_bias
                    * user
                (see here for details)[https://platform.openai.com/docs/api-reference/chat/create]
    return_resp_obj: if set to true, the response from ChatCompletion API will be returned directly                
    """

    definition: Definition
```

```python
def create_function(
        instruction: str,
        examples: Optional[List[Example]] = None,
        gpt_opts: Optional[GptApiOptions] = None,

        allow_no_arg: bool = False,
        default_message: Optional[str] = None,

        allow_pos: bool = False,

        allow_keyword: bool = False,
        message_template: Optional[str] = None,
        required_args: Optional[List[str]] = None,

        json_output=None,
)
```

```python
class NullaryFunction:
    @staticmethod
    def from_instruction(
            instruction: str,
            examples: Optional[List[Example]] = None,
            gpt_opts: Optional[GptApiOptions] = None,

            default_message: Optional[str] = None,

            json_output=None,
    )
```


```python
class UnaryFunction:
    @staticmethod
    def from_instruction(
            instruction: str,
            examples: Optional[List[Example]] = None,
            gpt_opts: Optional[GptApiOptions] = None,

            allow_no_arg: bool = False,
            default_message: Optional[str] = None,

            json_output=None,
    ):
```


```python
class KeywordFunction:
    @staticmethod
    def from_instruction(
            instruction: str,
            examples: Optional[List[Example]] = None,
            gpt_opts: Optional[GptApiOptions] = None,

            message_template: Optional[str] = None,

            allow_no_arg: bool = False,
            default_message: Optional[str] = None,

            json_output=None,
    ):
```
