import os
import glob

# Directories and files to process
base_dir = r"c:\Users\Admin\Desktop\pandesalhub"

def process_file(filepath):
    # Exclude migrations and node_modules and .git and binary files
    if "migrations" in filepath or "node_modules" in filepath or ".git" in filepath or "media" in filepath or "staticfiles" in filepath or "public" in filepath:
        return
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        return # Skip binary or non-utf8 files
        
    original = content
    # Case sensitive replacements
    content = content.replace("Pandesal", "Pandesal")
    content = content.replace("pandesal", "pandesal")
    content = content.replace("PANDESAL", "PANDESAL")
    
    if original != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {filepath}")

def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.py', '.html', '.js', '.css', '.json', '.txt')):
                process_file(os.path.join(root, file))

if __name__ == "__main__":
    process_directory(base_dir)
    print("Done renaming Pandesal to Pandesal.")
