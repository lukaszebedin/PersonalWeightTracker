import streamlit as st

def show_total_weight_loss(total_loss):
    if total_loss > 0:
        st.success(f"**Total weight lost:** `{total_loss:.1f} kg`")
    elif total_loss < 0:
        st.warning(f"**Total weight gained:** `{abs(total_loss):.1f} kg`")
    else:
        st.info("No net weight change.")