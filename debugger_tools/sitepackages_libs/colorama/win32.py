# Copyright Jonathan Hartley 2013. BSD 3-Clause license, see LICENSE file.

try:
    import ctypes
    from ctypes import LibraryLoader
    windll = LibraryLoader(ctypes.WinDLL)
    from ctypes import wintypes
except (AttributeError, ImportError):
    windll = None
    SetConsoleTextAttribute = lambda *_: None
    winapi_test = lambda *_: None
else:
    #from ctypes import byref, Structure, c_char, POINTER
    from .win32_util import *


    # ctypes wrapper to GetStdHandle 
    #                   ============
    _GetStdHandle = windll.kernel32.GetStdHandle
    _GetStdHandle.restype  = wintypes.HANDLE
    _GetStdHandle.argtypes = [wintypes.DWORD]

    handles = {
        STDIN : _GetStdHandle(STDIN),
        STDOUT: _GetStdHandle(STDOUT),
        STDERR: _GetStdHandle(STDERR),
    }


    # ctypes wrapper to GetConsoleScreenBufferInfo 
    #                   ========================== 
    _GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo
    _GetConsoleScreenBufferInfo.restype  = wintypes.BOOL
    _GetConsoleScreenBufferInfo.argtypes = [
        wintypes.HANDLE,
        POINTER(CONSOLE_SCREEN_BUFFER_INFO),
    ]

    def GetConsoleScreenBufferInfo(stream_id=STDOUT):
        handle = handles[stream_id]
        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        success = _GetConsoleScreenBufferInfo(
            handle, byref(csbi))
        return csbi


    # ctypes wrapper to SetConsoleTextAttribute 
    #                   ======================= 
    _SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute
    _SetConsoleTextAttribute.restype  = wintypes.BOOL
    _SetConsoleTextAttribute.argtypes = [
        wintypes.HANDLE,
        wintypes.WORD,
    ]

    def SetConsoleTextAttribute(stream_id, attrs):
        handle = handles[stream_id]
        return _SetConsoleTextAttribute(handle, attrs)


    # ctypes wrapper to SetConsoleCursorPosition 
    #                   ======================== 
    _SetConsoleCursorPosition = windll.kernel32.SetConsoleCursorPosition
    _SetConsoleCursorPosition.restype  = wintypes.BOOL
    _SetConsoleCursorPosition.argtypes = [
        wintypes.HANDLE,
        COORD,
    ]

    def SetConsoleCursorPosition(stream_id, position, adjust=True):
        position = COORD(*position)
        # If the position is out of range, do nothing.
        if position.Y <= 0 or position.X <= 0:
            return
        # Adjust for Windows' SetConsoleCursorPosition:
        #    1. being 0-based, while ANSI is 1-based.
        #    2. expecting (x,y), while ANSI uses (y,x).
        adjusted_position = COORD(position.Y - 1, position.X - 1)
        if adjust:
            # Adjust for viewport's scroll position
            sr = GetConsoleScreenBufferInfo(STDOUT).srWindow
            adjusted_position.Y += sr.Top
            adjusted_position.X += sr.Left
        # Resume normal processing
        handle = handles[stream_id]
        return _SetConsoleCursorPosition(handle, adjusted_position)


    # ctypes wrapper to FillConsoleOutputCharacterA 
    #                   =========================== 
    _FillConsoleOutputCharacterA = windll.kernel32.FillConsoleOutputCharacterA
    _FillConsoleOutputCharacterA.restype  = wintypes.BOOL
    _FillConsoleOutputCharacterA.argtypes = [
        wintypes.HANDLE,
        c_char,
        wintypes.DWORD,
        COORD,
        POINTER(wintypes.DWORD),
    ]

    def FillConsoleOutputCharacter(stream_id, char, length, start):
        handle = handles[stream_id]
        char = c_char(char.encode())
        length = wintypes.DWORD(length)
        num_written = wintypes.DWORD(0)
        # Note that this is hard-coded for ANSI (vs wide) bytes.
        success = _FillConsoleOutputCharacterA(
            handle, char, length, start, byref(num_written))
        return num_written.value


    # ctypes wrapper to FillConsoleOutputAttribute 
    #                   ========================== 
    _FillConsoleOutputAttribute = windll.kernel32.FillConsoleOutputAttribute
    _FillConsoleOutputAttribute.restype  = wintypes.BOOL
    _FillConsoleOutputAttribute.argtypes = [
        wintypes.HANDLE,
        wintypes.WORD,
        wintypes.DWORD,
        COORD,
        POINTER(wintypes.DWORD),
    ]
 
    def FillConsoleOutputAttribute(stream_id, attr, length, start):
        ''' FillConsoleOutputAttribute( hConsole, csbi.wAttributes, dwConSize, coordScreen, &cCharsWritten )'''
        handle = handles[stream_id]
        attribute = wintypes.WORD(attr)
        length = wintypes.DWORD(length)
        num_written = wintypes.DWORD(0)
        # Note that this is hard-coded for ANSI (vs wide) bytes.
        return _FillConsoleOutputAttribute(
            handle, attribute, length, start, byref(num_written))


    # ctypes wrapper to SetConsoleTitleA 
    #                   ================
    _SetConsoleTitleW = windll.kernel32.SetConsoleTitleA
    _SetConsoleTitleW.restype  = wintypes.BOOL
    _SetConsoleTitleW.argtypes = [
        wintypes.LPCSTR
    ]

    def SetConsoleTitle(title):
        return _SetConsoleTitleW(title)

    ########################
    # Nuevos Super Poderes #
    ########################

    # ctypes wrapper to GetConsoleMode 
    #                   ==============
    _GetConsoleMode = windll.kernel32.GetConsoleMode
    _GetConsoleMode.restype  = wintypes.BOOL
    _GetConsoleMode.argtypes = [
        wintypes.HANDLE,
        POINTER(wintypes.DWORD)
    ]

    def GetConsoleMode(stream_id=STDIN):
        handle = handles[stream_id]
        mode = wintypes.DWORD()
        success = _GetConsoleMode(handle, byref(mode))
        return mode


    # ctypes wrapper to SetConsoleMode 
    #                   ==============
    _SetConsoleMode = windll.kernel32.SetConsoleMode
    _SetConsoleMode.restype  = wintypes.BOOL
    _SetConsoleMode.argtypes = [
        wintypes.HANDLE,
        wintypes.DWORD,
    ]

    def SetConsoleMode(stream_id=STDIN, mode=135):
        handle = handles[stream_id]
        return _SetConsoleMode(handle, mode)


    # ctypes wrapper to ReadConsoleInputA 
    #                   =================
    _ReadConsoleInput = windll.kernel32.ReadConsoleInputW
    _ReadConsoleInput.restype  = wintypes.BOOL
    _ReadConsoleInput.argtypes = [
        wintypes.HANDLE,
        POINTER(INPUT_RECORD),
        wintypes.DWORD,
        POINTER(wintypes.DWORD)
    ]

    def ReadConsoleInput(stream_id=STDIN, bfsize=10):
        handle = handles[stream_id]
        input_array = (INPUT_RECORD * bfsize)()
        buffer_size = wintypes.DWORD(bfsize)
        records_length = wintypes.DWORD()
        success = _ReadConsoleInput(
            handle,
            input_array,
            buffer_size,
            byref(records_length),
        )
        return input_array[0:records_length.value]


    # ctypes wrapper to SetConsoleScreenBufferSize 
    #                   ==========================
    _SetConsoleScreenBufferSize = windll.kernel32.SetConsoleScreenBufferSize
    _SetConsoleScreenBufferSize.restype  = wintypes.BOOL
    _SetConsoleScreenBufferSize.argtypes = [
        wintypes.HANDLE,
        COORD,
    ]

    def SetConsoleScreenBufferSize(width=80, height=24, stream_id=STDOUT):
        handle = handles[stream_id]
        size = COORD(width, height)
        return _SetConsoleScreenBufferSize(handle, size)
