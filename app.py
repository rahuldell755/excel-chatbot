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
        st.session_state.pending_client = None
        st.session_state.pending_intent = None

    # ---------- HOW MANY / COUNT ----------
    elif "how many" in q or "count" in q:
        temp_df = apply_filters(q, df)
        if temp_df.empty:
            response = "No records found matching your criteria."
        elif "customer" in q:
            count = temp_df["client name"].nunique()
            response = f"There are **{count} unique customer(s)** matching your criteria."
            st.session_state.last_count_result = temp_df[["client name"]].drop_duplicates()
            st.session_state.last_list_type = "customer"
        else:  # client / site
            count = len(temp_df)
            response = f"There are **{count} client site(s)** matching your criteria."
            st.session_state.last_count_result = temp_df
            st.session_state.last_list_type = "client"

    # ---------- CONSULTING CONTACT ----------
    elif "consulting" in q and client:
        rows = df[df["client name"] == client]
        countries = rows["country"].unique()
        if len(countries) > 1 and not country:
            st.session_state.pending_client = client
            st.session_state.pending_intent = "consulting"
            response = f"**{client}** exists in multiple countries: {', '.join(countries)}. Please specify the country."
        else:
            country = country or countries[0]
            response = f"The consulting contact for **{client} ({country})** is **{rows[rows['country']==country]['consulting contact'].iloc[0]}**."

    # ---------- GSUP CONTACT ----------
    elif ("gsup" in q or "support" in q) and client:
        rows = df[df["client name"] == client]
        countries = rows["country"].unique()
        if len(countries) > 1 and not country:
            st.session_state.pending_client = client
            st.session_state.pending_intent = "gsup"
            response = f"**{client}** exists in multiple countries: {', '.join(countries)}. Please specify the country."
        else:
            country = country or countries[0]
            response = f"The GSUP contact for **{client} ({country})** is **{rows[rows['country']==country]['gsup contact'].iloc[0]}**."

    # ---------- STATUS ----------
    elif "status" in q and client:
        rows = df[df["client name"] == client]
        countries = rows["country"].unique()
        if len(countries) > 1 and not country:
            st.session_state.pending_client = client
            st.session_state.pending_intent = "status"
            response = f"**{client}** exists in multiple countries: {', '.join(countries)}. Please specify the country."
        else:
            country = country or countries[0]
            row = rows[rows["country"] == country]
            response = (
                f"**{client} ({country})** current status is "
                f"**{row['current status'].iloc[0]}**, "
                f"implementation status is **{row['impl status'].iloc[0]}**."
            )

    # ---------- FALLBACK ----------
    else:
        temp_df = apply_filters(q, df)
        if not temp_df.empty:
            response = (
                f"I found **{temp_df['client name'].nunique()} unique customer(s)** "
                f"and **{len(temp_df)} client site(s)** matching your criteria."
            )
            st.session_state.last_count_result = temp_df
            st.session_state.last_list_type = "client"

    # ================= OUTPUT =================
    if response:
        st.chat_message("assistant").write(response)

# ---------- SHOW SITES / CUSTOMERS BUTTON ----------
if st.session_state.last_count_result is not None:
    show_df = st.session_state.last_count_result.copy()
    if st.session_state.last_list_type == "client":
        show_df = show_df[["client name","country","regioncode"]]
    elif st.session_state.last_list_type == "customer":
        show_df = show_df[["client name"]].drop_duplicates()

    if st.button(f"Show {st.session_state.last_list_type} list"):
        st.dataframe(show_df)
        st.session_state.last_count_result = None
        st.session_state.last_list_type = None
