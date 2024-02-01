from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from mysql.connector import connect

from .forms import LoginForm
from .decorators import require_session


def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            host = form.cleaned_data['host']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
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


@require_session
def get_databases(request):
    db = connect(
        host=request.session['host'],
        username=request.session['username'],
        password=request.session['password']
    )
    cursor = db.cursor()

    # Execute query to get list of databases
    cursor.execute("SHOW DATABASES")

    # Fetch all databases
    databases = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    db.close()

    # Convert the list of databases to a dictionary
    data = {"databases": [db[0] for db in databases], "host": request.session['host']}

    return JsonResponse(data)


@method_decorator(require_session, name="dispatch")
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

