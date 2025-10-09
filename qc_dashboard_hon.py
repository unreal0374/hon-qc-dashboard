
import streamlit as st
import pandas as pd
from PIL import Image
import io

# Set page configuration
st.set_page_config(page_title="HON Image QC Dashboard", layout="wide")

# Title
st.title("📋 HON Brand Image QC Dashboard")

# Description
st.markdown("""
This dashboard allows you to review images based on HON's 2025 brand guidelines.  
Upload images, score them against each criterion, and export the QC results.
""")

# Define QC criteria based on HON guidelines
criteria = [
    {
        "name": "Logo Placement",
        "description": "Ensure logo is present and correctly placed if applicable.",
        "weight": 10
    },
    {
        "name": "Color Palette",
        "description": "Use light, airy neutrals with vibrant pops. Avoid overly muted, dark, or clashing patterns.",
        "weight": 15
    },
    {
        "name": "Typography",
        "description": "Fonts should align with HON’s brand tone (if text is present).",
        "weight": 10
    },
    {
        "name": "Image Quality",
        "description": "Bright, natural lighting with soft shadows. Avoid harsh or fluorescent lighting.",
        "weight": 10
    },
    {
        "name": "Composition",
        "description": "Product should be the focal point. Use eye-level or overhead angles. Avoid clutter.",
        "weight": 15
    },
    {
        "name": "Talent Representation",
        "description": "Diverse, natural, candid poses. Avoid overly posed or executive aesthetics.",
        "weight": 10
    },
    {
        "name": "Propping & Accessories",
        "description": "Use minimal, intentional props. Avoid clutter or irrelevant items.",
        "weight": 10
    },
    {
        "name": "Architectural Elements",
        "description": "Include realistic flooring, windows, and wall treatments. Avoid traditional or uninspiring styles.",
        "weight": 10
    },
    {
        "name": "Vibe/Impression",
        "description": "Energetic, business casual, approachable. Avoid overly formal or unrealistic settings.",
        "weight": 10
    }
]

# Initialize session state for storing results
if "results" not in st.session_state:
    st.session_state.results = []

# Image uploader
uploaded_files = st.file_uploader("📤 Upload Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

# Review each image
if uploaded_files:
    for uploaded_file in uploaded_files:
        st.header(f"🖼️ Review: {uploaded_file.name}")
        image = Image.open(uploaded_file)
        st.image(image, use_column_width=True)

        scores = {}
        total_score = 0

        # Scoring sliders
        for criterion in criteria:
            score = st.slider(
                label=f"{criterion['name']} (Weight: {criterion['weight']}%)",
                min_value=0,
                max_value=5,
                value=3,
                help=criterion["description"],
                key=f"{uploaded_file.name}_{criterion['name']}"
            )
            scores[criterion["name"]] = score
            total_score += score * criterion["weight"]

        # Normalize score to 100
        max_possible_score = sum([c["weight"] * 5 for c in criteria])
        final_score = round((total_score / max_possible_score) * 100, 2)
        status = "✅ Pass" if final_score >= 80 else "❌ Fail"

        st.markdown(f"**Final Score:** {final_score} / 100 — {status}")

        # Save results
        if st.button(f"Save Review for {uploaded_file.name}"):
            result = {
                "Image Name": uploaded_file.name,
                "Final Score": final_score,
                "Status": status
            }
            for criterion in criteria:
                result[criterion["name"]] = scores[criterion["name"]]
            st.session_state.results.append(result)
            st.success(f"Review saved for {uploaded_file.name}")

# Display summary table
if st.session_state.results:
    st.subheader("📊 QC Summary Table")
    df = pd.DataFrame(st.session_state.results)
    st.dataframe(df, use_container_width=True)

    # Download CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download QC Report as CSV",
        data=csv,
        file_name="hon_qc_report.csv",
        mime="text/csv"
    )
