from langchain.tools import BaseTool
from typing import Union
import requests
import os
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from langchain.chat_models import ChatOpenAI
from langchain.chains.conversation.memory import ConversationBufferWindowMemory

from dotenv import load_dotenv
load_dotenv()
ninja_api_key = os.getenv("NINJA_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

class NutriInfoTool(BaseTool):
    name = "NutriInfoTool"
    description = "Use this tool to fetch the nutritional information for a specific food item."

    def _run(self, food: str):
        api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(food)
        response = requests.get(api_url, timeout=100, headers={'X-Api-Key': ninja_api_key})

        if response.status_code == requests.codes.ok:
            return response.json()  # Use json instead of text for a more structured data
        else:
            return {"Error": response.status_code, "Message": response.text}

    def _arun(self, food: str):
        raise NotImplementedError("This tool does not support async.")

class BMITool(BaseTool):
    name = "BMITool"
    description = "Use this tool to calculate the body mass index(BMI) of a person when his height and weight is given."

    def _run(self, input: str):
        weight, height = input.split(',')
        weight = float(weight)
        height = float(height)
        height_m = height / 100
        bmi = weight / (height_m*height_m)
        return round(bmi, 2)

    def _arun(self, food: str):
        raise NotImplementedError("This tool does not support async.")

class CCLW(BaseTool):
    name = "CCLW"
    description = "Use this tool to calculate the number of calories required to lose a certain amount of weight"

    def _run(self, weight_loss_amount: str):
        weight_loss_amount = float(weight_loss_amount)
        calories_per_kg_fat = 7700  # Approximate number of calories in a kg of body fat
        weight = weight_loss_amount * calories_per_kg_fat
        return weight

    def _arun(self, food: str):
        raise NotImplementedError("This tool does not support async.")

def load_agent():
    multi_tools = [NutriInfoTool(), BMITool(), CCLW()]
    prompt = hub.pull("hwchase17/openai-tools-agent")

    llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)
    agent = create_openai_tools_agent(llm, multi_tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=multi_tools, verbose=True, max_iterations=5)
    return agent_executor