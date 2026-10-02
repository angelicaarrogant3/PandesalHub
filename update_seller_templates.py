import os
import re

TEMPLATES_DIR = r"c:\Users\Admin\Desktop\pandesalhub\pandesal\templates\pandesal\seller"

files_to_update = [
    'shop_settings.html',
    'products.html',
    'product_form.html',
    'orders.html',
    'order_detail.html',
    'reservations.html',
    'reservation_detail.html',
]

for filename in files_to_update:
    filepath = os.path.join(TEMPLATES_DIR, filename)
    if not os.path.exists(filepath):
        continue
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if '{% extends' in content:
        continue
        
    # Replace the top part
    # Look for <main class="flex-1 p-8"> or similar
    main_match = re.search(r'<main[^>]*>', content)
    if main_match:
        main_start = main_match.end()
        # Find closing </main>
        main_end = content.rfind('</main>')
        
        if main_start != -1 and main_end != -1:
            main_content = content[main_start:main_end].strip()
            
            # Find the title if possible
            title_match = re.search(r'<title>(.*?)</title>', content)
            title = title_match.group(1) if title_match else "Seller Dashboard"
            
            new_content = f"{{% extends 'pandesal/seller/seller_base.html' %}}\n\n{{% block title %}}{title}{{% endblock %}}\n\n{{% block content %}}\n{main_content}\n{{% endblock %}}\n"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {filename}")
        else:
            print(f"Could not find main tags in {filename}")
    else:
        print(f"Could not find <main> in {filename}")

print("Done.")
