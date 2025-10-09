
import streamlit as st
import pandas as pd
from PIL import Image
import base64
import io
from datetime import datetime

# Define QC criteria with weights and suggestions
criteria = [
    {
        "name": "Logo Placement",
        "weight": 10,
        "description": "Ensure logo is visible and correctly placed if applicable.",
        "suggestion": "Ensure the logo is visible, correctly placed, and not obstructed by other elements."
    },
    {
        "name": "Color Palette",
        "weight": 15,
        "description": "Use light, airy neutrals with vibrant pops. Avoid overly dark or clashing patterns.",
        "suggestion": "Use lighter neutrals with vibrant pops. Avoid overly dark tones or clashing patterns."
    },
    {
        "name": "Typography",
        "weight": 10,
        "description": "Fonts should align with HON’s brand tone (if text is present).",
        "suggestion": "Use brand-approved fonts. Avoid decorative or inconsistent typefaces."
    },
    {
        "name": "Image Quality",
        "weight": 10,
        "description": "Bright, natural lighting with soft shadows. Avoid harsh or fluorescent lighting.",
        "suggestion": "Improve lighting—use natural or soft diffused light. Avoid harsh shadows or low resolution."
    },
    {
        "name": "Composition",
        "weight": 15,
        "description": "Product should be the focal point. Use eye-level or overhead angles. Avoid clutter.",
        "suggestion": "Make the product the focal point. Use clean spacing and avoid clutter."
    },
    {
        "name": "Talent Representation",
        "weight": 10,
        "description": "Diverse, natural, candid poses. Avoid overly posed or executive aesthetics.",
        "suggestion": "Use diverse, candid poses. Avoid overly posed or executive-style clothing."
    },
    {
        "name": "Propping & Accessories",
        "weight": 10,
        "description": "Use minimal, intentional props (books, plants, tech). Avoid clutter or irrelevant items.",
        "suggestion": "Use minimal, intentional props. Avoid clutter or irrelevant items."
    },
    {
        "name": "Architectural Elements",
        "weight": 10,
        "description": "Include realistic flooring, windows, and wall treatments. Avoid traditional or uninspiring styles.",
        "suggestion": "Include realistic flooring, windows, and wall treatments. Avoid traditional styles."
    },
    {
        "name": "Vibe/Impression",
        "weight": 10,
        "description": "Energetic, business casual, approachable. Avoid overly formal or unrealistic settings.",
        "suggestion": "Aim for a business casual, approachable feel. Avoid overly formal or sterile environments."
    }
]

# Initialize session state
if "reviews" not in st.session_state:
    st.session_state.reviews = []

st.title("🧪 HON Image QC Dashboard")
st.markdown("Upload images and review them based on HON's 2025 Image Style Guidelines.")

uploaded_files = st.file_uploader("Upload one or more images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.header(f"Review: {uploaded_file.name}")
        image = Image.open(uploaded_file)
        st.image(image, caption=uploaded_file.name, use_column_width=True)

        scores = []
        suggestions = []

        for item in criteria:
            score = st.slider(
                f"{item['name']} ({item['description']})",
                min_value=0,
                max=5,
                value=3,
                key=f"{uploaded_file.name}_{item['name']}"
            )
            scores.append((item["name"], score, item["weight"]))
            if score < 3:
                st.markdown(f"🔧 **Suggestion:** {item['suggestion']}")
                suggestions.append(f"{item['name']}: {item['suggestion']}")

        # Calculate weighted score
        weighted_score = sum(score * weight for _, score, weight in scores) / sum(item["weight"] for item in criteria)
        status = "✅ Pass" if weighted_score >= 4 else "❌ Needs Improvement"

        # Save review
        if st.button(f"Save Review for {uploaded_file.name}"):
            st.session_state.reviews.append({
                "Image": uploaded_file.name,
                "Score": round(weighted_score * 20, 1),
                "Status": status,
                "Suggestions": "; ".join(suggestions)
            })
            st.success(f"Review saved for {uploaded_file.name}")

# Display summary table
if st.session_state.reviews:
    st.subheader("📊 Review Summary")
    df = pd.DataFrame(st.session_state.reviews)
    st.dataframe(df)

    # Download CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV Report", csv, "hon_qc_report.csv", "text/csv")