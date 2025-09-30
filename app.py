# app.py
import streamlit as st
import components.filters as fx

st.set_page_config(page_title="Fellowship Dashboard", page_icon="📊", layout="wide")

fx.ensure_global_filters()
fx.topbar("📊 Fellowship Dashboard", "Use the global filters, then jump into a section.")

# ALWAYS renders in the sidebar now:
gf = fx.write_global_filters()
if fx.reset_button(target=st.sidebar):
    fx.reset_global_filters()
    st.experimental_rerun()

