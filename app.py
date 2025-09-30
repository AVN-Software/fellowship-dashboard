# app.py
import streamlit as st
import filters as fx

st.set_page_config(page_title="Fellowship Dashboard", page_icon="📊", layout="wide")

fx.ensure_global_filters()
fx.topbar("📊 Fellowship Dashboard", "Use the global filters, then jump into a section.")

# ALWAYS renders in the sidebar now:
gf = fx.write_global_filters()
if fx.reset_button(target=st.sidebar):
    fx.reset_global_filters()
    st.experimental_rerun()

st.markdown("### 🔗 Sections")
st.page_link("pages/1_Scale.py",                  label="Scale",                  icon="🗺️")
st.page_link("pages/2_Classroom_Observations.py", label="Classroom Observations", icon="📋")
st.page_link("pages/3_Academic_Results.py",       label="Academic Results",       icon="📚")
st.page_link("pages/4_Teacher_Wellbeing.py",      label="Teacher Wellbeing",      icon="🌱")
