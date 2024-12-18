from machine import Pin
import neopixel
import time

# LED setup
p = 2  # Pin number
n = 1  # Number of NeoPixels
np = neopixel.NeoPixel(Pin(p), n)

def wheel(pos, intensity=0.5):
    # Generate rainbow colors across 0-255 positions with reduced intensity
    if pos < 85:
        return (int(pos * 3 * intensity), int((255 - pos * 3) * intensity), int(0 * intensity))
    elif pos < 170:
        pos -= 85
        return (int((255 - pos * 3) * intensity), int(0 * intensity), int(pos * 3 * intensity))
    else:
        pos -= 170
        return (int(0 * intensity), int(pos * 3 * intensity), int((255 - pos * 3) * intensity))

# Main loop
while True:
    for i in range(256):
        np[0] = wheel(i, intensity=0.05)  # Adjust the intensity here
        np.write()
        time.sleep(0.01)  # Adjust the speed of the color cycle

