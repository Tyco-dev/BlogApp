from django import template
from ..models import Post
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown

register = template.Library()


@register.simple_tag
def total_posts():
    return Post.published.count()


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=3):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


@register.simple_tag
def get_most_commented_posts(count=3):
    # aggregate the total number of comments for each post
    return Post.published.annotate(
        # Store the number of comments in the computed field "total_comments" for each Post object.
        total_comments=Count('comments')
    ).order_by('-total_comments')[:count]


@register.filter(name='markdown')
def markdown_format(text):
    # Use "mark_safe" to mark the result as safe HTML to be rendered in the template.
    # Django will not trust any HTML code and will escape it before placing it in the output
    return mark_safe(markdown.markdown(text))
