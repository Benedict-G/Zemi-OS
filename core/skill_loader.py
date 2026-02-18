"""
Zemi Skills System
Dynamically loads and manages skills
"""

import os
from pathlib import Path

class SkillLoader:
    def __init__(self, skills_dir="/Users/zemi/ZemiV1/skills"):
        self.skills_dir = Path(skills_dir)
        self.skills = {}
        self.load_all_skills()
    
    def load_all_skills(self):
        """Load all skill files from core, user, and examples"""
        
        skill_dirs = [
            self.skills_dir / "core",
            self.skills_dir / "user",
            self.skills_dir / "examples"
        ]
        
        for skill_dir in skill_dirs:
            if skill_dir.exists():
                for skill_file in skill_dir.glob("*.md"):
                    self.load_skill(skill_file)
        
        print(f"📚 Loaded {len(self.skills)} skills")
    
    def load_skill(self, skill_path):
        """Load a single skill file"""
        
        try:
            with open(skill_path, 'r') as f:
                content = f.read()
            
            skill_name = skill_path.stem
            self.skills[skill_name] = {
                'name': skill_name,
                'content': content,
                'path': str(skill_path),
                'category': skill_path.parent.name
            }
            
            print(f"  ✓ Loaded skill: {skill_name}")
            
        except Exception as e:
            print(f"  ✗ Failed to load {skill_path}: {e}")
    
    def get_skill(self, skill_name):
        """Get a specific skill by name"""
        return self.skills.get(skill_name)
    
    def find_relevant_skills(self, user_query):
        """Find skills relevant to the user's query"""
        
        relevant = []
        query_lower = user_query.lower()
        
        for skill_name, skill_data in self.skills.items():
            # Simple keyword matching
            if skill_name.lower() in query_lower or \
               any(keyword in query_lower for keyword in self._get_keywords(skill_data)):
                relevant.append(skill_data)
        
        return relevant
    
    def _get_keywords(self, skill_data):
        """Extract keywords from skill content"""
        # Look for keywords in first few lines
        lines = skill_data['content'].split('\n')[:10]
        keywords = []
        
        for line in lines:
            if line.startswith('Keywords:') or line.startswith('Triggers:'):
                keywords = line.split(':', 1)[1].strip().split(',')
                keywords = [k.strip().lower() for k in keywords]
                break
        
        return keywords
    
    def list_all_skills(self):
        """Return list of all available skills"""
        return [
            {
                'name': skill['name'],
                'category': skill['category']
            }
            for skill in self.skills.values()
        ]
    
    def reload_skills(self):
        """Reload all skills (useful after adding new ones)"""
        self.skills = {}
        self.load_all_skills()

