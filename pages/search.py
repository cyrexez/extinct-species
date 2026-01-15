import streamlit as st
import pandas as pd

# 1. Page Config & CSS
st.set_page_config(page_title="Nigeria Species Search", layout="wide", initial_sidebar_state="collapsed")

# Hide the sidebar entirely
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stSidebarNav"] {display: none;}
        .main { background-color: #f9f9f9; }
        .stTextInput input { border-radius: 20px; }
    </style>
""", unsafe_allow_html=True)

# 2. Biological & Category Maps
# Consolidated Biological Mapping
CLASS_MAP = {
    # Animals - Vertebrates
    "MAMMALIA": "Mammals",
    "AVES": "Birds",
    "REPTILIA": "Reptiles",
    "AMPHIBIA": "Amphibians",
    "ACTINOPTERYGII": "Ray-finned Fishes",
    "SARCOPTERYGII": "Lobe-finned Fishes (Lungfish)",
    "CHONDRICHTHYES": "Sharks & Rays",

    # Animals - Invertebrates
    "INSECTA": "Insects", 
    "ARACHNIDA": "Arachnids (Spiders & Scorpions)", 
    "MALACOSTRACA": "Crustaceans (Crabs, Shrimp & Lobsters)",
    "GASTROPODA": "Snails & Slugs", 
    "CEPHALOPODA": "Squids & Octopuses", 
    "BIVALVIA": "Clams & Bivalves",
    "ANTHOZOA": "Corals & Anemones",
    "HOLOTHUROIDEA": "Sea Cucumbers",

    # Plants & Fungi
    "MAGNOLIOPSIDA": "Flowering Plants (Dicots)",
    "LILIOPSIDA": "Grasses & Monocots",
    "GNETOPSIDA": "Gnetophytes (includes Afang/Gnetum)",
    "PINOPSIDA": "Conifers (Pines & Firs)",
    "CYCADOPSIDA": "Cycads",
    "POLYPODIOPSIDA": "Ferns",
    "LYCOPODIOPSIDA": "Clubmosses",
    "AGARICOMYCETES": "Mushrooms & Gilled Fungi"
}
CAT_MAP = {
    "EX": "Extinct", "EW": "Extinct in the Wild", "CR": "Critically Endangered",
    "EN": "Endangered", "VU": "Vulnerable", "NT": "Near Threatened", 
    "LC": "Least Concern", "DD": "Data Deficient"
}

@st.cache_data
def load_and_clean_data():
    # Load your new enriched CSV
    df = pd.read_csv("nigeria_species_fast1.csv")
    
    # DEDUPLICATION: Keep only one entry per Scientific Name
    df = df.drop_duplicates(subset=['Scientific Name'], keep='first')
    
    # Mapping for UI display
    df['Friendly Group'] = df['Class'].map(CLASS_MAP).fillna(df['Class'].str.capitalize())
    df['Friendly Status'] = df['Category'].map(CAT_MAP).fillna(df['Category'])
    
    # Sort by status priority (Extinct first)
    status_order = ["EX", "EW", "CR", "EN", "VU", "NT", "LC", "DD"]
    df['Category'] = pd.Categorical(df['Category'], categories=status_order, ordered=True)
    return df.sort_values('Category')

df = load_and_clean_data()

# 3. Search UI (Main Page)
st.title("Species Explorer (Nigeria)")
st.write(f"Search through **{len(df):,}** unique species found in Nigeria.")

# Horizontal Filters
col_q, col_g, col_s = st.columns([2, 1, 1])

with col_q:
    search_query = st.text_input("🔍 Search by name...", placeholder="e.g. 'Elephant', 'Shark', or 'Lotus'")

with col_g:
    group_options = sorted(df['Friendly Group'].unique())
    selected_group = st.multiselect("Group", options=group_options)

with col_s:
    status_options = list(CAT_MAP.values())
    selected_status = st.multiselect("IUCN Status", options=status_options)

# 4. Filtering Logic
filtered = df.copy()

if selected_group:
    filtered = filtered[filtered['Friendly Group'].isin(selected_group)]
if selected_status:
    filtered = filtered[filtered['Friendly Status'].isin(selected_status)]
if search_query:
    filtered = filtered[
        (filtered['Scientific Name'].str.contains(search_query, case=False)) | 
        (filtered['Common Name'].str.contains(search_query, case=False, na=False))
    ]

# 5. Results Grid
st.divider()
st.subheader(f"Found {len(filtered)} results")

# Pagination
items_per_page = 12
page = st.number_input("Page", min_value=1, value=1)
start = (page - 1) * items_per_page
end = start + items_per_page

# Display cards in 3 columns
grid = st.columns(3)
for i, (idx, row) in enumerate(filtered.iloc[start:end].iterrows()):
    with grid[i % 3].container(border=True):
        sci = str(row['Scientific Name'])
        com = str(row['Common Name'])
        
        # Title Logic: Use Common Name if it's not the same as Latin
        has_common = com.lower() != sci.lower() and com != "nan"
        display_title = com if has_common else sci
        
        st.markdown(f"### {display_title}")
        if has_common:
            st.caption(f"🧬 *{sci}*")
            
        st.write(f"**Group:** {row['Friendly Group']}")
        
        # Color coding for status
        if row['Category'] in ["EX", "EW", "CR"]:
            st.error(row['Friendly Status'])
        elif row['Category'] in ["EN", "VU"]:
            st.warning(row['Friendly Status'])
        else:
            st.success(row['Friendly Status'])
            
        if st.button("View Details", key=f"btn_{sci}"):
            st.session_state["current_species"] = sci
            st.switch_page("pages/detail.py")