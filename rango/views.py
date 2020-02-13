from django.http import HttpResponse


def index(request):
    idx = "<h2>Rango says hey there partner!</h2><br><a href='/rango/about'>About</a>"
    return HttpResponse(idx)


def about(request):
    abt = "<h2>Rango says here is the about page</h2><br><a href='/rango/'>Home</a>"
    return HttpResponse(abt)
