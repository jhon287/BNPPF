#!/usr/bin/env python

import glob
import re
import sys
import os
import ConfigParser
import mysql.connector

from datetime import datetime

config = ConfigParser.ConfigParser()
config.read('includes/Settings.ini')

db = {}
db['user'] = config.get('database', 'user')
db['password'] = config.get('database', 'password')
db['server'] = config.get('database', 'server')
db['database'] = config.get('database', 'name')
db['port'] = config.get('database','port')

dir = {}
dir['in'] = config.get('directory', 'in')
dir['done'] = config.get('directory', 'done')

con = None
accounts = {}
from_db = {}

def get_statement_type(counterparty='',detail=''):
    # Search using COUNTERPARTY
    if re.search("^[A-Z][A-Z][0-9][0-9]", counterparty) or \
       re.search("^[0-9]{3}-[0-9]{7}-[0-9]{2}$", counterparty) or \
       re.search("^VIREMENT EUROPEEN ", counterparty) or \
       re.search("^VOTRE EPARGNE AUTOMATIQUE ", counterparty) or \
       re.search("^DOMICILIATION$", counterparty):
       return "Virement"
    elif re.search("^ASSURANCE COMPTE$", counterparty): return "Assurance"
    elif re.search("^INTERETS NETS ", counterparty): return "Interets"
    elif re.search("^RETRAIT D'ARGENT ", counterparty): return "Retrait"
    elif re.search("^VERSEMENT ESPECES$", counterparty): return "Cash"
    elif re.search("^GLOBALISATION 9 OPERATIONS POS", counterparty): return "P2M"
    elif re.search("^PAIEMENT A BANK CARD COMPANY$", counterparty): return "BCC"
    elif re.search("^VERSEMENT DE VOTRE SERVICE BONUS$", counterparty): return "Bonus"
    elif re.search("^PAIEMENT PAR CARTE DE BANQUE$", counterparty): return "Carte"
    elif re.search("^REDEVANCE MENSUELLE", counterparty): return "Redevance"
    elif re.search("^CHARGEMENT CARTE PROTON$", counterparty): return "Proton"
    elif re.search("^EASY SAVE ", counterparty): return "Easy Save"
    elif re.search("^FRAIS MENSUELS D'(EQUIPEMENT|UTILISATION)$", counterparty) or \
         re.search("^FRAIS DE PORT$", counterparty):
         return "Frais"
    # Search using DETAIL
    else:
        if re.search(".*[A-Z][A-Z][0-9][0-9].*COMMUNICATION.*:.*DATE.*: [0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$", detail) or \
           re.search("^DU COMPTE NO [A-Z][A-Z][0-9][0-9].*COMMUNICATION:.*DATE VALEUR : [0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$", detail) or \
           re.search(".*[A-Z][A-Z][0-9][0-9].*BIC .* REFERENCE DONNEUR D\'ORDRE : .*COMMUNICATION.*:", detail) or \
           re.search("PREMIER PRELEVEMENT D'UNE.*DOMICILIATION EUROPEENNE", detail):
           return 'Virement'
        elif re.search("^COMPTE INTERNE MASTERCARD: ETAT DE DEPENSES NUMERO [0-9]+DATE VALEUR : [0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$", detail):
            return 'BCC'
        elif re.search(".*NUMERO DE MANDAT :.*[0-9]+ REFERENCE :.*[0-9]+ COMMUNICATION : .*DATE VALEUR : [0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$", detail):
            return 'Mandat'
        elif re.search("^PERIODE DU [0-9][0-9]-[0-9][0-9]-20[0-9][0-9] AU [0-9][0-9]-[0-9][0-9]-20[0-9][0-9].*DATE VALEUR : [0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$", detail) or \
             re.search("^REMBOURSEMENT DES.*FRAIS MENSUELS D'UTILISATION", detail):
            return 'Frais'
        elif re.search(".*CASH DEPOSIT AVEC LA CARTE 6703.*", detail): return 'Cash'
        elif re.search("^DOMICILIATION EUROPEENNE", detail): return 'Domiciliation'
        elif re.search("^ARCHIVE.*OPERATIONS", detail): return 'Archive'
        elif re.search("VIREMENT EUROPEEN", detail) or re.search("VIREMENT DU COMPTE", detail) or \
             re.search("VIREMENT AU COMPTE", detail) or \
             re.search("VIREMENT AVEC DATE-MEMO", detail):
             return  'Virement'
        elif re.search("AVEC LA CARTE 6703.* DATE VALEUR : [0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$", detail): return 'Carte'
        elif re.search("ORDRE PERMANENT", detail): return 'Ordre Permanent'
        elif re.search("VERSEMENT CHEQUE", detail): return 'Versement'
        elif re.search("^DE VOTRE CARTE PROTON", detail) or \
             re.search("^REMBOURSEMENT DU SOLDE.*DE VOTRE CARTE PROTON", detail):
             return 'Proton'
        elif re.search("^TERMINAL NO [0-9]+ DATE : [0-9][0-9]-[0-9][0-9]-20[0-9][0-9].*DATE VALEUR : [0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$", detail): return 'P2M'
        elif re.search("^COMFORT PACK ", detail): return "Redevance"
        elif re.search("^VOTRE FIDELITE EST RECOMPENSEE ", detail): return "Bonus"
        elif re.search("^(DATE VALEUR|^EXECUTE LE)", detail): return "Divers"
        else: return 'Inconnu'

# Directories check
if not os.path.exists(dir['in']):
    print "%s does not exists! Please create it..." % dir['in']
    sys.exit(1)
elif not os.path.exists(dir['done']):
    print "%s does not exists! Please create it..." % dir['done']
    sys.exit(1)

try:
    con = mysql.connector.connect(
        user = db['user'],
        password = db['password'],
        host = db['server'],
        port = db['port'],
        database = db['database']
    )
    cur = con.cursor()
    for f in glob.glob(dir['in']+'/*'):
        if not os.path.isfile(f): continue
        print "Current: " + f
        fd = open(f,'r')
        first_line = True
        for line in fd:
            if first_line:
                if re.search("CONTREPARTIE DE (L'OPERATION|LA TRANSACTION)", line, re.IGNORECASE):
                    counterparty = True
                else:
                    counterparty = False
                first_line = False
                continue
            # Empty line ?
            if not line.strip(): continue
            elements = line.replace('"','').split(';') #"ANNEE + REFERENCE";"DATE DE L'EXECUTION";"DATE VALEUR";"MONTANT";"DEVISE DU COMPTE";"CONTREPARTIE DE L'OPERATION";"DETAIL";"NUMERO DE COMPTE"
            t_ref = elements[0].strip('"')
            # Good sequence number ?
            if not re.match('^20[0-9]{2}-[0-9]{4}$',t_ref):
                print "SKIP - Wrong sequence number detected %s !" % t_ref
                continue
            d = datetime.strptime(elements[1].strip('"'),'%d/%m/%Y')
            t_date = d.strftime('%Y%m%d')
            # Amount (replace comma (,) by dot (.))
            t_amount = elements[3].strip('"')
            t_currency = elements[4].strip('"')
            if counterparty:
                t_counterparty = elements[5].strip('"').strip()
                t_detail = elements[6].strip('"').strip()
                t_account = re.sub('("| )','',elements[7]).strip()
            else:
                t_counterparty = ''
                t_detail = elements[5].strip('"').strip()
                t_account = re.sub('("| )','',elements[6]).strip()
            t_type = get_statement_type(counterparty=t_counterparty, detail=t_detail)
            if t_type == "Inconnu":
                print line
            sql = 'CALL addTransaction("%s", "%s", %f, "%s", "%s", "%s", "%s");' % (t_ref, t_date, float(t_amount), t_currency, t_type, t_detail, t_account)
            cur.execute(sql)
        fd.close()
        os.rename(f, "%s" % f.replace(dir['in'], dir['done']))
    con.commit()
except:
    print "Unexpected error:", sys.exc_info()
    sys.exit(1)
finally:
    if con: con.close()
