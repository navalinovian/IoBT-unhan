# as_nrf_json.py Test script for as_nrf_stream

# (C) Peter Hinch 2020
# Released under the MIT licence

import uasyncio as asyncio
import ujson
import time
from as_nrf_stream import Master, Slave
from asconfig import config_master, config_slave  # Hardware configuration
import base64
import chacha20poly1305 as ccp


async def sender(device):
    ds = [0, 0]  # Data object for transmission
    swriter = asyncio.StreamWriter(device, {})
    while True:
        s = ''.join((ujson.dumps(ds), '\n'))
        swriter.write(s.encode())  # convert to bytes
        await swriter.drain()
        await asyncio.sleep(5)
        ds[0] += 1  # Record number
        ds[1] = device.t_last_ms()

async def receiver(device):
    sreader = asyncio.StreamReader(device)
    while True:
        res = await sreader.readline()  # Can return b''
        if res:
            try:
                dat = ujson.loads(res)
#                 print(dat)
            except ValueError:  # Extremely rare case of data corruption. See docs.
                print("val error, data corrupt")
                pass
            else:
#                 print('pelase wait')
                key = bytes.fromhex("c8dac0e4f2d62563360aa88db38b98c4d27d9fb791a3fee0ddc1970e8d24cf5b")
                nonce = base64.b64decode(dat['nc'])
#                 print(nonce)
                ciphertext = base64.b64decode(dat['ct']+'==')
                mac = base64.b64decode(dat['tg'])
                aad = dat['ad']
                aad = bytes(aad, "utf-8")
                
                start_decrypt = time.ticks_ms()
                plaintext = ccp.decrypt_and_verify(key, nonce, ciphertext, mac, aad)
                end_decrypt = time.ticks_ms()
                
                print("Decryption time: ", time.ticks_diff(end_decrypt, start_decrypt))
                print("Decrypted Text: ",plaintext)
                
            return res

async def fail_detect(device):
    while True:
        if device.t_last_ms() > 20000:
            print('Remote outage')
            
            while device.t_last_ms() > 20000:
                await asyncio.sleep(1)
            print('Remote has reconnected')
            
        await asyncio.sleep(1)
        break


async def main(master):
    global tstart
    tstart = time.time()
    # This line is the only *necessary* diffference between master and slave:
    device = Master(config_master) if master else Slave(config_slave)
    asyncio.create_task(sender(device))
    res = await asyncio.create_task(receiver(device))
    await fail_detect(device)
    return res

def test(master):
    try:
        return asyncio.run(main(master))
    finally:  # Reset uasyncio case of KeyboardInterrupt
        asyncio.new_event_loop()

msg = '''Test script for as_nrf_stream driver for nRF24l01 radios.
On master issue
as_nrf_json.test(True)
On slave issue
as_nrf_json.test(False)
'''
print(msg)