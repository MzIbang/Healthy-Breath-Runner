# Healthy Breath Runner

A 2D side-scrolling game using PyGame (window/loop/events) and PyCairo (rendering).

All visual elements are procedural placeholders drawn with Cairo. No external assets are loaded.

## Installation

1. Install Python 3.7 or higher

2. Install required packages:
   ```bash
   pip install pygame pycairo
   ```

   On Windows, you may need to install pycairo from a wheel:
   ```bash
   pip install pygame
   pip install pycairo
   ```

   On Linux (Ubuntu/Debian):
   ```bash
   sudo apt-get install python3-pygame python3-cairo
   ```

   On macOS:
   ```bash
   brew install pygobject3
   pip install pygame pycairo
   ```

3. Run the game:
   ```bash
   python game.py
   ```

## Controls

- **SPACE** - Jump

## Game Features

- Player character with gravity and jumping
- Auto-running animation (horizontal bob)
- Pollution objects spawning from the right
- Particle effects (smoke) from pollution
- Procedural rendering with Cairo (no external assets)
- HUD with health bar (always red)
- Balanced obstacle sizes and speeds for avoidability

## Project Structure

The codebase is organized into multiple modules for better maintainability:

- `constants.py` - All game constants, configuration, and colors
- `player.py` - Player character class with movement, jumping, and health
- `pollution.py` - Pollution obstacle class
- `particle.py` - Particle (smoke) effects class
- `game.py` - Main game class, rendering utilities, and entry point

## Game Balance

Obstacles are balanced to be avoidable:
- **Low obstacles**: Spawn near ground level - can be jumped over
- **High obstacles**: Spawn in upper area - can be avoided by staying on ground
- **Speeds**: Adjusted (80-120 px/s) to allow player reaction time
- **Sizes**: Limited (15-25px radius) so they don't block the entire path

Player jump mechanics:
- Jump height: ~100 pixels
- Player height: 60 pixels
- Allows clearing low obstacles while high obstacles can be avoided by staying grounded


