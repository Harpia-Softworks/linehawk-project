import enum

class GUIElementType(enum.IntEnum):
    """
    The type of the `GUIElement`
    ---

    Enumerates the types of the `GUIElement`(s) that can be, where `GUIDisplay`
    is the top one.
    """
    DISPLAY         = 0
    FRAME           = 1
    TEXT_LABEL      = 2
    TEXT_BUTTON     = 3

class GUITextHorizontalAlignment(enum.IntEnum):
    """
    Where the text should align horizontally for `GUITextElement`(s)
    ---

    Points either to the left, center or right on the alignment of the text.
    """
    LEFT            = 0
    CENTER          = 1
    RIGHT           = 2

class GUITextVerticalAlignment(enum.IntEnum):
    """
    Where the text should align vertically for `GUITextElement`(s)
    ---

    Points either to the top, center or bottom on the alignment of the text.
    """
    TOP             = 0
    CENTER          = 1
    BOTTOM          = 2