from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.views.generic.edit import CreateView
from django.urls import include, path, reverse_lazy, path, include

# from blog.views import UserLoginView

handler404 = 'pages.views.error404'
handler500 = 'pages.views.error500'

urlpatterns = [
    path('', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('admin/', admin.site.urls),

    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url=reverse_lazy('blog:index'),
        ),
        name='registration',
    ),

    path(
        'auth/login/',
        LoginView.as_view(
            template_name='registration/login.html'
        ),
        name='login'),

    path('auth/', include('django.contrib.auth.urls')),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
