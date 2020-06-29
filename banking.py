import glob
import re
import sys
import os
import configparser
import mysql.connector
import bnppf


accounts = {}
settings = {}
con = None

try:
    config = configparser.ConfigParser()
    config.read('./conf/settings.ini')
    for section in config.sections():
        if section not in settings:
            settings[section] = {}
        for key in config[section]:
            settings[section][key] = config[section][key]
except Exception as e:
    print("OS error: {0}".format(e))
    sys.exit(1)

for directory in [settings['directory']['in'], settings['directory']['done']]:
    if not os.path.exists(directory):
        print("Creating '{}'...".format(directory))
        os.makedirs(directory)

try:
    con = mysql.connector.connect(
        user=settings['database']['user'],
        password=settings['database']['password'],
        host=settings['database']['server'],
        port=settings['database']['port'],
        database=settings['database']['name']
    )
    cur = con.cursor()
    for f in glob.glob(settings['directory']['in'] + '/*'):
        if not os.path.isfile(f):
            continue
        print("Current: " + f)
        lines = [line.rstrip('\n') for line in
                 open(f, 'r', encoding='utf8', errors='ignore')]
        first_line = True
        for line in lines:
            transaction = bnppf.BNPPF()
            if first_line:
                if re.search("CONTREPARTIE DE (L'OPERATION|LA TRANSACTION)",
                             line, re.IGNORECASE):
                    counterparty = True
                else:
                    counterparty = False
                first_line = False
                continue
            if not line.strip():  # Empty line ?
                continue
            if not transaction.parse(line=line, format='csv',
                                     counterparty=counterparty):
                print('ERROR:', transaction.get_all())
                sys.exit(1)
            elif transaction.get_ref() is None:
                continue  # Skipping invalid sequence number
            account = transaction.get_account()
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
        os.rename(f, f.replace(settings['directory']['in'],
                               settings['directory']['done']))
        con.commit()  # Commit changes after each file
    print('--------------------------------------------------------')
    print('Transactions Summary:')
    for k, v in accounts.items():
        print(' - {account} -> {transactions}'.format(
                account=k, transactions=v['count']))
    print('--------------------------------------------------------')
except Exception:
    print("Unexpected error:", sys.exc_info())
    sys.exit(1)
finally:
    if con:
        con.close()
