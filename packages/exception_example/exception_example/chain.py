import json
from typing import Dict
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from fastapi import HTTPException

load_dotenv()

model = ChatOpenAI(model="gpt-3.5-turbo")

class FruitModel(BaseModel):
    shape: str = Field(
        ...,
        description="The shape of the fruit",
    )
    color: str = Field(
        ...,
        description="The color of the fruit",
    )
    taste: str = Field(
        ...,
        description="The taste of the fruit"
    )

template = "You are describing a {fruit}. Please provide the name, shape, and color of the fruit as per the {format_instructions}."

parser = JsonOutputParser(pydantic_object=FruitModel)   

def post_process_result(result):
    result = json.loads(f"result")
    if not result["is_fruit"]:
        raise HTTPException(status_code=400, detail="The object is not a fruit.")
    else:
        return result

prompt=PromptTemplate(
    template=template,
    input_variables=["fruit"],
    partial_variables={
        "format_instructions": parser.get_format_instructions()
    }
)

def is_input_numeric(input):
    return {
        "input": input,
        "result": input.isnumeric()
    }

# if you update this, you MUST also update ../pyproject.toml
# with the new `tool.langserve.export_attr`
chain = RunnableLambda(is_input_numeric).with_types(input_type=str, output_type=Dict) | RunnableLambda(
    lambda x: HTTPException(
        status_code=422,
        detail=f"{x['input']} is not string."
    ) if x["result"] else RunnableLambda(
        lambda x: x["input"]
     ).with_types(
         output_type = str
     ) | prompt | model | parser
)