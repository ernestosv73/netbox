#!/usr/bin/env python3
"""
nornir_init.py
Inicializa Nornir usando NetBoxInventory2
Filtra únicamente dispositivos Huawei (VRP)
"""

from nornir import InitNornir
import pynetbox
import sys

print("\n=== Inicializando Nornir (Huawei / VRP) ===\n")

try:
    nr = InitNornir(config_file="config.yaml")
except Exception as e:
    print(f"❌ Error inicializando Nornir: {e}")
    sys.exit(1)

# Verificación básica
if not nr.inventory.hosts:
    print("❌ Inventario vacío. Revisar filtros en config.yaml")
    sys.exit(1)

print(f"✅ Nornir inicializado correctamente")
print(f"📦 Dispositivos cargados: {len(nr.inventory.hosts)}\n")

print("📋 Inventario Huawei:\n")

for host in nr.inventory.hosts.values():
    print(f" • {host.name}")
    print(f"   ├─ hostname : {host.hostname}")
    print(f"   ├─ platform : {host.platform}")
    print(f"   └─ site     : {host.data.get('site', 'N/A')}\n")

print("🎯 Inicialización completada\n")
