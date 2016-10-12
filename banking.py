#!/usr/bin/python

import glob
import re
import sys
import os
from datetime import datetime
import ConfigParser
import mysql.connector
import sqlite3 as sqlite


config = ConfigParser.ConfigParser()
config.read('includes/Settings.ini')

db_user = config.get('generic', 'db_user')
db_password = config.get('generic', 'db_password')
db_host = config.get('generic', 'db_server')
db_name = config.get('generic', 'db_name')

csv_dir = config.get('generic', 'csv_dir')
old_csv_dir = config.get('generic', 'old_csv_dir')
#db_dir  = 'db'
con = None
accounts = {}
from_db = {}

try:
	con = mysql.connector.connect(
		user=db_user, password=db_password,
		host=db_host,
		database=db_name
	)
	cur = con.cursor()
	for f in glob.glob(csv_dir+'/*'):
		if not os.path.isfile(f): continue
		fd = open(f,'r')
		first_line = True
		for line in fd:
			if first_line:
				first_line = False
				continue
			# Empty line ?
			if not line.strip(): continue
			elements = line.replace('"','').split(';') #"ANNEE + REFERENCE";"DATE DE L'EXECUTION";"DATE VALEUR";"MONTANT";"DEVISE DU COMPTE";"CONTREPARTIE DE L'OPERATION";"DETAIL";"NUMERO DE COMPTE"
			t_ref = elements[0].strip('"')
			d = datetime.strptime(elements[1].strip('"'),'%d/%m/%Y')
			t_date = d.strftime('%Y%m%d')
			# Amount (replace comma (,) by dot (.))
			t_amount = elements[3].strip('"').replace(',','.')
			t_currency = elements[4].strip('"')
			t_type = elements[5].strip(' "')
			t_comment = elements[6].strip('"')
			# Virement
			if re.search('^[A-Z][A-Z][0-9][0-9]', t_type): t_type = 'Virement'
			# Paiement par carte de banque
			elif re.search('^PAIEMENT PAR CARTE DE BANQUE', t_type): t_type = 'Carte'
			# Paiement A BCC
			elif re.search('^PAIEMENT A BANK CARD COMPANY', t_type): t_type = 'BCC'
			# Retrait d'argent
			elif re.search("^RETRAIT D'ARGENT", t_type): t_type = 'Retrait'
			# Frais divers
			elif re.search("^FRAIS", t_type): t_type = 'Frais'
			# Interets nets
			elif re.search("^INTERETS NETS", t_type): t_type = 'Interets'
			# Chargement Proton
			elif re.search("^CHARGEMENT CARTE PROTON", t_type): t_type = 'Proton'
			# Assurance compte
			elif re.search("^ASSURANCE COMPTE", t_type): t_type = 'Assurance'
			# Remboursement 
			elif re.search("^REMBOURSEMENT", t_type): t_type = 'Remboursement'
			# Domiciliation 
			elif re.search("^DOMICILIATION", t_type): t_type = 'Domiciliation'
			# P2M (BCMC Mobile) 
			elif re.search("^000-0000000-00", t_type): t_type = 'P2M'
			else:
				# Cash deposit
				if re.search("CASH DEPOSIT", t_comment): t_type = 'Cash'
				# Domiciliation
				elif re.search("^DOMICILIATION EUROPEENNE", t_comment): t_type = 'Domiciliation'
				# Archives d'operation
				elif re.search("^ARCHIVE.*OPERATIONS", t_comment): t_type = 'Archive'
				# Virement (Old way)
				elif re.search("VIREMENT EUROPEEN", t_comment) or re.search("VIREMENT DU COMPTE", t_comment) or re.search("VIREMENT AU COMPTE", t_comment) or re.search("VIREMENT AVEC DATE-MEMO", t_comment): t_type = 'Virement'
				# Carte (Old way)
				elif re.search("AVEC LA CARTE", t_comment): t_type = 'Carte'
				# Ordre Permanent
				elif re.search("ORDRE PERMANENT", t_comment): t_type = 'Ordre Permanent'
				# Versement Cheque
				elif re.search("VERSEMENT CHEQUE", t_comment): t_type = 'Versement'
				# Remboursement Proton
				elif re.search("^DE VOTRE CARTE PROTON", t_comment): t_type = 'Proton'
				# Unknown
				else: t_type = 'Inconnu'
			t_account = re.sub('("| )','',elements[7]).strip()
			# New account ?
			sql = 'CALL addTransaction("%s","%s",%f,"%s","%s","%s","%s");' % (t_ref,t_date,float(t_amount),t_currency,t_type,t_comment,t_account)
			cur.execute(sql)
		fd.close()
		# Move CSV files to old_csv_dir
		os.rename(f,f.replace(csv_dir,old_csv_dir))
	con.commit()
except sqlite.Error, e:
	print "Error %s:" % e.args[0]
	sys.exit(1)
finally:
	if con: con.close()
