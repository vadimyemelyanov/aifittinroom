import requests
import io
from PIL import Image
import random
import datetime
import base64
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize OpenAI
# Initialize ChromaDB
PERSIST_DIRECTORY = "db"
chroma_client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
collection = chroma_client.get_or_create_collection(
    name="wedding_dresses",
    metadata={"hnsw:space": "cosine"}
)

# Sample data
BRANDS = ["Vera Wang", "Pronovias", "Maggie Sottero", "David's Bridal", "Oscar de la Renta", 
          "Elie Saab", "Jenny Packham", "Monique Lhuillier", "Reem Acra", "Carolina Herrera"]

COUNTRIES = ["USA", "Spain", "Italy", "France", "UK", "Australia", "Canada", "Japan", 
            "South Korea", "Germany"]

DRESS_ADJECTIVES = ["Elegant", "Romantic", "Modern", "Classic", "Bohemian", "Vintage", 
                   "Royal", "Ethereal", "Luxurious", "Minimalist"]

DRESS_STYLES = ["Princess", "Mermaid", "A-line", "Ballgown", "Sheath", "Empire", 
                "Tea Length", "Column", "Trumpet", "High-Low"]
from openai import OpenAI
import base64

client = OpenAI()

def analyze_dress_image(img_str):
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
    return str(response.choices[0].message.content)

def get_embeddings(text):
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

def analyze_search_results(search_query, results):
    system_prompt = """You are a wedding dress expert assistant. Analyze the search results and provide 
    personalized recommendations. For each dress, explain why it matches the user's requirements and 
    highlight its unique features."""
    
    search_results_context = f"User query: {search_query}\n\nSearch results:\n"
    for i in range(len(results['ids'][0])):
        metadata = results['metadatas'][0][i]
        description = results['documents'][0][i]
        search_results_context += f"\nDress {i+1}:\n{description}\n"
        search_results_context += f"Match score: {(1 - results['distances'][0][i]):.1%}\n"
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": search_results_context}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content 

def generate_dress_name():
    return f"{random.choice(DRESS_ADJECTIVES)} {random.choice(DRESS_STYLES)}"

def search_wedding_dresses():
    # Using Unsplash API for high-quality free images
    UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
    url = f"https://api.unsplash.com/search/photos"
    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
    params = {
        "query": "wedding dress portrait",
        "per_page": 20,
        "orientation": "portrait"
    }
    
    response = requests.get(url, headers=headers, params=params)
    return response.json()["results"]

def main():
    print("Fetching wedding dress images...")
    dresses = search_wedding_dresses()
    
    for i, dress in enumerate(dresses, 1):
        try:
            print(f"\nProcessing dress {i}/20...")
            
            # Download image
            img_response = requests.get(dress["urls"]["regular"])
            image = Image.open(io.BytesIO(img_response.content))
            
            # Convert image for AI analysis
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # AI Analysis
            print("Analyzing image...")
            analysis_text = analyze_dress_image(img_str)            
            # Get embeddings
            print("Generating embeddings...")
            embeddings = get_embeddings(analysis_text)
            
            # Generate random metadata
            metadata = {
                "filename": f"dress_{i}.jpg",
                "upload_date": datetime.datetime.now().isoformat(),
                "country": random.choice(COUNTRIES),
                "brand": random.choice(BRANDS),
                "price": round(random.uniform(1000, 10000), 2),
                "name": generate_dress_name(),
                "public_url": dress["urls"]["regular"]
            }
            
            # Save to database
            print("Saving to database...")
            doc_id = str(datetime.datetime.now().timestamp())
            collection.add(
                documents=[analysis_text],
                embeddings=[embeddings],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
            print(f"Successfully added dress {i}")
            
        except Exception as e:
            print(f"Error processing dress {i}: {str(e)}")
            continue

if __name__ == "__main__":
    main()


