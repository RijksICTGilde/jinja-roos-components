#!/usr/bin/env python3
"""
Examples of correct menubar data formats and usage patterns.
"""

# Example 1: Basic menu structure
basic_menu = [
    {
        'label': 'Home',
        'link': '/',
        'selected': True  # Always shows as selected/active
    },
    {
        'label': 'About',
        'link': '/about'
    },
    {
        'label': 'Services',
        'link': '/services'
    },
    {
        'label': 'Contact',
        'link': '/contact',
        'align': 'right'  # This item will appear on the right side
    }
]

# Example 2: Menu with icons and submenus
advanced_menu = [
    {
        'label': 'Dashboard',
        'link': '/dashboard',
        'icon': 'home',
        'selected': True  # Always shows as selected/active
    },
    {
        'label': 'Products',
        'link': '#',
        'icon': 'box',
        'submenu': [
            {
                'label': 'All Products',
                'link': '/products'
            },
            {
                'label': 'New Product',
                'link': '/products/new'
            },
            {
                'label': 'Categories',
                'link': '/categories'
            }
        ]
    },
    {
        'label': 'Reports',
        'link': '/reports',
        'icon': 'bar-chart'
    },
    {
        'label': 'Settings',
        'link': '/settings',
        'icon': 'settings',
        'align': 'right'
    },
    {
        'label': 'Logout',
        'link': '/logout',
        'icon': 'log-out',
        'align': 'right',
        'useDivider': True  # Adds a visual separator before this item
    }
]

# Example 3: Template usage examples
template_examples = {
    'using_variable': '''
<!-- In your Python/Flask code -->
menu_items = [
    {'label': 'Home', 'link': '/', 'selected': True},  # Always selected
    {'label': 'About', 'link': '/about'}
]

<!-- In your Jinja2 template -->
<c-menubar :items="menu_items" />
''',
    
    'inline_data': '''
<!-- Inline data structure -->
<c-menubar :items="[
    {'label': 'Home', 'link': '/', 'selected': true},  # Always selected
    {'label': 'About', 'link': '/about'},
    {'label': 'Contact', 'link': '/contact', 'align': 'right'}
]" />
''',

    'with_options': '''
<!-- With additional menubar options -->
<c-menubar 
    :items="navigation_menu"
    size="lg"
    :useIcons="true"
    iconPlacement="before"
    linkColor="hemelblauw"
    maxWidth="lg" />
''',
    
    'common_mistakes': '''
<!-- ❌ WRONG: Using items without colon (treats as string) -->
<c-menubar items="menu_data" />

<!-- ❌ WRONG: Python-style boolean -->
<c-menubar :items="menu_data" useIcons="True" />

<!-- ✅ CORRECT: Using binding syntax with colon -->
<c-menubar :items="menu_data" />

<!-- ✅ CORRECT: Jinja-style boolean -->
<c-menubar :items="menu_data" :useIcons="true" />
'''
}

def print_examples():
    """Print out data structure examples."""
    print("="*60)
    print("MENUBAR DATA STRUCTURE EXAMPLES")
    print("="*60)
    
    print("\n1. BASIC MENU STRUCTURE:")
    print("-" * 30)
    for item in basic_menu:
        print(f"  {item}")
    
    print("\n2. ADVANCED MENU WITH ICONS & SUBMENUS:")
    print("-" * 40)
    for item in advanced_menu:
        print(f"  {item}")
    
    print("\n3. TEMPLATE USAGE EXAMPLES:")
    print("-" * 30)
    for example_name, code in template_examples.items():
        print(f"\n{example_name.upper().replace('_', ' ')}:")
        print(code)
    
    print("\n4. KEY POINTS:")
    print("-" * 15)
    print("• Use ':items' (with colon) to pass data as Jinja expression")
    print("• Use 'items' (without colon) only for literal strings")
    print("• Each menu item should have 'label' and 'link' properties")
    print("• Optional properties: 'selected', 'active', 'align', 'icon', 'submenu', 'useDivider'")
    print("• Use 'selected': true for persistent active/selected state (always blue)")
    print("• Use 'active': true for temporary active state (click state)")
    print("• Submenus are arrays of items with 'label' and 'link'")
    print("• Use 'align': 'right' to position items on the right side")
    
    print("\n5. DEBUGGING TIPS:")
    print("-" * 20)
    print("• Check browser dev tools for HTML structure")
    print("• Verify data is passed correctly: {{ menu_data | tojson }}")
    print("• Make sure component is registered in registry")
    print("• Check for JavaScript errors in console")

if __name__ == '__main__':
    print_examples()