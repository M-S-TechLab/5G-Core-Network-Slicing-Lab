#!/usr/bin/env python3

"""
5G UE Provisioning and Network Slicing (Open5GS & UERANSIM)

Subscriber profile configuration for three 5G network slices:
  - Slice 1 (SST 1): eMBB  (5QI=6, Priority=4, Bandwidth=1 Gbps / 100 Mbps)
  - Slice 2 (SST 2): URLLC (5QI=1, Priority=1, Bandwidth=100 Mbps)
  - Slice 3 (SST 3): MIoT  (5QI=70, Priority=12, Bandwidth=1 Mbps / 512 Kbps)

Usage:
  python3 provision.py [N]          # Adds N new UEs (default: 1)
  python3 provision.py update-all   # Updates all existing UEs
"""

import os
import sys
import argparse
import yaml
import pymongo

MONGO_URI = 'mongodb://localhost:27017'
DB_NAME = 'open5gs'
CONFIG_DIR = '/home/ubuntu/UERANSIM/config'

BASE_IMSI = 999700000000000
BASE_IMEI = 356938035643800
BASE_IMEISV = 4370816125816150

SLICES = [
    {"sst": 1, "name": "eMBB",  "5qi": 6,  "arp": 4,  "dl": (1, 3),   "ul": (100, 2), "default": True},
    {"sst": 2, "name": "URLLC", "5qi": 1,  "arp": 1,  "dl": (100, 2), "ul": (100, 2), "default": False},
    {"sst": 3, "name": "MIoT",  "5qi": 70, "arp": 12, "dl": (1, 2),   "ul": (512, 1), "default": False},
]

def make_ids(idx):
    """Calcola le credenziali hardware e SIM per l'indice UE specificato."""
    return f"{BASE_IMSI + idx:015d}", f"{BASE_IMEI + idx:015d}", f"{BASE_IMEISV + idx:016d}"

def build_mongo_doc(imsi, imeisv):
    """Costruisce il documento subscriber conforme a Open5GS."""
    return {
        "imsi": imsi,
        "subscribed_rau_tau_timer": 12,
        "network_access_mode": 0,
        "subscriber_status": 0,
        "access_restriction_data": 32,
        "imeisv": imeisv,
        "ambr": {"downlink": {"value": 1, "unit": 3}, "uplink": {"value": 1, "unit": 3}},
        "security": {
            "k": "465B5CE8 B199B49F AA5F0A2E E238A6BC",
            "amf": "8000",
            "opc": "E8ED289D EBA952E4 283B54E8 8E6183CA",
            "sqn": {"high": 0, "low": 1000, "unsigned": False}
        },
        "slice": [
            {
                "sst": s["sst"],
                "default_indicator": s["default"],
                "session": [{
                    "name": "internet",
                    "type": 3,
                    "qos": {
                        "index": s["5qi"],
                        "arp": {
                            "priority_level": s["arp"],
                            "pre_emption_capability": 1 if s["arp"] < 10 else 2,
                            "pre_emption_vulnerability": 1 if s["arp"] < 10 else 2
                        }
                    },
                    "ambr": {
                        "downlink": {"value": s["dl"][0], "unit": s["dl"][1]},
                        "uplink": {"value": s["ul"][0], "unit": s["ul"][1]}
                    }
                }]
            } for s in SLICES
        ]
    }

def build_ueransim_yaml(imsi, imei, imeisv):
    """Costruisce la configurazione del terminale per UERANSIM."""
    return {
        'supi': f'imsi-{imsi}',
        'mcc': '999',
        'mnc': '70',
        'protectionScheme': 0,
        'homeNetworkPublicKey': '5a8d38864820197c3394b92613b20b91633cbd897119273bf8e4a6f4eec0a650',
        'homeNetworkPublicKeyId': 1,
        'routingIndicator': '0000',
        'key': '465B5CE8B199B49FAA5F0A2EE238A6BC',
        'op': 'E8ED289DEBA952E4283B54E88E6183CA',
        'opType': 'OPC',
        'amf': '8000',
        'imei': imei,
        'imeiSv': imeisv,
        'tunNetmask': '255.255.255.0',
        'useNamespace': True,
        'nsNamePrefix': 'ueransim',
        'gnbSearchList': ['192.168.64.12', '127.0.0.1'],
        'uacAic': {'mps': False, 'mcs': False},
        'uacAcc': {'normalClass': 0, 'class11': False, 'class12': False, 'class13': False, 'class14': False, 'class15': False},
        'sessions': [{'type': 'IPv4', 'apn': 'internet', 'slice': {'sst': s['sst']}} for s in SLICES],
        'configured-nssai': [{'sst': s['sst']} for s in SLICES],
        'default-nssai': [{'sst': 1}],
        'integrity': {'IA1': True, 'IA2': True, 'IA3': True},
        'ciphering': {'EA1': True, 'EA2': True, 'EA3': True},
        'integrityMaxRate': {'uplink': 'full', 'downlink': 'full'}
    }

def salva_ue(db, idx):
    """Azione atomica: registra l'UE sia in MongoDB che nel file YAML."""
    imsi, imei, imeisv = make_ids(idx)
    db.subscribers.replace_one({"imsi": imsi}, build_mongo_doc(imsi, imeisv), upsert=True)
    yaml_path = os.path.join(CONFIG_DIR, f"ue{idx}.yaml")
    with open(yaml_path, 'w') as f:
        yaml.dump(build_ueransim_yaml(imsi, imei, imeisv), f, default_flow_style=False, sort_keys=False)
    print(f"  [✓] UE {idx:02d} configurato: IMSI={imsi} -> MongoDB & {yaml_path}")

def main():
    parser = argparse.ArgumentParser(description="Provisioning UE 5G per Open5GS e UERANSIM")
    parser.add_argument("target", nargs="?", default="1", help="Numero di UE da aggiungere oppure 'update-all' (default: 1)")
    parser.add_argument("--update-all", action="store_true", help="Aggiorna tutti gli UE già presenti")
    args = parser.parse_args()

    is_update_all = args.update_all or (args.target == "update-all")

    try:
        db = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)[DB_NAME]
        db.command('ping')
    except Exception as e:
        sys.exit(f"Errore connessione MongoDB ({e}). Assicurati che sia attivo: sudo systemctl start mongod")

    if is_update_all:
        subs = list(db.subscribers.find({}, {"imsi": 1}))
        indici = [int(s["imsi"]) - BASE_IMSI for s in subs if s.get("imsi", "").isdigit()]
        print(f"Aggiornamento di {len(indici)} UE esistenti...")
    else:
        try:
            count = int(args.target)
        except ValueError:
            sys.exit("Argomento non valido. Usa un numero (es. 2) oppure 'update-all'.")
        last_sub = db.subscribers.find_one({}, sort=[("imsi", pymongo.DESCENDING)])
        start = (int(last_sub["imsi"]) - BASE_IMSI + 1) if (last_sub and last_sub.get("imsi", "").isdigit()) else 1
        indici = range(start, start + count)
        print(f"Creazione di {count} nuovo/i UE (indice di partenza: {start})...")

    for idx in indici:
        salva_ue(db, idx)

    print("Operazione completata!")

if __name__ == '__main__':
    main()
