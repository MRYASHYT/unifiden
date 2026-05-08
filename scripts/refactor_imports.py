import os
import re

def refactor_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Define the modules to update
    modules = ['agents', 'analysis', 'data', 'debate', 'evaluation', 'metrics', 'security']
    
    new_content = content
    for module in modules:
        # Replace 'from module' with 'from agentstress.module'
        new_content = re.sub(rf'^from {module}(\.|\s)', rf'from agentstress.{module}\1', new_content, flags=re.MULTILINE)
        # Replace 'import module' with 'import agentstress.module'
        new_content = re.sub(rf'^import {module}(\.|\s)', rf'import agentstress.{module}\1', new_content, flags=re.MULTILINE)

    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    root_dir = r'C:\Users\yashg\agentstress'
    target_dirs = [
        os.path.join(root_dir, 'agentstress'),
        os.path.join(root_dir, 'dashboard'),
        os.path.join(root_dir, 'experiments'),
        os.path.join(root_dir, 'tests'),
    ]
    target_files = [os.path.join(root_dir, 'main.py')]

    all_files = []
    for d in target_dirs:
        for root, dirs, files in os.walk(d):
            for file in files:
                if file.endswith('.py'):
                    all_files.append(os.path.join(root, file))
    
    all_files.extend(target_files)

    count = 0
    for file_path in all_files:
        if refactor_file(file_path):
            print(f"Refactored: {file_path}")
            count += 1
    
    print(f"Total files refactored: {count}")

if __name__ == "__main__":
    main()
