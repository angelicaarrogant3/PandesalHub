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

    # To avoid matching too much, let's process line by line or use a more specific regex.
    # The notification link to remove looks like:
    # <a href="{% url 'user_notifications' %}" class="flex items-center gap-4 px-4 py-3 rounded-xl {% if request.resolver_match.url_name == 'user_notifications' %}text-green-700 bg-green-50 hover:bg-green-100{% else %}text-gray-600 hover:text-green-700 hover:bg-green-50{% endif %} transition"><i class="fa-solid fa-bell text-lg min-w-[20px]"></i><span class="sidebar-text">Notifications</span></a>
    
    # Let's find the exact string that is the notifications link in the sidebar
    # We will look for <a href="{% url 'user_notifications' %}" ... ><i class="fa-solid fa-bell text-lg min-w-[20px]"></i><span class="sidebar-text">Notifications</span></a>
    
    # Remove notifications link from sidebar specifically
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

