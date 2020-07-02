from django.contrib.sitemaps import Sitemap
from  .models import Post


class PostSiteMap(Sitemap):
    # Change frequency of post pages and their relevance in website.
    changefreq = 'weekly'
    priority = 0.9

    # Returns the QuerySet of objects to include in this sitemap
    def items(self):
        return Post.published.all()

    # Receives each object returned by items() and returns the last time the object was modified.
    def lastmod(self, obj):
        return obj.updated
