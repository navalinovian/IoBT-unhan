import os
from time import ticks_ms, ticks_diff
import chacha20poly1305 as ccp
import base64

key = bytes.fromhex(
            "c8dac0e4f2d62563360aa88db38b98c4d27d9fb791a3fee0ddc1970e8d24cf5b"
        )
counter = 0x00000001

while True:
    nonce = os.urandom(12)
    aad= b"Encrypt on RPI pico"
    raw_pt = "a"*8192
    plaintext = bytes(raw_pt, 'utf-8')
    start_encrypt = ticks_ms()
    ciphertext, tag = ccp.chacha20_aead_encrypt(aad, key, nonce, plaintext)
    end_encrypt = ticks_ms()
    print("Encryption time: ", ticks_diff(end_encrypt, start_encrypt))
    start_decrypt = ticks_ms()
    plaintext = ccp.decrypt_and_verify(key, nonce, ciphertext, tag, aad)
    end_decrypt = ticks_ms()
    
    print("Decryption time: ", ticks_diff(end_decrypt, start_decrypt))