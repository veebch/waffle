pimport machine, neopixel, time, random, math

NUM_LEDS = 144
PIN_NUM = 0
np = neopixel.NeoPixel(machine.Pin(PIN_NUM), NUM_LEDS)

BLOCK_SIZE = 48
positions = [0, NUM_LEDS//3, 2*NUM_LEDS//3]  # centers for RGB blocks
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

speed = 0.01       # seconds per frame
frac_positions = [float(p) for p in positions]

# === Randomized white buildup ===
led_indices = list(range(NUM_LEDS))
for i in range(len(led_indices)-1, 0, -1):
    j = random.getrandbits(8) % (i+1)
    led_indices[i], led_indices[j] = led_indices[j], led_indices[i]

for idx in led_indices:
    np[idx] = (255, 255, 255)
    np.write()
    # time.sleep(speed)

# === Helper to draw blocks (movement phase) ===
def set_block_points(frac_positions, colors, block_size=12):
    np.fill((0,0,0))
    for pos, color in zip(frac_positions, colors):
        center = int(round(pos))  # center LED index
        start = (center - block_size//2) % NUM_LEDS
        for offset in range(block_size):
            led = (start + offset) % NUM_LEDS
            np[led] = color
    np.write()

# === Shrinking phase ===
MAX_WIDTH = NUM_LEDS
shrink_steps = (MAX_WIDTH - BLOCK_SIZE) // 2  # symmetric shrink

for step in range(shrink_steps + 1):
    np.fill((0,0,0))
    width = MAX_WIDTH - 2*step
    for cidx, color in enumerate(colors):
        center = positions[cidx]
        start = (center - width//2) % NUM_LEDS
        for i in range(width):
            led = (start + i) % NUM_LEDS
            # additive blend so colors don’t overwrite
            r, g, b = np[led]
            np[led] = (min(r+color[0],255),
                       min(g+color[1],255),
                       min(b+color[2],255))
    np.write()
    time.sleep(speed)

# === Ensure final positions match movement phase ===
frac_positions = [float(p) for p in positions]

# === Main moving blocks with ease-in/out ===
t = 0.0
T = 400      # total frames for full ease-in+ease-out
MAX_SPEED = 2.0  # peak step size

while t <= T:
    # smooth ease in/out curve (0 -> 2 -> 0)
    step_fraction = MAX_SPEED * math.sin(math.pi * (t/T))

    set_block_points(frac_positions, colors, BLOCK_SIZE)
    frac_positions = [(p + step_fraction) % NUM_LEDS for p in frac_positions]
    time.sleep(speed)

    t += 1

