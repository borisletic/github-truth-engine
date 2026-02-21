"""
Repository analyzer - gathers intelligence about GitHub repos
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from github import Github, GithubException
import requests


class RepoAnalyzer:
    """Analyzes GitHub repositories to gather evidence for roasting"""
    
    def __init__(self, repo_url: str, github_token: Optional[str] = None):
        if github_token is None:
            import os
            github_token = os.getenv('GITHUB_TOKEN')
        """
        Initialize analyzer with repo URL
        
        Args:
            repo_url: GitHub repository URL or owner/repo format
            github_token: Optional GitHub personal access token for higher rate limits
        """
        self.repo_url = repo_url
        self.github = Github(github_token) if github_token else Github()
        self.owner, self.repo_name = self._parse_repo_url(repo_url)
        
    def _parse_repo_url(self, url: str) -> tuple[str, str]:
        """Parse GitHub URL to extract owner and repo name"""
        # Handle different formats:
        # - https://github.com/owner/repo
        # - github.com/owner/repo
        # - owner/repo
        
        url = url.strip().rstrip('/')
        
        if 'github.com' in url:
            # Extract from URL
            match = re.search(r'github\.com/([^/]+)/([^/]+)', url)
            if match:
                return match.group(1), match.group(2)
        else:
            # Assume owner/repo format
            parts = url.split('/')
            if len(parts) == 2:
                return parts[0], parts[1]
        
        raise ValueError(f"Invalid GitHub URL format: {url}")
    
    def analyze(self) -> Dict:
        """
        Analyze repository and gather all evidence
        
        Returns:
            Dictionary containing all repo intelligence
        """
        try:
            repo = self.github.get_repo(f"{self.owner}/{self.repo_name}")
        except GithubException as e:
            raise ValueError(f"Could not access repository: {e}")
        
        print(f"📊 Analyzing {repo.full_name}...")
        
        # Gather all the evidence
        data = {
            'name': repo.name,
            'full_name': repo.full_name,
            'description': repo.description,
            'stars': repo.stargazers_count,
            'forks': repo.forks_count,
            'watchers': repo.watchers_count,
            'open_issues': repo.open_issues_count,
            'language': repo.language,
            'created_at': repo.created_at,
            'updated_at': repo.updated_at,
            'pushed_at': repo.pushed_at,
            'size': repo.size,
            'readme': self._get_readme(repo),
            'readme_claims': [],
            'languages': repo.get_languages(),
            'dependencies': self._get_dependencies(repo),
            'has_tests': self._check_tests(repo),
            'has_benchmarks': self._check_benchmarks(repo),
            'has_ci': self._check_ci(repo),
            'has_docs': self._check_docs(repo),
            'test_coverage': self._estimate_test_coverage(repo),
            'commit_frequency': self._get_commit_frequency(repo),
            'issue_stats': self._get_issue_stats(repo),
            'license': repo.license.name if repo.license else None,
        }
        
        # Extract claims from README
        if data['readme']:
            data['readme_claims'] = self._extract_claims(data['readme'])
        
        return data
    
    def _get_readme(self, repo) -> Optional[str]:
        """Fetch README content"""
        try:
            readme = repo.get_readme()
            return readme.decoded_content.decode('utf-8')
        except:
            return None
    
    def _extract_claims(self, readme: str) -> List[str]:
        """Extract common marketing claims from README"""
        claims = []
        readme_lower = readme.lower()
        
        # Common hype words/phrases
        patterns = {
            'performance': [
                r'blazingly?\s+fast', r'\d+x\s+faster', r'lightning\s+fast',
                r'extremely\s+fast', r'super\s+fast', r'optimized',
                r'high\s+performance', r'performant', r'blazing'
            ],
            'simplicity': [
                r'simple', r'easy', r'straightforward', r'just\s+\w+',
                r'zero\s+config', r'no\s+setup', r'quick\s+start',
                r'minimal\s+setup', r'plug\s+and\s+play'
            ],
            'production': [
                r'production\s+ready', r'battle\s+tested', r'enterprise\s+grade',
                r'stable', r'reliable', r'proven', r'mature',
                r'industry\s+standard'
            ],
            'lightweight': [
                r'lightweight', r'minimal', r'tiny', r'small\s+footprint',
                r'zero\s+dependencies', r'no\s+dependencies',
                r'minimal\s+dependencies'
            ],
            'modern': [
                r'modern', r'cutting\s+edge', r'next\s+generation',
                r'future\s+proof', r'state\s+of\s+the\s+art'
            ],
            'comprehensive': [
                r'complete', r'full\s+featured', r'comprehensive',
                r'all\s+in\s+one', r'everything\s+you\s+need'
            ]
        }
        
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, readme_lower)
                if matches:
                    claims.append({
                        'category': category,
                        'text': matches[0],
                        'count': len(matches)
                    })
        
        return claims
    
    def _get_dependencies(self, repo) -> Dict:
        """Analyze project dependencies"""
        deps = {
            'count': 0,
            'type': None,
            'list': []
        }
        
        # Check for different dependency files
        dep_files = {
            'package.json': 'npm',
            'requirements.txt': 'pip',
            'Cargo.toml': 'cargo',
            'go.mod': 'go',
            'pom.xml': 'maven',
            'build.gradle': 'gradle',
            'Gemfile': 'bundler',
        }
        
        for filename, dep_type in dep_files.items():
            try:
                content = repo.get_contents(filename)
                deps['type'] = dep_type
                
                if filename == 'package.json':
                    data = json.loads(content.decoded_content)
                    deps_dict = {
                        **data.get('dependencies', {}),
                        **data.get('devDependencies', {})
                    }
                    deps['count'] = len(deps_dict)
                    deps['list'] = list(deps_dict.keys())
                
                elif filename == 'requirements.txt':
                    lines = content.decoded_content.decode('utf-8').split('\n')
                    deps['list'] = [l.strip() for l in lines if l.strip() and not l.startswith('#')]
                    deps['count'] = len(deps['list'])
                
                # Found dependencies, break
                break
                
            except:
                continue
        
        return deps
    
    def _check_tests(self, repo) -> bool:
        """Check if repository has tests"""
        test_indicators = [
            'test', 'tests', '__tests__', 'spec', 'specs',
            'test_', '_test.py', '.test.js', '.spec.js'
        ]
        
        try:
            contents = repo.get_contents("")
            
            def search_for_tests(items):
                for item in items:
                    if item.type == "dir":
                        if any(indicator in item.name.lower() for indicator in test_indicators):
                            return True
                        try:
                            sub_items = repo.get_contents(item.path)
                            if search_for_tests(sub_items):
                                return True
                        except:
                            pass
                    elif item.type == "file":
                        if any(indicator in item.name.lower() for indicator in test_indicators):
                            return True
                return False
            
            return search_for_tests(contents)
        except:
            return False
    
    def _check_benchmarks(self, repo) -> bool:
        """Check if repository has benchmarks"""
        try:
            contents = repo.get_contents("")
            for item in contents:
                if 'benchmark' in item.name.lower() or 'bench' in item.name.lower():
                    return True
            return False
        except:
            return False
    
    def _check_ci(self, repo) -> bool:
        """Check if repository has CI/CD setup"""
        ci_files = [
            '.github/workflows',
            '.travis.yml',
            '.circleci',
            'Jenkinsfile',
            '.gitlab-ci.yml',
            'azure-pipelines.yml'
        ]
        
        for ci_file in ci_files:
            try:
                repo.get_contents(ci_file)
                return True
            except:
                continue
        
        return False
    
    def _check_docs(self, repo) -> bool:
        """Check if repository has documentation"""
        doc_indicators = ['docs', 'documentation', 'doc', 'wiki']
        
        try:
            contents = repo.get_contents("")
            for item in contents:
                if any(indicator in item.name.lower() for indicator in doc_indicators):
                    return True
            return False
        except:
            return False
    
    def _estimate_test_coverage(self, repo) -> Optional[int]:
        """Try to estimate test coverage (rough approximation)"""
        # This is a very rough estimate
        # In reality, you'd parse coverage reports
        if not self._check_tests(repo):
            return 0
        
        # If has tests but can't determine coverage, return None
        # A real implementation would parse coverage badges or reports
        return None
    
    def _get_commit_frequency(self, repo) -> Dict:
        """Analyze commit frequency"""
        try:
            # Get commits from last 3 months
            since = datetime.now() - timedelta(days=90)
            commits = repo.get_commits(since=since)
            
            commit_count = commits.totalCount
            
            return {
                'last_90_days': commit_count,
                'avg_per_week': round(commit_count / 13, 1),
                'is_active': commit_count > 0
            }
        except:
            return {
                'last_90_days': 0,
                'avg_per_week': 0,
                'is_active': False
            }
    
    def _get_issue_stats(self, repo) -> Dict:
        """Analyze issue statistics"""
        try:
            open_issues = repo.open_issues_count
            closed_issues = repo.get_issues(state='closed').totalCount
            total_issues = open_issues + closed_issues
            
            return {
                'open': open_issues,
                'closed': closed_issues,
                'total': total_issues,
                'close_rate': round(closed_issues / total_issues * 100, 1) if total_issues > 0 else 0
            }
        except:
            return {
                'open': 0,
                'closed': 0,
                'total': 0,
                'close_rate': 0
            }


if __name__ == "__main__":
    # Test the analyzer
    analyzer = RepoAnalyzer("facebook/react")
    data = analyzer.analyze()
    
    print("\n=== ANALYSIS RESULTS ===")
    print(f"Name: {data['name']}")
    print(f"Stars: {data['stars']}")
    print(f"Dependencies: {data['dependencies']['count']} ({data['dependencies']['type']})")
    print(f"Has Tests: {data['has_tests']}")
    print(f"Has Benchmarks: {data['has_benchmarks']}")
    print(f"Has CI: {data['has_ci']}")
    print(f"Claims found: {len(data['readme_claims'])}")
    for claim in data['readme_claims'][:5]:
        print(f"  - {claim['category']}: {claim['text']}")
