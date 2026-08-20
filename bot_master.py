import subprocess
import os

def nettoyer_et_preparer_csv():
    """Remet les statuts à 'en_attente' uniquement si nécessaire ou prépare le fichier."""
    print("[~] Préparation du fichier cibles_agences.csv...")
    if not os.path.exists("cibles_agences.csv"):
        print("[-] Fichier cibles_agences.csv introuvable !")
        return False
    
    # Lecture du fichier
    with open("cibles_agences.csv", "r", encoding="utf-8") as f:
        lignes = f.readlines()
    
    nouvelles_lignes = []
    # On garde l'en-tête (la première ligne)
    nouvelles_lignes.append(lignes[0])
    
    # On parcourt les autres lignes
    for ligne in lignes[1:]:
        if ligne.strip(): # si la ligne n'est pas vide
            parts = ligne.strip().split(',')
            if len(parts) >= 4:
                # Ici, on pourrait ajouter une logique pour ne pas renvoyer
                # si on veut vraiment tout automatiser, on force en 'en_attente'
                parts[3] = 'en_attente'
                nouvelles_lignes.append(",".join(parts) + "\n")
    
    # Écriture du fichier mis à jour
    with open("cibles_agences.csv", "w", encoding="utf-8") as f:
        f.writelines(nouvelles_lignes)
    print("[+] Fichier prêt pour une nouvelle campagne.")
    return True

def lancer_script(nom_script):
    print(f"\n[~] Lancement de {nom_script}...")
    subprocess.run(["python", nom_script], check=True)

def main():
    print("=== DÉMARRAGE DU BOT MASTER AUTOMATISÉ ===")
    
    # 1. Scraping
    lancer_script("bot_prospect_scraper.py")
    
    # 2. Reset automatique des statuts
    nettoyer_et_preparer_csv()
    
    # 3. Démarchage
    lancer_script("bot_demarchage.py")
    
    print("\n[✔] CYCLE COMPLET TERMINÉ.")

if __name__ == "__main__":
    main()