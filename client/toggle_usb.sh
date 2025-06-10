#!/bin/bash

DEVICE="$1"
ACTION="$2"

if [[ "$ACTION" != "bind" && "$ACTION" != "unbind" ]]; then
    echo "Acción inválida: $ACTION"
    exit 1
fi

echo "$DEVICE" | tee /sys/bus/usb/drivers/usb/"$ACTION"
