from numpy import abs, allclose, arange
from numpy import array as np_array
from numpy import linspace, sqrt, square, sum
from pytest import mark

from dagflow.core.graph import Graph
from dagflow.lib.arithmetic import (
    Abs,
    Difference,
    Division,
    Product,
    ProductShifted,
    ProductShiftedScaled,
    Sqrt,
    Square,
    Sum,
)
from dagflow.lib.common import Array
from dagflow.plot.graphviz import savegraph


@mark.parametrize("dtype", ("d", "f"))
def test_Sum_01(testname, debug_graph, dtype):
    arrays_in = tuple(arange(12, dtype=dtype) * i for i in (1, 2, 3))

    with Graph(close_on_exit=True, debug=debug_graph) as graph:
        arrays = tuple(
            Array(f"arr_{i}", array_in, mode="fill") for i, array_in in enumerate(arrays_in)
        )
        sm = Sum("sum")
        arrays >> sm

    output = sm.outputs[0]

    res = sum(arrays_in, axis=0)

    assert sm.tainted == True
    assert all(output.data == res)
    assert sm.tainted == False

    for i in range(len(arrays_in)):
        arrays_in[i][:] = 2.3 * (i + 2) ** 2 + i
        res = arrays_in[0] + arrays_in[1] + arrays_in[2]
        arrays[i].outputs[0].set(2.3 * (i + 2) ** 2 + i)
        assert sm.tainted == True
        assert all(output.data == res)
        assert sm.tainted == False

    savegraph(graph, f"output/{testname}.png")


@mark.parametrize("dtype", ("d", "f"))
def test_Difference_01(testname, debug_graph, dtype):
    arrays_in = tuple(arange(12, dtype=dtype) * i for i in (1, 2, 3))

    with Graph(close_on_exit=True, debug=debug_graph) as graph:
        arrays = tuple(
            Array(f"arr_{i}", array_in, mode="fill") for i, array_in in enumerate(arrays_in)
        )
        sm = Difference("sum")
        arrays >> sm

    output = sm.outputs[0]

    res = arrays_in[0] - sum(arrays_in[1:], axis=0)

    assert sm.tainted == True
    assert all(output.data == res)
    assert sm.tainted == False

    for i in range(len(arrays_in)):
        arrays_in[i][:] = 2.3 * (i + 2) ** 2 + i
        res = arrays_in[0] - arrays_in[1] - arrays_in[2]
        arrays[i].outputs[0].set(2.3 * (i + 2) ** 2 + i)
        assert sm.tainted == True
        assert all(output.data == res)
        assert sm.tainted == False

    savegraph(graph, f"output/{testname}.png")


@mark.parametrize("dtype", ("d", "f"))
def test_Product_01(testname, debug_graph, dtype):
    arrays_in = tuple(arange(12, dtype=dtype) * i for i in (1, 2, 3))

    with Graph(close_on_exit=True, debug=debug_graph) as graph:
        arrays = tuple(
            Array(f"arr_{i}", array_in, mode="fill") for i, array_in in enumerate(arrays_in)
        )
        prod = Product("prod")
        arrays >> prod

    output = prod.outputs[0]
    res = arrays_in[0] * arrays_in[1] * arrays_in[2]

    assert prod.tainted == True
    assert (output.data == res).all()
    assert prod.tainted == False

    for i in range(len(arrays_in)):
        arrays_in[i][:] = 2.3 * (i + 2) ** 2 + i
        res = arrays_in[0] * arrays_in[1] * arrays_in[2]
        arrays[i].outputs[0].set(2.3 * (i + 2) ** 2 + i)
        assert prod.tainted == True
        assert all(output.data == res)
        assert prod.tainted == False

    savegraph(graph, f"output/{testname}.png")


@mark.parametrize("dtype", ("d", "f"))
@mark.parametrize("scaled", (False, True))
def test_ProductShifted_01(testname, debug_graph, dtype: str, scaled: bool):
    arrays_in = tuple(arange(12, dtype=dtype) * i for i in (1, 2, 3))
    shift = 1.23245

    with Graph(close_on_exit=True, debug=debug_graph) as graph:
        arrays = tuple(
            Array(f"arr_{i}", array_in, mode="fill") for i, array_in in enumerate(arrays_in)
        )
        if scaled:
            prod = ProductShiftedScaled("prod", shift=shift)
        else:
            prod = ProductShifted("prod", shift=shift)
        arrays >> prod

    output = prod.outputs[0]

    def getres():
        if scaled:
            return arrays_in[0] * (shift + arrays_in[1] * arrays_in[2])

        return shift + arrays_in[0] * arrays_in[1] * arrays_in[2]

    res = getres()

    assert prod.tainted == True
    assert (output.data == res).all()
    assert prod.tainted == False

    for i in range(len(arrays_in)):
        arrays_in[i][:] = 2.3 * (i + 2) ** 2 + i
        res = getres()
        arrays[i].outputs[0].set(2.3 * (i + 2) ** 2 + i)
        assert prod.tainted == True
        assert all(output.data == res)
        assert prod.tainted == False

    savegraph(graph, f"output/{testname}.png")


@mark.parametrize("dtype", ("d", "f"))
def test_Division_01(testname, debug_graph, dtype):
    arrays_in = tuple(arange(12, dtype=dtype) * i + 1 for i in (1, 2, 3))

    with Graph(close_on_exit=True, debug=debug_graph) as graph:
        arrays = tuple(
            Array(f"arr_{i}", array_in, mode="fill") for i, array_in in enumerate(arrays_in)
        )
        div = Division("division")
        arrays >> div

    output = div.outputs[0]
    res = arrays_in[0] / arrays_in[1] / arrays_in[2]

    assert div.tainted == True
    assert (output.data == res).all()
    assert div.tainted == False

    for i in range(len(arrays_in)):
        arrays_in[i][:] = 2.3 * (i + 2) ** 2 + i
        res = arrays_in[0] / arrays_in[1] / arrays_in[2]
        arrays[i].outputs[0].set(2.3 * (i + 2) ** 2 + i)
        assert div.tainted == True
        assert all(output.data == res)
        assert div.tainted == False

    savegraph(graph, f"output/{testname}.png")


@mark.parametrize("dtype", ("d", "f"))
@mark.parametrize("function", (square, sqrt))
def test_Powers_01(testname, debug_graph, function, dtype):
    if function == square:
        arrays_in = tuple(linspace(-10, 10, 101, dtype=dtype) * i for i in (1, 2, 3))
        cls = Square
        name = "Square"
    else:
        arrays_in = tuple(linspace(0, 10, 101, dtype=dtype) * i for i in (1, 2, 3))
        cls = Sqrt
        name = "Sqrt"

    with Graph(close_on_exit=True, debug=debug_graph) as graph:
        arrays = tuple(
            Array(f"arr_{i}", array_in, label={"text": f"X axis {i}"}, mode="fill")
            for i, array_in in enumerate(arrays_in)
        )
        node = cls(name)
        arrays >> node

    outputs = node.outputs
    ress = function(arrays_in)

    assert node.tainted == True
    assert all(output.dd.dtype == dtype for output in outputs)
    assert allclose(tuple(outputs.iter_data()), ress, rtol=0, atol=0)
    assert node.tainted == False

    for i in range(len(arrays_in)):
        arrays_in[i][:] = 2.3 * (i + 2) ** 2 + i
        ress = function(arrays_in)
        arrays[i].outputs[0].set(2.3 * (i + 2) ** 2 + i)
        assert node.tainted == True
        assert all(output.dd.dtype == dtype for output in outputs)
        assert allclose(tuple(outputs.iter_data()), ress, rtol=0, atol=0)
        assert node.tainted == False

    savegraph(graph, f"output/{testname}.png", show="full")


@mark.parametrize("dtype", ("d", "f"))
@mark.parametrize("data", ([1, -1], [1], [-1]))
def test_Abs(testname, debug_graph, data, dtype):
    array_data = np_array(data)
    with Graph(close_on_exit=True, debug=debug_graph) as graph:
        array = Array(f"arr", array_data, mode="fill")
        abs_node = Abs("prod")
        array >> abs_node

    output = abs_node.outputs[0]

    assert abs_node.tainted == True
    assert (output.data == [x if x > 0 else -x for x in data]).all()
    assert abs_node.tainted == False
