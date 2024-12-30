import streamlit as st
import chromadb
from routers import admin, shop
from config import PERSIST_DIRECTORY

def main():
    # Initialize database
    collection = init_db()
    
    # Main navigation
    st.sidebar.title("Wedding Dress Shop")
    page = st.sidebar.radio("Navigation", ["Shop", "Admin Panel"])
    
    if page == "Admin Panel":
        admin.admin_panel(collection)
    else:
        shop.shop_page(collection)

def init_db():
    chroma_client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
    collection = chroma_client.get_or_create_collection(
        name="wedding_dresses",
        metadata={"hnsw:space": "cosine"}
    )
    return collection 

if __name__ == "__main__":
    main() 
