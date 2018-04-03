from Statement import Statement
from pymongo import MongoClient
import sys
sys.path.append('/Users/Shayna/Documents/GitHub/mivami/Scrapers')
from Scrapers import mongo_statement_extractor as m1
from Presentation import graphOutput

#T6 A8  one T4/T5 and no other slashes

client = MongoClient()
db = client.sefaria
person = db.person
texts = db.texts
pplDict = {}

from typing import Dict, Any
def extractNode(p: Dict[str, Any]) -> Dict[str, Any]:
    d = dict()
    d['name'] = p['key']
    d['generation'] = p['generation']
    return d


def genSplit(s: str):
    if s[0] == 'A':
        clss = 'Amora'
    elif s[0] == 'T':
        clss = 'Tanna'
    elif s[0] == 'Z': #don't know what this is, but it's in there and checked using regexes that are are no slashed to deal with for Zs
        clss = 'Z'
    else:
        raise Exception ('The first letter of generation in the p list from Mongo was not A, T, or Z.', "generation: " + s)

    if '/' not in s and str.isdigit(s[1]): #such as A1
        return clss, s[1:]
    elif '/' not in s: #which means that s[1] is str, such as TA
        if clss == 'Amora' and s[1] == 'T' or clss == 'Tanna' and s[1] == 'A':
            clss = 'Tanna/Amora'
            gen = 0
    #I checked Mongodb using cypher quieries and no generations exist that are A_/T_ or t_/A_.
    elif '/' in s: #such as A2/A3
        gen = 's[1]' + '/' + 's[4]'
    else: raise Exception ("Don't know how to read generation " + s)
    return clss, gen

def htmlOutputter(title, page):
    filename = 'labelled_force_graph_automated.html'
    f = open(filename,'w', encoding='utf8')
    wrapper = '''<!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <title>''' + title + '''</title>
<script src="http://d3js.org/d3.v3.min.js" charset="utf-8"></script>
<style type="text/css">
#divA
{
  float:left;
  border:1px solid blue;
  padding: 10px;
  width:45%;
}
#divB
{
  float:right;
  border:1px solid red;
  width:50%;
}
.he
{
    font-size:130%;
    font-family:"Frank Ruehl Libre","Times New Roman",serif;
    text-align:right;direction:rtl;
}
.en
{
    font-family:"adobe-garamond-pro",Georgia,serif;
    text-align:left;direction:ltr;
}

.Tanna[generation="1"] {
    color: pink;
}
.Tanna[generation="1/2"] {
   background: -webkit-linear-gradient(left, salmon, pink);
   background: -o-linear-gradient(right, pink, salmon);
   background: -moz-linear-gradient(right, pink, salmon);
   background: linear-gradient(to right, pink, salmon);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.Tanna[generation="2"] {
    color: salmon;
}
.Tanna[generation="2/3"] {
   background: -webkit-linear-gradient(left, yellow, salmon);
   background: -o-linear-gradient(right, salmon, yellow);
   background: -moz-linear-gradient(right, salmon, yellow);
   background: linear-gradient(to right, salmon, yellow);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.Tanna[generation="3"] {
    color: yellow;
}
.Tanna[generation="3/4"] {
   background: -webkit-linear-gradient(left, lime, yellow);
   background: -o-linear-gradient(right, yellow, lime);
   background: -moz-linear-gradient(right, yellow, lime);
   background: linear-gradient(to right, yellow, lime);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.Tanna[generation="4"] {
    color: lime;
}
.Tanna[generation="4/5"] {
   background: -webkit-linear-gradient(left, cyan, lime);
   background: -o-linear-gradient(right, lime, cyan);
   background: -moz-linear-gradient(right, lime, cyan);
   background: linear-gradient(to right, lime, cyan);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.Tanna[generation="5"] {
    color: cyan;
}
.Tanna[generation="5/6"] {
   background: -webkit-linear-gradient(left, mediumorchid, cyan);
   background: -o-linear-gradient(right, cyan, mediumorchid);
   background: -moz-linear-gradient(right, cyan, mediumorchid);
   background: linear-gradient(to right, cyan, mediumorchid);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.Tanna[generation="6"] {
    color: mediumorchid;
}




.Amora[generation="1"] {
    color: darkred;
}
.Amora[generation="1/2"] {
   background: -webkit-linear-gradient(left, darkorange, darkred);
   background: -o-linear-gradient(right, darkred, darkorange);
   background: -moz-linear-gradient(right, darkred, darkorange);
   background: linear-gradient(to right, darkred, darkorange);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.Amora[generation="2"] {
    color: darkorange;
}
.Amora[generation="2/3"] {
   background: -webkit-linear-gradient(left, gold, darkorange);
   background: -o-linear-gradient(right, darkorange, gold);
   background: -moz-linear-gradient(right, darkorange, gold);
   background: linear-gradient(to right, darkorange, gold);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.Amora[generation="3"] {
    color: gold;
}
.Amora[generation="3/4"] {
   background: -webkit-linear-gradient(left, green, gold);
   background: -o-linear-gradient(right, gold, green);
   background: -moz-linear-gradient(right, gold, green);
   background: linear-gradient(to right, gold, green);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.Amora[generation="4"] {
    color: green;
}
.Amora[generation="4/5"] {
   background: -webkit-linear-gradient(left, darkcyan, green);
   background: -o-linear-gradient(right, green, darkcyan);
   background: -moz-linear-gradient(right, green, darkcyan);
   background: linear-gradient(to right, green, darkcyan);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.Amora[generation="5"] {
    color: darkcyan;
}
.Amora[generation="5/6"] {
   background: -webkit-linear-gradient(left, darkblue, darkcyan);
   background: -o-linear-gradient(right, darkcyan, darkblue);
   background: -moz-linear-gradient(right, darkcyan, darkblue);
   background: linear-gradient(to right, darkcyan, darkblue);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.Amora[generation="6"] {
    color: darkblue;
}
.Amora[generation="6/7"] {
   background: -webkit-linear-gradient(left, purple, darkblue);
   background: -o-linear-gradient(right, darkblue, purple);
   background: -moz-linear-gradient(right, darkblue, purple);
   background: linear-gradient(to right, darkblue, purple);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.Amora[generation="7"] {
    color: purple;
}
.Amora[generation="7/8"] {
   background: -webkit-linear-gradient(left, saddlebrown, purple);
   background: -o-linear-gradient(right, purple, saddlebrown);
   background: -moz-linear-gradient(right, purple, saddlebrown);
   background: linear-gradient(to right, purple, saddlebrown);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.Amora[generation="8"] {
    color: saddlebrown;
}
</style>
</head>
</body>
<div id="container">
    <span id="divA">
'''
    perek = 1
    engVersionTitle = 'William Davidson Edition - English'
    hebVersionTitle = 'William Davidson Edition - Aramaic'
    hebEdition = {'title': title, 'versionTitle': hebVersionTitle}
    engEdition = {'title': title, 'versionTitle': engVersionTitle}

    positions = m1.mongoPerekInfoGetter(title)

    hebEdition = list(texts.find(hebEdition))[0]['chapter'][2:]
    engEdition = list(texts.find(engEdition))[0]['chapter'][2:]

    amud = page[-1]
    daf_start = (int(page[:-1]) - 2) * 2
    if amud == 'b':
        daf_start += 1

    daf = daf_start

    names = set()
    wrapper += '<a href=""https://www.sefaria.org/%s?lang=bi">%s</a></p>' % (title + '.' +str(page), title+" "+str(page)) #Pesachim.7b, Pesachim 7b

    h = hebEdition[daf]
    e = engEdition[daf]

    for i in range(len(h)):
        #print()
        #print(i)
        proc = Statement(e[i], h[i])
        tokens = proc.getTokens()
        print(tokens)

        wrapper += '\n<p>'
        for j in tokens: #for every list in the list tokens
            if len(j) >= 1:
                for tup in j: #for every tuple in each list j
                    if tup[0] == "LITERAL":
                        wrapper += '<b>'

                    if tup[2] == 'NAME':
                        name = tup[1] #if it's tagged as name, get the name
                        p = person.find_one({'key': name}) #find this person in Mongo sefaria
                        if p is None:
                            # attempt variations of name to find the best match
                            # Attempt 1: Look in alternate names. There is a names
                            # array and within each element, a text array. We can
                            # find Rabbi Eliezer as:
                            # { 'names.text.0': 'Rabbi', 'names.text.1': 'Eliezer'}
                            search = {'names.text.' + str(i): n for i, n in enumerate(name.split())}
                            import re
                            search['generation'] = re.compile('^[TA].*')
                            p = person.find_one(search)

                        if p is None:
                            # Attempt 2: assume it is a prefix.
                            # Case of Rabbi Eliezer as Rabbi Eliezer ben Hyrcanus
                            # We could make a list of such shorthands, or we
                            # can do our best, and not worry about noise
                            import re
                            regName = re.compile('^' + name + '.*')
                            regTannaOrAmora = re.compile('^[TA].*')
                            p = person.find_one({'key': regName, 'generation': regTannaOrAmora})

                        if p is not None:
                            names.add(p['key'])
                            #/////////do we want the whole node like {'name': 'Abaye', 'label': 'Person', 'id': 25}? In the example, just had the name.
                        try: #if 'generation' in p:
                            if p is not None:
                                clss, gen = genSplit(p['generation']) #returns a tuple of the class and generation
                                # store in dictionary just for fun
                                pplDict[p['key']] = (p['names'][0]['text'], p['names'][1]['text'], clss, gen)  # key = eng name, data = eng name, heb name, class (Amora or Tanna), generation
                                #make the necessary adjustments in the html and output it
                                wrapper += '<span class="%s" generation="%s">%s</span> ' % (clss, gen, name)
                            else:
                                w = tup[1]
                                wrapper += w + ' '

                                print('name: ' + name + ' is not found')
                        except Exception as e:
                            print(e)
                            print("ERROR.  P is:", p)
                    else:
                        w = tup[1]
                        wrapper += w + ' '

                    if tup[0] == "LITERAL":
                        wrapper += '</b> '

        wrapper += '</p>'

    # fix up tags like < strong >
    wrapper = wrapper.replace('< ', '<')
    wrapper = wrapper.replace(' >', '>')


#//////////////////////////made all the curly brackets double to escape so I could use a formatted string
    wrapper += '''
    </div>
    <div id="divB"></div>

<script type="text/javascript">
    var w = 1000;
    var h = 600;
    var linkDistance=200;
    var colors = d3.scale.category10();
    var dataset = {
    nodes: ******NODES******,
    edges: ******EDGES******
    };
    var svg = d3.select("#divB").append("svg").attr({"width":w,"height":h});
    var force = d3.layout.force()
        .nodes(dataset.nodes)
        .links(dataset.edges)
        .size([w,h])
        .linkDistance([linkDistance])
        .charge([-500])
        .theta(0.1)
        .gravity(0.05)
        .start();
    var edges = svg.selectAll("line")
      .data(dataset.edges)
      .enter()
      .append("line")
      .attr("id",function(d,i) {return 'edge'+i})
      .attr('marker-end','url(#arrowhead)')
      .style("stroke","green")
      .style("pointer-events", "none");
    var nodes = svg.selectAll("circle")
      .data(dataset.nodes)
      .enter()
      .append("circle")
      .attr({"r":40})
      .style("fill",function(d,i){return colors(i);})
      .call(force.drag)
    var nodelabels = svg.selectAll(".nodelabel")
       .data(dataset.nodes)
       .enter()
       .append("text")
       .attr({"text-anchor":"middle",
              "class":"nodelabel",
              "stroke":"black"})
       .text(function(d){return d.name;})
    var edgepaths = svg.selectAll(".edgepath")
        .data(dataset.edges)
        .enter()
        .append('path')
        .attr({'d': function(d) {return 'M '+d.source.x+' '+d.source.y+' L '+ d.target.x +' '+d.target.y},
               'class':'edgepath',
               'fill-opacity':0,
               'stroke-opacity':0,
               'fill':'blue',
               'stroke':'red',
               'id':function(d,i) {return 'edgepath'+i}})
        .style("pointer-events", "none");
    var edgelabels = svg.selectAll(".edgelabel")
        .data(dataset.edges)
        .enter()
        .append('text')
        .style("pointer-events", "none")
        .attr({'class':'edgelabel',
               'id':function(d,i){return 'edgelabel'+i},
               'dx':80,
               'dy':0,
               'font-size':10,
               'fill':'#aaa'});
    edgelabels.append('textPath')
        .attr('xlink:href',function(d,i) {return '#edgepath'+i})
        .style("pointer-events", "none")
        .text(function(d,i){return d['label']});
    svg.append('defs').append('marker')
        .attr({'id':'arrowhead',
               'viewBox':'-0 -5 10 10',
               'refX':50,
               'refY':0,
               //'markerUnits':'strokeWidth',
               'orient':'auto',
               'markerWidth':10,
               'markerHeight':10,
               'xoverflow':'visible'})
        .append('svg:path')
            .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
            .attr('fill', 'green')
            .attr('stroke','green');
    force.on("tick", function(){
        edges.attr({"x1": function(d){return d.source.x;},
                    "y1": function(d){return d.source.y;},
                    "x2": function(d){return d.target.x;},
                    "y2": function(d){return d.target.y;}
        });
        nodes.attr({"cx":function(d){return d.x;},
                    "cy":function(d){return d.y;}
        });
        nodelabels.attr("x", function(d) { return d.x; })
                  .attr("y", function(d) { return d.y; });
        edgepaths.attr('d', function(d) { var path='M '+d.source.x+' '+d.source.y+' L '+ d.target.x +' '+d.target.y;
                                           //console.log(d)
                                           return path});
        edgelabels.attr('transform',function(d,i){
            if (d.target.x<d.source.x){
                bbox = this.getBBox();
                rx = bbox.x+bbox.width/2;
                ry = bbox.y+bbox.height/2;
                return 'rotate(180 '+rx+' '+ry+')';
                }
            else {
                return 'rotate(0)';
                }
        });
    });
</script>
</div>
</body>
</html>        
    '''

    allRabbis = [key for key in pplDict]
    edges, nodes = graphOutput.findRelationship2(allRabbis)

    wrapper = wrapper.replace('******NODES******', str(nodes)).replace('******EDGES******', str(edges))
    # wrapper.format(nodes, ))


    ''' Sample nodes and edges code:
    var dataset = {
    nodes: [
    {'name': "Rava"},
    {'name': "Rav Zevid"},
    {'name': "Rav Naḥman bar Yitzḥak"},
    {'name': "Rav Pappa"},
    {'name': "Ravina I"},
    ],
    edges: [
    {source: 1, target: 0, label: 'student'},
    {source: 3, target: 0, label: 'student'},
    {source: 2, target: 0, label: 'student'},
    {source: 3, target: 1, label: 'bar plugta'},
    {source: 1, target: 3, label: 'bar plugta'},
    ]
    };'''


    f.write(wrapper)
    f.close()

htmlOutputter("Horayot", '3b')