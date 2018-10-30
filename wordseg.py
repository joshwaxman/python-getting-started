#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 26 00:29:19 2018

@author: kaylaboldt
"""

from typing import Dict, List, DefaultDict, Set
import re

Vertex = str
AdjList = Dict[Vertex, Set[Vertex]]


# create adjacency graph out of input, manipulates the h: AdjList input
def graph_grower(h: AdjList, text: list) -> None:
    line: str
    splitter: List
    v: str
    word: str

    for line in text:

        splitter = line.split()

        if len(splitter) >= 1:
            v = splitter[0]

            v = v.strip(":")
            if v not in h:
                h[v] = set()

            for word in splitter[1:]:

                word = word.strip('=')
                word = word.strip("(")
                word = word.strip(")")
                if re.match("[A-Z]+[0-9]+", word):

                    h[v].add(word)

                    if word not in h:
                        h[word] = set()


# dfs using an iterative function instead of recursion
def dfs(graph: AdjList, start, v) -> Set:
    visited: Set = set()
    stack: List = [start]
    vertex: str
    while stack:
        vertex = stack.pop()
        if vertex not in visited:
            visited.add(vertex)

            stack.extend(graph[vertex])

    return visited


# create an AdjList that is all the connections from that vertex
# not just the neighbors
# manipulates depend_graph, creating an AdjList that
# has all the connections for each vertex
def go_through(graph: AdjList, depend_graph: AdjList) -> AdjList:
    for vertex in graph:
        if vertex not in depend_graph:
            v = vertex
            depend_graph[v] = dfs(graph, vertex, v)

    return depend_graph


def cycle_detect(graph: AdjList) -> bool:
    depend_graph: AdjList = {}

    depend_graph = go_through(graph, depend_graph)

    vertex: str
    edge: str

    vertex: str
    edge: str

    for vertex in depend_graph:
        for edge in depend_graph[vertex]:
            if edge != vertex:
                if edge in depend_graph and vertex in depend_graph[edge]:
                    print("cycle detected," + str(edge) + "-->" + str(vertex) + "-->" + str(edge))
                    return True

    return False


# input
F = open("ex_list.txt", "r")
# process input
text: List = F.read().splitlines()

Adj_List: AdjList = {}

# adjList maker - create an Adj list where vertex is the index
# and it's dependency neighbor is the data in the set
graph_grower(Adj_List, text)

# test to see if there is a cycle
print(cycle_detect(Adj_List))

############################
##########################

# Connect to Neo4j

############################
    ##########################
from py2neo import *
graph = Graph(password="qwerty")

tranaction = graph.begin()
s = []
for i in Adj_List.keys():
    if i not in s:
        n0 = Node('Cell', name=i)
        transaction.create(n0)

        s.append(i)

    for j in Adj_List[i]:
        if j not in s:
            s.append(j)
            n1 = Node('Cell', name=j)
            transaction.create(n1)
        rel = Relationship(n0, None, n1)
        transaction.create(rel)
transaction.commit()
print("here")
print(graph)