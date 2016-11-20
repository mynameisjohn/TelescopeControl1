import copy
import ctypes
import sdl2

from InputManager import Button, KeyboardManager
from TelescopeComm import TelescopeComm

# Nothing doing
def Update():
    pass

# Global quit flag and keyboard input manager
g_QuitFlag = False
g_KeybdMgr = None

# Init with device name and address of SDL event
def Init(strDevice, sdlEventAddr):
    # Create communications object
    comm = TelescopeComm(str(strDevice))

    # Set up keyboard manager
    global g_KeybdMgr, g_QuitFlag


    # Escape key will quit
    def fnQuit(btn, mgr):
        global g_QuitFlag
        g_QuitFlag = True

    # Key presses up will stop movement in that direction
    def fnSlewKeyUp(btn, mgr):
        nonlocal comm
        if keyCode in {sdl2.keycode.SDLK_UP, sdl2.keycode.SDLK_DOWN}:
            strID = 'Alt'
        elif keyCode in {sdl2.keycode.SDLK_LEFT, sdl2.keycode.SDLK_RIGHT}:
            strID = 'Azm'
        g_TelescopeComm.slew(strID, 0)

    # Key  presses down will start slewing
    # TODO changing direction, check the manager for opposite state
    nSpeed = 5
    def fnSlewKeyDown(btn, mgr):
        nonlocal comm
        nonlocal nSpeed
        # Alt or Azimuth
        if keyCode in {sdl2.keycode.SDLK_UP, sdl2.keycode.SDLK_DOWN}:
            strID = 'Alt'
        elif keyCode in {sdl2.keycode.SDLK_LEFT, sdl2.keycode.SDLK_RIGHT}:
            strID = 'Azm'
        # Negate for down, left
        if keyCode in {sdl2.keycode.SDLK_DOWN, sdl2.keycode.SDLK_LEFT}:
            nSpeed = -nSpeed
        # Send slew command
        g_TelescopeComm.slew(strID, nSpeed)

    # create button handlers for escape, up, down, left, right
    keyList = [Button(sdl2.keycode.SDLK_ESCAPE, fnUp = fnQuit)]
    for keyCode in {sdl2.keycode.SDLK_UP, sdl2.keycode.SDLK_DOWN, sdl2.keycode.SDLK_LEFT, sdl2.keycode.SDLK_RIGHT}:
        keyList.append(Button(keyCode, fnUp = fnSlewKeyUp, fnDown = fnSlewKeyDown))

    # Create keyboard manager
    g_KeybdMgr = KeyboardManager(keyList)

# Handle SDL events
def HandleEvent():
    # Capture global telescope comm
    global g_KeybdMgr, g_QuitFlag
    # Slew commands have a speed of 5 for now
    nSpeed = 5

    # construct the SDL event from the addresss
    e = sdl2.events.SDL_Event.from_address(g_sdlEventAddress)

    # Return false for quit events
    if e.type == sdl2.events.SDL_QUIT:
        return False

    # Give it to the keyboard manager
    g_KeybdMgr.HandleEvent(e)
    return g_QuitFlag
