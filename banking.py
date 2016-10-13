#!/usr/bin/python

import glob
import re
import sys
import os
from datetime import datetime
import ConfigParser
import mysql

config = ConfigParser.ConfigParser()
config.read('includes/Settings.ini')

db_user = config.get('database', 'db_user')
db_password = config.get('database', 'db_password')
db_host = config.get('database', 'db_server')
db_name = config.get('database', 'db_name')

dir_in = config.get('directory', 'in')
dir_done = config.get('directory', 'done')

con = None
accounts = {}
from_db = {}

# Directories check
if not os.path.exists(dir_in):
    print "%s does not exists! Please create it..." % dir_in
    sys.exit(1)
elif not os.path.exists(dir_done):
    print "%s does not exists! Please create it..." % dir_done
    sys.exit(1)

try:
	#con = mysql.connector.connect(
	#	user=db_user, password=db_password,
	#	host=db_host,
	#	database=db_name
	#)
	#cur = con.cursor()
	for f in glob.glob(dir_in+'/*'):
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
			# Virement .*[A-Z][A-Z][0-9][0-9].*BIC .*COMMUNICATION.*: .*DATE.*: [0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$|^DU COMPTE NO [A-Z][A-Z][0-9][0-9].*COMMUNICATION:.*DATE VALEUR : [0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$|.*[A-Z][A-Z][0-9][0-9].*BIC .* REFERENCE DONNEUR D\'ORDRE : .*COMMUNICATION.*:
			# Frais ^PERIODE DU [0-9][0-9]-[0-9][0-9]-20[0-9][0-9] AU [0-9][0-9]-[0-9][0-9]-20[0-9][0-9].*DATE VALEUR : [0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$
			# Mandat .*NUMERO DE MANDAT :.*[0-9]+ REFERENCE :.*[0-9]+ COMMUNICATION : .*DATE VALEUR : [0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$
			# Mastercard ^COMPTE INTERNE MASTERCARD: ETAT DE DEPENSES NUMERO [0-9]+DATE VALEUR : [0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$
			# Carte ^AVEC LA CARTE 6703.* DATE VALEUR : [0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$
			# Cash .*CASH DEPOSIT AVEC LA CARTE 6703.*
			# P2M ^TERMINAL NO [0-9]+ DATE : [0-9][0-9]-[0-9][0-9]-20[0-9][0-9].*DATE VALEUR : [0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$
			print elements
			t_ref = elements[0].strip('"')
			d = datetime.strptime(elements[1].strip('"'),'%d/%m/%Y')
			t_date = d.strftime('%Y%m%d')
			# Amount (replace comma (,) by dot (.))
			t_amount = elements[2].strip('"').replace(',','.')
			t_currency = elements[3].strip('"')
			t_type = ''
			t_comment = elements[4].strip('"')
			if re.search(".*[A-Z][A-Z][0-9][0-9].*BIC .*COMMUNICATION.*: .*DATE.*: [0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$",t_comment) or \
			   re.search("^DU COMPTE NO [A-Z][A-Z][0-9][0-9].*COMMUNICATION:.*DATE VALEUR : [0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$",t_comment) or \
			   re.search(".*[A-Z][A-Z][0-9][0-9].*BIC .* REFERENCE DONNEUR D\'ORDRE : .*COMMUNICATION.*:",t_comment):
			       t_type = 'Virement'
			elif re.search("^COMPTE INTERNE MASTERCARD: ETAT DE DEPENSES NUMERO [0-9]+DATE VALEUR : [0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$",t_comment):
			    t_type = 'Mastercard'
			elif re.search(".*NUMERO DE MANDAT :.*[0-9]+ REFERENCE :.*[0-9]+ COMMUNICATION : .*DATE VALEUR : [0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$",t_comment):
			    t_type = 'Mandat'
			elif re.search("^PERIODE DU [0-9][0-9]-[0-9][0-9]-20[0-9][0-9] AU [0-9][0-9]-[0-9][0-9]-20[0-9][0-9].*DATE VALEUR : [0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$",t_comment):
			    t_type = 'Frais'
			# Cash deposit
			elif re.search(".*CASH DEPOSIT AVEC LA CARTE 6703.*", t_comment): t_type = 'Cash'
			# Domiciliation
			elif re.search("^DOMICILIATION EUROPEENNE", t_comment): t_type = 'Domiciliation'
			# Archives d'operation
			elif re.search("^ARCHIVE.*OPERATIONS", t_comment): t_type = 'Archive'
			# Virement (Old way)
			elif re.search("VIREMENT EUROPEEN", t_comment) or re.search("VIREMENT DU COMPTE", t_comment) or re.search("VIREMENT AU COMPTE", t_comment) or re.search("VIREMENT AVEC DATE-MEMO", t_comment): t_type = 'Virement'
			# Carte (Old way)
			elif re.search("^AVEC LA CARTE 6703.* DATE VALEUR : [0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$", t_comment): t_type = 'Carte'
			# Ordre Permanent
			elif re.search("ORDRE PERMANENT", t_comment): t_type = 'Ordre Permanent'
			# Versement Cheque
			elif re.search("VERSEMENT CHEQUE", t_comment): t_type = 'Versement'
			# Remboursement Proton
			elif re.search("^DE VOTRE CARTE PROTON", t_comment): t_type = 'Proton'
			# P2M
			elif re.search("^TERMINAL NO [0-9]+ DATE : [0-9][0-9]-[0-9][0-9]-20[0-9][0-9].*DATE VALEUR : [0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$",t_comment): t_type = 'P2M'
			# Unknown
			else: t_type = 'Inconnu'
			t_account = re.sub('("| )','',elements[5]).strip()
			# New account ?
			print t_type,t_account
			#sql = 'CALL addTransaction("%s","%s",%f,"%s","%s","%s","%s");' % (t_ref,t_date,float(t_amount),t_currency,t_type,t_comment,t_account)
			#cur.execute(sql)
		fd.close()
		# Move CSV files to old_csv_dir
		os.rename(f,"%s.%s" % (f.replace(dir_in,dir_done),datetime.now().strftime("%Y%m%d%H%M%S")))
	#con.commit()
except:
	print "Unexpected error:", sys.exc_info()
	sys.exit(1)
finally:
	if con: con.close()
