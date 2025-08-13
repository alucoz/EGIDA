import serial
import json
import time
from pyubx2 import UBXReader

# Nazwa pliku, który będzie naszą "skrzynką pocztową"
DATA_FILE = 'gps_data.json'
# Interwał zapisu do pliku w sekundach
WRITE_INTERVAL = 5

def read_and_save_ubx_data(serial_port, baud_rate):
    """
    Otwiera port szeregowy, ciągle odczytuje dane UBX,
    a co 5 sekund zapisuje najnowszy odczyt do pliku JSON.
    """
    print(f"[gps.py] Uruchamiam odczyt GPS z portu {serial_port}...")

    latest_data = {}
    last_write_time = time.time()

    while True:
        try:
            stream = serial.Serial(serial_port, baud_rate, timeout=3)
            ubr = UBXReader(stream)
            print(f"[gps.py] Połączono z portem {serial_port}. Oczekuję na dane...")

            for (raw_data, parsed_data) in ubr:
                if parsed_data:
                    if parsed_data.identity == 'NAV-PVT':
                        fix_status_str = {0: 'Brak fixa', 1: 'DR Only', 2: '2D-Fix', 3: '3D-Fix'}.get(parsed_data.fixType, 'Inny')
                        latest_data = {
                            "status": "Odbieranie danych",
                            "fix": fix_status_str,
                            "lat": parsed_data.lat,
                            "lon": parsed_data.lon,
                            "alt": parsed_data.hMSL / 1000,
                            "sats": parsed_data.numSV
                        }

                current_time = time.time()
                if latest_data and (current_time - last_write_time >= WRITE_INTERVAL):
                    try:
                        with open(DATA_FILE, 'w') as f:
                            json.dump(latest_data, f)
                        last_write_time = current_time
                        print(f"[gps.py] Zapisano dane do pliku: {latest_data}")
                    except IOError as e:
                        print(f"[gps.py] BŁĄD zapisu do pliku: {e}")

        except serial.SerialException as e:
            print(f"[gps.py] BŁĄD KRYTYCZNY portu '{serial_port}': {e}. Restart za 10s.")
            time.sleep(10)
        except Exception as e:
            print(f"[gps.py] Nieoczekiwany błąd: {e}. Restart za 10s.")
            time.sleep(10)

if __name__ == '__main__':
    PORT_GPS = 'COM3'
    BAUD_RATE_GPS = 115200
    read_and_save_ubx_data(PORT_GPS, BAUD_RATE_GPS)
