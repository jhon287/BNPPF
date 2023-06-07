import csv
from datetime import datetime
from re import search
from typing import Dict, List, Union


def get_csv_version(line: str = '') -> int:
    if search(r';CONTREPARTIE DE LA TRANSACTION;', line):
        return 2

    if search(r';Type de transaction;', line):
        return 3

    return 1


class BNPPF:
    ref: str = ''
    date: str = ''
    amount: float = 0.0
    currency: str = 'EUR'
    type: str = ''
    detail: str = ''
    account: str = ''
    csv_version: int = 3

    def __init__(self, ref: str = '', date: str = '', amount: float = 0,
                 currency: str = 'EUR', type: str = '', detail: str = '',
                 account: str = '', csv_version: int = 3) -> None:
        self.ref = ref
        self.date = date
        self.amount = amount
        self.currency = currency
        self.type = type
        self.detail = detail
        self.account = account
        self.csv_version = csv_version

    def __str__(self) -> str:
        return f'Ref: {self.ref}. Date: {self.date}. ' \
               f'Amount: {self.amount} {self.currency}. ' \
               f'Type: {self.type}. Detail: {self.detail}.' \
               f'Account: {self.account}. CSV Version: {self.csv_version}.'

    def _get_statement_type(self, counterparty: str = '', detail: str = '',
                            trx_type: str = '') -> str:
        counterparty = counterparty.strip()
        detail = detail.strip()
        trx_type = trx_type.strip()

        # Easy Save
        if search(r"^(EASY SAVE|AUTOMATIQUE$)", counterparty) or \
           search(r"^EASY SAVE - EPARGNE AUTOMATIQUE", detail):
            return "Easy Save"
        
        # Domiciliation
        if trx_type == 'Domiciliation' or counterparty == 'DOMICILIATION' or \
           detail.startswith('DOMICILIATION EUROPEENNE'):
            return 'Domiciliation'

        # Ordre Permanent
        if trx_type == 'Ordre permanent' or \
                search(r"ORDRE PERMANENT", detail):
            return 'Ordre Permanent'

        # Virement
        if trx_type == 'Virement en euros' or \
           search(r"^[A-Z][A-Z][0-9][0-9]", counterparty) or \
           search(r"^[0-9]{3}-[0-9]{7}-[0-9]{2}$", counterparty) or \
           counterparty.startswith('VIREMENT EUROPEEN ') or \
           counterparty.startswith('VOTRE EPARGNE AUTOMATIQUE '):
            return "Virement"

        # Assurance
        if search(r"^ASSURANCE((\-|\s)COMPTE)?$", counterparty):
            return "Assurance"

        # Interets
        if trx_type == "Intérêts du compte d'épargne" or \
                counterparty.startswith('INTERETS NETS'):
            return "Interets"

        # Retrait
        if trx_type.startswith('Retrait ') or \
                search(r"^RETRAIT D'(ARGENT|ESPECES)", counterparty):
            return "Retrait"

        # Cash
        if counterparty == 'VERSEMENT ESPECES' or \
           search(r".*CASH DEPOSIT AVEC LA CARTE 6703.*", detail):
            return "Cash"

        # P2M
        if search(r"^GLOBALISATION [0-9] OPERATIONS POS", counterparty) or \
           counterparty.startswith('PAIEMENT MOBILE') or \
           detail.startswith('PAIEMENT MOBILE') or \
           search(r"^AVEC LA CARTE 6703.* P2P MOBIL.* DATE VALEUR : "
                     r"[0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$",
                     detail) or \
           search(r"^TERMINAL NO [0-9]+ DATE : "
                     r"[0-9][0-9]-[0-9][0-9]-20[0-9][0-9].*"
                     "DATE VALEUR : "
                     r"[0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$",
                     detail):
            return "P2M"

        # BCC
        if trx_type == 'Paiement par carte de crédit' or \
           counterparty == 'PAIEMENT A BANK CARD COMPANY' or \
           search(r"^COMPTE INTERNE MASTERCARD: ETAT DE DEPENSES NUMERO "
                     r"[0-9]+DATE VALEUR : "
                     r"[0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$", detail):
            return "BCC"

        # Bonus
        if counterparty.startswith('VERSEMENT DE VOTRE SERVICE BONUS') or \
           detail.startswith('VOTRE FIDELITE EST RECOMPENSEE '):
            return "Bonus"

        # Carte
        if trx_type == 'Paiement par carte' or \
                search(r"^PAIEMENT (PAR|AVEC LA)"
                          r"( CARTE DE (BANQUE|DEBIT))?$", counterparty) or \
                search(r"AVEC LA CARTE 6703.* DATE VALEUR : "
                          r"[0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$", detail):
            return "Carte"

        # Redevance
        if trx_type == 'Frais liés au compte' or \
                counterparty.startswith('REDEVANCE MENSUELLE') or \
                detail.startswith('COMFORT PACK '):
            return "Redevance"

        # Proton
        if counterparty == 'CHARGEMENT CARTE PROTON' or \
            detail.startswith('DE VOTRE CARTE PROTON') or \
            search(r"^REMBOURSEMENT DU SOLDE.*DE VOTRE CARTE PROTON",
                      detail):
            return "Proton"

        # Frais
        if search(r"^FRAIS MENSUELS D'(EQUIPEMENT|UTILISATION)$",
                     counterparty) or counterparty == 'FRAIS DE PORT' or \
           search(r"^FRAIS D'UTILISATION PERIODE DU", detail) or \
           search(r"^PERIODE DU [0-9][0-9]-[0-9][0-9]-20[0-9][0-9] AU "
                     r"[0-9][0-9]-[0-9][0-9]-20[0-9][0-9].*DATE VALEUR : "
                     r"[0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$", detail) or \
           search(r"^REMBOURSEMENT DES.*FRAIS MENSUELS D'UTILISATION",
                     detail):
            return "Frais"

        # Annulation
        if search(r"^ANNULATION (DU )?PAIEMENT", counterparty) or \
           search(r"^ANNULATION (DU )?PAIEMENT", detail):
            return "Annulation"

        # Versement
        if counterparty.startswith('VERSEMENT DE') or \
           'VERSEMENT CHEQUE' in detail:
            return "Versement"

        # Virement
        if search(r".*[A-Z][A-Z][0-9][0-9].*COMMUNICATION.*:.*DATE.*: "
                     r"[0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$", detail) or \
           search(r"^DU COMPTE NO [A-Z][A-Z][0-9][0-9].*"
                     r"COMMUNICATION:.*DATE"
                     r" VALEUR : [0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$",
                     detail) or \
            search(r".*[A-Z][A-Z][0-9][0-9].*BIC .* REFERENCE DONNEUR "
                      r"D\'ORDRE : .*COMMUNICATION.*:", detail) or \
            search(r"PREMIER PRELEVEMENT D'UNE.*DOMICILIATION EUROPEENNE",
                      detail) or \
            'VIREMENT EUROPEEN' in detail or \
            'VIREMENT DU COMPTE' in detail or \
            'VIREMENT AU COMPTE' in detail or \
                'VIREMENT AVEC DATE-MEMO' in detail:
            return 'Virement2'

        # Mandat
        if search(r".*NUMERO DE MANDAT :.*[0-9]+ REFERENCE :.*[0-9]+ "
                     r"COMMUNICATION : .*DATE VALEUR : "
                     r"[0-9][0-9]\/[0-9][0-9]\/20[0-9][0-9]$", detail):
            return 'Mandat'

        # Archive
        if search(r"^ARCHIVE.*OPERATIONS", detail):
            return 'Archive'

        # Divers
        if search(r"^(DATE VALEUR|^EXECUTE LE)", detail):
            return "Divers"

        # Mastercard
        if search(r"^COMPTE INTERNE MASTERCARD.*ETAT"
                     r" DE DEPENSES NUMERO",
                     detail):
            return "Mastercard"

        # Inconnu
        return 'Inconnu'

    def parse(self, line: str = '', format: str = 'csv') -> bool:
        elements: List[str] = []

        if format == 'csv':
            elements = [element for element in
                        csv.reader([line], delimiter=';')][0]
            map(str(str).strip(), elements)  # type: ignore

        if self.csv_version == 3:
            ref_regex_pattern = r'^20[0-9]{2}-[0-9]{5}$'
        else:
            ref_regex_pattern = r'^20[0-9]{2}-[0-9]{4}$'

        if search(ref_regex_pattern, elements[0]):
            self.ref = elements[0]
        else:
            self.ref = ''
            return True

        d: datetime = datetime.strptime(elements[1], '%d/%m/%Y')
        self.date = d.strftime('%Y%m%d')

        if search(r'^(\-)?\d{1,3}\.\d{3},\d{1,2}$',  # 2.720,00
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
            trx_type=elements[6]
        )

        if self.type in ["" ,"Inconnu"]:
            print('ERROR: ', line)
            return False
        else:
            return True

    def get_ref(self) -> str:
        return self.ref

    def get_date(self) -> str:
        return self.date

    def get_amount(self) -> float:
        return self.amount

    def get_currency(self) -> str:
        return self.currency

    def get_type(self) -> str:
        return self.type

    def get_detail(self) -> str:
        return self.detail

    def get_account(self) -> str:
        return self.account

    def get_all(self) -> Dict[str, Union[str, int, float]]:
        return {
            'ref': self.ref,
            'date': self.date,
            'amount': self.amount,
            'currency': self.currency,
            'type': self.type,
            'detail': self.detail,
            'account': self.account,
        }
