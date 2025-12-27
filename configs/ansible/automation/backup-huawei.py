#!/usr/bin/env python3
"""
backup_simple.py - Versión corregida
"""
from nornir import InitNornir
from nornir_netmiko import netmiko_send_command
import pynetbox
import os
from datetime import datetime

# 1. Solicitar credenciales (sin .env por simplicidad)
print("=== Huawei Backup Simple ===\n")

netbox_url = input("URL de Netbox (ej: http://10.0.0.100:8000): ").strip()
netbox_token = input("Token de Netbox: ").strip()
ssh_username = input("Usuario SSH: ").strip()
ssh_password = input("Password SSH: ").strip()

# 2. Conectar a Netbox
try:
    print("\nConectando a Netbox...")
    nb = pynetbox.api(netbox_url, token=netbox_token)
    nb.http_session.verify = False
    
    # Obtener dispositivos Huawei activos
    devices = nb.dcim.devices.filter(manufacturer="huawei", status="active")
    device_list = list(devices)
    
    if not device_list:
        print("❌ No se encontraron dispositivos Huawei activos")
        exit(1)
    
    print(f"✅ Encontrados {len(device_list)} dispositivos Huawei")
    
except Exception as e:
    print(f"❌ Error conectando a Netbox: {e}")
    exit(1)

# 3. Crear directorio de backups
backup_dir = "backups"
os.makedirs(backup_dir, exist_ok=True)

# 4. Crear archivos de inventario para Nornir
# hosts.yaml
hosts_content = ""
for device in device_list:
    # Obtener IP
    if device.primary_ip:
        ip = str(device.primary_ip.address).split('/')[0]
    else:
        ip = device.name
    
    hosts_content += f"{device.name}:\n"
    hosts_content += f"  hostname: {ip}\n"
    hosts_content += f"  platform: huawei\n"
    hosts_content += f"  username: {ssh_username}\n"
    hosts_content += f"  password: {ssh_password}\n"
    hosts_content += f"  port: 22\n"
    hosts_content += f"  data:\n"
    hosts_content += f"    site: {device.site.name if device.site else 'N/A'}\n"
    hosts_content += f"    model: {device.device_type.model if device.device_type else 'N/A'}\n\n"

# groups.yaml
groups_content = """huawei:
  platform: huawei
  connection_options:
    netmiko:
      extras:
        device_type: huawei
"""

# defaults.yaml (opcional, vacío)
defaults_content = ""

# Escribir archivos
with open("hosts.yaml", "w") as f:
    f.write(hosts_content)

with open("groups.yaml", "w") as f:
    f.write(groups_content)

with open("defaults.yaml", "w") as f:
    f.write(defaults_content)

# config.yaml
config_content = """runner:
  plugin: threaded
  options:
    num_workers: 5

inventory:
  plugin: SimpleInventory
  options:
    host_file: "hosts.yaml"
    group_file: "groups.yaml"
    defaults_file: "defaults.yaml"
"""

with open("config.yaml", "w") as f:
    f.write(config_content)

print("✅ Archivos de inventario creados")

# 5. Inicializar Nornir CORRECTAMENTE
try:
    print("\nInicializando Nornir...")
    nr = InitNornir(config_file="config.yaml")
    
    print(f"✅ Nornir inicializado. {len(nr.inventory.hosts)} dispositivos cargados")
    
    # Mostrar dispositivos
    print("\n📋 Dispositivos encontrados:")
    for host_name, host in nr.inventory.hosts.items():
        print(f"  • {host_name} ({host.hostname})")
    
except Exception as e:
    print(f"❌ Error inicializando Nornir: {e}")
    exit(1)

# 6. Función de backup
def backup_task(task):
    print(f"\n[{task.host.name}] Conectando...")
    
    try:
        # Obtener configuración
        result = task.run(
            task=netmiko_send_command,
            command_string="display current-configuration",
            name="Obtener configuración"
        )
        
        # Crear nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{backup_dir}/{task.host.name}_{timestamp}.cfg"
        
        # Guardar backup
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# Backup: {datetime.now()}\n")
            f.write(f"# Device: {task.host.name}\n")
            f.write(f"# IP: {task.host.hostname}\n")
            f.write("#" * 50 + "\n\n")
            f.write(result.result)
        
        print(f"  ✅ Backup guardado: {filename}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:100]}")
        return False

# 7. Ejecutar backups
print(f"\n{'='*50}")
print("INICIANDO BACKUPS...")
print("="*50)

results = nr.run(task=backup_task)

# 8. Mostrar resumen
print(f"\n{'='*50}")
print("RESUMEN")
print("="*50)

success = 0
for host_name, result in results.items():
    if not result[0].failed:
        success += 1
        print(f"✅ {host_name}")
    else:
        print(f"❌ {host_name}: {result[0].exception}")

print(f"\n✅ {success}/{len(device_list)} backups exitosos")

# 9. Limpiar archivos temporales (opcional)
import os
for file in ["hosts.yaml", "groups.yaml", "defaults.yaml", "config.yaml"]:
    if os.path.exists(file):
        os.remove(file)
        print(f"🗑️  Archivo temporal eliminado: {file}")

print("\n🎉 Proceso completado!")
