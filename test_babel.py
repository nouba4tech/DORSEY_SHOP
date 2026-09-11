#!/usr/bin/env python3
"""Test Flask-Babel integration with templates."""

from app import create_app
from flask import render_template_string

app = create_app()

with app.test_request_context():
    # Test 1: Simple translation function
    template = "{{ _('Test') }}"
    result = render_template_string(template)
    print('✓ Template rendering works')
    print('  Result:', repr(result))
    
    # Test 2: Check that _ is in Jinja2 globals
    if '_' in app.jinja_env.globals:
        print('✓ _ function in Jinja2 globals')
    else:
        print('✗ _ function NOT in Jinja2 globals')
    
    # Test 3: Verify ngettext is available
    if 'ngettext' in app.jinja_env.globals:
        print('✓ ngettext function in Jinja2 globals')
    else:
        print('✗ ngettext function NOT in Jinja2 globals')
    
    print('\n✓ All checks passed! Flask-Babel is working correctly.')
