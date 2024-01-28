from machine import Pin, UART
import as_nrf_json as nrf
from time import sleep, ticks_ms, ticks_diff

uart0 = UART(0, baudrate=38400, tx=Pin(12), rx=Pin(13))

while True:
    try:
        res = nrf.test(False)
        print("Raw Received Data: ",res)
        uart0.write(res)
        uart0.flush()
    except OSError as e:
        print("Can't read: ", e)
        sys.print_exception(e)



