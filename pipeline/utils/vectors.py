"""Byte format for stored embedding vectors.

`BeatSegment.embedding` is a BinaryField holding a dense little-endian float32
array. A blob is opaque to the database, so the format contract lives here and is
enforced on read: the dtype is pinned (never native-endian, which would silently
depend on the CPU that wrote the row) and the length must be a whole number of
floats.

An unembedded segment stores b"" -- the binary equivalent of the empty list the
JSONField used to hold.
"""

import numpy as np


EMBEDDING_DTYPE = np.dtype("<f4")
EMPTY_EMBEDDING = b""


def pack_embedding(values) -> bytes:
    """Serialise a sequence of floats (or an ndarray) to stored bytes."""
    if values is None or len(values) == 0:
        return EMPTY_EMBEDDING
    return np.asarray(values, dtype=EMBEDDING_DTYPE).tobytes()


def unpack_embedding(blob) -> np.ndarray:
    """Deserialise stored bytes back to a 1-D float32 array."""
    if not blob:
        return np.empty(0, dtype=EMBEDDING_DTYPE)
    return _frombuffer(blob)


def unpack_matrix(blobs) -> np.ndarray:
    """Deserialise many equal-length blobs into one (n, dim) float32 matrix.

    Concatenating first means a single frombuffer over the whole payload rather
    than one array object per row.
    """
    blobs = list(blobs)
    if not blobs:
        return np.empty((0, 0), dtype=EMBEDDING_DTYPE)

    dim = len(blobs[0]) // EMBEDDING_DTYPE.itemsize
    mismatched = next((i for i, blob in enumerate(blobs) if len(blob) != len(blobs[0])), None)
    if mismatched is not None:
        raise ValueError(
            f"embedding at index {mismatched} has {len(blobs[mismatched])} bytes, "
            f"expected {len(blobs[0])} -- stored vectors must all have the same dimension"
        )
    return _frombuffer(b"".join(bytes(blob) for blob in blobs)).reshape(len(blobs), dim)


def _frombuffer(blob) -> np.ndarray:
    if len(blob) % EMBEDDING_DTYPE.itemsize:
        raise ValueError(
            f"embedding blob is {len(blob)} bytes, not a whole number of "
            f"{EMBEDDING_DTYPE.itemsize}-byte floats"
        )
    # bytes() copies, which np.frombuffer needs anyway to own a writeable array;
    # it also normalises the memoryview some backends hand back.
    return np.frombuffer(bytes(blob), dtype=EMBEDDING_DTYPE)
