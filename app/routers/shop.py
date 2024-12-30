import streamlit as st
from services import ai_service

def shop_page(collection):
    st.title("Wedding Dress Boutique")
    st.write("Find your perfect wedding dress with AI-powered search")
    
    # Search filters and implementation
    handle_search(collection)

def handle_search(collection):
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
            query_embeddings = ai_service.get_embeddings(search_query)
            # Search in database
            results = collection.query(
                query_embeddings=[query_embeddings],
                n_results=n_results
            )
            
            if results['distances'][0]:
                # Post-process results with GPT-4
                
                search_results_context = f"User query: {search_query}\n\nSearch results:\n"
                for i in range(len(results['ids'][0])):
                    metadata = results['metadatas'][0][i]
                    description = results['documents'][0][i]
                    search_results_context += f"\nDress {i+1}:\n{description}\n"
                    search_results_context += f"Match score: {(1 - results['distances'][0][i]):.1%}\n"
                expert_analysis =  ai_service.analyze_search_results(search_query, search_results_context)
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