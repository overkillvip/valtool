import os
from termcolor import colored
from debug import DEBUG

#cls = lambda: os.system("cls || clear")
color = "dark_grey"
prefix = f"{colored('[', color)}{colored('$', 'magenta')}{colored(']', color)}"

# circular imports can suck my dick
def cls(name:str = None):
    os.system("cls || clear")
    if name: print(f"\n{prefix} {colored(name, "light_magenta", attrs=["blink", "bold"])}")


def spinner(i):
    match i:
        case 1:
            spin = "/"
        case 2:
            spin = "-"
        case 3:
            spin = "\\"
        case 5:
            spin = "/"
        case 6:
            spin = "-"
        case 7:
            spin = "\\"
        case _:
            spin = "|"
    return spin

class Logger():
    def __init__(self):
        self.level = DEBUG.level
        self.verbose = DEBUG.verbose
    
    # notice the bot is cleaner
    def log(self, function:str, msg, type:str, level=1, **kwargs):
        if type.upper() == "DEBUG" and level > self.level: return

        function = f"{function.lower()}" if function else ""
        print(f"\n[{colored(type.upper(), 'magenta')}] ({colored(function, color)}) {colored(msg, color)}", **kwargs)
        if type.upper() == "CRITICAL": exit()

    def print(self, msg, inputmode=False, newlines=2):
        print(f"{'\n' * newlines}{prefix} {colored(msg, color)}", end=("\n" if inputmode else ""))
        if inputmode: return input(colored("   > ", color))

LOGGER = Logger()