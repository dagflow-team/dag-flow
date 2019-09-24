#!/usr/bin/env python

from __future__ import print_function
from dagflow.graph import Graph
from dagflow.graphviz import savegraph
import numpy as N
from dagflow.wrappers import *
from dagflow.input_extra import *

def test_00():
    graph = Graph()

    in1 = graph.add_node('n1', output='o1')
    in2 = graph.add_node('n2', output='o1')
    in3 = graph.add_node('n3', output='o1')
    in4 = graph.add_node('n4', output='o1')

    s = graph.add_node('add', missing_input_handler=MissingInputFail)

    try:
        (in1, in2, in3) >> s
    except:
        pass

    savegraph(graph, 'output/missing_input_handler_00.pdf', label='Fail on connect')

def test_01():
    graph = Graph()

    in1 = graph.add_node('n1', output='o1')
    in2 = graph.add_node('n2', output='o1')
    in3 = graph.add_node('n3', output='o1')
    in4 = graph.add_node('n4', output='o1')

    s = graph.add_node('add', missing_input_handler=MissingInputAdd)

    (in1, in2, in3) >> s
    in4 >> s

    print()
    print('test 01')
    s.print()

    savegraph(graph, 'output/missing_input_handler_01.pdf', label='Add only inputs')

def test_02():
    graph = Graph()

    in1 = graph.add_node('n1', output='o1')
    in2 = graph.add_node('n2', output='o1')
    in3 = graph.add_node('n3', output='o1')
    in4 = graph.add_node('n4', output='o1')

    s = graph.add_node('add', missing_input_handler=MissingInputAddPair)

    (in1, in2, in3) >> s
    in4 >> s

    print()
    print('test 02')
    s.print()

    for input, output in zip(s.inputs, s.outputs):
        assert input.corresponding_output is output

    savegraph(graph, 'output/missing_input_handler_02.pdf', label='Add inputs and an output for each input')

def test_03():
    graph = Graph()

    in1 = graph.add_node('n1', output='o1')
    in2 = graph.add_node('n2', output='o1')
    in3 = graph.add_node('n3', output='o1')
    in4 = graph.add_node('n4', output='o1')

    s = graph.add_node('add', missing_input_handler=MissingInputAddOne)

    (in1, in2, in3) >> s
    in4 >> s

    print()
    print('test 03')
    s.print()

    savegraph(graph, 'output/missing_input_handler_03.pdf', label='Add only inputs and only one output')

def test_04():
    graph = Graph()

    in1 = graph.add_node('n1', output='o1')
    in2 = graph.add_node('n2', output='o1')
    in3 = graph.add_node('n3', output='o1')
    in4 = graph.add_node('n4', output='o1')

    s = graph.add_node('add', missing_input_handler=MissingInputAddOne(add_corresponding_output=True))

    (in1, in2, in3) >> s
    in4 >> s

    print()
    print('test 04')
    s.print()

    output = s.outputs[0]
    for input in s.inputs:
        assert input.corresponding_output is output

    savegraph(graph, 'output/missing_input_handler_04.pdf', label='Add inputs and only one output')

def test_05():
    graph = Graph()

    in1 = graph.add_node('n1', output='o1')
    in2 = graph.add_node('n2', output='o1')
    in3 = graph.add_node('n3', output='o1')
    in4 = graph.add_node('n4', output='o1')

    s = graph.add_node('add', missing_input_handler=MissingInputAddEach(add_corresponding_output=False))

    (in1, in2, in3) >> s
    in4 >> s

    print()
    print('test 05')
    s.print()

    savegraph(graph, 'output/missing_input_handler_05.pdf', label='Add inputs and an output for each block')

def test_06():
    graph = Graph()

    in1 = graph.add_node('n1', output='o1')
    in2 = graph.add_node('n2', output='o1')
    in3 = graph.add_node('n3', output='o1')
    in4 = graph.add_node('n4', output='o1')

    s = graph.add_node('add', missing_input_handler=MissingInputAddEach(add_corresponding_output=True))

    (in1, in2, in3) >> s
    in4 >> s

    print()
    print('test 06')
    s.print()

    o1, o2 = s.outputs
    for input in s.inputs[:3]:
        assert input.corresponding_output is o1
    for input in s.inputs[3:]:
        assert input.corresponding_output is o2

    savegraph(graph, 'output/missing_input_handler_06.pdf', label='Add inputs and an output for each block')

if __name__ == "__main__":
    test_00()
    test_01()
    test_02()
    test_03()
    test_04()
    test_05()
    test_06()

