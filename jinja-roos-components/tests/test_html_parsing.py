"""
Test different HTML parsing approaches for component tags
"""

# Test with html.parser
from html.parser import HTMLParser

class ComponentParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.components = []
        self.stack = []
        
    def handle_starttag(self, tag, attrs):
        if tag.startswith('c-'):
            self.components.append({
                'tag': tag,
                'attrs': dict(attrs),
                'start': self.getpos(),
                'self_closing': False
            })
            self.stack.append(tag)
            
    def handle_endtag(self, tag):
        if tag.startswith('c-') and self.stack and self.stack[-1] == tag:
            self.stack.pop()
            # Mark the component as complete
            for comp in reversed(self.components):
                if comp['tag'] == tag and not comp.get('complete'):
                    comp['complete'] = True
                    comp['end'] = self.getpos()
                    break
                    
    def handle_startendtag(self, tag, attrs):
        if tag.startswith('c-'):
            self.components.append({
                'tag': tag,
                'attrs': dict(attrs),
                'start': self.getpos(),
                'self_closing': True,
                'complete': True
            })

# Test HTML
test_html = '''<c-page title="Test">
    <c-layout-flow gap="xl">
        <c-card outline="true">
            <c-layout-flow gap="md">
                <c-input name="test" />
                <p>Content</p>
            </c-layout-flow>
        </c-card>
    </c-layout-flow>
</c-page>'''

print("=== Testing html.parser ===")
parser = ComponentParser()
parser.feed(test_html)

print(f"Found {len(parser.components)} components:")
for comp in parser.components:
    print(f"  - {comp['tag']} at line {comp['start'][0]}, self-closing: {comp['self_closing']}")

# Test with xml.etree.ElementTree (more robust for XML-like syntax)
print("\n=== Testing xml.etree.ElementTree ===")
import xml.etree.ElementTree as ET

# Wrap in root to make valid XML
wrapped = f'<root>{test_html}</root>'
try:
    root = ET.fromstring(wrapped)
    
    def find_components(elem, path=""):
        components = []
        if elem.tag.startswith('c-'):
            components.append({
                'tag': elem.tag,
                'attrs': elem.attrib,
                'text': elem.text,
                'tail': elem.tail,
                'path': path
            })
        
        for child in elem:
            components.extend(find_components(child, f"{path}/{elem.tag}"))
        
        return components
    
    components = find_components(root)
    print(f"Found {len(components)} components:")
    for comp in components:
        print(f"  - {comp['tag']} with attrs: {comp['attrs']}")
        
except Exception as e:
    print(f"XML parsing failed: {e}")

# Test with BeautifulSoup (if available)
print("\n=== Testing BeautifulSoup approach (conceptual) ===")
print("BeautifulSoup would use:")
print("- soup.find_all(lambda tag: tag.name and tag.name.startswith('c-'))")
print("- Recursive processing of tag.contents")
print("- Handle both self-closing and paired tags automatically")

# Demonstrate a simple recursive approach
print("\n=== Manual recursive parsing approach ===")

def find_component_tags(html):
    """Find all component tags and their positions"""
    import re
    
    # Find all opening tags (including self-closing)
    open_pattern = re.compile(r'<(c-[\w-]+)([^>]*?)(/?)\>')
    components = []
    
    for match in open_pattern.finditer(html):
        tag_name = match.group(1)
        attrs_str = match.group(2)
        self_closing = match.group(3) == '/'
        
        component = {
            'tag': tag_name,
            'attrs_str': attrs_str,
            'start': match.start(),
            'tag_end': match.end(),
            'self_closing': self_closing,
            'full_match': match.group(0)
        }
        
        if not self_closing:
            # Find matching end tag
            end_pattern = re.compile(rf'</{re.escape(tag_name)}>')
            end_match = end_pattern.search(html, match.end())
            if end_match:
                component['end'] = end_match.end()
                component['content'] = html[match.end():end_match.start()]
            else:
                print(f"Warning: No closing tag found for {tag_name}")
                
        components.append(component)
    
    return components

components = find_component_tags(test_html)
print(f"Found {len(components)} components:")
for comp in components:
    print(f"  - {comp['tag']} {'(self-closing)' if comp['self_closing'] else ''}")
    if 'content' in comp:
        print(f"    Content preview: {comp['content'][:50].strip()}...")