import os
import json
from datetime import datetime

VAULT_PATH = "/Users/zemi/ZemiVault"
MEMORY_PATH = f"{VAULT_PATH}/Slack"

# Import the search function from obsidian_handler
from obsidian_handler import search_notes_by_content, read_note as obsidian_read_note

def ensure_dirs():
    os.makedirs(MEMORY_PATH, exist_ok=True)
    # Only create directories for items that are directories
    if os.path.exists(MEMORY_PATH):
        for item in os.listdir(MEMORY_PATH):
            item_path = os.path.join(MEMORY_PATH, item)
            if os.path.isdir(item_path):
                os.makedirs(item_path, exist_ok=True)

def log_message(channel, user, message, response):
    # Create the channel directory if it doesn't exist
    channel_dir = os.path.join(MEMORY_PATH, channel)
    os.makedirs(channel_dir, exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(channel_dir, f"{today}.md")
    
    timestamp = datetime.now().strftime("%H:%M")
    entry = f"\n## {timestamp}\n**{user}:** {message}\n**Zemi:** {response}\n"
    
    with open(filepath, 'a') as f:
        f.write(entry)

def enhanced_read_note(query):
    """
    Enhanced note reading that searches both titles and content across ALL notes
    """
    # First try exact title match
    title_result = obsidian_read_note(query)
    if "not found" not in title_result.lower():
        return title_result
    
    # If not found by title, search by content
    content_matches = search_notes_by_content(query)
    
    if content_matches:
        response = "📝 *Found these relevant notes (from all folders):*\n\n"
        for i, match in enumerate(content_matches[:3], 1):  # Show top 3
            response += f"*{i}. {match['title']}* (in _{match['folder']}_)\n"
            if match.get('excerpt'):
                response += f"   > {match['excerpt']}\n"
            response += "\n"
        return response
    
    return f"No notes found related to '{query}'. Try creating one with `create_note`."

def search_memory(query):
    ensure_dirs()
    results = []
    query_lower = query.lower()
    
    # Search Slack memory
    if os.path.exists(MEMORY_PATH):
        for channel in os.listdir(MEMORY_PATH):
            channel_path = os.path.join(MEMORY_PATH, channel)
            if os.path.isdir(channel_path):
                for filename in os.listdir(channel_path):
                    if filename.endswith('.md'):
                        filepath = os.path.join(channel_path, filename)
                        try:
                            with open(filepath, 'r') as f:
                                content = f.read()
                            if query_lower in content.lower():
                                # Find the relevant section
                                pos = content.lower().find(query_lower)
                                start = max(0, pos - 100)
                                end = min(len(content), pos + 200)
                                excerpt = content[start:end]
                                if start > 0:
                                    excerpt = "..." + excerpt
                                if end < len(content):
                                    excerpt = excerpt + "..."
                                results.append(f"#{channel} ({filename}): {excerpt}")
                        except Exception as e:
                            print(f"Error reading {filepath}: {e}")
    
    # Also search main vault notes
    vault_results = search_notes_by_content(query)
    for match in vault_results[:2]:  # Add top 2 vault results
        folder_info = f" in {match['folder']}" if match['folder'] != 'root' else ""
        excerpt = match.get('excerpt', match.get('content', '')[:100])
        results.append(f"📔 Note: {match['title']}{folder_info}\n   > {excerpt}")
    
    return results[:5] if results else ["No memory found for that query"]
