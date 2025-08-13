from flask import Flask, render_template, jsonify, request
import json
import subprocess
import sys
import atexit

# Nazwa pliku z danymi GPS
DATA_FILE = 'gps_data.json'
# Nazwa pliku dla ręcznie dodanego punktu
MANUAL_POINT_FILE = 'manual_point.json'

gps_process = None
app = Flask(__name__)


@app.route('/')
def index():
    """Wyświetla główną stronę HTML."""
    return render_template('index.html')


@app.route('/data')
def get_data():
    """Odczytuje dane GPS z pliku JSON i wysyła je do przeglądarki."""
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            return jsonify(data)
    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify({
            "status": "Oczekiwanie na utworzenie pliku przez gps.py...",
            "fix": "Brak", "lat": 0, "lon": 0, "alt": 0, "sats": 0
        })


@app.route('/save_point', methods=['POST'])
def save_point():
    """
    Odbiera współrzędne, zapisuje je do pliku ORAZ uruchamia skrypt
    radio.py do wysłania ich przez port szeregowy.
    """
    data = request.get_json()
    print(f"[app.py] Otrzymano żądanie /save_point z danymi: {data}")

    if 'lat' in data and 'lon' in data:
        # Krok 1: Zapis do pliku (bez zmian)
        try:
            with open(MANUAL_POINT_FILE, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"[app.py] Pomyślnie zapisano dane do {MANUAL_POINT_FILE}")
        except Exception as e:
            print(f"[app.py] Błąd zapisu do pliku {MANUAL_POINT_FILE}: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

        # Krok 2: Uruchomienie radio.py do wysłania danych
        try:
            print("[app.py] Uruchamianie procesu radio.py...")
            data_as_string = json.dumps(data)

            # === POPRAWKA TUTAJ: Dodajemy encoding='utf-8' ===
            # Wymusza to poprawne dekodowanie odpowiedzi z procesu potomnego.
            result = subprocess.run(
                [sys.executable, 'radio.py', data_as_string],
                capture_output=True, text=True, check=True, encoding='utf-8'
            )
            print(f"[app.py] Odpowiedź z radio.py (stdout): {result.stdout.strip()}")
            return jsonify({
                "status": "success",
                "message": f"Punkt zapisany i wysłany!"
            })
        except FileNotFoundError:
            error_msg = "BŁĄD: Nie można znaleźć pliku 'radio.py'."
            print(f"[app.py] {error_msg}")
            return jsonify({"status": "error", "message": error_msg}), 500
        except subprocess.CalledProcessError as e:
            error_msg = f"Błąd wykonania radio.py: {e.stderr.strip()}"
            print(f"[app.py] {error_msg}")
            return jsonify({"status": "error", "message": error_msg}), 500
        except Exception as e:
            error_msg = f"Nieoczekiwany błąd przy uruchamianiu radio.py: {e}"
            print(f"[app.py] {error_msg}")
            return jsonify({"status": "error", "message": error_msg}), 500

    return jsonify({"status": "error", "message": "Brakujące dane lat/lon"}), 400


def kill_gps_process():
    """Zabija proces gps.py przy zamykaniu aplikacji."""
    global gps_process
    if gps_process:
        print("[app.py] Zamykanie procesu gps.py...")
        gps_process.kill()
        gps_process.wait()
        print("[app.py] Proces gps.py zamknięty.")


if __name__ == '__main__':
    print("[app.py] Uruchamianie skryptu gps.py w tle...")
    try:
        gps_process = subprocess.Popen([sys.executable, 'gps.py'])
        atexit.register(kill_gps_process)
        print("[app.py] Skrypt gps.py uruchomiony pomyślnie.")
    except Exception as e:
        print(f"[app.py] BŁĄD KRYTYCZNY podczas uruchamiania gps.py: {e}")
        sys.exit(1)

    print("\n[app.py] Uruchamianie serwera Flask.")
    print("[app.py] Otwórz przeglądarkę i wejdź na http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
