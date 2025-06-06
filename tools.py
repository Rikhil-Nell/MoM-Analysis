import pandas as pd
import streamlit as st
from pathlib import Path
from pydantic_ai import RunContext
from typing import Dict
from dataclasses import dataclass
from rich.logging import RichHandler
import logging

# Rich logger setup
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(markup=True)]
)
logger = logging.getLogger("kpi-tools")

@dataclass
class Deps:
    kpi_base_folder: str = "./results"

async def explore_kpi_structure(ctx: RunContext[Deps]) -> str:
    st.toast("Starting explore_kpi_structure")
    logger.info("[cyan]Starting explore_kpi_structure[/cyan]")

    base_path = Path(ctx.deps.kpi_base_folder)
    st.toast(f"Checking base path: {base_path}")
    logger.info(f"[magenta]Checking base path:[/magenta] {base_path}")

    if not base_path.exists():
        st.toast("KPI base folder not found")
        logger.warning("[red]KPI base folder not found[/red]")
        return "KPI base folder not found"

    def scan_directory(path: Path, level: int = 0) -> Dict:
        st.toast(f"Scanning directory: {path}")
        logger.info(f"[blue]Scanning directory:[/blue] {path}")
        result = {"folders": [], "files": []}
        try:
            for item in path.iterdir():
                if item.is_dir():
                    st.toast(f"Found folder: {item.name}")
                    logger.info(f"📁 Found folder: {item.name}")
                    result["folders"].append({
                        "name": item.name,
                        "content": scan_directory(item, level + 1)
                    })
                elif item.suffix.lower() == '.csv':
                    st.toast(f"Found CSV file: {item.name}")
                    logger.info(f"📄 Found CSV file: {item.name}")
                    result["files"].append(item.name)
        except PermissionError:
            st.toast(f"PermissionError accessing: {path}")
            logger.warning(f"[yellow]PermissionError accessing:[/yellow] {path}")
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
    logger.info("[green]Completed scanning KPI folder structure[/green]")
    return f"KPI Folder Structure:\n{format_structure(structure)}"


async def list_kpi_files_by_category(ctx: RunContext[Deps], category: str, subcategory: str = None) -> str:
    st.toast(f"Listing KPI files for category: {category}, subcategory: {subcategory}")
    logger.info(f"[cyan]Listing KPI files:[/cyan] category={category}, subcategory={subcategory}")

    base_path = Path(ctx.deps.kpi_base_folder)
    target_path = base_path / category / subcategory if subcategory else base_path / category

    st.toast(f"Target path: {target_path}")
    logger.info(f"[magenta]Target path:[/magenta] {target_path}")

    if not target_path.exists():
        st.toast(f"Path not found: {target_path}")
        logger.warning(f"[red]Path not found:[/red] {target_path}")
        return f"Path {target_path} not found"

    csv_files = list(target_path.glob("*.csv"))

    if not csv_files:
        st.toast(f"No CSV files found in: {target_path}")
        logger.info(f"[yellow]No CSV files found in:[/yellow] {target_path}")
        return f"No CSV files found in {target_path}"

    file_info = []
    for file in csv_files:
        try:
            stat = file.stat()
            size_mb = stat.st_size / (1024 * 1024)
            st.toast(f"File found: {file.name}, size: {size_mb:.2f} MB")
            logger.info(f"📄 {file.name} ({size_mb:.2f} MB)")
            file_info.append(f"  📄 {file.name} ({size_mb:.2f} MB)")
        except Exception as e:
            st.toast(f"Error accessing file info for {file.name}: {str(e)}")
            logger.error(f"[red]Error accessing file info for {file.name}:[/red] {e}")
            file_info.append(f"  📄 {file.name}")

    st.toast("Completed listing files")
    logger.info("[green]Completed listing files[/green]")
    return f"Files in {category}" + (f"/{subcategory}" if subcategory else "") + f":\n" + "\n".join(file_info)


async def load_kpi_file(ctx: RunContext[Deps], category: str, filename: str, subcategory: str = None) -> str:
    st.toast(f"Loading KPI file: {filename} in category: {category}, subcategory: {subcategory}")
    logger.info(f"[cyan]Loading KPI file:[/cyan] {filename} from {category}/{subcategory or ''}")

    base_path = Path(ctx.deps.kpi_base_folder)
    filepath = base_path / category / subcategory / filename if subcategory else base_path / category / filename

    st.toast(f"Filepath resolved to: {filepath}")
    logger.info(f"[magenta]Resolved filepath:[/magenta] {filepath}")

    if not filepath.exists():
        st.toast(f"File not found: {filepath}")
        logger.warning(f"[red]File not found:[/red] {filepath}")
        return f"File not found: {filepath}"

    try:
        df = pd.read_csv(filepath)
        st.toast(f"Loaded file successfully with shape {df.shape}")
        logger.info(f"📊 Loaded file: {df.shape[0]} rows x {df.shape[1]} cols")

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
        logger.info("[green]Completed KPI file analysis[/green]")
        return summary
    except Exception as e:
        st.toast(f"Error loading file: {str(e)}")
        logger.error(f"[red]Error loading file:[/red] {e}")
        return f"Error loading file: {str(e)}"


async def search_kpi_files(ctx: RunContext[Deps], search_term: str) -> str:
    st.toast(f"Searching KPI files with term: '{search_term}'")
    logger.info(f"[cyan]Searching KPI files for:[/cyan] {search_term}")

    base_path = Path(ctx.deps.kpi_base_folder)
    if not base_path.exists():
        st.toast("KPI base folder not found")
        logger.warning("[red]KPI base folder not found[/red]")
        return "KPI base folder not found"

    matches = []

    def search_recursive(path: Path, current_path: str = ""):
        st.toast(f"Searching in: {path}")
        logger.info(f"[blue]Searching in:[/blue] {path}")
        try:
            for item in path.iterdir():
                if item.is_dir():
                    new_path = f"{current_path}/{item.name}" if current_path else item.name
                    search_recursive(item, new_path)
                elif item.suffix.lower() == '.csv' and search_term.lower() in item.name.lower():
                    st.toast(f"Match found: {item.name} in {current_path}")
                    logger.info(f"✅ Match: {current_path}/{item.name}")
                    matches.append(f"{current_path}/{item.name}" if current_path else item.name)
        except PermissionError:
            st.toast(f"Permission denied: {path}")
            logger.warning(f"[yellow]Permission denied:[/yellow] {path}")

    search_recursive(base_path)

    if not matches:
        st.toast(f"No files found matching '{search_term}'")
        logger.info(f"[yellow]No matches for:[/yellow] {search_term}")
        return f"No files found matching '{search_term}'"

    st.toast(f"Found {len(matches)} matching files")
    logger.info(f"[green]Found {len(matches)} matching files[/green]")
    return f"Files matching '{search_term}':\n" + "\n".join([f"  📄 {match}" for match in matches])


async def analyze_time_series_kpi(ctx: RunContext[Deps], category: str, time_period: str, filename: str) -> str:
    st.toast(f"Analyzing time series KPI: {category}/{time_period}/{filename}")
    logger.info(f"[cyan]Analyzing time series KPI:[/cyan] {category}/{time_period}/{filename}")

    base_path = Path(ctx.deps.kpi_base_folder)
    filepath = base_path / category / time_period / filename

    st.toast(f"Filepath: {filepath}")
    logger.info(f"[magenta]Resolved filepath:[/magenta] {filepath}")

    if not filepath.exists():
        st.toast(f"File not found: {filepath}")
        logger.warning(f"[red]File not found:[/red] {filepath}")
        return f"File not found: {filepath}"

    try:
        df = pd.read_csv(filepath)
        st.toast(f"Loaded file with shape {df.shape}")
        logger.info(f"📊 Loaded file: {df.shape[0]} rows x {df.shape[1]} cols")

        date_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['date', 'time', 'timestamp', 'day', 'month', 'year', 'hour'])]
        st.toast(f"Date/time columns detected: {date_cols if date_cols else 'None'}")
        logger.info(f"[blue]Date/time columns:[/blue] {date_cols if date_cols else 'None detected'}")

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
                    logger.info(f"[green]Time range for {col}:[/green] {df[col].min()} to {df[col].max()}")
                except Exception as e:
                    st.toast(f"Error parsing datetime for column {col}: {str(e)}")
                    logger.warning(f"[red]Error parsing datetime for {col}:[/red] {e}")

        st.toast("Completed time series analysis")
        logger.info("[green]Completed time series analysis[/green]")
        return analysis
    except Exception as e:
        st.toast(f"Error analyzing time series data: {str(e)}")
        logger.error(f"[red]Error analyzing time series data:[/red] {e}")
        return f"Error analyzing time series data: {str(e)}"
