import paho.mqtt.client as mqtt
import ssl
import time
import psutil
import subprocess
import json

BROKER_HOST = "192.168.15.31"
BROKER_PORT = 8883
TOPIC = "topic/"
username = "piZero2"
password = username
CA_CERT = "/etc/mosquitto/certs/ca.crt"

def get_cpu_temp():
	try:
		temp = subprocess.check_output(["vcgencmd", "measure_temp"]).decode("utf-8")
		return float(temp.replace("temp=", "").replace("'C\n", ""))
	except Exception as e:
		return None

def on_connect(client, userdata, flags, rc):
	if rc == 0:
		print("Connected!")
	else:
		print(f"Connection failed, rc: {rc}")

client = mqtt.Client()
client.username_pw_set(username, password)
client.tls_set(ca_certs=CA_CERT, tls_version=ssl.PROTOCOL_TLS_CLIENT)

client.on_connect = on_connect
client.connect(BROKER_HOST, BROKER_PORT, 60)

while True:
	system_data = {
		"cpu": {
			"cpu_temp": get_cpu_temp(),
			"cpu_usage": psutil.cpu_percent(),
			"frequency": psutil.cpu_freq().current
		},
		"memory":{
			"total": psutil.virtual_memory().total,
			"used": psutil.virtual_memory().used,
			"available": psutil.virtual_memory().available
		},
		"disk":{
			"total": psutil.disk_usage('/').total,
			"used": psutil.disk_usage('/').total,
			"free": psutil.disk_usage('/').free
		},
		"processes":{
			"total": len(psutil.pids())
		}
	}	
	client.publish(TOPIC, json.dumps(system_data))
	print(f"Info: {system_data}\npublished to: {TOPIC}")
	time.sleep(5)
