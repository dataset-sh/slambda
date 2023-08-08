from slambda.core import TextFunction, Template, Message

template = Template(
    name="entail",
    init_messages=[
        Message.system('Answer true if premise entail hypothesis, false otherwise.'),
        Message.example_user("premise: What can i do for you?\nhypothesis: asking user to provide request"),
        Message.example_assistant('true'),
        Message.example_user("premise: What can i do for you?\nhypothesis: providing user weather information"),
        Message.example_assistant('false'),
    ],
    temperature=0,
    message_template="premise: {premise}\nhypothesis: {hypothesis}",
)

entail = TextFunction(template)
