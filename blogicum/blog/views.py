from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
# from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.urls import reverse
# from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, DetailView

from .forms import (
    CommentCreateForm,
    PostForm,
    UserEditForm,
)
from .models import Category, Post, Comment

POSTS_ON_PAGE = 10


def get_paginator_page(request, query_set, posts_on_page=POSTS_ON_PAGE):
    return Paginator(query_set, posts_on_page
                     ).get_page(request.GET.get('page'))


class OnlyAuthorMixin(UserPassesTestMixin):
    # Если пользователь - автор объекта, то тест будет пройден.
    # Если нет, то будет вызвана ошибка 403.
    def test_func(self):
        return self.get_object().author == self.request.user


def get_published_posts(
    posts: QuerySet = Post.objects.all(),
    use_filtering: bool = True,
    use_select_related: bool = True,
    use_annotation: bool = True,
):
    if use_filtering:
        posts = posts.filter(
            pub_date__lt=timezone.now(),
            is_published=True,
            category__is_published=True
        )
    if use_select_related:
        posts = posts.select_related('category', 'location', 'author')
    if use_annotation:
        posts = posts.annotate(
            comment_count=Count('comments')
        ).order_by(
            *Post._meta.ordering
        )
    return posts


class PostListView(ListView):
    model = Post
    paginate_by = POSTS_ON_PAGE
    template_name = 'blog/index.html'
    queryset = get_published_posts()


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', request.user.username)
    return render(request, 'blog/create.html', {
        'post': post,
        'form': PostForm(instance=post),
    })


@login_required()
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id)

    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)

    return render(request, 'blog/create.html', {
        'form': form,
        'post': post,
    })


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    form = CommentCreateForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', {
        'form': form,
        'comment': comment,
    })


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user:
        return redirect('blog:post_detail', post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id)
    return render(request, 'blog/comment.html', {
        'comment': comment,
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    form = CommentCreateForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect('blog:post_detail', post_id=post.id)


class PostDetailView(DetailView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'

    def get_object(self):
        post = super().get_object()
        if post.author == self.request.user:
            return post
        return super().get_object(
            get_published_posts(
                use_select_related=False,
                use_annotation=False
            ))

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            comments=self.get_object().comments.all(),
            form=CommentCreateForm())


class CategoryPostListView(ListView):
    model = Post
    paginate_by = POSTS_ON_PAGE
    template_name = "blog/category.html"

    def get_category(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs.get('category_slug'),
            is_published=True
        )

    def get_queryset(self):
        return get_published_posts(self.get_category().posts)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            category=self.get_category()
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def get_success_url(self):
        return reverse(
            'blog:profile',
            args=[self.request.user.username]
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class UserDetailView(DetailView):
    model = User
    slug_url_kwarg = 'username'
    slug_field = 'username'
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            profile=self.get_object(),
            page_obj=get_paginator_page(
                self.request,
                get_published_posts(
                    posts=self.get_object().posts.all(),
                    use_filtering=(self.request.user != self.get_object())
                )
            )
        )


@login_required
def edit_profile(request):
    form = UserEditForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', request.user.username)
    return render(request, 'blog/user.html', {
        'form': form,
    })
