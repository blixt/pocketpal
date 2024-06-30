import os
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage


async def openai_prompt(prompt: str) -> str:
    chat = ChatOpenAI(model_name="gpt-4", openai_api_key=os.getenv("OPENAI_API_KEY"))
    messages = [HumanMessage(content=prompt)]
    response = await chat.ainvoke(messages)
    return response.content
