import numpy as np
import pytest

from pipeline.utils.vectors import EMPTY_EMBEDDING, pack_embedding, unpack_embedding, unpack_matrix


def test_pack_then_unpack_round_trips():
    values = [0.5, -0.25, 1.0, 0.0]
    assert unpack_embedding(pack_embedding(values)).tolist() == values


def test_packing_is_four_bytes_per_float():
    assert len(pack_embedding([1.0] * 768)) == 768 * 4


def test_packing_is_little_endian_regardless_of_host():
    # 1.0f is 00 00 80 3f little-endian. Pinning this keeps rows written on one
    # architecture readable on another.
    assert pack_embedding([1.0]) == b"\x00\x00\x80\x3f"


def test_empty_and_none_pack_to_the_empty_marker():
    assert pack_embedding([]) == EMPTY_EMBEDDING
    assert pack_embedding(None) == EMPTY_EMBEDDING
    assert unpack_embedding(EMPTY_EMBEDDING).size == 0


def test_unpack_rejects_a_blob_that_is_not_whole_floats():
    with pytest.raises(ValueError, match="not a whole number"):
        unpack_embedding(b"\x00\x00\x80")


def test_unpack_accepts_a_memoryview():
    blob = pack_embedding([1.0, 2.0])
    assert unpack_embedding(memoryview(blob)).tolist() == [1.0, 2.0]


def test_unpack_matrix_builds_one_2d_array():
    matrix = unpack_matrix([pack_embedding([1.0, 0.0]), pack_embedding([0.0, 1.0])])
    assert matrix.shape == (2, 2)
    assert matrix.dtype == np.dtype("<f4")
    assert matrix.tolist() == [[1.0, 0.0], [0.0, 1.0]]


def test_unpack_matrix_rejects_mixed_dimensions():
    with pytest.raises(ValueError, match="same dimension"):
        unpack_matrix([pack_embedding([1.0, 0.0]), pack_embedding([1.0, 0.0, 0.0])])


def test_unpack_matrix_of_nothing_is_empty():
    assert unpack_matrix([]).shape == (0, 0)


def test_float32_precision_is_preserved_exactly():
    original = np.random.default_rng(0).random(768).astype(np.float32)
    assert np.array_equal(unpack_embedding(pack_embedding(original)), original)
