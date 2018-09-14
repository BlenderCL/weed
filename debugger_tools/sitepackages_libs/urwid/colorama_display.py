#!/usr/bin/python
#
# Urwid curses output wrapper.. the horror..
#    Copyright (C) 2004-2011  Ian Ward
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Urwid web site: http://excess.org/urwid/
"""
Colorama-based UI implementation
"""

import os
import sys

from urwid import escape
from urwid.display_common import BaseScreen, AttrSpec, UNPRINTABLE_TRANS_TABLE
#from urwid.display_unix_common import RealTerminal
from urwid.compat import bytes, PYTHON3

import msvcrt
from urwid.msvcrt_to_curses import as_curses

from colorama import Fore, Back, Style, Cursor, init, deinit
from colorama.winterm import WinTerm, win32

#class ExitMainLoop(Exception):
#    """
#    When this exception is raised within a main loop the main loop
#    will exit cleanly.
#    """
#    pass

#import urwid


Fores = {
'black'         : Fore.BLACK   + Style.DIM,   
'dark red'      : Fore.RED     + Style.DIM,         
'dark green'    : Fore.GREEN   + Style.DIM,         
'dark blue'     : Fore.BLUE    + Style.DIM,         
'dark cyan'     : Fore.CYAN    + Style.DIM,         
'dark magenta'  : Fore.MAGENTA + Style.DIM,         
'brown'         : Fore.YELLOW  + Style.DIM,         
'light gray'    : Fore.WHITE   + Style.DIM,            
'dark gray'     : Fore.BLACK   + Style.BRIGHT, 
'light red'     : Fore.RED     + Style.BRIGHT, 
'light green'   : Fore.GREEN   + Style.BRIGHT, 
'light blue'    : Fore.BLUE    + Style.BRIGHT, 
'light cyan'    : Fore.CYAN    + Style.BRIGHT, 
'light magenta' : Fore.MAGENTA + Style.BRIGHT, 
'yellow'        : Fore.YELLOW  + Style.BRIGHT, 
'white'         : Fore.WHITE   + Style.BRIGHT, 
'default'       : ''
}

Backs = {
'black'         : Back.BLACK,         
'dark red'      : Back.RED,         
'dark green'    : Back.GREEN,         
'dark blue'     : Back.BLUE,         
'dark cyan'     : Back.CYAN,         
'dark magenta'  : Back.MAGENTA,         
'brown'         : Back.YELLOW,         
'light gray'    : Back.WHITE,         
'dark gray'     : Back.LIGHTBLACK_EX,      
'light red'     : Back.LIGHTRED_EX,      
'light green'   : Back.LIGHTGREEN_EX,      
'light blue'    : Back.LIGHTBLUE_EX,      
'light cyan'    : Back.LIGHTCYAN_EX,      
'light magenta' : Back.LIGHTMAGENTA_EX,      
'yellow'        : Back.LIGHTYELLOW_EX,      
'white'         : Back.LIGHTWHITE_EX,      
'default'       : ''
}

fix_box_draw = {
'l':'\u250C',
'q':'\u2500',
'k':'\u2510',
'w':'\u252C',
'x':'\u2502',
't':'\u251C',
'j':'\u2518',
'u':'\u2524',
'm':'\u2514',
'v':'\u2534',
'n':'\u253C'
}

#aliases 65001 with utf-8
#import codecs
#codecs.register(lambda name: codecs.lookup('utf-8') if name == 'cp65001' else None)

class Screen(BaseScreen):

    def __init__(self, catch_ctrl_c = False):
        super(Screen,self).__init__()
        # Can't be sure what pair 0 will default to
        # Quiza hay que borrar casi todas estas variables self *******
        self.catch_ctrl_c = catch_ctrl_c
        self.curses_pairs = [(None, None)]
        self.palette = {}
        self.has_color = False
        self.colors = 16 # FIXME: detect this
        self.has_underline = True # FIXME: detect this
        self.s = None
        self.cursor_state = None
        self._keyqueue = []
        self.prev_input_resize = 0
        self.set_input_timeouts()
        self.last_bstate = 0
        self.register_palette_entry(None, 'default','default')
        self.cmd = None
        self.orig_cmd_mode = 0
        #self.screen_buf = None
        self._screen_buf_canvas = None

    def set_mouse_tracking(self):
        """
        Enable mouse tracking.

        After calling this function get_input will include mouse
        click events along with keystrokes.
        """
        #curses.mousemask(0  curses.BUTTON1_PRESSED | ...
        pass


    def start(self):
        """
        Initialize colorama screen wrapper.
        """
        assert self._started == False
        #init() 
        init(autoreset=True)    
        self.cmd = WinTerm()     
        self.old_cmd_mode = self.cmd.get_console_mode()
        self.cmd.set_console_mode(
                    mode = win32.ENABLE_WINDOW_INPUT |
                           win32.ENABLE_MOUSE_INPUT)
        self.cmd.buffer_size_fit(True)
        self.cmd.set_title('Console Blender')
        super(Screen, self).start()

    
    def stop(self):
        """
        Restore the screen, unwrap colorama.
        """
        if self._started == False:
            return
        cols, rows = self.get_cols_rows()
        print(Cursor.POS(1, rows-2))
        deinit()
        self.cmd.set_console_mode(self.old_cmd_mode)
        super(Screen, self).stop()


    def run_wrapper(self,fn):
        """Call fn in fullscreen mode.  Return to normal on exit.
        
        This function should be called to wrap your main program loop.
        Exception tracebacks will be displayed in normal mode.
        """
        try:
            self.start()
            return fn()
        finally:
            self.stop()


    def _setup_colour_pairs(self):
        """
        Initialize strict basic palette for 
        Windows CMD console
        """
        if not self.has_color:
            return
        pass


    def _curs_set(self,x):
        pass

    
    def _clear(self):
        #os.system('cls')
        self.cmd.erase_screen(2) # erase entire screen and set cursor (1,1)


    def set_input_timeouts(self, max_wait=None, complete_wait=0.1, 
        resize_wait=0.1):
        """
        Set the get_input timeout values.  All values have a granularity
        of 0.1s, ie. any value between 0.15 and 0.05 will be treated as
        0.1 and any value less than 0.05 will be treated as 0.  The
        maximum timeout value for this module is 25.5 seconds.
    
        max_wait -- amount of time in seconds to wait for input when
            there is no input pending, wait forever if None
        complete_wait -- amount of time in seconds to wait when
            get_input detects an incomplete escape sequence at the
            end of the available input
        resize_wait -- amount of time in seconds to wait for more input
            after receiving two screen resize requests in a row to
            stop urwid from consuming 100% cpu during a gradual
            window resize operation
        """
        self.max_tenths = 10


    def get_input(self, raw_keys=False):
        """Return pending input as a list.

        raw_keys -- return raw keycodes as well as translated versions

        This function will immediately return all the input since the
        last time it was called.  If there is no input pending it will
        wait before returning an empty list.  The wait time may be
        configured with the set_input_timeouts function.

        If raw_keys is False (default) this function will return a list
        of keys pressed.  If raw_keys is True this function will return
        a ( keys pressed, raw keycodes ) tuple instead.

        Examples of keys returned:

        * ASCII printable characters:  " ", "a", "0", "A", "-", "/"
        * ASCII control characters:  "tab", "enter"
        * Escape sequences:  "up", "page up", "home", "insert", "f1"
        * Key combinations:  "shift f1", "meta a", "ctrl b"
        * Window events:  "window resize"

        When a narrow encoding is not enabled:

        * "Extended ASCII" characters:  "\\xa1", "\\xb2", "\\xfe"

        When a wide encoding is enabled:

        * Double-byte characters:  "\\xa1\\xea", "\\xb2\\xd4"

        When utf8 encoding is enabled:

        * Unicode characters: u"\\u00a5", u'\\u253c"

        Examples of mouse events returned:

        * Mouse button press: ('mouse press', 1, 15, 13),
                            ('meta mouse press', 2, 17, 23)
        * Mouse button release: ('mouse release', 0, 18, 13),
                              ('ctrl mouse release', 0, 17, 23)
        """
        assert self._started

        try:
            keys, raw = self._get_input( self.max_tenths )
            # Avoid pegging CPU at 100% when slowly resizing, and work
            # around a bug with some braindead curses implementations that 
            # return "no key" between "window resize" commands 
            if keys==['window resize'] and self.prev_input_resize:
                while True:
                    keys, raw2 = self._get_input(self.resize_tenths)
                    raw += raw2
                    if not keys:
                        keys, raw2 = self._get_input( 
                            self.resize_tenths)
                        raw += raw2
                    if keys!=['window resize']:
                        break
                if keys[-1:]!=['window resize']:
                    keys.append('window resize')
                    
            if keys==['window resize']:
                self.prev_input_resize = 2
            elif self.prev_input_resize == 2 and not keys:
                self.prev_input_resize = 1
            else:
                self.prev_input_resize = 0
            
            if raw_keys:
                return keys, raw
            return keys

        except KeyboardInterrupt:
            if self.catch_ctrl_c:
                return ['ctrl c'], [3]
            
            else:
                cols, rows = self.get_cols_rows()
                center = int(cols/2-12)
                print(Cursor.POS(center, rows-5)
                    + Fore.WHITE + Style.BRIGHT + Back.RED
                    + '   #' + ' '*20 + '#   ' 
                    + Cursor.POS(center, rows-4)
                    + '  #  Keyboard Interrupt  #  ' 
                    + Cursor.POS(center, rows-3)
                    + '  #  Cancelled by user   #  ' 
                    + Cursor.POS(center, rows-2)
                    + '   #' + ' '*20 + '#   \n')
                return ['exit mainloop'], [777]
                #raise ExitMainLoop()
                #quit()


    def _get_input(self, wait_tenths):
        #import time 
        #time.sleep(0.05)
        if msvcrt.kbhit():
            ky = msvcrt.getch()
            if len(str(ky)) != 0:
                if ky == b'\x00' or ky == b'\xe0':
                    ky2 = msvcrt.getch()
                    key, raw = as_curses((ky, ky2))
                else:
                    key, raw = as_curses(ky)
                return ([key], [raw])
        else:
            return ([],[])
        
#     def _encode_mouse_event(self):
#         # convert to escape sequence
#         last = next = self.last_bstate
#         (id,x,y,z,bstate) = curses.getmouse()
#         
#         mod = 0
#         if bstate & curses.BUTTON_SHIFT:    mod |= 4
#         if bstate & curses.BUTTON_ALT:        mod |= 8
#         if bstate & curses.BUTTON_CTRL:        mod |= 16
#         
#         l = []
#         def append_button( b ):
#             b |= mod
#             l.extend([ 27, ord('['), ord('M'), b+32, x+33, y+33 ])
#         
#         if bstate & curses.BUTTON1_PRESSED and last & 1 == 0:
#             append_button( 0 )
#             next |= 1
#         if bstate & curses.BUTTON2_PRESSED and last & 2 == 0:
#             append_button( 1 )
#             next |= 2
#         if bstate & curses.BUTTON3_PRESSED and last & 4 == 0:
#             append_button( 2 )
#             next |= 4
#         if bstate & curses.BUTTON4_PRESSED and last & 8 == 0:
#             append_button( 64 )
#             next |= 8
#         if bstate & curses.BUTTON1_RELEASED and last & 1:
#             append_button( 0 + escape.MOUSE_RELEASE_FLAG )
#             next &= ~ 1
#         if bstate & curses.BUTTON2_RELEASED and last & 2:
#             append_button( 1 + escape.MOUSE_RELEASE_FLAG )
#             next &= ~ 2
#         if bstate & curses.BUTTON3_RELEASED and last & 4:
#             append_button( 2 + escape.MOUSE_RELEASE_FLAG )
#             next &= ~ 4
#         if bstate & curses.BUTTON4_RELEASED and last & 8:
#             append_button( 64 + escape.MOUSE_RELEASE_FLAG )
#             next &= ~ 8
#         
#         self.last_bstate = next
#         return l
            

    def _dbg_instr(self): # messy input string (intended for debugging)
        pass
        
    def _dbg_out(self,str): # messy output function (intended for debugging)
        pass
        
    def _dbg_query(self,question): # messy query (intended for debugging)
        pass
    
    def _dbg_refresh(self):
        pass


    def get_cols_rows(self):
        """Return the terminal dimensions tuple (Cols, Rows)."""
        #return os.get_terminal_size()
        #return self.cmd.get_size()
        # Hacky solution on windows to avoid flickering
        # not use last row of the terminal
        col, row =  self.cmd.get_size()
        return (col, row - 1)
        

    def _setattr(self, a):
        """return ansicodes from colorama to set attributte"""
        if a is None: 
            #return ''
            return Fore.WHITE + Style.BRIGHT + Back.BLACK    
        elif not isinstance(a, AttrSpec):
            p = self._palette.get(a, (AttrSpec('default', 'default'),))
            a = p[0]

        fg = a.foreground.split(',')[0]
        bg = a.background.split(',')[0]
        try:
            ansicodes = Fores[fg] + Backs[bg]  
        except:
            ansicodes = ''
        return ansicodes


    def draw_screen(self, xxx_todo_changeme, r ):
        """Paint screen with rendered canvas."""
        # quick return if nothing has changed
        if r is self._screen_buf_canvas:
            return
        (cols, rows) = xxx_todo_changeme
        assert self._started
        assert r.rows() == rows, "canvas size and passed size don't match"

        print(Cursor.POS() + Cursor.UP(), end='')
        output = ''
        y = -1
        for row in r.content():
            y += 1
            
            first = True
            lasta = None
            nr = 0
            for a, cs, seg in row:
                if cs != 'U':
                    seg = seg.translate(UNPRINTABLE_TRANS_TABLE)
                    assert isinstance(seg, bytes)

                if first or lasta != a:
                    output += self._setattr(a)
                    #print(self._setattr(a), end='')
                    lasta = a
                try:
                    if cs in ("0", "U"):
                        for i in range(len(seg)):
                            #print('\u2592', end='')
                            #output += chr(seg[i])#.decode('cp850')
                            output += '#'
                            #output += fix_box_draw[chr(seg[i])]#.decode('cp850')
                            #output += '\u2592'
                            #print(0x400000 + seg[i], end='')
                    else:
                        assert cs is None
                        if PYTHON3:
                            assert isinstance(seg, bytes)
                            output += seg.decode('cp850')
                            #print(seg.decode('850'), end='')
                        else:
                            output += seg
                            #print(seg, end='')
                except:
                    raise Exception
                    # it's ok to get out of the
                    # screen on the lower right
                    #if (y == rows-1 and nr == len(row)-1):
                    #    pass
                    #else:
                        # perhaps screen size changed
                        # quietly abort.
                    #    return
                nr += 1
        
        #self.cmd.set_cursor_position((1,1))
        #import sys 
        #sys.stdout.write(output)
        #self._clear()
        #print(output[:-1], end='')
        print(output, end='')
        #bug = '# win32 warning: droped terminal last row to avoid flickering'
        #bug_style = Fore.BLACK + Style.BRIGHT + Back.BLACK + bug
        #print(' '*(cols-len(bug)-1) + bug_style, end='')
        #self.cmd.set_cursor_position((rows+1, cols))
        #self.cmd.set_cursor_position((1, 1))
        try:
            x,y = r.cursor
            self.cmd.set_cursor_position((y+1, x+1))
        except:
            pass
        self._screen_buf_canvas = r


    def clear(self):
        """
        Force the screen to be completely repainted on the next
        call to draw_screen().
        """
        #os.system('cls')
        #self.cmd.erase_screen(2) # erase entire screen and set cursor (1,1)
        self._clear()
        