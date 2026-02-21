"""
Command-line interface for GitHub Truth Engine
"""

import click
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

from .analyzer import RepoAnalyzer
from .roaster import AIRoaster

console = Console()


@click.group()
@click.version_option(version='0.1.0')
def cli():
    """
    ⚖️  GitHub Truth Engine - AI-powered repo roaster
    
    What if everything on GitHub was true? It's not. Here's proof.
    
    Examples:
      gte roast facebook/react
      gte roast vercel/next.js --spicy
      gte roast microsoft/vscode --model gpt-4 --api-key sk-...
    """
    pass


@cli.command()
@click.argument('repo_url')
@click.option('--model', default='mistral', help='AI model (mistral, llama3, gpt-4, gpt-3.5-turbo)')
@click.option('--api-key', default=None, help='OpenAI API key (for GPT models)')
@click.option('--github-token', default=None, help='GitHub token (for higher rate limits)')
@click.option('--spicy', is_flag=True, help='🌶️  Extra spicy roasts')
@click.option('--quick', is_flag=True, help='Quick roast without AI (offline mode)')
@click.option('--output', '-o', type=click.File('w'), default=None, help='Save roast to file')
def roast(repo_url, model, api_key, github_token, spicy, quick, output):
    """
    Roast a GitHub repository
    
    Analyzes the repo and generates an AI-powered roast comparing
    README claims to actual reality.
    
    REPO_URL can be:
      - Full URL: https://github.com/owner/repo
      - Short form: owner/repo
    """
    
    try:
        # Header
        console.print()
        console.print("⚖️  [bold cyan]GITHUB TRUTH ENGINE[/bold cyan]", justify="center")
        console.print("━" * 60, style="cyan")
        console.print()
        
        # Step 1: Analyze repository
        console.print("🔍 [yellow]Analyzing repository...[/yellow]")
        
        try:
            analyzer = RepoAnalyzer(repo_url, github_token=github_token)
            data = analyzer.analyze()
        except ValueError as e:
            console.print(f"❌ [red]Error:[/red] {e}")
            sys.exit(1)
        except Exception as e:
            console.print(f"❌ [red]Failed to analyze repository:[/red] {e}")
            sys.exit(1)
        
        console.print(f"✓ Found: [bold]{data['full_name']}[/bold]")
        console.print(f"  Stars: {data['stars']:,} ⭐  |  Language: {data['language'] or 'Unknown'}")
        console.print()
        
        # Step 2: Generate roast
        if quick:
            console.print("⚡ [yellow]Generating quick roast (offline mode)...[/yellow]")
            roaster = AIRoaster(model=model, api_key=api_key)
            roast_text = roaster.quick_roast(data)
        else:
            console.print(f"🤖 [yellow]Generating {'spicy ' if spicy else ''}roast with {model}...[/yellow]")
            console.print("   (This may take 10-30 seconds)")
            
            try:
                roaster = AIRoaster(model=model, api_key=api_key)
                roast_text = roaster.roast(data, spicy=spicy)
            except Exception as e:
                console.print(f"❌ [red]Failed to generate roast:[/red] {e}")
                console.print()
                console.print("[yellow]💡 Try:[/yellow]")
                console.print("  • Quick mode: gte roast <repo> --quick")
                console.print("  • Different model: gte roast <repo> --model llama3")
                console.print("  • Check Ollama is running: ollama serve")
                sys.exit(1)
        
        console.print()
        
        # Step 3: Display roast
        console.print("━" * 60, style="cyan")
        console.print()
        
        # Parse and display roast with formatting
        display_roast(roast_text, data)
        
        console.print()
        console.print("━" * 60, style="cyan")
        console.print("⚖️  [dim]Powered by GitHub Truth Engine[/dim]")
        console.print(f"   [dim]Run: gte roast <repo-url>[/dim]")
        console.print()
        
        # Save to file if requested
        if output:
            output.write(roast_text)
            console.print(f"💾 Saved to: {output.name}")
            console.print()
        
    except KeyboardInterrupt:
        console.print("\n\n❌ Cancelled by user")
        sys.exit(1)


def display_roast(roast_text: str, data: dict):
    """Display roast with nice formatting"""
    
    # Split into lines and format
    lines = roast_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            console.print()
            continue
        
        # Format different parts
        if line.startswith('CLAIM:'):
            console.print(f"[yellow bold]{line}[/yellow bold]")
        elif line.startswith('EVIDENCE:'):
            console.print(f"[cyan]{line}[/cyan]")
        elif line.startswith('ROAST:'):
            console.print(f"[magenta italic]{line}[/magenta italic]")
        elif line.startswith('TRUTH SCORE:'):
            # Extract score and color it
            score_part = line.replace('TRUTH SCORE:', '').strip()
            try:
                score = int(score_part.split('/')[0])
                if score >= 70:
                    color = "green"
                elif score >= 50:
                    color = "yellow"
                else:
                    color = "red"
                console.print(f"[{color} bold]{line}[/{color} bold]")
            except:
                console.print(f"[bold]{line}[/bold]")
        elif line.startswith('VERDICT:'):
            console.print(f"[bold]{line}[/bold]")
        elif line.startswith('SPICIEST TAKE:') or line.startswith('💀'):
            console.print(f"[red bold]{line}[/red bold]")
        elif line.startswith('━') or line.startswith('─'):
            console.print(f"[dim]{line}[/dim]")
        else:
            console.print(line)


@cli.command()
@click.option('--model', default='mistral', help='AI model to use')
@click.option('--api-key', default=None, help='OpenAI API key (for GPT models)')
@click.option('--github-token', default=None, help='GitHub token')
def random(model, api_key, github_token):
    """
    Roast a random trending repository
    
    Picks a random repo from GitHub trending and roasts it.
    """
    console.print("🎲 [yellow]Finding a random victim...[/yellow]")
    console.print("   (Feature coming soon!)")
    console.print()
    console.print("💡 For now, try:")
    console.print("   gte roast facebook/react")
    console.print("   gte roast vercel/next.js --spicy")


@cli.command()
def examples():
    """
    Show example roasts
    
    Displays pre-generated roasts of popular repositories.
    """
    console.print()
    console.print("⚖️  [bold cyan]GITHUB TRUTH ENGINE - EXAMPLES[/bold cyan]")
    console.print("━" * 60, style="cyan")
    console.print()
    
    examples_text = """
Here are some example repositories you can roast:

🔥 FRAMEWORKS:
  • gte roast facebook/react
  • gte roast vuejs/core
  • gte roast angular/angular
  • gte roast sveltejs/svelte

⚡ BUILD TOOLS:
  • gte roast vitejs/vite
  • gte roast webpack/webpack
  • gte roast evanw/esbuild

🎨 UI LIBRARIES:
  • gte roast tailwindlabs/tailwindcss
  • gte roast mui/material-ui
  • gte roast chakra-ui/chakra-ui

🚀 FULL-STACK:
  • gte roast vercel/next.js
  • gte roast nuxt/nuxt
  • gte roast remix-run/remix

Try them with --spicy for extra heat! 🌶️
    """
    
    console.print(examples_text)
    console.print("━" * 60, style="cyan")
    console.print()


@cli.command()
def setup():
    """
    Setup guide for GitHub Truth Engine
    
    Shows instructions for installing dependencies and models.
    """
    console.print()
    console.print("⚖️  [bold cyan]GITHUB TRUTH ENGINE - SETUP[/bold cyan]")
    console.print("━" * 60, style="cyan")
    console.print()
    
    setup_guide = """
[bold yellow]1. Install Ollama (for local AI)[/bold yellow]

   macOS/Linux:
   curl -fsSL https://ollama.com/install.sh | sh

   Windows:
   Download from: https://ollama.com/download

[bold yellow]2. Pull an AI model[/bold yellow]

   ollama pull mistral      # Good balance (4GB)
   ollama pull llama3       # Better quality (4.7GB)
   ollama pull codellama    # Code-focused (3.8GB)

[bold yellow]3. Verify installation[/bold yellow]

   ollama list              # See installed models
   ollama serve             # Start Ollama server

[bold yellow]4. Run GitHub Truth Engine[/bold yellow]

   gte roast facebook/react
   gte roast vercel/next.js --spicy
   gte roast --help

[bold yellow]5. Optional: Use OpenAI instead[/bold yellow]

   gte roast <repo> --model gpt-4 --api-key sk-...

[bold green]✓ You're ready to roast![/bold green]
    """
    
    console.print(setup_guide)
    console.print("━" * 60, style="cyan")
    console.print()


if __name__ == '__main__':
    cli()
