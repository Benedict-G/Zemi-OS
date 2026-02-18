"""
Zemi Orchestrator - Main AI Brain
Coordinates all subsystems and manages execution flow
"""

import asyncio
import ollama
import json
from datetime import datetime
from pathlib import Path
from skill_loader import SkillLoader # Add this
from browser import BrowserController # Add this

class ZemiOrchestrator:
    def __init__(self, config_path="config.json"):
        self.config = self._load_config(config_path)
        self.running = False
        self.command_queue = asyncio.Queue()
        self._last_user_input = "" # ADD THIS LINE
        self.skills = SkillLoader()
        self.browser = BrowserController() #Add this        

        # Execution levels
        self.LEVEL_0_REASONING = 0  # AI thinking only
        self.LEVEL_1_READ = 1       # Read-only operations
        self.LEVEL_2_NETWORK = 2    # Browser, email
        self.LEVEL_3_SYSTEM = 3     # Docker, scripts, root
        
        print("🤖 Zemi Orchestrator initialized")
    
    def _load_config(self, config_path):
        """Load configuration"""
        # Default config
        config = {
            "ollama_model": "llama3.2:3b",
            "require_approval": False,
            "log_dir": "../logs",
            "vault_dir": "../vault"
        }
        
        if Path(config_path).exists():
            with open(config_path, 'r') as f:
                config.update(json.load(f))
        
        return config
    
    async def process_command(self, user_input, user_id):
        """Main command processing pipeline"""
        
        print(f"\n📥 Command received from {user_id}: {user_input}")
        
        # Store for later use
        self._last_user_input = user_input

        # Step 1: Use Ollama to understand intent
        intent = await self._analyze_intent(user_input)
        
        print(f"🧠 Intent: {intent['action']}")
        print(f"📊 Execution Level: {intent['level']}")
        
        # Step 2: Check if approval needed
        if intent['level'] >= self.LEVEL_2_NETWORK and self.config['require_approval']:
            approved = await self._request_approval(intent, user_id)
            if not approved:
                return "❌ Action cancelled by user"
        
        # Step 3: Execute based on intent
        result = await self._execute_action(intent)
        
        # Step 4: Log everything
        self._log_action(user_id, user_input, intent, result)
        
        return result
    
    async def _analyze_intent(self, user_input):
        """Use Ollama to understand what user wants"""
        
        # Find relevant skills for this query
        relevant_skills = self.skills.find_relevant_skills(user_input)
        skill_context = ""
    
        if relevant_skills:
            skill_context = "\n\nRELEVANT SKILLS:\n"
            for skill in relevant_skills:
                skill_context += f"\n--- {skill['name']} ---\n{skill['content'][:500]}...\n"
    
        prompt = f"""You are Zemi, a security-focused AI assistant. Analyze this command and respond ONLY with a JSON object (no other text):

{skill_context}

User command: "{user_input}"

Determine:
1. action: what type of action (search_web, send_email, read_file, write_file, run_script, chat)
2. level: execution level (0=reasoning only, 1=read-only, 2=network actions, 3=system execution)
3. parameters: any needed parameters as a dict
4. requires_approval: true if this is a sensitive action

Example response:
{{"action": "search_web", "level": 2, "parameters": {{"query": "weather today"}}, "requires_approval": true}}

Respond with JSON only:"""

        try:
            response = ollama.chat(
                model=self.config['ollama_model'],
                messages=[{'role': 'user', 'content': prompt}]
            )
            
            # Parse JSON from response
            intent_text = response['message']['content'].strip()
            
            # Clean up any markdown formatting
            if intent_text.startswith('```'):
                intent_text = intent_text.split('```')[1]
                if intent_text.startswith('json'):
                    intent_text = intent_text[4:]
            
            intent = json.loads(intent_text)
            return intent
            
        except Exception as e:
            print(f"⚠️ Intent analysis error: {e}")
            # Fallback to safe defaults
            return {
                "action": "chat",
                "level": 0,
                "parameters": {"response": user_input},
                "requires_approval": False
            }
    
    async def _request_approval(self, intent, user_id):
        """Request user approval for sensitive actions"""
        
        print(f"\n⚠️  APPROVAL REQUIRED")
        print(f"Action: {intent['action']}")
        print(f"Level: {intent['level']}")
        print(f"Parameters: {intent['parameters']}")
        print(f"\nTYPE 'YES' TO EXECUTE: ", end='')
        
        # In production, this would come from Matrix
        # For now, use stdin for testing
        response = input().strip().upper()
        
        return response == "YES"
    
    async def _execute_action(self, intent):
        """Execute the intended action"""
        
        action = intent['action']
        params = intent.get('parameters', {})
        
        print(f"⚙️  Executing: {action}")
        
        # Route to appropriate handler
        if action == "chat":
            # Make sure we pass the user's original message
            if 'user_input' not in params:
                params['user_input'] = self._last_user_input
            return await self._handle_chat(params)
        elif action == "list_skills":
            return await self._handle_list_skills(params)
        elif action == "search_web":
            return await self._handle_web_search(params)
        elif action == "send_email":
            return await self._handle_email(params)
        elif action == "read_file":
            return await self._handle_read_file(params)
        elif action == "write_file":
            return await self._handle_write_file(params)
        else:
            return f"❓ Unknown action: {action}"

    async def _handle_list_skills(self, params):
        """List all available skills"""
    
        all_skills = self.skills.list_all_skills()
    
        response = "📚 **Available Skills:**\n\n"
    
        # Group by category
        categories = {}
        for skill in all_skills:
            cat = skill['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(skill['name'])
    
        for category, skill_names in categories.items():
            response += f"**{category.title()}:**\n"
            for name in skill_names:
                response += f"  • {name}\n"
            response += "\n"
    
        return response

    async def _handle_chat(self, params):
        """Handle conversational responses"""
        
        user_message = params.get('user_input', params.get('response',  'Hello'))
        
        # Check if asking about capabilities
        if any(word in user_message.lower() for word in ['capabilities', 'can you', 'what can', 'help', 'do for me']):
            capabilities = """I'm Zemi, your local AI assistant. Here's what I can currently do:

🧠 **Active Capabilities:**
- Chat and answer questions (using Llama 3.2)
- Understand your intent and commands
- Log all interactions securely

🔧 **In Development:**
- Web search and browsing (browser container ready)
- Send emails (Proton Bridge configured)
- Read and write files
- Execute scripts in Docker sandbox

🔒 **Security Features:**
- All processing stays on your Mac Mini
- Permission system (requires approval for sensitive actions)
- Encrypted credential vault
- Complete audit logging

📱 **Access:**
- Matrix (Element X on iPhone) - Active
- Voice commands - Ready
- HTTPS Dashboard - Ready

What would you like me to help you with?"""
            return capabilities
        
        # Regular chat response
        response = ollama.chat(
            model=self.config['ollama_model'],
            messages=[
                {'role': 'system', 'content': 'You are Zemi, a helpful, concise, and secure local AI assistant. Keep responses brief and friendly.'},
                {'role': 'user', 'content': user_message}
            ]
        )
        
        return response['message']['content']
    
    async def _handle_web_search(self, params):
        """Handle web searches using Brave API"""
        query = params.get('query', '')
        
        if not query:
            return "❓ What would you like me to search for?"

        result = await self.browser.search_web(query, num_results=3)
        return result
    
    async def _handle_email(self, params):
        """Handle email sending (placeholder for now)"""
        to = params.get('to', '')
        subject = params.get('subject', '')
        return f"📧 Email to {to}: {subject}\n(Email integration coming in next steps)"
    
    async def _handle_read_file(self, params):
        """Handle file reading"""
        filepath = params.get('path', '')
        return f"📄 Reading file: {filepath}\n(File operations coming in next steps)"
    
    async def _handle_write_file(self, params):
        """Handle file writing"""
        filepath = params.get('path', '')
        return f"✍️  Writing file: {filepath}\n(File operations coming in next steps)"
    
    def _log_action(self, user_id, command, intent, result):
        """Log all actions to audit trail"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "command": command,
            "intent": intent,
            "result_preview": str(result)[:200],
            "level": intent['level']
        }
        
        # Create logs directory if needed
        log_dir = Path(self.config['log_dir'])
        log_dir.mkdir(exist_ok=True)
        
        # Append to daily log file
        log_file = log_dir / f"zemi_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        print(f"📝 Action logged to {log_file}")

# Test mode
async def test_orchestrator():
    """Test the orchestrator"""
    
    zemi = ZemiOrchestrator()
    
    print("\n" + "="*50)
    print("🤖 ZEMI ORCHESTRATOR TEST MODE")
    print("="*50)
    
    test_commands = [
        "What is the weather like today?",
        "Search the web for Python tutorials",
        "Tell me a joke"
    ]
    
    for cmd in test_commands:
        print(f"\n{'='*50}")
        result = await zemi.process_command(cmd, "test_user")
        print(f"\n✅ Result: {result}")
        print(f"{'='*50}\n")
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(test_orchestrator())
