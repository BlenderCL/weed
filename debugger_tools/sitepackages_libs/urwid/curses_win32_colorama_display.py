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
Curses-based UI implementation
"""

import curses
import _curses

import colorama
import msvcrt
from urwid.msvcrt_to_curses import as_curses

from urwid import escape


from urwid.display_common import BaseScreen, AttrSpec, UNPRINTABLE_TRANS_TABLE
#from urwid.display_unix_common import RealTerminal
from urwid.compat import bytes, PYTHON3

KEY_RESIZE = 410 # curses.KEY_RESIZE (sometimes not defined)
KEY_MOUSE = 409 # curses.KEY_MOUSE

curses.COLOR_BLACK   = 0   #  'black':          
curses.COLOR_RED     = 7   #  'dark red':       
curses.COLOR_GREEN   = 7   #  'dark green':     
curses.COLOR_YELLOW  = 7   #  'brown':          
curses.COLOR_BLUE    = 7   #  'dark blue':      
curses.COLOR_MAGENTA = 7   #  'dark magenta':   
curses.COLOR_CYAN    = 7   #  'dark cyan':      
curses.COLOR_WHITE   = 7   #  'light gray':     
# curses.COLOR_BLACK   = 3   #  'dark gray':      
# curses.COLOR_RED     = 3   #  'light red':      
# curses.COLOR_GREEN   =    #  'light green':    
# curses.COLOR_YELLOW  =    #  'yellow':         
# curses.COLOR_BLUE    =    #  'light blue':     
# curses.COLOR_MAGENTA =    #  'light magenta':  
# curses.COLOR_CYAN    =    #  'light cyan':     
# curses.COLOR_WHITE   =    #  'white':          

_curses_colours = {
    'default':       (-1,0),#(-1,                    0),
    'black':         (0,0),#(curses.COLOR_BLACK,    0),
    'dark red':      (2,0),#(curses.COLOR_RED,      0),
    'dark green':    (2,0),#(curses.COLOR_GREEN,    0),
    'brown':         (2,0),#(curses.COLOR_YELLOW,   0),
    'dark blue':     (2,0),#(curses.COLOR_BLUE,     0),
    'dark magenta':  (2,0),#(curses.COLOR_MAGENTA,  0),
    'dark cyan':     (2,0),#(curses.COLOR_CYAN,     0),
    'light gray':    (2,0),#(curses.COLOR_WHITE,    0),
    'dark gray':     (2,0),#(curses.COLOR_BLACK,    1),
    'light red':     (2,0),#(curses.COLOR_RED,      1),
    'light green':   (2,0),#(curses.COLOR_GREEN,    1),
    'yellow':        (2,0),#(curses.COLOR_YELLOW,   1),
    'light blue':    (2,0),#(curses.COLOR_BLUE,     1),
    'light magenta': (2,0),#(curses.COLOR_MAGENTA,  1),
    'light cyan':    (2,0),#(curses.COLOR_CYAN,     1),
    'white':         (2,0),#(curses.COLOR_WHITE,    1),
}                     
                      
# _curses_colours = {
#     'default':        (-1,                    0),
#     'black':          (curses.COLOR_BLACK,    0),
#     'dark red':       (curses.COLOR_RED,      0),
#     'dark green':     (curses.COLOR_GREEN,    0),
#     'brown':          (curses.COLOR_YELLOW,   0),
#     'dark blue':      (curses.COLOR_BLUE,     0),
#     'dark magenta':   (curses.COLOR_MAGENTA,  0),
#     'dark cyan':      (curses.COLOR_CYAN,     0),
#     'light gray':     (curses.COLOR_WHITE,    0),
#     'dark gray':      (curses.COLOR_BLACK,    1),
#     'light red':      (curses.COLOR_RED,      1),
#     'light green':    (curses.COLOR_GREEN,    1),
#     'yellow':         (curses.COLOR_YELLOW,   1),
#     'light blue':     (curses.COLOR_BLUE,     1),
#     'light magenta':  (curses.COLOR_MAGENTA,  1),
#     'light cyan':     (curses.COLOR_CYAN,     1),
#     'white':          (curses.COLOR_WHITE,    1),
# }


class Screen(BaseScreen):
    def __init__(self):
        super(Screen,self).__init__()
        self.curses_pairs = [
            (None,None), # Can't be sure what pair 0 will default to
        ]
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

    def set_mouse_tracking(self):
        """
        Enable mouse tracking.

        After calling this function get_input will include mouse
        click events along with keystrokes.
        """
        curses.mousemask(0
            | curses.BUTTON1_PRESSED | curses.BUTTON1_RELEASED
            | curses.BUTTON2_PRESSED | curses.BUTTON2_RELEASED
            | curses.BUTTON3_PRESSED | curses.BUTTON3_RELEASED
            | curses.BUTTON4_PRESSED | curses.BUTTON4_RELEASED
            | curses.BUTTON_SHIFT | curses.BUTTON_ALT
            | curses.BUTTON_CTRL)

    def start(self):
        """
        Initialize the screen and input mode.
        """
        assert self._started == False

        self.s = curses.initscr()
        self.has_color = curses.has_colors()
        if self.has_color:
            curses.start_color()
            if curses.COLORS < 8:
                # not colourful enough
                self.has_color = False
        if self.has_color:
            try:
                curses.use_default_colors()
                self.has_default_colors=True
            except _curses.error:
                self.has_default_colors=False
        self._setup_colour_pairs()
        curses.noecho()
        curses.meta(True)
        self.s.nodelay(True)
        #curses.halfdelay(1) # use set_input_timeouts to adjust
        self.s.keypad(True) #changed to True to get special keys
        
        #if not self._signal_keys_set:
            #self._old_signal_keys = self.tty_signal_keys()
            #pass

        super(Screen, self).start()

    
    def stop(self):
        """
        Restore the screen.
        """
        if self._started == False:
            return
        curses.echo()
        self._curs_set(1)
        try:
            curses.endwin()
        except _curses.error:
            pass # don't block original error with curses error
        
        #if self._old_signal_keys:
        #    self.tty_signal_keys(*self._old_signal_keys)

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

#     def _setup_colour_pairs(self):
#         """
#         Initialize all 63 color pairs based on the term:
#         bg * 8 + 7 - fg
#         So to get a color, we just need to use that term and get the right color
#         pair number.
#         """
#         if not self.has_color:
#             return
# 
#         for fg in range(8):
#             for bg in range(8):
#                 # leave out white on black
#                 if fg == curses.COLOR_WHITE and \
#                    bg == curses.COLOR_BLACK:
#                     continue
# 
#                 curses.init_pair(bg * 8 + 7 - fg, fg + 4, bg)


    def _setup_colour_pairs(self):
        """
        Initialize strict basic palette for 
        Windows CMD console
        """
        if not self.has_color:
            return

#         curses.init_pair(7, 0, 0) # 0 negro
#         curses.init_pair(6, 4, 0) # 4 rojo
#         curses.init_pair(5, 2, 0) # 2 verde
#         curses.init_pair(4, 6, 0) # 6 amarillo
#         curses.init_pair(3, 1, 0) # 1 azul
#         curses.init_pair(2, 5, 0) # 5 magenta
#         curses.init_pair(1, 3, 0) # 3 cyan
#         curses.init_pair(9, 8, 0) # 7 light gray 8 dark gray
#         curses.init_pair(8, 8, 0) # 8 ... blanco ?

        curses.init_pair(15, 0, 4)
        curses.init_pair(14, 4, 4)
        curses.init_pair(13, 2, 4)
        curses.init_pair(12, 6, 4)
        curses.init_pair(11, 1, 4)
        curses.init_pair(10, 5, 4)
        curses.init_pair(9, 3, 4)
        curses.init_pair(8, 7, 4)
        curses.init_pair(7, 0, 0)
        curses.init_pair(6, 4, 0)
        curses.init_pair(5, 2, 0)
        curses.init_pair(4, 6, 0)
        curses.init_pair(3, 1, 0)
        curses.init_pair(2, 5, 0)
        curses.init_pair(1, 3, 0)
        #curses.init_pair(0, 7, 0) white  7 , black  0
        
        ###################################
        
        curses.init_pair(63, 0, 7)
        curses.init_pair(62, 1, 7)
        curses.init_pair(61, 2, 7)
        curses.init_pair(60, 3, 7)
        curses.init_pair(59, 4, 7)
        curses.init_pair(58, 5, 7)
        curses.init_pair(57, 6, 7)
        curses.init_pair(56, 7, 7)
        curses.init_pair(55, 0, 3)
        curses.init_pair(54, 1, 3)
        curses.init_pair(53, 2, 3)
        curses.init_pair(52, 3, 3)
        curses.init_pair(51, 4, 3)
        curses.init_pair(50, 5, 3)
        curses.init_pair(49, 6, 3)
        curses.init_pair(48, 7, 3)
        curses.init_pair(47, 0, 5)
        curses.init_pair(46, 1, 5)
        curses.init_pair(45, 2, 5)
        curses.init_pair(44, 3, 5)
        curses.init_pair(43, 4, 5)
        curses.init_pair(42, 5, 5)
        curses.init_pair(41, 6, 5)
        curses.init_pair(40, 7, 5)
        curses.init_pair(39, 0, 1)
        curses.init_pair(38, 1, 1)
        curses.init_pair(37, 2, 1)
        curses.init_pair(36, 3, 1)
        curses.init_pair(35, 4, 1)
        curses.init_pair(34, 5, 1)
        curses.init_pair(33, 6, 1)
        curses.init_pair(32, 7, 1)
        curses.init_pair(31, 0, 6)
        curses.init_pair(30, 1, 6)
        curses.init_pair(29, 2, 6)
        curses.init_pair(28, 3, 6)
        curses.init_pair(27, 4, 6)
        curses.init_pair(26, 5, 6)
        curses.init_pair(25, 6, 6)
        curses.init_pair(24, 7, 6)
        curses.init_pair(23, 0, 2)
        curses.init_pair(22, 1, 2)
        curses.init_pair(21, 2, 2)
        curses.init_pair(20, 3, 2)
        curses.init_pair(19, 4, 2)
        curses.init_pair(18, 5, 2)
        curses.init_pair(17, 6, 2)
        curses.init_pair(16, 7, 2)



    def _curs_set(self,x):
        if self.cursor_state== "fixed" or x == self.cursor_state: 
            return
        try:
            curses.curs_set(x)
            self.cursor_state = x
        except _curses.error:
            self.cursor_state = "fixed"

    
    def _clear(self):
        self.s.clear()
        self.s.refresh()
    
    
    def _getch(self, wait_tenths):
        if wait_tenths==0:
            return self._getch_nodelay()
        if wait_tenths is None:
            curses.cbreak()
        else:
            curses.halfdelay(wait_tenths)
        self.s.nodelay(0)
        return self.s.getch()
    
    def _getch_nodelay(self):
        self.s.nodelay(1)
        while 1:
            # this call fails sometimes, but seems to work when I try again
            try:
                curses.cbreak()
                break
            except _curses.error:
                pass
            
        return self.s.getch()

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

        def convert_to_tenths( s ):
            if s is None:
                return None
            return int( (s+0.05)*10 )

        self.max_tenths = convert_to_tenths(max_wait)
        self.complete_tenths = convert_to_tenths(complete_wait)
        self.resize_tenths = convert_to_tenths(resize_wait)

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
        
        
    def _get_input(self, wait_tenths):
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
                
                
    def _encode_mouse_event(self):
        # convert to escape sequence
        last = next = self.last_bstate
        (id,x,y,z,bstate) = curses.getmouse()
        
        mod = 0
        if bstate & curses.BUTTON_SHIFT:    mod |= 4
        if bstate & curses.BUTTON_ALT:        mod |= 8
        if bstate & curses.BUTTON_CTRL:        mod |= 16
        
        l = []
        def append_button( b ):
            b |= mod
            l.extend([ 27, ord('['), ord('M'), b+32, x+33, y+33 ])
        
        if bstate & curses.BUTTON1_PRESSED and last & 1 == 0:
            append_button( 0 )
            next |= 1
        if bstate & curses.BUTTON2_PRESSED and last & 2 == 0:
            append_button( 1 )
            next |= 2
        if bstate & curses.BUTTON3_PRESSED and last & 4 == 0:
            append_button( 2 )
            next |= 4
        if bstate & curses.BUTTON4_PRESSED and last & 8 == 0:
            append_button( 64 )
            next |= 8
        if bstate & curses.BUTTON1_RELEASED and last & 1:
            append_button( 0 + escape.MOUSE_RELEASE_FLAG )
            next &= ~ 1
        if bstate & curses.BUTTON2_RELEASED and last & 2:
            append_button( 1 + escape.MOUSE_RELEASE_FLAG )
            next &= ~ 2
        if bstate & curses.BUTTON3_RELEASED and last & 4:
            append_button( 2 + escape.MOUSE_RELEASE_FLAG )
            next &= ~ 4
        if bstate & curses.BUTTON4_RELEASED and last & 8:
            append_button( 64 + escape.MOUSE_RELEASE_FLAG )
            next &= ~ 8
        
        self.last_bstate = next
        return l
            

    def _dbg_instr(self): # messy input string (intended for debugging)
        curses.echo()
        self.s.nodelay(0)
        curses.halfdelay(100)
        str = self.s.getstr()
        curses.noecho()
        return str
        
    def _dbg_out(self,str): # messy output function (intended for debugging)
        self.s.clrtoeol()
        self.s.addstr(str)
        self.s.refresh()
        self._curs_set(1)
        
    def _dbg_query(self,question): # messy query (intended for debugging)
        self._dbg_out(question)
        return self._dbg_instr()
    
    def _dbg_refresh(self):
        self.s.refresh()



    def get_cols_rows(self):
        """Return the terminal dimensions (num columns, num rows)."""
        rows,cols = self.s.getmaxyx()
        return cols,rows
        

    def _setattr(self, a):
        if a is None:
            self.s.attrset(0)
            return
        elif not isinstance(a, AttrSpec):
            p = self._palette.get(a, (AttrSpec('default', 'default'),))
            a = p[0]

        if self.has_color:
            if a.foreground_basic:
                if a.foreground_number >= 8:
                    fg = a.foreground_number - 8
                else:
                    fg = a.foreground_number
            else:
                fg = 7

            if a.background_basic:
                bg = a.background_number
            else:
                bg = 0

            attr = curses.color_pair(bg * 8 + 7 - fg)
        else:
            attr = 0

        if a.bold:
            attr |= curses.A_BOLD
        if a.standout:
            attr |= curses.A_STANDOUT
        if a.underline:
            attr |= curses.A_UNDERLINE
        if a.blink:
            attr |= curses.A_BLINK

        self.s.attrset(attr)

    def draw_screen(self, xxx_todo_changeme, r ):
        """Paint screen with rendered canvas."""
        (cols, rows) = xxx_todo_changeme
        assert self._started
        
        assert r.rows() == rows, "canvas size and passed size don't match"
    
        y = -1
        for row in r.content():
            y += 1
            try:
                self.s.move( y, 0 )
            except _curses.error:
                # terminal shrunk? 
                # move failed so stop rendering.
                return
            
            first = True
            lasta = None
            nr = 0
            for a, cs, seg in row:
                if cs != 'U':
                    seg = seg.translate(UNPRINTABLE_TRANS_TABLE)
                    assert isinstance(seg, bytes)

                if first or lasta != a:
                    self._setattr(a)
                    lasta = a
                try:
                    if cs in ("0", "U"):
                        for i in range(len(seg)):
                            self.s.addch( 0x400000 +
                                seg[i] )
                                #print(seg[i])
                    else:
                        assert cs is None
                        if PYTHON3:
                            assert isinstance(seg, bytes)
                            self.s.addstr(seg.decode('utf-8','ignore'))
                        else:
                            self.s.addstr(seg)
                except _curses.error:
                    # it's ok to get out of the
                    # screen on the lower right
                    if (y == rows-1 and nr == len(row)-1):
                        pass
                    else:
                        # perhaps screen size changed
                        # quietly abort.
                        return
                nr += 1
        if r.cursor is not None:
            x,y = r.cursor
            self._curs_set(1)
            try:
                self.s.move(y,x)
            except _curses.error:
                pass
        else:
            self._curs_set(0)
            self.s.move(0,0)
        
        self.s.refresh()
        self.keep_cache_alive_link = r


    def clear(self):
        """
        Force the screen to be completely repainted on the next
        call to draw_screen().
        """
        self.s.clear()




class _test:
    def __init__(self):
        self.ui = Screen()
        self.l = list(_curses_colours.keys())
        self.l.sort()
        for c in self.l:
            self.ui.register_palette( [
                (c+" on black", c, 'black', 'underline'),
                (c+" on dark blue",c, 'dark blue', 'bold'),
                (c+" on light gray",c,'light gray', 'standout'),
                ])
        self.ui.run_wrapper(self.run)
        
    def run(self):
        class FakeRender: pass
        r = FakeRender()
        text = ["  has_color = "+repr(self.ui.has_color),""]
        attr = [[],[]]
        r.coords = {}
        r.cursor = None
        
        for c in self.l:
            t = ""
            a = []
            for p in c+" on black",c+" on dark blue",c+" on light gray":
                
                a.append((p,27))
                t=t+ (p+27*" ")[:27]
            text.append( t )
            attr.append( a )

        text += ["","return values from get_input(): (q exits)", ""]
        attr += [[],[],[]]
        cols,rows = self.ui.get_cols_rows()
        keys = None
        while keys!=['q']:
            r.text=([t.ljust(cols) for t in text]+[""]*rows)[:rows]
            r.attr=(attr+[[]]*rows) [:rows]
            self.ui.draw_screen((cols,rows),r)
            keys, raw = self.ui.get_input( raw_keys = True )
            if 'window resize' in keys:
                cols, rows = self.ui.get_cols_rows()
            if not keys:
                continue
            t = ""
            a = []
            for k in keys:
                if type(k) == str: k = k.encode("utf-8")
                t += "'"+k + "' "
                a += [(None,1), ('yellow on dark blue',len(k)),
                    (None,2)]
            
            text.append(t + ": "+ repr(raw))
            attr.append(a)
            text = text[-rows:]
            attr = attr[-rows:]
                
                


if '__main__'==__name__:
    _test()
