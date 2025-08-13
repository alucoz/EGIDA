import serial
import sys
import json

# === Konfiguracja portu dla radia telemetrycznego ===
# ZMIEŃ NA WŁAŚCIWY PORT I PRĘDKOŚĆ DLA TWOJEJ TELEMETRII
RADIO_PORT = 'COM5'  # Przykładowy port, MUSI być inny niż GPS!
RADIO_BAUD = 57600  # Przykładowa prędkość


def send_data_via_serial(data_to_send):
    """
    Otwiera port szeregowy, wysyła dane w formacie JSON i zamyka port.
    """
    print(f"[radio.py] Próba wysłania danych przez port {RADIO_PORT}...")
    try:
        # Użycie 'with' gwarantuje, że port zostanie zamknięty nawet w przypadku błędu
        with serial.Serial(RADIO_PORT, RADIO_BAUD, timeout=2) as ser:
            # Konwersja słownika Pythona na string JSON i dodanie znaku nowej linii
            # Znak nowej linii jest ważny, aby odbiorca wiedział, gdzie kończy się komunikat.
            line_to_send = json.dumps(data_to_send) + '\n'

            # Kodowanie stringa do bajtów (wymagane przez pyserial) i wysłanie
            ser.write(line_to_send.encode('utf-8'))

            print(f"[radio.py] Pomyślnie wysłano: {line_to_send.strip()}")

    except serial.SerialException as e:
        # Ten błąd zostanie przechwycony przez app.py i wyświetlony w jego konsoli
        sys.stderr.write(f"BŁĄD portu szeregowego {RADIO_PORT}: {e}\n")
        sys.exit(1)  # Zakończ z kodem błędu
    except Exception as e:
        sys.stderr.write(f"Nieoczekiwany błąd w radio.py: {e}\n")
        sys.exit(1)  # Zakończ z kodem błędu


if __name__ == '__main__':
    # Ten blok pozwala na uruchomienie skryptu z linii komend z argumentami.
    # app.py będzie go tak właśnie uruchamiał.
    # Przykład: python radio.py "{\"lat\": 51.1, \"lon\": 17.2}"
    if len(sys.argv) > 1:
        try:
            # Odczytanie danych (stringa JSON) z argumentu linii komend
            data_from_arg = json.loads(sys.argv[1])
            send_data_via_serial(data_from_arg)
        except json.JSONDecodeError:
            sys.stderr.write("Błąd: Przekazany argument nie jest poprawnym formatem JSON.\n")
            sys.exit(1)
    else:
        sys.stderr.write("Błąd: Skrypt radio.py wymaga danych JSON jako argumentu.\n")
        sys.exit(1)
