from django.shortcuts import render
from django.http import HttpResponse
#from neo4j.v1 import GraphDatabase, basic_auth
from py2neo import Graph
from json import loads

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

def brat(request):
    return render(request, 'sample_brat.html')

def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})


def tzurat(request, masechet, daf):
    text = 'אור לארבעה עשר בודקין את החמץ לאור הנר כל מקום שאין מכניסין בו חמץ אין צריך בדיקה ובמה אמרו שתי שורות במרתף מקום שמכניסין בו חמץ בית שמאי אומרים שתי שורות על פני כל המרתף ובית הלל אומרים שתי שורות החיצונות שהן העליונות: בגמ׳ מאי אור רב הונא אמר נגהי ורב יהודה אמר לילי קא סלקא דעתך דמאן דאמר נגהי נגהי ממש ומאן דאמר לילי לילי ממש גמיתיבי הבקר אור והאנשים שלחו אלמא אור יממא הוא מי כתיב האור בקר הבקר אור כתיב כמאן דאמר צפרא נהר וכדרב יהודה אמר רב דאמר רב יהודה אמר רב לעולם יכנס אדם בכי טוב ויצא בכי טוב דמיתיבי וכאור בקר יזרח שמש אלמא אור יממא הוא מי כתיב אור בקר וכאור בקר כתיב והכי קאמר וכאור בקר בעולם הזה כעין זריחת שמש לצדיקים לעולם הבא המיתיבי ויקרא אלהים לאור יום אלמא אור יממא הוא הכי קאמר למאיר ובא קראו יום אלא מעתה ולחשך קרא לילה למחשיך ובא קרא לילה והא קיימא לן דעד צאת הכוכבים יממא הוא ואלא הכי קאמר קרייה רחמנא לנהורא ופקדיה אמצותא דיממא וקרייה רחמנא לחשוכא ופקדיה אמצותא דלילה זמיתיבי הללוהו כל כוכבי אור אלמא אור אורתא הוא הכי קאמר הללוהו כל כוכבים המאירים אלא מעתה כוכבים המאירים הוא דבעו שבוחי שאינן מאירין לא בעו שבוחי והא כתיב הללוהו כל צבאיו חאלא הא קא משמע לן דאור דכוכבים נמי אור הוא למאי נפקא מינה לנודר מן האור (דתנן) הנודר מן האור אסור באורן של כוכבים טמיתיבי לאור יקום רוצח יקטל עני ואביון ובלילה יהי כגנב'
    # text = '''אור לארבעה עשר בודקין את החמץ לאור הנר כל מקום שאין מכניסין בו חמץ אין צריך בדיקה ובמה אמרו ב' שורות במרתף מקום שמכניסין בו חמץ בית שמאי אומרים ב' שורות על פני כל המרתף ובית הלל אומרים שתי שורות החיצונות שהן העליונות: בגמ׳ מאי אור רב הונא אמר נגהי ורב יהודה אמר לילי קא סלקא דעתך דמאן דאמר נגהי נגהי ממש ומאן דאמר לילי לילי ממש גמיתיבי (בראשית מד, ג) הבקר אור והאנשים שולחו אלמא אור יממא הוא מי כתיב האור בקר הבקר אור כתיב כמאן דאמר צפרא נהר וכדרב יהודה אמר רב דאמר רב יהודה אמר רב לעולם יכנס אדם בכי טוב ויצא בכי טוב דמיתיבי (שמואל ב כג, ד) וכאור בקר יזרח שמש אלמא אור יממא הוא מי כתיב אור בקר וכאור בקר כתיב והכי קאמר וכאור בקר בעולם הזה כעין זריחת שמש לצדיקים לעולם הבא המיתיבי (בראשית א, ה) ויקרא אלהים לאור יום אלמא אור יממא הוא הכי קאמר למאיר ובא קראו יום אלא מעתה ולחשך קרא לילה למחשיך ובא קרא לילה והא קיימא לן דעד צאת הכוכבים יממא הוא ואלא הכי קאמר קרייה רחמנא לנהורא ופקדיה אמצותא דיממא וקרייה רחמנא לחשוכא ופקדיה אמצותא דלילה זמיתיבי (תהלים קמח, ג) הללוהו כל כוכבי אור אלמא אור אורתא הוא הכי קאמר הללוהו כל כוכבים המאירים אלא מעתה כוכבים המאירים הוא דבעו שבוחי שאינן מאירין לא בעו שבוחי והא כתיב (תהלים קמח, ב) הללוהו כל צבאיו חאלא הא קמ"ל דאור דכוכבים נמי אור הוא למאי נפקא מינה לנודר מן האור (דתנן) הנודר מן האור אסור באורן של כוכבים טמיתיבי (איוב כד, יד) לאור יקום רוצח יקטל עני ואביון ובלילה יהי כגנב'''
    #text = ''''''
    structure = [('center-box', 1), ('center-text', 34)]

    g = Graph("bolt://172.104.217.202:7687", auth=("neo4j", "qwerty"))
    query = '''MATCH (t:Tzura2 {daf: $daf}) RETURN t'''
    result = g.run(query, dict(daf=masechet + '.' + daf.upper()))

    daf_info = None
    for record in result:
        daf_info = loads(record['t']['json'])
        break

    masechet_en = daf_info['masechet_en']
    masechet_he = daf_info['masechet_he']
    perek_title = daf_info['perek_title']

    daf = daf_info['daf']

    return render(request, 'tzurat.html', {'daf_info': daf_info, 'masechet': masechet_he, 'daf': daf, 'perek_title': perek_title } )

def show_tractates(request):
    from hello.talmud import getTalmudNavigation
    x = getTalmudNavigation()
    return render(request, "tractates.html", {'tractate_list': x})

def show_tractate_chapters(request, masechet):
    from hello.talmud import getTalmudPageNavigation
    x = getTalmudPageNavigation(masechet)
    return render(request, "tractates.html", {'tractate_list': x})

def get_daf_yomi(request):
    from hello.talmud import getDafYomi
    masechet, page = getDafYomi()
    return talmud(request, masechet, page)

def get_daf_yomi2(request):
    from hello.talmud import getDafYomi
    masechet, page = getDafYomi()
    return talmud2(request, masechet, page)

def talmud2(request, masechet='missing', page='missing'):
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

    return render(request, "talmud2.html", {'leftside': leftside,
                                           'student_nodes': student_nodes,
                                           'student_edges': student_edges,
                                           'local_interaction_nodes': local_interaction_nodes,
                                           'local_interaction_edges': local_interaction_edges,
                                           'global_interaction_nodes': global_interaction_nodes,
                                           'global_interaction_edges': global_interaction_edges,
                                           'sugya_graph': sugyaGraphs,
                                           'timeline': timeline})



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


def graphexplorer(request):
    return render(request, './GraphExplorer/example1.html')
