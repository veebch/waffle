import machine, neopixel, time

NUM_LEDS = 144
PIN_NUM = 0
np = neopixel.NeoPixel(machine.Pin(PIN_NUM), NUM_LEDS)

BLOCK_SIZE = 12
positions = [0, NUM_LEDS//3, 2*NUM_LEDS//3]
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

speed = 0.01       # seconds per frame
step_fraction = 1  # fractional LED per frame
frac_positions = [float(p) for p in positions]

# === Randomized white buildup ===
import random
led_indices = list(range(NUM_LEDS))
# Simple in-place shuffle
for i in range(len(led_indices)-1, 0, -1):
    j = random.getrandbits(8) % (i+1)
    led_indices[i], led_indices[j] = led_indices[j], led_indices[i]

for idx in led_indices:
    np[idx] = (255, 255, 255)
    np.write()
    time.sleep(speed)

# === Shrinking phase ===
# Each color starts full-width, then shrinks to its BLOCK_SIZE at its final position
MAX_WIDTH = NUM_LEDS
shrink_steps = (MAX_WIDTH - BLOCK_SIZE) // 2  # symmetric shrink

for step in range(shrink_steps + 1):
    np.fill((0, 0, 0))
    for cidx, color in enumerate(colors):
        # Calculate current block width for this color
        width = MAX_WIDTH - 2*step
        # Determine start index so it shrinks toward final 12-pixel block position
        final_pos = positions[cidx]
        start = (final_pos - width//2) % NUM_LEDS
        for i in range(width):
            led = (start + i) % NUM_LEDS
            # Additive to avoid overwriting other channels
            r, g, b = np[led]
            np[led] = (min(r+color[0], 255),
                       min(g+color[1], 255),
                       min(b+color[2], 255))
    np.write()
    time.sleep(speed)

# === Main moving blocks ===
def set_block_points(frac_positions, colors, block_size=12):
    np.fill((0,0,0))
    for pos, color in zip(frac_positions, colors):
        center = int(pos)
        for offset in range(block_size):
            led = (center + offset) % NUM_LEDS
            np[led] = color
    np.write()
ease_in = .05
while True:
    set_block_points(frac_positions, colors, BLOCK_SIZE)
    frac_positions = [(p + step_fraction) % NUM_LEDS for p in frac_positions]
    time.sleep(speed + ease_in)
    ease_in = ease_in - .001
    ease_in = max(0,ease_in)
