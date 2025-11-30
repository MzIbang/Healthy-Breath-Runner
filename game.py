import pygame
import cairo
import random
import math
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GROUND_Y,
    GROUND_COLOR, GROUND_DETAIL_COLOR,
    HEALTH_BAR_COLOR, BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR,
    TITLE_COLOR, SCORE_COLOR, SHADOW_COLOR,
    PARTICLE_DAMAGE, POLLUTION_SPAWN_INTERVAL_MIN, POLLUTION_SPAWN_INTERVAL_MAX,
    MASK_SPAWN_INTERVAL_MIN, MASK_SPAWN_INTERVAL_MAX,
    PARALLAX_GROUND_SPEED, PARALLAX_SKY_SPEED, PARALLAX_CITY_SPEED,
    PARALLAX_GROUND_PATTERN_WIDTH, PARALLAX_SKY_PATTERN_WIDTH, PARALLAX_CITY_PATTERN_WIDTH,
    SKY_TOP_COLOR, SKY_BOTTOM_COLOR, CITY_COLOR, CITY_WINDOW_COLOR
)
from player import Player
from pollution import Pollution
from particle import Particle
from mask import Mask

pygame.init()

MENU = 0
PLAYING = 1
GAME_OVER = 2

class Game:
    def __init__(self):
        self.state = MENU
        self.score = 0
        self.survival_time = 0.0
        self.best_score = 0
        self.menu_anim_timer = 0.0
        self.reset_game()

    def reset_game(self):
        self.player = Player(100, GROUND_Y - 60)
        self.pollution_objects = []
        self.particles = [] 
        self.masks = []
        self.pollution_spawn_timer = 0
        self.pollution_spawn_interval = random.uniform(
            POLLUTION_SPAWN_INTERVAL_MIN,
            POLLUTION_SPAWN_INTERVAL_MAX
        )
        self.mask_spawn_timer = 0
        self.mask_spawn_interval = random.uniform(
            MASK_SPAWN_INTERVAL_MIN,
            MASK_SPAWN_INTERVAL_MAX
        )
        self.ground_scroll = 0.0
        self.sky_scroll = 0.0
        self.city_scroll = 0.0
        self.survival_time = 0.0
        self.score = 0

    def spawn_pollution(self):
        pollution = Pollution.create_random()
        self.pollution_objects.append(pollution)

    def spawn_mask(self):
        mask = Mask.create_random()
        self.masks.append(mask)

    def update(self, dt):
        self.menu_anim_timer += dt

        scroll_speed_factor = 1.0
        if self.state != PLAYING:
            scroll_speed_factor = 0.2

        self.ground_scroll += PARALLAX_GROUND_SPEED * dt * scroll_speed_factor
        if self.ground_scroll >= PARALLAX_GROUND_PATTERN_WIDTH:
            self.ground_scroll -= PARALLAX_GROUND_PATTERN_WIDTH
            
        self.sky_scroll += PARALLAX_SKY_SPEED * dt * scroll_speed_factor
        if self.sky_scroll >= PARALLAX_SKY_PATTERN_WIDTH:
            self.sky_scroll -= PARALLAX_SKY_PATTERN_WIDTH

        self.city_scroll += PARALLAX_CITY_SPEED * dt * scroll_speed_factor
        if self.city_scroll >= PARALLAX_CITY_PATTERN_WIDTH:
            self.city_scroll -= PARALLAX_CITY_PATTERN_WIDTH

        if self.state != PLAYING:
            return

        self.survival_time += dt
        self.score = int(self.survival_time * 10)
        self.player.update(dt)
        
        if self.player.health <= 0:
            if self.score > self.best_score:
                self.best_score = self.score
            self.state = GAME_OVER
            
        self.pollution_spawn_timer += dt
        if self.pollution_spawn_timer >= self.pollution_spawn_interval:
            self.spawn_pollution()
            self.pollution_spawn_timer = 0
            self.pollution_spawn_interval = random.uniform(
                POLLUTION_SPAWN_INTERVAL_MIN,
                POLLUTION_SPAWN_INTERVAL_MAX
            )
            
        self.mask_spawn_timer += dt
        if self.mask_spawn_timer >= self.mask_spawn_interval:
            self.spawn_mask()
            self.mask_spawn_timer = 0
            self.mask_spawn_interval = random.uniform(
                MASK_SPAWN_INTERVAL_MIN,
                MASK_SPAWN_INTERVAL_MAX
            )
            
        # LOGIKA TABRAKAN: POLUSI
        for pollution in self.pollution_objects[:]:
            pollution.update(dt)
            
            # Cek Tabrakan: Player vs Awan Polusi
            if self.player.check_collision_with_particle(pollution):
                # Kurangi darah saat nabrak
                self.player.take_damage(15) 
                self.pollution_objects.remove(pollution)
                continue
            
            if pollution.is_off_screen():
                self.pollution_objects.remove(pollution)
                
        # LOGIKA TABRAKAN: MASKER
        for mask in self.masks[:]:
            mask.update(dt)
            if mask.check_collision_with_player(self.player):
                self.player.collect_mask()
                self.masks.remove(mask)
            if mask.is_off_screen():
                self.masks.remove(mask)

    def draw_background(self, ctx):
        ctx.save()
        pat = cairo.LinearGradient(0, 0, 0, GROUND_Y)
        pat.add_color_stop_rgb(0, SKY_TOP_COLOR[0]/255.0, SKY_TOP_COLOR[1]/255.0, SKY_TOP_COLOR[2]/255.0)
        pat.add_color_stop_rgb(1, SKY_BOTTOM_COLOR[0]/255.0, SKY_BOTTOM_COLOR[1]/255.0, SKY_BOTTOM_COLOR[2]/255.0)
        ctx.rectangle(0, 0, SCREEN_WIDTH, GROUND_Y)
        ctx.set_source(pat)
        ctx.fill()
        ctx.restore()

        ctx.save()
        pattern_start = -int(self.city_scroll) % PARALLAX_CITY_PATTERN_WIDTH
        x = pattern_start - PARALLAX_CITY_PATTERN_WIDTH
        while x < SCREEN_WIDTH + PARALLAX_CITY_PATTERN_WIDTH:
            ctx.set_source_rgb(CITY_COLOR[0]/255.0, CITY_COLOR[1]/255.0, CITY_COLOR[2]/255.0)
            ctx.rectangle(x + 20, GROUND_Y - 180, 50, 180)
            ctx.fill()
            ctx.rectangle(x + 80, GROUND_Y - 120, 60, 120)
            ctx.fill()
            ctx.rectangle(x + 150, GROUND_Y - 220, 70, 220)
            ctx.fill()
            ctx.rectangle(x + 230, GROUND_Y - 150, 90, 150)
            ctx.fill()
            ctx.set_source_rgb(CITY_WINDOW_COLOR[0]/255.0, CITY_WINDOW_COLOR[1]/255.0, CITY_WINDOW_COLOR[2]/255.0)
            for row in range(6):
                for col in range(3):
                    ctx.rectangle(x + 160 + col*15, GROUND_Y - 200 + row*25, 8, 15)
            ctx.fill()
            x += PARALLAX_CITY_PATTERN_WIDTH
        ctx.restore()

        ctx.save()
        ctx.set_source_rgba(1, 1, 1, 0.6)
        pattern_start = -int(self.sky_scroll) % PARALLAX_SKY_PATTERN_WIDTH
        x = pattern_start - PARALLAX_SKY_PATTERN_WIDTH
        while x < SCREEN_WIDTH + PARALLAX_SKY_PATTERN_WIDTH:
            ctx.arc(x + 100, 80, 40, 0, 2 * math.pi)
            ctx.arc(x + 140, 70, 50, 0, 2 * math.pi)
            ctx.arc(x + 180, 80, 40, 0, 2 * math.pi)
            ctx.fill()
            ctx.arc(x + 320, 120, 25, 0, 2 * math.pi)
            ctx.arc(x + 350, 120, 30, 0, 2 * math.pi)
            ctx.fill()
            x += PARALLAX_SKY_PATTERN_WIDTH
        ctx.restore()

        ctx.save()
        ctx.set_source_rgb(GROUND_COLOR[0]/255.0, GROUND_COLOR[1]/255.0, GROUND_COLOR[2]/255.0)
        ctx.rectangle(0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y)
        ctx.fill()
        ctx.set_source_rgba(1, 1, 1, 0.15)
        ctx.rectangle(0, GROUND_Y, SCREEN_WIDTH, 10)
        ctx.fill()
        ctx.set_source_rgb(GROUND_DETAIL_COLOR[0]/255.0, GROUND_DETAIL_COLOR[1]/255.0, GROUND_DETAIL_COLOR[2]/255.0)
        pattern_start = -int(self.ground_scroll) % PARALLAX_GROUND_PATTERN_WIDTH
        x = pattern_start - PARALLAX_GROUND_PATTERN_WIDTH
        while x < SCREEN_WIDTH + PARALLAX_GROUND_PATTERN_WIDTH:
            for i in range(5):
                gx = x + i * 40
                ctx.move_to(gx, GROUND_Y)
                ctx.line_to(gx + 10, GROUND_Y + 15)
                ctx.line_to(gx + 20, GROUND_Y)
                ctx.fill()
            x += PARALLAX_GROUND_PATTERN_WIDTH
        ctx.restore()

    def draw_hud(self, ctx):
        ctx.save()
        bar_x, bar_y = 60, 25
        bar_w, bar_h = 200, 22
        ctx.set_source_rgba(0, 0, 0, 0.2)
        ctx.rectangle(bar_x + 3, bar_y + 3, bar_w, bar_h)
        ctx.fill()
        ctx.set_source_rgb(1.0, 1.0, 1.0)
        ctx.rectangle(bar_x, bar_y, bar_w, bar_h)
        ctx.fill()
        ctx.set_line_width(2)
        ctx.set_source_rgb(0.2, 0.2, 0.2)
        ctx.stroke()
        health_pct = max(0, self.player.health / self.player.max_health)
        fill_w = int((bar_w - 4) * health_pct)
        if fill_w > 0:
            ctx.set_source_rgb(HEALTH_BAR_COLOR[0]/255.0, HEALTH_BAR_COLOR[1]/255.0, HEALTH_BAR_COLOR[2]/255.0)
            ctx.rectangle(bar_x + 2, bar_y + 2, fill_w, bar_h - 4)
            ctx.fill()
            ctx.set_source_rgba(1, 1, 1, 0.3)
            ctx.rectangle(bar_x + 2, bar_y + 2, fill_w, (bar_h - 4)/2)
            ctx.fill()
        ctx.translate(35, 35)
        ctx.scale(1.3, 1.3)
        ctx.set_source_rgb(238/255.0, 82/255.0, 83/255.0)
        ctx.move_to(0, -5)
        ctx.curve_to(-7, -12, -12, -5, 0, 8)
        ctx.curve_to(12, -5, 7, -12, 0, -5)
        ctx.fill()
        ctx.restore()

    def draw_button(self, ctx, x, y, width, height, text, hover=False):
        ctx.save()
        radius = 15
        def rounded_rect(bx, by, bw, bh, br):
            ctx.new_sub_path()
            ctx.arc(bx + bw - br, by + br, br, -math.pi/2, 0)
            ctx.arc(bx + bw - br, by + bh - br, br, 0, math.pi/2)
            ctx.arc(bx + br, by + bh - br, br, math.pi/2, math.pi)
            ctx.arc(bx + br, by + br, br, math.pi, 3*math.pi/2)
            ctx.close_path()

        ctx.set_source_rgba(0, 0, 0, 0.3)
        rounded_rect(x + 4, y + 4, width, height, radius)
        ctx.fill()
        color = BUTTON_HOVER_COLOR if hover else BUTTON_COLOR
        ctx.set_source_rgb(color[0]/255.0, color[1]/255.0, color[2]/255.0)
        rounded_rect(x, y, width, height, radius)
        ctx.fill()
        ctx.set_source_rgba(1, 1, 1, 0.4)
        ctx.set_line_width(2)
        ctx.stroke()
        ctx.restore()
        if not hasattr(self, '_button_texts'):
            self._button_texts = []
        self._button_texts.append((x, y, width, height, text))

    def check_button_click(self, mouse_x, mouse_y, button_x, button_y, button_width, button_height):
        return (button_x <= mouse_x <= button_x + button_width and
                button_y <= mouse_y <= button_y + button_height)

    def draw_menu(self, ctx, mouse_x, mouse_y):
        self.draw_background(ctx)
        float_offset = math.sin(self.menu_anim_timer * 2) * 8
        title_y = 150 + float_offset
        title_text = "Healthy Breath Runner"
        self._text_overlays.append((title_text, SCREEN_WIDTH / 2 + 3, title_y + 3, 64, SHADOW_COLOR, True))
        self._text_overlays.append((title_text, SCREEN_WIDTH / 2, title_y, 64, TITLE_COLOR, True))
        button_x = SCREEN_WIDTH / 2 - 150
        button_y = SCREEN_HEIGHT / 2 + 20
        button_width = 300
        button_height = 65
        hover = self.check_button_click(mouse_x, mouse_y, button_x, button_y, button_width, button_height)
        self.draw_button(ctx, button_x, button_y, button_width, button_height, "PLAY GAME", hover)
        inst_text = "SPACE: Jump   |   DOWN: Duck"
        self._text_overlays.append((inst_text, SCREEN_WIDTH / 2, button_y + button_height + 60, 24, (100, 100, 100), False))

    def draw_game_over(self, ctx, mouse_x, mouse_y):
        self.draw_background(ctx)
        ctx.save()
        ctx.set_source_rgba(0, 0, 0, 0.6)
        ctx.rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        ctx.fill()
        ctx.restore()
        title_text = "GAME OVER"
        self._text_overlays.append((title_text, SCREEN_WIDTH / 2 + 4, 160 + 4, 70, SHADOW_COLOR, True))
        self._text_overlays.append((title_text, SCREEN_WIDTH / 2, 160, 70, (238, 82, 83), True))
        score_text = f"Score: {self.score}"
        self._text_overlays.append((score_text, SCREEN_WIDTH / 2, 240, 48, SCORE_COLOR, True))
        if self.best_score > 0:
            best_text = f"Best Score: {self.best_score}"
            self._text_overlays.append((best_text, SCREEN_WIDTH / 2, 290, 32, (220, 220, 220), False))
        button_x = SCREEN_WIDTH / 2 - 150
        button_y = SCREEN_HEIGHT / 2 + 60
        button_width = 300
        button_height = 65
        hover = self.check_button_click(mouse_x, mouse_y, button_x, button_y, button_width, button_height)
        self.draw_button(ctx, button_x, button_y, button_width, button_height, "TRY AGAIN", hover)

    def draw(self, ctx, mouse_x=0, mouse_y=0):
        self._text_overlays = []
        self._button_texts = []
        if self.state == MENU:
            self.draw_menu(ctx, mouse_x, mouse_y)
        elif self.state == GAME_OVER:
            self.draw_game_over(ctx, mouse_x, mouse_y)
        else:
            self.draw_background(ctx)
            for pollution in self.pollution_objects:
                pollution.draw(ctx)
            for mask in self.masks:
                mask.draw(ctx)
            self.player.draw(ctx)
            self.draw_hud(ctx)
            score_text = f"{self.score}"
            self._text_overlays.append((score_text, SCREEN_WIDTH - 60 + 2, 50 + 2, 48, SHADOW_COLOR, True))
            self._text_overlays.append((score_text, SCREEN_WIDTH - 60, 50, 48, SCORE_COLOR, True))

def cairo_surface_to_pygame(cairo_surface):
    buf = cairo_surface.get_data()
    width = cairo_surface.get_width()
    height = cairo_surface.get_height()
    pygame_surface = pygame.image.frombuffer(buf, (width, height), "BGRA")
    return pygame_surface

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Healthy Breath Runner")
    game = Game()
    game._text_overlays = []
    game._button_texts = []
    
    font_cache = {}
    def get_font(size):
        if size not in font_cache:
            font_cache[size] = pygame.font.Font(None, size)
        return font_cache[size]
        
    running = True
    clock = pygame.time.Clock()
    mouse_x, mouse_y = 0, 0
    
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game.state == PLAYING:
                        game.player.jump()
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    if game.state == PLAYING:
                        game.player.duck()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    if game.state == PLAYING:
                        game.player.unduck()
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = event.pos
                    if game.state == MENU:
                        button_x = SCREEN_WIDTH / 2 - 150
                        button_y = SCREEN_HEIGHT / 2 + 20
                        button_width = 300
                        button_height = 65
                        if game.check_button_click(mouse_x, mouse_y, button_x, button_y, button_width, button_height):
                            game.state = PLAYING
                            game.reset_game()
                    elif game.state == GAME_OVER:
                        button_x = SCREEN_WIDTH / 2 - 150
                        button_y = SCREEN_HEIGHT / 2 + 60
                        button_width = 300
                        button_height = 65
                        if game.check_button_click(mouse_x, mouse_y, button_x, button_y, button_width, button_height):
                            game.state = PLAYING
                            game.reset_game()
        game.update(dt)
        cairo_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, SCREEN_WIDTH, SCREEN_HEIGHT)
        ctx = cairo.Context(cairo_surface)
        game.draw(ctx, mouse_x, mouse_y)
        cairo_surface.flush()
        draw_surface = cairo_surface_to_pygame(cairo_surface)
        screen.blit(draw_surface, (0, 0))
        if game._text_overlays:
            for text, x, y, size, color, bold in game._text_overlays:
                try:
                    font = get_font(size)
                    text_surface = font.render(text, True, color)
                    text_rect = text_surface.get_rect(center=(x, y))
                    screen.blit(text_surface, text_rect)
                except:
                    pass
        if game._button_texts:
            try:
                button_font = get_font(32)
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