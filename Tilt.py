from machine import I2C, Pin
import time, math
import urequests  # HTTP client

# -------------------------------
# CONFIG / API
# -------------------------------
API_KEY = "**************"   # Your Thingspeak Write API Key

# -------------------------------
# I2C setup (ESP32 ↔ MPU6050)
# -------------------------------
i2c = I2C(0, scl=Pin(22), sda=Pin(23))  # SCL=22, SDA=23
MPU_ADDR = 0x68
i2c.writeto_mem(MPU_ADDR, 0x6B, b'\x00')  # wake MPU6050

# -------------------------------
# RGB LED setup (Common Anode)
# -------------------------------
R = Pin(25, Pin.OUT)
G = Pin(26, Pin.OUT)
B = Pin(27, Pin.OUT)

def rgb_off():
    R.value(1)
    G.value(1)
    B.value(1)

def rgb_green():   # NORMAL
    rgb_off()
    G.value(0)

def rgb_blue():    # WARNING
    rgb_off()
    B.value(0)

def rgb_red():     # DANGER
    rgb_off()
    R.value(0)

# -------------------------------
# Parameters
# -------------------------------
WARNING_DELTA = 2
DANGER_DELTA = 10
READ_INTERVAL = 7

# -------------------------------
# MPU6050 helper functions
# -------------------------------
def read_raw(addr):
    d = i2c.readfrom_mem(MPU_ADDR, addr, 2)
    v = (d[0]<<8) | d[1]
    if v > 32767: v -= 65536
    return v

def get_accel():
    return (
        read_raw(0x3B)/16384,
        read_raw(0x3D)/16384,
        read_raw(0x3F)/16384
    )

def tilt(ax, ay, az):
    return abs(math.degrees(math.atan(ax / math.sqrt(ay*ay + az*az))))

# -------------------------------
# Capture baseline
# -------------------------------
print("Capturing baseline... keep pole straight")
time.sleep(2)
ax, ay, az = get_accel()
baseline = tilt(ax, ay, az)
print("Original-Position:", round(baseline,2), "°\n")

# Set initial LED to GREEN
rgb_green()

# -------------------------------
# Main loop
# -------------------------------
while True:
    ax, ay, az = get_accel()
    current_angle = tilt(ax, ay, az)
    delta = abs(current_angle - baseline)

    # Determine status and set RGB
    if delta >= DANGER_DELTA:
        status = "DANGER"
        status_num = 2
        rgb_red()
    elif delta >= WARNING_DELTA:
        status = "WARNING"
        status_num = 1
        rgb_blue()
    else:
        status = "NORMAL"
        status_num = 0
        rgb_green()

    # Print in requested format
    print(
        "Original-Position:", f"{round(baseline,2)}° |",
        "Current-Position:", f"{round(current_angle,2)}° Tilt |",
        "Position-Change:", f"{round(delta,2)}° Tilt from Original |",
        "Status:", status
    )

    # -------------------------------
    # Upload to Thingspeak via GET request
    # -------------------------------
    try:
        URL = "https://api.thingspeak.com/update?api_key={}&field1={}&field2={}&field3={}".format(
            API_KEY,
            round(current_angle,2),
            round(delta,2),
            status_num
        )
        r = urequests.get(URL)
        print("Upload response:", r.text)  # Thingspeak returns '1' if successful
        r.close()
    except Exception as e:
        print("Upload error:", e)

    time.sleep(READ_INTERVAL)

