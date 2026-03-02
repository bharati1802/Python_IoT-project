from machine import Pin
import time
import network
import urequests
import dht

# -------- WiFi ----------
SSID = "iPhone"
PASSWORD = "18Bh@#ratii"

# -------- ThingSpeak ----------
API_KEY = "4F4CNT1KY49A2U97"
THINGSPEAK_URL = "http://api.thingspeak.com/update"
THINGSPEAK_INTERVAL = 15

# -------- DHT22 ----------
DHT_PIN = 15
OVERHEAT_TEMP = 40

sensor = dht.DHT22(Pin(DHT_PIN, Pin.OUT, Pin.PULL_UP))


# =================================================
# WIFI
# =================================================
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Connecting WiFi...")
        wlan.connect(SSID, PASSWORD)

        while not wlan.isconnected():
            time.sleep(1)

    print("WiFi Connected ✓")


# =================================================
# TEMPERATURE READ (Improved)
# =================================================
def read_temperature():

    for _ in range(3):  # retry 3 times
        try:
            sensor.measure()
            temp = sensor.temperature()

            # sanity check
            if -10 < temp < 100:
                return temp

        except:
            pass

        time.sleep(0.5)

    print("❌ DHT Sensor ERROR")
    return None   # very important


# =================================================
# THINGSPEAK
# =================================================
def send_to_thingspeak(temp, status):
    try:
        url = (
            f"{THINGSPEAK_URL}?api_key={API_KEY}"
            f"&field1={temp}"
            f"&field2={status}"
        )

        r = urequests.get(url)
        r.close()
        print("📡 ThingSpeak Updated")

    except:
        print("❌ ThingSpeak failed")


# =================================================
# MAIN
# =================================================
connect_wifi()

print("\n🔥 Overheating Monitor Started (GPIO15)\n")

last_send_time = 0

while True:

    temp = read_temperature()

    # =========================
    # SENSOR FAILED
    # =========================
    if temp is None:
        print("⚠ Sensor not responding")
        status = -1

    # =========================
    # OVERHEAT CHECK
    # =========================
    else:
        if temp >= OVERHEAT_TEMP:
            status = 1
            print("🔥 OVERHEAT DETECTED !!!")
        else:
            status = 0
            print("✅ Normal Temperature")

        print("Temperature:", temp, "°C")

    # =========================
    # ThingSpeak send only if valid
    # =========================
    now = time.time()
    if now - last_send_time >= THINGSPEAK_INTERVAL and temp is not None:
        send_to_thingspeak(temp, status)
        last_send_time = now

    print("---------------------------")
    time.sleep(3)

