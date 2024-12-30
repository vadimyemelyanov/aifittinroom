import streamlit as st
from openai import OpenAI
from PIL import Image
import io
import datetime
import json
import boto3
from dotenv import load_dotenv
import os
import chromadb
from chromadb.config import Settings
import base64

# Load environment variables
load_dotenv(".env")

# Vector DB setup
PERSIST_DIRECTORY = "db"
chroma_client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
collection = chroma_client.get_or_create_collection(
    name="wedding_dresses",
    metadata={"hnsw:space": "cosine"}
)

# S3 setup
s3_client = boto3.client('s3', 
                         region_name='eu-central-1',
                           aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                             aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"), config=boto3.session.Config(signature_version='s3v4'))
S3_BUCKET = os.getenv("S3_BUCKET_NAME")

client = OpenAI()

# Authentication
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        
    if not st.session_state.authenticated:
        with st.form("login"):
            st.title("Admin Login (admin/admin)")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit and username == "admin" and password == "admin":  # Replace with secure authentication
                st.session_state.authenticated = True
                st.rerun()
        return False
    return True

# Main navigation
st.sidebar.title("Wedding Dress Shop")
page = st.sidebar.radio("Navigation", ["Shop", "Admin Panel"])

if page == "Admin Panel":
    if not check_password():
        st.stop()
        
    st.title("Admin Panel - Wedding Dress Management")
    
    # Add tabs for different admin functions
    admin_tab1, admin_tab2 = st.tabs(["Add New Dress", "Manage Inventory"])
    
    with admin_tab1:
        st.header("Add New Wedding Dress")
        
        # Product details form
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
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Analyze this wedding dress and provide detailed specifications including: material, color, fabric, close color shemas, style, silhouette, neckline, train length, suitable body types, occasion recommendations, and any unique features, recommended age group, and any other relevant information. Format as JSON."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}
                            ]
                        }]
                    )
                    
                    analysis_text = str(response.choices[0].message.content)
                    
                    # Get embeddings
                    embedding_response = client.embeddings.create(
                        model="text-embedding-ada-002",
                        input=analysis_text
                    )
                    embeddings = embedding_response.data[0].embedding
                    
                    # Save to S3
                    temp_path = f"temp_{uploaded_file.name}"
                    image.save(temp_path)
                    s3_path = f"wedding_dresses/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
                    s3_client.upload_file(temp_path, S3_BUCKET, s3_path)
                    url = f"https://{S3_BUCKET}.s3.eu-central-1.amazonaws.com/{s3_path}"
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
                        "public_url": url
                    }
                    
                    collection.add(
                        documents=[analysis_text],
                        embeddings=[embeddings],
                        metadatas=[metadata],
                        ids=[doc_id]
                    )
                    
                    st.success("Dress added successfully!")
    
    with admin_tab2:
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

else:  # Shop page
    st.title("Wedding Dress Boutique")
    st.write("Find your perfect wedding dress with AI-powered search")
    
    # Search filters
    col1, col2, col3 = st.columns(3)
    with col1:
        price_range = st.slider("Price Range ($)", 0, 10000, (0, 10000), step=100)
    with col2:
        brands = ["All Brands"] + list(set([m.get('brand') for m in collection.get()['metadatas'] if m.get('brand')]))
        selected_brand = st.selectbox("Brand", brands)
    with col3:
        countries = ["All Countries"] + list(set([m.get('country') for m in collection.get()['metadatas'] if m.get('country')]))
        selected_country = st.selectbox("Country", countries)
    
    # AI Search
    search_query = st.text_area("Describe your dream dress:", 
                               placeholder="Example: A romantic A-line dress with lace sleeves and a sweetheart neckline, perfect for a garden wedding")
    
    n_results = st.slider("Number of results", min_value=1, max_value=10, value=5)
    
    if st.button("Search Dresses") and search_query:
        with st.spinner("Finding perfect matches..."):
            # Get embeddings for search
            query_embedding_response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=search_query
            )
            query_embeddings = query_embedding_response.data[0].embedding
            
            # Search in database
            results = collection.query(
                query_embeddings=[query_embeddings],
                n_results=n_results
            )
            
            if results['distances'][0]:
                # Post-process results with GPT-4
                system_prompt = """You are a wedding dress expert assistant. Analyze the search results and provide 
                personalized recommendations. For each dress, explain why it matches the user's requirements and 
                highlight its unique features."""
                
                search_results_context = f"User query: {search_query}\n\nSearch results:\n"
                for i in range(len(results['ids'][0])):
                    metadata = results['metadatas'][0][i]
                    description = results['documents'][0][i]
                    search_results_context += f"\nDress {i+1}:\n{description}\n"
                    search_results_context += f"Match score: {(1 - results['distances'][0][i]):.1%}\n"
                
                analysis_response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": search_results_context}
                    ],
                    temperature=0.7
                )
                
                expert_analysis = analysis_response.choices[0].message.content
                st.write("### Expert Analysis")
                st.write(expert_analysis)
                
                st.write("### Found Matches")
                
                for i in range(len(results['ids'][0])):
                    metadata = results['metadatas'][0][i]
                    
                    # Apply filters
                    if (selected_brand != "All Brands" and metadata.get('brand') != selected_brand) or \
                       (selected_country != "All Countries" and metadata.get('country') != selected_country) or \
                       (metadata.get('price', 0) < price_range[0] or metadata.get('price', 0) > price_range[1]):
                        continue
                    
                    # Display dress card
                    with st.container():
                        st.write("---")
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            if 'public_url' in metadata:
                                st.image(metadata['public_url'], caption=metadata.get('name', 'Wedding Dress'))
                        
                        with col2:
                            st.subheader(metadata.get('name', 'Wedding Dress'))
                            st.write(f"Brand: {metadata.get('brand', 'Unknown')}")
                            st.write(f"Price: ${metadata.get('price', 0):,.2f}")
                            st.write(f"Country: {metadata.get('country', 'Unknown')}")
                            st.write(f"Match Score: {(1 - results['distances'][0][i]):.1%}")
                            
                            with st.expander("View Details"):
                                st.write(results['documents'][0][i])
                                
                            st.button(f"Contact About This Dress {i+1}", key=f"contact_{i}")
            else:
                st.info("No matching dresses found. Try adjusting your search terms.")

if __name__ == "__main__":
    pass