import os
import csv
import logging
from datetime import datetime

# --- CONFIGURATION DES FICHIERS ---
CSV_CIBLES = "cibles_agences.csv"
CSV_VRAIS_CONTACTS = "vrais_contacts_pro.csv"  # Ton vrai carnet d'adresses propre
FICHIER_LOG = "system.log"

# --- CONFIGURATION DES LOGS ---
logging.basicConfig(
    filename=FICHIER_LOG,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_error(message):
    print(f"[!] ERREUR : {message}")
    logging.error(message)

def charger_emails_existants():
    """Charge les e-mails déjà traités pour éviter les doublons"""
    emails_existants = set()
    if os.path.exists(CSV_CIBLES):
        with open(CSV_CIBLES, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if 'email' in row:
                    emails_existants.add(row['email'].lower().strip())
    return emails_existants

def lire_vrai_carnet_adresses():
    """Lit directement ton carnet d'adresses réel en production"""
    prospects = []
    
    # Si le carnet réel n'existe pas encore, on le crée vide pour éviter tout plantage
    if not os.path.exists(CSV_VRAIS_CONTACTS):
        with open(CSV_VRAIS_CONTACTS, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['nom', 'email', 'secteur'])
            writer.writeheader()
        print(f"[*] Fichier '{CSV_VRAIS_CONTACTS}' créé. Ajoute tes vrais contacts dedans une seule fois.")
        return prospects

    with open(CSV_VRAIS_CONTACTS, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if 'email' in row and row['email'].strip():
                prospects.append(row)
                
    return prospects

def ajouter_nouveaux_prospects():
    print("=== DÉMARRAGE DU BOT DE SYNCHRONISATION (CARNET RÉEL) ===")
    logging.info("Démarrage de la synchronisation avec le carnet d'adresses réel.")
    
    file_exists = os.path.exists(CSV_CIBLES)
    emails_deja_presents = charger_emails_existants()
    source_prospects = lire_vrai_carnet_adresses()
    
    if not source_prospects:
        print(f"[-] Ton carnet '{CSV_VRAIS_CONTACTS}' est vide. Ajoute tes vrais contacts dedans.")
        return

    nouveaux_ajoutes = 0
    doublons_ignores = 0

    try:
        with open(CSV_CIBLES, mode='a', newline='', encoding='utf-8') as file:
            fieldnames = ['nom', 'email', 'secteur', 'statut']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()

            for p in source_prospects:
                email = p.get('email', '').lower().strip()
                nom = p.get('nom', 'Inconnu').strip()
                secteur = p.get('secteur', 'General').strip()
                
                if email and email not in emails_deja_presents:
                    writer.writerow({
                        'nom': nom,
                        'email': email,
                        'secteur': secteur,
                        'statut': 'en_attente'
                    })
                    emails_deja_presents.add(email)
                    nouveaux_ajoutes += 1
                else:
                    doublons_ignores += 1

        print(f"\n[SUCCÈS] Synchro réussie : {nouveaux_ajoutes} nouveau(x) vrai(s) prospect(s) injecté(s).")
        logging.info(f"Synchro réussie : {nouveaux_ajoutes} ajoutés, {doublons_ignores} doublons ignorés.")

    except Exception as e:
        log_error(f"Erreur critique lors de la synchronisation : {str(e)}")

if __name__ == "__main__":
    ajouter_nouveaux_prospects()