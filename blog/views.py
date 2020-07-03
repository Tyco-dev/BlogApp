from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.utils.text import slugify
from django.views.generic import ListView, UpdateView, DeleteView
from django.contrib.auth.models import User
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm, AddPostForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from taggit.managers import TaggableManager
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy


# Create your views here.


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 5)  # 5 posts in each page
    page = request.GET.get('page')  # Indicates the current page number
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/list.html',
                  {'page': page,
                   'posts': posts,
                   'tag': tag})


@login_required(login_url='users:login')
def post_detail(request, year, month, day, post, ):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    # List of active comments for this post
    comments = post.comments.filter(active=True)

    new_comment = None

    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Assign the current user to the comment
            new_comment.name = request.user
            # Save the comment to the database
            new_comment.save()
            messages.success(request, 'Comment submission successful')
    else:
        comment_form = CommentForm()

    # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids) \
        .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')) \
                        .order_by('-same_tags', '-publish')[:4]

    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'new_comment': new_comment,
                   'comment_form': comment_form,
                   'similar_posts': similar_posts})


class PostListView(ListView):
    # Use a specific queryset instead of retrieving all objects.
    queryset = Post.published.all()
    # Use context variable 'posts' for the query results. Default is 'object_list'
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_share(request, post_id):
    # Retrieve post by id.
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.user, request.POST)
        if form.is_valid():
            # Form fields passed validation
            user = request.user
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['user']} recommends you read " f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" f"{cd['user']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'admin@myblog.com',
                      [cd['to']])
            sent = True
            # ... send email
    else:
        form = EmailPostForm()

    return render(request, 'blog/post/share.html',
                  {'post': post,
                   'form': form,
                   'sent': sent})


@staff_member_required
def add_post(request):
    if request.method == 'POST':
        form = AddPostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.slug = slugify(post.title)
            post.author = request.user
            post.publish = timezone.now()
            post.slug = slugify(post.title)
            post.save()
            form.save_m2m()
            messages.success(request, 'Post submission successful')
            return redirect('blog:post_list')
    else:
        form = AddPostForm()
    return render(request, 'blog/post/add_post.html', {'form': form})


class UpdatePostView(SuccessMessageMixin, UpdateView):
    model = Post
    template_name = 'blog/post/update_post.html'
    fields = ['title', 'body', 'tags']
    success_message = 'Post has been updated!'


class DeletePostView(SuccessMessageMixin, DeleteView):
    model = Post
    template_name = 'blog/post/delete_post.html'
    success_url = reverse_lazy('blog:post_list')
    success_message = 'Post has been delete!'

