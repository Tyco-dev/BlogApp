from django.urls import path
from . import views
from .views import UpdatePostView, DeletePostView, DraftListView
from .feeds import LatestPostFeed

app_name = 'blog'


urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('drafts/', DraftListView.as_view(), name="draft_list"),
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    # path('', views.PostListView.as_view(), name='post_list'),
    path('<int:pk>/<slug:post>/',
         views.post_detail,
         name='post_detail'),
    path('<int:post_id>/share/',
         views.post_share, name='post_share'),
    path('add_post/', views.add_post, name='add_post'),
    path('update_post/<int:pk>', UpdatePostView.as_view(), name='update_post'),
    path('delete_post/<int:pk>', DeletePostView.as_view(), name='delete_post'),
    path('feed/', LatestPostFeed(), name='post_feed'),
    path('search/', views.post_search, name='post_search'),
]