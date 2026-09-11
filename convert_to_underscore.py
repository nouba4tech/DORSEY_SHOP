#!/usr/bin/env python3
"""
Convert {{ t('...') }} to {{ _('...') }} in templates for pybabel compatibility.
This allows pybabel to properly extract translatable strings from templates.
"""

import os
import re
from pathlib import Path

def convert_templates():
    """Replace {{ t( with {{ _( and {% t %} with {% trans %}"""
    templates_dir = Path('app/templates')
    
    if not templates_dir.exists():
        print(f"Templates directory not found: {templates_dir}")
        return
    
    html_files = list(templates_dir.rglob('*.html'))
    converted_count = 0
    total_replacements = 0
    
    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace {{ t( with {{ _( 
        content = re.sub(r'{{\s*t\s*\(', '{{ _(', content)
        
        # Replace {% t %} ... {% end t %} with {% trans %} ... {% endtrans %}
        content = re.sub(r'{%\s*t\s*%}', '{% trans %}', content)
        content = re.sub(r'{%\s*end\s*t\s*%}', '{% endtrans %}', content)
        
        if content != original_content:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            replacements = len(re.findall(r'_\(', content))
            converted_count += 1
            total_replacements += replacements
            print(f"✓ Converted: {html_file.relative_to('.')}")
    
    print(f"\nTotal files converted: {converted_count}")
    print(f"Total translation markers updated: {total_replacements}")

if __name__ == '__main__':
    convert_templates()
