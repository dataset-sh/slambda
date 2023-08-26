from enum import Enum
from typing import Optional, Union, List, Dict

from pydantic import BaseModel


class Role(str, Enum):
    """
    Role for chat message.
    https://platform.openai.com/docs/api-reference/chat/create#chat/create-role
    """
    system = 'system'
    user = 'user'
    assistant = 'assistant'
    function = 'function'


class Message(BaseModel):
    """Chat Model Message.

    Args:
        role: (Role for chat message)[https://platform.openai.com/docs/api-reference/chat/create#chat/create-role]
        content: (The contents of the message)[https://platform.openai.com/docs/api-reference/chat/create#chat/create-content]
        name: (The name of the author of this message)[https://platform.openai.com/docs/api-reference/chat/create#chat/create-name]
    """
    role: Role
    content: str
    name: Optional[str] = None

    @staticmethod
    def user(content, name=None):
        return Message(role=Role.user, content=content, name=name)

    @staticmethod
    def assistant(content, name=None):
        return Message(role=Role.assistant, content=content, name=name)

    @staticmethod
    def system(content, name=None):
        return Message(role=Role.system, content=content, name=name)

    @staticmethod
    def example_user(content):
        return Message(role=Role.system, content=content, name='example_user')

    @staticmethod
    def example_assistant(content):
        return Message(role=Role.system, content=content, name='example_assistant')


class GptApiOptions(BaseModel):
    """
    GptApiOptions used in OpenAI's ChatCompletion API.
    See [OpenAI's API reference](https://platform.openai.com/docs/api-reference/chat/create).

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
