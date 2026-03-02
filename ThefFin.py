from machine import ADC, Pin
import time
import network
import urequests

# -------- WiFi Settings ----------
SSID = "*******"       
PASSWORD = "*******"   

# -------- ThingSpeak ----------
API_KEY = "*********"
THINGSPEAK_URL = "http://api.thingspeak.com/update"

# -------- Pole Mapping ----------
P1_PIN = 34
P2_PIN = 35
P3_PIN = 32

# -------- Constants ----------
VREF = 3.3
ADC_MAX = 4095
SENSITIVITY = 0.185   # ACS712-5A

# -------- Offsets ----------
offsetP1 = 2.4277
offsetP2 = 2.4463
offsetP3 = 2.4392

# -------- ADC setup ----------
adc_p1 = ADC(Pin(P1_PIN))
adc_p2 = ADC(Pin(P2_PIN))
adc_p3 = ADC(Pin(P3_PIN))

for adc in [adc_p1, adc_p2, adc_p3]:
    adc.atten(ADC.ATTN_11DB)
    adc.width(ADC.WIDTH_12BIT)

# -------- WiFi Connect ----------
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
    print("WiFi Connected:", wlan.ifconfig())
    return wlan

wlan = connect_wifi()

# -------- Read raw current ----------
def read_current(adc, offset):
    adc_val = adc.read()
    voltage = (adc_val * VREF) / ADC_MAX
    i = (voltage - offset) / SENSITIVITY
    # Normalize negative readings
    if i < -0.01:
        i = -i
    return i

# -------- Averaged current ----------
def read_current_avg(adc, offset):
    s = 0
    for _ in range(50):
        s += read_current(adc, offset)
        time.sleep_us(200)
    return s / 50

# -------- Dead zone ----------
def clean_current(i):
    if i < 0.15:
        return 0.0
    return i

# -------- Send readings to ThingSpeak ----------
def send_to_thingspeak(p1, p2, p3):
    try:
        url = f"{THINGSPEAK_URL}?api_key={API_KEY}&field1={p1}&field2={p2}&field3={p3}"
        response = urequests.get(url)
        response.close()
        print("📡 Sent to ThingSpeak")
    except:
        print("❌ ThingSpeak send failed")

print("\n⚡ Max-Pole Theft Logic Active (MicroPython)")

while True:

    # -------- Read currents ----------
    P1 = clean_current(read_current_avg(adc_p1, offsetP1))
    P2 = clean_current(read_current_avg(adc_p2, offsetP2))
    P3 = clean_current(read_current_avg(adc_p3, offsetP3))

    print(
        "P1:", round(P1, 3),
        "| P2:", round(P2, 3),
        "| P3:", round(P3, 3)
    )

    # -------- Send to ThingSpeak ----------
    send_to_thingspeak(P1, P2, P3)

    # -------- Activate logic only if any current > 50mA ----------
    max_abs = max(P1, P2, P3)
    if max_abs <= 0.05:
        print("----------------------------------")
        time.sleep(1)
        continue

    # -------- Find biggest current (magnitude) ----------
    max_pole = 1
    max_i = P1

    if P2 > max_i:
        max_i = P2
        max_pole = 2

    if P3 > max_i:
        max_i = P3
        max_pole = 3

    # -------- Disconnected sensor check ----------
    if max_pole == 1:
        pole_current = P1
    elif max_pole == 2:
        pole_current = P2
    else:
        pole_current = P3

    # For normalized values, using magnitude ~12.5–13.5A for disconnection
    if 12.5 <= pole_current <= 13.5:
        print("⚠️ Pole{} sensor DISCONNECTED".format(max_pole))
        print("----------------------------------")
        time.sleep(4)
        continue

    # -------- Theft zone decision ----------
    if max_pole == 1:
        print("🚨 Possible THEFT between Pole1 & Pole2")
    elif max_pole == 2:
        print("🚨 Possible THEFT between Pole2 & Pole3")
    else:
        print("🚨 Possible THEFT after Pole3 (downstream)")

    print("----------------------------------")
    time.sleep(4)
