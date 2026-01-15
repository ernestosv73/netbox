#!/usr/bin/env python3
"""
deploy_fortigate_netbox.py - Versión final para FortiOS con 'execute cfg save'
"""

import os
import requests
from netmiko import ConnectHandler

NETBOX_URL = "http://192.168.117.135:8000"
NETBOX_TOKEN = "c889397e6b09cfd1556378047213220b2c47b7e8"
DEVICE_ID = 4

DEVICE = {
    "device_type": "fortinet",
    "host": "172.80.80.6",
    "username": "admin",
    "password": "admin",
    "timeout": 10,
}

def get_rendered_config() -> str:
    url = f"{NETBOX_URL}/api/dcim/devices/{DEVICE_ID}/render-config/"
    headers = {"Authorization": f"Token {NETBOX_TOKEN}", "Accept": "text/plain"}
    resp = requests.post(url, headers=headers)
    resp.raise_for_status()
    if resp.text.strip().startswith("{"):
        raise RuntimeError("❌ ¡Se recibió JSON!")
    return resp.text

def main():
    config_text = get_rendered_config()
    print("✅ Configuración recibida. Enviando al dispositivo...\n")

    conn = ConnectHandler(**DEVICE)
    try:
        # Preparar comandos (sin comentarios)
        commands = [line.rstrip() for line in config_text.splitlines() 
                   if line.strip() and not line.strip().startswith("#")]
        
        print(f"📤 Enviando {len(commands)} comandos...")
        output = conn.send_config_set(commands, cmd_verify=False, exit_config_mode=False)
        print(output)

        # Salir del modo config (volver a CLI raíz)
        print("\n🔙 Saliendo del modo configuración...")
        conn.send_command("end", expect_string=r"#")

        # Guardar configuración (comando específico de tu FortiGate)
        print("💾 Guardando configuración...")
        save_out = conn.send_command("execute cfg save", expect_string=r"#")
        print(save_out)

    finally:
        conn.disconnect()
        print("\n✅ ¡Proceso completado!")

if __name__ == "__main__":
    main()
