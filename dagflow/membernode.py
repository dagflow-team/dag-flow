from __future__ import print_function
from dagflow.node import Node
from dagflow.tools import undefinedgraph
from dagflow.graph import Graph

class MemberNodesHolder(object):
    _graph = undefinedgraph
    def __init__(self, graph=None):
        self.graph=graph
        for key in dir(self):
            val = getattr(self, key)
            if isinstance(val, (Node)):
                val.obj=self
                val.graph=self._graph

    @property
    def graph(self):
        return self._graph

    @graph.setter
    def graph(self, graph):
        if self._graph:
            raise Exception('Graph is already set')

        if graph is True:
            self._graph = Graph()
        elif isinstance(graph, str):
            self._graph = Graph(label=graph)
        elif isinstance(graph, dict):
            self._graph = Graph(**kwargs)
        elif graph:
            self._graph = graph

class MemberNode(Node):
    """Function signature: fcn(master, node, inputs, outputs)"""
    _obj = None
    def __init__(self, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)

    def _eval(self):
        self._evaluating = True
        ret = self._fcn(self._obj, self, inputs, outputs)
        self._evaluating = False
        return ret

    @property
    def obj(self):
        return self._obj

    @obj.setter
    def obj(self, obj):
        self._obj = obj

    def _stash_fcn(self):
        prev_fcn = self._fcn
        self._fcn_chain.append(prev_fcn)
        return lambda node, inputs, outputs: prev_fcn(node._obj, node, inputs, outputs)

    def _make_wrap(self, prev_fcn, wrap_fcn):
        def wrapped_fcn(master, node, inputs, outputs):
            wrap_fcn(prev_fcn, node, inputs, outputs)
        return wrapped_fcn

class StaticMemberNode(Node):
    """Function signature: fcn(self)"""
    _obj = None
    _touch_inputs = True
    def __init__(self, *args, **kwargs):
        self._touch_inputs = kwargs.pop('touch_inputs', True)
        Node.__init__(self, *args, **kwargs)

    def _eval(self):
        self._evaluating = True
        if self._touch_inputs:
            self.inputs._touch()
        ret = self._fcn(self._obj)
        self._evaluating = False
        return ret

    @property
    def obj(self):
        return self._obj

    @obj.setter
    def obj(self, obj):
        self._obj = obj

    def _stash_fcn(self):
        prev_fcn = self._fcn
        self._fcn_chain.append(prev_fcn)
        return lambda node, inputs, outputs: prev_fcn(node._obj)

    def _make_wrap(self, prev_fcn, wrap_fcn):
        def wrapped_fcn(master):
            wrap_fcn(prev_fcn, self, self.inputs, self.outputs)
        return wrapped_fcn

