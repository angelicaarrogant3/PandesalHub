import re

shop_user_path = r'c:\Users\Admin\Desktop\pandesalhub\pandesal\templates\pandesal\shop_user.html'
shop_path = r'c:\Users\Admin\Desktop\pandesalhub\pandesal\templates\pandesal\shop.html'

filter_html = """
    <!-- Shop Filters -->
    {% if shops %}
    <div class="px-6 py-4 bg-gray-50 border-b border-gray-200 overflow-x-auto">
      <div class="flex items-center gap-3 whitespace-nowrap">
        <span class="text-sm font-semibold text-gray-600 mr-2"><i class="fas fa-filter mr-1"></i> Shop:</span>
        <a href="?{% if search_query %}search={{ search_query }}{% endif %}" 
           class="px-4 py-1.5 rounded-full text-sm font-medium transition-colors border {% if not selected_shop %}bg-green-600 text-white border-green-600 shadow-sm{% else %}bg-white text-gray-700 border-gray-300 hover:bg-gray-50{% endif %}">
          All Shops
        </a>
        {% for shop in shops %}
        <a href="?shop={{ shop.id }}{% if search_query %}&search={{ search_query }}{% endif %}" 
           class="flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-medium transition-colors border {% if selected_shop == shop.id %}bg-green-600 text-white border-green-600 shadow-sm{% else %}bg-white text-gray-700 border-gray-300 hover:bg-gray-50{% endif %}">
          {% if shop.logo %}
            <img src="{{ shop.logo.url }}" alt="{{ shop.shop_name }}" class="w-5 h-5 rounded-full object-cover">
          {% else %}
            <div class="w-5 h-5 rounded-full bg-gray-200 flex items-center justify-center text-[10px] text-gray-500"><i class="fas fa-store"></i></div>
          {% endif %}
          {{ shop.shop_name }}
        </a>
        {% endfor %}
      </div>
    </div>
    {% endif %}
"""

for filepath in [shop_user_path, shop_path]:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if "<!-- Shop Filters -->" not in content:
        # We find the end of the banner block.
        # It usually ends right before <!-- Django Messages -->
        pattern = r"(</div>\s*<!-- Django Messages -->)"
        
        new_content = re.sub(pattern, filter_html + r"\1", content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
            print(f"Updated {filepath}")
