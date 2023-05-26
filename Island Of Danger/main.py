from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.prefabs.health_bar import HealthBar
from ursina.prefabs.trail_renderer import TrailRenderer
import random
import math

from shader import light

app = Ursina()

#---------------start-----------------

#---------------window----------------

window.title = 'Island Of Danger'
window.borderless = False
window.icon = "icon.ico"
window.cog_button.disable()
window.fps_counter.disable()
window.exit_button.disable()
window.fullscreen = True

#-------------throw_ball--------------

spawned_object = Entity(model='rock', color=color.gray, collider='sphere', position=(0,-5,0))

def spawn_object():
    position = camera.world_position + camera.forward * 2
    spawned_object.position = position
    spawned_object.direction = camera.forward
    
    def update():
        spawned_object.position += spawned_object.direction * 2
    
    spawned_object.update = update

#------------death_screen-------------

Text.default_resolution = 8000 * Text.size

def death_screen():
	bg = Entity(model='cube', scale=10, color=color.black, parent=camera.ui)
	text = Text(scale=10, text='DED', position=(-.25,.1), always_on_top=True)

#----------------UI-------------------

crosshair = Entity(model='sphere', scale=.01, parent=camera.ui, always_on_top=True, texture='crosshair')

ball = Entity(model='rock', scale=.5, parent=camera, position = (1.3, -0.75, 1.7), color=color.gray)

instructions = Text(scale=2.5, text='ESC to close', position=(.5,.47), always_on_top=True)

#---------------health----------------

health_bar = HealthBar(bar_color=color.hex("#FF7D78"), roundness=0, value=50, scale=(.5,.03), position = window.top_left + (0.05, -.01), show_text=False)

#--------------stamina----------------

stamina_bar = HealthBar(text_color=color.white, bar_color=color.hex("#3B85F5"), roundness=0, value=50, scale=(.5,.03), position = window.top_left + (0.05, -0.05), show_text=False)

#---------------input-----------------

kills = 0

def increase_score():
    global kills
    kills += 1
    score.text = f'kills: {kills}'

score = Text(text=kills, scale=2.5, position=(-.1,.5))

def input(key):
    if key == 'left mouse down':
        spawn_object()
        throw = Audio('sounds\\throw.mp3', volume=0.5, loop=False)

    if key == 'escape':
        application.quit()

    if key == 'r':
        health_bar.value += 100
        player.position=(0,0,0)

player = FirstPersonController(collider ='box',speed=20, gravity = .3)

def update(): 
    if player.y <=-6:
        player.position=(0,0,0)

    if health_bar.value <= 0:
        death_screen()
#---------------player---------------


#----------------map-----------------

ground = Entity(model='island',scale=(5,1,5),collider='mesh', position=(0,-5.5,0), texture='ground.png', texture_scale=(10,10,10))
cube = Entity(model='cube',scale=(2,.5,2),collider='box', position=(0,-5,0), texture='spawn')
water = Entity(model='plane', scale=500, position=(0,-5.2, 0), texture='water', texture_scale=(65,65,65))
sun = Entity(model='sun', scale=1, position=(0,550,550))

#---------------enemy----------------

class Enemy(Entity):
    def __init__(self, position):
        super().__init__(
            model='enemy',
            scale=2,
            position=position
        )
        self.speed = 5
        self.min_distance = 10
        self.bullet_speed = 5
        self.shoot_interval = 2
        self.time_since_last_shot = 0

    def update(self):
        distance = (self.position - player.position).length()

        if distance < 1:
        	health_bar.value -= 20

        if distance < 1:
            enemies.remove(self)
            self.disable()

        throwable_distance = (self.position - spawned_object.position).length()

        self.time_since_last_shot += time.dt
        if self.time_since_last_shot >= self.shoot_interval:
            self.time_since_last_shot = 0
            self.shoot_bullet()

        if throwable_distance < 2:
            enemies.remove(self)
            self.disable()
            increase_score()
            

        self.look_at(player)

        if distance < self.min_distance:
                self.position -= self.forward * self.speed * time.dt
        else:
                self.position += self.forward * self.speed * time.dt

    def shoot_bullet(self):
        direction = (player.position - self.position).normalized()
        bullet = Bullet(position=self.position, direction=direction)
        self.bullet = Audio('sounds\\shoot.wav', volume=0.5, loop=False)

class Bullet(Entity):
    def __init__(self, position, direction):
        super().__init__(
            model='power_ball',
            texture='power_ball',
            scale=0.5,
            position=position
        )
        self.speed = 150
        self.direction = direction
        invoke(self.delete, delay=0.5)

    def update(self):
        self.position += self.direction * self.speed * time.dt

        distance = (self.position - player.position).length()

        tr = TrailRenderer(size=[1,1], segments=8, min_spacing=.05, fade_speed=0, parent=self, color=color.red)

        if distance < 1:
            health_bar.value -= 15
            self.disable()

    def delete(self):
        destroy(self)

spawn_points = [
    Vec3(50, 10, 50),
    Vec3(-50, 10, -50),
    Vec3(50, 10, -50),
    Vec3(-50, 10, 50)
]

enemies = []

def spawn_enemy():
    spawn_point = random.choice(spawn_points)
    enemy = Enemy(position=spawn_point)
    enemies.append(enemy)

for _ in range(4):
    spawn_enemy()

def spawn_interval():
    spawn_enemy()
    invoke(spawn_interval, delay=1)

spawn_interval()

#---------------shader---------------

sun = light(direction = (-0.7, -0.9, 0.5), resolution = 3072, player = player)
ambient = AmbientLight(color = Vec4(0.5, 0.55, 0.66, 0) * 1.3)

render.setShaderAuto()

Sky(texture='skybox')

#----------------end-----------------

app.run()