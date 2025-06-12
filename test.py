import asyncio
import json
from datetime import datetime
from typing import List, Any
from dataclasses import dataclass

# Import Rich components for enhanced UI
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align
from rich.rule import Rule
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.prompt import Prompt

from pydantic_ai import Agent
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel, OpenAIModelName
from pydantic_ai.messages import (
    ModelMessage,
    ToolCallPart,
    ToolReturnPart,
)
from pydantic import BaseModel
# Assuming these tools exist in a 'tools.py' file
from tools import analyze_time_series_kpi, explore_kpi_structure, load_kpi_file, list_kpi_files_by_category, search_kpi_files
# Assuming a 'settings.py' file with an OpenAI API key
from settings import Settings

# --- Enhanced Models ---
class ChatStats(BaseModel):
    total_messages: int = 0
    tools_called: int = 0
    session_start: datetime = datetime.now()

# --- Agent Setup ---
settings = Settings()
# FIX: Using a valid, modern model name to avoid API errors.
chat_model_name: OpenAIModelName = "gpt-4.1" 
chat_model = OpenAIModel(
    model_name=chat_model_name,
    provider=OpenAIProvider(api_key=settings.openai_api_key)
)

@dataclass
class Deps:
    kpi_base_folder: str

try:
    with open("prompts/creative_coupon.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
except FileNotFoundError:
    print("Warning: 'prompts/creative_coupon.txt' not found. Using a default prompt.")
    prompt = "You are a helpful KPI analysis assistant."


agent = Agent(
    model=chat_model,
    system_prompt=prompt,
    tools=[
        explore_kpi_structure,
        list_kpi_files_by_category,
        load_kpi_file,
        search_kpi_files,
        analyze_time_series_kpi
    ],
    deps_type=Deps
)

# Global stats tracker
chat_stats = ChatStats()

def create_header() -> Panel:
    """Create a fancy header panel."""
    # FIX: Updated header to reflect the agent's purpose.
    header_text = Text()
    header_text.append("🤖 ", style="bold blue")
    header_text.append("AI KPI Analysis Agent", style="bold white")
    header_text.append(" 📈", style="bold green")
    
    return Panel(
        Align.center(header_text),
        style="bold blue",
        border_style="bright_blue",
        padding=(1, 2)
    )

def create_stats_panel(stats: ChatStats) -> Panel:
    """Create a statistics panel."""
    table = Table(show_header=False, box=None)
    table.add_column("Metric", style="cyan", width=14)
    table.add_column("Value", style="bright_white")
    
    session_time = datetime.now() - stats.session_start
    
    table.add_row("💬 Messages", str(stats.total_messages))
    table.add_row("🔧 Tools Used", str(stats.tools_called))
    table.add_row("⏱️ Time", f"{session_time.seconds // 60}m {session_time.seconds % 60}s")
    # FIX: Using the dynamic model name variable instead of a hardcoded string.
    table.add_row("🤖 Model", chat_model_name)
    
    return Panel(
        table,
        title="📊 Session Stats",
        border_style="green",
        padding=(0, 1)
    )

def create_help_panel() -> Panel:
    """Create a help panel with available commands."""
    # FIX: Updated help text with relevant examples.
    help_text = Text()
    help_text.append("You can ask me to perform tasks like:\n", style="bold cyan")
    help_text.append("• 'List all kpi files in the sales category'\n", style="white")
    help_text.append("• 'Search for kpis related to revenue'\n", style="white")
    help_text.append("• 'Load the file sales_2023.json and tell me about it'\n", style="white")
    help_text.append("• 'Analyze the time series in regional_growth.json'\n", style="white")
    help_text.append("\nSpecial commands:\n", style="bold cyan")
    help_text.append("• 'help' for this message\n", style="white")
    help_text.append("• 'stats' for session statistics\n", style="white")
    help_text.append("• 'clear' to clear the screen\n", style="white")
    help_text.append("• 'exit' to quit", style="white")
    
    return Panel(
        help_text,
        title="❓ Help / Examples",
        border_style="yellow",
        padding=(1, 2)
    )

async def process_tool_calls(console: Console, result: Any):
    """Process and display tool calls with enhanced visuals."""
    # FIX: This function was rewritten to be functional and generic.
    global chat_stats
    
    for message in result.new_messages():
        for part in message.parts:
            if isinstance(part, ToolCallPart):
                # FIX: Actually incrementing the tool counter.
                chat_stats.tools_called += 1
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True
                ) as progress:
                    progress.add_task(
                        f"🔧 Calling [bold]{part.tool_name}[/bold]...",
                        total=None
                    )
                    await asyncio.sleep(0.5)
            
            elif isinstance(part, ToolReturnPart):
                try:
                    # Try to parse and pretty-print as JSON
                    content_data = json.loads(part.content)
                    pretty_json = json.dumps(content_data, indent=2)
                    console.print(Panel(
                        Syntax(pretty_json, "json", theme="default", word_wrap=True),
                        title="✅ Tool Result",
                        border_style="green",
                        padding=(1, 2),
                        subtitle=f"from {part.tool_name}"
                    ))
                except (json.JSONDecodeError, TypeError):
                    # Fallback for non-JSON or simple string returns
                    console.print(Panel(
                        Text(part.content, overflow="fold"),
                        title="✅ Tool Result",
                        border_style="green",
                        padding=(1, 2),
                        subtitle=f"from {part.tool_name}"
                    ))

async def stream_response(console: Console, result: Any) -> str:
    """Stream the AI response with enhanced formatting."""
    response_text = ""
    
    with Live(console=console, auto_refresh=True, vertical_overflow="visible") as live:
        response_panel = Panel(
            "", title="🤖 Assistant", border_style="bright_magenta", padding=(1, 2)
        )
        live.update(response_panel)
        
        async for message_chunk in result.stream():
            response_text = message_chunk
            content = Markdown(response_text, style="bright_white") if len(response_text) > 3 else Text(response_text)
            response_panel = Panel(
                content, title="🤖 Assistant", border_style="bright_magenta", padding=(1, 2)
            )
            live.update(response_panel)
            
    return response_text

async def main():
    """Enhanced main function with rich UI."""
    global chat_stats
    message_history: List[ModelMessage] = []
    console = Console()
    
    console.clear()
    console.print(create_header())
    console.print()
    console.print(create_help_panel())
    console.print()
    
    while True:
        console.print(Rule(style="dim"))
        user_prompt = Prompt.ask("👤 [bold cyan]You", console=console)
        
        if user_prompt.lower() == "exit":
            console.print(Panel("👋 Thanks for analyzing! Goodbye!", style="bold green", border_style="green"))
            break
        elif user_prompt.lower() == "help":
            console.print(create_help_panel())
            continue
        elif user_prompt.lower() == "stats":
            console.print(create_stats_panel(chat_stats))
            continue
        elif user_prompt.lower() == "clear":
            console.clear()
            console.print(create_header())
            console.print(create_help_panel())
            continue
        
        chat_stats.total_messages += 1
        
        try:

            async with agent.run_stream(
                user_prompt=user_prompt, 
                message_history=message_history,
                deps=Deps(kpi_base_folder="./results")
            ) as result:
                # Process tool calls first
                await process_tool_calls(console, result)
                
                # Then, stream the final text response
                await stream_response(console, result)
                
                # Update message history for the next turn
                message_history = result.all_messages()
            
            # Show updated stats after the response is complete
            console.print()
            console.print(create_stats_panel(chat_stats))
            
        except Exception as e:
            error_panel = Panel(
                f"❌ Error: {str(e)}", title="⚠️ Error", border_style="red", padding=(1, 2)
            )
            console.print(error_panel)
        
        console.print()

if __name__ == "__main__":
    console = Console()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n👋 Chat interrupted. Goodbye!", style="bold yellow")
    except Exception as e:
        console.print(f"\nAn unexpected error occurred: {e}", style="bold red")