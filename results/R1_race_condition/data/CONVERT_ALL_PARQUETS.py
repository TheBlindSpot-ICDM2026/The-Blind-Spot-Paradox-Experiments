import pandas as pd
from pathlib import Path

BASE_DIR = Path("/home/m53/The-Blind-Spot-Paradox-Experiments/results/R3_regime_crossover/")
RESULTS_DIR = BASE_DIR / "data"

def convertir_parquets():
    if not RESULTS_DIR.exists():
        print(f"[ERREUR ABSOLUE] Le répertoire {RESULTS_DIR} n'existe pas.")
        return

    # Recherche dynamique de tous les fichiers .parquet dans le répertoire
    fichiers_trouves = list(RESULTS_DIR.glob("*.parquet"))
    
    if not fichiers_trouves:
        print(f"[INFO] Aucun fichier .parquet trouvé dans {RESULTS_DIR}.")
        return

    print(f"[INFO] {len(fichiers_trouves)} fichier(s) .parquet trouvé(s). Début de la conversion...")

    for chemin_parquet in fichiers_trouves:
        chemin_csv = chemin_parquet.with_suffix('.csv')
        
        print(f"Chargement de {chemin_parquet.name}...")
        try:
            df = pd.read_parquet(chemin_parquet)
            df.to_csv(chemin_csv, index=False)
            print(f"[SUCCÈS] Converti en : {chemin_csv.name}")
        except Exception as e:
            print(f"[ERREUR CRITIQUE] Échec lors de la conversion de {chemin_parquet.name} : {e}")

if __name__ == "__main__":
    convertir_parquets()