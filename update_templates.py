import os
import re

BASE_DIR = r"c:\Users\Admin\Desktop\pandesalhub\pandesal\templates\pandesal"

def process_index():
    path = os.path.join(BASE_DIR, "index.html")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace CSS
    css_pattern = re.compile(r'    /\* Header styles \*/.*?(?=    /\* Hero Grid \*/)', re.DOTALL)
    content = css_pattern.sub('    {% include "pandesal/includes/guest_navbar_style.html" %}\n', content)

    # Replace Header + Sidebar + JS
    html_pattern = re.compile(r'  <!-- Header / Navigation -->.*?  <!-- Hero Section', re.DOTALL)
    content = html_pattern.sub('  {% include "pandesal/includes/guest_navbar.html" %}\n\n  <!-- Hero Section', content)

    # Remove JS from bottom of index.html
    js_pattern = re.compile(r'  <script>\n    function toggleMobileMenu.*?  </script>\n', re.DOTALL)
    content = js_pattern.sub('', content)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def process_shop():
    path = os.path.join(BASE_DIR, "shop.html")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace CSS
    css_pattern = re.compile(r'    /\* Header styles \*/.*?(?=    \.shop-container \{)', re.DOTALL)
    content = css_pattern.sub('    {% include "pandesal/includes/guest_navbar_style.html" %}\n', content)

    # Replace Header
    html_pattern = re.compile(r'  <!-- Header / Navigation -->.*?  <!-- Shop Content Section -->', re.DOTALL)
    content = html_pattern.sub('  {% include "pandesal/includes/guest_navbar.html" %}\n\n  <!-- Shop Content Section -->', content)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def process_about():
    path = os.path.join(BASE_DIR, "about.html")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # For about, we need to inject the style include in the head block.
    # Currently it has a <style> block at line 24. We'll append it before </style>.
    if '{% include "pandesal/includes/guest_navbar_style.html" %}' not in content:
        content = content.replace('</style>', '    {% include "pandesal/includes/guest_navbar_style.html" %}\n  </style>')

    # Replace Guest Header
    # From <!-- Navbar --> down to </header>
    html_pattern = re.compile(r'  <!-- Navbar -->.*?  </header>', re.DOTALL)
    content = html_pattern.sub('  {% include "pandesal/includes/guest_navbar.html" %}', content)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def process_contact():
    path = os.path.join(BASE_DIR, "contact.html")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Add <style> block in head for guest navbar style
    if '{% include "pandesal/includes/guest_navbar_style.html" %}' not in content:
        head_end = content.find('</head>')
        if head_end != -1:
            style_inject = '\n  <style>\n    {% include "pandesal/includes/guest_navbar_style.html" %}\n  </style>\n'
            content = content[:head_end] + style_inject + content[head_end:]

    # Replace Guest Header
    # From <header class="bg-white shadow-md"> down to </header>
    html_pattern = re.compile(r'  <header class="bg-white shadow-md">.*?</header>', re.DOTALL)
    content = html_pattern.sub('  {% include "pandesal/includes/guest_navbar.html" %}', content)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    process_index()
    process_shop()
    process_about()
    process_contact()
    print("Done updating templates.")
