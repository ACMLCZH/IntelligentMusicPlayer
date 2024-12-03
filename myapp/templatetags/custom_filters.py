from django import template

register = template.Library()

@register.filter
def youtube_embed_url(url):
    return url.replace('watch?v=', 'embed/')