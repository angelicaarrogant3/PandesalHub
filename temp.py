
import re

filepath = 'c:/Users/Admin/Desktop/pandesalhub/pandesal/views.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

funcs = {
    'admin_product_create': '''    messages.error(request, 'Admins can only view products. Product management is restricted to Sellers.')\n    return redirect('admin_products')\n''',
    'admin_product_edit': '''    messages.error(request, 'Admins can only view products. Product management is restricted to Sellers.')\n    return redirect('admin_products')\n''',
    'admin_product_delete': '''    messages.error(request, 'Admins can only view products. Product management is restricted to Sellers.')\n    return redirect('admin_products')\n''',
    'admin_orders': '''    messages.error(request, 'Order management is handled by Sellers.')\n    return redirect('admin_dashboard')\n''',
    'admin_order_detail': '''    messages.error(request, 'Order management is handled by Sellers.')\n    return redirect('admin_dashboard')\n''',
    'admin_order_delete': '''    messages.error(request, 'Order management is handled by Sellers.')\n    return redirect('admin_dashboard')\n''',
    'admin_bulk_delete_orders': '''    messages.error(request, 'Order management is handled by Sellers.')\n    return redirect('admin_dashboard')\n'''
}

for func, body in funcs.items():
    pattern = r'(def ' + func + r'\(.*?\):).*?(?=\n@|\ndef |\Z)'
    content = re.sub(pattern, r'\1\n' + body, content, flags=re.MULTILINE | re.DOTALL)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('views.py updated')

filepath = 'c:/Users/Admin/Desktop/pandesalhub/pandesal/reservation_views.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

res_funcs = [
    'admin_reservations',
    'admin_reservation_detail',
    'admin_reservation_confirm',
    'admin_reservation_reject',
    'admin_reservation_complete',
    'admin_bulk_delete_reservations'
]

body = '''    from django.contrib import messages
    from django.shortcuts import redirect
    messages.error(request, 'Reservation management is handled by Sellers.')
    return redirect('admin_dashboard')\n'''

for func in res_funcs:
    pattern = r'(def ' + func + r'\(.*?\):).*?(?=\n@|\ndef |\Z)'
    content = re.sub(pattern, r'\1\n' + body, content, flags=re.MULTILINE | re.DOTALL)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('reservation_views.py updated')

