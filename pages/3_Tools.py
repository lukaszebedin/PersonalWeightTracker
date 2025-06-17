import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")
st.title("⚖️ Fitness Calculators")

tab1, tab2 = st.tabs(["TDEE and Calorie Target Calculator", "Macro Calculator"])

# Form for TDEE and Calorie Target Calculator
with tab1:
    with st.expander("Which BMR/TDEE Calculation Method Should I Use? See explanation and recommendations"):
        st.markdown("""
    **Mifflin-St Jeor** is generally considered the most accurate and modern for estimating BMR in the general population.

    **Harris-Benedict** is older and tends to overestimate BMR.

    **Katch-McArdle** is best if you know your body fat percentage, as it calculates BMR based on lean mass.

    **Recommendation:**
    - Use **Mifflin-St Jeor** as the default for most users.
    - If you know your body fat %, **Katch-McArdle** may be more precise.
    - **Harris-Benedict** can be shown for comparison, but is less commonly used today.
    """)

    gender = st.radio("Gender", ["Male", "Female"])
    age = st.number_input("Age", min_value=10, max_value=100, value=25)
    weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0)
    height = st.number_input("Height (cm)", min_value=120.0, max_value=250.0, value=170.0)
    activity = st.selectbox(
        "Activity Level",
        [
            "Sedentary (little or no exercise)",
            "Lightly active (light exercise/sports 1-3 days/week)",
            "Moderately active (moderate exercise/sports 3-5 days/week)",
            "Very active (hard exercise/sports 6-7 days/week)",
            "Extra active (very hard exercise & physical job)"
        ]
    )

    # Calculate BMR using Mifflin-St Jeor Equation
    if gender == "Male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    # Activity multiplier
    activity_multipliers = {
        "Sedentary (little or no exercise)": 1.2,
        "Lightly active (light exercise/sports 1-3 days/week)": 1.375,
        "Moderately active (moderate exercise/sports 3-5 days/week)": 1.55,
        "Very active (hard exercise/sports 6-7 days/week)": 1.725,
        "Extra active (very hard exercise & physical job)": 1.9,
    }
    # Optional for Katch-McArdle
    body_fat = st.number_input("Body Fat (%) [for Katch-McArdle, optional]", min_value=0.0, max_value=70.0, value=20.0)

    # --- BMR Calculations ---
    def mifflin_st_jeor(weight, height, age, gender):
        if gender == "Male":
            return 10 * weight + 6.25 * height - 5 * age + 5
        else:
            return 10 * weight + 6.25 * height - 5 * age - 161

    def harris_benedict(weight, height, age, gender):
        if gender == "Male":
            return 66.47 + (13.75 * weight) + (5.003 * height) - (6.755 * age)
        else:
            return 655.1 + (9.563 * weight) + (1.850 * height) - (4.676 * age)

    def katch_mcardle(weight, body_fat):
        lean_mass = weight * (1 - body_fat/100)
        return 370 + (21.6 * lean_mass)

    bmr_msj = mifflin_st_jeor(weight, height, age, gender)
    bmr_hb = harris_benedict(weight, height, age, gender)
    bmr_km = katch_mcardle(weight, body_fat) if body_fat > 0 else None

    # --- TDEE Calculations ---
    mult = activity_multipliers[activity]
    tdee_msj = bmr_msj * mult
    tdee_hb = bmr_hb * mult
    tdee_km = bmr_km * mult if bmr_km else None

    # --- Table of Calorie Targets ---
    deficit_surplus = [-1000, -500, -200, 0, 200, 500, 1000]
    rows = []
    for adj in deficit_surplus:
        row = {
            "Deficit/Surplus (kcal)": adj,
            "TDEE (Mifflin-St Jeor)": int(tdee_msj + adj),
            "TDEE (Harris-Benedict)": int(tdee_hb + adj),
            "TDEE (Katch-McArdle)": int(tdee_km + adj) if tdee_km else "N/A"
        }
        rows.append(row)
    df = pd.DataFrame(rows)

    # --- Display ---
    #st.header("Results")
    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("BMR (Mifflin-St Jeor)", f"{int(bmr_msj)} kcal")
    col2.metric("BMR (Harris-Benedict)", f"{int(bmr_hb)} kcal")
    col3.metric("BMR (Katch-McArdle)", f"{int(bmr_km) if bmr_km else 'N/A'} kcal")

    st.info("""
    **BMR (Basal Metabolic Rate):**  
    Calories your body burns at rest.

    **TDEE (Total Daily Energy Expenditure):**  
    Estimated daily calorie need including activity.
    """)

    st.table({
        "Method": ["Mifflin-St Jeor", "Harris-Benedict", "Katch-McArdle"],
        "BMR (kcal)": [int(bmr_msj), int(bmr_hb), int(bmr_km) if bmr_km else "N/A"],
        "TDEE (kcal)": [int(tdee_msj), int(tdee_hb), int(tdee_km) if tdee_km else "N/A"]
    })

    st.divider()
    # --- Weight Loss Table ---
    loss_data = {
        "Goal": ["Mild weight loss (0.25 kg/week)", "Weight loss (0.5 kg/week)"],
        "Mifflin-St Jeor": [int(tdee_msj - 250), int(tdee_msj - 500)],
        "Harris-Benedict": [int(tdee_hb - 250), int(tdee_hb - 500)],
        "Katch-McArdle": [int(tdee_km - 250) if tdee_km else "N/A", int(tdee_km - 500) if tdee_km else "N/A"]
    }
    st.markdown("##### Table of Weight Loss Calorie Targets")
    st.table(pd.DataFrame(loss_data))

    # --- Weight Gain Table ---
    gain_data = {
        "Goal": ["Mild weight gain (0.25 kg/week)", "Weight gain (0.5 kg/week)"],
        "Mifflin-St Jeor": [int(tdee_msj + 250), int(tdee_msj + 500)],
        "Harris-Benedict": [int(tdee_hb + 250), int(tdee_hb + 500)],
        "Katch-McArdle": [int(tdee_km + 250) if tdee_km else "N/A", int(tdee_km + 500) if tdee_km else "N/A"]
    }
    st.markdown("##### Table of Weight Gain Calorie Targets")
    st.table(pd.DataFrame(gain_data))

    st.info(
        "Choose your calorie target based on your goal. "
        "For weight loss, a deficit (e.g., -500 kcal) is typical. "
        "For muscle gain, a surplus (e.g., +200 kcal) is common. "
        "Consult a health professional for personalized advice."
    )
    
with tab2:
    st.write("In development. Coming soon...")