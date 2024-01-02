
# PygamingTheSeleniumSystem

## Introduction

A wrapper to create keyboard support for selenium. Instead of modifying Selenium, it simply uses a Pygame window to 
capture the keyboard presses. Mouse support is not included, but "refocus" mode allows an user to click the selenium
navigator and gets back to focus the Pygame window.

## How to use

The code is fairly straight-forward. Create a function which receives 3 variables, controller, pipes and locks. From 
there, wrap the function in the wrapper call.

    def quit_on_escape(driver, queues, locks):
        while (new_key := queues["i"].get(block=True)) != pygame.K_ESCAPE:
            print(pygame.key.name(new_key))

    wrapper(quit_on_escape)

## Transparency mode (experimental)

Transparency mode is a feature on early implementation (still non-functional) with the purpose of creating
a mode where one can over-lap a transparent PYGAMES-window over the navigator. That way, "click-through" would 
be possible, allowing a programatic handling of mouse-clicks as well as keystrokes. 

Right now it's only on a test stage, as it seems to be more complex than originally intended. This is  due to how 
different linux window-managers and x-servers handle transparency. It may be removed if it's deemed to be too much
of a hustle.

The short-comings need to be taken into consideration are the following: 

* More configuration would be needed to run the program, either by adding an ENV-VAR or on a config file.
* The code becomes considerably more complex, having to be able to check if it's doing a regualr run or one 
that's using transparency.
* There will be a lot of unsupported window-manager configurations, as I don't intend to spend much time on them.
* Support relays on 3rd parties not changing how their configurations work together. Changes there are to be expected, 
and they can lead to things breaking on this library for apparently no reason.
* You would have a mode that only work on certain number of machines, requiring 2 sets of logic for the same 
program. (one in which you expect to know when a user makes a click, a second one where you don't) 


# TODO

* Either complete or remove transparency-mode. 
* Add Mac support
* Test Win support
