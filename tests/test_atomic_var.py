import threading
from dataclasses import dataclass

from strif import AtomicVar
from strif.atomic_var import value_is_immutable


def test_atomic_var_set_swap_update():
    var = AtomicVar(0)
    var.set(5)
    assert var.value == 5
    assert var.swap(10) == 5
    assert var.value == 10
    # update() with a returning function.
    assert var.update(lambda x: x + 1) == 11
    # update() with an in-place mutation returns None -> value unchanged reference.
    lst = AtomicVar([1, 2])
    assert lst.update(lambda x: x.append(3)) == [1, 2, 3]


def test_atomic_var_copy_independence():
    var = AtomicVar([[1], [2]])
    shallow = var.copy()
    deep = var.deepcopy()
    var.value[0].append(99)
    # Shallow copy shares inner lists; deep copy does not.
    assert shallow[0] == [1, 99]
    assert deep[0] == [1]


def test_atomic_var_updates_context_manager():
    var = AtomicVar([1, 2, 3])
    with var.updates() as value:
        value.append(4)
    assert var.value == [1, 2, 3, 4]


def test_atomic_var_updates_rejects_immutable():
    var = AtomicVar(0)
    try:
        with var.updates():
            pass
        raise AssertionError("updates() should reject immutable values")
    except ValueError:
        pass


def test_atomic_var_truthiness():
    assert not AtomicVar(0)
    assert AtomicVar(1)
    assert not AtomicVar([])
    assert AtomicVar([1])


def test_value_is_immutable():
    assert value_is_immutable(0)
    assert value_is_immutable("x")
    assert value_is_immutable((1, 2))
    assert not value_is_immutable([1, 2])
    assert not value_is_immutable({})

    @dataclass(frozen=True)
    class Frozen:
        x: int

    @dataclass
    class Mutable:
        x: int

    assert value_is_immutable(Frozen(1))
    assert not value_is_immutable(Mutable(1))


def test_atomic_var_concurrent_updates():
    # Without the lock serializing the read-modify-write, the final count would be
    # less than the expected total due to lost updates.
    var = AtomicVar(0)
    threads_count = 10
    increments = 1000

    def worker():
        for _ in range(increments):
            var.update(lambda x: x + 1)

    threads = [threading.Thread(target=worker) for _ in range(threads_count)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert var.value == threads_count * increments
