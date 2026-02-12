import streamlit as st
import pandas as pd
import joblib
import os
import datetime


st.set_page_config(page_title="Telecom X Churn Predictor")

st.title("📊 Telecom X Churn Prediction")

#st.write("Ingrese la información del cliente:")

st.info("Complete la información del cliente para estimar el riesgo de cancelación.")
# Inputs principales


#En lugar que sea 0 y 1 cambiamos a meses
#0  → cliente muy nuevo | 1  → cliente muy antiguo

tenure = st.slider(" Antigüedad (Tenure) [0  → cliente muy nuevo | 1  → cliente muy antiguo]", 0.0, 1.0) 

#tenure_months = st.slider("Antigüedad del cliente (meses) / (Tenure: 0-1) ", 0, 72)
#tenure = tenure_months / 72

#Mostrar dólares reales para cargo mensual
#0 → cargo bajo | 1 → cargo alto

charges = st.slider(" Cargo Mensual [0 → cargo bajo | 1 → cargo alto] ", 0.0, 1.0)

#monthly_charge = st.slider("Cargo mensual ($) / (Tenure: 0-1) ", 20, 120)
#charges = (monthly_charge - 20) / (120 - 20)



fiber = st.selectbox("¿Tiene Fibra Óptica?", ["No", "Sí"])
contract = st.selectbox("Tipo de Contrato", ["Month-to-month", "One year", "Two year"])
tech_support = st.selectbox("¿Tiene Soporte Técnico?", ["No", "Sí"])

st.caption("Los valores se transforman automáticamente al formato usado por el modelo.")

# Convertir a formato modelo
#------------------------------------------
#data = {
#    "tenure": tenure,
#    "Charges.Monthly": charges,
#    "InternetService_Fiber optic": 1 if fiber == "Sí" else 0,
#    "Contract_One year": 1 if contract == "One year" else 0,
#    "Contract_Two year": 1 if contract == "Two year" else 0,
#    "TechSupport_Yes": 1 if tech_support == "Sí" else 0
#}

#input_df = pd.DataFrame([data])
#-------------------------------

FEATURES = [
    'SeniorCitizen',
    'tenure',
    'Charges.Monthly',
    'Charges.Total',
    'gender_Male',
    'Partner_Yes',
    'Dependents_Yes',
    'PhoneService_Yes',
    'MultipleLines_No phone service',
    'MultipleLines_Yes',
    'InternetService_Fiber optic',
    'InternetService_No',
    'OnlineSecurity_No internet service',
    'OnlineSecurity_Yes',
    'OnlineBackup_No internet service',
    'OnlineBackup_Yes',
    'DeviceProtection_No internet service',
    'DeviceProtection_Yes',
    'TechSupport_No internet service',
    'TechSupport_Yes',
    'StreamingTV_No internet service',
    'StreamingTV_Yes',
    'StreamingMovies_No internet service',
    'StreamingMovies_Yes',
    'Contract_One year',
    'Contract_Two year',
    'PaperlessBilling_Yes',
    'PaymentMethod_Credit card (automatic)',
    'PaymentMethod_Electronic check',
    'PaymentMethod_Mailed check'
]



input_df = pd.DataFrame(0, index=[0], columns=FEATURES)

input_df["tenure"] = tenure
input_df["Charges.Monthly"] = charges
input_df["InternetService_Fiber optic"] = 1 if fiber == "Sí" else 0
input_df["Contract_One year"] = 1 if contract == "One year" else 0
input_df["Contract_Two year"] = 1 if contract == "Two year" else 0
input_df["TechSupport_Yes"] = 1 if tech_support == "Sí" else 0


# Obtiene la ruta de la carpeta donde está este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "modelo_churn.pkl")

#st.write(f"Buscando el modelo en: {model_path}")

model = joblib.load(model_path)

if st.button("Predecir"):
    #prediction = model.predict(input_df)[0]
    proba = model.predict_proba(input_df)[0][1]
    prediction = 1 if proba >= 0.5 else 0

    st.metric("Probabilidad de Cancelación", f"{proba*100:.2f}%")
    st.progress(float(proba))


    if prediction == 1:
        st.error("⚠️  Cliente en Riesgo de Cancelación")
    else:
        st.success("✅ Cliente Probablemente Permanecerá")
   
   
   # result = "Churn" if prediction == 1 else "No Churn"
    result = "Cliente en Riesgo de Cancelación" if prediction == 1 else "Cliente Probablemente Permanecerá"

    log = {
        "fecha": datetime.datetime.now(),
        "tenure": tenure,
        #"tenure_meses": tenure_months,
        "cargo_mensual": charges,
        #"cargo_mensual": monthly_charge,
        "fibra": fiber,
        "contrato": contract,
        "soporte": tech_support,
        "resultado": result
    }

    log_df = pd.DataFrame([log])

    if os.path.exists("predicciones.csv"):
        log_df.to_csv("predicciones.csv", mode="a", header=False, index=False)
    else:
        log_df.to_csv("predicciones.csv", index=False)


if os.path.exists("predicciones.csv"):
    st.subheader("Histórico de Predicciones")
    st.dataframe(pd.read_csv("predicciones.csv"))


#Barras: Cancelación vs Permanencia
if os.path.exists("predicciones.csv"):
    hist = pd.read_csv("predicciones.csv")

    st.subheader("Distribución de Predicciones")
    st.bar_chart(hist["resultado"].value_counts())



#Histograma de cargos
st.subheader("Distribución de Cargos Mensuales")

# por temas de visualización se cambio por rangos.
#st.bar_chart(hist["cargo_mensual"].value_counts(bins=10))

bins = [0, 20, 40, 60, 80, 100, 150]
labels = ["0-20", "21-40", "41-60", "61-80", "81-100", "100+"]
hist["rango_cargo"] = pd.cut(hist["cargo_mensual"], bins=bins, labels=labels)
st.bar_chart(hist["rango_cargo"].value_counts())


# KPIs
col1, col2, col3 = st.columns(3)

total_preds = len(hist)
churn_preds = (hist["resultado"] == "Cliente en Riesgo de Cancelación").sum()
stay_preds = (hist["resultado"] == "Cliente Probablemente Permanecerá").sum()

col1.metric("Total Predicciones", total_preds)
col2.metric("Clientes en Riesgo", churn_preds)
col3.metric("Clientes Estables", stay_preds)



#####
importance_df = pd.read_csv("../data/feature_importance.csv")

st.subheader("Factores que más influyen en el modelo")
st.dataframe(importance_df.head(10))

st.bar_chart(importance_df.head(10).set_index("feature"))

if st.button("🗑️ Limpiar historial"):
    hist = hist.iloc[0:0]
    hist.to_csv("predicciones.csv", index=False)
    st.success("Historial limpiado")
    st.rerun()


if st.button("Eliminar último registro"):
    if len(hist) > 0:
        hist = hist.iloc[:-1]
        hist.to_csv("predicciones.csv", index=False)
        st.success("Último registro eliminado")
        st.rerun()


#Botón Descargar Histórico
st.download_button(
    "⬇ Descargar historial (CSV)",
    data=hist.to_csv(index=False),
    file_name="predicciones.csv",
    mime="text/csv"
)

