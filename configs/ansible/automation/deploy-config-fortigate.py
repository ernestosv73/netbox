#!/usr/bin/env python3
"""
deploy_fortigate_netbox.py - Aplica configuración renderizada a FortiGate desde NetBox
"""

import os
import requests
from netmiko import ConnectHandler

# === Configuración ===
NETBOX_URL = "http://192.168.117.135:8000"
NETBOX_TOKEN = "c889397e6b09cfd1556378047213220b2c47b7e8"
DEVICE_ID = 4  # ID del Firewall FortiGate en NetBox

DEVICE = {
    "device_type": "fortinet",          # ← Cambiado
    "host": "172.80.80.6",             # ← Cambiado
    "username": "admin",
    "password": "admin",
    "timeout": 10,
}

def get_rendered_config() -> str:
    url = f"{NETBOX_URL}/api/dcim/devices/{DEVICE_ID}/render-config/"
    headers = {
        "Authorization": f"Token {NETBOX_TOKEN}",
        "Accept": "text/plain",
    }
    print("📡 Solicitando configuración renderizada a NetBox...")
    resp = requests.post(url, headers=headers)
    resp.raise_for_status()
    
    if resp.text.strip().startswith("{"):
        raise RuntimeError("❌ ¡Se recibió JSON! Algo está mal en la solicitud.")
    
    return resp.text

def main():
    config_text = get_rendered_config()
    print("✅ Configuración recibida. Enviando al dispositivo...\n")

    conn = ConnectHandler(**DEVICE)
    try:
        # FortiGate: entrar en modo config
        print("🔧 Entrando en modo configuración...")
        conn.send_command("config system global", expect_string=r"#")

        # Enviar comandos línea por línea (FortiGate no soporta bloques grandes)
        commands = [
            line.strip()
            for line in config_text.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]

        print(f"📤 Enviando {len(commands)} comandos...")
        for cmd in commands:
            # Saltar líneas de edición de interfaz (ya están en modo global)
            if cmd.startswith("config system interface"):
                continue
            if cmd == "end":
                continue
            if "edit" in cmd or "next" in cmd:
                continue
            # Solo enviar comandos de configuración real
            if cmd.startswith("set "):
                output = conn.send_command(cmd, expect_string=r"#")
                print(f"  → {cmd}")

        # Guardar configuración
        print("\n💾 Guardando configuración...")
        save_out = conn.send_command("execute write memory")
        print(save_out)

    finally:
        conn.disconnect()
        print("\n✅ ¡Proceso completado!")

if __name__ == "__main__":
    main()
