from pydantic_ai import Agent
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel, OpenAIModelName, OpenAIModelSettings
from pydantic_ai.messages import ModelMessage, UserPromptPart, TextPart, ModelRequest, ModelResponse
from tools import *
from settings import Settings
from pydantic import BaseModel, Field

settings = Settings()
model_name: OpenAIModelName = "gpt-4.1"
model = OpenAIModel(model_name=model_name, provider=OpenAIProvider(api_key=settings.openai_api_key))
model_settings = OpenAIModelSettings(
    temperature=0.1,
    top_p=0.95
)


class Response(BaseModel):
    coupons: str = Field(description="Best Coupons to bring more footfall to the stores")
    reasoning: str = Field(description="Reasoning behind the suggested coupons")
    cost: str = Field(description="How many orders/sales would increase. How much discount they are going to spend")
    conversation : str = Field(description="Use this field to respond normally if none other fields fit for the answer")

with open("prompts/prompt.txt", "r", encoding="utf-8") as f:
    prompt = f.read()

agent = Agent(
    model=model,
    model_settings=model_settings,
    system_prompt=prompt,
    output_type=Response,
    tools=[
        explore_kpi_structure,
        list_kpi_files_by_category,
        load_kpi_file,
        search_kpi_files,
        analyze_time_series_kpi
    ]
)

messages: list[ModelMessage] = []

if __name__ == "__main__":
    deps = Deps(kpi_base_folder="./results")  # Set your KPI base folder path
    
    while True:
        user_prompt = input("You: ")
        
        if user_prompt == "exit":
            break
        
        result = agent.run_sync(user_prompt=user_prompt, message_history=messages, deps=deps)
        
        print("Clink: " + str(result.output))
        messages.append(ModelRequest(parts=[UserPromptPart(content=user_prompt)]))
        messages.append(ModelResponse(parts=[TextPart(content=str(result.output))]))

