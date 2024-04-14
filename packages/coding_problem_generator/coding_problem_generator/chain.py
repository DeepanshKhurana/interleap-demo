# Add langchain debug
from typing import Any, List

from langchain.globals import set_debug, set_verbose
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI

set_debug(True)
set_verbose(False)

model = ChatOpenAI(
    temperature=0.7,
    api_key="sk-...",
    # model="gpt-4"
)


class Example(BaseModel):
    input: Any
    output: Any
    explanation: str


class Problem(BaseModel):
    problem_statement: str = Field(
        ..., description="Detailed explanation of the programming problem requirement."
    )
    function_signature: str = Field(
        ..., description="Function signature that the user will implement."
    )
    unit_tests: List[Example] = Field(
        ...,
        description="List of atleast 5 parameterised unit tests (along corner cases) ensuring correctness and reliability of the solution.",
    )
    constraints: List[str] = Field(
        ..., description="Set of constraints applicable on the problem."
    )
    sample_solution: str = Field(
        ...,
        description="Working solution that follows coding best practices, implemented in the specified language/framework.",
    )
    incomplete_solution: str = Field(
        ...,
        description="Partially working solution with logical errors or parts to be filled in, implemented in the specified language/framework.",
    )


class ProblemList(BaseModel):
    problems: List[Problem]


parser = JsonOutputParser(pydantic_object=ProblemList)

prompt = PromptTemplate(
    template="""You are a professor of Computer Science in MIT, and you are responsible for generating unique competitive coding problems applicable to language/framework mentioned below based on the topics provided from the textbook. The problem should be independent and solvable on it's own. The problem should be able to test the understanding of the candidate on all of these topics. Always try to create real world problems that can be solved using the concepts based on the topics mentioned below. Create 5 problems.

Language: {language}
Level: {difficulty_level}
Topics: {topics}

{format_instructions}

New Problem:""",
    input_variables=["language", "difficulty_level", "topics"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)


sub_chain = prompt | model | parser


def wrap(input):
    return sub_chain.invoke(input)


chain = RunnableLambda(wrap).with_types(
    input_type=sub_chain.get_input_schema(),
    output_type=sub_chain.get_output_schema(),
)
