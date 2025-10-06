import subprocess

# Lista plików do uruchomienia
scripts = ['app.py', 'gps.py', 'radio.py']

# Przechowuj procesy
processes = []

# Uruchom każdy skrypt jako osobny proces
for script in scripts:
    try:
        p = subprocess.Popen(['python', script])
        processes.append(p)
        print(f"Uruchomiono {script} (PID: {p.pid})")
    except Exception as e:
        print(f"Błąd przy uruchamianiu {script}: {e}")

# Opcjonalnie: czekaj aż wszystkie procesy się zakończą
for p in processes:
    p.wait()
    print(f"Proces (PID: {p.pid}) zakończony")
