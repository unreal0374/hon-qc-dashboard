import streamlit as st
from PIL import Image, ImageStat
import pandas as pd
import numpy as np
import io
import os

# Define brand-specific criteria and suggestions
brand_criteria = {
    "HON": [
        {"name": "Logo Placement", "description": "Ensure logo is present and correctly placed", "weight": 10, "ai_check": False},
        {"name": "Color Palette", "description": "Use light, airy neutrals with vibrant pops", "weight": 15, "ai_check": True},
        {"name": "Typography", "description": "Fonts should align with HON’s brand tone", "weight": 10, "ai_check": False},
        {"name": "Image Quality", "description": "Bright, natural lighting with soft shadows", "weight": 10, "ai_check": True},
        {"name": "Composition", "description": "Product should be the focal point", "weight": 15, "ai_check": False},
        {"name": "Talent Representation", "description": "Diverse, natural, candid poses", "weight": 10, "ai_check": False},
        {"name": "Propping & Accessories", "description": "Minimal, intentional props", "weight": 10, "ai_check": False},
        {"name": "Architectural Elements", "description": "Realistic flooring, windows, walls", "weight": 10, "ai_check": False},
        {"name": "Vibe/Impression", "description": "Energetic, business casual, approachable", "weight": 10, "ai_check": False}
    ],
    "Allsteel": [
        {"name": "Styling", "description": "Shelves and surfaces should be thoughtfully styled", "weight": 15, "ai_check": False},
        {"name": "Lighting", "description": "Natural, soft, and diffused lighting preferred", "weight": 15, "ai_check": True},
        {"name": "Color Palette", "description": "Use warm modernism tones", "weight": 15, "ai_check": True},
        {"name": "Composition", "description": "Composition should be believable and aspirational", "weight": 15, "ai_check": False},
        {"name": "Propping", "description": "Props should be minimal, organic, and purposeful", "weight": 10, "ai_check": False},
        {"name": "Architecture", "description": "Include realistic, modern architectural elements", "weight": 10, "ai_check": False},
        {"name": "Vibe/Impression", "description": "Should feel warm, inviting, and human-centered", "weight": 10, "ai_check": False},
        {"name": "People", "description": "Diverse, authentic, and not distracting", "weight": 5, "ai_check": False},
        {"name": "Background", "description": "Clean, neutral, and not distracting", "weight": 5, "ai_check": False}
    ],
    "Gunlocke": [
        {"name": "Craftsmanship", "description": "Furniture should reflect attention to detail", "weight": 15, "ai_check": False},
        {"name": "Integrity", "description": "Imagery should feel authentic and trustworthy", "weight": 15, "ai_check": False},
        {"name": "Harmony", "description": "Elements should work together harmoniously", "weight": 15, "ai_check": False},
        {"name": "Material Quality", "description": "Use premium wood, veneer, and sustainable materials", "weight": 15, "ai_check": False},
        {"name": "Lighting & Mood", "description": "Lighting should be warm and sophisticated", "weight": 15, "ai_check": True},
        {"name": "Leadership Aesthetic", "description": "Spaces should reflect modern leadership", "weight": 15, "ai_check": False},
        {"name": "Timeless Design", "description": "Avoid trendy or overly decorative elements", "weight": 10, "ai_check": False}
    ]
}

# Suggestions if score is low
suggestion_map = {
    "Logo Placement": "Ensure the logo is visible, correctly placed, and not obstructed.",
    "Color Palette": "Use lighter neutrals with vibrant pops. Avoid overly dark tones or clashing patterns.",
    "Typography": "Use brand-approved fonts. Avoid decorative or inconsistent typefaces.",
    "Image Quality": "Improve lighting—use natural or soft diffused light. Avoid harsh shadows or low resolution.",
    "Composition": "Make the product the focal point. Use clean spacing and avoid clutter.",
    "Talent Representation": "Use diverse, candid poses. Avoid overly posed or executive-style clothing.",
    "Propping & Accessories": "Use minimal, intentional props. Avoid clutter or irrelevant items.",
    "Architectural Elements": "Include realistic flooring, windows, and wall treatments. Avoid traditional styles.",
    "Vibe/Impression": "Aim for a business casual, approachable feel. Avoid overly formal or sterile environments.",
    "Styling": "Balance styling with intentional props; avoid clutter or emptiness.",
    "Lighting": "Use warm, natural light; avoid harsh shadows or overly dramatic lighting.",
    "Propping": "Remove excess props; use natural materials and textures.",
    "Background": "Simplify background; avoid brick walls and busy window scenes.",
    "Craftsmanship": "Highlight craftsmanship through textures, finishes, and refined details.",
    "Integrity": "Avoid overly staged or artificial scenes; aim for realism.",
    "Harmony": "Rebalance layout and props to create visual harmony.",
    "Material Quality": "Replace or highlight materials that reflect Gunlocke’s standards.",
    "Lighting & Mood": "Use diffused lighting and avoid harsh shadows or sterile tones.",
    "Leadership Aesthetic": "Incorporate open layouts, glass elements, and thoughtful design cues.",
    "Timeless Design": "Simplify design to focus on timeless elegance and function."
}

# AI evaluation function
def ai_score_image(image, criterion):
    stat = ImageStat.Stat(image.convert("RGB"))
    brightness = sum(stat.mean) / len(stat.mean)
    contrast = max(stat.stddev)
    if criterion == "Image Quality" or criterion == "Lighting" or criterion == "Lighting & Mood":
        if brightness > 100 and contrast < 60:
            return 4
        elif brightness > 80:
            return 3
        else:
            return 2
    elif criterion == "Color Palette":
        r, g, b = stat.mean
        if abs(r - g) < 15 and abs(g - b) < 15:
            return 2
        elif max(r, g, b) > 180:
            return 4
        else:
            return 3
    return 3

# Streamlit UI
st.title("Multi-Brand Image QC Dashboard")

brand = st.selectbox("Select Brand", options=list(brand_criteria.keys()))
uploaded_files = st.file_uploader("Upload Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

results = []

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)
        image = Image.open(uploaded_file)
        criteria = brand_criteria[brand]
        total_score = 0
        suggestions = []
        for item in criteria:
            if item["ai_check"]:
                score = ai_score_image(image, item["name"])
            else:
                score = st.slider(
                    label=f"{item['name']} ({item['description']})",
                    min_value=0,
                    max_value=5,
                    value=3,
                    key=f"{uploaded_file.name}_{item['name']}"
                )
            weighted = score * item["weight"]
            total_score += weighted
            if score < 3 and item["name"] in suggestion_map:
                suggestions.append(suggestion_map[item["name"]])
        final_score = round(total_score / sum([c["weight"] for c in criteria]), 2)
        status = "Pass" if final_score >= 80 else "Fail"
        st.markdown(f"**Final Score:** {final_score} — **Status:** {status}")
        if suggestions:
            st.markdown("**Suggestions for Improvement:**")
            for s in suggestions:
                st.write(f"- {s}")
        results.append({
            "Image": uploaded_file.name,
            "Brand": brand,
            "Score": final_score,
            "Status": status,
            "Suggestions": "; ".join(suggestions)
        })

    df = pd.DataFrame(results)
    st.dataframe(df)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download QC Report", data=csv, file_name="qc_report.csv", mime="text/csv")