from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from mysql.connector import connect

from .forms import LoginForm


def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            host=form.cleaned_data['host']
            username=form.cleaned_data['username']
            password=form.cleaned_data['password']
            try:
                db = connect(host=host, username=username, password=password)
            except:
                return HttpResponseRedirect(request.path_info)

            request.session['host'] = host
            request.session['username'] = username
            request.session['password'] = password

            return HttpResponseRedirect('/')

    form = LoginForm()
    return render(request, 'app/login.html', {'form': form})


class MainPageView(View):
    @staticmethod
    def get(request):
        if 'host' in request.session and 'username' in request.session and 'password' in request.session:
            host = request.session.get('host')
            username = request.session.get('username')
            password = request.session.get('password')

            return render(request, 'app/main.html', {
                'Host': host,
                'Username': username,
                'Password': password
            })

        else:
            return HttpResponseRedirect('/login')

