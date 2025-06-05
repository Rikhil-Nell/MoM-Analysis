from pydantic_ai import Agent, RunContext
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel, OpenAIModelName, OpenAIModelSettings
from pydantic_ai.messages import ModelMessage, UserPromptPart, TextPart, ModelRequest, ModelResponse
from dataclasses import dataclass
from settings import Settings
from pydantic import BaseModel, Field
import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Dict

settings = Settings()
model_name: OpenAIModelName = "gpt-4.1"
model = OpenAIModel(model_name=model_name, provider=OpenAIProvider(api_key=settings.openai_api_key))
model_settings = OpenAIModelSettings(
    temperature=0.1,
    top_p=0.95
)

@dataclass
class Deps:
    kpi_base_folder: str = "./results"

class Response(BaseModel):
    coupons: str = Field(description="Best Coupons to bring more footfall to the stores")
    reasoning: str = Field(description="Reasoning behind the suggested coupons")
    cost: str = Field(description="How many orders/sales would increase. How much discount they are going to spend")

def explore_kpi_structure(ctx: RunContext[Deps]) -> str:
    st.toast("Starting explore_kpi_structure")
    base_path = Path(ctx.deps.kpi_base_folder)
    st.toast(f"Checking base path: {base_path}")

    if not base_path.exists():
        st.toast("KPI base folder not found")
        return "KPI base folder not found"

    structure = {}

    def scan_directory(path: Path, level: int = 0) -> Dict:
        st.toast(f"Scanning directory: {path}")
        result = {"folders": [], "files": []}
        try:
            for item in path.iterdir():
                if item.is_dir():
                    st.toast(f"Found folder: {item.name}")
                    result["folders"].append({
                        "name": item.name,
                        "content": scan_directory(item, level + 1)
                    })
                elif item.suffix.lower() == '.csv':
                    st.toast(f"Found CSV file: {item.name}")
                    result["files"].append(item.name)
        except PermissionError:
            st.toast(f"PermissionError accessing: {path}")
            pass
        return result

    structure = scan_directory(base_path)

    def format_structure(struct: Dict, level: int = 0) -> str:
        output = []
        indent = "  " * level
        for folder in struct["folders"]:
            output.append(f"{indent}📁 {folder['name']}/")
            output.append(format_structure(folder["content"], level + 1))
        for file in struct["files"]:
            output.append(f"{indent}📄 {file}")
        return "\n".join(output)

    st.toast("Completed scanning KPI folder structure")
    return f"KPI Folder Structure:\n{format_structure(structure)}"

def list_kpi_files_by_category(ctx: RunContext[Deps], category: str, subcategory: str = None) -> str:
    st.toast(f"Listing KPI files for category: {category}, subcategory: {subcategory}")
    base_path = Path(ctx.deps.kpi_base_folder)

    if subcategory:
        target_path = base_path / category / subcategory
    else:
        target_path = base_path / category

    st.toast(f"Target path: {target_path}")

    if not target_path.exists():
        st.toast(f"Path not found: {target_path}")
        return f"Path {target_path} not found"

    csv_files = list(target_path.glob("*.csv"))

    if not csv_files:
        st.toast(f"No CSV files found in: {target_path}")
        return f"No CSV files found in {target_path}"

    file_info = []
    for file in csv_files:
        try:
            stat = file.stat()
            size_mb = stat.st_size / (1024 * 1024)
            st.toast(f"File found: {file.name}, size: {size_mb:.2f} MB")
            file_info.append(f"  📄 {file.name} ({size_mb:.2f} MB)")
        except Exception as e:
            st.toast(f"Error accessing file info for {file.name}: {str(e)}")
            file_info.append(f"  📄 {file.name}")

    st.toast("Completed listing files")
    return f"Files in {category}" + (f"/{subcategory}" if subcategory else "") + f":\n" + "\n".join(file_info)

def load_kpi_file(ctx: RunContext[Deps], category: str, filename: str, subcategory: str = None) -> str:
    st.toast(f"Loading KPI file: {filename} in category: {category}, subcategory: {subcategory}")
    base_path = Path(ctx.deps.kpi_base_folder)

    if subcategory:
        filepath = base_path / category / subcategory / filename
    else:
        filepath = base_path / category / filename

    st.toast(f"Filepath resolved to: {filepath}")

    if not filepath.exists():
        st.toast(f"File not found: {filepath}")
        return f"File not found: {filepath}"

    try:
        df = pd.read_csv(filepath)
        st.toast(f"Loaded file successfully with shape {df.shape}")

        summary = f"""
📊 KPI File Analysis
Path: {category}{'/' + subcategory if subcategory else ''}/{filename}
Shape: {df.shape[0]} rows, {df.shape[1]} columns
Columns: {', '.join(df.columns.tolist())}

📋 First 5 rows:
{df.head().to_string()}

📈 Basic Statistics:
{df.describe().to_string()}

🔍 Data Info:
{df.info(buf=None)}
        """
        st.toast("Completed KPI file analysis")
        return summary
    except Exception as e:
        st.toast(f"Error loading file: {str(e)}")
        return f"Error loading file: {str(e)}"

def search_kpi_files(ctx: RunContext[Deps], search_term: str) -> str:
    st.toast(f"Searching KPI files with term: '{search_term}'")
    base_path = Path(ctx.deps.kpi_base_folder)

    if not base_path.exists():
        st.toast("KPI base folder not found")
        return "KPI base folder not found"

    matches = []

    def search_recursive(path: Path, current_path: str = ""):
        st.toast(f"Searching in: {path}")
        try:
            for item in path.iterdir():
                if item.is_dir():
                    new_path = f"{current_path}/{item.name}" if current_path else item.name
                    search_recursive(item, new_path)
                elif item.suffix.lower() == '.csv' and search_term.lower() in item.name.lower():
                    st.toast(f"Match found: {item.name} in {current_path}")
                    matches.append(f"{current_path}/{item.name}" if current_path else item.name)
        except PermissionError:
            st.toast(f"Permission denied: {path}")
            pass

    search_recursive(base_path)

    if not matches:
        st.toast(f"No files found matching '{search_term}'")
        return f"No files found matching '{search_term}'"

    st.toast(f"Found {len(matches)} matching files")
    return f"Files matching '{search_term}':\n" + "\n".join([f"  📄 {match}" for match in matches])

def analyze_time_series_kpi(ctx: RunContext[Deps], category: str, time_period: str, filename: str) -> str:
    st.toast(f"Analyzing time series KPI: {category}/{time_period}/{filename}")
    base_path = Path(ctx.deps.kpi_base_folder)
    filepath = base_path / category / time_period / filename

    st.toast(f"Filepath: {filepath}")

    if not filepath.exists():
        st.toast(f"File not found: {filepath}")
        return f"File not found: {filepath}"

    try:
        df = pd.read_csv(filepath)
        st.toast(f"Loaded file with shape {df.shape}")

        date_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['date', 'time', 'timestamp', 'day', 'month', 'year', 'hour'])]
        st.toast(f"Date/time columns detected: {date_cols if date_cols else 'None'}")

        analysis = f"""
⏰ Time Series Analysis: {category}/{time_period}/{filename}
Shape: {df.shape[0]} rows, {df.shape[1]} columns

📅 Potential date/time columns: {', '.join(date_cols) if date_cols else 'None detected'}

📊 Summary Statistics:
{df.describe().to_string()}
        """

        if date_cols:
            for col in date_cols[:1]:
                try:
                    df[col] = pd.to_datetime(df[col])
                    analysis += f"\n\n📈 Time range for {col}: {df[col].min()} to {df[col].max()}"
                    st.toast(f"Time range for {col}: {df[col].min()} to {df[col].max()}")
                except Exception as e:
                    st.toast(f"Error parsing datetime for column {col}: {str(e)}")

        st.toast("Completed time series analysis")
        return analysis
    except Exception as e:
        st.toast(f"Error analyzing time series data: {str(e)}")
        return f"Error analyzing time series data: {str(e)}"

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

