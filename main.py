import machine, neopixel, time, random, math

NUM_LEDS = 144
PIN_NUM = 0
np = neopixel.NeoPixel(machine.Pin(PIN_NUM), NUM_LEDS)

BLOCK_SIZE = 36
# Single position for the white block
position = 0
color = (255, 255, 255)  # White color

speed = 0.01       # seconds per frame
frac_position = float(position)

# === Randomized white buildup ===
led_indices = list(range(NUM_LEDS))
for i in range(len(led_indices)-1, 0, -1):
    j = random.getrandbits(8) % (i+1)
    led_indices[i], led_indices[j] = led_indices[j], led_indices[i]

for idx in led_indices:
    np[idx] = (255, 255, 255)
    np.write()
    # time.sleep(speed)

# === Helper to draw a single block ===
def set_block_point(frac_position, color, block_size=12):
    np.fill((0,0,0))
    center = int(round(frac_position))
    start = (center - block_size//2) % NUM_LEDS
    for offset in range(block_size):
        led = (start + offset) % NUM_LEDS
        np[led] = color
    np.write()

# === Shrinking phase (full width to BLOCK_SIZE) ===
MAX_WIDTH = NUM_LEDS
shrink_steps = (MAX_WIDTH - BLOCK_SIZE) // 2

for step in range(shrink_steps + 1):
    np.fill((0,0,0))
    width = MAX_WIDTH - 2*step
    center = position
    start = (center - width//2) % NUM_LEDS
    for i in range(width):
        led = (start + i) % NUM_LEDS
        r, g, b = np[led]
        # Add white color
        np[led] = (min(r+color[0],255),
                   min(g+color[1],255),
                   min(b+color[2],255))
    np.write()
    time.sleep(speed)

# === Movement with ease-in/out ===
TOTAL_FRAMES = 400
MAX_SPEED = 2.0  # peak LED/frame

for t in range(TOTAL_FRAMES + 1):
    step_fraction = MAX_SPEED * math.sin(math.pi * (t/TOTAL_FRAMES))
    set_block_point(frac_position, color, BLOCK_SIZE)
    frac_position = (frac_position + step_fraction) % NUM_LEDS
    time.sleep(speed)

# === Reverse shrinking / spread back to white ===
final_position = frac_position  # capture final position

for step in range(shrink_steps, -1, -1):
    np.fill((0,0,0))
    width = MAX_WIDTH - 2*step
    center = final_position
    start = (int(center) - width//2) % NUM_LEDS
    for i in range(width):
        led = (start + i) % NUM_LEDS
        r, g, b = np[led]
        # Add white color
        np[led] = (min(r+color[0],255),
                   min(g+color[1],255),
                   min(b+color[2],255))
    np.write()
    time.sleep(speed)
time.sleep(5)
# === Fade white to off ===
FADE_STEPS = 200
for step in range(FADE_STEPS + 1):
    brightness = int(255 * (1 - step/FADE_STEPS))
    np.fill((brightness, brightness, brightness))
    np.write()
    time.sleep(speed)
