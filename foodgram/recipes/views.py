from django.shortcuts import render


def index(request):
    template = 'frontend/public/index.html'
    return render(request, template)