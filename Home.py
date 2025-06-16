import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from collections import defaultdict
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

st.title('Personal weight loss tracker')
st.write("""
Welcome!  
Use the sidebar to navigate between data entry and analysis pages.
""")

def show_footer():
    footer = """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #22272B;
        color: #fff;
        text-align: center;
        padding: 10px 0;
        font-size: 15px;
        z-index: 100;
    }
    </style>
    <div class="footer">
        <p>© 2025 Prashant Jeswani Tejwani</p>
    </div>
    """

    st.markdown(footer, unsafe_allow_html=True)

show_footer()