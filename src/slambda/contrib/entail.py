from slambda import LmFunction, Example, GptApiOptions

examples = [
    Example(
        input={
            'premise': 'Wasps are attracted to sweet foods and beverages, as well as protein-based sources.',
            'hypothesis': 'Wasp like sugary drinks',
        },
        output='true'
    )
]
 
entail = LmFunction.create(
    instruction='Answer true if premise entail hypothesis, false otherwise.',
    examples=examples,
    message_template="premise: {premise}\nhypothesis: {hypothesis}",
    gpt_opts=GptApiOptions(temperature=0)
)
