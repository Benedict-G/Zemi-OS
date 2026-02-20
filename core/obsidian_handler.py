import os
from datetime import datetime

VAULT_PATH = "/Users/zemi/ZemiVault"

def create_note(title, content, folder=""):
    folder_path = os.path.join(VAULT_PATH, folder) if folder else VAULT_PATH
    os.makedirs(folder_path, exist_ok=True)
    filename = title.replace(' ', '_') + ".md"
    filepath = os.path.join(folder_path, filename)
    with open(filepath, 'w') as f:
        f.write("# " + title + "\n")
        f.write("Created: " + datetime.now().strftime('%B %d, %Y %I:%M %p') + "\n\n")
        f.write(content)
    return "Note '" + title + "' created in " + (folder or 'vault root')

def search_notes_by_content(search_term):
    """
    Search for notes containing the search term in their content
    Returns list of matching notes with excerpts
    """
    results = []
    search_term_lower = search_term.lower()
    
    for root, dirs, files in os.walk(VAULT_PATH):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if search_term_lower in content.lower():
                        # Count occurrences for relevance
                        score = content.lower().count(search_term_lower)
                        if search_term_lower in file.lower():
                            score += 5
                        if "Slack" in root:
                            score -= 2
                        
                        # Get excerpt around the match
                        excerpt = extract_excerpt(content, search_term)
                        
                        # Get relative path
                        rel_path = os.path.relpath(filepath, VAULT_PATH)
                        folder = os.path.dirname(rel_path)
                        if folder == '.':
                            folder = 'root'
                        
                        results.append({
                            'file': file,
                            'path': rel_path,
                            'folder': folder,
                            'title': file.replace('.md', '').replace('_', ' '),
                            'score': score,
                            'excerpt': excerpt
                        })
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
    
    # Sort by relevance
    results.sort(key=lambda x: x['score'], reverse=True)
    return results

def extract_excerpt(content, search_term, context_chars=100):
    """Extract text around the search term for context"""
    import re
    
    # Find the position of the search term
    match = re.search(re.escape(search_term), content, re.IGNORECASE)
    if match:
        start = max(0, match.start() - context_chars)
        end = min(len(content), match.end() + context_chars)
        excerpt = content[start:end]
        # Add ellipsis if we truncated
        if start > 0:
            excerpt = "..." + excerpt
        if end < len(content):
            excerpt = excerpt + "..."
        return excerpt
    return ""

def read_note(title):
    # First try exact title match
    for root, dirs, files in os.walk(VAULT_PATH):
        for file in files:
            expected_filename = title.lower().replace(' ', '_') + ".md"
            if file.lower() == expected_filename:
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    return f.read()
    
    # If not found by title, search by content
    content_matches = search_notes_by_content(title)
    if content_matches:
        response = f"Note '{title}' not found by title, but found these notes containing that text:\n\n"
        for i, match in enumerate(content_matches[:3], 1):
            response += f"{i}. {match['title']} (in {match['folder']})\n"
            if match['excerpt']:
                response += f"   > {match['excerpt']}\n"
        return response
    
    return "Note '" + title + "' not found"

def search_notes(query):
    results = []
    for root, dirs, files in os.walk(VAULT_PATH):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                if query.lower() in content.lower():
                    results.append("- " + file.replace('.md', '').replace('_', ' '))
    if not results:
        return "No notes found containing: " + query
    return "Found " + str(len(results)) + " note(s):\n" + "\n".join(results)

def daily_note():
    today = datetime.now().strftime('%Y-%m-%d')
    title = "Daily_" + today
    content = "## Tasks\n- \n\n## Notes\n\n## Progress\n"
    return create_note(title, content, "Daily")

def list_notes():
    results = []
    for root, dirs, files in os.walk(VAULT_PATH):
        for file in files:
            if file.endswith('.md'):
                rel_path = os.path.relpath(os.path.join(root, file), VAULT_PATH)
                results.append("- " + rel_path)
    if not results:
        return "No notes found"
    return str(len(results)) + " notes:\n" + "\n".join(results)

if __name__ == "__main__":
    print("Testing Obsidian handler...")
    print(list_notes())
    print(daily_note())
    print(list_notes())
