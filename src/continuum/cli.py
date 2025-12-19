"""CLI for Continuum - portable context for Claude."""

from datetime import datetime
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# Load .env from current directory and ~/.continuum/
load_dotenv()  # Current directory
load_dotenv(Path.home() / ".continuum" / ".env")  # User's continuum directory

from . import __version__
from .config import Config, get_default_base_path
from .export import generate_export, write_export
from .files import (
    count_memory_entries,
    extract_current_focus,
    get_file_age_str,
    get_last_export_time,
    init_directory,
    init_project,
    is_stale,
    open_in_editor,
)
from .voice import analyze_voice, generate_voice_md

console = Console()


@click.group()
@click.version_option(version=__version__)
def cli():
    """Continuum - portable context for Claude.

    Own your memory, voice, and identity across all Claude interfaces.
    """
    pass


@cli.command()
@click.option(
    "--path",
    type=click.Path(),
    default=None,
    help="Custom path for Continuum directory (default: ~/.continuum)",
)
@click.option("--project", is_flag=True, help="Initialize project-level .continuum/ in current directory")
@click.option("--force", is_flag=True, help="Overwrite existing files")
def init(path: str | None, project: bool, force: bool):
    """Initialize Continuum directory structure.

    Without --project: creates ~/.continuum/ (global context)
    With --project: creates .continuum/ in project root (project-specific context)
    """
    if project:
        # Project-level initialization
        from .config import find_project_root

        project_root = find_project_root()
        if project_root is None:
            project_root = Path.cwd()

        continuum_dir = project_root / ".continuum"

        if continuum_dir.exists() and not force:
            if not click.confirm(f"{continuum_dir} exists. Continue?"):
                return

        console.print(f"Creating project context in {continuum_dir}...", style="dim")
        actions = init_project(project_root, force=force)

        for action in actions:
            if "Created" in action:
                console.print(f"  [green]{action}[/green]")
            else:
                console.print(f"  [dim]{action}[/dim]")

        console.print()
        console.print("[bold]Next steps:[/bold]")
        console.print("  1. Run [cyan]continuum edit context --project[/cyan] to add project details")
        console.print("  2. Run [cyan]continuum status[/cyan] to see merged context")
        console.print("  3. Run [cyan]continuum export[/cyan] to export with project context")
    else:
        # Global initialization
        base_path = Path(path).expanduser() if path else get_default_base_path()

        if base_path.exists() and not force:
            if not click.confirm(f"{base_path} exists. Continue?"):
                return

        console.print(f"Creating {base_path}...", style="dim")
        actions = init_directory(base_path, force=force)

        for action in actions:
            if "Created" in action:
                console.print(f"  [green]{action}[/green]")
            else:
                console.print(f"  [dim]{action}[/dim]")

        console.print()
        console.print("[bold]Next steps:[/bold]")
        console.print("  1. Run [cyan]continuum edit identity[/cyan] to add your information")
        console.print("  2. Run [cyan]continuum edit voice[/cyan] to define your style")
        console.print("  3. Run [cyan]continuum export[/cyan] to generate context for Claude Code")


@cli.command()
@click.argument("file", type=click.Choice(["identity", "voice", "context", "memory"]))
@click.option("--path", type=click.Path(), default=None, help="Custom Continuum directory")
@click.option("--project", is_flag=True, help="Edit project-level file instead of global")
def edit(file: str, path: str | None, project: bool):
    """Open a context file in your editor.

    Without --project: edits ~/.continuum/<file>.md
    With --project: edits .continuum/<file>.md in project root
    """
    base_path = Path(path).expanduser() if path else get_default_base_path()
    config = Config.load(base_path)

    if project:
        if not config.has_project:
            console.print("[red]No project context found.[/red]")
            console.print("Run [cyan]continuum init --project[/cyan] first.")
            return

        # Map to project paths
        project_file_map = {
            "identity": config.project_path / "identity.md",
            "voice": config.project_path / "voice.md",
            "context": config.project_path / "context.md",
            "memory": config.project_path / "memory.md",
        }
        target_path = project_file_map[file]

        # Create if doesn't exist (for identity/voice which aren't created by default)
        if not target_path.exists():
            if file in ("identity", "voice"):
                console.print(f"[dim]Creating {target_path}...[/dim]")
                target_path.write_text(f"# Project {file.title()}\n\n")
            else:
                console.print(f"[red]{target_path} does not exist.[/red]")
                return
    else:
        file_map = {
            "identity": config.identity_path,
            "voice": config.voice_path,
            "context": config.context_path,
            "memory": config.memory_path,
        }
        target_path = file_map[file]

        if not target_path.exists():
            console.print(f"[red]{target_path} does not exist.[/red]")
            console.print("Run [cyan]continuum init[/cyan] first.")
            return

    if open_in_editor(target_path):
        console.print(f"[dim]Updated: {target_path}[/dim]")
    else:
        console.print(f"[red]Could not open editor. Edit manually: {target_path}[/red]")


@cli.command()
@click.option("--path", type=click.Path(), default=None, help="Custom Continuum directory")
def status(path: str | None):
    """Show current context status."""
    base_path = Path(path).expanduser() if path else get_default_base_path()

    if not base_path.exists():
        console.print("[red]Continuum not initialized.[/red]")
        console.print("Run [cyan]continuum init[/cyan] to get started.")
        return

    config = Config.load(base_path)

    # Build global file status table
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("File", style="bold")
    table.add_column("Status")
    table.add_column("Age")

    files = [
        ("identity.md", config.identity_path),
        ("voice.md", config.voice_path),
        ("context.md", config.context_path),
        ("memory.md", config.memory_path),
    ]

    for name, filepath in files:
        if filepath.exists():
            stale = is_stale(filepath, config.stale_days)
            status_icon = "[yellow]![/yellow]" if stale else "[green]ok[/green]"
            age = get_file_age_str(filepath)
            if stale:
                age = f"[yellow]{age} (stale?)[/yellow]"
            table.add_row(name, status_icon, age)
        else:
            table.add_row(name, "[red]x[/red]", "[red]missing[/red]")

    # Memory count
    memory_count = count_memory_entries(config.memory_path)

    # Current focus
    focus = extract_current_focus(config.context_path)

    # Last export
    last_export = get_last_export_time(config.exports_path)
    export_str = (
        last_export.strftime("%Y-%m-%d") if last_export else "never"
    )

    # Print global status
    console.print()
    console.print(f"[bold blue]Continuum[/bold blue] [dim]{base_path}[/dim]")
    console.print()
    console.print(table)

    # Print additional info
    console.print()
    if focus:
        console.print(f"[bold]Focus:[/bold] {focus}")
    if memory_count:
        console.print(f"[bold]Memories:[/bold] {memory_count} entries")
    console.print(f"[bold]Last export:[/bold] {export_str}")

    # Show project context if present
    if config.has_project:
        console.print()
        console.print(f"[bold cyan]Project[/bold cyan] [dim]{config.project_path}[/dim]")
        console.print()

        project_table = Table(show_header=False, box=None, padding=(0, 2))
        project_table.add_column("File", style="bold")
        project_table.add_column("Status")
        project_table.add_column("Age")

        project_files = [
            ("context.md", config.project_context_path),
            ("memory.md", config.project_memory_path),
        ]

        for name, filepath in project_files:
            if filepath and filepath.exists():
                stale = is_stale(filepath, config.stale_days)
                status_icon = "[yellow]![/yellow]" if stale else "[green]ok[/green]"
                age = get_file_age_str(filepath)
                if stale:
                    age = f"[yellow]{age} (stale?)[/yellow]"
                project_table.add_row(name, status_icon, age)
            else:
                project_table.add_row(name, "[dim]-[/dim]", "[dim]not set[/dim]")

        console.print(project_table)

        # Project focus
        if config.project_context_path:
            project_focus = extract_current_focus(config.project_context_path)
            if project_focus:
                console.print()
                console.print(f"[bold]Project focus:[/bold] {project_focus}")

        # Project memory count
        if config.project_memory_path:
            project_memory_count = count_memory_entries(config.project_memory_path)
            if project_memory_count:
                console.print(f"[bold]Project memories:[/bold] {project_memory_count} entries")


@cli.command()
@click.argument("text")
@click.option(
    "--category",
    "-c",
    type=click.Choice(["fact", "decision", "lesson", "preference"]),
    default=None,
    help="Memory category (auto-detected if not specified)",
)
@click.option("--path", type=click.Path(), default=None, help="Custom Continuum directory")
@click.option("--project", is_flag=True, help="Add to project memory instead of global")
def remember(text: str, category: str | None, path: str | None, project: bool):
    """Add a memory entry.

    Without --project: adds to ~/.continuum/memory.md
    With --project: adds to .continuum/memory.md in project root
    """
    base_path = Path(path).expanduser() if path else get_default_base_path()
    config = Config.load(base_path)

    if project:
        if not config.has_project:
            console.print("[red]No project context found.[/red]")
            console.print("Run [cyan]continuum init --project[/cyan] first.")
            return
        memory_path = config.project_path / "memory.md"
        label = "project memory"
    else:
        memory_path = config.memory_path
        label = "memory.md"

    if not memory_path.exists():
        console.print(f"[red]{memory_path} not found.[/red]")
        if project:
            console.print("Run [cyan]continuum init --project[/cyan] first.")
        else:
            console.print("Run [cyan]continuum init[/cyan] first.")
        return

    # Auto-detect category if not specified
    if category is None:
        category = auto_detect_category(text)

    # Format entry
    date = datetime.now().strftime("%Y-%m-%d")
    entry = f"[{date}] {category.upper()} - {text}"

    # Append to memory.md
    with open(memory_path, "a") as f:
        f.write(f"\n{entry}")

    console.print(f"[green]Added to {label}:[/green]")
    console.print(f"  {entry}")


def auto_detect_category(text: str) -> str:
    """Infer category from text content."""
    text_lower = text.lower()

    decision_keywords = ["decided", "chose", "picked", "selected", "going with", "went with"]
    lesson_keywords = ["learned", "realized", "discovered", "found out", "turns out"]
    preference_keywords = ["prefer", "like", "want", "always", "never", "don't like"]

    if any(w in text_lower for w in decision_keywords):
        return "decision"
    elif any(w in text_lower for w in lesson_keywords):
        return "lesson"
    elif any(w in text_lower for w in preference_keywords):
        return "preference"

    return "fact"


@cli.command("export")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--stdout", is_flag=True, help="Print to stdout instead of file")
@click.option("--path", type=click.Path(), default=None, help="Custom Continuum directory")
def export_cmd(output: str | None, stdout: bool, path: str | None):
    """Export context for Claude Code."""
    base_path = Path(path).expanduser() if path else get_default_base_path()

    if not base_path.exists():
        console.print("[red]Continuum not initialized.[/red]")
        console.print("Run [cyan]continuum init[/cyan] first.")
        return

    config = Config.load(base_path)

    if stdout:
        content = generate_export(config)
        click.echo(content)
    else:
        output_path = Path(output).expanduser() if output else None
        result_path = write_export(config, output_path)
        console.print(f"[green]Exported to {result_path}[/green]")
        console.print()
        console.print("To use with Claude Code:")
        console.print(f"  1. Copy to your project: [cyan]cp {result_path} ./CONTEXT.md[/cyan]")
        console.print("  2. Reference in CLAUDE.md: [cyan]See CONTEXT.md for user context[/cyan]")


@cli.command()
@click.option("--path", type=click.Path(), default=None, help="Custom Continuum directory")
def validate(path: str | None):
    """Validate Continuum files."""
    base_path = Path(path).expanduser() if path else get_default_base_path()

    if not base_path.exists():
        console.print("[red]Continuum not initialized.[/red]")
        console.print("Run [cyan]continuum init[/cyan] first.")
        return

    config = Config.load(base_path)
    issues = []
    warnings = []

    console.print("[bold]Validating Continuum files...[/bold]")
    console.print()

    # Check each file
    files = [
        ("identity.md", config.identity_path, ["## Core", "## Background"]),
        ("voice.md", config.voice_path, ["## Do", "## Don't"]),
        ("context.md", config.context_path, ["## Current Focus"]),
        ("memory.md", config.memory_path, []),
    ]

    for name, filepath, required_sections in files:
        console.print(f"[bold]{name}[/bold]")

        if not filepath.exists():
            console.print("  [red]x File missing[/red]")
            issues.append(f"{name} missing")
            continue

        console.print("  [green]ok[/green] File exists")

        # Check for required sections
        content = filepath.read_text()
        for section in required_sections:
            if section.lower() in content.lower():
                console.print(f"  [green]ok[/green] Has '{section}' section")
            else:
                console.print(f"  [yellow]![/yellow] Missing '{section}' section")
                warnings.append(f"{name}: missing {section}")

        # Check staleness
        if is_stale(filepath, config.stale_days):
            age = get_file_age_str(filepath)
            console.print(f"  [yellow]![/yellow] Updated {age} (may be stale)")
            warnings.append(f"{name}: possibly stale")

        # Special checks for memory.md
        if name == "memory.md":
            count = count_memory_entries(filepath)
            console.print(f"  [dim]{count} entries[/dim]")

        console.print()

    # Summary
    if issues:
        console.print(f"[red]Issues: {len(issues)}[/red]")
    if warnings:
        console.print(f"[yellow]Warnings: {len(warnings)}[/yellow]")
    if not issues and not warnings:
        console.print("[green]All files valid[/green]")


@cli.group()
def voice():
    """Voice profile commands."""
    pass


@voice.command("analyze")
@click.option(
    "--samples",
    type=click.Path(exists=True),
    default=None,
    help="Path to samples directory (default: ~/.continuum/samples)",
)
@click.option(
    "--model",
    default="google/gemini-3-flash-preview",
    help="OpenRouter model to use for analysis",
)
@click.option("--dry-run", is_flag=True, help="Show analysis without updating voice.md")
@click.option("--raw", is_flag=True, help="Show raw API response")
@click.option("--path", type=click.Path(), default=None, help="Custom Continuum directory")
def voice_analyze(
    samples: str | None,
    model: str,
    dry_run: bool,
    raw: bool,
    path: str | None,
):
    """Analyze writing samples to generate voice profile.

    Reads samples from ~/.continuum/samples/ (or --samples path) and uses
    an LLM to extract voice patterns, vocabulary, and structural preferences.

    Requires OPENROUTER_API_KEY environment variable.

    Example:
        continuum voice analyze
        continuum voice analyze --dry-run
        continuum voice analyze --samples ~/my-emails/
    """
    import os

    base_path = Path(path).expanduser() if path else get_default_base_path()
    config = Config.load(base_path)

    samples_path = Path(samples).expanduser() if samples else config.base_path / "samples"

    # Check for API key early
    if not os.environ.get("OPENROUTER_API_KEY"):
        console.print("[red]Error: OPENROUTER_API_KEY environment variable not set[/red]")
        console.print()
        console.print("Set it with:")
        console.print("  export OPENROUTER_API_KEY=your-key-here")
        return

    # Check for samples
    if not samples_path.exists():
        console.print(f"[red]Samples directory not found: {samples_path}[/red]")
        console.print()
        console.print("Create it and add writing samples:")
        console.print(f"  mkdir -p {samples_path}/emails")
        console.print(f"  mkdir -p {samples_path}/technical")
        console.print("  # Add .md or .txt files to these directories")
        return

    # Count samples
    sample_count = 0
    for item in samples_path.rglob("*"):
        if item.is_file() and item.suffix in (".md", ".txt", ".eml", ""):
            sample_count += 1

    if sample_count == 0:
        console.print(f"[red]No samples found in {samples_path}[/red]")
        console.print("Add .md, .txt, or .eml files to analyze.")
        return

    console.print(f"[bold]Analyzing {sample_count} samples...[/bold]")
    console.print(f"  Samples: {samples_path}")
    console.print(f"  Model: {model}")
    console.print()

    with console.status("[bold green]Calling API..."):
        result = analyze_voice(config, samples_path, model=model)

    if result.error:
        console.print(f"[red]Error: {result.error}[/red]")
        return

    if raw:
        console.print("[bold]Raw API Response:[/bold]")
        console.print(result.raw_response)
        return

    if not result.parsed:
        console.print("[yellow]Warning: Could not parse structured response[/yellow]")
        console.print()
        console.print("[bold]Raw response:[/bold]")
        console.print(result.raw_response)
        return

    # Generate voice.md content
    voice_content = generate_voice_md(result.parsed)

    if dry_run:
        console.print("[bold]Generated voice.md (dry run):[/bold]")
        console.print()
        console.print(voice_content)
        console.print()
        console.print("[dim]Use without --dry-run to update voice.md[/dim]")
    else:
        # Write to voice.md
        voice_path = config.voice_path
        voice_path.write_text(voice_content)
        console.print(f"[green]Updated {voice_path}[/green]")
        console.print()
        console.print("Review with:")
        console.print(f"  continuum edit voice")


@voice.command("samples")
@click.option("--path", type=click.Path(), default=None, help="Custom Continuum directory")
def voice_samples(path: str | None):
    """Show sample collection status."""
    base_path = Path(path).expanduser() if path else get_default_base_path()
    samples_path = base_path / "samples"

    if not samples_path.exists():
        console.print(f"[yellow]Samples directory not found: {samples_path}[/yellow]")
        console.print()
        console.print("Create it with:")
        console.print(f"  mkdir -p {samples_path}/emails")
        console.print(f"  mkdir -p {samples_path}/technical")
        console.print(f"  mkdir -p {samples_path}/feedback")
        return

    console.print(f"[bold]Samples directory: {samples_path}[/bold]")
    console.print()

    # Count by category
    total = 0
    for item in sorted(samples_path.iterdir()):
        if item.is_dir():
            count = len(list(item.glob("*")))
            total += count
            status = "[green]" if count > 0 else "[dim]"
            console.print(f"  {status}{item.name}/[/] {count} files")
        elif item.is_file():
            total += 1
            console.print(f"  {item.name}")

    console.print()
    console.print(f"[bold]Total: {total} samples[/bold]")

    if total == 0:
        console.print()
        console.print("[dim]Add writing samples (.md, .txt, .eml) to analyze[/dim]")


@cli.group()
def serve():
    """MCP server commands."""
    pass


@serve.command("stdio")
def serve_stdio():
    """Run MCP server with stdio transport (for local Claude Code/Desktop)."""
    from .mcp_server import run_stdio

    console.print("[bold]Starting Continuum MCP server (stdio)...[/bold]")
    run_stdio()


@serve.command("sse")
@click.option("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0 for Tailscale)")
@click.option("--port", default=8765, help="Port to listen on (default: 8765)")
def serve_sse(host: str, port: int):
    """Run MCP server with SSE transport (for remote access via Tailscale).

    This starts an HTTP server that Claude can connect to remotely.
    Use with Tailscale for secure access from any device.

    Example:
        continuum serve sse
        continuum serve sse --port 9000
    """
    from .mcp_server import run_sse

    console.print(f"[bold]Starting Continuum MCP server (SSE)...[/bold]")
    console.print(f"  Host: {host}")
    console.print(f"  Port: {port}")
    console.print()
    run_sse(host=host, port=port)


@serve.command("config")
@click.option("--sse", is_flag=True, help="Show SSE config (for remote access)")
@click.option("--port", default=8765, help="Port for SSE server")
def serve_config(sse: bool, port: int):
    """Show MCP configuration for Claude Code or Claude Desktop.

    Prints the JSON config to add to your MCP settings.
    """
    import json
    import subprocess

    if sse:
        # Get Tailscale hostname
        try:
            result = subprocess.run(
                ["tailscale", "status", "--json"],
                capture_output=True,
                text=True,
                check=True,
            )
            import json as json_mod
            ts_status = json_mod.loads(result.stdout)
            hostname = ts_status.get("Self", {}).get("DNSName", "").rstrip(".")
            if not hostname:
                hostname = "<your-tailscale-hostname>"
        except Exception:
            hostname = "<your-tailscale-hostname>"

        config = {
            "continuum": {
                "transport": "sse",
                "url": f"https://{hostname}/mcp/sse",
            }
        }
        console.print("[bold]SSE MCP Config (for remote Claude):[/bold]")
    else:
        # Find the continuum-mcp executable
        import shutil

        mcp_path = shutil.which("continuum-mcp")
        if not mcp_path:
            mcp_path = "continuum-mcp"

        config = {
            "continuum": {
                "command": mcp_path,
                "args": [],
            }
        }
        console.print("[bold]Stdio MCP Config (for local Claude Code):[/bold]")

    console.print()
    console.print(json.dumps(config, indent=2))
    console.print()
    console.print("[dim]Add this to your MCP settings file.[/dim]")


if __name__ == "__main__":
    cli()
