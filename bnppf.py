import re
import csv
from datetime import datetime


def get_csv_version(line: str = None) -> int:
    if re.search(r';CONTREPARTIE DE LA TRANSACTION;', line):
        return 2
    elif re.search(r';Type de transaction;', line):
        return 3
    else:
        return 1


class BNPPF:

    def __init__(self, ref: str = '', date: str = '', amount: int = 0,
                 currency: str = 'EUR', type: str = '', detail: str = '',
                 account='', csv_version: int = 3):
        self.ref = ref
        self.date = date
        self.amount = amount
        self.currency = currency
        self.type = type
        self.detail = detail
        self.account = account
        self.csv_version = csv_version

    def __str__(self):
        return f'Ref: {self.ref}. Date: {self.date}. ' \
               f'Amount: {self.amount} {self.currency}. ' \
               f'Type: {self.type}. Detail: {self.detail}.' \
               f'Account: {self.account}. CSV Version: {self.csv_version}.'

    def _get_statement_type(self, counterparty: str = '',
                            detail: str = '', trx_type: str = ''):
        counterparty = counterparty.strip()
        detail = detail.strip()
        trx_type = trx_type.strip()

        if trx_type == 'Virement en euros' or \
           re.search("^[A-Z][A-Z][0-9][0-9]", counterparty) or \
           re.search("^[0-9]{3}-[0-9]{7}-[0-9]{2}$", counterparty) or \
           counterparty.startswith('VIREMENT EUROPEEN ') or \
           counterparty.startswith('VOTRE EPARGNE AUTOMATIQUE '):
            return "Virement"
        elif trx_type == 'Domiciliation' or counterparty == 'DOMICILIATION':
            return 'Domiciliation'
        elif re.search(r"^ASSURANCE((\-|\s)COMPTE)?$", counterparty):
            return "Assurance"
        elif trx_type == "Intérêts du compte d'épargne" or \
                counterparty.startswith('INTERETS NETS'):
            return "Interets"
        elif trx_type.startswith('Retrait ') or \
                re.search("^RETRAIT D'(ARGENT|ESPECES)", counterparty):
            return "Retrait"
        elif counterparty == 'VERSEMENT ESPECES':
            return "Cash"
        elif re.search("^GLOBALISATION [0-9] OPERATIONS POS",
                       counterparty) or \
                counterparty.startswith('PAIEMENT MOBILE'):
            return "P2M"
        elif trx_type == 'Paiement par carte de crédit' or \
                counterparty == 'PAIEMENT A BANK CARD COMPANY':
            return "BCC"
        elif counterparty.startswith('VERSEMENT DE VOTRE SERVICE BONUS'):
            return "Bonus"
        elif trx_type == 'Paiement par carte' or \
                re.search("^PAIEMENT (PAR|AVEC LA)"
                          "( CARTE DE (BANQUE|DEBIT))?$", counterparty):
            return "Carte"
        elif trx_type == 'Frais liés au compte' or \
                counterparty.startswith('REDEVANCE MENSUELLE'):
            return "Redevance"
        elif counterparty == 'CHARGEMENT CARTE PROTON':
            return "Proton"
        elif re.search("^(EASY SAVE|AUTOMATIQUE$)", counterparty):
            return "Easy Save"
        elif re.search(
                "^FRAIS MENSUELS D'(EQUIPEMENT|UTILISATION)$",
                counterparty
             ) or counterparty == 'FRAIS DE PORT':
            return "Frais"
        elif re.search("^ANNULATION (DU )?PAIEMENT", counterparty):
            return "Annulation"
        elif counterparty.startswith('VERSEMENT DE'):
            return "Versement"
        else:
            if re.search(".*[A-Z][A-Z][0-9][0-9].*COMMUNICATION.*:.*DATE.*: "
                         r"[0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$", detail) or \
               re.search("^DU COMPTE NO [A-Z][A-Z][0-9][0-9].*"
                         "COMMUNICATION:.*DATE"
                         r" VALEUR : [0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$",
                         detail) or \
               re.search(".*[A-Z][A-Z][0-9][0-9].*BIC .* REFERENCE DONNEUR "
                         "D\'ORDRE : .*COMMUNICATION.*:", detail) or \
               re.search("PREMIER PRELEVEMENT D'UNE.*DOMICILIATION EUROPEENNE",
                         detail):
                return 'Virement'
            elif re.search("^COMPTE INTERNE MASTERCARD: "
                           "ETAT DE DEPENSES NUMERO "
                           "[0-9]+DATE VALEUR : "
                           r"[0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$", detail):
                return 'BCC'
            elif re.search(".*NUMERO DE MANDAT :.*[0-9]+ REFERENCE :.*[0-9]+ "
                           "COMMUNICATION : .*DATE VALEUR : "
                           r"[0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$", detail):
                return 'Mandat'
            elif re.search("^PERIODE DU [0-9][0-9]-[0-9][0-9]-20[0-9][0-9] AU "
                           "[0-9][0-9]-[0-9][0-9]-20[0-9][0-9].*DATE VALEUR : "
                           r"[0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$",
                           detail) or \
                re.search("^REMBOURSEMENT DES.*FRAIS MENSUELS D'UTILISATION",
                          detail):
                return 'Frais'
            elif re.search(".*CASH DEPOSIT AVEC LA CARTE 6703.*", detail):
                return 'Cash'
            elif detail.startswith('DOMICILIATION EUROPEENNE'):
                return 'Domiciliation'
            elif re.search("^ARCHIVE.*OPERATIONS", detail):
                return 'Archive'
            elif 'VIREMENT EUROPEEN' in detail or \
                 'VIREMENT DU COMPTE' in detail or \
                 'VIREMENT AU COMPTE' in detail or \
                 'VIREMENT AVEC DATE-MEMO' in detail:
                return 'Virement'
            elif re.search("^AVEC LA CARTE 6703.* P2P MOBIL.* DATE VALEUR : "
                           r"[0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$",
                           detail) or \
                re.search("^TERMINAL NO [0-9]+ DATE : "
                          "[0-9][0-9]-[0-9][0-9]-20[0-9][0-9].*"
                          "DATE VALEUR : "
                          r"[0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$",
                          detail):
                return 'P2M'
            elif re.search("AVEC LA CARTE 6703.* DATE VALEUR : "
                           r"[0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$", detail):
                return 'Carte'
            elif trx_type == 'Ordre permanent' or \
                    re.search("ORDRE PERMANENT", detail):
                return 'Ordre Permanent'
            elif 'VERSEMENT CHEQUE' in detail:
                return 'Versement'
            elif detail.startswith('DE VOTRE CARTE PROTON') or \
                re.search("^REMBOURSEMENT DU SOLDE.*DE VOTRE CARTE PROTON",
                          detail):
                return 'Proton'
            elif detail.startswith('COMFORT PACK '):
                return "Redevance"
            elif detail.startswith('VOTRE FIDELITE EST RECOMPENSEE '):
                return "Bonus"
            elif re.search("^(DATE VALEUR|^EXECUTE LE)", detail):
                return "Divers"
            elif re.search("^COMPTE INTERNE MASTERCARD.*ETAT"
                           " DE DEPENSES NUMERO",
                           detail):
                return "Mastercard"
            else:
                return 'Inconnu'

    def parse(self, line: str = '', format: str = 'csv') -> bool:
        if format == 'csv':
            elements = [element for element in
                        csv.reader([line], delimiter=';')][0]
            map(str(str).strip(), elements)

        if self.csv_version == 3:
            ref_regex_pattern = r'^20[0-9]{2}-[0-9]{5}$'
        else:
            ref_regex_pattern = r'^20[0-9]{2}-[0-9]{4}$'

        if re.search(ref_regex_pattern, elements[0]):
            self.ref = elements[0]
        else:
            self.ref = None
            return True

        d = datetime.strptime(elements[1], '%d/%m/%Y')
        self.date = d.strftime('%Y%m%d')

        if re.search(r'^(\-)?\d{1,3}\.\d{3},\d{1,2}$',  # 2.720,00
                     elements[3]):
            self.amount = float(elements[3].replace('.', '').replace(',', '.'))
        else:
            self.amount = float(elements[3].replace(',', '.'))
        self.currency = elements[4]

        if self.csv_version == 1:
            self.counterparty = ''
            self.detail = elements[5].rstrip('"')
            self.account = elements[6].replace(' ', '')
        elif self.csv_version == 2:
            self.counterparty = elements[5]
            self.detail = elements[6].rstrip('"')
            self.account = elements[7].replace(' ', '')
        else:
            self.account = elements[5].replace(' ', '')
            self.counterparty = elements[8]
            self.detail = elements[10].rstrip('"')

        self.type = self._get_statement_type(
                counterparty=self.counterparty,
                detail=self.detail,
                trx_type=elements[6])

        if self.type == "Inconnu":
            print('ERROR: ', line)
            return False
        else:
            return True

    def get_ref(self):
        return self.ref

    def get_date(self):
        return self.date

    def get_amount(self):
        return self.amount

    def get_currency(self):
        return self.currency

    def get_type(self):
        return self.type

    def get_detail(self):
        return self.detail

    def get_account(self):
        return self.account

    def get_all(self):
        return {
            'ref': self.ref,
            'date': self.date,
            'amount': self.amount,
            'currency': self.currency,
            'type': self.type,
            'detail': self.detail,
            'account': self.account,
        }
