import streamlit as st
import pandas as pd

# ---------------- LOAD DATA ----------------
df = pd.read_excel("install_base.xlsx")
df = df.fillna("").astype(str)
df.columns = df.columns.str.strip().str.lower()

st.set_page_config(page_title="Install Base Chatbot", layout="wide")
st.title("📊 Install Base Chatbot")

# ---------------- SESSION STATE ----------------
if "pending_client" not in st.session_state:
    st.session_state.pending_client = None

# ---------------- CHAT INPUT ----------------
query = st.chat_input(
    "Ask: Consulting contact for ABC Bank, How many customers in EMEA?"
)

# ---------------- HELPERS ----------------
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

# ---------------- CHAT LOGIC ----------------
if query:
    st.chat_message("user").write(query)
    q = query.lower()

    response = ""
    result_df = pd.DataFrame()

    client = find_client(q)
    country = find_country(q)

    # ---------- FOLLOW-UP COUNTRY HANDLING ----------
    if st.session_state.pending_client and country:
        client = st.session_state.pending_client
        row = df[
            (df["client name"] == client) &
            (df["country"].str.lower() == country.lower())
        ]

        if not row.empty:
            contact = row["consulting contact"].iloc[0]
            response = (
                f"The consulting contact for **{client} ({country})** "
                f"is **{contact}**."
            )

        st.session_state.pending_client = None

    # ---------- HOW MANY (UNIQUE CLIENTS) ----------
    elif "how many" in q or "count" in q:
        temp_df = df.copy()

        if "emea" in q:
            temp_df = temp_df[temp_df["regioncode"].str.contains("emea", case=False)]
        if "africa" in q:
            temp_df = temp_df[temp_df["regioncode"].str.contains("africa", case=False)]
        if "europe" in q:
            temp_df = temp_df[temp_df["regioncode"].str.contains("europe", case=False)]
        if "flexcube" in q:
            temp_df = temp_df[temp_df["products used"].str.contains("flexcube", case=False)]

        unique_clients = temp_df["client name"].nunique()
        response = f"There are **{unique_clients} unique customer(s)** matching your criteria."

    # ---------- CONSULTING CONTACT ----------
    elif "consulting" in q and client:
        rows = df[df["client name"] == client]
        countries = rows["country"].unique()

        if len(countries) > 1 and not country:
            st.session_state.pending_client = client
            response = (
                f"**{client}** exists in multiple countries: "
                f"{', '.join(countries)}. "
                f"Please specify the country."
            )
        else:
            if not country:
                country = countries[0]
            row = rows[rows["country"] == country]
            contact = row["consulting contact"].iloc[0]
            response = (
                f"The consulting contact for **{client} ({country})** "
                f"is **{contact}**."
            )

    # ---------- GSUP CONTACT ----------
    elif "gsup" in q and client:
        rows = df[df["client name"] == client]
        countries = rows["country"].unique()

        if len(countries) > 1 and not country:
            st.session_state.pending_client = client
            response = (
                f"**{client}** exists in multiple countries: "
                f"{', '.join(countries)}. "
                f"Please specify the country."
            )
        else:
            if not country:
                country = countries[0]
            row = rows[rows["country"] == country]
            contact = row["gsup contact"].iloc[0]
            response = (
                f"The GSUP contact for **{client} ({country})** "
                f"is **{contact}**."
            )

    # ---------- FALLBACK ----------
    else:
        temp_df = df[df.apply(lambda r: q in " ".join(r).lower(), axis=1)]
        if not temp_df.empty:
            response = f"I found **{temp_df['client name'].nunique()} unique customer(s)**."
            result_df = temp_df

    # ---------------- OUTPUT ----------------
    if response:
        st.chat_message("assistant").write(response)

    if not result_df.empty:
        st.dataframe(result_df)

    if not response:
        st.chat_message("assistant").write(
            "I couldn’t find an exact match. Try client name, country, region, or product."
        )
