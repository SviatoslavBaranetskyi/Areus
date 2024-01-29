from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView

from .forms import LoginForm


def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            return HttpResponseRedirect('/main')

    else:
        form = LoginForm()
        return render(request, 'app/index.html', {
            'form': form
        })


def main_page_view(request):
    entered_data = request.POST
    return render(request, "app/main.html", {
        "Host": entered_data['host'],
        "Username": entered_data['username'],
        "Password": 'lol'
    })

