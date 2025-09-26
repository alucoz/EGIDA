import serial

def odbieraj_dane(port="COM7", baudrate=57600):
    try:
        # Otwórz port szeregowy
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"[INFO] Nawiązano połączenie z {port} przy {baudrate} baud.")

        while True:
            if ser.in_waiting > 0:  # jeśli są dane w buforze
                linia = ser.readline().decode('utf-8', errors='ignore').strip()
                if linia:
                    print(f"Odebrano: {linia}")

    except serial.SerialException as e:
        print(f"[BŁĄD] Nie można otworzyć portu {port}: {e}")
    except KeyboardInterrupt:
        print("\n[INFO] Zatrzymano odbieranie danych.")
    finally:
        try:
            ser.close()
            print("[INFO] Zamknięto port szeregowy.")
        except:
            pass

if __name__ == "__main__":
    odbieraj_dane()
