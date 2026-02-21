"""
Zemi Orchestrator - Main AI Brain
Coordinates all subsystems and manages execution flow
"""

import asyncio
import ollama
import time
from voice_handler import speak
VOICE_ENABLED = False  # Default off
import json
from datetime import datetime
from pathlib import Path
from skill_loader import SkillLoader # Add this
from browser import BrowserController # Add this

class ZemiOrchestrator:
    APPROVAL_TIMEOUT = 300
    PENDING_FILE = "pending_actions.json"
    def __init__(self, config_path="/Users/zemi/ZemiV1/config.json"):
        self.config = self._load_config(config_path)
        self.running = False
        self.command_queue = asyncio.Queue()
        self._last_user_input = "" # ADD THIS LINE
        self.skills = SkillLoader()
        self.browser = BrowserController() #Add this        
        self.pending_actions = {}
        self._load_pending_actions()

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
            "ollama_model": "llama3.1:8b",
            "require_approval": False,
            "log_dir": "../logs",
            "vault_dir": "../vault"
        }
        
        if Path(config_path).exists():
            with open(config_path, 'r') as f:
                config.update(json.load(f))
        
        return config
     
    def _load_pending_actions(self):
        try:
            if Path(self.PENDING_FILE).exists():
                with open(self.PENDING_FILE, "r") as f:
                    self.pending_actions = json.load(f)
                
                # Clean expired approvals on startup
                now = time.time()
                cleaned = {}
                for user_id, data in self.pending_actions.items():
                    if now - data["timestamp"] <= self.APPROVAL_TIMEOUT:
                        cleaned[user_id] = data
                    
                self.pending_actions = cleaned
            else:
                self.pending_actions = {}
        except Exception as e:
            print(f"Error loading pending actions: {e}")
            self.pending_actions = {}
    
    def _save_pending_actions(self):
        try:
            with open(self.PENDING_FILE, "w") as f:
                json.dump(self.pending_actions, f)
        except Exception as e:
            print(f"Error saving pending actions: {e}") 
     
    async def process_command(self, user_input, user_id):
        """Main command processing pipeline"""
        
        print(f"\n📥 Command received from {user_id}: {user_input}")
         
        # Slack approval check
        if user_input.strip().upper() == "YES":
            print("Pending actions keys:", list (self.pending_actions.keys()))
            print("Current user_id:", user_id)
            print("MEMORY STATE:", self.pending_actions)

            if user_id in self.pending_actions:            
                pending = self.pending_actions.get(user_id)
                intent = pending["intent"]
                timestamp = pending["timestamp"]
                
                # 5 minute expiration window
                if time.time() - timestamp > self.APPROVAL_TIMEOUT:
                    del self.pending_actions[user_id]
                    self._save_pending_actions()
                    return "Approval expired. Please reissue the command."
                
                # Execute approved action
                del self.pending_actions[user_id]
                self._save_pending_actions()
                 
                result = await self._execute_action(intent)
                return result
            else:
                return "No pending action to approve."

        # NO - Cancel pending action
        if user_input.strip().upper() == "NO":
            if user_id in self.pending_actions:
                del self.pending_actions[user_id]
                self._save_pending_actions()
                return "Action cancelled. Nothing was executed."
            else:
                return "No pending action to cancel."
            
        # Store for later use
        self._last_user_input = user_input

        # Step 1: Use Ollama to understand intent
        intent = await self._analyze_intent(user_input, user_id)
        
        print(f"🧠 Intent: {intent['action']}")
        print(f"📊 Execution Level: {intent['level']}")
        
        # Step 2: Check if approval needed
        if intent['level'] >= self.LEVEL_2_NETWORK and self.config['require_approval']:
            self.pending_actions[user_id] = {
                "intent": intent,
                "timestamp": time.time()
            }

            self._save_pending_actions()

            return (
                "Approval Required\n\n"
                f"Action: {intent['action']}\n"
                f"Parameters: {intent.get('parameters', {})}\n\n"
                "Reply YES to confirm."
            )
        
        # Step 3: Execute based on intent
        result = await self._execute_action(intent)
        
        # Step 4: Log everything
        self._log_action(user_id, user_input, intent, result)
        
        if VOICE_ENABLED:
            speak(str(result))
        return result
    
    async def _analyze_intent(self, user_input, user_id="@benedict:localhost"):
        """Use Ollama to understand what user wants"""
        # Prompt injection protection
        ALLOWED_USERS = ["@benedict:localhost"]
        if not user_id.endswith(":slack") and user_id not in ALLOWED_USERS:
            return {"action": "chat", "level": 0, "parameters": {"user_input": "Unauthorized user"}}
        
        injection_patterns = [
            "ignore previous", "ignore all", "system prompt", 
            "you are now", "pretend you", "forget your", 
            "new instructions", "admin mode", "developer mode",
            "jailbreak", "disregard", "override"
        ]
        message_lower = user_input.lower()
        if user_input.lower() in ["voice on", "voice off"]:
            global VOICE_ENABLED
            VOICE_ENABLED = user_input.lower() == "voice on"
            status = "on" if VOICE_ENABLED else "off"
            return {"action": "chat", "level": 0, "parameters": {"user_input": f"Voice turned {status}"}}
        
        if any(pattern in message_lower for pattern in injection_patterns):
            return {"action": "chat", "level": 0, "parameters": {"user_input": "nice try"}}
        
        
        # Find relevant skills for this query
        relevant_skills = self.skills.find_relevant_skills(user_input)
        skill_context = ""
    
        if relevant_skills:
            skill_context = "\n\nRELEVANT SKILLS:\n"
            for skill in relevant_skills:
                skill_context += f"\n--- {skill['name']} ---\n{skill['content'][:500]}...\n"
    
        from datetime import datetime
        today = datetime.now().strftime("%A, %B %d, %Y, %I:%M %p")
        prompt = f"""You are Zemi, a security-focused AI assistant. Today is {today}. Analyze this command and respond ONLY with a JSON object (no other text):

{skill_context}

User command: "{user_input}"

Determine:
1. action: what type of action (search_web, send_email, read_file, write_file, create_note, read_note, search_notes, list_notes, daily_note, add_event, list_events, chat)
2. level: execution level (0=reasoning only, 1=read-only, 2=network actions including calendar, notes and email, 3=system commands only)
3. parameters: any needed parameters as a dict
4. requires_approval: true if this is a sensitive action

Example responses:
{{"action": "chat", "level": 0, "parameters": {{"user_input": "hey what is up"}}}}
{{"action": "chat", "level": 0, "parameters": {{"user_input": "how are you"}}}}
{{"action": "create_note", "level": 1, "parameters": {{"title": "Meeting Notes", "content": "", "folder": ""}}}}
{{"action": "add_event", "level": 2, "parameters": {{"title": "Leave Work", "start": "2026-02-18T15:00:00", "duration_hours": 1}}}}
{{"action": "search_web", "level": 2, "parameters": {{"query": "weather today"}}}}, "requires_approval": true}}

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
        elif action in ["create_note", "write_note"]:
            return await self._handle_create_note(params)
        elif action in ["read_note", "search_notes", "list_notes"]:
            memory_triggers = ["what did we", "what was decided", "what did i say", "search memory", "recall", "what did we decide", "did we talk about", "do you remember"]
            if any(w in self._last_user_input.lower() for w in memory_triggers):
                params['user_input'] = self._last_user_input
                return await self._handle_chat(params)
            return await self._handle_read_note(params)
        elif action == "daily_note":
            return await self._handle_daily_note(params)
        elif action in ["add_event", "create_event", "add_calendar"]:
            return await self._handle_add_event(params)
        elif action in ["list_events", "check_calendar"]:
            return await self._handle_list_events(params)
        elif action == "run_script":
            return "⚠️ Script execution not enabled yet"
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
        # Check memory first
        user_input = params.get("user_input", "")
        print(f"DEBUG chat handler params: {params}")

        # Check Slack memory FIRST before notes search
        memory_triggers = ["what did we", "what was decided", "what did i say", "search memory", "recall", "what did we decide", "did we talk about", "do you remember"]
        if any(w in user_input.lower() for w in memory_triggers):
            from slack_memory import search_memory
            results = search_memory(user_input)
            if results and results[0] != "No memory found for that query":
                return "Here is what I found:\n" + "\n".join(results)
            else:
                return "I searched my memory but could not find anything about that. Try checking the specific channel directly."

        # Then check Obsidian notes
        from obsidian_handler import search_notes_by_content
        if len(user_input.strip()) > 2:
            matches = [m for m in search_notes_by_content(user_input) if not m["folder"].startswith("Slack")]
            if matches:
                if len(matches) == 1:
                    m = matches[0]
                    response = "\U0001f4cb " + m["title"] + "\n\n"
                    if m.get("excerpt"):
                        response += m["excerpt"] + "\n"
                    return response
                else:
                    response = "\U0001f4cb Relevant notes:\n\n"
                    for i, m in enumerate(matches[:5], 1):
                        response += str(i) + ". " + m["title"] + " (in " + m["folder"] + ")\n"
                    return response


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
                {'role': 'system', 'content': '''You are Zemi - a personal AI assistant running locally on Anthony's Mac Mini. CRITICAL RULES: 1) NEVER invent calendar events, emails, meetings, tasks, deadlines, people or projects - you have NO access to this data unless a tool explicitly retrieved it. 2) If asked about schedule, emails or tasks and no data was retrieved, say exactly: I do not have that data pulled up - ask me to check your calendar or email specifically. 3) For greetings like hey or what is up, respond casually in 1-2 sentences max. No fake updates. No invented context. Just chat. Your job is to make Anthony's day easier: research, email, calendar, notes, and smart conversation. You're not a generic chatbot. You're his assistant, and you know his setup.

TONE: Sound like a sharp, witty friend who happens to know everything - not a customer service bot. Be direct. Skip filler phrases like "Certainly!", "Great question!", "Of course!" - just answer. Match energy: casual when he's casual, focused when he's working. If something is blocked or broken, say so plainly and tell him what to do next. Never repeat what he just said back to him before answering.

HUMOR & SARCASM: You have a dry sense of humor. Use it. Light sarcasm is welcome when the moment calls for it - especially when he asks you something obvious or does something inefficient. Keep it punchy, never mean. Think witty assistant, not class clown. One liner when appropriate, then get back to business.

RESPONSE STYLE: Lead with the answer, not preamble. Use plain language. Bullet points only when there is a real list. If you are unsure, say so - do not hallucinate confidence. For quick tasks: confirm what you did, done. Keep it short.

IDENTITY: You run on Anthony's hardware. His data stays local. You know his projects: Zemi development, client websites, coursework. You are always improving. If something does not work, acknowledge it and move on.

AVOID: Inventing physical details like what is on his desk, what he is drinking, or anything you cannot actually know. AVOID: "I'd be happy to help!" - just help. "As an AI language model..." - you are Zemi, full stop. Hollow affirmations. Restating the question before answering. Explaining the joke.'''},
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
        if VOICE_ENABLED:
            speak(str(result))
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
    
    async def _handle_create_note(self, params):
        from obsidian_handler import create_note
        title = params.get('title', 'Untitled')
        content = params.get('content', '')
        folder = params.get('folder', '')
        return create_note(title, content, folder)

    async def _handle_read_note(self, params):
        from slack_memory import enhanced_read_note
        search_term = params.get("query", params.get("title", self._last_user_input))
        result = enhanced_read_note(search_term)
        if result and "not found" not in result.lower():
            return result
        return f"No notes found related to '{search_term}'."

        


    async def _handle_daily_note(self, params):
        from obsidian_handler import daily_note
        return daily_note()

    async def _handle_add_event(self, params):
        from calendar_handler import add_event
        from datetime import datetime, timedelta
        title = params.get('title', 'New Event')
        start_str = params.get('start', '')
        try:
            start = datetime.fromisoformat(start_str)
        except:
            start = datetime.now() + timedelta(days=1)
            start = start.replace(hour=14, minute=0, second=0, microsecond=0)
        duration = float(params.get('duration_hours', 1.0))
        return add_event(title, start, duration)

    async def _handle_list_events(self, params):
        from calendar_handler import list_events
        days = int(params.get('days_ahead', 7))
        return list_events(days)

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
