from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!
    context_dict = {'boldmessage': "Crunchy, creamy, cookie, candy, cupcake!"}

    return render(request, 'rango/index.html', context_dict)


def about(request):
    abt = "<h2>Rango says here is the about page</h2><br><a href='/rango/'>Home</a>"
    return HttpResponse(abt)

