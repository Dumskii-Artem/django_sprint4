from django.urls import path

from . import views

app_name = 'pages'

urlpatterns = [
    path('about/', views.AboutPage.as_view(), name='about'),
    path('rules/', views.RulesPage.as_view(), name='rules'),
    path('403/', views.Error403Page.as_view(), name='error403'),
]
