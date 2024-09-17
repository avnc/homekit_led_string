import WIFI_CONFIG
from network_manager import NetworkManager
import uasyncio
import os
import time
from umqtt.robust import MQTTClient
import plasma
from plasma import plasma_stick

# Constants
# Set how many LEDs you have, set this as needed
NUM_LEDS = 50
LAST_FILENAME = "lastvalue.txt" # file to store last value
PREV_FILENAME = "prevvalue.txt" # file to store the previous value

def read_value(filename):
    try:
        with open(filename) as f:
            val = f.read()
    except:
        val = "0, 0, 0"
    return map(int, val.split(","))

# Define the RGB color (initially off unless a saved value is found)
def update_value(red, green, blue, update_file = LAST_FILENAME ):
    try:
        f = open(update_file, "wt")
        f.write(str(red) + "," + str(green) + "," + str(blue))
        print(f"wrote value to file {update_file}")
        f.close()
    except Exception as e:
        # do nothing
        print(f"exception {e} updating last value file")

# Function to handle incoming MQTT messages
def mqtt_callback(topic, msg):
    print(f"received {topic} and {msg}")
    global red, green, blue
    if topic.endswith(b"setRGB"):
        # Parse RGB values from the message
        r, g, b = map(int, msg.split(b","))
        # Update the RGB color values
        red, green, blue = r, g, b
        # Control the LED based on the RGB values (assuming you have an RGB LED)
        # Replace 'gpio_red', 'gpio_green', and 'gpio_blue' with the actual GPIO pin numbersif topic.endswith(b"setOn"):
        for i in range(NUM_LEDS):
            led_strip.set_rgb(i, red, green, blue)
        update_value(red, green, blue)
    if topic.endswith(b"setOn"):    
        if msg == b"true":
            print("turning on")
            red, green, blue = read_value(PREV_FILENAME)
            for i in range(NUM_LEDS):
                led_strip.set_rgb(i, red, green, blue)
                time.sleep(0.005)
        else: 
            for i in range(NUM_LEDS):
                led_strip.set_rgb(i, 0, 0, 0)
            update_value(red, green, blue, PREV_FILENAME)
            update_value(0, 0, 0)
        
    elif topic.endswith(b"getRGB"):
        # Respond with the current RGB color
        client.publish(topic, f"{red},{green},{blue}")

def status_handler(mode, status, ip):
    # reports wifi connection status
    print(mode, status, ip)
    print('Connecting to wifi...')
    # flash purple while connecting
    for i in range(NUM_LEDS):
        led_strip.set_rgb(i, 30, 10, 70) 
        time.sleep(0.02)
    for i in range(NUM_LEDS):
        led_strip.set_rgb(i, 0, 0, 0)
    if status is not None:
        if status:
            print('Connection successful!')
        else:
            print('Connection failed!')
            # light up red if connection fails
            for i in range(NUM_LEDS):
                led_strip.set_rgb(i, 255, 0, 0)
            # sleep for 1 min, then turn off
            time.sleep(60)
            for i in range(NUM_LEDS):
                led_strip.set_rgb(i, 0, 0, 0)

# read last value from file           
red, green, blue = read_value(LAST_FILENAME)
print(f"last values are r:{red}, g:{green}, b:{blue}")

# set up the WS2812 / NeoPixel™ LEDs
led_strip = plasma.WS2812(NUM_LEDS, 0, 0, plasma_stick.DAT, color_order=plasma.COLOR_ORDER_RGB)

# start updating the LED strip
led_strip.start()

# set up wifi, set timeout to 3 mins to handle power loss (wifi takes a couple of mins to come back online)
# if set to too low a timeout, the device will not connect to wifi on boot
network_manager = NetworkManager(WIFI_CONFIG.COUNTRY, status_handler=status_handler, client_timeout=180)
uasyncio.get_event_loop().run_until_complete(network_manager.client(WIFI_CONFIG.SSID, WIFI_CONFIG.PSK))

#Define MQTT parameters
mqtt_broker = WIFI_CONFIG.BROKER
mqtt_topic_set = WIFI_CONFIG.LOCATION + WIFI_CONFIG.SET_RGB
mqtt_topic_get = WIFI_CONFIG.LOCATION + WIFI_CONFIG.GET_RGB
mqtt_topic_setOn = WIFI_CONFIG.LOCATION + WIFI_CONFIG.SET_ON

# Initialize MQTT client
client = MQTTClient(WIFI_CONFIG.HOSTNAME, server=mqtt_broker)

# Connect to the MQTT broker and set the callback function
client.set_callback(mqtt_callback)
client.connect()
client.subscribe(mqtt_topic_set)
client.subscribe(mqtt_topic_get)
client.subscribe(mqtt_topic_setOn)
print("MQTT connection setup")

# set initial values (read from file or defaults to 0,0,0 if no file)
for i in range(NUM_LEDS):
    led_strip.set_rgb(i, red, green, blue)

# Main loop
try:
    while True:
        # Check for incoming MQTT messages
        client.check_msg()
        time.sleep(0.005)
finally:
    client.disconnect()
