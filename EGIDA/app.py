from flask import Flask, render_template, jsonify
import json
import subprocess  # Do uruchamiania innych skryptów
import sys  # Do znalezienia ścieżki do interpretera Python
import atexit  # Do wykonywania zadań przy zamykaniu programu

# Nazwa pliku, z którego będziemy czytać dane
DATA_FILE = 'gps_data.json'
# Zmienna do przechowywania procesu potomnego (gps.py)
gps_process = None

app = Flask(__name__)


@app.route('/')
def index():
    """Wyświetla główną stronę HTML."""
    return render_template('index.html')


@app.route('/data')
def get_data():
    """Odczytuje dane z pliku JSON i wysyła je do przeglądarki."""
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            return jsonify(data)
    except (FileNotFoundError, json.JSONDecodeError):
        # Jeśli plik nie istnieje lub jest pusty/uszkodzony, wyślij status oczekiwania
        return jsonify({
            "status": "Oczekiwanie na utworzenie pliku przez gps.py...",
            "fix": "Brak",
            "lat": 0, "lon": 0, "alt": 0, "sats": 0
        })


def kill_gps_process():
    """Funkcja do "zabijania" procesu gps.py przy zamykaniu aplikacji."""
    global gps_process
    if gps_process:
        print("Zamykanie procesu gps.py...")
        gps_process.kill()
        gps_process.wait()
        print("Proces gps.py zamknięty.")


if __name__ == '__main__':
    print("Uruchamianie skryptu gps.py w tle...")
    try:
        # Używamy sys.executable, aby mieć pewność, że używamy tego samego interpretera Python.
        # Popen uruchamia proces i nie czeka na jego zakończenie.
        gps_process = subprocess.Popen([sys.executable, 'gps.py'])

        # Rejestrujemy funkcję, która zabije proces potomny, gdy główny skrypt się zakończy
        atexit.register(kill_gps_process)
        print("Skrypt gps.py uruchomiony pomyślnie.")

    except FileNotFoundError:
        print("BŁĄD KRYTYCZNY: Nie można znaleźć pliku 'gps.py'.")
        print("Upewnij się, że znajduje się on w tym samym folderze co app.py.")
        sys.exit(1)  # Zakończ program, jeśli nie można uruchomić skryptu GPS
    except Exception as e:
        print(f"Wystąpił błąd podczas uruchamiania gps.py: {e}")
        sys.exit(1)

    print("\nUruchamianie serwera Flask.")
    print("Otwórz przeglądarkę i wejdź na http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
