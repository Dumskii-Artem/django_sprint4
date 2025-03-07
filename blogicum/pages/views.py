from django.shortcuts import render
from django.views.generic import TemplateView


class AboutPage(TemplateView):
    template_name = 'pages/about.html'


class RulesPage(TemplateView):
    template_name = 'pages/rules.html'


def error404(request, exception=None):
    return render(request, 'pages/404.html', status=404)


class Error403Page(TemplateView):
    template_name = 'pages/403csrf.html'


def error403csrf(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def error500(request, exception=None):
    return render(request, 'pages/500.html', status=500)
