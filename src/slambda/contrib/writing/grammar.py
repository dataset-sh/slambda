from slambda import Example, LmFunction

fix_grammar = LmFunction.create(
    instruction="Fix grammar and spelling error for user",
    examples=[
        Example("I eat three applr yesteday.", "I ate three apples yesterday."),
    ]
)
