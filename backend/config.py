#!/usr/bin/env python
# encoding: utf-8
# Configuration file for Suricata Rule Generator

import os

# API Configuration
API_KEY = os.getenv('AI_API_KEY', 'fk168504229.k2h9hyebSX7c_UzjTA5U5T0t_3IzR10124707b23')
AI_MODEL = os.getenv('AI_MODEL', '360gpt-pro')

# Database Configuration
DB_PATH = os.getenv('DB_PATH', os.path.join(os.path.dirname(__file__), 'suricata_rules.db'))

# Suricata Configuration (for Linux/Kali environment)
SURICATA_CONFIG = {
    'rules_dir': os.getenv('SURICATA_RULES_DIR', '/var/lib/suricata/rules'),
    'config_file': os.getenv('SURICATA_CONFIG', '/etc/suricata/suricata.yaml'),
    'log_dir': os.getenv('SURICATA_LOG_DIR', '/var/log/suricata'),
    'pcap_dir': os.getenv('PCAP_DIR', '/home/kali/pcap_check')
}

# SSH Configuration (for Windows to connect to Kali VM)
SSH_CONFIG = {
    'enabled': os.getenv('SSH_ENABLED', 'false').lower() == 'true',
    'host': os.getenv('SSH_HOST', ''),
    'user': os.getenv('SSH_USER', 'kali'),
    'key': os.getenv('SSH_KEY', '')
}

# Flask Configuration
FLASK_CONFIG = {
    'host': os.getenv('FLASK_HOST', '0.0.0.0'),
    'port': int(os.getenv('FLASK_PORT', 5000)),
    'debug': os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
}
