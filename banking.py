import glob
import re
import sys
import os
import configparser
import mysql.connector

from datetime import datetime


def get_statement_type(counterparty='', detail=''):
    # COUNTERPARTY
    if re.search("^[A-Z][A-Z][0-9][0-9]", counterparty) or \
       re.search("^[0-9]{3}-[0-9]{7}-[0-9]{2}$", counterparty) or \
       re.search("^VIREMENT EUROPEEN ", counterparty) or \
       re.search("^VOTRE EPARGNE AUTOMATIQUE ", counterparty) or \
       re.search("^DOMICILIATION$", counterparty):
        return "Virement"
    elif re.search(r"^ASSURANCE((\-|\s)COMPTE)?$", counterparty):
        return "Assurance"
    elif re.search("^INTERETS NETS", counterparty):
        return "Interets"
    elif re.search("^RETRAIT D'(ARGENT|ESPECES)", counterparty):
        return "Retrait"
    elif re.search("^VERSEMENT ESPECES$", counterparty):
        return "Cash"
    elif re.search("^GLOBALISATION [0-9] OPERATIONS POS", counterparty):
        return "P2M"
    elif re.search("^PAIEMENT A BANK CARD COMPANY$", counterparty):
        return "BCC"
    elif re.search("^VERSEMENT DE VOTRE SERVICE BONUS", counterparty):
        return "Bonus"
    elif re.search("^PAIEMENT PAR CARTE DE (BANQUE|DEBIT)$", counterparty):
        return "Carte"
    elif re.search("^REDEVANCE MENSUELLE", counterparty):
        return "Redevance"
    elif re.search("^CHARGEMENT CARTE PROTON$", counterparty):
        return "Proton"
    elif re.search("^EASY SAVE", counterparty):
        return "Easy Save"
    elif re.search(
            "^FRAIS MENSUELS D'(EQUIPEMENT|UTILISATION)$",
            counterparty
         ) or re.search("^FRAIS DE PORT$", counterparty):
        return "Frais"
    elif re.search("^ANNULATION PAIEMENT", counterparty):
        return "Annulation"
    # DETAIL
    else:
        if re.search(".*[A-Z][A-Z][0-9][0-9].*COMMUNICATION.*:.*DATE.*: "
                     r"[0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$", detail) or \
           re.search("^DU COMPTE NO [A-Z][A-Z][0-9][0-9].*COMMUNICATION:.*DATE"
                     r" VALEUR : [0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$",
                     detail) or \
           re.search(".*[A-Z][A-Z][0-9][0-9].*BIC .* REFERENCE DONNEUR "
                     "D\'ORDRE : .*COMMUNICATION.*:", detail) or \
           re.search("PREMIER PRELEVEMENT D'UNE.*DOMICILIATION EUROPEENNE",
                     detail):
            return 'Virement'
        elif re.search("^COMPTE INTERNE MASTERCARD: ETAT DE DEPENSES NUMERO "
                       "[0-9]+DATE VALEUR : "
                       r"[0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$", detail):
            return 'BCC'
        elif re.search(".*NUMERO DE MANDAT :.*[0-9]+ REFERENCE :.*[0-9]+ "
                       "COMMUNICATION : .*DATE VALEUR : "
                       r"[0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$", detail):
            return 'Mandat'
        elif re.search("^PERIODE DU [0-9][0-9]-[0-9][0-9]-20[0-9][0-9] AU "
                       "[0-9][0-9]-[0-9][0-9]-20[0-9][0-9].*DATE VALEUR : "
                       r"[0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$", detail) or \
            re.search("^REMBOURSEMENT DES.*FRAIS MENSUELS D'UTILISATION",
                      detail):
            return 'Frais'
        elif re.search(".*CASH DEPOSIT AVEC LA CARTE 6703.*", detail):
            return 'Cash'
        elif re.search("^DOMICILIATION EUROPEENNE", detail):
            return 'Domiciliation'
        elif re.search("^ARCHIVE.*OPERATIONS", detail):
            return 'Archive'
        elif re.search("VIREMENT EUROPEEN", detail) or \
                re.search("VIREMENT DU COMPTE", detail) or \
                re.search("VIREMENT AU COMPTE", detail) or \
                re.search("VIREMENT AVEC DATE-MEMO", detail):
            return 'Virement'
        elif re.search("^AVEC LA CARTE 6703.* P2P MOBIL.* DATE VALEUR : "
                       r"[0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$", detail) or \
                re.search("^TERMINAL NO [0-9]+ DATE : "
                          "[0-9][0-9]-[0-9][0-9]-20[0-9][0-9].*DATE VALEUR : "
                          r"[0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$", detail):
            return 'P2M'
        elif re.search("AVEC LA CARTE 6703.* DATE VALEUR : "
                       r"[0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$", detail):
            return 'Carte'
        elif re.search("ORDRE PERMANENT", detail):
            return 'Ordre Permanent'
        elif re.search("VERSEMENT CHEQUE", detail):
            return 'Versement'
        elif re.search("^DE VOTRE CARTE PROTON", detail) or \
            re.search("^REMBOURSEMENT DU SOLDE.*DE VOTRE CARTE PROTON",
                      detail):
            return 'Proton'
        elif re.search("^COMFORT PACK ", detail):
            return "Redevance"
        elif re.search("^VOTRE FIDELITE EST RECOMPENSEE ", detail):
            return "Bonus"
        elif re.search("^(DATE VALEUR|^EXECUTE LE)", detail):
            return "Divers"
        elif re.search("^COMPTE INTERNE MASTERCARD.*ETAT DE DEPENSES NUMERO",
                       detail):
            return "Mastercard"
        else:
            return 'Inconnu'


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
                 open(f, 'r', encoding='utf8', errors="ignore")]
        first_line = True
        for line in lines:
            transaction = {}
            if first_line:
                if re.search("CONTREPARTIE DE (L'OPERATION|LA TRANSACTION)",
                             line, re.IGNORECASE):
                    counterparty = True
                else:
                    counterparty = False
                first_line = False
                continue
            # Empty line ?
            if not line.strip():
                continue
            elements = line.replace('"', '').split(';')
            transaction['ref'] = elements[0].strip('"')
            # Good sequence number ?
            if not re.match('^20[0-9]{2}-[0-9]{4}$', transaction['ref']):
                print("SKIP - Wrong sequence number detected {} !"
                      .format(transaction['ref']))
                continue
            d = datetime.strptime(elements[1].strip('"'), '%d/%m/%Y')
            transaction['date'] = d.strftime('%Y%m%d')
            transaction['amount'] = elements[3].strip('"').replace(',', '.')
            transaction['currency'] = elements[4].strip('"')
            if counterparty:
                transaction['counterparty'] = elements[5].strip('"').strip()
                transaction['detail'] = elements[6].strip('"').strip()
                transaction['account'] = \
                    re.sub('("| )', '', elements[7]).strip()
            else:
                transaction['counterparty'] = ''
                transaction['detail'] = elements[5].strip('"').strip()
                transaction['account'] = \
                    re.sub('("| )', '', elements[6]).strip()
            transaction['type'] = get_statement_type(
                        counterparty=transaction['counterparty'],
                        detail=transaction['detail'])
            if transaction['type'] == "Inconnu":
                print('ERROR: ', line)
            sql = 'CALL addTransaction("{ref}", "{date}", {amount}, ' \
                  '"{currency}", "{type}", "{detail}", "{account}");'.format(
                    ref=transaction['ref'],
                    date=transaction['date'],
                    amount=transaction['amount'],
                    currency=transaction['currency'],
                    type=transaction['type'],
                    detail=transaction['detail'],
                    account=transaction['account'],
                  )
            cur.execute(sql)
            if transaction['account'] not in accounts:
                accounts[transaction['account']] = 0
            accounts[transaction['account']] += 1
        os.rename(f, f.replace(settings['directory']['in'],
                               settings['directory']['done']))
    con.commit()
    print('--------------------------------------------------------')
    print('Transactions Summary:')
    for k, v in accounts.items():
        print(' - {account} -> {transactions}'.format(
                account=k, transactions=v))
    print('--------------------------------------------------------')
except Exception:
    print("Unexpected error:", sys.exc_info())
    sys.exit(1)
finally:
    if con:
        con.close()
