import os
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage


llm = ChatOpenAI(model_name="gpt-4", openai_api_key=os.getenv("OPENAI_API_KEY"))


async def openai_prompt(prompt: str) -> str:
    messages = [HumanMessage(content=prompt)]
    response = await llm.ainvoke(messages)
    return response.content
