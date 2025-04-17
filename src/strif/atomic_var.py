import copy as cpy
import threading
from collections.abc import Callable
from contextlib import contextmanager
from typing import Any, Generic, TypeVar

T = TypeVar("T")


def value_is_immutable(obj: Any) -> bool:
    """
    Check if a value is of a known immutable type. Just a heuristic for common
    cases and not perfect.
    """
    immutable_types = (int, float, bool, str, tuple, frozenset, type(None), bytes, complex)
    if isinstance(obj, immutable_types):
        return True
    if hasattr(obj, "__dataclass_params__") and getattr(obj.__dataclass_params__, "frozen", False):
        return True
    return False


class AtomicVar(Generic[T]):
    """
    `AtomicVar` is a simple zero-dependency thread-safe variable that works
    for any type.

    Often the standard "Pythonic" approach is to use locks directly, but for
    some common use cases, `AtomicVar` may be simpler and more readable.
    Works on any type, including lists and dicts.

    Other options include `threading.Event` (for shared booleans),
    `threading.Queue` (for producer-consumer queues), and `multiprocessing.Value`
    (for process-safe primitives).

    Examples:

    ```python
    # Immutable types are always safe:
    count = AtomicVar(0)
    count.update(lambda x: x + 5)  # In any thread.
    count.set(0)  # In any thread.
    current_count = count.value  # In any thread.

    # Useful for flags:
    global_flag = AtomicVar(False)
    global_flag.set(True)  # In any thread.
    if global_flag:  # In any thread.
        print("Flag is set")


    # For mutable types,consider using `copy` or `deepcopy` to access the value:
    my_list = AtomicVar([1, 2, 3])
    my_list_copy = my_list.copy()  # In any thread.
    my_list_deepcopy = my_list.deepcopy()  # In any thread.

    # For mutable types, the `updates()` context manager gives a simple way to
    # lock on updates:
    with my_list.updates() as value:
        value.append(5)

    # Or if you prefer, via a function:
    my_list.update(lambda x: x.append(4))  # In any thread.

    # You can also use the var's lock directly. In particular, this encapsulates
    # locked one-time initialization:
    initialized = AtomicVar(False)
    with initialized.lock:
        if not initialized:  # checks truthiness of underlying value
            expensive_setup()
            initialized.set(True)

    # Or:
    lazy_var: AtomicVar[list[str] | None] = AtomicVar(None)
    with lazy_var.lock:
        if not lazy_var:
            lazy_var.set(expensive_calculation())
    ```
    """

    def __init__(self, initial_value: T, is_immutable: bool | None = None):
        self._value: T = initial_value
        # Use an RLock just in case we read from the var while in an update().
        self.lock: threading.RLock = threading.RLock()
        self.is_immutable: bool
        if is_immutable is None:
            self.is_immutable = value_is_immutable(initial_value)
        else:
            self.is_immutable = is_immutable

    @property
    def value(self) -> T:
        """
        Current value. For immutable types, this is thread safe. For mutable types,
        this gives direct access to the value, so you should consider using `copy` or
        `deepcopy` instead.
        """
        with self.lock:
            return self._value

    def copy(self) -> T:
        """
        Shallow copy of the current value.
        """
        with self.lock:
            return cpy.copy(self._value)

    def deepcopy(self) -> T:
        """
        Deep copy of the current value.
        """
        with self.lock:
            return cpy.deepcopy(self._value)

    def set(self, new_value: T) -> None:
        with self.lock:
            self._value = new_value

    def swap(self, new_value: T) -> T:
        """
        Set to new value and return the old value.
        """
        with self.lock:
            old_value = self._value
            self._value = new_value
            return old_value

    def update(self, update_func: Callable[[T], T | None]) -> T:
        """
        Update value with a function and return the new value.

        The `update_func` can either return a new value or update a mutable type in place,
        in which case it should return None. Always returns the final value of the
        variable after the update.
        """
        with self.lock:
            result = update_func(self._value)
            if result is not None:
                self._value = result
            # Always return the potentially updated self._value
            return self._value

    @contextmanager
    def updates(self):
        """
        Context manager for convenient thread-safe updates. Only applicable to
        mutable types.

        Example usage:
        ```
        my_list = AtomicVar([1, 2, 3])
        with my_list.updates() as value:
            value.append(4)
        ```
        """
        # Sanity check to avoid accidental use with atomic/immutable types.
        if self.is_immutable:
            raise ValueError("Cannot use AtomicVar.updates() context manager on an immutable value")
        with self.lock:
            yield self._value

    def __bool__(self) -> bool:
        """
        Truthiness matches that of the underlying value.
        """
        return bool(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"

    def __str__(self) -> str:
        return str(self.value)
