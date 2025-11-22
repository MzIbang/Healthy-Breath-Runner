import random
import math
from constants import PARTICLE_COLOR

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # Random size dan velocity untuk variasi
        self.radius = random.uniform(2, 5)
        self.velocity_x = random.uniform(-20, 20)
        self.velocity_y = random.uniform(-30, -10)
        # Lifetime untuk efek fade out
        self.max_lifetime = random.uniform(0.5, 1.5)
        self.lifetime = self.max_lifetime

    def update(self, dt):
        # Update posisi berdasarkan velocity
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.lifetime -= dt
        # Tambah upward drift untuk efek asap
        self.velocity_y -= 20 * dt

    def is_alive(self):
        # Cek apakah particle masih hidup
        return self.lifetime > 0

    def get_alpha(self):
        # Return alpha berdasarkan sisa lifetime (untuk fade out)
        return max(0, self.lifetime / self.max_lifetime)

    def draw(self, ctx):
        ctx.save()
        # Gambar particle dengan alpha yang fade out
        alpha = self.get_alpha()
        ctx.set_source_rgba(
            PARTICLE_COLOR[0] / 255.0,
            PARTICLE_COLOR[1] / 255.0,
            PARTICLE_COLOR[2] / 255.0,
            alpha
        )
        ctx.arc(self.x, self.y, self.radius, 0, 2 * math.pi)
        ctx.fill()
        ctx.restore()
