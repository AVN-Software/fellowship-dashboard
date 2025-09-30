import streamlit as st
from typing import List


def render_tab_bar(tab_labels: List[str]):
    """
    Create a reusable tab bar with given labels.
    Returns unpacked tab objects in the same order.
    """
    return st.tabs(tab_labels)
