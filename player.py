import math
import cairo
from constants import (
    GROUND_Y, BLOCK_SIZE, DAMAGE_COOLDOWN, PARTICLE_DAMAGE,
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_DUCK_HEIGHT,
    PLAYER_GRAVITY, PLAYER_JUMP_STRENGTH,
    PLAYER_COLOR, MASK_HEALTH_RESTORE, MASK_PROTECTION_DURATION,
    PLAYER_SKIN_COLOR, PLAYER_HEADBAND_COLOR
)

class Player:
    def __init__(self, x, y):
        # Inisialisasi atribut player (posisi, ukuran, physics, animasi, health)
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.original_height = PLAYER_HEIGHT
        self.height = PLAYER_HEIGHT
        
        self.velocity_y = 0
        self.gravity = PLAYER_GRAVITY
        self.jump_strength = PLAYER_JUMP_STRENGTH
        self.on_ground = True
        self.is_ducking = False
        
        self.animation_offset = 0
        self.animation_vertical_offset = 0
        self.animation_time = 0
        self.leg_animation_phase = 0
        
        self.max_health = 100
        self.health = self.max_health
        self.damage_cooldown = 0
        self.protection_timer = 0
        self.is_protected = False

    def update(self, dt):
        # Update posisi player berdasarkan gravitasi
        self.velocity_y += self.gravity * dt
        self.y += self.velocity_y * dt
        
        # Cek apakah player menyentuh tanah
        ground_level = GROUND_Y - self.height
        if self.y >= ground_level:
            self.y = ground_level
            self.velocity_y = 0
            self.on_ground = True
        else:
            self.on_ground = False
            
        # Update animasi player
        if self.on_ground:
            speed_multiplier = 12 if not self.is_ducking else 18
            self.animation_time += dt * speed_multiplier
            
            self.animation_offset = math.sin(self.animation_time) * 2
            self.animation_vertical_offset = abs(math.sin(self.animation_time * 2)) * 2
            self.leg_animation_phase = (self.animation_time * 2) % (2 * math.pi)
        else:
            self.animation_vertical_offset = 0
            self.leg_animation_phase = 0
            
        # Kurangi cooldown damage & timer proteksi
        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt
            
        if self.protection_timer > 0:
            self.protection_timer -= dt
            self.is_protected = True
        else:
            self.is_protected = False

    def duck(self):
        # Aktifkan mode jongkok
        if self.on_ground and not self.is_ducking:
            self.is_ducking = True
            self.height = PLAYER_DUCK_HEIGHT
            self.y = GROUND_Y - self.height

    def unduck(self):
        # Kembalikan tinggi saat berhenti jongkok
        if self.is_ducking:
            self.is_ducking = False
            self.height = self.original_height
            self.y = GROUND_Y - self.height

    def take_damage(self, amount):
        # Ambil damage jika tidak terlindungi dan cooldown habis
        if self.is_protected:
            return False
        if self.damage_cooldown <= 0:
            self.health -= amount
            self.health = max(0, self.health)
            self.damage_cooldown = DAMAGE_COOLDOWN
            return True
        return False

    def collect_mask(self):
        # Mask menambah health atau memberi proteksi
        if self.health < self.max_health:
            self.health += MASK_HEALTH_RESTORE
            self.health = min(self.max_health, self.health)
            return "health"
        else:
            self.protection_timer = MASK_PROTECTION_DURATION
            self.is_protected = True
            return "protection"

    def check_collision_with_particle(self, particle):
        # Hitbox sederhana antara player dan partikel
        player_left = self.x
        player_right = self.x + self.width
        player_top = self.y
        player_bottom = self.y + self.height
        
        closest_x = max(player_left, min(particle.x, player_right))
        closest_y = max(player_top, min(particle.y, player_bottom))
        
        dx_closest = particle.x - closest_x
        dy_closest = particle.y - closest_y
        distance_to_closest = math.sqrt(dx_closest * dx_closest + dy_closest * dy_closest)
        
        return distance_to_closest < particle.radius

    def jump(self):
        # Lompat hanya saat di tanah
        if self.on_ground:
            if self.is_ducking:
                self.unduck()
            self.velocity_y = -self.jump_strength
            self.on_ground = False

    def draw(self, ctx):
        # Menggambar player: tubuh, kepala, animasi, efek proteksi
        ctx.save()
        draw_x = self.x + self.animation_offset
        draw_y = self.y - self.animation_vertical_offset
        
        # Ekor ikat kepala
        ctx.set_source_rgb(
            PLAYER_HEADBAND_COLOR[0] / 255.0,
            PLAYER_HEADBAND_COLOR[1] / 255.0,
            PLAYER_HEADBAND_COLOR[2] / 255.0
        )
        ctx.set_line_width(4)
        
        headband_base_y = draw_y + (15 if not self.is_ducking else 10)
        tail_y_offset = math.sin(self.animation_time * 1.5) * 5
        
        ctx.move_to(draw_x + 5, headband_base_y)
        ctx.curve_to(
            draw_x - 10, headband_base_y, 
            draw_x - 15, headband_base_y - 5 + tail_y_offset, 
            draw_x - 25, headband_base_y + 5 + tail_y_offset
        )
        ctx.stroke()

        # Kaki
        if self.on_ground:
            ctx.set_source_rgb(0.2, 0.2, 0.2)
            leg_height = 18 if not self.is_ducking else 12
            leg_width = 8
            
            left_leg_x = draw_x + 10
            left_leg_y = draw_y + self.height - (15 if not self.is_ducking else 10)
            left_leg_offset = math.sin(self.leg_animation_phase) * 6
            
            right_leg_x = draw_x + self.width - 18
            right_leg_y = draw_y + self.height - (15 if not self.is_ducking else 10)
            right_leg_offset = math.sin(self.leg_animation_phase + math.pi) * 6

            ctx.set_line_width(leg_width)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            
            ctx.move_to(left_leg_x, left_leg_y)
            ctx.line_to(left_leg_x - left_leg_offset, left_leg_y + leg_height)
            ctx.stroke()
            
            ctx.move_to(right_leg_x, right_leg_y)
            ctx.line_to(right_leg_x - right_leg_offset, right_leg_y + leg_height)
            ctx.stroke()

        # Badan (rounded rectangle)
        ctx.set_source_rgb(
            PLAYER_COLOR[0] / 255.0,
            PLAYER_COLOR[1] / 255.0,
            PLAYER_COLOR[2] / 255.0
        )
        radius = 10
        ctx.new_sub_path()
        body_top_offset = 15 if not self.is_ducking else 5
        
        ctx.arc(draw_x + radius, draw_y + radius + body_top_offset, radius, math.pi, 1.5 * math.pi)
        ctx.arc(draw_x + self.width - radius, draw_y + radius + body_top_offset, radius, 1.5 * math.pi, 0)
        ctx.arc(draw_x + self.width - radius, draw_y + self.height - radius, radius, 0, 0.5 * math.pi)
        ctx.arc(draw_x + radius, draw_y + self.height - radius, radius, 0.5 * math.pi, math.pi)
        ctx.close_path()
        ctx.fill()

        # Kepala
        ctx.set_source_rgb(
            PLAYER_SKIN_COLOR[0] / 255.0,
            PLAYER_SKIN_COLOR[1] / 255.0,
            PLAYER_SKIN_COLOR[2] / 255.0
        )
        head_radius = 14
        center_head_x = draw_x + self.width / 2
        center_head_y = draw_y + (12 if not self.is_ducking else 8)
        
        ctx.arc(center_head_x, center_head_y, head_radius, 0, 2 * math.pi)
        ctx.fill()
        
        # Ikat kepala depan
        ctx.set_source_rgb(
            PLAYER_HEADBAND_COLOR[0] / 255.0,
            PLAYER_HEADBAND_COLOR[1] / 255.0,
            PLAYER_HEADBAND_COLOR[2] / 255.0
        )
        ctx.set_line_width(4)
        ctx.move_to(center_head_x - head_radius + 1, center_head_y - 5)
        ctx.line_to(center_head_x + head_radius - 1, center_head_y - 5)
        ctx.stroke()

        # Mata
        ctx.set_source_rgb(1, 1, 1)
        ctx.arc(center_head_x + 6, center_head_y, 4, 0, 2 * math.pi)
        ctx.fill()
        ctx.set_source_rgb(0, 0, 0)
        ctx.arc(center_head_x + 7, center_head_y, 1.5, 0, 2 * math.pi)
        ctx.fill()

        # Efek proteksi (glow)
        if self.is_protected:
            from constants import PROTECTION_COLOR
            ctx.save()
            ctx.set_source_rgba(
                PROTECTION_COLOR[0] / 255.0,
                PROTECTION_COLOR[1] / 255.0,
                PROTECTION_COLOR[2] / 255.0,
                0.3
            )
            glow_radius = max(self.width, self.height) / 2 + 10
            ctx.arc(draw_x + self.width/2, draw_y + self.height/2, glow_radius, 0, 2 * math.pi)
            ctx.fill()
            ctx.set_line_width(2)
            ctx.set_source_rgba(
                PROTECTION_COLOR[0] / 255.0,
                PROTECTION_COLOR[1] / 255.0,
                PROTECTION_COLOR[2] / 255.0,
                0.8
            )
            ctx.stroke()
            ctx.restore()
            
        ctx.restore()

    def get_spawn_area(self):
        # Area spawn objek di sekitar player
        spawn_width = BLOCK_SIZE
        spawn_height = 3 * BLOCK_SIZE
        spawn_x = self.x + (self.width - spawn_width) / 2
        spawn_y = self.y + self.height - spawn_height
        return (spawn_x, spawn_y, spawn_width, spawn_height)
