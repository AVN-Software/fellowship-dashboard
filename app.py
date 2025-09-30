import streamlit as st

# Page config
st.set_page_config(
    page_title="Fellowship Dashboard",
    page_icon="📊",
    layout="wide"
)

# Main landing page
st.title("📊 Fellowship Dashboard")
st.markdown("""
Welcome to the **Fellowship Dashboard** 👋  

This dashboard has three main sections:

1. **Classroom Observations** – Track teaching practices and observation data  
2. **Academic Results** – Review learner academic performance across terms  
3. **Teacher Wellbeing** – Monitor wellbeing and support needs of fellows  

👉 Use the sidebar on the left to navigate between pages.
""")

# Optional: show quick stats or links
st.info("Select a page from the sidebar to begin.")
