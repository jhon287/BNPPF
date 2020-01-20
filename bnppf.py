import re
from datetime import datetime


class BNPPF:

    def __init__(self, ref='', date='', amount=0, currency='EUR', type='',
                 detail='', account=''):
        self.ref = ref
        self.date = date
        self.amount = amount
        self.currency = currency
        self.type = type
        self.detail = detail
        self.account = account

    def __str__(self):
        return "Ref: {}. Date: {}. Amount: {} {}. " \
               "Type: {}. Detail: {}. Account: {}" \
               .format(self.ref, self.date, self.amount, self.currency,
                       self.type, self.detail, self.account)

    def _get_statement_type(self, counterparty='', detail=''):
        counterparty = counterparty.strip()
        detail = detail.strip()
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
        elif re.search("^PAIEMENT PAR( CARTE DE (BANQUE|DEBIT))?$",
                       counterparty):
            return "Carte"
        elif re.search("^REDEVANCE MENSUELLE", counterparty):
            return "Redevance"
        elif re.search("^CHARGEMENT CARTE PROTON$", counterparty):
            return "Proton"
        elif re.search("^(EASY SAVE|AUTOMATIQUE$)", counterparty):
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
            elif re.search("^COMPTE INTERNE MASTERCARD.*ETAT"
                           " DE DEPENSES NUMERO",
                           detail):
                return "Mastercard"
            else:
                return 'Inconnu'

    def parse(self, line='', format='csv', counterparty=True):
        if format == 'csv':
            elements = line.replace('"', '').split(';')
            map(str.strip('"'), elements)
            self.ref = elements[0]
            if not re.match('^20[0-9]{2}-[0-9]{4}$', self.ref):
                self.ref = None
                return True
            d = datetime.strptime(elements[1], '%d/%m/%Y')
            self.date = d.strftime('%Y%m%d')
            if re.search(r'^(\-)?\d{1,3}\.\d{3},\d{1,2}$',  # 2.720,00
                         elements[3].strip()):
                self.amount = float(elements[3]
                                    .replace('.', '').replace(',', '.'))
            else:
                self.amount = float(elements[3].replace(',', '.'))
            self.currency = elements[4].strip()
            if counterparty:
                self.counterparty = elements[5].strip()
                self.detail = elements[6].strip()
                self.account = re.sub('("| )', '', elements[7]).strip()
            else:
                self.counterparty = ''
                self.detail = elements[5].strip()
                self.account = re.sub('("| )', '', elements[6]).strip()
            self.type = self._get_statement_type(
                counterparty=self.counterparty,
                detail=self.detail)
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
