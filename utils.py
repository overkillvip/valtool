import os
from termcolor import colored

#cls = lambda: os.system("cls || clear")
color = "dark_grey"
prefix = f"{colored('[', color)}{colored('$', 'magenta')}{colored(']', color)}"

def cls(name):
    os.system("cls || clear")
    print(f"\n{prefix} {colored(name, "light_magenta", attrs=["blink", "bold"])}")


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