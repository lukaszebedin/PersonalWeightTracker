import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from collections import defaultdict
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

# st.set_page_config(
#     page_title="Personal weight loss tracker",
#     page_icon="🏋️‍♂️",
#     layout="wide"
# )

st.title('Personal weight loss tracker')
st.markdown("""
Welcome to your personal weight loss tracking app!  
Track your progress, analyze your trends, and stay motivated on your fitness journey.

---

### 🚀 **How to get started**

1. **Go to the sidebar** and open the **Data Editor** page.
2. **Upload** your weight data (CSV) or start entering new entries.
3. **Edit, add, or delete** your weight records as needed.
4. **Download** your updated CSV to save your changes.
5. **Visit the Analysis page** to visualize your progress and weekly trends.
6. Explore the **Tools** page for extra utilities like calorie calculation and macro calculation.
---

### 📊 **Features**

- Easy data entry and editing
- Interactive charts and weekly summaries
- Download your updated data anytime
- Extra tools for calorie tracking
- All data stays private in your browser session
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