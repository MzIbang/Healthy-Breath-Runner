import math
import random
from constants import (
    SCREEN_WIDTH, MASK_COLOR, MASK_STRAP_COLOR,
    MASK_SIZE, MASK_SPAWN_MIN_Y, MASK_SPAWN_MAX_Y,
    POLLUTION_MIN_SPEED, POLLUTION_MAX_SPEED
)

class Mask:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = MASK_SIZE
        self.speed = random.uniform(POLLUTION_MIN_SPEED, POLLUTION_MAX_SPEED)
        # Variabel untuk animasi rotasi dan floating
        self.rotation = 0.0
        self.float_offset = 0.0
        self.float_time = random.uniform(0, 2 * math.pi)

    def update(self, dt):
        # Gerak ke kiri seperti pollution
        self.x -= self.speed * dt
        # Rotasi untuk efek visual
        self.rotation += dt * 2
        # Animasi floating (naik turun)
        self.float_time += dt * 3
        self.float_offset = math.sin(self.float_time) * 3

    def is_off_screen(self):
        # Cek apakah sudah keluar dari layar
        return self.x + self.radius < 0

    def check_collision_with_player(self, player):
        # Hitung jarak antara mask dengan player center
        player_center_x = player.x + player.width / 2
        player_center_y = player.y + player.height / 2
        dx = self.x - player_center_x
        dy = (self.y + self.float_offset) - player_center_y
        distance = math.sqrt(dx * dx + dy * dy)
        # Collision kalau jarak kurang dari radius mask + player radius
        player_radius = max(player.width, player.height) / 2
        return distance < (self.radius + player_radius)

    def draw(self, ctx):
        ctx.save()
        # Apply floating offset
        draw_y = self.y + self.float_offset
        # Apply rotation transform
        ctx.translate(self.x, draw_y)
        ctx.rotate(self.rotation)
        # Gambar body mask
        ctx.set_source_rgb(
            MASK_COLOR[0] / 255.0,
            MASK_COLOR[1] / 255.0,
            MASK_COLOR[2] / 255.0
        )
        mask_width = self.radius * 1.5
        mask_height = self.radius * 1.2
        ctx.rectangle(-mask_width/2, -mask_height/2, mask_width, mask_height)
        ctx.fill()
        # Gambar tali mask
        ctx.set_source_rgb(
            MASK_STRAP_COLOR[0] / 255.0,
            MASK_STRAP_COLOR[1] / 255.0,
            MASK_STRAP_COLOR[2] / 255.0
        )
        ctx.set_line_width(3)
        # Tali atas
        ctx.move_to(-mask_width/2, -mask_height/2 - 2)
        ctx.line_to(mask_width/2, -mask_height/2 - 2)
        ctx.stroke()
        # Tali bawah
        ctx.move_to(-mask_width/2, mask_height/2 + 2)
        ctx.line_to(mask_width/2, mask_height/2 + 2)
        ctx.stroke()
        # Detail garis vertikal dan circle di tengah
        ctx.set_line_width(2)
        ctx.move_to(0, -mask_height/2)
        ctx.line_to(0, mask_height/2)
        ctx.stroke()
        ctx.arc(0, 0, 3, 0, 2 * math.pi)
        ctx.fill()
        ctx.restore()
        # Gambar efek glow
        ctx.save()
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.3)
        ctx.arc(self.x, draw_y, self.radius + 5, 0, 2 * math.pi)
        ctx.fill()
        ctx.restore()

    @staticmethod
    def create_random():
        y = random.uniform(MASK_SPAWN_MIN_Y, MASK_SPAWN_MAX_Y)
        x = SCREEN_WIDTH + MASK_SIZE
        return Mask(x, y)
