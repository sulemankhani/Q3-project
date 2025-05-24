import streamlit as st
import hashlib
import base64
from cryptography.fernet import Fernet, InvalidToken

# Derive encryption key from passkey
def derive_key(passkey: str) -> bytes:
    sha_hash = hashlib.sha256(passkey.encode()).digest()
    return base64.urlsafe_b64encode(sha_hash)

# Encrypt text using Fernet
def encrypt_text(plain_text: str, passkey: str) -> str:
    key = derive_key(passkey)
    f = Fernet(key)
    return f.encrypt(plain_text.encode()).decode()

# Decrypt encrypted text using passkey
def decrypt_text(cipher_text: str, passkey: str) -> str:
    key = derive_key(passkey)
    f = Fernet(key)
    return f.decrypt(cipher_text.encode()).decode()

# Hash passkey for verification
def hash_passkey(passkey: str) -> str:
    return hashlib.sha256(passkey.encode()).hexdigest()

# Initialize session state variables
default_state = {
    'stored_data': {},
    'failed_attempts': 0,
    'logged_in': False
}
for key, value in default_state.items():
    if key not in st.session_state:
        st.session_state[key] = value

def reset_failed_attempts():
    st.session_state.failed_attempts = 0

# ---------------- UI Pages ---------------- #

def home_page():
    st.title("🔐 Secure Data Storage & Retrieval System")
    st.markdown("""
    Welcome! This app lets you:
    - 🔑 **Insert Data**: Securely store any secret data using a passkey.
    - 🔓 **Retrieve Data**: Decrypt your data by entering the correct passkey.
    - 🔁 **Login**: Reauthorize access after multiple failed attempts.
    """)
    st.info(f"📛 Failed decryption attempts: **{st.session_state.failed_attempts}**")
    stored_keys = list(st.session_state.stored_data.keys()) or ['None yet']
    st.success(f"🗂️ Stored data keys: {stored_keys}")

def insert_data_page():
    st.title("📥 Insert Data")
    data_key = st.text_input("🗝️ Data Key (unique identifier):")
    plain_text = st.text_area("📝 Text to Store:")
    passkey = st.text_input("🔐 Passkey", type="password")

    if st.button("Store Data"):
        if not data_key or not plain_text or not passkey:
            st.warning("⚠️ Please fill in all fields.")
        elif data_key in st.session_state.stored_data:
            st.error("❌ Data key already exists.")
        else:
            try:
                encrypted = encrypt_text(plain_text, passkey)
                st.session_state.stored_data[data_key] = {
                    "encrypted_text": encrypted,
                    "passkey": hash_passkey(passkey)
                }
                st.success(f"✅ Data stored successfully under key: `{data_key}`")
            except Exception as e:
                st.error(f"Encryption error: {str(e)}")

def retrieve_data_page():
    st.title("📤 Retrieve Data")

    if st.session_state.failed_attempts >= 3 and not st.session_state.logged_in:
        st.error("❌ Too many failed attempts. Please login first.")
        return

    data_key = st.text_input("🔍 Enter Data Key:")
    passkey = st.text_input("🔐 Enter Passkey:", type="password")

    if st.button("Retrieve"):
        if not data_key or not passkey:
            st.warning("⚠️ Enter both key and passkey.")
        elif data_key not in st.session_state.stored_data:
            st.error("❌ Data key not found.")
        else:
            record = st.session_state.stored_data[data_key]
            if hash_passkey(passkey) == record["passkey"]:
                try:
                    decrypted = decrypt_text(record["encrypted_text"], passkey)
                    st.success("✅ Data retrieved successfully!")
                    st.text_area("📄 Decrypted Text:", decrypted, height=150)
                    reset_failed_attempts()
                except InvalidToken:
                    st.error("❌ Decryption failed. Invalid token.")
                    st.session_state.failed_attempts += 1
            else:
                st.error("❌ Incorrect passkey!")
                st.session_state.failed_attempts += 1

            if st.session_state.failed_attempts >= 3:
                st.warning("⚠️ 3 failed attempts. Please go to the Login page.")

def login_page():
    st.title("🔐 Reauthorize / Login")
    username = st.text_input("👤 Username:")
    password = st.text_input("🔑 Password:", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin":
            st.session_state.logged_in = True
            reset_failed_attempts()
            st.success("✅ Login successful!")
        else:
            st.error("❌ Invalid credentials.")

# ---------------- App Navigation ---------------- #

st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio("", ["Home", "Insert Data", "Retrieve Data", "Login"])

if page == "Home":
    home_page()
elif page == "Insert Data":
    insert_data_page()
elif page == "Retrieve Data":
    retrieve_data_page()
elif page == "Login":
    login_page()
