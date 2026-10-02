import os
import re

files = [
    r"c:\Users\Admin\Desktop\pandesalhub\pandesal\templates\pandesal\seller\seller_base.html",
    r"c:\Users\Admin\Desktop\pandesalhub\pandesal\templates\pandesal\messages_inbox.html",
    r"c:\Users\Admin\Desktop\pandesalhub\pandesal\templates\pandesal\user_profile.html",
    r"c:\Users\Admin\Desktop\pandesalhub\pandesal\templates\pandesal\notifications.html"
]

for filepath in files:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Regex to remove the Notifications sidebar link
        content = re.sub(r'<a href="{% url \'user_notifications\' %}".*?<span class="sidebar-text">Notifications</span></a>', '', content, flags=re.DOTALL)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")
