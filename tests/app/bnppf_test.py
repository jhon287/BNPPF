#!/usr/bin/env python3

import unittest
import bnppf


class Test(unittest.TestCase):
    trx_csv_v1: bnppf.BNPPF = bnppf.BNPPF(csv_version=1)
    trx_csv_v2: bnppf.BNPPF = bnppf.BNPPF(csv_version=2)
    trx_csv_v3: bnppf.BNPPF = bnppf.BNPPF(csv_version=3)

    def test_csv_version(self):
        # v1
        header: str = ("Num�ro de s�quence;Date d'ex�cution;Date valeur;"
                       "Montant;Devise du compte;D�tails;Num�ro de compte")
        self.assertEqual(bnppf.get_csv_version(line=header), 1)

        # v2
        header = ("N� de s�quence;Date d'ex�cution;Date valeur;Montant;"
                  "Devise du compte;CONTREPARTIE DE LA TRANSACTION;"
                  "D�tails;Num�ro de compte")
        self.assertEqual(bnppf.get_csv_version(line=header), 2)

        # v3
        header = ("Nº de séquence;Date d'exécution;Date valeur;Montant;"
                  "Devise du compte;Numéro de compte;"
                  "Type de transaction;Contrepartie;"
                  "Nom de la contrepartie;Communication;Détails;Statut;"
                  "Motif du refus")
        self.assertEqual(bnppf.get_csv_version(line=header), 3)

    def test_account(self):
        line: str = ("2000-00001;01/01/2000;01/01/2000;-2.720,12;EUR;"
                     "BE05123456789012;Virement en euros;BE05123456789012;"
                     "SABBE JONATHAN;;ABCDEFGHIJKLMNOPQRSTUVWXYZ;Accepté;")
        self.trx_csv_v3.parse(line=line)
        self.assertEqual(first=self.trx_csv_v3.get_account(),
                         second='BE05123456789012')

    def test_currency(self):
        line: str = ("2000-00001;01/01/2000;01/01/2000;-2.720,12;EUR;"
                     "BE05123456789012;Virement en euros;BE05123456789012;"
                     "SABBE JONATHAN;;ABCDEFGHIJKLMNOPQRSTUVWXYZ;Accepté;")
        self.trx_csv_v3.parse(line=line)
        self.assertEqual(first=self.trx_csv_v3.get_currency(), second='EUR')

    def test_date(self):
        line: str = ("2000-00001;01/01/2000;01/01/2000;-2.720,12;EUR;"
                     "BE05123456789012;Virement en euros;BE05123456789012;"
                     "SABBE JONATHAN;;ABCDEFGHIJKLMNOPQRSTUVWXYZ;Accepté;")
        self.trx_csv_v3.parse(line=line)
        self.assertEqual(first=self.trx_csv_v3.get_date(), second='20000101')

    def test_ref(self):
        line: str = ""

        # CSV v3
        line = ("2022-01538;02/12/2022;30/11/2022;-28.96;EUR;BE05123456789012"
                ";Paiement par carte;;;;PAIEMENT AVEC LA CARTE DE DEBIT "
                "NUMERO 4871 04XX XXXX 1711 BIOSTORY JOGOIGNE JOGOIGNE "
                "30/11/2022 VISA DEBIT - Apple Pay REFERENCE BANQUE : "
                "2212021425068897 DATE VALEUR : 30/11/2022;Accepté;")
        self.trx_csv_v3.parse(line=line)
        self.assertEqual(first=self.trx_csv_v3.get_ref(), second='2022-01538')

        # CSV v2
        line = ("2019-0027;02/04/2019;01/04/2019;1.55;EUR;INTERETS NETS : "
                "DETAILS VOIR ANN;REFERENCE BANQUE : 1904020435103482 DATE "
                "VALEUR : 01/04/2019;BE05123456789012")
        self.trx_csv_v2.parse(line=line)
        self.assertEqual(first=self.trx_csv_v2.get_ref(), second='2019-0027')

        # CSV v1
        line = ("2017-0170;08/03/2017;08/03/2017;-12,60;EUR;AVEC LA CARTE "
                "6703 04XX XXXX X200 2 DP FOOD SPRL      JODOIGNE08-03-2017 "
                "DATE VALEUR : 08/03/2017;BE05123456789012")
        self.trx_csv_v1.parse(line=line)
        self.assertEqual(first=self.trx_csv_v1.get_ref(), second='2017-0170')

        # Empty ref
        line = ("2017-;11/11/2017;11/11/2017;-0,20;EUR;EASY SAVE - EPARGNE "
                "AUTOMATIQUE ;POUR COMPTE BE05 1234 5678 9012 DE SABBE "
                "JONATHANDATE VALEUR : 11/11/2017;BE05123456789012")
        self.trx_csv_v2.parse(line=line)
        self.assertEqual(first=self.trx_csv_v2.get_ref(), second='')

    def test_amount(self):
        # 2.720.12
        line: str = ("2000-00001;01/01/2000;01/01/2000;-2.720,12;EUR;"
                     "BE05123456789012;Virement en euros;BE05123456789012;"
                     "SABBE JONATHAN;;ABCDEFGHIJKLMNOPQRSTUVWXYZ;Accepté;")
        trx: bnppf.BNPPF = bnppf.BNPPF()
        trx.parse(line=line)
        self.assertEqual(first=trx.get_amount(), second=-2720.12)

        # 2720.12
        line = ("2000-00001;01/01/2000;01/01/2000;-2720.12;EUR;"
                "BE05123456789012;Virement en euros;BE05123456789012;"
                "SABBE JONATHAN;;ABCDEFGHIJKLMNOPQRSTUVWXYZ;Accepté;")
        trx.parse(line=line)
        self.assertEqual(first=trx.get_amount(), second=-2720.12)

        # 2720,12
        line = ("2000-00001;01/01/2000;01/01/2000;-2720,12;EUR;"
                "BE05123456789012;Virement en euros;BE05123456789012;"
                "SABBE JONATHAN;;ABCDEFGHIJKLMNOPQRSTUVWXYZ;Accepté;")
        trx.parse(line=line)
        self.assertEqual(first=trx.get_amount(), second=-2720.12)

    def test_detail(self):
        line: str = (
            "2000-00001;01/01/2000;01/01/2000;-2720,12;EUR;"
            "BE05123456789012;Virement en euros;BE05123456789012;"
            "SABBE JONATHAN;;ABCDEFGHIJKLMNOPQRSTUVWXYZ;Accepté;"
        )
        trx: bnppf.BNPPF = bnppf.BNPPF()
        trx.parse(line=line)
        self.assertEqual(first=trx.get_detail(),
                         second='ABCDEFGHIJKLMNOPQRSTUVWXYZ')

    def test_get_all(self):
        line: str = (
            "2000-00001;01/01/2000;01/01/2000;-2720,12;EUR;"
            "BE05123456789012;Virement en euros;BE05123456789012;"
            "SABBE JONATHAN;;ABCDEFGHIJKLMNOPQRSTUVWXYZ;Accepté;"
        )
        trx: bnppf.BNPPF = bnppf.BNPPF()
        trx.parse(line=line)
        self.assertTrue(expr=type(trx.get_all()) == dict)
        self.assertTrue(expr=type(trx.__str__()) == str)

    def test_trx_easy_safe(self):
        line: str = ("2022-00234;21/02/2022;21/02/2022;-0.98;EUR;"
                     "BE05123456789012;Virement en euros;BE05123456789012;"
                     "SABBE JONATHAN;;EASY SAVE - EPARGNE AUTOMATIQUE "
                     "(ORDRE PERMANENT) POUR COMPTE BE37 XXXX XXXX 4428 "
                     "DE SABBE JONATHAN REFERENCE BANQUE : 2202210039506160 "
                     "DATE VALEUR : 21/02/2022;Accepté;")
        self.trx_csv_v3.parse(line=line)
        self.assertEqual(first=self.trx_csv_v3.get_type(), second='Easy Save')

    def test_trx_interets(self):
        line: str = ("2023-00001;01/01/2023;01/01/2023;1.77;EUR;"
                     "BE05123456789012;Intérêts du compte d'épargne;;;;"
                     "INTERETS NETS : DETAILS VOIR ANNEXE REFERENCE BANQUE : "
                     "2301010945415640 DATE VALEUR : 01/01/2023;Accepté;")
        self.trx_csv_v3.parse(line=line)
        self.assertEqual(first=self.trx_csv_v3.get_type(), second='Interets')

        line = ("2017-0026;01/04/2017;01/04/2017;0,58;EUR;INTERETS NETS "
                ": DETAILS VOIR ANN;DATE VALEUR : 01/04/2017 ;"
                "BE05123456789012")
        self.trx_csv_v2.parse(line=line)
        self.assertEqual(first=self.trx_csv_v2.get_type(), second='Interets')

    def test_trx_cash(self):
        line: str = ("2021-0397;23/04/2021;23/04/2021;123.00;EUR;VERSEMENT "
                     "ESPECES               ;EN CASH DEPOSIT AVEC LA CARTE "
                     "6703 04XX XXXX X200 2 A L'AGENCE JODOIGNE CASH RECY "
                     "COMMUNICATION: RETOUR GARRANTIE APPARTEMENT MIDDLEKE "
                     "RKE DATE VALEUR : 23/04/2021;BE05123456789012")
        self.trx_csv_v2.parse(line=line)
        self.assertEqual(first=self.trx_csv_v2.get_type(), second='Cash')

    def test_trx_bonus(self):
        line: str = ("2019-0090;01/02/2019;01/02/2019;12.00;EUR;VERSEMENT DE "
                     "VOTRE BONUS 2018   ;VOTRE FIDELITE EST RECOMPENSEE "
                     "VOIR DETAILS EN ANNEXE EXECUTE LE 31-01 DATE VALEUR : "
                     "01/02/2019;BE05123456789012")
        self.trx_csv_v2.parse(line=line)
        self.assertEqual(first=self.trx_csv_v2.get_type(), second='Bonus')

    def test_trx_redevance(self):
        line: str = ("2017-0353;07/06/2017;01/06/2017;-3,00;EUR;REDEVANCE "
                     "MENSUELLE             ;COMFORT PACK DATE VALEUR : "
                     "01/06/2017;BE05123456789012")
        self.trx_csv_v2.parse(line=line)
        self.assertEqual(first=self.trx_csv_v2.get_type(), second='Redevance')

        line: str = ("2023-00002;01/01/2023;01/01/2023;-1.23;EUR;"
                     "BE05123456789012;Frais liés au compte;;;;"
                     "ASSURANCE-COMPTE REFERENCE BANQUE : 2301011603366249 "
                     "DATE VALEUR : 01/01/2023;Accepté;")
        self.trx_csv_v3.parse(line=line)
        self.assertEqual(first=self.trx_csv_v3.get_type(), second='Redevance')

    def test_trx_annulation(self):
        line: str = ("2019-1379;30/12/2019;28/12/2019;26.00;EUR;ANNULATION "
                     "DU PAIEMENT DU 28/12/;AVEC LA CARTE DE DEBIT NUMERO "
                     "6703 04XX XXXX X200 2 LOUVAIN-LA EUR26,00 REFERENCE "
                     "BANQUE : 1912301216561975 DATE VALEUR : 28/12/2019;"
                     "BE05123456789012")
        self.trx_csv_v2.parse(line=line)
        self.assertEqual(first=self.trx_csv_v2.get_type(),
                         second='Annulation')

    def test_trx_carte(self):
        line: str = ("2021-0214;03/10/2021;03/10/2021;-11.44;EUR;PAIEMENT "
                     "AVEC LA CARTE DE DEBIT ;NUMERO 4871 04XX XXXX 2247 AD "
                     "DELHAIZE JODO  JODOIGNE 03/10/2021 DATE VALEUR : "
                     "03/10/2021;BE05123456789012")
        self.trx_csv_v2.parse(line=line)
        self.assertEqual(first=self.trx_csv_v2.get_type(), second='Carte')

        line = ("2022-01532;01/12/2022;30/11/2022;-4.55;EUR;"
                "BE05123456789012;Paiement par carte;;;;PAIEMENT AVEC "
                "LA CARTE DE DEBIT NUMERO 4871 04XX XXXX 1711 DP FOOD "
                "JODOIGNE 30/11/2022 VISA DEBIT - Apple Pay REFERENCE "
                "BANQUE : 2212011356465578 DATE VALEUR : 30/11/2022;"
                "Accepté;")
        self.trx_csv_v3.parse(line=line)
        self.assertEqual(first=self.trx_csv_v3.get_type(), second='Carte')

    def test_trx_p2m(self):
        line: str = ("2021-0170;09/08/2021;09/08/2021;6.90;EUR;PAIEMENT "
                     "MOBILE                 ;COMPTE DU DONNEUR D'ORDRE : "
                     "BE94 2500 5316 8314  BIC GEBABEBB DATE VALEUR : "
                     "09/08/2021;BE05123456789012")
        self.trx_csv_v2.parse(line=line)
        self.assertEqual(first=self.trx_csv_v2.get_type(), second='P2M')

        line = ("2022-01326;21/10/2022;21/10/2022;21.32;EUR;"
                "BE05123456789012;Paiement par carte;BE05123456789012;"
                "BANKSYS;29378773000020102214452010221445651281894130030"
                "2052300000877300000000044000000000000000P2P MOBILE 000;"
                "PAIEMENT MOBILE COMPTE DU DONNEUR D'ORDRE : "
                "BE05 1234 5678 9012 BIC ABCDBEBB REFERENCE BANQUE : "
                "2210210901595603 DATE VALEUR : 21/10/2022;Accepté;")
        self.trx_csv_v3.parse(line=line)
        self.assertEqual(first=self.trx_csv_v3.get_type(), second='P2M')

    def test_trx_domiciliation(self):
        line: str = ("2022-0191;09/02/2022;09/02/2022;-35.95;EUR;"
                     "NL49ABNA0514089784;DOMICILIATION EUROPEENNE DE "
                     "HELLOFRESH NUMERO DE MANDAT : 1319442315350586 "
                     "REFERENCE : C7419442315397120C COMMUNICATION : "
                     "HELLOFRESH BENELUX B.V. HELLOFRESH285 537979;"
                     "BE05123456789012")
        self.trx_csv_v2.parse(line=line)
        self.assertEqual(first=self.trx_csv_v2.get_type(),
                         second='Domiciliation')

        line = ("2022-01535;02/12/2022;02/12/2022;-100.00;EUR;"
                "BE05123456789012;Domiciliation;BE38001697497572;AG "
                "INSURANCE;Home Invest Plan 006-7348614-59PRIME DE "
                "12/2022;DOMICILIATION EUROPEENNE DE AG INSURANCE "
                "NUMERO DE MANDAT : 301465359 REFERENCE : 000042991 "
                "16827954701 COMMUNICATION : HOME INVEST PLAN "
                "006-7348614-59PRIME DE 12/2022 REFERENCE BANQUE : "
                "2212020650045340 DATE VALEUR : 02/12/2022;Accepté;")
        self.trx_csv_v3.parse(line=line)
        self.assertEqual(first=self.trx_csv_v3.get_type(),
                         second='Domiciliation')

    def test_trx_ordre_permanent(self):
        line: str = ("2022-01517;01/12/2022;01/12/2022;-850.00;EUR;"
                     "BE05123456789012;Ordre permanent;BE83140058282115;"
                     "LAFRUIT JOSIANA;Loyer - Sabbe Jonathan;VOTRE ORDRE "
                     "PERMANENT AU PROFIT DU COMPTE BE83 1400 5828 2115 BIC "
                     "GEBABEBB LAFRUIT JOSIANA COMMUNICATION: LOYER - SABBE "
                     "JONATHAN REFERENCE BANQUE : 2212010332237736 DATE "
                     "VALEUR : 01/12/2022;Accepté")
        self.trx_csv_v3.parse(line=line)
        self.assertEqual(first=self.trx_csv_v3.get_type(),
                         second='Ordre Permanent')

        line = ('"2011-0244";"16/08/2011";"16/08/2011";"-250,56";"EUR";'
                '"934-5312839-32";"VOTRE ORDRE PERMANENT AU PROFIT          '
                '16-08          250,56-DU COMPTE 934-5312839-32 DE RECORD '
                'CREDIT SERVICES COMMUNICATION: 934531283932 EXECUTE LE '
                '14-08 DATE VALEUR : 16/08/2011 ";"BE05 1234 5678 9012 "')
        self.trx_csv_v2.parse(line=line)
        self.assertEqual(first=self.trx_csv_v2.get_type(),
                         second='Ordre Permanent')

    def test_trx_bcc(self):
        line: str = ("2017-0446;13/07/2017;13/07/2017;-123,45;EUR;PAIEMENT A "
                     "BANK CARD COMPANY    ;COMPTE INTERNE MASTERCARD: ETAT "
                     "DE DEPENSES NUMERO 185DATE VALEUR : 13/07/2017;"
                     "BE05123456789012")
        self.trx_csv_v2.parse(line=line)
        self.assertEqual(first=self.trx_csv_v2.get_type(), second='BCC')

        line = ("2022-01585;13/12/2022;13/12/2022;-123.45;EUR;"
                "BE05123456789012;Paiement par carte de crédit;;;MASTERCARD "
                "338 17655880-01/043717655880228;PAIEMENT A BANK CARD "
                "COMPANY COMPTE INTERNE MASTERCARD: 17655880 ETAT DE "
                "DEPENSES NUMERO 338 REFERENCE BANQUE : 2212130902163844 "
                "DATE VALEUR : 13/12/2022;Accepté;")
        self.trx_csv_v3.parse(line=line)
        self.assertEqual(first=self.trx_csv_v3.get_type(), second='BCC')

    def test_trx_assurance(self):
        line: str = ("2017-0007;06/01/2017;01/01/2017;-1,23;EUR;ASSURANCE "
                     "COMPTE                ;DATE VALEUR : 01/01/2017 ;"
                     "BE05123456789012")
        self.trx_csv_v2.parse(line=line)
        self.assertEqual(first=self.trx_csv_v2.get_type(), second='Assurance')

    def test_trx_retrait(self):
        line: str = ("2017-0346;03/06/2017;03/06/2017;-12,34;EUR;RETRAIT "
                     "D'ARGENT AUTRES DISTRIBU;AVEC LA CARTE 6703 04XX XXXX "
                     "X200 2 JODOIGNE          JODOIGNE03/06/2017 DATE "
                     "VALEUR : 03/06/2017;BE05123456789012")
        self.trx_csv_v2.parse(line=line)
        self.assertEqual(first=self.trx_csv_v2.get_type(), second='Retrait')

    def test_trx_proton(self):
        line: str = ('"2014-0497";"02/10/2014";"02/10/2014";"-10,00";"EUR";'
                     '"CHARGEMENT CARTE PROTON";"NUMERO 6703 04XX XXXX X200 '
                     '2 DU 02-10-2014 COMMUNICATION: BANKSYS HALL    1130 '
                     'DATE VALEUR : 02/10/2014";"BE05 1234 5678 9012 ";')
        self.trx_csv_v2.parse(line=line)
        self.assertEqual(first=self.trx_csv_v2.get_type(), second='Proton')

    def test_trx_frais(self):
        line: str = ('"2014-0173";"07/08/2014";"01/08/2014";"-1,23";"EUR";'
                     '"FRAIS MENSUELS D\'EQUIPEMENT";"PERIODE DU 01-08-2014 '
                     'AU 31-08-2014 DETAILS VOIR ANNEXE EXECUTE LE 06-08 '
                     'DATEVALEUR : 01/08/2014";"BE05 1234 5678 9012 "')
        self.trx_csv_v2.parse(line=line)
        self.assertEqual(first=self.trx_csv_v2.get_type(), second='Frais')

    def test_trx_versement(self):
        line: str = ('"2011-0240";"11/08/2011";"13/08/2011";"+123,45";"EUR"'
                     ';"VERSEMENT CHEQUE";"VERSEMENT CHEQUE                '
                     '         13-08          600,00+NUMERO 5426475949 VIA '
                     'HAMME-MILLE DATE VALEUR : 13/08/2011 ";'
                     '"BE05 1234 5678 9012 "')
        self.trx_csv_v2.parse(line=line)
        self.assertEqual(first=self.trx_csv_v2.get_type(), second='Versement')

    def test_trx_mandat(self):
        line: str = ("2017-0350;06/06/2017;06/06/2017;-20,00;EUR;"
                     "BE05123456789012;GREENPEACE BELGIUM NUMERO DE MANDAT "
                     ":GPB1234567890 REFERENCE : 000123456789 COMMUNICATION "
                     ": 1234567890 DATE VALEUR : 06/06/2017;BE05123456789012")
        self.trx_csv_v2.parse(line=line)
        self.assertEqual(first=self.trx_csv_v2.get_type(), second='Mandat')

    def test_trx_archive(self):
        line: str = ('"2015-0427";"06/07/2015";"05/07/2015";"-5,00";"EUR";'
                     '"000-0000000-00";"ARCHIVE D\'OPERATIONS                '
                     '     05-07            5,00- DOSSIER NO '
                     '0000001180-1-495654 COMPTE NUMERO 123-4567890-12 '
                     'EXECUTE LE 05-07 DATE VALEUR : 05/07/2015";'
                     '"BE05 1234 5678 9012 ')
        self.trx_csv_v2.parse(line=line)
        self.assertEqual(first=self.trx_csv_v2.get_type(), second='Archive')

    def test_trx_inconnu(self):
        line: str = ('"2015-0427";"06/07/2015";"05/07/2015";"-5,00";"EUR";'
                     '"000-0000000-00";"ARCHIVE D\'OPERATIONS                '
                     '     05-07            5,00- DOSSIER NO '
                     '0000001180-1-495654 COMPTE NUMERO 123-4567890-12 '
                     'EXECUTE LE 05-07 DATE VALEUR : 05/07/2015";'
                     '"BE05 1234 5678 9012 ')
        self.trx_csv_v1.parse(line=line)
        self.assertEqual(first=self.trx_csv_v1.get_type(), second='Inconnu')


if __name__ == '__main__':
    unittest.main()
