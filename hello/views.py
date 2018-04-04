from django.shortcuts import render
from django.http import HttpResponse


from .models import Greeting

# Create your views here.
def index(request):
    # return HttpResponse('Hello from Python!')
    return render(request, 'index.html')


def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})


def talmud(request, masechet='Horayot', page='3b'):
    from hello.talmud import htmlOutputter
    leftside, edges, nodes = htmlOutputter(masechet, page)
    return render(request, "talmud.html", {'leftside': leftside, 'nodes': nodes, 'edges': edges})
