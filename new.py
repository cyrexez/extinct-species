import pandas as pd
import requests
from io import StringIO

csv_data = """Scientific Name
Hexanchus griseus
Diplodus cervinus
Chamaeleo africanus
Loxodonta africana
Pedaria durandi"""

df = pd.read_csv(StringIO(csv_data))

def get_real_english_name(sci_name):
    try:
        # 1. Get the ID (usageKey) for the species
        match_url = f"https://api.gbif.org/v1/species/match?name={sci_name}"
        match_res = requests.get(match_url, timeout=5).json()
        usage_key = match_res.get('usageKey')

        if usage_key:
            # 2. Specifically look for English vernacular names using the ID
            v_url = f"https://api.gbif.org/v1/species/{usage_key}/vernacularNames"
            v_res = requests.get(v_url, timeout=5).json()
            
            # Look for the first name labeled as English ('eng')
            for entry in v_res.get('results', []):
                if entry.get('language') == 'eng':
                    return entry['vernacularName'].title()
        
        # Fallback to backbone name if no specific English record exists
        return match_res.get('vernacularName', sci_name)
    except:
        return sci_name

print("🚀 Running deep search for English names...")
df['Common Name'] = df['Scientific Name'].apply(get_real_english_name)
print("\n--- NEW TEST RESULTS ---")
print(df)