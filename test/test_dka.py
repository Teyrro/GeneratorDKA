import numpy
import pytest

from Widgets.models.dka import DKA


@pytest.fixture()
def get_dka() -> list[DKA]:
    result = []
    for i in range(1, 3):
        dka: DKA = DKA(None)
        dka.set_info("abc", "a", str(i))
        dka.create_dka()
        result.append(dka)

    subchain = ""
    char = "a"
    for i in range(3):
        dka: DKA = DKA(None, "abc", subchain, "1")
        dka.create_dka()
        result.append(dka)
        subchain += char
    return result


def test_one_multiplicity_dka(get_dka):
    arr: numpy = numpy.array(
        [
            [
                "q-1",
                "q-1",
                "q-1",
            ],
            [
                "q-1",
                "q0",
                "q0",
            ],
        ]
    )
    assert numpy.array_equal(arr, get_dka[0].dt.to_numpy())


def test_multiple_multiplicity_dka(get_dka):
    arr: numpy = numpy.array(
        [
            ["q-2", "q-2", "q-2"],
            ["q-1", "q-1", "q-1"],
            ["q-1", "q1", "q1"],
            ["q-2", "q0", "q0"],
        ]
    )
    assert numpy.array_equal(arr, get_dka[1].dt.to_numpy())


def test_empty_subchain_dka(get_dka):
    arr: numpy = numpy.array(
        [
            [
                "q-1",
                "q-1",
                "q-1",
            ]
        ]
    )
    assert numpy.array_equal(arr, get_dka[2].dt.to_numpy())


def test_multiple_subchain_dka(get_dka):
    arr: numpy = numpy.array(
        [
            ["q-1", "q-1", "q-1"],
            ["q1", "q0", "q0"],
            ["q-1", "q0", "q0"],
        ]
    )
    assert numpy.array_equal(arr, get_dka[4].dt.to_numpy())
