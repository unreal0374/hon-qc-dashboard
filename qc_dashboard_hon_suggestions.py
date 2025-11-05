import streamlit as st
from PIL import Image, ImageStat, ImageFilter
import pandas as pd
import numpy as np
import io

# Define brand-specific criteria and suggestions
brand_guidelines = {
    "HON": [
        {"name": "Image Quality", "description": "Bright, natural lighting with soft shadows.", "weight": 10},
        {"name": "Color Palette", "description": "Use light, airy neutrals with vibrant pops.", "weight": 15},
        {"name": "Composition", "description": "Product should be the focal point.", "weight": 15}
    ],
    "Allsteel": [
        {"name": "Image Quality", "description": "Natural, soft, and diffused lighting preferred.", "weight": 10},
        {"name": "Color Palette", "description": "Use warm modernism tones.", "weight": 15},
        {"name": "Composition", "description": "Composition should be believable and aspirational.", "weight": 15}
    ],
    "Gunlocke": [
        {"name": "Image Quality", "description": "Lighting should be warm and sophisticated.", "weight": 10},
        {"name": "Color Palette", "description": "Use premium wood, veneer, and sustainable materials.", "weight": 15},
        {"name": "Composition", "description": "Elements should work together to create a balanced space.", "weight": 15}
    ]
}

# Suggestions based on low scores
suggestions_map = {
    "Image Quality": "Improve lighting and resolution for better clarity.",
    "Color Palette": "Adjust colors to align with brand-approved tones.",
    "Composition": "Reframe image to emphasize product and reduce clutter."
}

# Function to evaluate image using Pillow
def evaluate_image(image):
    image_rgb = image.convert("RGB")
    stat = ImageStat.Stat(image_rgb)
    brightness = sum(stat.mean) / len(stat.mean)
    contrast = max(stat.stddev)
    sharpness = image.filter(ImageFilter.FIND_EDGES).getbbox() is not None
    width, height = image.size
    aspect_ratio = round(width / height, 2)
    resolution = width * height

    # Estimate scores based on metrics
    scores = {}
    # Image Quality: brightness and contrast
    if brightness > 100 and contrast > 30:
        scores["Image Quality"] = 5
    elif brightness > 80:
        scores["Image Quality"] = 4
    elif brightness > 60:
        scores["Image Quality"] = 3
    else:
        scores["Image Quality"] = 2

    # Color Palette: based on RGB balance
    r, g, b = stat.mean
    if abs(r - g) < 15 and abs(g - b) < 15:
        scores["Color Palette"] = 2
    elif max(r, g, b) > 180:
        scores["Color Palette"] = 4
    else:
        scores["Color Palette"] = 3

    # Composition: based on aspect ratio and sharpness
    if 1.3 <= aspect_ratio <= 1.8 and sharpness:
        scores["Composition"] = 5
    elif sharpness:
        scores["Composition"] = 4
    else:
        scores["Composition"] = 3

    return scores, {
        "Brightness": round(brightness, 2),
        "Contrast": round(contrast, 2),
        "Sharpness": "Yes" if sharpness else "No",
        "Resolution": f"{width}x{height}",
        "Aspect Ratio": aspect_ratio
    }

# Streamlit UI
st.title("Multi-Brand Image QC Dashboard with AI Evaluation")

brand = st.selectbox("Select Brand", list(brand_guidelines.keys()))
uploaded_files = st.file_uploader("Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

results = []

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)
        image = Image.open(uploaded_file)
        auto_scores, metrics = evaluate_image(image)

        st.subheader(f"Evaluation for {uploaded_file.name} ({brand})")
        total_score = 0
        suggestions = []

        for item in brand_guidelines[brand]:
            criterion = item["name"]
            weight = item["weight"]
            score = auto_scores.get(criterion, 3)
            weighted_score = score * weight
            total_score += weighted_score

            st.write(f"**{criterion}**: {score}/5")
            st.caption(item["description"])
            if score < 3:
                st.warning(suggestions_map.get(criterion, "Consider improving this aspect."))
                suggestions.append(suggestions_map.get(criterion, "Consider improving this aspect."))

        final_score = round(total_score / sum(i["weight"] for i in brand_guidelines[brand]), 2)
        status = "Pass" if final_score >= 80 else "Fail"
        st.markdown(f"**Final Score:** {final_score}/100 — **Status:** {status}")
        st.markdown(f"**Image Metrics:** {metrics}")

        results.append({
            "Image": uploaded_file.name,
            "Brand": brand,
            "Score": final_score,
            "Status": status,
            "Suggestions": "; ".join(suggestions),
            **metrics
        })

    # Display summary table
    st.subheader("Review Summary")
    df = pd.DataFrame(results)
    st.dataframe(df)

    # Download CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download QC Report", data=csv, file_name="qc_report.csv", mime="text/csv")