from django.shortcuts import render
from django.http import HttpResponse


from .models import Greeting

# Create your views here.
def index(request):
    # return HttpResponse('Hello from Python!')
    return render(request, 'index.html')

def about(request):
    # return HttpResponse('Hello from Python!')
    return render(request, 'about.html')


def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})


def talmud(request, masechet='missing', page='missing'):
    from hello.talmud import htmlOutputter, getDafYomi
    if masechet == 'missing' or page == 'missing':
        # try to find in dafyomi

        masechet, page = getDafYomi()
    from hello.talmud import htmlOutputter
    leftside, e, n, edges, nodes = htmlOutputter(masechet, page)
    return render(request, "talmud.html", {'leftside': leftside,
                                           'student_nodes': n,
                                           'student_edges': e,
                                           'local_interaction_nodes': nodes,
                                           'local_interaction_edges': edges})
