from machine import ADC, Pin, UART
import time
import network
import urequests


# -------- WiFi Settings ----------
SSID = "iPhone"
PASSWORD = "18Bh@#ratii"


# -------- ThingSpeak ----------
API_KEY = "OZTBWQYC1WZQAE0D"
THINGSPEAK_URL = "http://api.thingspeak.com/update"
THINGSPEAK_INTERVAL = 15   # seconds


# =================================================
# 🔵 RGB LED (COMMON ANODE)
# LOW = ON, HIGH = OFF
# =================================================
RED   = Pin(12, Pin.OUT)
GREEN = Pin(13, Pin.OUT)
BLUE  = Pin(14, Pin.OUT)

def rgb_off():
    RED.value(1)
    GREEN.value(1)
    BLUE.value(1)

def set_green():
    rgb_off()
    GREEN.value(0)

def set_red():
    rgb_off()
    RED.value(0)

set_green()   # default green


# =================================================
# 🔊 DFPLAYER (Speaker)
# =================================================
uart = UART(2, baudrate=9600, tx=17, rx=16)

def df_send(cmd, p1=0, p2=0):
    buf = bytearray([0x7E,0xFF,0x06,cmd,0x00,p1,p2,0x00,0x00,0xEF])
    checksum = 0 - sum(buf[1:7])
    buf[7] = (checksum >> 8) & 0xFF
    buf[8] = checksum & 0xFF
    uart.write(buf)

def play_alert():
    df_send(0x03, 0x00, 0x01)   # play 0001.mp3

def stop_audio():
    df_send(0x16)


# -------- Pole Mapping ----------
# Dummy P1 & P6, real sensors P2–P5
POLE_PINS = [32, 33, 34, 35]
OFFSETS   = [2.4088, 2.4094, 2.4142, 2.4128]


# -------- ADC setup ----------
adcs = []
for pin in POLE_PINS:
    a = ADC(Pin(pin))
    a.atten(ADC.ATTN_11DB)
    a.width(ADC.WIDTH_12BIT)
    adcs.append(a)


# ---------------- WIFI ----------------
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Connecting WiFi...")
        wlan.connect(SSID, PASSWORD)

        while not wlan.isconnected():
            time.sleep(1)

    print("WiFi Connected ✓")
    return wlan

connect_wifi()


# ---------------- CURRENT READ ----------------
VREF = 3.3
ADC_MAX = 4095
SENSITIVITY = 0.185

def read_current(adc, offset):
    val = adc.read()
    voltage = (val * VREF) / ADC_MAX
    i = (voltage - offset) / SENSITIVITY

    if i < -0.01:
        i = -i

    return i


def read_avg(adc, offset):
    s = 0
    for _ in range(50):
        s += read_current(adc, offset)
        time.sleep_us(200)
    return s / 50


# ---------------- WIRE CUT CHECK ----------------
def is_wire_cut(i):
    return 12.5 <= i <= 13.5


# ---------------- THINGSPEAK ----------------
def send_to_thingspeak(*values):

    try:
        url = THINGSPEAK_URL + "?api_key=" + API_KEY

        for i, v in enumerate(values):
            url += "&field{}={}".format(i+1, v)

        r = urequests.get(url)
        r.close()

        print("ThingSpeak Updated OK")

    except Exception as e:
        print("ThingSpeak ERROR:", e)


# =================================================
print("\n⚡ Wire Cut Monitoring Started\n")

last_send_time = 0
last_audio_time = 0
AUDIO_REPEAT = 5   # seconds


while True:

    # ----- Read currents for P2–P5 -----
    currents = []

    for adc, offset in zip(adcs, OFFSETS):
        currents.append(read_avg(adc, offset))

    display = currents[:]  # copy for printing / zeroing cut

    wire_cut_found = False
    cut_index = -1


    # ----- Detect wire cut -----
    for idx, current in enumerate(currents):

        if is_wire_cut(current):
            wire_cut_found = True
            cut_index = idx
            display[idx] = 0.0
            break


    # ----- Report wire cut -----
    now = time.time()

    if wire_cut_found:

        set_red()

        # repeat audio every 5 sec
        if now - last_audio_time >= AUDIO_REPEAT:
            play_alert()
            last_audio_time = now

        if cut_index == 0:
            print("⚠️ Wire CUT detected between Source and Pole2")
        else:
            print(f"⚠️ Wire CUT detected between Pole{cut_index+1} and Pole{cut_index+2}")

    else:

        set_green()
        stop_audio()
        print("✅ The Line Is Fully Operational!")


    # ----- Show readings -----
    for idx, val in enumerate(display):
        print(f"P{idx+2}: {round(val,3)}", end="  ")

    print()


    # ----- ThingSpeak every 15 seconds -----
    if now - last_send_time >= THINGSPEAK_INTERVAL:
        send_to_thingspeak(*display)
        last_send_time = now


    print("----------------------------------")
    time.sleep(1)
