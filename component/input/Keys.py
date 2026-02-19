"""
Key constants for input handling.
This module provides key code constants independent of any specific game engine.
Key code constants matching Pyxel's key mapping (SDL key codes).
Components should use these constants instead of importing pyxel directly.
"""

# Letter keys (A-Z) - lowercase ASCII values
KEY_A = 97
KEY_B = 98
KEY_C = 99
KEY_D = 100
KEY_E = 101
KEY_F = 102
KEY_G = 103
KEY_H = 104
KEY_I = 105
KEY_J = 106
KEY_K = 107
KEY_L = 108
KEY_M = 109
KEY_N = 110
KEY_O = 111
KEY_P = 112
KEY_Q = 113
KEY_R = 114
KEY_S = 115
KEY_T = 116
KEY_U = 117
KEY_V = 118
KEY_W = 119
KEY_X = 120
KEY_Y = 121
KEY_Z = 122

# Number keys (0-9) - ASCII values
KEY_0 = 48
KEY_1 = 49
KEY_2 = 50
KEY_3 = 51
KEY_4 = 52
KEY_5 = 53
KEY_6 = 54
KEY_7 = 55
KEY_8 = 56
KEY_9 = 57

# Arrow keys - SDL key codes
KEY_LEFT = 1073741904
KEY_RIGHT = 1073741903
KEY_UP = 1073741906
KEY_DOWN = 1073741905

# Special keys
KEY_SPACE = 32
KEY_RETURN = 13
KEY_ENTER = 13  # Alias for RETURN
KEY_BACKSPACE = 8
KEY_DELETE = 127
KEY_TAB = 9
KEY_ESCAPE = 27

# Modifier keys - SDL key codes
KEY_SHIFT = 1342177281  # Generic shift
KEY_LSHIFT = 1073742049
KEY_RSHIFT = 1073742053
KEY_CTRL = 1342177282   # Generic ctrl
KEY_LCTRL = 1073742048
KEY_RCTRL = 1073742052
KEY_ALT = 1342177283    # Generic alt
KEY_LALT = 1073742050
KEY_RALT = 1073742054

# Punctuation and symbols - ASCII values
KEY_MINUS = 45
KEY_EQUALS = 61
KEY_LEFTBRACKET = 91
KEY_RIGHTBRACKET = 93
KEY_BACKSLASH = 92
KEY_SEMICOLON = 59
KEY_APOSTROPHE = 39
KEY_QUOTE = 39  # Alias for apostrophe
KEY_COMMA = 44
KEY_PERIOD = 46
KEY_SLASH = 47
KEY_GRAVE = 96
KEY_BACKQUOTE = 96  # Alias for grave
KEY_COLON = 58

# Mouse buttons (for consistency with Pyxel)
MOUSE_BUTTON_LEFT = 0
MOUSE_BUTTON_RIGHT = 1
MOUSE_BUTTON_MIDDLE = 2
