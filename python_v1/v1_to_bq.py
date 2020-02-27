#!/usr/bin/env

import paho.mqtt.client as paho
import queue
import datetime
from time import sleep
import threading
from google.cloud import bigquery
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file("scottgale.json")

mqtt_host = 'air.eng.utah.edu'
mqtt_port = 8883
mqtt_keep_alive = 60
mosquitto_username = 'sensor'
mosquitto_password = 'PaG06pSo43oM4Cx'
cert_path = 'C:/Users/scott/Downloads/ca_airu.crt'
work_to_do = True                   # used as a variable to keep the thread looping

# BigQuery connection configuration **************************************************
project_id = 'scottgale'
bq_client = bigquery.Client(credentials=credentials, project=project_id)
dataset_id = 'airu_dataset_iot'
table_id = 'v1_test'
table_ref = bq_client.dataset(dataset_id).table(table_id)
table = bq_client.get_table(table_ref)
# ************************************************************************************

# data structure for subscribe messages
q = queue.Queue(maxsize=0)  # No limit on size


def on_connect(client, userdata, flags, rc):
    # print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("airu/influx", 1)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # print(str(msg.payload))
    packet = str(msg.payload).split(',')
    packet[1] = 'M' + packet[1][3:]

    data = {                                    # format the relevant data from the payload
        'DEVICE_ID': packet[1],
        'TIMESTAMP': datetime.datetime.now(),
        'PM1': packet[7][4:],
        'PM25': packet[8][6:],
        'PM10': packet[9][5:],
        'TEMP': packet[10][12:],
        'HUM': packet[11][9:],
        'CO': packet[12][3:],
        'NOX': packet[13][3:],
        'LAT': packet[5][9:],
        'LON': packet[6][10:],
        'ALT': packet[4][9:],
        'VER': 1
    }
    # print(data)
    q.put(data)                                 # insert data into the q


def worker_thread_function():
    while work_to_do:
        while not q.empty():
            data = q.get()
            # insert data into bigquery
            row_to_insert = [data]
            errors = bq_client.insert_rows(table, row_to_insert)
        sleep(.010)

# ******************* BEGIN EXECUTION ***********************************************************
v1_client = paho.Client('v1_bq')
v1_client.on_connect = on_connect
v1_client.on_message = on_message
v1_client.tls_set(cert_path)
v1_client.username_pw_set(mosquitto_username, mosquitto_password)
v1_client.connect(mqtt_host, mqtt_port, mqtt_keep_alive)

# SETUP WORKER THREAD **************************************************************************
worker_thread = threading.Thread(target=worker_thread_function, daemon=True)
worker_thread.start()

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
v1_client.loop_forever()






