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
g_sdlEventAddress = None

# Init with device name and address of SDL event
def Init(strDevice, sdlEventAddr):
    # Create communications object
    comm = TelescopeComm(strDevice.decode('utf-8'))

    # Set up keyboard manager
    global g_KeybdMgr, g_QuitFlag, g_sdlEventAddress

    # Escape key will quit
    def fnQuit(btn, mgr):
        global g_QuitFlag
        g_QuitFlag = True

    # Key presses up will stop movement in that direction
    def fnSlewKeyUp(btn, mgr):
        nonlocal comm
        if btn.code in {sdl2.keycode.SDLK_UP, sdl2.keycode.SDLK_DOWN}:
            strID = 'Alt'
        elif btn.code in {sdl2.keycode.SDLK_LEFT, sdl2.keycode.SDLK_RIGHT}:
            strID = 'Azm'
        comm.slew(strID, 0)

    # Key  presses down will start slewing
    # TODO changing direction, check the manager for opposite state
    def fnSlewKeyDown(btn, mgr):
        nonlocal comm
        nSpeed = 7
        # Alt or Azimuth
        if btn.code in {sdl2.keycode.SDLK_UP, sdl2.keycode.SDLK_DOWN}:
            strID = 'Alt'
        elif btn.code in {sdl2.keycode.SDLK_LEFT, sdl2.keycode.SDLK_RIGHT}:
            strID = 'Azm'
        # Negate for down, left
        if btn.code in {sdl2.keycode.SDLK_DOWN, sdl2.keycode.SDLK_LEFT}:
            nSpeed = -nSpeed
        # Send slew command
        comm.slew(strID, nSpeed)

    # create button handlers for escape, up, down, left, right
    keyList = [Button(sdl2.keycode.SDLK_ESCAPE, fnUp = fnQuit)]
    for keyCode in {sdl2.keycode.SDLK_UP, sdl2.keycode.SDLK_DOWN, sdl2.keycode.SDLK_LEFT, sdl2.keycode.SDLK_RIGHT}:
        keyList.append(Button(keyCode, fnUp = fnSlewKeyUp, fnDown = fnSlewKeyDown))

    # Create keyboard manager, store event address
    g_KeybdMgr = KeyboardManager(keyList)
    g_sdlEventAddress = int(sdlEventAddr)

# Handle SDL events
def HandleEvent():
    # Capture global telescope comm
    global g_KeybdMgr, g_QuitFlag, g_sdlEventAddress

    # construct the SDL event from the address
    e = sdl2.events.SDL_Event.from_address(g_sdlEventAddress)

    # Return false for quit events
    if e.type == sdl2.events.SDL_QUIT:
        return False

    # Give it to the keyboard manager
    g_KeybdMgr.HandleEvent(e)
    return g_QuitFlag
