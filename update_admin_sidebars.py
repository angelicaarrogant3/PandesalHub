import os
import re
import glob

def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    # Remove Admin Orders link
    content = re.sub(r'<a href="\{% url \'admin_orders\' %\}"[^>]*>.*?<span class="sidebar-text">Orders</span></a>', '', content, flags=re.DOTALL)
    # Remove Admin Reservations link
    content = re.sub(r'<a href="\{% url \'admin_reservations\' %\}"[^>]*>.*?<span class="sidebar-text">Reservations</span></a>', '', content, flags=re.DOTALL)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")

if __name__ == "__main__":
    search_path = os.path.join("c:\\Users\\Admin\\Desktop\\pandesalhub\\pandesal\\templates\\pandesal", "*.html")
    for file in glob.glob(search_path):
        update_file(file)
    print("Done")
