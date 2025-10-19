import serial
import sys
import json


RADIO_PORT = '/dev/serial0'
# Upewnij się, że prędkość jest zgodna z konfiguracją radia
RADIO_BAUD = 57600
DEFAULT_ALTITUDE = 20.0


def send_data_via_serial(data_to_send):
    """
    Otwiera port szeregowy, wysyła dane w formacie LAT,LON,ALT i zamyka port.
    """
    print(f"[radio.py] Próba wysłania danych przez port {RADIO_PORT}...")
    try:
        # Sprawdzamy, czy mamy potrzebne klucze w słowniku
        if 'lat' in data_to_send and 'lon' in data_to_send:
            lat = data_to_send['lat']
            lon = data_to_send['lon']
            alt = DEFAULT_ALTITUDE
            line_to_send = f"{lat},{lon},{alt}\n"

            with serial.Serial(RADIO_PORT, RADIO_BAUD, timeout=2) as ser:
                ser.write(line_to_send.encode('utf-8'))
                print(f"[radio.py] Pomyślnie wysłano: {line_to_send.strip()}")
        else:
            raise ValueError("Brakujące klucze 'lat' lub 'lon' w danych.")

    except serial.SerialException as e:
        sys.stderr.write(f"BŁĄD portu szeregowego {RADIO_PORT}: {e}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Nieoczekiwany błąd w radio.py: {e}\n")
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            data_from_arg = json.loads(sys.argv[1])
            send_data_via_serial(data_from_arg)
        except json.JSONDecodeError:
            sys.stderr.write("Błąd: Przekazany argument nie jest poprawnym formatem JSON.\n")
            sys.exit(1)
    else:
        sys.stderr.write("Błąd: Skrypt radio.py wymaga danych JSON jako argumentu.\n")
        sys.exit(1)