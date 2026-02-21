"""
AI Roaster - Generates witty roasts using local or cloud AI
"""

from typing import Dict, Optional
from .prompts import ROASTER_SYSTEM_PROMPT, build_analysis_prompt


class AIRoaster:
    """Generates AI-powered roasts of GitHub repositories"""
    
    def __init__(self, model: str = "mistral", api_key: Optional[str] = None, quick_mode: bool = False):
        """
        Initialize the roaster
        
        Args:
            model: Model to use (mistral, llama3, gpt-4, gpt-3.5-turbo, etc.)
            api_key: OpenAI API key if using GPT models
            quick_mode: Skip AI initialization (for quick roasts only)
        """
        self.model = model
        self.api_key = api_key
        self.client = None
        self.backend = None
        
        # Skip initialization in quick mode
        if quick_mode:
            return
        
        # Determine which backend to use
        if model.startswith('gpt'):
            self._init_openai()
        else:
            self._init_ollama()
    
    def _init_ollama(self):
        """Initialize Ollama client"""
        try:
            import ollama
            self.client = ollama.Client()
            self.backend = 'ollama'
            
            # Check if model is available
            try:
                models = self.client.list()
                available = [m['name'] for m in models.get('models', [])]
                
                if self.model not in available and f"{self.model}:latest" not in available:
                    print(f"⚠️  Model '{self.model}' not found locally.")
                    print(f"   Run: ollama pull {self.model}")
                    print(f"   Available models: {', '.join(available)}")
                    raise ValueError(f"Model {self.model} not available")
                    
            except Exception as e:
                print(f"")
                
        except ImportError:
            raise ImportError(
                "Ollama not installed. Install with: pip install ollama\n"
                "Also install Ollama: https://ollama.com/download"
            )
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required for GPT models.\n"
                "Usage: gte roast <repo> --model gpt-4 --api-key YOUR_KEY"
            )
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            self.backend = 'openai'
        except ImportError:
            raise ImportError("OpenAI not installed. Install with: pip install openai")
    
    def roast(self, repo_data: Dict, spicy: bool = False) -> str:
        """
        Generate roast for a repository
        
        Args:
            repo_data: Repository analysis data
            spicy: Enable extra spicy mode
            
        Returns:
            Generated roast text
        """
        # Build the prompt
        prompt = build_analysis_prompt(repo_data, spicy=spicy)
        
        # Generate roast based on backend
        if self.backend == 'ollama':
            return self._roast_ollama(prompt)
        else:
            return self._roast_openai(prompt)
    
    def _roast_ollama(self, prompt: str) -> str:
        """Generate roast using Ollama"""
        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'system',
                        'content': ROASTER_SYSTEM_PROMPT
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': 0.8,  # Creative but not random
                    'top_p': 0.9,
                }
            )
            
            return response['message']['content']
            
        except Exception as e:
            raise RuntimeError(f"Ollama error: {e}\nMake sure Ollama is running: ollama serve")
    
    def _roast_openai(self, prompt: str) -> str:
        """Generate roast using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        'role': 'system',
                        'content': ROASTER_SYSTEM_PROMPT
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=0.8,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise RuntimeError(f"OpenAI error: {e}")
    
    def quick_roast(self, repo_data: Dict) -> str:
        """
        Generate a quick roast without AI (fallback)
        Uses template-based roasting for offline mode
        """
        roasts = []
        score = 100
        
        # Check performance claims
        perf_claims = [c for c in repo_data['readme_claims'] if c['category'] == 'performance']
        if perf_claims and not repo_data['has_benchmarks']:
            roasts.append({
                'claim': perf_claims[0]['text'],
                'evidence': 'No benchmarks found',
                'roast': '"Trust me bro" - The Benchmark'
            })
            score -= 20
        
        # Check dependency claims
        dep_claims = [c for c in repo_data['readme_claims'] if c['category'] == 'lightweight']
        if dep_claims and repo_data['dependencies']['count'] > 50:
            roasts.append({
                'claim': dep_claims[0]['text'],
                'evidence': f"{repo_data['dependencies']['count']} dependencies",
                'roast': f"'{dep_claims[0]['text']}' is a state of mind, not a dependency count"
            })
            score -= 15
        
        # Check production readiness
        prod_claims = [c for c in repo_data['readme_claims'] if c['category'] == 'production']
        if prod_claims and not repo_data['has_tests']:
            roasts.append({
                'claim': prod_claims[0]['text'],
                'evidence': 'No tests detected',
                'roast': 'Production ready for chaos engineering'
            })
            score -= 25
        
        # Build output
        output = f"\n📊 Repository: {repo_data['full_name']}\n"
        output += f"⭐ Stars: {repo_data['stars']:,}\n\n"
        
        if roasts:
            for r in roasts:
                output += f"❌ CLAIM: \"{r['claim']}\"\n"
                output += f"   EVIDENCE: {r['evidence']}\n"
                output += f"   ROAST: {r['roast']}\n\n"
        else:
            output += "✅ No obvious lies detected. Surprisingly honest!\n\n"
            score = 95
        
        # Score and verdict
        if score >= 90:
            verdict = "Honest AF"
        elif score >= 70:
            verdict = "Mostly True"
        elif score >= 50:
            verdict = "Marketing Spin"
        elif score >= 30:
            verdict = "Creative Liberties"
        else:
            verdict = "README Fiction"
        
        output += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        output += f"TRUTH SCORE: {score}/100\n"
        output += f"VERDICT: {verdict}\n"
        output += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        return output


if __name__ == "__main__":
    # Test the roaster with mock data
    from datetime import datetime
    
    test_data = {
        'full_name': 'awesome/framework',
        'name': 'framework',
        'stars': 50000,
        'description': 'A blazingly fast web framework',
        'readme_claims': [
            {'category': 'performance', 'text': 'blazingly fast', 'count': 3},
            {'category': 'lightweight', 'text': 'minimal dependencies', 'count': 1},
            {'category': 'production', 'text': 'production ready', 'count': 2}
        ],
        'dependencies': {'count': 127, 'type': 'npm'},
        'has_tests': True,
        'test_coverage': 45,
        'has_benchmarks': False,
        'has_ci': True,
        'has_docs': True,
        'created_at': datetime(2020, 1, 1),
        'updated_at': datetime.now(),
        'pushed_at': datetime.now(),
        'commit_frequency': {'last_90_days': 150},
        'open_issues': 234,
        'issue_stats': {'close_rate': 67},
        'license': 'MIT'
    }
    
    print("Testing quick roast (no AI):")
    print("="*50)
    
    roaster = AIRoaster()
    quick = roaster.quick_roast(test_data)
    print(quick)
