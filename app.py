from flask import Flask, render_template, jsonify, request
import json
import subprocess
import sys
import atexit
import os  # Dodane dla sprawdzenia, czy gps.py już działa

# Pliki danych
DATA_FILE = 'gps_data.json'
MANUAL_POINT_FILE = 'manual_point.json'

app = Flask(__name__)
gps_process = None  # Zmienna do przechowywania procesu gps.py

def kill_gps_process():
    """Zabija proces gps.py przy zamykaniu aplikacji."""
    global gps_process
    if gps_process and gps_process.poll() is None:  # Sprawdź, czy proces żyje
        print("[app.py] Zamykanie procesu gps.py...")
        gps_process.kill()
        gps_process.wait()
        print("[app.py] Proces gps.py zamknięty.")

@app.route('/')
def index():
    """Wyświetla główną stronę HTML."""
    return render_template('index.html')

@app.route('/data')
def get_data():
    """Odczytuje i zwraca najnowsze dane z pliku gps_data.json."""
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            return jsonify(data)
    except (FileNotFoundError, json.JSONDecodeError):
        # Zwróć domyślne dane, jeśli plik nie istnieje lub jest pusty
        return jsonify({"status": "Oczekiwanie na sygnał GPS...", "fix": "Brak fixa"})

@app.route('/save_point', methods=['POST'])
def save_point():
    """
    Odbiera współrzędne, zapisuje je do pliku ORAZ uruchamia skrypt
    radio.py do wysłania ich przez port szeregowy.
    """
    data = request.get_json()
    print(f"[app.py] Otrzymano żądanie /save_point z danymi: {data}")

    if 'lat' in data and 'lon' in data:
        # Krok 1: Zapis do pliku
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
            result = subprocess.run(
                [sys.executable, 'radio.py', data_as_string],
                capture_output=True, text=True, check=True, encoding='utf-8'
            )
            print(f"[app.py] Odpowiedź z radio.py (stdout): {result.stdout.strip()}")
            if result.stderr:
                print(f"[app.py] Ostrzeżenie z radio.py (stderr): {result.stderr.strip()}")
            return jsonify({
                "status": "success",
                "message": "Punkt zapisany i wysłany!"
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

if __name__ == '__main__':
    # Sprawdź, czy gps.py już działa (unikaj duplikacji)
    gps_running = any('gps.py' in line for line in os.popen('ps -Af').readlines())
    if not gps_running:
        # Uruchom skrypt gps.py jako osobny proces w tle
        print("[app.py] Uruchamianie skryptu gps.py w tle...")
        try:
            gps_process = subprocess.Popen([sys.executable, 'gps.py'])
            atexit.register(kill_gps_process)
            print("[app.py] Skrypt gps.py uruchomiony pomyślnie.")
        except Exception as e:
            print(f"[app.py] BŁĄD KRYTYCZNY podczas uruchamiania gps.py: {e}")
            sys.exit(1)
    else:
        print("[app.py] gps.py już działa – pomijam uruchomienie.")

    print("\n[app.py] Uruchamianie serwera Flask.")
    print(f"[app.py] Otwórz przeglądarkę na innym urządzeniu w sieci i wejdź na http://<IP_RASPBERRY_PI>:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)