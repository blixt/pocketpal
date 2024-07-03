import os

from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(name="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))


async def openai_prompt(prompt: str) -> str:
    messages = [HumanMessage(content=prompt)]
    response = await llm.ainvoke(messages)
    return response.content
