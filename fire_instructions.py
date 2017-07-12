from pyadb.adb import ADB
import re

class InstructionsList:

    def listen_up(self):
        print 'turning on command mode!'
        global command_mode
        command_mode = True
    def go_away(self):
        print 'command mode off.'
        global command_mode
        command_mode = False

    def home(self):
        adb.shell_command('input keyevent HOME')
    def go_home(self): self.home()
    def take_me_home(self): self.home()

    def wake_up(self):
        screen_on = 'mScreenOn=true' in adb.shell_command('dumpsys input_method')
        if not screen_on:
            self.toggle_screen()
        else:
            awake = 'Bad window' in adb.shell_command('dumpsys window dream')
            if not awake:
                adb.shell_command('input keyevent BACK')

    def down(self): adb.shell_command('input keyevent DPAD_DOWN')
    def up(self): adb.shell_command('input keyevent DPAD_UP')
    def right(self): adb.shell_command('input keyevent DPAD_RIGHT')
    def left(self): adb.shell_command('input keyevent DPAD_LEFT')
    def select(self): adb.shell_command('input keyevent DPAD_CENTER')

    def play(self): adb.shell_command('input keyevent MEDIA_PLAY')
    def pause(self): adb.shell_command('input keyevent MEDIA_PAUSE')
    def paws(self): self.pause()  # Fuck you Google
    def cause(self): self.pause()  # Fuck you Google


    def toggle_screen(self):
        adb.shell_command('input keyevent 26')

    def open_app(self, package):
        print package
        adb.shell_command('monkey -p %s -c android.intent.category.LAUNCHER 1' % package)

command_mode = False
tvip = '192.168.1.170'

def do(instr):
    instr = instr.lower()
    print instr

    if not command_mode:
        if instr.startswith('okay fire'):
            instr = instr[9:].strip()
        elif instr.startswith('ok fire'):
            instr = instr[7:].strip()
        else:
            return

    if ' and ' in instr:
        [ do(part) for part in instr.split(' and ') ]
        return

    if instr.startswith('open '):
        app = instr[5:]
        il.open_app(app_names.get(app.lower().replace(' ',''), ''))
        return
    if instr.startswith('type '):
        text = instr[6:]
        adb.shell_command('input text %s' % text)
        return
    if instr.startswith('press '):
        text = instr[6:]
        adb.shell_command('input keyevent %s' % re.sub(r'[^\w\d\ ]', '', text).replace(' ','_').upper())
        return
    try:
        eval('il.%s()' % instr.replace(' ','_'))
    except AttributeError: pass

def get_label(apk):
    aapt_output = adb.shell_command('/data/local/tmp/aapt d badging %s' % apk)
    if 'not found' in aapt_output:
        adb.push_local_file('aapt', '/data/local/tmp/aapt')  # aapt needed to find application names
        adb.shell_command('chmod 755 /data/local/tmp/aapt')
        return get_label(apk)
    match = re.search(r'^application: label=\'([\S]+?)\'', aapt_output, re.MULTILINE)
    if match and match.groups():
        return match.group(1)

il = InstructionsList()

app_names = {}

adb = ADB()
adb.connect_remote(tvip)

pm_list = adb.shell_command('pm list packages -f')
for line in pm_list.split('\r\n'):
    try:
        groups = re.match(r'package:(.+?\.apk)=(.*)', line).groups()
        if groups:
            apk, package = groups
            print apk, package
            label = get_label(apk)
            if label:
                app_names[label.lower()] = package.replace(' ','')
    except KeyboardInterrupt: exit(1)
    except: pass
