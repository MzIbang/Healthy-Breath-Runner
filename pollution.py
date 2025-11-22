from constants import (
    SCREEN_WIDTH, POLLUTION_COLOR,
    POLLUTION_MIN_RADIUS, POLLUTION_MAX_RADIUS,
    POLLUTION_MIN_SPEED, POLLUTION_MAX_SPEED,
    POLLUTION_MIN_ALPHA, POLLUTION_MAX_ALPHA,
    POLLUTION_SPAWN_MIN_Y, POLLUTION_SPAWN_MID_Y, POLLUTION_SPAWN_MAX_Y
)
import random
import math

class Pollution:
    def __init__(self, x, y, radius, speed, alpha):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.alpha = alpha
        # Timer untuk emit particle
        self.particle_emission_timer = 0
        self.particle_emission_interval = 0.1

    def update(self, dt):
        # Gerak ke kiri
        self.x -= self.speed * dt
        self.particle_emission_timer += dt

    def is_off_screen(self):
        # Cek apakah sudah keluar dari layar
        return self.x + self.radius < 0

    def should_emit_particle(self):
        # Cek apakah sudah waktunya emit particle
        if self.particle_emission_timer >= self.particle_emission_interval:
            self.particle_emission_timer = 0
            return True
        return False

    def draw(self, ctx):
        ctx.save()
        # Gambar lingkaran polusi dengan alpha transparency
        ctx.set_source_rgba(
            POLLUTION_COLOR[0] / 255.0,
            POLLUTION_COLOR[1] / 255.0,
            POLLUTION_COLOR[2] / 255.0,
            self.alpha
        )
        ctx.arc(self.x, self.y, self.radius, 0, 2 * math.pi)
        ctx.fill()
        # Gambar inner circle untuk efek depth
        ctx.set_source_rgba(0.3, 0.3, 0.3, self.alpha * 0.5)
        ctx.arc(self.x, self.y, self.radius * 0.6, 0, 2 * math.pi)
        ctx.fill()
        ctx.restore()

    @staticmethod
    def create_random():
        # Buat pollution dengan parameter random
        radius = random.uniform(POLLUTION_MIN_RADIUS, POLLUTION_MAX_RADIUS)
        speed = random.uniform(POLLUTION_MIN_SPEED, POLLUTION_MAX_SPEED)
        alpha = random.uniform(POLLUTION_MIN_ALPHA, POLLUTION_MAX_ALPHA)
        # Spawn di posisi random (50% low, 50% high)
        if random.random() < 0.5:
            y = random.uniform(POLLUTION_SPAWN_MID_Y, POLLUTION_SPAWN_MAX_Y)
        else:
            y = random.uniform(POLLUTION_SPAWN_MIN_Y, POLLUTION_SPAWN_MID_Y)
        x = SCREEN_WIDTH + radius
        return Pollution(x, y, radius, speed, alpha)
