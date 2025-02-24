import paho.mqtt.client as mqtt
import ssl
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

# CONFIGURAZIONE BROKER
BROKER_HOST = "192.168.15.31"
BROKER_PORT = 8883
TOPIC = "topic/"
USERNAME = "windows"
PASSWORD = USERNAME
CA_CERT = "C:\\Users\\immed\\Repos\\mqtt_rpi\\ca.crt"

# Buffer dati (ultimi 50 valori per ogni metrica)
data_history = {
    "cpu_temp": deque(maxlen=50),
    "cpu_usage": deque(maxlen=50),
    "cpu_freq": deque(maxlen=50),
    "used_memory": deque(maxlen=50),
    "available_memory": deque(maxlen=50),
    "used_disk": deque(maxlen=50),
    "free_disk": deque(maxlen=50),
    "processes": deque(maxlen=50)
}

# Funzione chiamata quando il client si connette
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connesso con successo al broker!")
        client.subscribe(TOPIC)
        print(f"🔔 Sottoscritto al topic: {TOPIC}")
    else:
        print(f"⚠️ Connessione fallita. Codice errore: {rc} - {mqtt.error_string(rc)}")

# Funzione chiamata quando un messaggio viene ricevuto
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"📥 Messaggio ricevuto: {payload}")

        # Aggiunge i nuovi dati al buffer usando la struttura JSON corretta
        data_history["cpu_temp"].append(payload["cpu"]["cpu_temp"])
        data_history["cpu_usage"].append(payload["cpu"]["cpu_usage"])
        data_history["cpu_freq"].append(payload["cpu"]["frequency"])
        data_history["used_memory"].append(payload["memory"]["used"])
        data_history["available_memory"].append(payload["memory"]["available"])
        data_history["used_disk"].append(payload["disk"]["used"])
        data_history["free_disk"].append(payload["disk"]["free"])
        data_history["processes"].append(payload["processes"]["total"])
    
    except Exception as e:
        print(f"❌ Errore nella gestione del messaggio MQTT: {e}")

# Configura il client MQTT
client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set(ca_certs=CA_CERT, tls_version=ssl.PROTOCOL_TLS_CLIENT)
client.on_connect = on_connect
client.on_message = on_message

# Connessione al broker
try:
    client.connect(BROKER_HOST, BROKER_PORT, 60)
    print(f"🚀 Connessione a {BROKER_HOST}:{BROKER_PORT}")
except Exception as e:
    print(f"❌ Errore di connessione: {e}")

# Imposta matplotlib per grafici in tempo reale
fig, axs = plt.subplots(3, 1, figsize=(10, 8))
fig.suptitle("Monitoraggio Raspberry Pi - MQTT")

# Funzione per aggiornare i grafici
def update_graph(frame):
    axs[0].clear()
    axs[1].clear()
    axs[2].clear()

    axs[0].plot(data_history["cpu_usage"], label="CPU Usage (%)", color="r")
    axs[0].plot(data_history["cpu_freq"], label="CPU Frequency (MHz)", color="b")
    axs[0].plot(data_history["cpu_temp"], label="CPU Temp (°C)", color="g")
    axs[0].set_title("CPU")
    axs[0].legend()
    axs[0].grid()

    axs[1].plot(data_history["used_memory"], label="Used RAM (MB)", color="r")
    axs[1].plot(data_history["available_memory"], label="Available RAM (MB)", color="b")
    axs[1].set_title("Memoria RAM")
    axs[1].legend()
    axs[1].grid()

    axs[2].plot(data_history["used_disk"], label="Used Disk (GB)", color="r")
    axs[2].plot(data_history["free_disk"], label="Free Disk (GB)", color="b")
    axs[2].set_title("Disco")
    axs[2].legend()
    axs[2].grid()

    plt.tight_layout()

# Avvia l'animazione in tempo reale
ani = animation.FuncAnimation(fig, update_graph, interval=2000)

# Avvia il loop MQTT in un thread separato
import threading
mqtt_thread = threading.Thread(target=client.loop_forever)
mqtt_thread.start()

# Mostra i grafici
plt.show()
