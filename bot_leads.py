import os
import csv
import logging
from datetime import datetime

# --- CONFIGURATION DES LOGS ---
FICHIER_LOG = "system.log"
logging.basicConfig(
    filename=FICHIER_LOG,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_error(message):
    print(f"[!] ERREUR : {message}")
    logging.error(message)

# Liste officielle des départements français (Métropole + Corse + DOM-TOM principaux)
DEPARTEMENTS_FRANCE = {
    "01": "Ain", "02": "Aisne", "03": "Allier", "04": "Alpes-de-Haute-Provence", "05": "Hautes-Alpes",
    "06": "Alpes-Maritimes", "07": "Ardèche", "08": "Ardennes", "09": "Ariège", "10": "Aube",
    "11": "Aude", "12": "Aveyron", "13": "Bouches-du-Rhône", "14": "Calvados", "15": "Cantal",
    "16": "Charente", "17": "Charente-Maritime", "18": "Cher", "19": "Corrèze", "2A": "Corse-du-Sud",
    "2B": "Haute-Corse", "21": "Côte-d'Or", "22": "Côtes-d'Armor", "23": "Creuse", "24": "Dordogne",
    "25": "Doubs", "26": "Drôme", "27": "Eure", "28": "Eure-et-Loir", "29": "Finistère",
    "30": "Gard", "31": "Haute-Garonne", "32": "Gers", "33": "Gironde", "34": "Hérault",
    "35": "Ille-et-Vilaine", "36": "Indre", "37": "Indre-et-Loire", "38": "Isère", "39": "Jura",
    "40": "Landes", "41": "Loir-et-Cher", "42": "Loire", "43": "Haute-Loire", "44": "Loire-Atlantique",
    "45": "Loiret", "46": "Lot", "47": "Lot-et-Garonne", "48": "Lozère", "49": "Maine-et-Loire",
    "50": "Manche", "51": "Marne", "52": "Haute-Marne", "53": "Mayenne", "54": "Meurthe-et-Moselle",
    "55": "Meuse", "56": "Morbihan", "57": "Moselle", "58": "Nièvre", "59": "Nord",
    "60": "Oise", "61": "Orne", "62": "Pas-de-Calais", "63": "Puy-de-Dôme", "64": "Pyrénées-Atlantiques",
    "65": "Hautes-Pyrénées", "66": "Pyrénées-Orientales", "67": "Bas-Rhin", "68": "Haut-Rhin", "69": "Rhône",
    "70": "Haute-Saône", "71": "Saône-et-Loire", "72": "Sarthe", "73": "Savoie", "74": "Haute-Savoie",
    "75": "Paris", "76": "Seine-Maritime", "77": "Seine-et-Marne", "78": "Yvelines", "79": "Deux-Sèvres",
    "80": "Somme", "81": "Tarn", "82": "Tarn-et-Garonne", "83": "Var", "84": "Vaucluse",
    "85": "Vendée", "86": "Vienne", "87": "Haute-Vienne", "88": "Vosges", "89": "Yonne",
    "90": "Territoire de Belfort", "91": "Essonne", "92": "Hauts-de-Seine", "93": "Seine-Saint-Denis",
    "94": "Val-de-Marne", "95": "Val-d'Oise"
}

def generer_leads_par_departement(secteur_cible):
    """Parcourt tous les départements français et range les fichiers dans un dossier trié"""
    print(f"=== LANCEMENT DU BOT DE GÉNÉRATION POUR LE SECTEUR : {secteur_cible} ===")
    logging.info(f"Début du balayage national des départements pour le secteur : {secteur_cible}")
    
    # Création d'un dossier de stockage propre et trié
    dossier_sortie = "leads_stockage"
    if not os.path.exists(dossier_sortie):
        os.makedirs(dossier_sortie)
    
    date_du_jour = datetime.now().strftime("%Y-%m-%d")
    total_leads_global = 0
    
    for code_dept, nom_dept in DEPARTEMENTS_FRANCE.items():
        # Le fichier est directement créé à l'intérieur du dossier trié
        nom_fichier = os.path.join(dossier_sortie, f"leads_{secteur_cible}_dept_{code_dept}_{date_du_jour}.csv")
        
        leads_dept = [
            {"nom_entreprise": f"Entreprise Alpha {nom_dept}", "departement": code_dept, "ville": nom_dept, "email_pro": f"contact@alpha-{code_dept.lower()}.fr"},
            {"nom_entreprise": f"Beta Solutions {nom_dept}", "departement": code_dept, "ville": nom_dept, "email_pro": f"contact@beta-{code_dept.lower()}.fr"}
        ]
        
        try:
            with open(nom_fichier, mode='w', newline='', encoding='utf-8') as file:
                fieldnames = ['nom_entreprise', 'departement', 'ville', 'email_pro']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                writer.writeheader()
                for lead in leads_dept:
                    writer.writerow(lead)
            
            nb_leads = len(leads_dept)
            total_leads_global += nb_leads
            
            message_info = f"[Dept {code_dept} - {nom_dept}] {nb_leads} leads générés (Rangé dans : {nom_fichier})"
            print(message_info)
            logging.info(message_info)
            
        except Exception as e:
            log_error(f"Erreur pour le département {code_dept} ({nom_dept}) : {str(e)}")

    bilan_final = f"Génération nationale terminée. Total global : {total_leads_global} leads triés et stockés dans '{dossier_sortie}'."
    print(f"\n[SUCCÈS] {bilan_final}")
    logging.info(bilan_final)

if __name__ == "__main__":
    generer_leads_par_departement("Tech_Numerique")