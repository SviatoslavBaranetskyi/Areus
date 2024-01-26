from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View


def index(request):
    if request.method == "POST":
        return HttpResponseRedirect('/login')
    return render(request, 'app/index.html')


def login_page_view(request):
    entered_data = request.POST
    return render(request, "app/main-page.html", {
        "Host": entered_data['host'],
        "Username": entered_data['username'],
        "Password": 'Secret'
    })


'''class LoginPageView(View):
    def get(self, request):
        return render(request, 'app/index.html')

    def post(self, request):
        return HttpResponse("Hello World!")'''
