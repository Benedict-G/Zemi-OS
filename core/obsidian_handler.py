import os
from datetime import datetime

VAULT_PATH = "/Users/zemi/Documents/ZemiVault"

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

def read_note(title):
    for root, dirs, files in os.walk(VAULT_PATH):
        for file in files:
            if file.lower() == title.lower().replace(' ', '_') + ".md":
                with open(os.path.join(root, file), 'r') as f:
                    return f.read()
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
