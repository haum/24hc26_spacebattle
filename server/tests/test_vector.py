import pytest

from game.vector import vector


def test_vector_mod():
    assert vector.mod([1, 2], [10, 10]) == [1, 2]
    assert vector.mod([1, 2, 3], [10, 10, 10]) == [1, 2, 3]
    assert vector.mod([1, 2, 3, 4], [10, 10, 10, 10]) == [1, 2, 3, 4]

    assert vector.mod([11, 12], [10, 10]) == [1, 2]
    assert vector.mod([11, 12, 13], [10, 10, 10]) == [1, 2, 3]
    assert vector.mod([11, 12, 13, 14], [10, 10, 10, 10]) == [1, 2, 3, 4]


def test_vector_add_vectors():
    assert vector.add([1, 2], [3, 4]) == [4, 6]
    assert vector.add([1, 2, 3], [4, 5, 6]) == [5, 7, 9]
    assert vector.add([1, 2, 3, 4], [5, 6, 7, 8]) == [6, 8, 10, 12]

    assert vector.add([10, 20], [1, 2]) == [11, 22]
    assert vector.add([10, 20, 30], [1, 2, 3]) == [11, 22, 33]
    assert vector.add([10, 20, 30, 40], [1, 2, 3, 4]) == [11, 22, 33, 44]

    assert vector.add([1, 2], [-3, -4]) == [-2, -2]
    assert vector.add([1, 2, 3], [-4, -5, -6]) == [-3, -3, -3]
    assert vector.add([1, 2, 3, 4], [-5, -6, -7, -8]) == [-4, -4, -4, -4]


def test_vector_add_scalar():
    assert vector.add([1, 2], 5) == [6, 7]
    assert vector.add([1, 2, 3], 5) == [6, 7, 8]
    assert vector.add([1, 2, 3, 4], 5) == [6, 7, 8, 9]

    assert vector.add([1, 2], -5) == [-4, -3]
    assert vector.add([1, 2, 3], -5) == [-4, -3, -2]
    assert vector.add([1, 2, 3, 4], -5) == [-4, -3, -2, -1]


def test_vector_sub_vectors():
    assert vector.sub([4, 6], [3, 4]) == [1, 2]
    assert vector.sub([5, 7, 9], [4, 5, 6]) == [1, 2, 3]
    assert vector.sub([6, 8, 10, 12], [5, 6, 7, 8]) == [1, 2, 3, 4]

    assert vector.sub([11, 22], [1, 2]) == [10, 20]
    assert vector.sub([11, 22, 33], [1, 2, 3]) == [10, 20, 30]
    assert vector.sub([11, 22, 33, 44], [1, 2, 3, 4]) == [10, 20, 30, 40]

    assert vector.sub([-2, -2], [-3, -4]) == [1, 2]
    assert vector.sub([-3, -3, -3], [-4, -5, -6]) == [1, 2, 3]
    assert vector.sub([-4, -4, -4, -4], [-5, -6, -7, -8]) == [1, 2, 3, 4]


def test_vector_sub_scalar():
    assert vector.sub([6, 7], 5) == [1, 2]
    assert vector.sub([6, 7, 8], 5) == [1, 2, 3]
    assert vector.sub([6, 7, 8, 9], 5) == [1, 2, 3, 4]

    assert vector.sub([-4, -3], -5) == [1, 2]
    assert vector.sub([-4, -3, -2], -5) == [1, 2, 3]
    assert vector.sub([-4, -3, -2, -1], -5) == [1, 2, 3, 4]


def test_vector_mul():
    assert vector.mul([1, 2], 3) == [3, 6]
    assert vector.mul([1, 2, 3], 3) == [3, 6, 9]
    assert vector.mul([1, 2, 3, 4], 3) == [3, 6, 9, 12]

    assert vector.mul([1, 2], -3) == [-3, -6]
    assert vector.mul([1, 2, 3], -3) == [-3, -6, -9]
    assert vector.mul([1, 2, 3, 4], -3) == [-3, -6, -9, -12]


def test_vector_str():
    assert vector.str([1, 2]) == "[1.0, 2.0]"
    assert vector.str([1, 2, 3]) == "[1.0, 2.0, 3.0]"
    assert vector.str([1, 2, 3, 4]) == "[1.0, 2.0, 3.0, 4.0]"

    assert vector.str([0.123, 4]) == "[0.1, 4.0]"
    assert vector.str([0.123, 1.28, 4]) == "[0.1, 1.3, 4.0]"
    assert vector.str([0.123, 1.28, -0.65, 4]) == "[0.1, 1.3, -0.7, 4.0]"


def test_vector_autodim_no_modulo():
    assert vector.autodim([1], [10, 10], False) == [1, 0]
    assert vector.autodim([1], [10, 10, 10], False) == [1, 0, 0]
    assert vector.autodim([1], [10, 10, 10, 10], False) == [1, 0, 0, 0]

    assert vector.autodim([1, 1, 1, 1, 1], [10, 10], False) == [1, 1]
    assert vector.autodim([1, 1, 1, 1, 1], [10, 10, 10], False) == [1, 1, 1]
    assert vector.autodim([1, 1, 1, 1, 1], [10, 10, 10, 10], False) == [1, 1, 1, 1]

    assert vector.autodim([-1], [10, 10], False) == [-1, 0]
    assert vector.autodim([-1], [10, 10, 10], False) == [-1, 0, 0]
    assert vector.autodim([-1], [10, 10, 10, 10], False) == [-1, 0, 0, 0]

    assert vector.autodim([-1, -1, -1, -1, -1], [10, 10], False) == [-1, -1]
    assert vector.autodim([-1, -1, -1, -1, -1], [10, 10, 10], False) == [-1, -1, -1]
    assert vector.autodim([-1, -1, -1, -1, -1], [10, 10, 10, 10], False) == [-1, -1, -1, -1]


def test_vector_autodim_with_modulo():
    assert vector.autodim([1], [10, 10], True) == [1, 0]
    assert vector.autodim([1], [10, 10, 10], True) == [1, 0, 0]
    assert vector.autodim([1], [10, 10, 10, 10], True) == [1, 0, 0, 0]

    assert vector.autodim([1, 1, 1, 1, 1], [10, 10], True) == [1, 1]
    assert vector.autodim([1, 1, 1, 1, 1], [10, 10, 10], True) == [1, 1, 1]
    assert vector.autodim([1, 1, 1, 1, 1], [10, 10, 10, 10], True) == [1, 1, 1, 1]

    assert vector.autodim([-1], [10, 10], True) == [9, 0]
    assert vector.autodim([-1], [10, 10, 10], True) == [9, 0, 0]
    assert vector.autodim([-1], [10, 10, 10, 10], True) == [9, 0, 0, 0]

    assert vector.autodim([-1, -1, -1, -1, -1], [10, 10], True) == [9, 9]
    assert vector.autodim([-1, -1, -1, -1, -1], [10, 10, 10], True) == [9, 9, 9]
    assert vector.autodim([-1, -1, -1, -1, -1], [10, 10, 10, 10], True) == [9, 9, 9, 9]
