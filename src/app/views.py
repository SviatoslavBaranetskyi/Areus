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
            request.session['host'] = form.cleaned_data['host']
            request.session['username'] = form.cleaned_data['username']
            request.session['password'] = form.cleaned_data['password']

            return HttpResponseRedirect('/main')

    else:
        form = LoginForm()

    return render(request, 'app/index.html', {'form': form})


class MainPageView(View):
    def get(self, request):
        host = request.session.get('host')
        username = request.session.get('username')
        password = request.session.get('password')

        return render(request, 'app/main.html', {
            'Host': host,
            'Username': username,
            'Password': password
        })


