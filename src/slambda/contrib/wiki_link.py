from slambda.core import Example, UnaryFunction, GptApiOptions

extract_wiki_links = UnaryFunction.from_instruction(
    instruction="Extract all wikipedia entities mention in the text.",
    examples=[
        Example(
            input="An analog computer or analogue computer is a type of computer that uses the continuous variation"
                  "aspect of physical phenomena such as electrical, mechanical, or hydraulic quantities (analog signals) "
                  "to model the problem being solved.",
            output="""
[computer](https://en.wikipedia.org/wiki/Computation)
[electrical](https://en.wikipedia.org/wiki/Electrical_network)
[mechanical](https://en.wikipedia.org/wiki/Mechanics)
[hydraulic](https://en.wikipedia.org/wiki/Hydraulics)
[analog signals](https://en.wikipedia.org/wiki/Analog_signal)
                """.strip()
        )
    ],
    gpt_opts=GptApiOptions(temperature=0)
)
