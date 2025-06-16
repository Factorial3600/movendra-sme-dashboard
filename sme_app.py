import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="South-West SME Dashboard",
    page_icon="📦",
    layout="wide"
)

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
    }
    .main {
        background-color: #f9fbfc;
        padding: 2rem;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .kpi-box {
        background-color: #e8f1fa;
        padding: 1rem 2rem;
        border-left: 6px solid #0066cc;
        border-radius: 8px;
        font-size: 17px;
        color: #003366;
        margin-bottom: 1rem;
    }
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_csv("southwest_smes.csv")
    df = df.dropna(subset=["lat", "lng"])
    return df

df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("📍 SME Filters")

states_with_data = df['state'].dropna().unique()
selected_states = st.sidebar.multiselect("Select State(s)", sorted(states_with_data), default=sorted(states_with_data))

industries = df['industry'].dropna().unique()
selected_industries = st.sidebar.multiselect("Select Industry (Optional)", sorted(industries), default=sorted(industries))

# --- FILTER LOGIC ---
filtered_df = df[df['state'].isin(selected_states) & df['industry'].isin(selected_industries)]

# --- KPI DISPLAY ---
col1, col2 = st.columns(2)
col1.markdown(f"<div class='kpi-box'>📌 <strong>Total SMEs:</strong> {len(filtered_df):,}</div>", unsafe_allow_html=True)
col2.markdown(f"<div class='kpi-box'>📍 <strong>States Selected:</strong> {len(selected_states)}</div>", unsafe_allow_html=True)

# --- MAP ---
st.subheader("🗺️ SME Locations")
if len(filtered_df) > 0:
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=filtered_df['lat'].mean(),
            longitude=filtered_df['lng'].mean(),
            zoom=6.2,
            pitch=30,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=filtered_df,
                get_position='[lng, lat]',
                get_color='[30, 144, 255, 180]',
                get_radius=300,
                radius_scale=1,
                pickable=True,
                auto_highlight=True
            )
        ],
        tooltip={"text": "{name}\n{city}, {state}"}
    ))
else:
    st.warning("⚠️ No SMEs to display. Adjust your filters.")

# --- BAR CHART ---
if len(filtered_df) > 0:
    st.subheader("🏙️ Top 10 Cities by SME Count")
    city_counts = filtered_df['city'].value_counts().head(10).sort_values()
    st.bar_chart(city_counts)

# --- PIE CHART ---
    st.subheader("📊 SME Share: Top 6 States")
    top_states = filtered_df['state'].value_counts().head(6)
    others_count = filtered_df['state'].value_counts().iloc[6:].sum()
    labels = list(top_states.index) + ['Others']
    sizes = list(top_states.values) + [others_count]

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')
    st.pyplot(fig)

# --- INSIGHTS ---
    st.subheader("🧠 Key Insights")
    st.markdown(f"""
    - **Total SMEs Displayed:** `{len(filtered_df):,}`
    - **Top State:** `{top_states.idxmax().title()}` with `{top_states.max():,}` SMEs
    - **States Filtered:** {', '.join(selected_states)}
    - **Industries Filtered:** {', '.join(selected_industries) if selected_industries else "All"}
    """)
else:
    st.info("⚠️ No SMEs match your filters.")

# --- DOWNLOAD BUTTON ---
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=filtered_df.to_csv(index=False),
    file_name='filtered_smes.csv',
    mime='text/csv'
)

# --- FOOTER ---
st.markdown("---")
st.markdown(
    "<center style='color: gray;'>🚀 Built for Bootcamp Final Project | Movendra Logistics • Powered by Streamlit</center>",
    unsafe_allow_html=True
)
n