#!/usr/bin/env python3

import sys
import os
import mysql.connector
import bnppf
from typing import Dict, Union


accounts: Dict[str, Dict[str, Union[str, int]]] = {}
con = None

db_hostname = os.environ["DB_HOST"]
db_name = os.environ["DB_NAME"]
db_password = os.environ["DB_PASSWORD"]
db_port = os.environ["DB_PORT"]
db_username = os.environ["DB_USER"]

csv_todo = os.environ["CSV_TODO"]
csv_done = os.environ["CSV_DONE"]
csv_error = os.environ["CSV_ERROR"]

for directory in [csv_todo, csv_done]:
    if not os.path.exists(directory):
        print(f"Creating '{directory}'...")
        os.makedirs(directory)

try:
    con = mysql.connector.connect(  # type: ignore
        user=db_username,
        password=db_password,
        host=db_hostname,
        port=db_port,
        database=db_name
    )
    cur = con.cursor()  # type: ignore

    csv_version = None

    for f in [filename for filename in
              sorted(os.listdir(path=csv_todo)) if filename.endswith('.csv')]:
        # Full path
        f = f"{csv_todo}/{f}"

        # Check if file in really a file and that is exists
        if not os.path.isfile(f):
            continue

        print(f'Current: {f}')

        lines = [line.rstrip('\n') for line in
                 open(f, 'r', encoding='utf8', errors='ignore')]

        for line in lines:
            # Skip empty line
            if not line.strip():
                continue

            # First line -> CSV header
            if csv_version is None:
                csv_version = bnppf.get_csv_version(line)
                continue

            transaction = bnppf.BNPPF(csv_version=csv_version)

            # Parse CSV transaction line
            if not transaction.parse(line=line, format='csv'):
                print('ERROR:', transaction.get_all())
                os.rename(f, f.replace(csv_todo, csv_error))
                sys.exit(1)
            # Skipping invalid sequence number
            elif transaction.get_ref() == '':
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
            cur.execute(sql)  # type: ignore
            if account not in accounts:
                accounts[account] = {'count': 0}
            accounts[account]['count'] += 1  # type: ignore

        # Move CSV file to done folder
        os.rename(f, f.replace(csv_todo, csv_done))

        # Commit changes after each file
        con.commit()  # type: ignore
        csv_version = None
    print('--------------------------------------------------------')
    print('Transactions Summary:')
    for k, v in accounts.items():
        print(f" - {k} -> {v['count']}")
    print('--------------------------------------------------------')
except Exception:
    print('Unexpected error:', sys.exc_info())
    sys.exit(1)
finally:
    if con:
        con.close()  # type: ignore
