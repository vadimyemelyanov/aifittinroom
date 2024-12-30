import streamlit as st
from PIL import Image
import io
import datetime
import base64
import os
from services import ai_service, s3_service, auth_service

def admin_panel(collection):
    if not auth_service.check_password():
        st.stop()
        
    st.title("Admin Panel - Wedding Dress Management")
    
    admin_tab1, admin_tab2 = st.tabs(["Add New Dress", "Manage Inventory"])
    
    with admin_tab1:
        handle_new_dress(collection)
    
    with admin_tab2:
        handle_inventory(collection)

def handle_new_dress(collection):
    st.header("Add New Wedding Dress")
    uploaded_file = st.file_uploader("Upload Dress Image", type=['png', 'jpg', 'jpeg'])
    col1, col2 = st.columns(2)
    
    with col1:
        country = st.text_input("Country of Origin")
        brand = st.text_input("Brand Name")
        
    with col2:
        price = st.number_input("Price ($)", min_value=0.0, step=0.01)
        name = st.text_input("Dress Name/Model")
        
    if uploaded_file:
        # Display preview
        image = Image.open(uploaded_file)
        st.image(image, caption="Preview", use_column_width=True, width=300)
        
        # Convert image for AI analysis
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        if st.button("Analyze and Save"):
            with st.spinner('Analyzing dress...'):
                # AI Analysis
                analysis_text = ai_service.analyze_dress_image(img_str)
                # Get embeddings
                embeddings = ai_service.get_embeddings(analysis_text)
                
                # Save to S3
                temp_path = f"temp_{uploaded_file.name}"
                image.save(temp_path)
                s3_path = f"wedding_dresses/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
                public_url = s3_service.upload_file(temp_path, s3_path)
                os.remove(temp_path)
                
                # Save to database
                doc_id = str(datetime.datetime.now().timestamp())
                metadata = {
                    "filename": uploaded_file.name,
                    "upload_date": datetime.datetime.now().isoformat(),
                    "country": country,
                    "brand": brand,
                    "price": float(price),
                    "name": name,
                    "public_url": public_url
                }
                
                collection.add(
                    documents=[analysis_text],
                    embeddings=[embeddings],
                    metadatas=[metadata],
                    ids=[doc_id]
                )
                
                st.success("Dress added successfully!")

def handle_inventory(collection):
    st.header("Manage Inventory")
    if st.button("View All Dresses"):
        results = collection.get()
        if results['ids']:
            for i, dress_id in enumerate(results['ids']):
                with st.expander(f"Dress {i+1}: {results['metadatas'][i].get('name', 'Unnamed')}"):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        if 'public_url' in results['metadatas'][i]:
                            st.image(results['metadatas'][i]['public_url'], width=200)
                    with col2:
                        st.json(results['metadatas'][i])
                        if st.button(f"Delete Dress {i+1}"):
                            collection.delete(ids=[dress_id])
                            st.success("Dress deleted successfully!")
                            st.rerun()
        else:
            st.info("No dresses in inventory") 