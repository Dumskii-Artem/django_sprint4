from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, DetailView

from .models import Category, Post, Comment
from .forms import (CommentCreateForm,
                    PostForm,
                    UserEditForm)


User = get_user_model()


class OnlyAuthorMixin(UserPassesTestMixin):
    # Если пользователь - автор объекта, то тест будет пройден.
    # Если нет, то будет вызвана ошибка 403.
    def test_func(self):
        return self.get_object().author == self.request.user


def get_published_posts(posts: QuerySet = Post.objects.all()):
    return posts.select_related(
        'category', 'location', 'author'
    ).filter(
        pub_date__lt=timezone.now(),
        is_published=True,
        category__is_published=True
    ).annotate(
        comment_count=Count('comment')
    )


class PostListView(ListView):
    model = Post
    paginate_by = 10
    template_name = "blog/index.html"
    queryset = get_published_posts().order_by('-pub_date')


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    return render(
        request,
        'blog/create.html',
        {'post': post, 'form': PostForm(instance=post)}
    )


# class PostEditView(OnlyAuthorMixin, UpdateView):
#     model = Post
#     form_class = PostForm
#     pk_url_kwarg = 'post_id'
#     template_name = 'blog/create.html'
#     success_url = reverse_lazy('blog.list')

#     def dispatch(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             p_id = self.kwargs.get('post_id')
#             return redirect('blog:post_detail', post_id=p_id)
#         return super().dispatch(request, *args, **kwargs)

@login_required()
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = PostForm(instance=post)
    return render(
        request, 'blog/create.html', {'form': form, 'post': post}
    )


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        form = CommentCreateForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentCreateForm(instance=comment)
    return render(
        request, 'blog/comment.html', {'form': form, 'comment': comment}
    )


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(
        request, 'blog/comment.html', {'comment': comment}
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        form = CommentCreateForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', post_id=post.id)
    else:
        form = CommentCreateForm()

    return render(request, 'detail.html', {'form': form, 'post': post})


class PostDetailView(DetailView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_id = self.kwargs['post_id']
        post = get_object_or_404(
            Post,
            id=post_id
        )
        if post.author == self.request.user:
            context['post'] = post
        else:
            if (
                post.is_published
                and post.category.is_published
                and post.pub_date < timezone.now()
            ):
                context['post'] = post
            else:
                raise Http404("Пост не найден или недоступен")

        context['comments'] = Comment.objects.filter(post=post_id)
        context['form'] = CommentCreateForm()
        return context


class CategoryPostListView(ListView):
    model = Post
    paginate_by = 10
    template_name = "blog/category.html"

    def get_queryset(self):
        category = get_object_or_404(
            Category,
            slug=self.kwargs.get('category_slug'),
            is_published=True)
        return get_published_posts(category.post).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs.get('category_slug'),
            is_published=True)
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )

    def form_valid(self, form):
        # Присвоить полю author объект пользователя из запроса.
        form.instance.author = self.request.user
        return super().form_valid(form)


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        username = self.request.user.username
        return reverse_lazy('blog:profile', kwargs={'username': username})


class UserDetailView(DetailView):
    model = User
    slug_url_kwarg = 'username'
    slug_field = 'username'
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        context['profile'] = profile
        context['user'] = self.request.user

        posts = (
            Post.objects
            .filter(author=profile.id)
            .annotate(comment_count=Count('comment'))
            .order_by('-pub_date')
        )

        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')

        context['page_obj'] = paginator.get_page(page_number)

        return context


@login_required
def edit_profile(request):
    print('<<-')
    print(request)
    print('->>')
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', request.user)
    else:
        form = UserEditForm(instance=request.user)

    return render(request, 'blog/user.html', {'form': form})
