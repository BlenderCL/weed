__doc__ = '''
╔══════════════════════════════╦═══════════════════════════════════════════════╗
║ ░▒▓█ BGE Console REBORN █▓▒░ ║   Upgraded and improved for:    Blender 2.7x  ║
╠═════════════════════════════╦╝─────────────────────────────────── Python 3.x ║
║                             ║      [up]/[down] : History                     ║
║  sce = current scene        ║    [CTRL][space] : special chars.              ║
║ cont = current controller   ║            [TAB] : Indent/Autocomplete         ║
╚═════════════════════════════╩════════════════════════════════════════════════╝
                 based on: Ideasman42 BGE Console for blender 2.49, python 2.x  
'''

from bge import logic, render, events
from datetime import datetime
import bpy
import sys
import bgl
import blf

SCROLLBACK = 28
BUFFER = 150
WRAP = 80
# Both prompts must be the same length
PROMPT = '>>> '
PROMPT_MULTI = '  | '

MESSGS_COLOR = (1.0, 1.0, 0.0)      # Amarillo
PROMPT_COLOR = (1.0, 1.0, 1.0)      # Blanco
OUTPUT_COLOR = (0.0, 1.0, 0.0)      # Verde
ERRORS_COLOR = (1.0, 0.0, 0.0)      # Rojo

bge_log = None

try:
    from colorama import init, AnsiToWin32, Fore, Back, Style
    init(wrap=False)
    stream = AnsiToWin32(sys.stdout).stream
except ImportError:
    from io import StringIO
    stream = StringIO()

# Python 3
# print(Fore.BLUE + 'blue text on stderr', file=stream)

def register_draw(cont):
    '''register draw functions on scene.postdraw'''
    # FONTS: lucida-console monaco SourceCodePro-Light ProFontWindows .ttf
    #logic.font_path = logic.expandPath('//lucida-console.ttf')
    scene = logic.getCurrentScene()
    #breakpoint.here
    scene.post_draw = [draw_console_gl]
    # row attr for console
    logic.rows = [ { 'id' : 1,#blf.load(logic.font_path),
                    'pos' : (10, 10 + x*14, 1),
                   'size' : (15, 72),
                  'alpha' : 0.22 + x*x/1000.0,
                  'color' : (1, 1, 1),
                   'text' : '' }
                        for x in range(29) ]
    # welcome message                                
    logic.rows[0]['text'] = 'Press any key to start BGE Console'
    print()


def draw_console_gl():
    '''draw console with blf, line by line'''
    for r in logic.rows:
        blf.color(r['id'], r['color'][0], r['color'][1], 
                      r['color'][2] ,1 - r['alpha'])
        blf.position(r['id'], *r['pos'])
        blf.size(r['id'], *r['size'])
        blf.draw(r['id'], r['text'])


def extended_namespace(cont):
    '''namespace plus logic, sce, cont, own'''
    namespace = locals()
    namespace.update({ 'logic':logic,
                       'sce':logic.getCurrentScene(),
                       'cont':cont,
                       'own':cont.owner })
    return namespace

def is_delimiter(ch):
    '''For skipping words'''
    if ch.isalnum() or ch == '_':
        return False
    return True
    
def is_delimiter_autocomp(ch):
    '''For autocomp words'''
    if ch.isalnum() or ch in '._':
        return False
    return True


class fileRedirect:
    def __init__(self, errors):
        self.error = errors
        self.used = False
        self.message = ''
    def write(self, data):
        self.message += data
    def read(self):
        return self.message
    def close(self):
        self.message = ''       # quiza mejor 'pass'


class BgeConsole:
    def __init__(self, cont):
        self.namespace = extended_namespace(cont)
        self.console = __import__('code').InteractiveConsole(self.namespace)
        self.cur = 0
        self.edit_text = ''
        self.scrollback = []
        self.history = ['']
        self.is_multiline = False
        self.key_repeat = events.MIDDLEMOUSE
        # PREFERENCE HERE... Fix non american keyboard
        # let the preference property have the maketrans strings...
        self.my_keyboard = str.maketrans('@^&*()"<>', '"&/()=?;:')
        self.popup_lines = 0
        self.doing_autocomplete = False
        self.special_char_request = False
        self.special_char_map = {
            events.ONEKEY   : '()',   events.SIXKEY   : '@&',
            events.TWOKEY   : '[]',   events.SEVENKEY : ';:',
            events.THREEKEY : '{}',   events.EIGHTKEY : '+*',
            events.FOURKEY  : '<>',   events.NINEKEY  : '-/',
            events.FIVEKEY  : '\\\''
            }
            

    def PrevChar(self): 
        if self.cur > 0:
            return self.edit_text[self.cur - 1]
        else:
            return None
    
    def NextChar(self):
        if len(self.edit_text) > self.cur:
            return self.edit_text[self.cur]
        else:
            return None

    def curInsertChar(self, ch):
        edt = self.edit_text
        self.edit_text = edt[:self.cur] + ch + edt[self.cur:]
        if self.cur > len(edt):
            self.cur = len(edt)
        self.curRight()
        #if self.doing_autocomplete:
        #    self.autocomp()

    def FillScrollback(self):
        #self.scrollback = self.scrollback[:-self.popup_lines]
        sb = self.scrollback
        #self.popup_lines = 0
        while len(sb) < SCROLLBACK:
            #sb.append(('', PROMPT_COLOR))
            sb.insert(0, ('', PROMPT_COLOR))
        while len(sb) > BUFFER:
            sb.pop(0)

    def AddScrollback(self, data, row_color=PROMPT_COLOR):
        sb = self.scrollback
        data = data.splitlines() #if type(data)==str else data
        for line in data:
            while len(line) > WRAP:
                sb.append((line[:WRAP], row_color))
                line = line[WRAP:]
            sb.append((line, row_color))
        self.FillScrollback()

    def removePopup(self):
        if self.popup_lines:
            self.scrollback = self.scrollback[:-self.popup_lines]
            self.popup_lines = 0


    def curLeft(self, hold=[]):
        if 'ctrl' in hold:
            self.cur = 0
        elif self.cur > 0:
            self.cur -= 1

    def curRight(self, hold=[]):
        if 'ctrl' in hold:
            self.cur = len(self.edit_text)
        elif self.cur < len(self.edit_text):
            self.cur += 1

    def curBackspace(self, hold=[]):
        edt = self.edit_text
        if 'ctrl' in hold:
            cur_prev = self.cur
            self.curLeftJump()
            if cur_prev != self.cur:
                self.edit_text = edt[:self.cur] + edt[cur_prev:]

        elif self.cur > 0:
            self.edit_text = edt[:self.cur-1] + edt[self.cur:]
            self.curLeft()

        if self.doing_autocomplete:
            self.autocomp()
    
    def curDelete(self, hold=[]):
        edt = self.edit_text
        cur = self.cur
        if 'ctrl' in hold:
            self.curRightJump()
            if cur != self.cur:
                self.edit_text = edt[:cur] + edt[self.cur:]
                self.cur = cur

        elif cur < len(edt):
            self.edit_text = edt[:cur] + edt[cur+1:]

    def curHome(self, hold=[]):
        self.cur = 0

    def curEnd(self, hold=[]):
        self.cur = len(self.edit_text)

    def historyUp(self, hold=[]):
        hs = self.history
        '''
        if bcon['edit_text'] in hs:
            hs.remove(bcon['edit_text'])
            if not hs: hs[:] = ['']
        '''
        hs[0] = self.edit_text
        
        hs.append(hs.pop(0))
        
        self.edit_text = hs[0]
        self.curEnd()
        #print(hs)
        
        

    def historyDown(self, hold=[]):
        hs = self.history
        '''
        if bcon['edit_text'] in hs:
            hs.remove(bcon['edit_text'])
            if not hs: hs[:] = ['']
        '''
        hs[0] = self.edit_text
        
        hs.insert(0, hs.pop())
        
        self.edit_text = hs[0]
        
        
        self.curEnd()
        #print(hs)

    def execute(self, hold=[]):
        global bge_log
        self.doing_autocomplete = False
        if self.popup_lines:
            self.removePopup()
        cmdline = self.GetTextCommandline()
        self.AddScrollback(*cmdline) #row_color='PROMPT'
        
        if len(cmdline[0]) > 4 and cmdline[0][:5] == '>>> #':
            print(Fore.YELLOW + cmdline[0][4:], file=stream)
            print(Fore.WHITE, end='', file=stream)
        else:
            print(Fore.WHITE + cmdline[0][4:], file=stream)
        bge_log.write(cmdline[0][4:] + '\n')
        stdout_redir = fileRedirect(False)
        stderr_redir = fileRedirect(True)
        
        sys.stdout = stdout_redir
        sys.stderr = stderr_redir
        
        pytext = self.edit_text if self.edit_text else '\n'
        
        self.is_multiline = self.console.push(pytext)
        
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        sys.last_traceback = None
        
        if stdout_redir.read(): 
            self.AddScrollback(stdout_redir.read(), row_color=OUTPUT_COLOR)
            print(Fore.GREEN + '"""\n' + stdout_redir.read() + '"""', file=stream)
            print(Fore.WHITE + ' ', file=stream)
            bge_log.write('"""\n' + stdout_redir.read() + '"""\n\n')
            stdout_redir.close()
        if stderr_redir.read():
            self.AddScrollback(stderr_redir.read(), row_color=ERRORS_COLOR)
            print(Fore.RED + '# ERROR !\n# ', end='', file=stream)
            print(stderr_redir.read().rstrip().replace('\n','\n# '), file=stream)
            print(Fore.WHITE + ' ', file=stream)
            bge_log.write('# ERROR !\n# ')
            bge_log.write(stderr_redir.read().rstrip().replace('\n','\n# ') + '\n')
            
            stderr_redir.close()

        # Avoid double ups, add the new one at the front
        if pytext != '\n':
            if self.edit_text in self.history:
                self.history.remove(self.edit_text)
            
            self.history.insert(0, self.edit_text)
            
            while '' in self.history:
                self.history.remove('')
            #if '' in self.history:
            #    self.history[:] = [v for v in self.history if v]
            
            self.history.insert(0, '')
            self.edit_text = ''
        if self.is_multiline:
            self.edit_text = '    ' + self.edit_text
        self.curEnd()

    #####################
    ## magicKey

    def magicKey(self, hold=[]):
        if self.doing_autocomplete:
            self.removePopup()
            self.doing_autocomplete = False
        elif (self.is_multiline and
            self.edit_text[:self.cur].lstrip() == ''):
            # multiline with chars left to the cursor
            # are spaces. Do indents            
            if 'shft' in hold:
                self.edit_text = self.edit_text[:4].lstrip() + self.edit_text[4:]
                self.cur = self.cur - 4 if self.cur > 3 else 0
            else:
                self.edit_text = '    ' + self.edit_text
                self.cur = self.cur + 4
        
        else:
            # No indents in prompt
            self.autocomp()


    def autocomp(self, hold=[]):

        def word_wrap(string, width=78):
            #string = '║ ' + string
            newstring = ''
            self.popup_lines += 1
            while len(string) > width:
                # find position of nearest whitespace char to the left of "width"
                marker = width - 2
                while not string[marker].isspace():
                    marker = marker - 1

                # remove line from original string and add it to the new string
                newline = string[0:marker] + ' '*(width-marker-1) + '║\n║ '
                newstring = newstring + newline
                self.popup_lines += 1
                string = string[marker + 1:]

            return newstring + string + ' '*(width-len(string)-1) + '║'            
                    
        def do_autocomp(autocomp_prefix, autocomp_members):
            '''return text to insert and a list of options'''
            autocomp_members = [
                v for v in autocomp_members
                if v.startswith(autocomp_prefix) ]
            
            if not autocomp_prefix:
                return '', autocomp_members
            elif len(autocomp_members) > 1:
                # find a common string between all members after the prefix 
                # 'ge' [getA, getB, getC] --> 'get'
                
                # get the shortest member
                min_len = min([len(v) for v in autocomp_members])
                
                autocomp_prefix_ret = ''
                
                for i in range(len(autocomp_prefix), min_len):
                    char_soup = set()
                    for v in autocomp_members:
                        char_soup.add(v[i])
                    
                    if len(char_soup) > 1:
                        break
                    else:
                        autocomp_prefix_ret += char_soup.pop()
                    
                #print(autocomp_prefix_ret)
                return autocomp_prefix_ret, autocomp_members
            elif len(autocomp_members) == 1:
                return autocomp_members[0][len(autocomp_prefix):], []
            else:
                return '', []
        
        #######################
        ## autocomp
        self.doing_autocomplete = True
        self.special_char_request = False
        if self.popup_lines:
            self.removePopup()
        
        TEMP_NAME = '___tempname___'
        
        cur_orig = self.cur
        
        ch = self.PrevChar()
        while ch is not None and not is_delimiter(ch):
            ch = self.PrevChar()
            self.curLeft()
        
        if ch != None:
            self.curRight()
        
        #print(cur_orig, self.cur)
        
        cur_base = self.cur
        
        autocomp_prefix = self.edit_text[cur_base:cur_orig]
        #print(autocomp_prefix)
        
        if self.PrevChar()=='.':
        # Get the previous word
            self.curLeft()
            ch = self.PrevChar()
            while ch is not None and not is_delimiter_autocomp(ch):
                ch = self.PrevChar()
                self.curLeft()
            
            cur_new = self.cur
            
            if ch != None:
                cur_new += 1
            
            pytxt = self.edit_text[cur_new:cur_base-1]
            #print("WOW '%s'" % pytxt)
            #try:
            if pytxt:
                self.console.runsource(TEMP_NAME + '=' + pytxt, '<input>', 'single')
                # print(val)
            else: ##except:
                val = None
            
            try:
                val = self.namespace[TEMP_NAME]
                del self.namespace[TEMP_NAME]
            except:
                val = None
            
            if val:
                autocomp_members = dir(val)
                
                autocomp_prefix_ret, autocomp_members = do_autocomp(autocomp_prefix, autocomp_members)
                
                self.cur = cur_orig
                #self.doing_autocomplete = False
                for v in autocomp_prefix_ret:
                    self.curInsertChar(v)
                cur_orig = self.cur
                #self.doing_autocomplete = True
                
                if autocomp_members:
                    _box = word_wrap('  '.join(autocomp_members))
                    self.AddScrollback('╔'+'═'*78 +'╗'+ '\n║ ' + _box, MESSGS_COLOR) #row_color=PROMPT_COLOR
                    self.AddScrollback('╚'+'═'*78 +'╝', MESSGS_COLOR) #row_color=PROMPT_COLOR
                    self.popup_lines +=2
                else:
                    self.doing_autocomplete = False
            del val
            
        else:
            # Autocomp global namespace
            autocomp_members = self.namespace.keys()
            
            if autocomp_prefix:
                autocomp_members = [v for v in autocomp_members if v.startswith(autocomp_prefix)]
            
            autocomp_prefix_ret, autocomp_members = do_autocomp(autocomp_prefix, autocomp_members)
            
            self.cur = cur_orig
            for v in autocomp_prefix_ret:
                self.curInsertChar(v)
            cur_orig = self.cur
            
            if autocomp_members:
                _box = word_wrap('  '.join(autocomp_members))
                self.AddScrollback('╔'+'═'*78 +'╗'+ '\n║ ' + _box, MESSGS_COLOR) #row_color=PROMPT_COLOR
                self.AddScrollback('╚'+'═'*78 +'╝', MESSGS_COLOR) #row_color=PROMPT_COLOR
                self.popup_lines +=2
            else:
                self.doing_autocomplete = False
        self.cur = cur_orig
    


    def handleEvents(self, evn_handled, key_repeat, repeat_timer, repeat_delay):
        '''principal function to evaluate key pressed'''
        holded = []     # ['shft', 'ctrl', 'alt', 'oskey']

        modifiers = {
            events.LEFTSHIFTKEY  : 'shft',
            events.RIGHTSHIFTKEY : 'shft',
            events.LEFTCTRLKEY   : 'ctrl',
            events.RIGHTCTRLKEY  : 'ctrl',
            events.LEFTALTKEY    : 'alt',
            events.RIGHTALTKEY   : 'alt',
            events.OSKEY         : 'oskey',
            }

        keys = {
            events.LEFTARROWKEY  : self.curLeft,
            events.RIGHTARROWKEY : self.curRight,
            events.BACKSPACEKEY  : self.curBackspace,
            events.DELKEY        : self.curDelete,
            events.HOMEKEY       : self.curHome,
            events.ENDKEY        : self.curEnd,
            events.ENTERKEY      : self.execute,
            events.UPARROWKEY    : self.historyUp,
            events.DOWNARROWKEY  : self.historyDown,
            events.TABKEY        : self.magicKey,
            #events.TABKEY        : self.autocomp
            #events.TABKEY : selfself.autocomp if self.PrevChar
            #181 : lambda holded:self.curInsertChar(':'),
            }


        def process_key(holded):
            if self.special_char_request:
                self.removePopup()
                self.special_char_request = False
                #if 'ctrl' in holded and key == events.SPACEKEY:
                if key in self.special_char_map:
                    self.curInsertChar(self.special_char_map[key])

            elif 'ctrl' in holded and key == events.SPACEKEY:
                self.removePopup()
                self.AddScrollback('╔'+'═'*78 +'╗', MESSGS_COLOR)
                self.AddScrollback('║ 1 ()    2 []     3 {}     4 <>'
                                   '     5 \\\'     6 @&     7 ;:   '
                                   '  8 +*     9 -/  ║', MESSGS_COLOR)
                self.AddScrollback('╚'+'═'*78 +'╝', MESSGS_COLOR)
                self.special_char_request = True
                self.doing_autocomplete = False
                self.popup_lines +=3

            else:
                self.curInsertChar(
                    events.EventToCharacter(key, 'shft' in holded)
                    .translate(self.my_keyboard))
                if self.doing_autocomplete:
                    self.autocomp()


                    
        # check modifiers in key events
        #     and keep in a list, ['ctrl', 'shft', 'alt']
        for key, status in evn_handled:
            if (key in modifiers and 
                    (status.active or status.activated)):
                holded.append(modifiers[key])

        # first process cursor keys, then oskeys,
        #     finally normal chars with process_key function
        for key, status in evn_handled:
            if (key not in modifiers and 
                    (status.active or status.activated)):
                if key == key_repeat:
                    if repeat_timer > repeat_delay:
                        keys.get(key, process_key)(holded)
                    return key, repeat_timer
                else:
                    keys.get(key, process_key)(holded)
                    return key, 0
        
        # never process a key different than modifiers 
        # don't send key repeat (return False)
        return events.MIDDLEMOUSE, 0


    def GetTextCommandline(self):
        #self.FillScrollback()
        prefix = PROMPT_MULTI if self.is_multiline else PROMPT
        #self.edit_text = edt[:self.cur] + ch + edt[self.cur:]
        #if blink:
        #    return prefix + self.edit_text[:self.cur] + '|' + self.edit_text[self.cur+1:]
        #else:
        return (prefix + self.edit_text, PROMPT_COLOR)


    def GetText(self):
        self.FillScrollback()
        sb = self.scrollback
        lines = [ sb[i][0] for i in range(len(sb)) ]
        return '\n'.join(lines) + '\n' + self.GetTextCommandline()[0]



def main(cont):

    own = cont.owner
    sens = cont.sensors['any_key']
    global bge_log
    
    if sens.positive :

        if hasattr(logic, '__console__'):
            bcon = logic.__console__
            #print(sens.events)
            #delay = (own['repeat_delay'] > own['repeat_length'])
            #breakpoint.here
            (bcon.key_repeat,
             own['repeat_timer']) = bcon.handleEvents(sens.inputs.items(),
                                                bcon.key_repeat,
                                                own['repeat_timer'],
                                                own['repeat_delay'])

        else: # if 181 in list(zip(*sens.events))[0]: #magia
            bcon = logic.__console__ = BgeConsole(cont)
            #bcon.AddScrollback('\n'*10)
            bcon.AddScrollback(__doc__, MESSGS_COLOR)
            now = datetime.now()
            bge_log = bpy.data.texts.get('bge_console_log')
            if bge_log:
                bge_log = bpy.data.texts['bge_console_log']
                bge_log.clear()
            else:
                bge_log = bpy.data.texts.new('bge_console_log')
            
            print(Fore.YELLOW + "# BGE Console started", file=stream)
            print(now.strftime("# session of %Y %m %d, %A at %H:%M"), file=stream)
            print("# On file %s\n" % __file__[:-10], file=stream)
            
            bge_log.write("# BGE Console started\n")
            bge_log.write(now.strftime("# session of %Y %m %d, %A at %H:%M\n"))
            bge_log.write("# On file %s\n\n" % __file__[:-10])
            

        try:
            # Draw the text!
            for i, line in enumerate(bcon.scrollback[-SCROLLBACK:]):
                logic.rows[28 - i]['text'] = line[0]
                logic.rows[28 - i]['color'] = line[1]
            logic.rows[0]['text'] = bcon.GetTextCommandline()[0]
            logic.rows[0]['color'] = bcon.GetTextCommandline()[1]
        except:
            pass

    elif hasattr(logic, '__console__'):
        bcon = logic.__console__
        bcon.key_repeat = events.MIDDLEMOUSE
        # own['repeat_timer'] = ? 0?
        


def blink(cont):
    '''function for making blinking cursor'''
    own = cont.owner
    try:
        bcon = logic.__console__
        own['blink'] = not own['blink']
        if own['blink']:
            logic.rows[0]['text'] = logic.rows[0]['text'][:bcon.cur+4] + \
                                    '█' + logic.rows[0]['text'][bcon.cur+5:]
        else:
            logic.rows[0]['text'] = bcon.GetTextCommandline()[0]
    except:
        pass

