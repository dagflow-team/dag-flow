#!/usr/bin/env python

from __future__ import print_function
from dagflow.graph import Graph
from dagflow.graphviz import GraphDot
from dagflow.wrappers import *

from dagflow.printl import printl, set_prefix_function, current_level
set_prefix_function(lambda: '{:<2d} '.format(current_level()),)

counter = 0
def test_graph_big_01():
    """Create a graph of nodes and test evaluation features"""
    g = Graph()
    label = None
    def plot(suffix=''):
        global counter
        d = GraphDot(g)
        newlabel = label and label+suffix or suffix
        if newlabel is not None:
            d.set_label(newlabel)
        d.savegraph('output/test_graph_big_{:03d}.png'.format(counter))
        counter+=1

    def plotter(fcn, node, inputs, outputs):
        plot('[start evaluating {}]'.format(node.name))
        fcn(node, inputs, outputs)
        plot('[done evaluating {}]'.format(node.name))

    A1 = g.add_node('A1')
    A2 = g.add_node('A2', auto_freeze=True, label='{name}|frozen')
    A3 = g.add_node('A3', immediate=True, label='{name}|immediate')
    B  = g.add_node('B')
    C1 = g.add_node('C1')
    C2 = g.add_node('C2')
    D  = g.add_node('D')
    E  = g.add_node('E')
    F  = g.add_node('F')
    H  = g.add_node('H')
    P  = g.add_node('P', immediate=True, label='{name}|immediate')

    g._wrap_fcns(toucher, printer, plotter)

    A1._add_output('o1')
    A2._add_output('o1')
    P._add_output('o1')
    A3._add_pair('i1', 'o1')
    B._add_pair(('i1', 'i2', 'i3', 'i4'), ('o1', 'o2'))
    C1._add_output('o1')
    C2._add_output('o1')
    D._add_pair('i1', 'o1')
    D._add_pair('i2', 'o2')
    H._add_pair('i1', 'o1')
    _, other = F._add_pair('i1', 'o1')
    _, final = E._add_pair('i1', 'o1')

    (A1, A2, (P>>A3), D[:1]) >> B >> (E, H)
    ((C1, C2) >> D[:,1]) >> F

    g.print()

    label = 'Initial graph state.'
    plot()

    label = 'Read E...'
    plot()
    plot()
    plot()
    final.data
    label = 'Done reading E.'
    plot()

    label = 'Taint D.'
    plot()
    plot()
    plot()
    D.taint()
    plot()
    label = 'Read F...'
    other.data
    label = 'Done reading F.'
    plot()

    label = 'Read E...'
    plot()
    plot()
    plot()
    final.data
    label = 'Done reading E.'
    plot()

    label = 'Taint A2.'
    plot()
    plot()
    plot()
    A2.taint()
    plot()
    label = 'Read E...'
    plot()
    final.data
    label = 'Done reading E.'
    plot()

    label = 'Unfreeze A2 (tainted).'
    plot()
    plot()
    plot()
    A2.unfreeze()
    plot()
    label = 'Read E...'
    plot()
    final.data
    label = 'Done reading E.'
    plot()

    label = 'Unfreeze A2 (not tainted).'
    plot()
    plot()
    plot()
    A2.unfreeze()
    plot()
    label = 'Read E...'
    plot()
    final.data
    label = 'Done reading E.'
    plot()

    label = 'Taint P'
    plot()
    plot()
    plot()
    P.taint()
    plot()
    label = 'Read E...'
    plot()
    final.data
    label = 'Done reading E.'
    plot()

    label = 'Invalidate P'
    plot()
    plot()
    plot()
    P.invalid = True
    plot()

    label = 'Validate P'
    plot()
    plot()
    plot()
    P.invalid = False
    plot()
    label = 'Read E...'
    plot()
    final.data
    label = 'Done reading E.'
    plot()

if __name__ == "__main__":
    test_graph_big_01()
