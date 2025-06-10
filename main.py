from pydantic_ai import Agent
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel, OpenAIModelName, OpenAIModelSettings
from pydantic_ai.messages import ModelMessage, UserPromptPart, TextPart, ModelRequest, ModelResponse
from tools import *
from settings import Settings
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
import logfire

settings = Settings()

logfire.configure(token=settings.logfire_key)

model_name: OpenAIModelName = "gpt-4.1"

openai_client = AsyncOpenAI(api_key=settings.openai_api_key)

logfire.instrument_openai(openai_client=openai_client)

model = OpenAIModel(model_name=model_name, provider=OpenAIProvider(openai_client=openai_client))

model_settings = OpenAIModelSettings(
    temperature=0.1,
    top_p=0.95
)

class StandardResponse(BaseModel):
    # joining bonus coupon
    joining_bonus_coupon : str = Field(description="Best Joining Bonus Coupon to bring more footfall to the stores")
    joining_bonus_coupon_reasoning : str = Field(description="Best Joining Bonus Coupon to bring more footfall to the stores")
    joining_bonus_coupon_cost_analysis : str = Field(description="Analyze the cost of the joining bonus coupon, like 'How many orders/sales would increase?','How much discount they are going to spend?'")
    # stamp card coupon
    stamp_card_coupon : str = Field(description="Best Stamp Card Coupon to bring more footfall to the stores")
    stamp_card_coupon_reasoning : str = Field(description="Reasoning behind the suggested stamp card coupon")
    stamp_card_coupon_cost_analysis : str = Field(description="Analyze the cost of the stamp card coupon, like 'How many orders/sales would increase?','How much discount they are going to spend?'")
    # miss you coupon
    miss_you_coupon : str = Field(description="Best Miss You Coupon to bring more footfall to the stores")
    miss_you_coupon_reasoning : str = Field(description="Reasoning behind the suggested miss you coupon")
    miss_you_coupon_cost_analysis : str = Field(description="Analyze the cost of the miss you coupon, like 'How many orders/sales would increase?','How much discount they are going to spend?'")
    # combined cost analysis
    combined_cost_analysis : str = Field(description="Analyze the cost of all the coupons, like 'How many orders/sales would increase?','How much discount they are going to spend?'")

with open("prompts/standard_coupon.txt", "r", encoding="utf-8") as f:
    prompt = f.read()

standard_coupon_agent = Agent(
    model=model,
    model_settings=model_settings,
    output_type=StandardResponse,
    system_prompt=prompt,
    tools=[
        explore_kpi_structure,
        list_kpi_files_by_category,
        load_kpi_file,
        search_kpi_files,
        analyze_time_series_kpi
    ]
)

logfire.instrument_pydantic_ai(standard_coupon_agent)

class CreativeResponse(BaseModel):
    coupons: str = Field(description="Best Coupons to bring more footfall to the stores")
    reasoning: str = Field(description="Reasoning behind the suggested coupons")
    cost: str = Field(description="How many orders/sales would increase. How much discount they are going to spend")
    conversation : str = Field(description="Use this field to respond normally if none other fields fit for the answer")

with open("prompts/creative_coupon.txt", "r", encoding="utf-8") as f:
    prompt = f.read()

creative_coupon_agent = Agent(
    model=model,
    model_settings=model_settings,
    system_prompt=prompt,
    output_type=CreativeResponse,
    tools=[
        explore_kpi_structure,
        list_kpi_files_by_category,
        load_kpi_file,
        search_kpi_files,
        analyze_time_series_kpi
    ]
)

logfire.instrument_pydantic_ai(creative_coupon_agent)

messages: list[ModelMessage] = []

