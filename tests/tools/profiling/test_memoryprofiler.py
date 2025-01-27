from __future__ import annotations

from typing import TYPE_CHECKING
from functools import reduce
from operator import mul
from itertools import chain

from pandas import DataFrame

from dagflow.tools.profiling import MemoryProfiler
from dagflow.core.input import Input
from test_helpers import graph_0, graph_1


if TYPE_CHECKING:
    from dagflow.core.output import Output
    from dagflow.core.input import Input
    from numpy.typing import NDArray


def _calc_numpy_size(data: NDArray) -> int:
    """Size of Numpy's `NDArray` in bytes"""
    length = reduce(mul, data.shape)
    return length * data.dtype.itemsize

def get_input_size(inp: Input) -> int:
    if inp.owns_buffer:
        return _calc_numpy_size(inp.own_data)
    return 0

def get_output_size(out: Output) -> int:
    if out.owns_buffer or (out.has_data and out._allocating_input is None):
        return _calc_numpy_size(out._data)
    return 0

def edge_size(edge: Output | Input) -> int:
    """Return size of `edge` data in bytes"""
    if isinstance(edge, Input):
        return get_input_size(edge)
    return get_output_size(edge)


def test_basic_edges_g0():
    _, nodes = graph_0()
    _, _, a2, _, _, _, _, s1, _, _, _, _ = nodes

    # A2 (1 output)
    out: Output = a2.outputs["array"]  # 'array' - default name for Array output

    actual_sizes = MemoryProfiler.estimate_node(a2)
    o_expected = edge_size(out)
    assert o_expected != 0
    assert o_expected == actual_sizes[out]

    # S1 (3 inputs, 2 outputs)
    actual_sizes = MemoryProfiler.estimate_node(s1)

    for inp in s1.inputs.iter_all():
        i_expected = edge_size(inp)
        assert i_expected == actual_sizes[inp]

    for out in s1.outputs.iter_all():
        o_expected = edge_size(out)
        assert o_expected == actual_sizes[out]


def test_array_store_mods_g0():
    """Test profiling behavior with different array store modes"""
    _, nodes = graph_0()
    _, a1, _, a3, _, p1, s0, _, _, _, _, _ = nodes

    # P1 (2 inputs, 2 outputs)
    #  parent output from 'A1' has Array node type with 'store_weak' mode
    sw_out: Output = a1.outputs["array"]
    conn_input: Input = p1.inputs[0]

    assert conn_input.parent_output == sw_out
    assert sw_out._allocating_input is None

    assert edge_size(conn_input) == 0
    assert edge_size(sw_out) != edge_size(conn_input)

    actual_sizes = MemoryProfiler.estimate_node(a1)
    assert edge_size(sw_out) == actual_sizes[sw_out]

    actual_sizes = MemoryProfiler.estimate_node(p1)
    assert edge_size(conn_input) == actual_sizes[conn_input]

    # S0 (2 inputs, 1 output)
    #  parent output from 'A3' has Array node type with 'fill' mode
    f_out: Output = a3.outputs["array"]
    conn_input: Input = s0.inputs[1]

    assert conn_input.parent_output == f_out


def test_estimate_all_edges():
    for graph in (graph_0, graph_1):
        _, nodes = graph()

        mp = MemoryProfiler(nodes)
        mp.estimate_target_nodes()

        assert hasattr(mp, "_estimations_table")

        # check if "size" column exists and it is not empty
        assert len(mp._estimations_table["size"]) > 0

        expected = 0
        for node in nodes:
            for edge in chain(node.inputs, node.outputs):
                expected += edge_size(edge)
        actual = mp._estimations_table["size"].sum()

        assert expected == actual, (
            "expected and actual sizes of all edges does not match"
        )


def test_total_size_property():
    _, nodes = graph_0()

    mp = MemoryProfiler(nodes)
    mp.estimate_target_nodes()

    assert sum(mp._estimations_table["size"]) == mp.total_size


def test_make_report():
    _, nodes = graph_0()

    mp = MemoryProfiler(nodes).estimate_target_nodes()
    report = mp.make_report()

    assert isinstance(report, DataFrame)


def test_print_report_g0():
    _, nodes = graph_0()

    mp = MemoryProfiler(nodes).estimate_target_nodes()
    mp.print_report(40, group_by=None, sort_by="type", aggregations=None)
    mp.print_report()

    mp = MemoryProfiler(nodes).estimate_target_nodes()
    mp.print_report()

    mp.print_report(group_by="node", aggregations=("sum", "mean"), sort_by="sum")

    # "single" also means "mean"
    mp.print_report(group_by="type", aggregations=["var", "single"])

    mp.print_report(group_by="edge_count")


def test_chain_methods_g1():
    _, nodes = graph_1()

    report = MemoryProfiler(nodes).estimate_target_nodes().print_report()
    assert isinstance(report, DataFrame)

    report = MemoryProfiler(nodes).estimate_target_nodes().make_report()
    assert isinstance(report, DataFrame)
