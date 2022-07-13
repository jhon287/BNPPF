#!/usr/bin/env python3

import sys
import os
import configparser

from bnppf import BNPPF, get_csv_version
from mysql.connector import MySQLConnection
from typing import Dict

accounts: Dict[str, Dict[str, int]] = {}
settings: Dict[str, Dict[str, str]] = {}
cnx: MySQLConnection

try:
    config = configparser.ConfigParser()
    config.read('./conf/settings.ini')
    for section in config.sections():
        if section not in settings:
            settings[section] = {}
        for key in config[section]:
            settings[section][key] = config[section][key]
except Exception as e:
    print(f'OS error: {e}')
    sys.exit(1)

for directory in [settings['directory']['in'], settings['directory']['done']]:
    if not os.path.exists(directory):
        print(f"Creating '{directory}'...")
        os.makedirs(directory)

try:
    cnx = MySQLConnection(
        user=settings['database']['user'],
        password=settings['database']['password'],
        host=settings['database']['server'],
        port=settings['database']['port'],
        database=settings['database']['name']
    )
    cur = cnx.cursor()

    csv_version: int = 0

    for f in sorted(os.listdir(settings['directory']['in'])):
        # Full path
        f = f"{settings['directory']['in']}/{f}"

        # Check if file in really a file and that is exists
        if not os.path.isfile(f):
            continue

        print(f'Current: {f}')

        lines = [line.rstrip('\n') for line in
                 open(f, 'r', encoding='utf8', errors='ignore')]

        for line in lines:
            # Empty line ?
            if not line.strip():
                continue

            # First line -> CSV header
            if csv_version == 0:
                csv_version = get_csv_version(line)
                continue

            transaction: BNPPF = BNPPF(csv_version=csv_version)

            # Parse CSV transaction line
            if not transaction.parse(line=line, format='csv'):
                print(f'ERROR:{str(transaction.get_all())}')
                sys.exit(1)
            # Skipping invalid sequence number
            elif not transaction.get_ref():
                continue

            account: str = transaction.get_account()
            sql = 'CALL addTransaction("{ref}", "{date}", {amount}, ' \
                  '"{currency}", "{type}", "{detail}", "{account}");'.format(
                    ref=transaction.get_ref(),
                    date=transaction.get_date(),
                    amount=transaction.get_amount(),
                    currency=transaction.get_currency(),
                    type=transaction.get_type(),
                    detail=transaction.get_detail(),
                    account=account,
                  )
            cur.execute(sql)
            if account not in accounts:
                accounts[account] = {'count': 0}
            accounts[account]['count'] += 1

        # Move CSV file to done folder
        os.rename(f, f.replace(settings['directory']['in'],
                               settings['directory']['done']))

        # Commit changes after each file
        cnx.commit()
        csv_version = 0
    print('--------------------------------------------------------')
    print('Transactions Summary:')
    for k, v in accounts.items():
        print(f" - {k} -> {v['count']}")
    print('--------------------------------------------------------')
except Exception:
    print('Unexpected error:', sys.exc_info())
    sys.exit(1)
finally:
    if cnx:
        cnx.close()
