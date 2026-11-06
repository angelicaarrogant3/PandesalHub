import os
import re

files = [
    r"c:\Users\Admin\Desktop\pandesalhub\pandesal\templates\pandesal\seller\seller_base.html",
    r"c:\Users\Admin\Desktop\pandesalhub\pandesal\templates\pandesal\messages_inbox.html",
    r"c:\Users\Admin\Desktop\pandesalhub\pandesal\templates\pandesal\user_profile.html",
    r"c:\Users\Admin\Desktop\pandesalhub\pandesal\templates\pandesal\notifications.html"
]

def update_file(filepath):
    if not os.path.exists(filepath):
        print(f"Not found: {filepath}")
        return
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # By ensuring it has sidebar-text
    content = re.sub(r'<a href="\{% url \'user_notifications\' %\}"[^>]*><i class="fa-solid fa-bell text-lg min-w-\[20px\]"></i><span class="sidebar-text">Notifications</span></a>', '', content)

    # Rename Dashboard to Home in the sidebar
    content = re.sub(r'(<a href="\{% url \'seller_dashboard\' %\}"[^>]*><i class="fa-solid fa-house text-lg min-w-\[20px\]"></i><span class="sidebar-text">)Dashboard(</span></a>)', r'\g<1>Home\g<2>', content)

    # Rename My Shop to Shop in the sidebar
    content = re.sub(r'(<a href="\{% url \'seller_shop_settings\' %\}"[^>]*><i class="fa-solid fa-store text-lg min-w-\[20px\]"></i><span class="sidebar-text">)My Shop(</span></a>)', r'\g<1>Shop\g<2>', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {filepath}")

for f in files:
    update_file(f)

