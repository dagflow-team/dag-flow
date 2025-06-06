from __future__ import annotations

from typing import TYPE_CHECKING

from numpy import add, divide, matmul, multiply, subtract, zeros
from scipy.linalg import solve_triangular

from ..node import Node
from ..typefunctions import (
    check_has_inputs,
    check_input_dimension,
    check_input_matrix_or_diag,
    check_inputs_equivalence,
    check_inputs_multiplicable_mat,
    copy_from_input_to_output,
)

if TYPE_CHECKING:
    from numpy.typing import NDArray

    from ..input import Input
    from ..output import Output


class NormalizeCorrelatedVars2(Node):
    """Normalize correlated variables or correlate normal variables with linear expression

    If x is a vector of values, μ are the central values and L is a cholesky decomposition
    of the covariance matrix V=LLᵀ then
    z = L⁻¹(x - μ)
    x = Lz + μ
    """

    __slots__ = (
        "_ndim",
        "_matrix",
        "_central",
        "_value",
        "_normvalue",
        "_matrix_input",
        "_central_input",
        "_value_input",
        "_normvalue_input",
        "_value_output",
        "_normvalue_output",
    )

    _ndim: str
    _matrix: NDArray
    _central: NDArray
    _value: NDArray
    _normvalue: NDArray

    _matrix_input: Input
    _central_input: Input
    _value_input: Input
    _normvalue_input: Input

    _value_output: Output
    _normvalue_output: Output

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            *args,
            **kwargs,
            allowed_kw_inputs=(
                "matrix",
                "central",
                "value",
                "normvalue",
            ),
        )
        self._fd.needs_postallocate = True
        self._labels.setdefault("mark", "c↔u")

        self._matrix_input = self._add_input("matrix", positional=False)
        self._central_input = self._add_input("central", positional=False)

        self._value_input, self._value_output = self._add_pair(
            "value",
            "value",
            input_kws={"allocatable": True},
            output_kws={"forbid_reallocation": True, "allocatable": False},
        )
        self._normvalue_input, self._normvalue_output = self._add_pair(
            "normvalue",
            "normvalue",
            input_kws={"allocatable": True},
            output_kws={"forbid_reallocation": True, "allocatable": False},
        )

        self._functions.update(
            {
                "forward_2d": self._fcn_forward_2d,
                "forward_1d": self._fcn_forward_1d,
                "backward_2d": self._fcn_backward_2d,
                "backward_1d": self._fcn_backward_1d,
            }
        )

    def _fcn_forward_2d(self):
        for callback in self._input_nodes_callbacks:
            callback()

        subtract(self._value, self._central, out=self._normvalue)
        solve_triangular(
            self._matrix,
            self._normvalue,
            lower=True,
            overwrite_b=True,
            check_finite=False,
        )

    def _fcn_backward_2d(self):
        for callback in self._input_nodes_callbacks:
            callback()

        matmul(self._matrix, self._normvalue, out=self._value)
        add(self._value, self._central, out=self._value)

    def _fcn_forward_1d(self):
        for callback in self._input_nodes_callbacks:
            callback()

        subtract(self._value, self._central, out=self._normvalue)
        divide(self._normvalue, self._matrix, out=self._normvalue)

    def _fcn_backward_1d(self):
        for callback in self._input_nodes_callbacks:
            callback()

        multiply(self._matrix, self._normvalue, out=self._value)
        add(self._value, self._central, out=self._value)

    def _on_taint(self, caller: Input) -> None:
        """Choose the function to call based on the modified input:
        - if normvalue is modified, the value should be updated
        - if value is modified, the normvalue should be updated
        - if sigma or central is modified, the normvalue should be updated

        TODO:
            - implement partial taintflag propagation
            - value should not be tainted on sigma/central modificantion
        """
        if caller is self._normvalue_input:
            self.fcn = self._functions[f"backward_{self._ndim}"]
        else:
            self.fcn = self._functions[f"forward_{self._ndim}"]

    def _typefunc(self) -> None:
        check_has_inputs(self)
        ndim = check_input_matrix_or_diag(self, "matrix", check_square=True)
        check_input_dimension(self, "central", 1)
        check_inputs_equivalence(self, ("central", slice(None)))
        check_inputs_multiplicable_mat(self, "matrix", slice(None))
        copy_from_input_to_output(self, slice(None), slice(None))

        self.labels.inherit(
            self._value_input.parent_node.labels,
            fmtlong="[norm] {}",
            fmtshort="n({})",
        )

        self._ndim = f"{ndim}d"
        self.fcn = self._functions[f"forward_{self._ndim}"]

        self._value = zeros(shape=self._value_input.dd.shape, dtype=self._value_input.dd.dtype)
        self._normvalue = zeros(
            shape=self._normvalue_input.dd.shape,
            dtype=self._normvalue_input.dd.dtype,
        )
        self._value_input.set_own_data(self._value, owns_buffer=False)
        self._normvalue_input.set_own_data(self._normvalue, owns_buffer=False)
        self._value_output._set_data(self._value, owns_buffer=False, forbid_reallocation=True)
        self._normvalue_output._set_data(
            self._normvalue, owns_buffer=False, forbid_reallocation=True
        )

    def _post_allocate(self):
        super()._post_allocate()

        self._matrix = self.inputs["matrix"].data_unsafe
        self._central = self.inputs["central"].data_unsafe
