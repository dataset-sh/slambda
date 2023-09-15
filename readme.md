# Sλ: Getting Started

[![codecov](https://codecov.io/gh/dataset-sh/slambda/graph/badge.svg?token=MPNI0H3U7C)](https://codecov.io/gh/dataset-sh/slambda)

## What does slambda do?

Integrating language model such as GPT into your code can be a difficult process. sLambda simplifies the process by
translating natural language instructions and examples into ready-to-use **Python functions**.

## Install

```bash
pip install slambda
```

## Prerequisite

Currently, sLambda only supports OpenAI's ChatCompletion API, so you will need an OpenAI API key in order to use this
package,

Please check [OpenAI's documentation: Authentication](https://platform.openai.com/docs/api-reference/authentication) if
you need to create a new API key.  [Create an OpenAI API Key Here](https://platform.openai.com/account/api-keys).

If you have encountered this error:

```
AuthenticationError: No API key provided. You can set your API key in code using 'openai.api_key = <API-KEY>', 
or you can set the environment variable OPENAI_API_KEY=<API-KEY>). If your API key is stored in a file, 
you can point the openai module at it with 'openai.api_key_path = <PATH>'. You can generate API keys in the OpenAI web 
interface. See https://platform.openai.com/account/api-keys for details.
```

It means that you need to supply `OPENAI_API_KEY` somewhere in your code. Check out our guide
on [Loading API key](/docs/tips/apikey) for best practices.

```python
import os
import openai

# We highly recommend you to load OPENAI_API_KEY via environmental variable 

if not os.getenv("OPENAI_API_KEY"):
    print(
        "You need to set environmental variable OPENAI_API_KEY, consider using dotenv."
        "See more on https://slambda.dataset.sh/docs/tips/apikey"
    )

openai.api_key = os.getenv("OPENAI_API_KEY")

# ---------or---------

# You can also do it by providing value directly
openai.api_key = "sk-ThIsIsAFaKeKEY12345678990...."
# But we considered to be a security risk, please read our guide on how to load api key for more details. 
```

## Define your own functions

`sLambda` can help you turn OpenAI's ChatCompletion api into a extraction, classification, generation api with ease.

### Extraction

```python title="Extract stock Tickers"
from slambda.core import UnaryFunction
from slambda import Example, GptApiOptions

find_tickers = UnaryFunction.from_instruction(
    instruction="Extract all companies' tickers mention in the news title.",
    examples=[
        Example("Why Kroger, Albertsons need to merge immediately to compete with Walmart", "$KR, $ACI")
    ],
    gpt_opts=GptApiOptions(temperature=0)
)

find_tickers("These Stocks Are Moving the Most Today: Keysight, Farfetch, XPeng, Tesla, Deere, and More")
# Output: '$KEYS, $FTCH, $XPEV, $TSLA, $DE'
```

```python title="Extract Wikipeida Links"
from slambda.core import UnaryFunction
from slambda import Example, GptApiOptions

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

extract_wiki_links(
    "Without negative feedback, and optionally positive feedback for regeneration, an op amp acts as a comparator.")

# Output: 
# [negative feedback](https://en.wikipedia.org/wiki/Negative_feedback)
# [op amp](https://en.wikipedia.org/wiki/Operational_amplifier)
# [comparator](https://en.wikipedia.org/wiki/Comparator)
```

### Generation

```python title="Fix Grammar"
from slambda.core import UnaryFunction
from slambda import Example

fix_grammar = UnaryFunction.from_instruction(
    instruction="Fix grammar and spelling error for user",
    examples=[
        Example("I eat three applr yesteday.", "I ate three apples yesterday."),
    ]
)

fix_grammar(
    "Schopenhaur did not deny that the external world exists empiracle, but he followed Kant in claimin' that our knowledge and experiense of the world are always indirekt.")
# Output: 'Schopenhauer did not deny that the external world exists empirically, but he followed Kant in claiming that our knowledge and experience of the world are always indirect.'

```

```python title="Write Essay"
from slambda.core import KeywordFunction
from slambda import Example

generate_essay = KeywordFunction.from_instruction(
    instruction="Write an grad school application essay about 250 words using the given information",
    examples=[
        Example(
            input={
                "title": " Why I want to apply for master degree in computer science",
                "work_experience": "electrician, financial analyst",
                "education_experience": "Bachelor degree in english",
            },
            output="""
Transitioning from being an electrician to a financial analyst, and equipped with a Bachelor's degree in English, I am driven to undertake a Master's degree in Computer Science. This decision arises from my diverse experiences, revealing the intersecting points between my past and the boundless possibilities of the tech world.
My time as an electrician cultivated problem-solving and precision skills, paralleling the demands of programming. Similarly, my role as a financial analyst exposed me to the potency of data analysis and technology-driven decision-making. Recognizing these common threads, I am keen to meld my existing expertise with the innovation fostered by computer science.
My Bachelor's degree in English endowed me with critical thinking and communication prowess, invaluable assets when navigating interdisciplinary collaborations and explaining intricate technicalities. By pursuing a Master's in Computer Science, I aspire to fuse my linguistic finesse with programming adeptness, enhancing my capacity to innovate and contribute effectively.
The evolving landscape of computer science intrigues my intellectual curiosity, from AI and machine learning to cybersecurity and software engineering. This fervor drives my academic pursuit, aiming to amplify my theoretical knowledge and hands-on skills, positioning me at technology's vanguard.
In conclusion, my journey – from electrician to financial analyst, fortified by a Bachelor's in English – has illuminated the transformative potential of computer science. With a burning desire to challenge and unite my experiences, I am resolute in my commitment to a Master's in Computer Science. This endeavor promises not only personal enrichment but also a chance to meaningfully influence the trajectory of technological advancement.        
            """.strip()),
    ]
)

generate_essay(
    title=" Why I want to apply for master degree in computer science",
    work_experience="actor, bartender",
    education_experience="Bachelor degree in english",
    age=60  # Yes, you can add more information beyond what is included in the examples. 
)

# Output:
# As a non-traditional applicant, my decision to pursue a Master's degree in Computer Science stems from a combination
# of my diverse work experiences and my passion for embracing new challenges at the age of 60. Having worked as an actor 
# and bartender, I have always been comfortable in dynamic and fast-paced environments, traits that align 
# well with the ever-evolving field of technology.
# 
# Although my Bachelor's degree in English may seem unrelated, it has sharpened my critical thinking and analytical 
# skills, which are essential in problem-solving and logical reasoning, both foundational elements in computer science. 
# Additionally, my degree has honed my communication abilities, allowing me to effectively convey complex concepts 
# to diverse audiences.
# 
# Despite being a senior applicant, I have a strong motivation to contribute to the field of computer science. 
# With a growing interest in areas such as big data, artificial intelligence, and programming, 
# I am eager to acquire the technical skills and knowledge necessary to engage in meaningful research and innovation. 
# I firmly believe that age should never be a barrier to pursuing one's passions, and I am determined to prove that 
# age can be an asset in terms of experience, wisdom, and a unique perspective.
# 
# Moreover, my life experiences have taught me the value of adaptability, resilience, and a growth mindset. I am 
# prepared to face the challenges and demands of a rigorous Master's program, fully committed to embracing new 
# technologies and pushing the boundaries of my own capabilities.
# 
# In sum, my diverse work experiences, coupled with my Bachelor's degree in English, have paved the way for my decision 
# to pursue a Master's degree in Computer Science. My age only strengthens my resolve to contribute to the field, 
# armed with a lifetime of experiences and a relentless pursuit of knowledge.

```

### Classification

```python title="Binary sentiment classifier"
from slambda.core import UnaryFunction
from slambda import Example, GptApiOptions

sentiment = UnaryFunction.from_instruction(
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
    gpt_opts=GptApiOptions(temperature=0),
)
sentiment("The food is pretty, pretty, pretty, pretty good.")
# Output: positive
```

## Use existing functions

```py

from slambda.contrib.sentiment import sentiment

print(sentiment('the food is great!') == 'positive')
# Output: True
```

See [Functions](/docs/category/builtin-functions) for existing function implementations.

## Project Status

The basic functionalities of this package have been reasonably tested (coverage: 100%), and you should have no problem
creating your own
functions.

Function implementations in `slambda.contrib` should have a reasonable output quality. However, since they are powered
by a language model, you should conduct your own evaluation/testing within your problem domain to ensure that the
model's performance meets your requirements.

We plan to add more functions to `slambda.contrib` and provide a more thorough evaluation report for each function
implementation in the near future.