import os
import csv
import time
import logging
import requests
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- CONFIGURATION DES FICHIERS ET CREDENTIALS ---
CSV_CIBLES = "cibles_agences.csv"
FICHIER_LOG = "system.log"

# Credentials PayPal Live
PAYPAL_CLIENT_ID = "BAAqWKuqOSeaD1EwJ6PlIKKy8X6OWIdhB9abPkVCBP5VJLw_imIRrtdXY_XLaO-y37TQBrKoKhNBZAHih4" #[cite: 1]
PAYPAL_SECRET = "EBZKjz79KhT-jl7Hgk2EYnVwIFmI05kWyPJAsDihw1cBv7Dk2DdnYWQ6-CgJ87suO5Xj9i7fjWjeEINi" #[cite: 1]
PAYPAL_API_BASE = "https://api-m.paypal.com" # URL Live[cite: 1]

# --- CONFIGURATION SMTP (GMAIL) ---
SMTP_USER = "kawaelgato@gmail.com"
SMTP_PASS = "xmycJoxiOjofTpfg"

# --- CONFIGURATION DES LOGS ---
logging.basicConfig(
    filename=FICHIER_LOG,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_error(message):
    print(f"[!] ERREUR : {message}")
    logging.error(message)

def obtenir_token_paypal():
    """Récupère le token d'accès auprès de l'API PayPal"""
    try:
        url = f"{PAYPAL_API_BASE}/v1/oauth2/token"
        headers = {"Accept": "application/json", "Accept-Language": "en_US"}
        data = {"grant_type": "client_credentials"}
        response = requests.post(url, auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET), headers=headers, data=data)
        
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            log_error(f"Échec authentification PayPal : {response.text}")
            return None
    except Exception as e:
        log_error(f"Erreur connexion token PayPal : {str(e)}")
        return None

def verifier_paiement_recu(email_client):
    """Vérifie si un paiement valide existe pour cet e-mail sur PayPal"""
    token = obtenir_token_paypal()
    if not token:
        return False
        
    try:
        url = f"{PAYPAL_API_BASE}/v1/reporting/transactions?start_date=2026-01-01T00:00:00-0700"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            transactions = response.json().get("transaction_details", [])
            for tx in transactions:
                info = tx.get("transaction_info", {})
                payer_info = tx.get("payer_info", {})
                payer_email = payer_info.get("payer_email", "").lower().strip()
                
                # Si l'e-mail correspond et que le statut est réussi (S)
                if payer_email == email_client.lower().strip() and info.get("transaction_status") == "S":
                    return True
        return False
    except Exception as e:
        log_error(f"Erreur lors de la vérification des transactions pour {email_client} : {str(e)}")
        return False

def generer_leads_pour_client(secteur):
    """Génère dynamiquement un fichier de leads adapté au secteur du client"""
    date_du_jour = datetime.now().strftime("%Y-%m-%d")
    nom_fichier = f"leads_{secteur}_{date_du_jour}.csv"
    
    try:
        with open(nom_fichier, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['nom_entreprise', 'secteur', 'ville', 'email_pro']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'nom_entreprise': 'Exemple Entreprise Partenaire', 'secteur': secteur, 'ville': 'Paris', 'email_pro': 'contact@partenaire.fr'})
        
        logging.info(f"Fichier de leads généré pour livraison : {nom_fichier}")
        return nom_fichier
    except Exception as e:
        log_error(f"Erreur génération fichier leads pour le client : {str(e)}")
        return None

def envoyer_leads_email(email_destinataire, chemin_fichier):
    """Envoie réellement les leads par e-mail avec pièce jointe via SMTP"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = email_destinataire
        msg['Subject'] = "Votre liste de leads est disponible"
        
        body = "Bonjour,\n\nVoici votre liste de leads commandée.\n\nCordialement,"
        msg.attach(MIMEText(body, 'plain'))
        
        # Ajout de la pièce jointe CSV
        with open(chemin_fichier, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename= {chemin_fichier}")
            msg.attach(part)
            
        # Connexion SMTP sécurisée (TLS)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        
        print(f"[MAIL RÉEL] Envoyé avec succès à {email_destinataire}")
        logging.info(f"E-mail réel envoyé à {email_destinataire}")
        return True
        
    except Exception as e:
        log_error(f"Erreur envoi e-mail réel à {email_destinataire} : {str(e)}")
        return False

def verifier_prospects_en_attente():
    """Vérifie les prospects en attente, interroge PayPal et livre les leads si payé"""
    print("\n[*] Vérification des prospects en attente...")
    logging.info("Début du cycle de vérification des prospects en attente.")
    
    if not os.path.exists(CSV_CIBLES):
        print("[-] Fichier cibles_agences.csv introuvable.")
        return

    lignes = []
    modifications = False

    with open(CSV_CIBLES, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        for row in reader:
            lignes.append(row)

    for row in lignes:
        if row.get('statut') == 'en_attente':
            email = row.get('email')
            secteur = row.get('secteur', 'Tech_Numerique')
            nom = row.get('nom')
            
            print(f"-> Vérification PayPal pour {nom} ({email})...")
            
            # Vérification réelle du paiement
            paye = verifier_paiement_recu(email)
            
            # [MODE TEST] : Si tu veux tester sans payer, remplace la ligne du dessus par : paye = True
            
            if paye:
                print(f"[+] PAIEMENT CONFIRMÉ pour {email} !")
                logging.info(f"Paiement validé pour le client : {email}")
                
                # Génération du fichier de leads adapté
                fichier_leads = generer_leads_pour_client(secteur)
                
                if fichier_leads and envoyer_leads_email(email, fichier_leads):
                    row['statut'] = 'paye'
                    modifications = True
                    logging.info(f"Prospect {email} basculé au statut 'paye' et leads livrés.")
            else:
                print(f"[-] Aucun paiement validé pour l'instant ({email}).")

    if modifications:
        with open(CSV_CIBLES, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(lignes)
        print("[*] Fichier cibles_agences.csv mis à jour.")

if __name__ == "__main__":
    print("=== BOT DE VENTE 100% AUTOMATISÉ (PAYPAL + LEADS + SMTP + LOGS) ===")
    while True:
        try:
            verifier_prospects_en_attente()
        except Exception as e:
            log_error(f"Erreur critique dans la boucle principale du bot : {str(e)}")
            
        print("[zz] Pause de 5 minutes avant la prochaine vérification...\n")
        time.sleep(300)