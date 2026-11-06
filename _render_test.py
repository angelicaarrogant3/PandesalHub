import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pandesalhub.settings")
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.template.loader import render_to_string

factory = RequestFactory()
request = factory.get("/messages/")
request.user = AnonymousUser()
# give a resolver_match so base sidebar active checks don't blow up
from django.urls import resolve
request.resolver_match = resolve("/messages/")

for name in ["pandesal/admin_messages_inbox.html", "pandesal/admin_messages_thread.html"]:
    ctx = {
        "recent_threads": [],
        "all_users": [],
        "other_user": None,
        "messages_list": [],
        "all_threads": [],
    }
    try:
        html = render_to_string(name, ctx, request=request)
        print(f"RENDER OK  {name}  ({len(html)} chars)")
    except Exception as e:
        print(f"RENDER FAIL {name} -> {type(e).__name__}: {e}")
