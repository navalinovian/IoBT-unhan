from machine import Pin, RTC, I2C, SoftI2C
import chacha20poly1305 as ccp
import as_nrf_json as nrf
from imu import MPU6050
from time import sleep, ticks_ms, ticks_diff
import sys
import os
import ujson
import base64

key = bytes.fromhex(
            "c8dac0e4f2d62563360aa88db38b98c4d27d9fb791a3fee0ddc1970e8d24cf5b"
        )
counter = 0x00000001

i2c_mpu = I2C(0, sda=Pin(0), scl=Pin(1))
h = i2c_mpu.scan()
print(h)
imu = MPU6050(i2c_mpu)


def readSensor():
    ax=round(imu.accel.x,2)
    ay=round(imu.accel.y,2)
    az=round(imu.accel.z,2)
    gx=round(imu.gyro.x)
    gy=round(imu.gyro.y)
    gz=round(imu.gyro.z)
    tem=round(imu.temperature,2)

    return {"ax":ax, "ay":ay, "az":az, "gx":gx, "gy":gy, "gz":gz, "tem":tem}

for i in range(105):
    sleep(3)
    try:
        sensorData = str(readSensor())
        nonce = os.urandom(12)
        aad= b"header"
        plaintext = bytes(sensorData, 'utf-8')
        start_encrypt = ticks_ms()
        ciphertext, tag = ccp.chacha20_aead_encrypt(aad, key, nonce, plaintext)
        end_encrypt = ticks_ms()
        print("Encryption Time: ", ticks_diff(end_encrypt, start_encrypt))
        payload = {
            "ct": base64.b64encode(ciphertext),
            "tg": base64.b64encode(tag),
            "nc": base64.b64encode(nonce),
            "ad": aad,
            "count": i
            }
        
        nrf.test(True, payload)
#         print(payload)
    except OSError as e:
        print("Can't read: ", e)
        sys.print_exception(e)



