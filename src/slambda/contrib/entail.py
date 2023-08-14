from slambda.core import TextFunction, Template, Example

examples = [
    Example(
        input={
            'premise': 'Wasps are attracted to sweet foods and beverages, as well as protein-based sources.',
            'hypothesis': 'Wasp like sugary drinks',
        },
        output='true'
    )
]

template = Template(
    name="entail",
    description="",
    temperature=0,
    message_template="premise: {premise}\nhypothesis: {hypothesis}",
    required_args=['premise', 'hypothesis'],
).follow_instruction(
    instruction='Answer true if premise entail hypothesis, false otherwise.',
    examples=examples,
)

entail = TextFunction(template)
