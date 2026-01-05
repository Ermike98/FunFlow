from typing import Callable
from .layer import Layer
from .templates import Template


class Functional(Layer):
    """
    A layer that wraps a standard Python function or lambda.
    """

    def __init__(self,
                 func: Callable,
                 inputs: str | Template | list[Template | str] = None,
                 outputs: str | Template | list[Template | str] = None,
                 call_type: str = "args",
                 **kwargs):
        """
        Initialize a Functional layer.

        :param func: The function or callable to wrap.
        :param inputs: Input names or templates.
        :param outputs: Output names or templates.
        :param call_type: How to call the function ("args" or "kwargs").
        :param kwargs: Additional metadata for the Layer base class.
        """
        super().__init__(inputs=inputs, outputs=outputs, call_type=call_type, **kwargs)
        self.__func = func

    def call(self, *args, **kwargs):
        """Invoke the wrapped function."""
        return self.__func(*args, **kwargs)

