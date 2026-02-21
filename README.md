# Can Your Repo Handle the Truth? GitHub Truth Engine
Truth ? Hype

AI-powered roast bot that calls out BS in GitHub READMEs.

## Install
```bash
pip install -e .
```

## Setup AI

**Install Ollama:**
- Windows: Download from [ollama.com](https://ollama.com/download)
- Mac/Linux: `curl -fsSL https://ollama.com/install.sh | sh`

**Pull model:**
```bash
ollama pull mistral
```

## Usage
```bash
# Roast any repo
gte roast facebook/react

# Extra spicy
gte roast vercel/next.js --spicy

# Quick mode (no AI needed)
gte roast tailwindcss/tailwindcss --quick
```

## GitHub Token (Optional)

Avoid rate limits:

1. Create token: https://github.com/settings/tokens
2. Set environment variable:
   - **Windows:** `$env:GITHUB_TOKEN = "ghp_YOUR_TOKEN"`
   - **Mac/Linux:** `export GITHUB_TOKEN="ghp_YOUR_TOKEN"`

## Examples
```bash
gte roast vuejs/core
gte roast angular/angular --spicy
gte roast sveltejs/svelte -o roast.txt
```

---

**Can your repo handle the truth?** ⚖️
