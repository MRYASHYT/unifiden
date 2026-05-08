import os

def replace_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = content.replace('AgentStress', 'AgentStress').replace('agentstress', 'agentstress').replace('AGENTSTRESS', 'AGENTSTRESS')
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {filepath}")
    except Exception as e:
        pass # Skip binary files or unreadable files

def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        if '.git' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith(('.py', '.md', '.json', '.txt', '.yml', '.tex')):
                filepath = os.path.join(root, file)
                replace_in_file(filepath)

if __name__ == "__main__":
    process_directory(os.getcwd())
    
    # Rename specific files if they exist
    old_spec = "AGENTSTRESS_SPECIFICATION.md"
    new_spec = "AGENTSTRESS_SPECIFICATION.md"
    if os.path.exists(old_spec):
        os.rename(old_spec, new_spec)
        print(f"Renamed {old_spec} to {new_spec}")
        
    old_stats = "analysis/agentstress_stats.py"
    new_stats = "analysis/agentstress_stats.py"
    if os.path.exists(old_stats):
        os.rename(old_stats, new_stats)
        print(f"Renamed {old_stats} to {new_stats}")
