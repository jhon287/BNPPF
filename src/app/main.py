"""Main application that instantiate BNPPF class."""

from typing import Dict, Union
import sys
import os
from mysql.connector import MySQLConnection, connect  # type: ignore
import bnppf


accounts: Dict[str, Dict[str, Union[str, int]]] = {}
con: MySQLConnection = MySQLConnection()

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
    con = connect(  # type: ignore
        user=db_username,
        password=db_password,
        host=db_hostname,
        port=db_port,
        database=db_name
    )
    cur = con.cursor()  # type: ignore

    csv_version: int = 0

    for f in [filename for filename in
              sorted(os.listdir(path=csv_todo)) if filename.endswith('.csv')]:
        # Full path
        f = f"{csv_todo}/{f}"

        # Check if file in really a file and that is exists
        if not os.path.isfile(f):
            continue

        print(f'Current: {f}')

        # pylint: disable=consider-using-with
        lines = [line.rstrip('\n') for line in
                 open(f, 'r', encoding='utf8', errors='ignore')]

        for line in lines:
            # Skip empty line
            if not line.strip():
                continue

            # First line -> CSV header
            if csv_version == 0:
                csv_version: int = bnppf.get_csv_version(line)
                continue

            trx: bnppf.BNPPF = bnppf.BNPPF(csv_version=csv_version)

            # Parse CSV transaction line
            if not trx.parse(line=line, file_format='csv'):
                print('ERROR:', trx.get_all())
                os.rename(f, f.replace(csv_todo, csv_error))
                sys.exit(1)
            # Skipping invalid sequence number
            elif trx.get_ref() == '':
                continue

            account: str = trx.get_account()
            sql: str = (
                f'CALL addTransaction("{trx.get_ref()}", "{trx.get_date()}", '
                f'{trx.get_amount()}, "{trx.get_currency()}", '
                f'"{trx.get_type()}", "{trx.get_detail()}", "{account}");'
            )
            cur.execute(sql)  # type: ignore
            if account not in accounts:
                accounts[account] = {'count': 0}
            accounts[account]['count'] += 1  # type: ignore

        # Move CSV file to done folder
        os.rename(f, f.replace(csv_todo, csv_done))

        # Commit changes after each file
        con.commit()  # type: ignore
        csv_version: int = 0
    print('--------------------------------------------------------')
    print('Transactions Summary:')
    for k, v in accounts.items():
        print(f" - {k} -> {v['count']}")
    print('--------------------------------------------------------')
except Exception:  # pylint: disable=broad-except
    print('Unexpected error:', sys.exc_info())
    sys.exit(1)
finally:
    if con:
        con.close()  # type: ignore
