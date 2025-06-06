from ..inputhandler import MissingInputAddOne
from ..typefunctions import check_has_inputs, check_input_dimension, check_input_dtype
from .ManyToOneNode import ManyToOneNode


class Concatenation(ManyToOneNode):
    """
    Creates a node with a single data output which is a concatenated data of the inputs.
    Now supports only 1d arrays.
    """

    __slots__ = (
        "_offsets",
        "_sizes",
    )

    _offsets: tuple[int,...]
    _sizes: tuple[int,...]

    def __init__(self, name, **kwargs):
        kwargs.setdefault("missing_input_handler", MissingInputAddOne(output_fmt="result"))
        super().__init__(name, **kwargs)
        self._offsets = ()
        self._sizes = ()

    def _typefunc(self) -> None:
        """A output takes this function to determine the dtype and shape"""
        check_has_inputs(self)
        cdtype = self.inputs[0].dd.dtype
        check_input_dtype(self, slice(None), cdtype)
        check_input_dimension(self, slice(None), 1)
        _output = self.outputs["result"]

        offset = 0
        offsets, sizes = [], []
        for input in self.inputs:
            offsets.append(offset)
            newsize = input.dd.shape[0]
            offset += newsize
            sizes.append(newsize)
        _output.dd.shape = (offset,)
        _output.dd.dtype = cdtype

        self._offsets = tuple(offsets)
        self._sizes = tuple(sizes)

    def _fcn(self):
        _output = self.outputs["result"]
        data = _output.data
        for offset, _input in zip(self._offsets, self.inputs):
            size = _input.dd.shape[0]
            data[offset : offset + size] = _input.data[:]

    @property
    def sizes(self) -> list[int]:
        return self._sizes

