import math
from constants import (
    GROUND_Y, BLOCK_SIZE, DAMAGE_COOLDOWN, PARTICLE_DAMAGE,
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_GRAVITY, PLAYER_JUMP_STRENGTH,
    PLAYER_COLOR, MASK_HEALTH_RESTORE, MASK_PROTECTION_DURATION
)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.velocity_y = 0
        self.gravity = PLAYER_GRAVITY
        self.jump_strength = PLAYER_JUMP_STRENGTH
        self.on_ground = True
        # Variabel untuk animasi running
        self.animation_offset = 0
        self.animation_vertical_offset = 0
        self.animation_time = 0
        self.leg_animation_phase = 0
        # Sistem health dan protection
        self.max_health = 100
        self.health = self.max_health
        self.damage_cooldown = 0
        self.protection_timer = 0
        self.is_protected = False

    def update(self, dt):
        # Terapkan gravity ke velocity
        self.velocity_y += self.gravity * dt
        # Update posisi berdasarkan velocity
        self.y += self.velocity_y * dt
        # Cek collision dengan ground
        ground_level = GROUND_Y - self.height
        if self.y >= ground_level:
            self.y = ground_level
            self.velocity_y = 0
            self.on_ground = True
        else:
            self.on_ground = False
        # Animasi running cuma jalan kalau di ground
        if self.on_ground:
            self.animation_time += dt * 12
            self.animation_offset = math.sin(self.animation_time) * 2
            self.animation_vertical_offset = abs(math.sin(self.animation_time * 2)) * 2
            self.leg_animation_phase = (self.animation_time * 2) % (2 * math.pi)
        else:
            self.animation_vertical_offset = 0
            self.leg_animation_phase = 0
        # Update cooldown damage
        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt
        # Update timer protection dari mask
        if self.protection_timer > 0:
            self.protection_timer -= dt
            self.is_protected = True
        else:
            self.is_protected = False

    def take_damage(self, amount):
        # Kalau lagi protected, gak bisa kena damage
        if self.is_protected:
            return False
        # Cek cooldown dulu sebelum nerima damage
        if self.damage_cooldown <= 0:
            self.health -= amount
            self.health = max(0, self.health)
            self.damage_cooldown = DAMAGE_COOLDOWN
            return True
        return False

    def collect_mask(self):
        # Kalau health belum penuh, restore health
        if self.health < self.max_health:
            self.health += MASK_HEALTH_RESTORE
            self.health = min(self.max_health, self.health)
            return "health"
        else:
            # Kalau health penuh, kasih protection
            self.protection_timer = MASK_PROTECTION_DURATION
            self.is_protected = True
            return "protection"

    def check_collision_with_particle(self, particle):
        # Hitung collision antara player rectangle dengan particle circle
        player_left = self.x
        player_right = self.x + self.width
        player_top = self.y
        player_bottom = self.y + self.height
        # Cari titik terdekat di rectangle ke particle
        closest_x = max(player_left, min(particle.x, player_right))
        closest_y = max(player_top, min(particle.y, player_bottom))
        # Hitung jarak dari particle ke titik terdekat
        dx_closest = particle.x - closest_x
        dy_closest = particle.y - closest_y
        distance_to_closest = math.sqrt(dx_closest * dx_closest + dy_closest * dy_closest)
        # Collision kalau jarak kurang dari radius particle
        return distance_to_closest < particle.radius

    def jump(self):
        # Lompat cuma bisa kalau lagi di ground
        if self.on_ground:
            self.velocity_y = -self.jump_strength
            self.on_ground = False

    def draw(self, ctx):
        ctx.save()
        # Apply offset animasi untuk efek running
        draw_x = self.x + self.animation_offset
        draw_y = self.y - self.animation_vertical_offset
        # Gambar body player
        ctx.set_source_rgb(
            PLAYER_COLOR[0] / 255.0,
            PLAYER_COLOR[1] / 255.0,
            PLAYER_COLOR[2] / 255.0
        )
        ctx.rectangle(draw_x, draw_y, self.width, self.height)
        ctx.fill()
        # Gambar mata
        ctx.set_source_rgb(0, 0, 0)
        eye_size = 4
        eye_y_offset = self.animation_vertical_offset * 0.5
        ctx.arc(draw_x + 12, draw_y + 15 + eye_y_offset, eye_size, 0, 2 * math.pi)
        ctx.fill()
        ctx.arc(draw_x + 28, draw_y + 15 + eye_y_offset, eye_size, 0, 2 * math.pi)
        ctx.fill()
        # Gambar kaki yang animasi kalau lagi di ground
        if self.on_ground:
            ctx.set_source_rgb(
                PLAYER_COLOR[0] / 255.0 * 0.8,
                PLAYER_COLOR[1] / 255.0 * 0.8,
                PLAYER_COLOR[2] / 255.0 * 0.8
            )
            leg_width = 6
            leg_height = 12
            # Kaki kiri
            left_leg_x = draw_x + 8
            left_leg_y = draw_y + self.height
            left_leg_offset = math.sin(self.leg_animation_phase) * 4
            ctx.rectangle(left_leg_x, left_leg_y + left_leg_offset, leg_width, leg_height)
            ctx.fill()
            # Kaki kanan (phase berlawanan)
            right_leg_x = draw_x + 26
            right_leg_y = draw_y + self.height
            right_leg_offset = math.sin(self.leg_animation_phase + math.pi) * 4
            ctx.rectangle(right_leg_x, right_leg_y + right_leg_offset, leg_width, leg_height)
            ctx.fill()
        # Gambar efek glow protection kalau lagi protected
        if self.is_protected:
            from constants import PROTECTION_COLOR
            ctx.save()
            ctx.set_source_rgba(
                PROTECTION_COLOR[0] / 255.0,
                PROTECTION_COLOR[1] / 255.0,
                PROTECTION_COLOR[2] / 255.0,
                0.4
            )
            glow_radius = max(self.width, self.height) / 2 + 5
            ctx.arc(draw_x + self.width/2, draw_y + self.height/2, glow_radius, 0, 2 * math.pi)
            ctx.fill()
            ctx.restore()
        ctx.restore()

    def get_spawn_area(self):
        # Return area spawn untuk particle (1 block lebar, 3 block tinggi)
        spawn_width = BLOCK_SIZE
        spawn_height = 3 * BLOCK_SIZE
        # Center area spawn di player
        spawn_x = self.x + (self.width - spawn_width) / 2
        spawn_y = self.y + self.height - spawn_height
        return (spawn_x, spawn_y, spawn_width, spawn_height)
