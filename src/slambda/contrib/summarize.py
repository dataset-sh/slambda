from slambda import Example, LmFunction

examples = [
    Example(
        input='Due to how affordable the clothing is and how new trends convince consumers to seek out more, '
              'the value of clothes may diminish in the eyes of consumers. '
              'As of 2019, the current report shows that 62 million metric tons of apparel were consumed globally.',
        output='One of the significant differences is that airplanes have more '
               'limitations to taking off and manuvering in different spaces than a helicopters'
    )
]

summarize = LmFunction.create(
    instruction='You are an assistant that summarize user input.',
    examples=examples
)
