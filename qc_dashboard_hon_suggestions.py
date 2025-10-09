import streamlit as st
import pandas as pd
from PIL import Image
import io

# Define QC criteria based on HON guidelines
qc_criteria = [
    {
        "name": "Logo Placement",
        "description": "Ensure logo is present and correctly placed if applicable.",
        "weight": 10,
        "suggestion": "Ensure the logo is visible, correctly placed, and not obstructed by other elements."
    },
    {
        "name": "Color Palette",
        "description": "Use light, airy neutrals with vibrant pops. Avoid overly muted, dark, or clashing patterns.",
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
        "description": "Bright, natural lighting with soft shadows. Avoid harsh or fluorescent lighting.",
        "weight": 10,
        "suggestion": "Improve lighting—use natural or soft diffused light. Avoid harsh shadows or low resolution."
    },
    {
        "name": "Composition",
        "description": "Product should be the focal point. Use eye-level or overhead angles. Avoid clutter.",
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
        "description": "Include realistic flooring, windows, and wall treatments. Avoid traditional styles.",
        "weight": 10,
        "suggestion": "Include realistic architectural elements. Avoid traditional or uninspiring styles."
    },
    {
        "name": "Vibe/Impression",
        "description": "Energetic, business casual, approachable. Avoid overly formal or unrealistic settings.",
        "weight": 10,
        "suggestion": "Aim for a business casual, approachable feel. Avoid overly formal or sterile environments."
    }
]

st.title("HON Image QC Dashboard")

uploaded_files = st.file_uploader("Upload Images for Review", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    results = []

    for uploaded_file in uploaded_files:
        st.header(f"Review: {uploaded_file.name}")
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
                suggestions.append(f"{item['name']}: {item['suggestion']}")

        final_score = total_score / sum([c["weight"] * 5 for c in qc_criteria]) * 100
        status = "Pass" if final_score >= 80 else "Fail"

        st.markdown(f"**Final Score:** {final_score:.2f} / 100")
        st.markdown(f"**Status:** {status}")

        if suggestions:
            st.markdown("**Suggestions for Improvement:**")
            for s in suggestions:
                st.write(f"- {s}")

        results.append({
            "Image": uploaded_file.name,
            "Score": round(final_score, 2),
            "Status": status,
            "Suggestions": "; ".join(suggestions)
        })

    st.subheader("Review Summary")
    df = pd.DataFrame(results)
    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download QC Report as CSV", data=csv, file_name="qc_report.csv", mime="text/csv")
