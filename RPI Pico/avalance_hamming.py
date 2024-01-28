from machine import Pin, RTC, I2C, SoftI2C
import chacha20poly1305 as ccp
import as_nrf_json as nrf
from imu import MPU6050
from bmp180 import BMP180
from time import sleep, ticks_ms, ticks_diff
import sys
import os
import ujson
import base64
import random
import binascii


key = bytes.fromhex(
            "c8dac0e4f2d62563360aa88db38b98c4d27d9fb791a3fee0ddc1970e8d24cf5b"
        )
counter = 0x00000001

i2c_mpu = I2C(0, sda=Pin(0), scl=Pin(1))
imu = MPU6050(i2c_mpu)
array = []

def hamming_distance(bytes1, bytes2):
    """Calculate the Hamming distance between two byte arrays."""
    return sum(bin(b1 ^ b2).count('1') for b1, b2 in zip(bytes1, bytes2))

def changeOneBit(nonce):
    nonce_bytes = list(nonce)
    byte_index= random.randint(0,11)
    bit_index = random.randint(0,7)
    bitmask = 1 << bit_index
    nonce_bytes[byte_index] ^= bitmask
    modified_nonce = bytes(nonce_bytes)
    return modified_nonce

def readSensor():
    ax=round(imu.accel.x,2)
    ay=round(imu.accel.y,2)
    az=round(imu.accel.z,2)
    gx=round(imu.gyro.x)
    gy=round(imu.gyro.y)
    gz=round(imu.gyro.z)
    tem=round(imu.temperature,2)

    return {"ax":ax, "ay":ay, "az":az, "gx":gx, "gy":gy, "gz":gz, "tem":tem}

for i in range(1, 100):
    try:
        sensorData = str(readSensor())
        nonce = os.urandom(12)
#         print("Key: ",key)
#         print("Counter: ", counter)
#         print("Nonce: ",str(binascii.hexlify(nonce)))
        
        aad= b"Encrypt on RPI pico"
#         print("Additional data: ",aad)
        
        plaintext = bytes(sensorData, 'utf-8')
#         print("Plaintext: ", plaintext)
#         print("Length Plaintext: ", len(plaintext))
        
        modified_nonce = changeOneBit(nonce)
#         print("Modified_nonce: ", str(binascii.hexlify(modified_nonce)))
        
        start_encrypt = ticks_ms()
        ciphertext, tag = ccp.chacha20_aead_encrypt(aad, key, nonce, plaintext)
        end_encrypt = ticks_ms()
#         print("Encryption Time: ", ticks_diff(end_encrypt, start_encrypt))
#         print("Chipertext: ", ciphertext)
#         print("Tag: ", tag)
        
        start_encrypt = ticks_ms()
        mod_ciphertext, mod_tag = ccp.chacha20_aead_encrypt(aad, key, modified_nonce, plaintext)
        end_encrypt = ticks_ms()
#         print("Modified Encryption Time: ", ticks_diff(end_encrypt, start_encrypt))
#         print("Modified nonce Chipertext: ", mod_ciphertext)
#         print("Modified nonce Tag: ", mod_tag)
        

        hamming_dist = hamming_distance(ciphertext, mod_ciphertext)
        
        total_bits = len(ciphertext) * 8
        percentage_difference = (hamming_dist / total_bits) * 100
        
        payload = {
            "nc": base64.b64encode(nonce),
            "mnc":base64.b64encode(modified_nonce),
            "pt": plaintext,
            "ct": base64.b64encode(ciphertext),
            "mct": base64.b64encode(mod_ciphertext),
            "ac":percentage_difference
            }
        print(payload)
        array.append(percentage_difference)        
        
    except OSError as e:
        print("Can't read: ", e)
        sys.print_exception(e)
        
print("Average:", sum(array)/len(array))
print("DONE!")