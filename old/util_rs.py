import warnings
from typing import (
    Optional,
    Tuple,
    Union,
)


DEFAULT_LENGTH_BEFORE_BLOCK = 25

def parse_rs_block_header(
    block: Union[bytes, bytearray],
    length_before_block: Optional[int] = None,
    raise_on_late_block: bool = False,
) -> Tuple[int, int]:
    """Parse the header of a IEEE block.

    Definite Length Arbitrary Block:
    #<header_length><data_length><data>

    The header_length specifies the size of the data_length field.
    And the data_length field specifies the size of the data.

    Indefinite Length Arbitrary Block:
    #0<data>

    In this case the data length returned will be 0. The actual length can be
    deduced from the block and the offset.

    Parameters
    ----------
    block : Union[bytes, bytearray]
        IEEE formatted block of data.
    length_before_block : Optional[int], optional
        Number of bytes before the actual start of the block. Default to None,
        which means that number will be inferred.
    raise_on_late_block : bool, optional
        Raise an error in the beginning of the block is not found before
        DEFAULT_LENGTH_BEFORE_BLOCK, if False use a warning. Default to False.

    Returns
    -------
    int
        Offset at which the actual data starts
    int
        Length of the data in bytes.

    """
    begin = block.find(b"#")
    if begin < 0:
        raise ValueError(
            "Could not find hash sign (#) indicating the start of the block. "
            "The block begin by %r" % block[:25]
        )

    length_before_block = length_before_block or DEFAULT_LENGTH_BEFORE_BLOCK
    if begin > length_before_block:
        msg = (
            "The beginning of the block has been found at %d which "
            "is an unexpectedly large value. The actual block may "
            "have been missing a beginning marker but the block "
            "contained one:\n%s"
        ) % (begin, repr(block))
        if raise_on_late_block:
            raise RuntimeError(msg)
        else:
            warnings.warn(msg, UserWarning)

    try:
        # int(block[begin+1]) != int(block[begin+1:begin+2]) in Python 3
        header_length = int(block[begin + 1 : begin + 2])
    except ValueError:
        header_length = 0
    offset = begin + 2 + header_length

    if header_length > 0:
        # #3100DATA
        # 012345
        data_length = int(block[begin + 2 : offset])
    else:
        # #0DATA
        # 012
        data_length = 0

    # R&S header for large transfer size (>1GB)
    #  "#(data_length)<data>"
    if chr(block[begin+1]) == "(":
        offset = block.find(b")") + 1
        data_length = int(block[begin + 2: offset-1])

    return offset, data_length