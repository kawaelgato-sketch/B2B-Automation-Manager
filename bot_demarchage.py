import csv
import smtplib
import time
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# --- CONFIGURATION ---
CSV_CIBLES = "cibles_agences.csv"
SMTP_USER = "kawaelgato@gmail.com"
SMTP_PASS = "xmycjoxiojoftpfg"  # Ton mot de passe d'application
LIEN_PAYPAL = "https://www.paypal.com/ncp/payment/WFCDP9M5A2S46"

logging.basicConfig(filename="system.log", level=logging.INFO, format='%(asctime)s - %(message)s')

def envoyer_offre_prospection(destinataire, nom_entreprise):
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = destinataire
        msg['Subject'] = f"Opportunité : Leads qualifiés pour {nom_entreprise}"
        
        body = f"""Bonjour,

Nous avons identifié {nom_entreprise} comme un acteur clé dans votre secteur.
Pour booster votre développement commercial, nous proposons des listes de leads qualifiés et géolocalisés.

Vous pouvez obtenir votre pack de leads immédiatement ici : {LIEN_PAYPAL}

Une fois le paiement effectué, vous recevrez votre fichier CSV automatiquement.

Cordialement,
L'équipe commerciale"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Erreur envoi à {destinataire} : {e}")
        return False

def lancer_prospection():
    print("=== DÉMARRAGE DU BOT DE PROSPECTION AUTOMATISÉE ===")
    
    with open(CSV_CIBLES, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # On ne contacte que ceux qui ne sont pas encore payeurs
            if row.get('statut') == 'en_attente':
                email = row.get('email')
                nom = row.get('nom')
                
                print(f"[*] Envoi de l'offre à {nom} ({email})...")
                if envoyer_offre_prospection(email, nom):
                    print(f"[+] Offre envoyée.")
                
                # SÉCURITÉ : Pause de 2 minutes entre chaque mail pour éviter le bannissement
                time.sleep(120) 

if __name__ == "__main__":
    lancer_prospection()