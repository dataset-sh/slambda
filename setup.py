#!/usr/bin/env python

from distutils.core import setup

REQUIRES = [
    "pydantic >= 2.0.0",
    "openai"
]

description = """
sLambda, a simple wrapper for OpenAI's chat model APIs (chatgpt).
""".strip()

setup(
    name='slambda',
    version='0.0.1',
    description=description,
    author='Hao Wu',
    author_email='haowu@dataset.sh',
    url='https://slambda.dataset.sh',
    packages=['slambda'],
    install_requires=REQUIRES
)
