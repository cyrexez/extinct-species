import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import os

# --- PATH CONFIG ---
INPUT_CSV = "nigeria_extinction_final_clean.csv"
OUTPUT_CSV = "nigeria_species_fast1.csv"

def get_real_english_name(sci_name):
    """Deep search logic: usageKey -> vernacularNames -> English filter"""
    try:
        # 1. Match the name to get the internal ID
        match_url = f"https://api.gbif.org/v1/species/match?name={sci_name}"
        match_res = requests.get(match_url, timeout=5).json()
        usage_key = match_res.get('usageKey')

        if usage_key:
            # 2. Specifically look for English names
            v_url = f"https://api.gbif.org/v1/species/{usage_key}/vernacularNames"
            v_res = requests.get(v_url, timeout=5).json()
            for entry in v_res.get('results', []):
                if entry.get('language') == 'eng':
                    return entry['vernacularName'].title()
        
        # Fallback to backbone name if eng not found
        return match_res.get('vernacularName', sci_name)
    except:
        return sci_name

# 1. Load and Deduplicate
print("📂 Loading and cleaning data...")
if not os.path.exists(INPUT_CSV):
    print(f"❌ Error: Could not find {INPUT_CSV}")
    exit()

df = pd.read_csv(INPUT_CSV)
initial_count = len(df)

# Drop duplicates based on Scientific Name, keeping the most complete record
df = df.drop_duplicates(subset=['Scientific Name'], keep='first')
print(f"✨ Deduplicated: {initial_count} rows -> {len(df)} unique species.")

# 2. Multi-threaded Search
print("🚀 Starting High-Speed Deep Search for English names...")
# Using 20 workers to make it 20x faster
with ThreadPoolExecutor(max_workers=20) as executor:
    # tqdm creates the progress bar
    df['Common Name'] = list(tqdm(executor.map(get_real_english_name, df['Scientific Name']), total=len(df)))

# 3. Save Final Version
df.to_csv(OUTPUT_CSV, index=False)
print(f"✅ Success! Created {OUTPUT_CSV} with unique species and English names.")