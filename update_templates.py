import os
import re

directory = r'c:\Users\Admin\Desktop\pandesalhub\pandesal\templates\pandesal\seller'

for filename in os.listdir(directory):
    if filename.endswith('.html') and filename != 'shop_settings.html':
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'seller_shop_settings' not in content:
            pattern = r'(<a href="\{\%\s*url\s*\'seller_reservations\'\s*\%\}"[^>]*>.*?</a>)'
            replacement = r'\1\n        <a href="{% url \'seller_shop_settings\' %}" class="block px-4 py-2 text-gray-700 hover:bg-green-50 hover:text-green-700 rounded transition"><i class="fas fa-store w-6"></i> Shop Settings</a>'
            
            new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
                print(f"Updated {filename}")
