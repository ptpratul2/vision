import os
import glob
import shutil

app_dir = "/home/frappe-user/frappe-bench/apps/vision"
old_name = "vision"
new_name = "vision"

old_module = "Vision"
new_module = "Vision"

old_title = "Vision"
new_title = "Vision"

def replace_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return # Skip binary or unreadable files

    if old_name in content or old_module in content or old_title in content:
        new_content = content.replace(old_name, new_name)
        new_content = new_content.replace(old_module, new_module)
        new_content = new_content.replace(old_title, new_title)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated: {filepath}")

def main():
    # 1. Replace text in all files
    for root, dirs, files in os.walk(app_dir):
        if '.git' in root or 'node_modules' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith(('.py', '.js', '.json', '.html', '.md', '.txt', '.toml', '.csv')):
                replace_in_file(os.path.join(root, file))
                
    # 2. Rename internal directories and files
    for root, dirs, files in os.walk(app_dir, topdown=False):
        if '.git' in root:
            continue
        
        # Rename files
        for file in files:
            if old_name in file:
                old_path = os.path.join(root, file)
                new_path = os.path.join(root, file.replace(old_name, new_name))
                os.rename(old_path, new_path)
                print(f"Renamed file: {old_path} -> {new_path}")
                
        # Rename dirs
        for d in dirs:
            if old_name in d:
                old_path = os.path.join(root, d)
                new_path = os.path.join(root, d.replace(old_name, new_name))
                os.rename(old_path, new_path)
                print(f"Renamed dir: {old_path} -> {new_path}")

if __name__ == "__main__":
    main()
