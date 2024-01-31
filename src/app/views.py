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
            try:
                db = connect(
                    host=form.cleaned_data['host'],
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password']
                )
            except:
                return HttpResponse('ERRORRRRRRRRRRRRRRRR!')

            request.session['host'] = form.cleaned_data['host']
            request.session['username'] = form.cleaned_data['username']
            request.session['password'] = form.cleaned_data['password']

            return HttpResponseRedirect('/')

    else:
        form = LoginForm()

    return render(request, 'app/index.html', {'form': form})


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

