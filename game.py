import pygame
import cairo
import random
import math
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GROUND_Y,
    BACKGROUND_COLOR, GROUND_COLOR, GROUND_DETAIL_COLOR, SKY_DETAIL_COLOR,
    HEALTH_BAR_COLOR, BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR,
    TITLE_COLOR, SCORE_COLOR,
    PARTICLE_DAMAGE, POLLUTION_SPAWN_INTERVAL_MIN, POLLUTION_SPAWN_INTERVAL_MAX,
    MASK_SPAWN_INTERVAL_MIN, MASK_SPAWN_INTERVAL_MAX,
    PARALLAX_GROUND_SPEED, PARALLAX_SKY_SPEED,
    PARALLAX_GROUND_PATTERN_WIDTH, PARALLAX_SKY_PATTERN_WIDTH
)
from player import Player
from pollution import Pollution
from particle import Particle
from mask import Mask

pygame.init()

# Game states - state-state game (menu, playing, game over)
MENU = 0
PLAYING = 1
GAME_OVER = 2

class Game:
    def __init__(self):
        # Inisialisasi state dan score
        self.state = MENU
        self.score = 0
        self.survival_time = 0.0
        self.best_score = 0
        self.reset_game()

    def reset_game(self):
        # Reset semua objek game ke kondisi awal
        self.player = Player(100, GROUND_Y - 60)
        self.pollution_objects = []
        self.particles = []
        self.masks = []
        # Timer untuk spawn pollution
        self.pollution_spawn_timer = 0
        self.pollution_spawn_interval = random.uniform(
            POLLUTION_SPAWN_INTERVAL_MIN,
            POLLUTION_SPAWN_INTERVAL_MAX
        )
        # Timer untuk spawn mask
        self.mask_spawn_timer = 0
        self.mask_spawn_interval = random.uniform(
            MASK_SPAWN_INTERVAL_MIN,
            MASK_SPAWN_INTERVAL_MAX
        )
        # Reset parallax scroll
        self.ground_scroll = 0.0
        self.sky_scroll = 0.0
        self.survival_time = 0.0
        self.score = 0

    def spawn_pollution(self):
        # Spawn pollution baru dari kanan
        pollution = Pollution.create_random()
        self.pollution_objects.append(pollution)

    def spawn_mask(self):
        # Spawn mask item baru dari kanan
        mask = Mask.create_random()
        self.masks.append(mask)

    def update(self, dt):
        # Kalau lagi di menu atau game over, cuma update parallax aja (lebih lambat)
        if self.state == MENU or self.state == GAME_OVER:
            self.ground_scroll += PARALLAX_GROUND_SPEED * dt * 0.3
            if self.ground_scroll >= PARALLAX_GROUND_PATTERN_WIDTH:
                self.ground_scroll -= PARALLAX_GROUND_PATTERN_WIDTH
            self.sky_scroll += PARALLAX_SKY_SPEED * dt * 0.3
            if self.sky_scroll >= PARALLAX_SKY_PATTERN_WIDTH:
                self.sky_scroll -= PARALLAX_SKY_PATTERN_WIDTH
            return
        # Update parallax scrolling saat playing
        self.ground_scroll += PARALLAX_GROUND_SPEED * dt
        if self.ground_scroll >= PARALLAX_GROUND_PATTERN_WIDTH:
            self.ground_scroll -= PARALLAX_GROUND_PATTERN_WIDTH
        self.sky_scroll += PARALLAX_SKY_SPEED * dt
        if self.sky_scroll >= PARALLAX_SKY_PATTERN_WIDTH:
            self.sky_scroll -= PARALLAX_SKY_PATTERN_WIDTH
        # Update score berdasarkan waktu bertahan (10 poin per detik)
        self.survival_time += dt
        self.score = int(self.survival_time * 10)
        self.player.update(dt)
        # Cek kalau player mati
        if self.player.health <= 0:
            if self.score > self.best_score:
                self.best_score = self.score
            self.state = GAME_OVER
        # Spawn pollution berdasarkan timer
        self.pollution_spawn_timer += dt
        if self.pollution_spawn_timer >= self.pollution_spawn_interval:
            self.spawn_pollution()
            self.pollution_spawn_timer = 0
            self.pollution_spawn_interval = random.uniform(
                POLLUTION_SPAWN_INTERVAL_MIN,
                POLLUTION_SPAWN_INTERVAL_MAX
            )
        # Spawn mask berdasarkan timer
        self.mask_spawn_timer += dt
        if self.mask_spawn_timer >= self.mask_spawn_interval:
            self.spawn_mask()
            self.mask_spawn_timer = 0
            self.mask_spawn_interval = random.uniform(
                MASK_SPAWN_INTERVAL_MIN,
                MASK_SPAWN_INTERVAL_MAX
            )
        # Dapatkan area spawn player untuk particle
        spawn_x, spawn_y, spawn_width, spawn_height = self.player.get_spawn_area()
        # Update semua pollution objects
        for pollution in self.pollution_objects[:]:
            pollution.update(dt)
            # Cek apakah pollution harus emit particle
            if pollution.should_emit_particle():
                # Hitung bounds pollution untuk collision check
                pollution_left = pollution.x - pollution.radius
                pollution_right = pollution.x + pollution.radius
                pollution_top = pollution.y - pollution.radius
                pollution_bottom = pollution.y + pollution.radius
                spawn_right = spawn_x + spawn_width
                spawn_bottom = spawn_y + spawn_height
                # Cek apakah pollution overlap dengan spawn area
                pollution_in_spawn_area = (
                    pollution_right >= spawn_x and
                    pollution_left <= spawn_right and
                    pollution_bottom >= spawn_y and
                    pollution_top <= spawn_bottom
                )
                # Kalau overlap, spawn particle di area player
                if pollution_in_spawn_area:
                    num_particles = random.randint(1, 3)
                    for _ in range(num_particles):
                        particle_x = random.uniform(spawn_x, spawn_x + spawn_width)
                        particle_y = random.uniform(spawn_y, spawn_y + spawn_height)
                        particle = Particle(particle_x, particle_y)
                        self.particles.append(particle)
            # Hapus pollution yang sudah keluar layar
            if pollution.is_off_screen():
                self.pollution_objects.remove(pollution)
        # Update semua particles dan cek collision dengan player
        for particle in self.particles[:]:
            particle.update(dt)
            # Cek collision dengan player
            if self.player.check_collision_with_particle(particle):
                if self.player.take_damage(PARTICLE_DAMAGE):
                    pass
            # Hapus particle yang sudah mati
            if not particle.is_alive():
                self.particles.remove(particle)
        # Update semua masks dan cek collision dengan player
        for mask in self.masks[:]:
            mask.update(dt)
            # Cek collision dengan player
            if mask.check_collision_with_player(self.player):
                result = self.player.collect_mask()
                self.masks.remove(mask)
            # Hapus mask yang sudah keluar layar
            if mask.is_off_screen():
                self.masks.remove(mask)

    def draw_background(self, ctx):
        # Gambar background sky dengan parallax
        ctx.save()
        ctx.set_source_rgb(
            BACKGROUND_COLOR[0] / 255.0,
            BACKGROUND_COLOR[1] / 255.0,
            BACKGROUND_COLOR[2] / 255.0
        )
        ctx.rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        ctx.fill()
        # Gambar awan dengan parallax scrolling
        ctx.set_source_rgba(
            SKY_DETAIL_COLOR[0] / 255.0,
            SKY_DETAIL_COLOR[1] / 255.0,
            SKY_DETAIL_COLOR[2] / 255.0,
            0.3
        )
        # Loop untuk pattern awan yang berulang
        pattern_start = -int(self.sky_scroll) % PARALLAX_SKY_PATTERN_WIDTH
        x = pattern_start - PARALLAX_SKY_PATTERN_WIDTH
        while x < SCREEN_WIDTH + PARALLAX_SKY_PATTERN_WIDTH:
            for i in range(3):
                cloud_x = x + i * (PARALLAX_SKY_PATTERN_WIDTH // 3) + 50
                cloud_y = 80 + i * 40
                ctx.arc(cloud_x, cloud_y, 60, 0, 2 * math.pi)
                ctx.fill()
                ctx.arc(cloud_x + 40, cloud_y, 50, 0, 2 * math.pi)
                ctx.fill()
                ctx.arc(cloud_x + 20, cloud_y - 30, 45, 0, 2 * math.pi)
                ctx.fill()
            x += PARALLAX_SKY_PATTERN_WIDTH
        ctx.restore()
        # Gambar ground dengan parallax
        ctx.save()
        ctx.set_source_rgb(
            GROUND_COLOR[0] / 255.0,
            GROUND_COLOR[1] / 255.0,
            GROUND_COLOR[2] / 255.0
        )
        ctx.rectangle(0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y)
        ctx.fill()
        # Gambar detail ground (rumput, batu) dengan parallax
        ctx.set_source_rgb(
            GROUND_DETAIL_COLOR[0] / 255.0,
            GROUND_DETAIL_COLOR[1] / 255.0,
            GROUND_DETAIL_COLOR[2] / 255.0
        )
        # Loop untuk pattern ground yang berulang
        pattern_start = -int(self.ground_scroll) % PARALLAX_GROUND_PATTERN_WIDTH
        x = pattern_start - PARALLAX_GROUND_PATTERN_WIDTH
        while x < SCREEN_WIDTH + PARALLAX_GROUND_PATTERN_WIDTH:
            # Gambar rumput
            for i in range(4):
                tuft_x = x + i * (PARALLAX_GROUND_PATTERN_WIDTH // 4) + 20
                tuft_width = 8
                tuft_height = 12
                ctx.rectangle(tuft_x, GROUND_Y - tuft_height, tuft_width, tuft_height)
                ctx.fill()
            # Gambar detail kecil (batu)
            for i in range(3):
                detail_x = x + i * (PARALLAX_GROUND_PATTERN_WIDTH // 3) + 30
                detail_y = GROUND_Y - 5
                ctx.arc(detail_x, detail_y, 3, 0, 2 * math.pi)
                ctx.fill()
            x += PARALLAX_GROUND_PATTERN_WIDTH
        # Gambar garis horizon
        ctx.set_source_rgb(0.2, 0.5, 0.2)
        ctx.set_line_width(2)
        ctx.move_to(0, GROUND_Y)
        ctx.line_to(SCREEN_WIDTH, GROUND_Y)
        ctx.stroke()
        ctx.restore()

    def draw_hud(self, ctx):
        # Gambar health bar border
        ctx.save()
        ctx.set_source_rgb(0.2, 0.2, 0.2)
        ctx.set_line_width(2)
        ctx.rectangle(20, 20, 200, 30)
        ctx.stroke()
        # Gambar health bar background
        ctx.set_source_rgb(0.4, 0.4, 0.4)
        ctx.rectangle(22, 22, 196, 26)
        ctx.fill()
        # Hitung dan gambar health bar fill
        health_percentage = self.player.health / self.player.max_health
        health_width = int(196 * health_percentage)
        ctx.set_source_rgb(
            HEALTH_BAR_COLOR[0] / 255.0,
            HEALTH_BAR_COLOR[1] / 255.0,
            HEALTH_BAR_COLOR[2] / 255.0
        )
        if health_width > 0:
            ctx.rectangle(22, 22, health_width, 26)
            ctx.fill()
        ctx.restore()

    def draw_button(self, ctx, x, y, width, height, text, hover=False):
        # Gambar button background (warna beda kalau hover)
        ctx.save()
        color = BUTTON_HOVER_COLOR if hover else BUTTON_COLOR
        ctx.set_source_rgb(
            color[0] / 255.0,
            color[1] / 255.0,
            color[2] / 255.0
        )
        ctx.rectangle(x, y, width, height)
        ctx.fill()
        # Gambar border button
        ctx.set_source_rgb(0.2, 0.2, 0.2)
        ctx.set_line_width(3)
        ctx.rectangle(x, y, width, height)
        ctx.stroke()
        ctx.restore()
        # Simpan info button untuk text rendering nanti
        if not hasattr(self, '_button_texts'):
            self._button_texts = []
        self._button_texts.append((x, y, width, height, text))

    def check_button_click(self, mouse_x, mouse_y, button_x, button_y, button_width, button_height):
        # Cek apakah mouse click ada di dalam bounds button
        return (button_x <= mouse_x <= button_x + button_width and
                button_y <= mouse_y <= button_y + button_height)

    def draw_menu(self, ctx, mouse_x, mouse_y):
        # Gambar background menu
        self.draw_background(ctx)
        # Title game
        title_text = "Healthy Breath Runner"
        self._text_overlays.append((title_text, SCREEN_WIDTH / 2, 150, 48, TITLE_COLOR, True))
        # Button START
        button_x = SCREEN_WIDTH / 2 - 150
        button_y = SCREEN_HEIGHT / 2
        button_width = 300
        button_height = 60
        hover = self.check_button_click(mouse_x, mouse_y, button_x, button_y, button_width, button_height)
        self.draw_button(ctx, button_x, button_y, button_width, button_height, "START", hover)
        # Instruksi
        inst_text = "Press SPACE to jump"
        self._text_overlays.append((inst_text, SCREEN_WIDTH / 2, button_y + button_height + 50, 20, (77, 77, 77), False))

    def draw_game_over(self, ctx, mouse_x, mouse_y):
        # Gambar background game over
        self.draw_background(ctx)
        # Overlay semi-transparan untuk efek gelap
        ctx.save()
        ctx.set_source_rgba(0, 0, 0, 0.6)
        ctx.rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        ctx.fill()
        ctx.restore()
        # Title GAME OVER
        title_text = "GAME OVER"
        self._text_overlays.append((title_text, SCREEN_WIDTH / 2, 150, 56, TITLE_COLOR, True))
        # Score saat ini
        score_text = f"Score: {self.score}"
        self._text_overlays.append((score_text, SCREEN_WIDTH / 2, 220, 32, SCORE_COLOR, True))
        # Best score kalau ada
        if self.best_score > 0:
            best_text = f"Best: {self.best_score}"
            self._text_overlays.append((best_text, SCREEN_WIDTH / 2, 260, 32, SCORE_COLOR, True))
        # Button RESPAWN
        button_x = SCREEN_WIDTH / 2 - 150
        button_y = SCREEN_HEIGHT / 2 + 50
        button_width = 300
        button_height = 60
        hover = self.check_button_click(mouse_x, mouse_y, button_x, button_y, button_width, button_height)
        self.draw_button(ctx, button_x, button_y, button_width, button_height, "RESPAWN", hover)

    def draw(self, ctx, mouse_x=0, mouse_y=0):
        # Clear semua overlay di awal setiap draw call
        self._text_overlays = []
        self._button_texts = []
        # Gambar sesuai state
        if self.state == MENU:
            self.draw_menu(ctx, mouse_x, mouse_y)
        elif self.state == GAME_OVER:
            self.draw_game_over(ctx, mouse_x, mouse_y)
        else:  # PLAYING
            self.draw_background(ctx)
            # Gambar semua particles
            for particle in self.particles:
                particle.draw(ctx)
            # Gambar semua pollution objects
            for pollution in self.pollution_objects:
                pollution.draw(ctx)
            # Gambar semua masks
            for mask in self.masks:
                mask.draw(ctx)
            # Gambar player
            self.player.draw(ctx)
            # Gambar HUD
            self.draw_hud(ctx)
            # Score text overlay (cuma muncul saat playing)
            score_text = f"Score: {self.score}"
            self._text_overlays.append((score_text, SCREEN_WIDTH - 150, 40, 24, SCORE_COLOR, True))

def cairo_surface_to_pygame(cairo_surface):
    # Convert Cairo surface ke PyGame surface untuk display
    buf = cairo_surface.get_data()
    width = cairo_surface.get_width()
    height = cairo_surface.get_height()
    pygame_surface = pygame.image.frombuffer(buf, (width, height), "BGRA")
    return pygame_surface

def main():
    # Setup PyGame window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Healthy Breath Runner")
    game = Game()
    # Inisialisasi list untuk text overlay
    game._text_overlays = []
    game._button_texts = []
    # Cache fonts untuk performance (bikin sekali, dipake berkali-kali)
    font_cache = {}
    def get_font(size):
        if size not in font_cache:
            font_cache[size] = pygame.font.Font(None, size)
        return font_cache[size]
    # Main game loop
    running = True
    clock = pygame.time.Clock()
    mouse_x, mouse_y = 0, 0
    while running:
        dt = clock.tick(FPS) / 1000.0
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game.state == PLAYING:
                        game.player.jump()
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = event.pos
                    # Cek klik button START di menu
                    if game.state == MENU:
                        button_x = SCREEN_WIDTH / 2 - 150
                        button_y = SCREEN_HEIGHT / 2
                        button_width = 300
                        button_height = 60
                        if game.check_button_click(mouse_x, mouse_y, button_x, button_y, button_width, button_height):
                            game.state = PLAYING
                            game.reset_game()
                    # Cek klik button RESPAWN di game over
                    elif game.state == GAME_OVER:
                        button_x = SCREEN_WIDTH / 2 - 150
                        button_y = SCREEN_HEIGHT / 2 + 50
                        button_width = 300
                        button_height = 60
                        if game.check_button_click(mouse_x, mouse_y, button_x, button_y, button_width, button_height):
                            game.state = PLAYING
                            game.reset_game()
        # Update game
        game.update(dt)
        # Buat Cairo surface untuk drawing
        cairo_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, SCREEN_WIDTH, SCREEN_HEIGHT)
        ctx = cairo.Context(cairo_surface)
        # Draw semua game elements dengan Cairo
        game.draw(ctx, mouse_x, mouse_y)
        cairo_surface.flush()
        # Convert ke PyGame surface dan blit ke screen
        draw_surface = cairo_surface_to_pygame(cairo_surface)
        screen.blit(draw_surface, (0, 0))
        # Render text overlays dengan PyGame (pakai cached fonts)
        if game._text_overlays:
            for text, x, y, size, color, bold in game._text_overlays:
                try:
                    font = get_font(size)
                    text_surface = font.render(text, True, color)
                    text_rect = text_surface.get_rect(center=(x, y))
                    screen.blit(text_surface, text_rect)
                except:
                    pass
        # Render button texts (pakai cached font)
        if game._button_texts:
            try:
                button_font = get_font(28)
                for x, y, width, height, text in game._button_texts:
                    text_surface = button_font.render(text, True, BUTTON_TEXT_COLOR)
                    text_rect = text_surface.get_rect(center=(x + width/2, y + height/2))
                    screen.blit(text_surface, text_rect)
            except:
                pass
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
