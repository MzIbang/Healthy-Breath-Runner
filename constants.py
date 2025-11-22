# Screen settings - pengaturan ukuran layar game
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GROUND_Y = SCREEN_HEIGHT - 50

# Block system - sistem blok untuk spawn area
BLOCK_SIZE = 30

# Game mechanics - mekanika game seperti damage
DAMAGE_COOLDOWN = 0.5
PARTICLE_DAMAGE = 5

# Player physics - fisika player seperti gravity dan jump
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_GRAVITY = 800
PLAYER_JUMP_STRENGTH = 400

# Obstacle (Pollution) settings - pengaturan rintangan polusi
POLLUTION_MIN_RADIUS = 15
POLLUTION_MAX_RADIUS = 25
POLLUTION_MIN_SPEED = 250
POLLUTION_MAX_SPEED = 280
POLLUTION_MIN_ALPHA = 0.2
POLLUTION_MAX_ALPHA = 0.6

# Obstacle spawn heights - tinggi spawn rintangan
POLLUTION_SPAWN_MIN_Y = 500
POLLUTION_SPAWN_MID_Y = POLLUTION_SPAWN_MIN_Y + 10
POLLUTION_SPAWN_MAX_Y = POLLUTION_SPAWN_MIN_Y + 30

# Spawn timing - waktu spawn rintangan
POLLUTION_SPAWN_INTERVAL_MIN = 1.5
POLLUTION_SPAWN_INTERVAL_MAX = 3.0

# Mask (protective item) settings - pengaturan item mask pelindung
MASK_SPAWN_INTERVAL_MIN = 5.0
MASK_SPAWN_INTERVAL_MAX = 10.0
MASK_SIZE = 25
MASK_HEALTH_RESTORE = 20
MASK_PROTECTION_DURATION = 5.0
MASK_SPAWN_MIN_Y = 500
MASK_SPAWN_MAX_Y = MASK_SPAWN_MIN_Y + 30

# Parallax scrolling speeds - kecepatan scrolling parallax untuk efek depth
PARALLAX_GROUND_SPEED = 200
PARALLAX_SKY_SPEED = 30

# Parallax pattern sizes - ukuran pattern untuk parallax
PARALLAX_GROUND_PATTERN_WIDTH = 200
PARALLAX_SKY_PATTERN_WIDTH = 400

# Colors (RGB) - warna-warna yang dipake di game
BACKGROUND_COLOR = (135, 206, 235)
GROUND_COLOR = (34, 139, 34)
GROUND_DETAIL_COLOR = (28, 120, 28)
SKY_DETAIL_COLOR = (100, 180, 220)
PLAYER_COLOR = (255, 200, 100)
POLLUTION_COLOR = (100, 100, 100)
PARTICLE_COLOR = (150, 150, 150)
HEALTH_BAR_COLOR = (200, 20, 20)
MASK_COLOR = (50, 150, 255)
MASK_STRAP_COLOR = (200, 200, 200)
PROTECTION_COLOR = (100, 200, 255)

# UI Colors - warna untuk UI seperti button
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER_COLOR = (100, 150, 200)
BUTTON_TEXT_COLOR = (255, 255, 255)
TITLE_COLOR = (50, 50, 50)
SCORE_COLOR = (255, 255, 255)
