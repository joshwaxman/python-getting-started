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

F = open("ex_list.txt", "r")

text: list = F.read().splitlines()


def graph_grower(h: AdjList, text: list):
    for line in text:

        splitter = line.split()

        if len(splitter) >= 1:
            v = splitter[0]
            # COMMENT: next line not necessary
            v.strip(">")
            v.strip(":")

            h[v] = set()
            #
            for word in splitter[1:]:
                h[v].add(word)
                word.strip('=')
                word.strip("(")
                word.strip(")")

                h[v].add(word)
                # COMMENT: in next line, change g to h
                if v not in h:
                    h[v] = set()
    #
    #
    #
    #
    #
    print(h)


#
#
h: AdjList = {}
graph_grower(h, text)
# COMMENT: you need a visited set to make this work
visited = set()
def dfs(v: Vertex, g: AdjList):
    for u in g[v]:
        if u not in visited:
            visited.add(u)
            print(u)
            dfs(u, g)

# COMMENT: change g to h in next line; change 'a' to 'A1'
dfs('A1', h)