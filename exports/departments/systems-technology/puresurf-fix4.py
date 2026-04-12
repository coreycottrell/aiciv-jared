#!/usr/bin/env python3
"""FIX 4: Ensure proxy configuration has protocol field in both keys files.

Also add protocol field to keys.json (profile_manager uses it) since it's missing.
"""
import json, sys

# Fix keys.json (used by profile_manager.py)
keys_file = '/opt/baas/keys.json'
with open(keys_file, 'r') as f:
    keys_data = json.load(f)

changed = False
for name, provider in keys_data.get('proxy_providers', {}).items():
    if 'protocol' not in provider:
        provider['protocol'] = 'http'
        changed = True
        print(f"FIX 4: Added protocol='http' to keys.json provider '{name}'")

if changed:
    with open(keys_file, 'w') as f:
        json.dump(keys_data, f, indent=2)
    print("FIX 4a: keys.json updated with protocol fields")
else:
    print("FIX 4a: keys.json already has protocol fields")

# Verify baas_keys.json format
baas_keys_file = '/opt/baas/baas_keys.json'
with open(baas_keys_file, 'r') as f:
    baas_data = json.load(f)

changed2 = False
for name, provider in baas_data.get('proxy_providers', {}).items():
    if 'protocol' not in provider:
        provider['protocol'] = 'http'
        changed2 = True
        print(f"FIX 4: Added protocol='http' to baas_keys.json provider '{name}'")
    # Ensure port is integer (some have string "10080")
    if isinstance(provider.get('port'), str):
        try:
            provider['port'] = int(provider['port'])
            changed2 = True
            print(f"FIX 4: Fixed port type for baas_keys.json provider '{name}' (str->int)")
        except:
            pass

if changed2:
    with open(baas_keys_file, 'w') as f:
        json.dump(baas_data, f, indent=2)
    print("FIX 4b: baas_keys.json updated")
else:
    print("FIX 4b: baas_keys.json already correct")

# Test that proxy URL can be constructed
for keys_path, label in [(keys_file, 'keys.json'), (baas_keys_file, 'baas_keys.json')]:
    with open(keys_path, 'r') as f:
        d = json.load(f)
    for name, p in d.get('proxy_providers', {}).items():
        if p.get('username') and p.get('password') and p.get('host') and p.get('port'):
            url = f"{p.get('protocol', 'http')}://{p['username']}:{p['password']}@{p['host']}:{p['port']}"
            print(f"  [{label}] {name}: {p.get('protocol','http')}://*:*@{p['host']}:{p['port']} (OK)")
        else:
            print(f"  [{label}] {name}: INCOMPLETE CONFIG")

print("FIX 4: COMPLETE — Proxy configuration verified")
