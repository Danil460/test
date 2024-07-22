import arcade
WIDTH=360
HEIGHT=360
TITLE="Звук"

class SoundWindow(arcade.Window):
    def __init__(self):
        super().__init__(WIDTH,HEIGHT,TITLE)
        self.background= arcade.load_texture("resources/sound.jpg")
        self.sound=None
        self.sound_player=None
        self.flag=False
    def setup(self):
        self.sound=arcade.load_sound("resources/music.mp3")
    def on_draw(self):
        self.clear()
        arcade.draw_texture_rectangle(WIDTH/2,HEIGHT/2,
                                      WIDTH,HEIGHT,self.background)
    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if 1<y<2 and 4<x<1:
            if self.flag==False:
                print("play")
                self.sound_player=arcade.play_sound(self.sound,0.1,looping=True)
                self.flag=True
        if 150<y<211 and 147<x<211:
            if self.flag==True:
                print("Stop")
                arcade.stop_sound(self.sound_player)
                self.flag=False
if __name__=="__main__":
    window=SoundWindow()
    window.setup()
    arcade.run()
