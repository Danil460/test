import arcade
import math

SCREEN_TITLE = "Использование PyMunk"

SPRITE_IMAGE_SIZE = 128

SPRITE_SCALING_PLAYER = 0.3
SPRITE_SCALING_TILES = 0.3

SPRITE_SIZE = int(SPRITE_IMAGE_SIZE * SPRITE_SCALING_PLAYER)

SCREEN_GRID_WIDTH = 25 #Ширина
SCREEN_GRID_HEIGHT = 15 #Высота

SCREEN_WIDTH = SPRITE_SIZE * SCREEN_GRID_WIDTH#Общая ширина
SCREEN_HEIGHT = SPRITE_SIZE * SCREEN_GRID_HEIGHT#Общая высота
GRAVITY=1500#Гравитация

DEFAULT_DAMPING=1.0
PLAYER_DAMPING=0.4#Ускорение

PLAYER_FRICTION=1.0#Трения игрока
WALL_FRICTION=0.7#Трения стен
DYNAMIC_ITEM_FRICTION=0.6#Трения предметов

PLAYER_MASS=2.0#Масса
PLAYER_MAX_HORIZONTAL_SPEED=200#Максимальная горизонтальная скорость игрока
PLAYER_MAX_VERTICAL_SPEED=1600#Максимальная вертикальная скорость игрока
PLAYER_MOVE_FORCE_ON_GROUND=8000#Скорость с которой он будет перемещаться
PLAYER_JUMP_IMPULSE=1300#Прыжок сила
DEAD_ZONE=0.1#мертвая зона
RIGHT_FACING=0#Лицо вправо
LEFT_FACING=1#Лицо в лево
DISTANCE_TO_CHANGE_TEXTURE=20#Дистанция для изменения техтуры
BULLET_MOVE_FORCE = 4500#Скорость(движение)
BULLET_MASS = 0.1#Масса пули
BULLET_GRAVITY = 300#Гравитация пули


class PlayerSprite(arcade.Sprite):
    def __init__(self):
        super().__init__()

        self.scale = SPRITE_SCALING_PLAYER

        main_path = ":resources:images/animated_characters/female_person/femalePerson"

        self.idle_texture_pair = arcade.load_texture_pair(f"{main_path}_idle.png")
        self.jump_texture_pair = arcade.load_texture_pair(f"{main_path}_jump.png")
        self.fall_texture_pair = arcade.load_texture_pair(f"{main_path}_fall.png")

        self.walk_textures = []
        for i in range(8):
            texture = arcade.load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)

        self.texture = self.idle_texture_pair[0]

        self.hit_box = self.texture.hit_box_points#Хитбоксы или касание(консулся ли чего)
        self.character_face_direction = RIGHT_FACING
        self.cur_texture = 0
        self.x_odometer = 0

    def pymunk_moved(self, physics_engine, dx, dy, d_angle):  # Физические движения
        if dx < -DEAD_ZONE and self.character_face_direction == RIGHT_FACING:  # Меняет лицо взависимости от мертвой зоны
            self.character_face_direction = LEFT_FACING
        elif dx > DEAD_ZONE and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        is_on_ground = physics_engine.is_on_ground(self)

        self.x_odometer += dx

        if not is_on_ground:
            if dy > DEAD_ZONE:
                self.texture = self.jump_texture_pair[self.character_face_direction]
                return
            elif dy < -DEAD_ZONE:
                self.texture = self.fall_texture_pair[self.character_face_direction]
                return

        if abs(dx) <= DEAD_ZONE:  # Встроенный модуль который делает -1=1.
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        if abs(self.x_odometer) > DISTANCE_TO_CHANGE_TEXTURE:
            self.x_odometer = 0

            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
                self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]

class BulletSprite(arcade.SpriteSolidColor):
    def pymunk_moved(self, phisics_engine, dx, dy, d_angle):
        if self.center_y < -100:
            self.remove_from_sprite_lists()

class GameWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.player_sprite = None

        self.player_list = None  # игрок
        self.wall_list = None  # Стена
        self.bullet_list = None  # Пуля
        self.item_list = None  # Предмет

        self.left_pressed = False
        self.right_pressed = False
        arcade.set_background_color(arcade.color.AMAZON)
        self.phisics_engine = None
        self.back_sound=None
        self.back_play_sound=None
        self.bullet_sound=None
        self.bullet_play_sound=None
        self.jump_sound=None
        self.jump_sound_play=None



    def setup(self):
        self.jump_sound=arcade.load_sound("8bit-synth-bounce-short.mp3")
        self.back_sound=arcade.load_sound("resources/music.mp3")
        self.bullet_sound=arcade.load_sound("resources/sfx_wing.ogg")
        self.back_play_sound=arcade.play_sound(self.back_sound,0.1,
                                               looping=True)
        self.player_list = arcade.SpriteList()  # Подключили список игрока
        self.bullet_list = arcade.SpriteList()
        map_name = (":resources:/tiled_maps/pymunk_test_map.json")
        tile_map = arcade.load_tilemap(map_name, SPRITE_SCALING_TILES)
        self.wall_list = tile_map.sprite_lists["Platforms"]
        self.item_list = tile_map.sprite_lists["Dynamic Items"]
        self.player_sprite = PlayerSprite()
        self.player_sprite.center_y = SPRITE_SIZE + SPRITE_SIZE / 2
        self.player_sprite.center_x = SPRITE_SIZE + SPRITE_SIZE / 2
        self.player_list.append(self.player_sprite)
        damping = DEFAULT_DAMPING
        gravity = (0, -GRAVITY)  # -GRAVITY Улетает вниз,а не верх
        self.phisics_engine = arcade.PymunkPhysicsEngine(damping=damping, gravity=gravity)
        self.phisics_engine.add_sprite(self.player_sprite, friction=PLAYER_FRICTION, mass=PLAYER_MASS,
                                       moment=arcade.PymunkPhysicsEngine.MOMENT_INF, collision_type='player',
                                       max_horizontal_velocity=PLAYER_MAX_HORIZONTAL_SPEED,
                                       max_vertical_velocity=PLAYER_MAX_VERTICAL_SPEED)
        self.phisics_engine.add_sprite_list(self.wall_list, friction=WALL_FRICTION, collision_type="wall",
                                            body_type=arcade.PymunkPhysicsEngine.STATIC)
        self.moving_sprites_list = None
        self.moving_sprites_list = tile_map.sprite_lists['Moving Platforms']
        self.phisics_engine.add_sprite_list(self.moving_sprites_list,
                                            body_type=arcade.PymunkPhysicsEngine.KINEMATIC)
        self.phisics_engine.add_sprite_list(self.item_list,
                                            friction=DYNAMIC_ITEM_FRICTION,
                                            collision_type="item")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.UP:
            if self.phisics_engine.is_on_ground(self.player_sprite):
                impulse = (0, PLAYER_JUMP_IMPULSE)
                self.jump_sound_play=arcade.play_sound(self.jump_sound,0.5 )
                self.phisics_engine.apply_impulse(self.player_sprite, impulse)
        elif key==arcade.key.SPACE:
            arcade.stop_sound(self.back_play_sound)
    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False

    def on_update(self, delta_time):
        if self.left_pressed and not self.right_pressed:  # работает лево и не работае право то
            force = (-PLAYER_MOVE_FORCE_ON_GROUND, 0)
            self.phisics_engine.apply_force(self.player_sprite, force)
            self.phisics_engine.set_friction(self.player_sprite, 0)
        elif self.right_pressed and not self.left_pressed:  # работает право и не работае лево то
            force = (PLAYER_MOVE_FORCE_ON_GROUND, 0)
            self.phisics_engine.apply_force(self.player_sprite, force)
            self.phisics_engine.set_friction(self.player_sprite, 0)
        else:
            self.phisics_engine.set_friction(self.player_sprite, 1.0)
        self.phisics_engine.step()
        for moving_sprite in self.moving_sprites_list:
            if moving_sprite.boundary_right and \
                    moving_sprite.change_x > 0 and \
                    moving_sprite.right > moving_sprite.boundary_right:
                moving_sprite.change_x *= -1
            elif moving_sprite.boundary_left and \
                    moving_sprite.change_x < 0 and \
                    moving_sprite.left > moving_sprite.boundary_left:
                moving_sprite.change_x *= -1
            if moving_sprite.boundary_top and \
                    moving_sprite.change_y > 0 and \
                    moving_sprite.top > moving_sprite.boundary_top:
                moving_sprite.change_y *= -1
            elif moving_sprite.boundary_bottom and \
                    moving_sprite.change_y < 0 and \
moving_sprite.bottom < moving_sprite.boundary_bottom:
                moving_sprite.change_y *= -1
            velocity = (moving_sprite.change_x * 1 / delta_time, moving_sprite.change_y * 1 / delta_time)
            self.phisics_engine.set_velocity(moving_sprite, velocity)

    def on_mouse_press(self, x, y, button, modifiers):#Событие нажатие кнопки мыши
        self.bullet_play_sound=arcade.play_sound(self.bullet_sound,1)
        bullet = BulletSprite(20, 5, arcade.color.DARK_YELLOW)
        self.bullet_list.append(bullet)
        start_x = self.player_sprite.center_x
        start_y = self.player_sprite.center_y
        bullet.position = self.player_sprite.position
        #Запоминаем где пользователь нажал кнопку

        dest_x = x
        dest_y = y

        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)#Рассчёт

        size = max(self.player_sprite.width, self.player_sprite.height) / 2

        bullet.center_x += size * math.cos(angle)
        bullet.center_y += size * math.sin(angle)
        bullet.angle = math.degrees(angle)

        bullet_gravity = (0, -BULLET_GRAVITY)

        self.phisics_engine.add_sprite(bullet,
                                       mass=BULLET_MASS,
                                       damping=1.0,
                                       friction=0.6,
                                       collision_type="bullet",
                                       gravity=bullet_gravity,
                                       elasticity=0.9)

        force = (BULLET_MOVE_FORCE, 0)
        self.phisics_engine.apply_force(bullet,force)

    def on_draw(self):
        self.clear()
        self.wall_list.draw()
        self.item_list.draw()
        self.player_list.draw()
        self.bullet_list.draw()
        self.moving_sprites_list.draw()


def main():
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()



if __name__ == "__main__":
    main()