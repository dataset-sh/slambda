from slambda import Example, LmFunction, GptApiOptions, LmOutputCastingError

extract_wiki_links = LmFunction.create(
    instruction="Extract all wikipedia entities mentioned in the text and format them in JSON as following [{name: '', url: ''}].",
    examples=[
        Example(
            input="An analog computer or analogue computer is a type of computer that uses the continuous variation"
                  "aspect of physical phenomena such as electrical, mechanical, or hydraulic quantities (analog signals) "
                  "to model the problem being solved.",
            output=[
                {
                    "name": "computer",
                    "url": "https://en.wikipedia.org/wiki/Computation",

                },
                {
                    "name": "electrical",
                    "url": "https://en.wikipedia.org/wiki/Electrical_network",
                },
                {
                    "name": "mechanical",
                    "url": "https://en.wikipedia.org/wiki/Mechanics",
                },
                {
                    "name": "hydraulic",
                    "url": "https://en.wikipedia.org/wiki/Hydraulics",
                },
                {
                    "name": "analog signals",
                    "url": "https://en.wikipedia.org/wiki/Analog_signal",
                }
            ]
        )
    ],
    gpt_opts=GptApiOptions(temperature=0)
)
