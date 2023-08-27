from slambda import Example, LmFunction, GptApiOptions

sentiment = LmFunction.create(
    instruction='Detect sentiment of the given text, answer positive for positive sentiment, negative for negative sentiment, otherwise neutral.',
    examples=[
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
    ],
    gpt_opts=GptApiOptions(temperature=0)
)

aspect_sentiment = LmFunction.create(
    instruction='Detect sentiment of the given text, list all aspect sentiment in the following format, sentiment can be one of positive, negative, and neutral',
    examples=[
        Example(
            input="The camera on this smartphone is amazing, capturing stunning photos even in low light. However, the battery life leaves much to be desired.",
            output=[
                {'aspect': 'Camera', 'sentiment': 'positive'}
            ]
        )
    ],
    gpt_opts=GptApiOptions(temperature=0)
)
