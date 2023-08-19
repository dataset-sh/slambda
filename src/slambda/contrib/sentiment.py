from slambda import Example, UnaryFunction, GptApiOptions

examples = [
    Example(
        input="Absolutely love this product! The self-licking feature is a game-changer for ice cream lovers like me. No more melty messes, just pure enjoyment. A must-have for summer!",
        output="positive"
    ),
    Example(
        input="Bought this new HyperGadget Pro and what a disappointment! It feels cheap, doesn't work as advertised, and the battery life is a joke. Save your money and avoid this one.",
        output="negative"
    ),
    Example(
        input="I ate at this restaurant yesterday.",
        output="neutral"
    )

]

sentiment = UnaryFunction.from_instruction(
    instruction='Detect sentiment of the given text, answer positive for positive sentiment, negative for negative sentiment, otherwise neutral.',
    examples=examples,
    gpt_opts=GptApiOptions(temperature=0)
)
