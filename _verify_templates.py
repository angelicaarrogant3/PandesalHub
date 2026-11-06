import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pandesalhub.settings")
django.setup()

from django.template.loader import get_template

templates = [
    "pandesal/includes/admin_base.html",
    "pandesal/admin_products.html",
    "pandesal/admin_users.html",
    "pandesal/admin_sellers.html",
    "pandesal/admin_content.html",
    "pandesal/admin_orders.html",
    "pandesal/admin_reservations.html",
    "pandesal/admin_notifications.html",
    "pandesal/admin_order_detail.html",
    "pandesal/admin_reservation_detail.html",
    "pandesal/admin_product_form.html",
    "pandesal/admin_product_delete.html",
    "pandesal/admin_messages_inbox.html",
    "pandesal/admin_messages_thread.html",
    "pandesal/messages_inbox.html",
    "pandesal/messages_thread.html",
]

fail = 0
for t in templates:
    try:
        get_template(t)
        print(f"OK   {t}")
    except Exception as e:
        fail += 1
        print(f"FAIL {t} -> {type(e).__name__}: {e}")

print(f"\n{len(templates) - fail}/{len(templates)} templates compiled.")
