import streamlit as st
import pandas as pd

# ================= LOAD DATA =================
df = pd.read_excel("install_base.xlsx")
df = df.fillna("").astype(str)
df.columns = df.columns.str.strip().str.lower()

st.set_page_config(page_title="Install Base Chatbot", layout="wide")
st.title("📊 Install Base Chatbot")

# ================= SESSION STATE =================
if "pending_client" not in st.session_state:
    st.session_state.pending_client = None
if "pending_intent" not in st.session_state:
    st.session_state.pending_intent = None
if "last_count_result" not in st.session_state:
    st.session_state.last_count_result = None
if "last_list_type" not in st.session_state:
    st.session_state.last_list_type = None  # "customer" or "client"

# ================= HELPERS =================
def find_client(text):
    for c in df["client name"].unique():
        if c.lower() in text:
            return c
    return None

def find_country(text):
    for c in df["country"].unique():
        if c.lower() in text:
            return c
    return None

def apply_filters(text, base_df):
    temp = base_df.copy()
    # REGION
    for region in ["emea","africa","europe","apac"]:
        if region in text:
            temp = temp[temp["regioncode"].str.contains(region, case=False)]
    # COUNTRY
    for c in temp["country"].unique():
        if c.lower() in text:
            temp = temp[temp["country"].str.lower() == c.lower()]
            break
    # PRODUCT
    if "flexcube" in text:
        temp = temp[temp["products used"].str.contains("flexcube", case=False)]
    # DEPLOYMENT
    if "oci" in text:
        temp = temp[temp["deployment type"].str.contains("oci", case=False)]
    if "aws" in text:
        temp = temp[temp["deployment type"].str.contains("aws", case=False)]
    return temp

# ================= CHAT INPUT =================
query = st.chat_input("Ask anything about clients/customers:")

# ================= CHAT LOGIC =================
if query:
    st.chat_message("user").write(query)
    q = query.lower().strip()
    response = ""
    result_df = pd.DataFrame()

    client = find_client(q)
    country = find_country(q)

    # ---------- VALIDATION ----------
    valid_clients = [c.lower() for c in df["client name"].unique()]
    valid_countries = [c.lower() for c in df["country"].unique()]
    valid_keywords = ["customer","client","product","products","deployment",
                      "consulting","gsup","support","status","how many","count","region"]

    if not any(word in q for word in valid_clients + valid_countries + valid_keywords):
        response = "Invalid ask, please make a correct query."

    else:
        # ---------- FOLLOW-UP COUNTRY (for client contacts) ----------
        if st.session_state.pending_client and country:
            client = st.session_state.pending_client
            intent = st.session_state.pending_intent
            row = df[
                (df["client name"] == client) &
                (df["country"].str.lower() == country.lower())
            ]
            if not row.empty:
                if intent == "consulting":
                    response = f"The consulting contact for **{client} ({country})** is **{row['consulting contact'].iloc[0]}**."
                elif intent == "gsup":
                    response = f"The GSUP contact for **{client} ({country})** is **{row['gsup contact'].iloc[0]}**."
                elif intent == "status":
                    response = (
                        f"**{client} ({country})** current status is "
                        f"**{row['current status'].iloc[0]}**, "
                        f"implementation status is **{row['impl status'].iloc[0]}**."
                    )
                elif intent == "product":
                    products = row["products used"].unique()
                    response = f"**{client} ({country})** is using the following products: {', '.join(products)}."
                elif intent == "deployment":
                    deployments = row["deployment type"].unique()
                    response = f"**{client} ({country})** deployment types: {', '.join(deployments)}."
            st.session_state.pending_client = None
            st.session_state.pending_intent = None

        # ---------- ATTRIBUTE / PRODUCT LOOKUP ----------
        elif client and any(k in q for k in ["product","products","deployment","consulting","gsup","support","status"]):
            rows = df[df["client name"] == client]
            if c
