#include <pyliaison.h>
#include <SDL2/SDL.h>
#include <iostream>

int main(int argc, char ** argv){
    // Command line args are device and speed
    if (argc < 2){
       std::cout << "Error: Need device name on cmd line" << std::endl;
       return -1;
    }

    // We need a dummy window for handling events
    SDL_Window * pWindow = SDL_CreateWindow("Dummy", SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED, 400, 400, 0);
    if (!pWindow)
        return -1;

    // Init python
    pyl::initialize();

    // Get device name
    std::string strDevice = argv[1];

    // Get main python script
    pyl::Object obMain = pyl::Object::from_script("main.py");

    // Initialize python script with address of SDL event
    SDL_Event e{0};
    obMain.call("Init", strDevice, (int64_t)&e);

    // Main event loop
    volatile bool bQuit(false);
    while (!bQuit){
        // Update
        obMain.call("Update");

        // Convert HandleEvent result to bool
        while (SDL_PollEvent(&e))
            obMain.call("HandleEvent").convert(bQuit);
    }

    // Close window, finalize python, return
    SDL_DestroyWindow(pWindow);
    pyl::finalize();
    return 0;
}
