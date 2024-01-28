from machine import UART
import os

def sub_cb(topic, msg):
  print((topic, msg))
  if topic == b'unhan_iot' and msg == b'received':
    print('ESP received hello message')

def connect_and_subscribe():
  global client_id, mqtt_server, topic_sub
  client = MQTTClient(client_id, mqtt_server)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

try:
  client = connect_and_subscribe()
  uart = UART(0, baudrate=9600)
  uart.init(9600, bits=8, stop=1, timeout=1000)
  
except OSError as e:
  restart_and_reconnect()

while True:
  try:
    client.check_msg()
    msg = str({"msg": "hello"})
#     os.dupterm(None, 1)
#     client.publish(topic_pub, msg, qos=0)
    if uart.any():
        data = uart.readline()
        uart.write(data)
        print("got", data)
#         client.publish(topic_pub, data, qos=0)
        if data == b'q':
            break
    os.dupterm(uart, 1)
  except OSError as e:
    restart_and_reconnect()