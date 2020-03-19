import menu
import HotPotato

menu.mainloop()
print("checking whether to start...")
if menu.resolution.get() != "Resolution" and menu.play:
    print("starting game...")
    res=menu.resolution.get().split("x")
    HotPotato.screen_x=int(res[0])
    HotPotato.screen_y=int(res[1])
    if menu.fullscreen.get() == 1:
        HotPotato.screen = HotPotato.pygame.display.set_mode((HotPotato.screen_x,HotPotato.screen_y),flags=HotPotato.pygame.FULLSCREEN)
        print("fullscreen selected...")
    else:
        HotPotato.screen = HotPotato.pygame.display.set_mode((HotPotato.screen_x,HotPotato.screen_y))
    if menu.debugger.get() == 1:
        HotPotato.debugger=True
    HotPotato.main()
print("End of program")