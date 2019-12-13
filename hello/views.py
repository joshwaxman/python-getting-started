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

def clark(request, shoresh=''):
    from hello.clark import getClarkShoresh
    from hello.clark import getClarkFullList
    if shoresh == '':
        html, nodes, edges = getClarkFullList()
    else:
        html, nodes, edges = getClarkShoresh(shoresh)

    return render(request, 'clark.html', dict(leftside=html, root_nodes=nodes, root_edges=edges))

def klein(request, shoresh=''):
    from hello.klein import getKleinFullList, getKleinShoresh
    if shoresh == '':
        html, nodes, edges = getKleinFullList()
    else:
        html, nodes, edges = getKleinShoresh(shoresh)

    return render(request, 'klein.html', dict(leftside=html, root_nodes=nodes, root_edges=edges))

def bdb(request, shoresh=''):
    from hello.bdb import getBDBFullList, getBDBShoresh
    if shoresh == '':
        html, nodes, edges = getBDBFullList()
    else:
        html, nodes, edges = getBDBShoresh(shoresh)

    return render(request, 'bdb.html', dict(leftside=html, root_nodes=nodes, root_edges=edges))



def distributional(request, shoresh=''):
    from hello.distributional import getDistFullList, getShoreshDist
    if shoresh == '':
        html, nodes, edges = getDistFullList()
    else:
        html, nodes, edges = getShoreshDist(shoresh)

    return render(request, 'distributional.html', dict(leftside=html, root_nodes=nodes, root_edges=edges))


def trup(request, verse):
    from hello.trup import getTree
    if verse == '':
        verse = 'Nehemiah 8:8'
    tree, text, engText, tagged, next, prev, iso_html, probProduct, probAverage = getTree(verse)
    return render(request, 'trup.html', dict(tree=tree, text=text, engText=engText, tagged=tagged, verse=verse,
                                             next=next, prev=prev, iso_html=iso_html, prob=probProduct, probAverage=probAverage))

def dictionary(request):
    return render(request, 'dictionary.html')


def blog(request):
    from hello.blog import getBlogPost
    text = getBlogPost()
    return render(request, 'blog.html', {'blogpost': text})

def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})

def show_tractates(request):
    from hello.talmud import getTalmudNavigation
    x = getTalmudNavigation()
    return render(request, "tractates.html", {'tractate_list': x})

def show_tractate_chapters(request, masechet):
    from hello.talmud import getTalmudPageNavigation
    x = getTalmudPageNavigation(masechet)
    return render(request, "tractates.html", {'tractate_list': x})

def get_daf_yomi(request):
    from hello.talmud import htmlOutputter, getDafYomi
    masechet, page = getDafYomi()
    talmud(request, masechet, page)

def talmud(request, masechet='missing', page='missing'):
    from hello.talmud import htmlOutputter, getDafYomi
    from hello.talmud import getTalmudPageNavigation
    if masechet == 'missing' or page == 'missing':
        # try to find in dafyomi
        masechet, page = getDafYomi()
    elif page == 'missing':
        x = getTalmudPageNavigation(masechet)
        return render(request, "tractates.html", {'tractate_list': x})

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
            tree, text, tagged, iso_html, probProduct, probAverage = generateTree(pasuk)
            return render(request, 'trup_unknown.html', dict(tree=tree, text=text, tagged=tagged,
                                             iso_html=iso_html, prob=probProduct, probAverage=probAverage))
    else:
        form = TrupForm()
    return render(request, 'trup_form.html', {'form': form})


def neo_form(request):
    from .set_neo import NeoForm
    from pymongo import MongoClient
    if request.method == 'POST':
        form = NeoForm(request.POST)
        if form.is_valid(): #pass  # trigger the validation
            connection_string = form.cleaned_data['connection_string']
            # write this value to both the database for mivami
            client = MongoClient(
                "mongodb://mivami:Talmud1%@talmud-shard-00-00-ol0w9.mongodb.net:27017,talmud-shard-00-01-ol0w9.mongodb.net:27017,talmud-shard-00-02-ol0w9.mongodb.net:27017/admin?replicaSet=Talmud-shard-0&ssl=true")
            db = client.sefaria
            db.connection_strings.replace_one({'bolt_connection': connection_string}, True)

            return render(request, 'neo_set.html')
    else:
        form = TrupForm()
    return render(request, 'set_neo.html', {'form': form})


def full_graph(request):
    from pymongo import MongoClient
    client = MongoClient(
        "mongodb://mivami:Talmud1%@talmud-shard-00-00-ol0w9.mongodb.net:27017,talmud-shard-00-01-ol0w9.mongodb.net:27017,talmud-shard-00-02-ol0w9.mongodb.net:27017/admin?replicaSet=Talmud-shard-0&ssl=true")
    db = client.sefaria
    x = db.fullgraph.find_one()
    return render(request, 'full_graph.html', {'graph': x['full_graph']})

