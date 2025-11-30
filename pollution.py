from constants import (
    SCREEN_WIDTH, POLLUTION_COLOR, POLLUTION_DETAIL_COLOR,
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
        
        # Animasi
        self.anim_timer = random.uniform(0, 10.0)
        
        # Membuat bentuk awan acak
        self.num_puffs = random.randint(5, 7)
        self.puffs = []
        for i in range(self.num_puffs):
            angle = (i / self.num_puffs) * 2 * math.pi
            # Acak jarak dan ukuran setiap gumpalan agar terlihat alami
            dist = random.uniform(0.4, 0.7) * self.radius
            size = random.uniform(0.5, 0.8) * self.radius
            self.puffs.append({
                'angle': angle,
                'dist': dist,
                'size': size,
                'offset_speed': random.uniform(2, 4) # Kecepatan goyang tiap gumpalan
            })

    def update(self, dt):
        self.x -= self.speed * dt
        self.anim_timer += dt

    def is_off_screen(self):
        return self.x + self.radius + 30 < 0

    def draw(self, ctx):
        ctx.save()
        ctx.translate(self.x, self.y)
        
        # Rotasi sedikit kiri-kanan agar terlihat melayang
        hover_rot = math.sin(self.anim_timer * 2) * 0.1
        ctx.rotate(hover_rot)
        
        # Warna Dasar Asap
        ctx.set_source_rgba(
            POLLUTION_COLOR[0] / 255.0,
            POLLUTION_COLOR[1] / 255.0,
            POLLUTION_COLOR[2] / 255.0,
            self.alpha
        )
        
        # 1. Gambar Inti Awan
        ctx.arc(0, 0, self.radius * 0.7, 0, 2 * math.pi)
        ctx.fill()
        
        # 2. Gambar Gumpalan-gumpalan (Puffs) di sekeliling
        for puff in self.puffs:
            # Gumpalan bergerak sedikit (breathing effect)
            move = math.sin(self.anim_timer * puff['offset_speed']) * 2
            
            px = math.cos(puff['angle']) * (puff['dist'] + move)
            py = math.sin(puff['angle']) * (puff['dist'] + move)
            
            ctx.arc(px, py, puff['size'], 0, 2 * math.pi)
            ctx.fill()
            
        # 3. Wajah Lucu (Cute Face)
        # Agar terlihat kontras, wajah warna putih/terang
        ctx.set_source_rgba(1, 1, 1, 0.9)
        
        # Mata Kiri & Kanan
        eye_y = -self.radius * 0.1
        eye_x_offset = self.radius * 0.25
        eye_size = self.radius * 0.15
        
        # Kedip (Blinking) setiap beberapa detik
        is_blinking = math.sin(self.anim_timer * 3) > 0.95
        
        if is_blinking:
            # Mata tertutup (garis)
            ctx.set_line_width(2)
            ctx.move_to(-eye_x_offset - eye_size, eye_y)
            ctx.line_to(-eye_x_offset + eye_size, eye_y)
            ctx.move_to(eye_x_offset - eye_size, eye_y)
            ctx.line_to(eye_x_offset + eye_size, eye_y)
            ctx.stroke()
        else:
            # Mata terbuka (bulat)
            ctx.arc(-eye_x_offset, eye_y, eye_size, 0, 2 * math.pi)
            ctx.fill()
            ctx.arc(eye_x_offset, eye_y, eye_size, 0, 2 * math.pi)
            ctx.fill()
            
            # Pupil (Hitam)
            ctx.set_source_rgba(0.2, 0.2, 0.2, 1.0)
            ctx.arc(-eye_x_offset, eye_y, eye_size * 0.5, 0, 2 * math.pi)
            ctx.fill()
            ctx.arc(eye_x_offset, eye_y, eye_size * 0.5, 0, 2 * math.pi)
            ctx.fill()

        # Mulut Kecil
        ctx.set_source_rgba(1, 1, 1, 0.9)
        ctx.set_line_width(2)
        ctx.set_line_cap(1) # Round
        
        # Mulut senyum kecil atau garis 'o'
        mouth_y = self.radius * 0.2
        ctx.new_path()
        ctx.arc(0, mouth_y, self.radius * 0.15, 0.1 * math.pi, 0.9 * math.pi)
        ctx.stroke()

        ctx.restore()

    @staticmethod
    def create_random():
        radius = random.uniform(POLLUTION_MIN_RADIUS, POLLUTION_MAX_RADIUS)
        speed = random.uniform(POLLUTION_MIN_SPEED, POLLUTION_MAX_SPEED)
        alpha = random.uniform(POLLUTION_MIN_ALPHA, POLLUTION_MAX_ALPHA)
        
        if random.random() < 0.5:
            y = random.uniform(POLLUTION_SPAWN_MID_Y, POLLUTION_SPAWN_MAX_Y)
        else:
            y = random.uniform(POLLUTION_SPAWN_MIN_Y, POLLUTION_SPAWN_MID_Y)
            
        x = SCREEN_WIDTH + radius + 50
        return Pollution(x, y, radius, speed, alpha)