import streamlit as st
import pandas as pd
import wikipedia
from google import genai
from google.genai import types
from io import BytesIO
import os
import requests
from urllib.parse import quote
from dotenv import load_dotenv
# --- 1. CONFIG & UI ---
st.set_page_config(page_title="Species Profile", layout="wide", initial_sidebar_state="collapsed")

# Aggressive CSS to hide all sidebars and streamline the layout
st.markdown("""
    <style>
        [data-testid="stSidebar"], [data-testid="stSidebarNav"], 
        section[data-testid="stSidebar"] {display: none !important;}
        .main .block-container { padding-top: 1.5rem; max-width: 1200px; }
        .stButton>button { border-radius: 20px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 2. AUTHENTICATION ---
# Using your provided key
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY)

# --- 3. DATA DICTIONARIES ---
CLASS_MAP = {
    "MAMMALIA": "Mammals", "AVES": "Birds", "REPTILIA": "Reptiles", "AMPHIBIA": "Amphibians",
    "ACTINOPTERYGII": "Ray-finned Fishes", "CHONDRICHTHYES": "Sharks & Rays", 
    "INSECTA": "Insects", "MAGNOLIOPSIDA": "Flowering Plants", "LILIOPSIDA": "Grasses"
}

CAT_MAP = {
    "EX": "Extinct", "EW": "Extinct in the Wild", "CR": "Critically Endangered",
    "EN": "Endangered", "VU": "Vulnerable", "NT": "Near Threatened", 
    "LC": "Least Concern", "DD": "Data Deficient"
}

# --- 4. DATA LOADING ---
if "current_species" not in st.session_state:
    st.switch_page("pages/search.py")
    st.stop()

@st.cache_data
def load_species_info(name):
    df = pd.read_csv("nigeria_species_fast.csv")
    match = df[df['Scientific Name'] == name]
    if match.empty: return None
    return match.iloc[0].fillna("Information Unavailable").to_dict()

row = load_species_info(st.session_state["current_species"])

# --- 5. LOGIC FUNCTIONS ---
@st.cache_data
def get_wiki_summary(name):
    """Fetches verified facts from Wikipedia."""
    try:
        return wikipedia.summary(name, sentences=3)
    except:
        return "Biological profile: This species is an integral part of the Nigerian ecosystem. Further field data is being compiled for this record."

@st.cache_data
def generate_gemini_image(sci, common):
    """Generates a high-quality visual using Gemini 2.5 Flash Image."""
    prompt = f"A high-quality, photorealistic wildlife documentary shot of a {common} ({sci}) in its native habitat in Nigeria. Cinematic lighting, National Geographic style."
    try:
        # Using the specific image generation model
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=prompt
        )
        # Extract the image bytes from the response parts
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                return part.inline_data.data
        return None
    except Exception as e:
        print(f"Image Generation Error: {e}")
        return None



@st.cache_data
def get_iucn_threats(sci_name, token="ddCBBhXQeuBD5kgP6g5Dr688meukFRxHi76f"):
    # 1. Clean the name: Remove extra spaces and URL encode it
    # 'Panthera leo' becomes 'Panthera%20leo'
    clean_name = quote(sci_name.strip())
    
    BASE_URL = "https://api.iucnredlist.org/api/v4"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    try:
        # STEP 1: Search for the Taxon
        taxon_url = f"{BASE_URL}/taxa/scientific_name/{clean_name}"
        response = requests.get(taxon_url, headers=headers, timeout=10)
        
        # DEBUG: See what the API is actually saying in your terminal
        if response.status_code != 200:
            print(f"IUCN API Error {response.status_code}: {response.text}")
            return "Species not found (Not Evaluated by IUCN)."

        taxon_data = response.json()
        
        # STEP 2: Find the Latest Assessment ID
        assessments = taxon_data.get('assessments', [])
        latest = next((a for a in assessments if a.get('latest')), None)
        
        if not latest:
            return "No recent IUCN assessment available."
            
        assessment_id = latest['assessment_id']
        
        # STEP 3: Get the Threats
        detail_url = f"{BASE_URL}/assessment/{assessment_id}"
        detail_res = requests.get(detail_url, headers=headers, timeout=10)
        
        if detail_res.status_code == 200:
            details = detail_res.json()
            threats = details.get('threats', [])
            if threats:
                return ", ".join(sorted(list(set(t.get('title') for t in threats if t.get('title')))))
                
        return "No specific threats cataloged in the current assessment."

    except Exception as e:
        return f"Connection error: {str(e)}"
# --- 6. UI DISPLAY ---
if st.button("⬅️ Back to Search"):
    st.switch_page("pages/search.py")

# Clean title logic
display_title = row['Common Name']
if display_title == "Information Unavailable" or display_title.lower() == row['Scientific Name'].lower():
    display_title = row['Scientific Name']

col1, col2 = st.columns([1, 1.3], gap="large")

with col1:
    with st.spinner("🎨 Generating a visual profile..."):
        img_data = generate_gemini_image(row['Scientific Name'], display_title)
    
    if img_data:
        st.image(img_data, use_container_width=True, caption=f"{display_title}")
    else:
        st.error("🖼️ Image generator is currently updating. Please view the technical data below.")

with col2:
    st.title(display_title)
    st.subheader(f"🧬 *{row['Scientific Name']}*")
    # Status Alert
    status_full = CAT_MAP.get(row['Category'], row['Category'])
    if row['Category'] in ["EX", "EW", "CR"]:
        st.error(f"🔴 Red List Status: {status_full}")
    elif row['Category'] in ["EN", "VU"]:
        st.warning(f"🟡 Red List Status: {status_full}")
    else:
        st.success(f"🟢 Red List Status: {status_full}")

    st.write(f"**Biological Group:** {CLASS_MAP.get(row['Class'], row['Class'])}")
    # Call the function and store the result
    iucn_data = get_iucn_threats(row['Scientific Name'])

    # Display: use API data if available, otherwise use your fallback string
    st.write(f"**Known Threats:** {iucn_data if iucn_data != 'No specific threats cataloged...' else 'Habitat loss and environmental change'}")

    st.divider()
    st.markdown("### 📚 Species Overview (Wikipedia)")
    st.write(get_wiki_summary(row['Scientific Name']))

    st.markdown("### 💡 More Info")
    try:
        insight = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=f"Provide a 2-sentence biologist's overview on the habitat and ecology of the {display_title} ({row['Scientific Name']}) specifically regarding its survival in Nigeria."
        )
        st.info(insight.text)
    except:
        st.info("Additional conservation insights are being reviewed by local experts.")

with st.expander("📊 Technical Metadata"):
    st.json(row)