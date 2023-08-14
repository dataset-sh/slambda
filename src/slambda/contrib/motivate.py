from slambda.core import TextFunction, Template, Example

examples = [
    Example(
        output="Embrace each new day as a fresh opportunity to chase your dreams and create the life you envision. Challenges may arise, but remember, they are stepping stones on your path to success. Believe in your abilities, stay focused on your goals, and let your determination shine brighter than any obstacles. You have the power to turn your aspirations into reality – keep moving forward with unwavering courage and a positive spirit. Your journey is unique, and every step you take brings you closer to the extraordinary success that awaits. Keep pushing, keep believing, and keep thriving!"
    )
]

template = Template(
    name="motivate",
    description="Generate motivational messages.",
    default_message="Generate a motivational message.",
).follow_instruction(
    instruction='Generate motivational messages.',
    examples=examples,
)

motivate_me = TextFunction(template)
