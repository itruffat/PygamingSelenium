import os
from time import sleep
from multiprocessing import Process, Queue, Lock

import pygame
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions

from os_parse import (gw, get_activate_function, transparent,
                      window_mode, PGWindowMode,
                      local_chrome_binary, local_chromedriver_path)


class RefocusingError(Exception):
    """Error on refocus branch"""


def refocus_pygames_after_pause(refocus, read, read_lock, ending):
    """Refocus is a subprocess that takes the focus back into pygames, allowing you to click things on selenium without
    losing the access to keyboard presses.
    """
    # Input with other processes is shared via 3 pipelines:
    #
    # * Refocus pipe enables/disables this functionality via the reception of a number.
    # For most inputs, 1 means active / -1 means inactive.
    #
    # >    Note: Other numerical values may be introduced to indicate the desired wait-time between steps. 2 means active
    # >    with 1-second delay. 3.5 means active with 2.5-seconds delay. -2 means inactive with 1-second delay. And so on.
    #
    # > Read pipe tells the status of the current refocus, so that an application can get the desired status without
    # having to sync any variable.
    #
    # * Ending pipeline means the whole subprocess should be killed. It doesn't matter which value, as long as anything is
    # present it will stop the loop and return a Null value.
    # """

    if window_mode is not PGWindowMode.REFOCUS:
        return 0   # No need to run this if we are not on refocus mode

    active = False
    sleep_time = 1
    pygame_window = None

    while pygame_window is None:
        potential_windows = gw.getWindowsWithTitle('Pygaming_selenium')
        pygame_window = potential_windows[0] if len(potential_windows) > 0 else None

    pygame_window_activate = get_activate_function(pygame_window)

    read_lock.acquire()
    read.put(active)
    read_lock.release()

    while ending.empty():

        if not refocus.empty():
            value = refocus.get()
            if value >= 1:
                active = True
                if value == 1:
                    sleep_time = 0.02
                else:
                    sleep_time = value - 1
            elif value <= -1:
                active = False
                if value == -1:
                    sleep_time = 1
                else:
                    sleep_time = -1 - value
            else:
                raise RefocusingError()

            read_lock.acquire()
            read.get()
            read.put(active)
            read_lock.release()

        sleep(sleep_time)

        if not active:
            continue

        if gw.getActiveWindow() != pygame_window:
            pygame_window_activate()

    return 0


def get_input_with_pygames(inputs, ending, write_focus, read_focus, read_lock,  *, corner, only_up):
    """Get input from pygames, and put it into the inputs pipe. If refocus is allowed, it will look for the F1 key to
    reverse the automatic refocus feature. (Either activate or deactivate)"""
    if corner:
        os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
        os.environ['SDL_VIDEO_CENTERED'] = '0'
    pygame.init()
    pygame.display.set_caption('Pygaming_selenium')
    pygame.display.set_mode(size=[90, 90], flags=pygame.NOFRAME)
    pygame.display.update()
    while ending.empty():
        for event in pygame.event.get():
            if (not only_up and event.type == pygame.KEYDOWN) or event.type == pygame.KEYUP:
                if window_mode is PGWindowMode.REFOCUS:
                    if pygame.K_F1 == event.key and event.type == pygame.KEYUP:
                        read_lock.acquire()
                        focus_value = read_focus.get()
                        read_focus.put(focus_value)
                        read_lock.release()
                        write_focus.put(-1 if focus_value else 1)  # Reverse value of refocus task
                inputs.put(event.key)
    pygame.quit()
    return 0


def wrapper(main_loop, chromedriver_path=local_chromedriver_path, chrome_binary=local_chrome_binary):
    """


    """
    # Define subprocesses
    i_queue = Queue()   # INPUT
    r1_queue = Queue()  # REFOCUS
    r2_queue = Queue()  # REFOCUS_READ
    r2_lock = Lock()    # REFOCUS_READ (LOCK)
    e_queue = Queue()   # EXIT
    ps = (
        Process(target=get_input_with_pygames,
                args=(i_queue, e_queue, r1_queue, r2_queue, r2_lock),
                kwargs={'corner': True, 'only_up': True}
                ),
        Process(target=refocus_pygames_after_pause,
                args=(r1_queue, r2_queue, r2_lock, e_queue)
                ),
    )

    # Setup selenium
    chrome_service = Service(executable_path=chromedriver_path)
    options = ChromeOptions()
    # options.add_argument("--headless=new")
    # options.add_argument('--kiosk')
    options.binary_location = chrome_binary
    driver = webdriver.Chrome(options=options, service=chrome_service)

    # Run subprocesses
    for p in ps:
        p.start()

    # Main Loop
    main_loop(driver=driver,
              queues={'i': i_queue, 'r1': r1_queue, 'r2': r2_queue, 'e': e_queue},
              locks={'r2': r2_lock}
    )

    # End subprocesses
    if e_queue.empty():
        e_queue.put(1)

    for p in ps:
        p.join()