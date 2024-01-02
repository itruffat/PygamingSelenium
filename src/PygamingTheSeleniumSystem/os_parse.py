import sys
import pygame
import os
import re
from enum import Enum
import subprocess


class PGWindowMode(Enum):
    VANILLA = "VANILLA"             # NO REFOCUS OR TRANSPARENT
    REFOCUS = "REFOCUS"             # REFOCUS EVERY FEW SECONDS ON PYCHARM WINDOW
    TRANSPARENT = "TRANSPARENT"     # TRANSPARENT WINDOW, CLICK THROUGH
    UNKNOWN = "UNKNOWN"             # GUESS THE AVAILABLE MODE, IN TRANSPARENT > REFOCUS > VANILLA ORDER


window_mode = PGWindowMode(os.environ.get("PYGAMING_SELENIUM_PYGAME_WINDOW", "REFOCUS"))

try:
    from local import local_chrome_binary, local_chromedriver_path  # TODO remove this line
except ImportError:
    local_chrome_binary = os.environ.get("PYGAMING_SELENIUM_BINARY", "")
    local_chromedriver_path = os.environ.get("PYGAMING_SELENIUM_PATH", "")

# WINDOW GETTER

if sys.platform == "linux":
    import pywinctl as gw
elif sys.platform == "win32":
    import pygetwindow as gw
    print("WARNING: NOT TESTED ON WINDOWS")
elif sys.platform == "darwin":
    gw = None
    if window_mode is PGWindowMode.UNKNOWN:
        window_mode = PGWindowMode.VANILLA
    if window_mode is not PGWindowMode.VANILLA:
        raise NotImplementedError("Not supported on MAC")
else:
    raise NotImplementedError("Unknown platform is not supported")


# WINDOW ACTIVATION


def get_activate_function(window):
    if sys.platform == "linux":
        return window.activate
    elif sys.platform == "win32":
        return window.focus
    else:
        raise Exception()


# TRANSPARENCY FUNCTIONS

def get_linux_window_manager():
    """https://stackoverflow.com/questions/3333243/how-can-i-check-with-python-which-window-manager-is-running"""
    output = subprocess.run(['wmctrl', '-m'], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if output.stderr:
        return -1, output.stderr
    else:
        regex_answer = re.match(r"Name: (.*)", output.stdout)
        if regex_answer is None:
            return -2, None
        return 0, regex_answer.group(1)


def transparent_window32(window, color):
    """From https://stackoverflow.com/questions/550001/fully-transparent-windows-in-pygame """
    win32gui.SetWindowLong(window, win32con.GWL_EXSTYLE,
                           win32gui.GetWindowLong(window, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
    win32gui.SetLayeredWindowAttributes(window, win32api.RGB(*color), 0, win32con.LWA_COLORKEY)
    pygame.display.get_surface().fill(color)
    pygame.display.update()


def transparent_marco():
    pass


supported_window_managers = {'Metacity (Marco)': transparent_marco}

not_supported_window_managers = []


assert(all([window_man not in supported_window_managers.keys() for window_man in not_supported_window_managers]))


if window_mode is PGWindowMode.TRANSPARENT or window_mode is PGWindowMode.UNKNOWN:
    raise NotImplementedError()
    if sys.platform == "linux":
        win32api, win32con, win32gui = None, None, None
        error, window_manager = get_linux_window_manager()
        if window_mode is PGWindowMode.TRANSPARENT:
            if error != 0:
                raise FileNotFoundError(f"Could not run wmctrl.(Error {error})")
            if window_manager not in supported_window_managers.keys():
                raise NotImplementedError(f"Window manager '{window_manager}' not supported.")
        if window_mode is PGWindowMode.UNKNOWN:
            if error != 0:
                print(f"Could not run wmctrl. (Error {error}) Using non transparency-mode")
                window_mode = PGWindowMode.REFOCUS
            elif window_manager not in supported_window_managers.keys():
                print(f"Window manager '{window_manager}' not supported. Using non transparency-mode. ")
                window_mode = PGWindowMode.REFOCUS
            else:
                window_mode = PGWindowMode.TRANSPARENT

        if window_mode is PGWindowMode.TRANSPARENT:
            transparent = supported_window_managers[window_manager]

    elif sys.platform == "win32":
        try:
            import win32api, win32con, win32gui
        except ImportError as er:
            if window_mode is PGWindowMode.TRANSPARENT:
                raise er
            window_mode = PGWindowMode.REFOCUS
        else:
            transparent = transparent_window32
            window_mode = PGWindowMode.TRANSPARENT

if window_mode is PGWindowMode.REFOCUS or window_mode is PGWindowMode.VANILLA:
    win32api, win32con, win32gui = None, None, None
    transparent = None