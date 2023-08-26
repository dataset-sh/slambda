from slambda.core import UnaryFunction
from slambda import Example

fix_grammar = UnaryFunction.from_instruction(
    instruction="Fix grammar and spelling error for user",
    examples=[
        Example("I eat three applr yesteday.", "I ate three apples yesterday."),
    ]
)
