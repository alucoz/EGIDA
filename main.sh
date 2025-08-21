#!/bin/bash

# Zaktualizuj listę pakietów i zainstaluj Python3 oraz pip3
echo "Aktualizuję listę pakietów i instaluję python3 oraz pip3..."
if sudo apt update && sudo apt install -y python3 python3-pip; then
    echo "Python3 i pip3 zostały pomyślnie zainstalowane."
else
    echo "Wystąpił błąd podczas instalacji python3/pip3."
    exit 1
fi

# Instalacja pakietów Python
echo "Instaluję pakiety Python: flask oraz pyubx2..."
if pip3 install flask pyubx2; then
    echo "Wszystkie pakiety zostały pomyślnie zainstalowane."
else
    echo "Wystąpił błąd podczas instalacji pakietów."
    exit 1
fi