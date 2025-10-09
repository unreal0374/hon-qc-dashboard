
import streamlit as st
import pandas as pd
from PIL import Image
import io

# Define QC criteria based on HON guidelines
qc_criteria = [
    {
        "name": "Logo Placement",
        "description": "Ensure the logo is present and correctly placed if applicable.",
        "weight": 10,
        "suggestion": "Ensure the logo is visible, correctly placed, and not obstructed by other elements."
    },
    {
        "name": "Color Palette",
        "description": "Use light, airy neutrals with vibrant pops. Avoid dark or clashing patterns.",
        "weight": 15,
        "suggestion": "Use lighter neutrals with vibrant pops. Avoid overly dark tones or clashing patterns."
    },
    {
        "name": "Typography",
        "description": "Fonts should align with HON’s brand tone (if text is present).",
        "weight": 10,
        "suggestion": "Use brand-approved fonts. Avoid decorative or inconsistent typefaces."
    },
    {
        "name": "Image Quality",
        "description": "Bright, natural lighting with soft shadows. Avoid harsh lighting.",
        "weight": 10,
        "suggestion": "Improve lighting—use natural or soft diffused light. Avoid harsh shadows or low resolution."
    },
    {
        "name": "Composition",
        "description": "Product should be the focal point. Use eye-level or overhead angles.",
        "weight": 15,
        "suggestion": "Make the product the focal point. Use clean spacing and avoid clutter."
    },
    {
        "name": "Talent Representation",
        "description": "Diverse, natural, candid poses. Avoid overly posed or executive aesthetics.",
        "weight": 10,
        "suggestion": "Use diverse, candid poses. Avoid overly posed or executive-style clothing."
    },
    {
        "name": "Propping & Accessories",
        "description": "Use minimal, intentional props. Avoid clutter or irrelevant items.",
        "weight": 10,
        "suggestion": "Use minimal, intentional props. Avoid clutter or irrelevant items."
    },
    {
        "name": "Architectural Elements",
        "description": "Include realistic flooring, windows, and wall treatments.",
        "weight": 10,
        "suggestion": "Include realistic flooring, windows, and wall treatments. Avoid traditional styles."
    },
    {
        "name": "Vibe/Impression",
        "description": "Energetic, business casual, approachable. Avoid overly formal settings.",
        "weight": 10,
        "suggestion": "Aim for a business casual, approachable feel. Avoid overly formal or sterile environments."
    }
]

# Initialize session state for storing results
if "results" not in st.session_state:
    st.session_state.results = []

st.title("HON Image QC Dashboard (with Suggestions)")

uploaded_files = st.file_uploader("Upload images for review", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.header(f"Reviewing: {uploaded_file.name}")
        image = Image.open(uploaded_file)
        st.image(image, caption=uploaded_file.name, use_column_width=True)

        total_score = 0
        suggestions = []

        for item in qc_criteria:
            score = st.slider(
                label=f"{item['name']} ({item['description']})",
                min_value=0,
                max_value=5,
                value=3,
                key=f"{uploaded_file.name}_{item['name']}"
            )
            weighted_score = score * item["weight"]
            total_score += weighted_score

            if score < 3:
                suggestions.append(f"- {item['name']}: {item['suggestion']}")

        final_score = round(total_score / 100, 2)
        status = "Pass" if final_score >= 0.8 else "Fail"

        st.markdown(f"**Final Score:** {final_score * 100}/100")
        st.markdown(f"**Status:** {status}")

        if suggestions:
            st.markdown("### Suggestions for Improvement:")
            for s in suggestions:
                st.markdown(s)

        # Save results
        st.session_state.results.append({
            "Image": uploaded_file.name,
            "Score": final_score * 100,
            "Status": status,
            "Suggestions": "\n".join(suggestions)
        })

    # Display summary table
    if st.session_state.results:
        st.subheader("Review Summary")
        df = pd.DataFrame(st.session_state.results)
        st.dataframe(df)

        # Download CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download QC Report as CSV", data=csv, file_name="qc_report.csv", mime="text/csv")
