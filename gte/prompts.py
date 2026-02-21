"""
System prompts and templates for AI roasting
"""

from datetime import datetime

ROASTER_SYSTEM_PROMPT = """You are the GitHub Truth Engine, a witty AI code critic with a sharp sense of humor.

Your mission: Compare what GitHub repos CLAIM in their READMEs versus what they ACTUALLY deliver.

PERSONALITY:
- Sarcastic but fair, like a senior developer who's seen every framework war
- Evidence-based (never make things up - roast based on actual data)
- Funny but not cruel (roast the code/claims, not the developers personally)
- Use developer humor, memes, and programming culture references
- Be quotable and memorable

ROASTING TARGETS (with examples):
1. Performance claims without proof
   - "Blazingly fast" with zero benchmarks → "Trust me bro: The Benchmark"
   - "10x faster" with no comparison → "10x faster than what? A potato?"

2. Dependency inflation
   - "Zero dependencies" with 100+ packages → "Zero dependencies* (*terms and conditions apply)"
   - "Lightweight" with massive node_modules → "Lightweight like a Boeing 747"

3. Production readiness theater
   - "Production ready" with 30% test coverage → "Production ready for your nightmares"
   - "Battle tested" from 2 weeks ago → "The battle lasted 15 minutes"

4. Simplicity lies
   - "Just works" with 47 setup steps → "Just works (PhD required)"
   - "Easy setup" with complex config → "Easy for time travelers"

5. Maintenance promises
   - "Actively maintained" with last commit 2 years ago → "Active like my gym membership"
   - "Growing community" with 3 contributors → "Growing pains included"

FORMAT YOUR RESPONSE:
For each major claim, provide:
CLAIM: [exact quote from README]
EVIDENCE: [what you actually found in the data]
ROAST: [your witty one-liner]

Then end with:
TRUTH SCORE: [0-100, where 100 is perfectly honest]
VERDICT: [Creative category name]
SPICIEST TAKE: [Your most memorable roast]

SCORING GUIDE:
90-100: Honest AF (rare unicorn)
70-89: Mostly True (refreshingly honest)
50-69: Marketing Spin (standard GitHub fare)
30-49: Creative Liberties (stretching it)
0-29: README Fiction (pure fantasy)

REMEMBER:
- Be funny, not mean
- Roast with love (we're all trying to build cool stuff)
- If something is actually good, say so
- The best roasts are unexpected and clever
- Make developers laugh while making them think
"""

ANALYSIS_TEMPLATE = """Analyze this GitHub repository and generate a roast:

REPOSITORY: {name}
STARS: {stars} ⭐
DESCRIPTION: {description}

README CLAIMS DETECTED:
{claims}

ACTUAL EVIDENCE:
- Dependencies: {dep_count} ({dep_type})
- Has Tests: {has_tests}
- Test Coverage: {test_coverage}
- Has Benchmarks: {has_benchmarks}
- Has CI/CD: {has_ci}
- Has Documentation: {has_docs}
- Last Commit: {last_commit}
- Commit Activity (90 days): {commit_count} commits
- Open Issues: {open_issues}
- Issue Close Rate: {issue_close_rate}%
- Age: {age}
- License: {license}

SPECIFIC CLAIMS TO VERIFY:
{specific_claims}

Generate a witty, sarcastic but fair roast. Focus on the gap between claims and reality.
Be creative with your roasts - make them memorable and quotable.
If the repo is actually honest and well-maintained, acknowledge that too.
"""

SPICY_MODE_ADDITION = """
🌶️ SPICY MODE ACTIVATED 🌶️

Turn up the heat! Be extra sarcastic and witty, but still fair.
Reference developer culture, memes, and inside jokes.
Make this roast legendary.
"""

def build_analysis_prompt(data: dict, spicy: bool = False) -> str:
    """Build the analysis prompt from repo data"""
    
    # Format claims
    claims_text = ""
    if data['readme_claims']:
        for claim in data['readme_claims'][:10]:  # Top 10 claims
            claims_text += f"- {claim['category'].upper()}: \"{claim['text']}\" (mentioned {claim['count']}x)\n"
    else:
        claims_text = "- No specific claims detected in README\n"
    
    # Calculate age
    age_days = (data['updated_at'] - data['created_at']).days
    if age_days < 30:
        age = f"{age_days} days old (fresh!)"
    elif age_days < 365:
        age = f"{age_days // 30} months old"
    else:
        age = f"{age_days // 365} years old"
    
    # Format last commit
    days_since_commit = (datetime.now(data['pushed_at'].tzinfo) - data['pushed_at']).days
    if days_since_commit == 0:
        last_commit = "today"
    elif days_since_commit == 1:
        last_commit = "yesterday"
    elif days_since_commit < 30:
        last_commit = f"{days_since_commit} days ago"
    elif days_since_commit < 365:
        last_commit = f"{days_since_commit // 30} months ago"
    else:
        last_commit = f"{days_since_commit // 365} years ago"
    
    # Build specific claims to verify
    specific_claims = []
    if any(c['category'] == 'performance' for c in data['readme_claims']):
        specific_claims.append(f"- Performance claims: Has benchmarks = {data['has_benchmarks']}")
    if any(c['category'] == 'lightweight' for c in data['readme_claims']):
        specific_claims.append(f"- Lightweight claims: {data['dependencies']['count']} dependencies")
    if any(c['category'] == 'production' for c in data['readme_claims']):
        specific_claims.append(f"- Production ready claims: Tests = {data['has_tests']}, CI = {data['has_ci']}")
    if any(c['category'] == 'simplicity' for c in data['readme_claims']):
        specific_claims.append(f"- Simplicity claims: Dependency count = {data['dependencies']['count']}")
    
    specific_claims_text = "\n".join(specific_claims) if specific_claims else "- No specific claims to verify"
    
    # Build the prompt
    prompt = ANALYSIS_TEMPLATE.format(
        name=data['full_name'],
        stars=data['stars'],
        description=data['description'] or "No description",
        claims=claims_text,
        dep_count=data['dependencies']['count'],
        dep_type=data['dependencies']['type'] or 'unknown',
        has_tests=data['has_tests'],
        test_coverage=data['test_coverage'] or "Unknown",
        has_benchmarks=data['has_benchmarks'],
        has_ci=data['has_ci'],
        has_docs=data['has_docs'],
        last_commit=last_commit,
        commit_count=data['commit_frequency']['last_90_days'],
        open_issues=data['open_issues'],
        issue_close_rate=data['issue_stats']['close_rate'],
        age=age,
        license=data['license'] or "No license",
        specific_claims=specific_claims_text
    )
    
    if spicy:
        prompt += "\n" + SPICY_MODE_ADDITION
    
    return prompt


if __name__ == "__main__":
    # Test prompt generation
    from datetime import datetime
    
    test_data = {
        'full_name': 'test/repo',
        'stars': 1000,
        'description': 'A blazingly fast framework',
        'readme_claims': [
            {'category': 'performance', 'text': 'blazingly fast', 'count': 3},
            {'category': 'lightweight', 'text': 'zero dependencies', 'count': 1}
        ],
        'dependencies': {'count': 50, 'type': 'npm'},
        'has_tests': False,
        'test_coverage': None,
        'has_benchmarks': False,
        'has_ci': True,
        'has_docs': False,
        'created_at': datetime(2020, 1, 1),
        'updated_at': datetime.now(),
        'pushed_at': datetime.now(),
        'commit_frequency': {'last_90_days': 5},
        'open_issues': 100,
        'issue_stats': {'close_rate': 30},
        'license': 'MIT'
    }
    
    prompt = build_analysis_prompt(test_data, spicy=True)
    print(prompt)
