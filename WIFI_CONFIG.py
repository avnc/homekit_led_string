# Description: Configuration file for WIFI connection and MQTT broker
# Update the following variables with your own values that match your network and MQTT broker
SSID = "WIFI_SSID" # e.g. "my_wifi"
PSK = "WIFI_PASSWORD" # e.g. "password"
COUNTRY = "COUNTRY_CODE" # e.g. "US"
BROKER = "BROKER_IP" # e.g. "192.168.1.2"
HOSTNAME = "NETWORK_HOSTNAME" # e.g. "DasBlinkenLights"
LOCATION = b"LOCATION" # e.g. b"Living\\Cabinet2\\" for MQTT topic
# MQTT topics, note these need to match the topics configured in the MQTT Thing plugin
# These are the topics that the Pico W will subscribe to
# and the topics that Homebridge will publish to
SET_ON = b"setOn" # MQTT topic for turning on/off
GET_RGB = b"getRGB" # MQTT topic for getting RGB values
SET_RGB = b"setRGB" # MQTT topic for setting RGB values
