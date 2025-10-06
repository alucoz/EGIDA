from dronekit import connect
import time

SITL_ADDRESS = 'tcp:127.0.0.1:5762'

print(f"Próba połączenia z {SITL_ADDRESS}...")

try:
    # Ustawiamy krótki timeout, żeby nie czekać 30 sekund
    vehicle = connect(SITL_ADDRESS, wait_ready=True, timeout=15)

    # Jeśli doszło tutaj, to znaczy, że połączenie się udało
    print("\n===================================")
    print("  POŁĄCZENIE Z DRONEM UDANE!")
    print("===================================")
    print(f" Wersja oprogramowania: {vehicle.version}")
    print(f" Status: {vehicle.system_status.state}")
    print(f" Tryb: {vehicle.mode.name}")
    print(f" Uzbrojony: {vehicle.armed}")

    vehicle.close()
    print("\nPołączenie zamknięte. Test zakończony sukcesem.")

except Exception as e:
    print("\n***********************************")
    print("  BŁĄD: POŁĄCZENIE NIEUDANE")
    print(f"  Powód: {e}")
    print("***********************************")