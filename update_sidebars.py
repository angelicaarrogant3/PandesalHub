import os

files = [
    r"c:\Users\Admin\Desktop\pandesalhub\pandesal\templates\pandesal\messages_inbox.html",
    r"c:\Users\Admin\Desktop\pandesalhub\pandesal\templates\pandesal\user_profile.html",
    r"c:\Users\Admin\Desktop\pandesalhub\pandesal\templates\pandesal\user_notifications.html"
]

seller_links = """
      {% if user.userprofile.user_type == 'seller' %}
      <a href="{% url 'seller_dashboard' %}" class="flex items-center gap-4 px-4 py-3 rounded-xl text-gray-600 hover:text-green-700 hover:bg-green-50 transition"><i class="fa-solid fa-house text-lg min-w-[20px]"></i><span class="sidebar-text">Dashboard</span></a>
      <a href="{% url 'seller_shop_settings' %}" class="flex items-center gap-4 px-4 py-3 rounded-xl text-gray-600 hover:text-green-700 hover:bg-green-50 transition"><i class="fa-solid fa-store text-lg min-w-[20px]"></i><span class="sidebar-text">My Shop</span></a>
      <a href="{% url 'seller_products' %}" class="flex items-center gap-4 px-4 py-3 rounded-xl text-gray-600 hover:text-green-700 hover:bg-green-50 transition"><i class="fa-solid fa-box text-lg min-w-[20px]"></i><span class="sidebar-text">Products</span></a>
      <a href="{% url 'seller_orders' %}" class="flex items-center gap-4 px-4 py-3 rounded-xl text-gray-600 hover:text-green-700 hover:bg-green-50 transition"><i class="fa-solid fa-shopping-cart text-lg min-w-[20px]"></i><span class="sidebar-text">Orders</span></a>
      <a href="{% url 'seller_reservations' %}" class="flex items-center gap-4 px-4 py-3 rounded-xl text-gray-600 hover:text-green-700 hover:bg-green-50 transition"><i class="fa-solid fa-calendar-check text-lg min-w-[20px]"></i><span class="sidebar-text">Reservations</span></a>
      <a href="{% url 'messages_inbox' %}" class="flex items-center gap-4 px-4 py-3 rounded-xl {% if request.resolver_match.url_name == 'messages_inbox' %}text-green-700 bg-green-50 hover:bg-green-100{% else %}text-gray-600 hover:text-green-700 hover:bg-green-50{% endif %} transition relative"><i class="fa-solid fa-message text-lg min-w-[20px]"></i><span class="sidebar-text">Messages</span>{% if unread_messages_count > 0 %}<span class="absolute right-3 top-1/2 -translate-y-1/2 bg-red-500 text-white text-xs font-bold rounded-full min-w-[20px] h-5 flex items-center justify-center px-1.5">{{ unread_messages_count }}</span>{% endif %}</a>
      <a href="{% url 'user_notifications' %}" class="flex items-center gap-4 px-4 py-3 rounded-xl {% if request.resolver_match.url_name == 'user_notifications' %}text-green-700 bg-green-50 hover:bg-green-100{% else %}text-gray-600 hover:text-green-700 hover:bg-green-50{% endif %} transition"><i class="fa-solid fa-bell text-lg min-w-[20px]"></i><span class="sidebar-text">Notifications</span></a>
      <a href="{% url 'user_profile' %}" class="flex items-center gap-4 px-4 py-3 rounded-xl {% if request.resolver_match.url_name == 'user_profile' %}text-green-700 bg-green-50 hover:bg-green-100{% else %}text-gray-600 hover:text-green-700 hover:bg-green-50{% endif %} transition"><i class="fa-solid fa-user-circle text-lg min-w-[20px]"></i><span class="sidebar-text">Profile / Settings</span></a>
      {% else %}
"""

for filepath in files:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        start_marker = '<nav class="mt-8 px-4 space-y-2 text-base flex-1 overflow-y-auto">'
        
        parts = content.split(start_marker, 1)
        if len(parts) == 2:
            nav_inner, rest = parts[1].split('</nav>', 1)
            
            new_nav = start_marker + "\n" + seller_links + nav_inner + "\n      {% endif %}\n      </nav>"
            new_content = parts[0] + new_nav + rest
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {filepath}")
