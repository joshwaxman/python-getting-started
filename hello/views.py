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


def people(request):
    # return HttpResponse('Hello from Python!')
    return render(request, 'people.html')

def convert(request, text=''):
    # return HttpResponse('Hello from Python!')
    from hello.hebconvert import convert
    return render(request, 'convert.html', dict(original=text, converted=convert(text)))

def bio(request, person):
    from hello.bio import getBiography
    html, nodes, edges = getBiography(person)
    return render(request, 'bio.html', dict(leftside=html, student_nodes=nodes, student_edges=edges))


def blog(request):
    from hello.blog import getBlogPost
    text = getBlogPost()
    return render(request, 'blog.html', {'blogpost': text})

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
    leftside, student_edges, student_nodes, local_interaction_edges, \
    local_interaction_nodes, global_interaction_edges, global_interaction_nodes, \
    sugyaGraphs, timeline = htmlOutputter(masechet, page)

    return render(request, "talmud.html", {'leftside': leftside,
                                           'student_nodes': student_nodes,
                                           'student_edges': student_edges,
                                           'local_interaction_nodes': local_interaction_nodes,
                                           'local_interaction_edges': local_interaction_edges,
                                           'global_interaction_nodes': global_interaction_nodes,
                                           'global_interaction_edges': global_interaction_edges,
                                           'sugya_graph': sugyaGraphs,
                                           'timeline': timeline})


def talmud_dev(request, masechet='missing', page='missing'):
    from hello.talmud import getDafYomi
    if masechet == 'missing' or page == 'missing':
        # try to find in dafyomi

        masechet, page = getDafYomi()

    from hello.talmud_dev import htmlOutputter
    leftside, student_edges, student_nodes, local_interaction_edges,\
                local_interaction_nodes, global_interaction_edges, global_interaction_nodes, \
                sugyaGraphs = htmlOutputter(masechet, page)

    return render(request, "talmud_dev.html", {'leftside': leftside,
                                           'student_nodes': student_nodes,
                                           'student_edges': student_edges,
                                           'local_interaction_nodes': local_interaction_nodes,
                                           'local_interaction_edges': local_interaction_edges,
                                           'global_interaction_nodes': global_interaction_nodes,
                                           'global_interaction_edges': global_interaction_edges,
                                           'sugya_graph': sugyaGraphs})
