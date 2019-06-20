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


def clark(request, shoresh):
    from hello.clark import getClarkShoresh
    html, nodes, edges = getClarkShoresh(shoresh)
    return render(request, 'clark.html', dict(leftside=html, root_nodes=nodes, root_edges=edges))


def trup(request, verse):
    from hello.trup import getTree
    tree, text, tagged, next, prev, iso_html, prob = getTree(verse)
    return render(request, 'trup.html', dict(tree=tree, text=text, tagged=tagged, verse=verse,
                                             next=next, prev=prev, iso_html=iso_html, prob=prob))



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


def trup_form(request):
    from .trup_form import TrupForm
    from hello.trup import generateTree

    if request.method == 'POST':
        form = TrupForm(request.POST)
        if form.is_valid(): #pass  # trigger the validation
            pasuk = form.cleaned_data['pasuk']
            tree, text, tagged, iso_html, prob = generateTree(pasuk)
            return render(request, 'trup_unknown.html', dict(tree=tree, text=text, tagged=tagged,
                                             iso_html=iso_html, prob=prob))
    else:
        form = TrupForm()
    return render(request, 'trup_form.html', {'form': form})
