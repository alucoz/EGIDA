import serial
import time
from dronekit import connect, VehicleMode, Command, APIException
from pymavlink import mavutil

# --- Konfiguracja ---
# === ZMIEŃ NA WŁAŚCIWY PORT! ===
# Port, na którym LattePanda odbiera dane z RPi (sprawdź w Menedżerze Urządzeń)
SERIAL_PORT_IN = "COM4"
SERIAL_BAUDRATE = 57600

# === ZMIEŃ NA WŁAŚCIWY PORT! ===
# Adres połączenia z FIZYCZNYM dronem przez radio MAVLink
# To będzie port COM radia telemetrycznego podłączonego do LattePanda
CONNECTION_STRING = 'COM5'
# Prędkość musi być zgodna z konfiguracją radia MAVLink (zwykle 57600)
CONNECTION_BAUDRATE = 57600
TAKEOFF_ALTITUDE = 10.0

# --- Zmienne globalne ---
vehicle = None
mission_started = False

def connect_to_vehicle():
    """Funkcja do łączenia się z fizycznym pojazdem."""
    global vehicle
    print(f"Próba połączenia z dronem przez: {CONNECTION_STRING} z prędkością {CONNECTION_BAUDRATE}...")
    try:
        vehicle = connect(CONNECTION_STRING, baud=CONNECTION_BAUDRATE, wait_ready=True, timeout=60)
        print("\n===================================")
        print("  POŁĄCZENIE Z DRONEM UDANE!")
        print("===================================")
        return True
    except Exception as e:
        print(f"\nBŁĄD: Nie udało się połączyć z dronem: {e}")
        return False

def upload_mission(lat, lon, alt):
    """Przygotowuje i wgrywa misję (TYLKO WAYPOINT)."""
    cmds = vehicle.commands
    cmds.clear()

    # Do misji dodajemy już tylko punkt docelowy. Startem zajmie się skrypt.
    cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                     mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0,
                     lat, lon, alt))

    print("Przygotowano misję z 1 punktem (WAYPOINT).")
    print("Wgrywanie misji na drona...")
    cmds.upload()
    time.sleep(1)  # Daj dronowi chwilę na przetworzenie
    print(f"[MISSION] Zaplanowano/zaktualizowano lot do: lat={lat}, lon={lon}, alt={alt}")

def parse_coords(line):
    """Przetwarza tekst na współrzędne."""
    try:
        parts = line.strip().split(",")
        if len(parts) == 3:
            return float(parts[0]), float(parts[1]), float(parts[2])
    except Exception:
        return None

# --- Główna pętla programu ---
if connect_to_vehicle():
    try:
        ser = serial.Serial(SERIAL_PORT_IN, SERIAL_BAUDRATE, timeout=1)
        print(f"[OK] Otwarty port szeregowy: {SERIAL_PORT_IN}")
    except Exception as e:
        print(f"[ERR] Nie udało się otworzyć {SERIAL_PORT_IN}: {e}")
        ser = None

    if ser:
        print("\nOczekiwanie na dane z portu szeregowego...")
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode("utf-8").strip()
                print(f"\nUzyskałem nowe dane: {line}")
                coords = parse_coords(line)

                if coords:
                    lat, lon, alt = coords
                    print(f"[DATA] Odebrano punkt: {lat}, {lon}, {alt}")

                    if not mission_started:
                        # --- PIERWSZY START ---
                        print("\n--- ROZPOCZYNANIE PIERWSZEJ MISJI ---")

                        while not vehicle.is_armable:
                            print(" Czekam, aż dron będzie gotowy do lotu (armable)...")
                            time.sleep(1)

                        print(" Ustawiam tryb GUIDED...")
                        vehicle.mode = VehicleMode("GUIDED")
                        while vehicle.mode.name != "GUIDED": time.sleep(0.5)

                        print(" Uzbrajam drona...")
                        vehicle.armed = True
                        while not vehicle.armed: time.sleep(0.5)

                        print(f" Dron uzbrojony! Wydaję komendę startu na {TAKEOFF_ALTITUDE}m...")
                        vehicle.simple_takeoff(TAKEOFF_ALTITUDE)

                        # Czekaj na osiągnięcie wysokości startowej
                        while True:
                            current_altitude = vehicle.location.global_relative_frame.alt
                            print(f"  Aktualna wysokość: {current_altitude:.2f}m")
                            if current_altitude >= TAKEOFF_ALTITUDE * 0.95:
                                print(" Osiągnięto wysokość startową!")
                                break
                            time.sleep(1)

                        print("\nWGrywam misję i przełączam w tryb AUTO...")
                        upload_mission(lat, lon, alt)
                        vehicle.mode = VehicleMode("AUTO")

                        mission_started = True
                        print("\n[SUCCESS] Misja rozpoczęta. Dron jest w locie w trybie AUTO.")

                    else:
                        # --- AKTUALIZACJA MISJI W LOCIE ---
                        print("\n--- AKTUALIZOWANIE MISJI W LOCIE ---")
                        upload_mission(lat, lon, alt)
                        print("[SUCCESS] Misja zaktualizowana.")

            time.sleep(0.2)
else:
    print("Zamykanie skryptu z powodu błędu połączenia.")