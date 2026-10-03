
import re

filepath = 'c:/Users/Admin/Desktop/pandesalhub/pandesal/seller_views.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'(def seller_shop_settings\(request\):).*?(?=\n@|\ndef |\Z)'
body = '''    from django.contrib import messages
    from django.shortcuts import redirect
    messages.error(request, \'The Shop Settings feature has been disabled.\')
    return redirect(\'seller_dashboard\')
'''

new_content = re.sub(pattern, r'\1\n' + body, content, flags=re.MULTILINE | re.DOTALL)
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)
print('Disabled view')

