from slambda.core import TextFunction, Template, Example

examples = [
    Example(
        input="Absolutely love this product! The self-licking feature is a game-changer for ice cream lovers like me. No more melty messes, just pure enjoyment. A must-have for summer!",
        output="positive"
    ),
    Example(
        input="Bought this new HyperGadget Pro and what a disappointment! It feels cheap, doesn't work as advertised, and the battery life is a joke. Save your money and avoid this one.",
        output="negative"
    )
]

template = Template(
    name="sentiment",
    description="Detect sentiment of the given text",
    temperature=0,
).follow_instruction(
    instruction='Answer positive if premise entail hypothesis, false negative.',
    examples=examples,
)

sentiment = TextFunction(template)
