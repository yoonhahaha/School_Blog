from django import template
import re
from django.utils.html import escape
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def render_mentions(text):
    """Render @username mentions as links to user profiles"""
    # First escape the text to prevent XSS
    text = escape(text)
    
    # Replace @username with links
    pattern = r'@(\w+)'
    
    def replace_mention(match):
        username = match.group(1)
        url = f"/posts/by/{username}/"
        return f'<a href="{url}">@{username}</a>'
    
    result = re.sub(pattern, replace_mention, text)
    
    # Convert newlines to <br> tags
    result = result.replace('\n', '<br>')
    
    return mark_safe(result)