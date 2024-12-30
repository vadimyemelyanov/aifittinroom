from openai import OpenAI
import base64

client = OpenAI()

def analyze_dress_image(img_str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Analyze this wedding dress and provide detailed specifications including: material, color, fabric, close color shemas, style, silhouette, neckline, train length, suitable body types, occasion recommendations, and any unique features, recommended age group, and any other relevant information. At least 50 tags and specifications. Format as JSON. "
            },
            {
                "role": "user",
                "content": f"Here is an image of a wedding dress: data:image/jpeg;base64,{img_str}"
            }
        ],
        response_format={"type": "text"},
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
    highlight its unique features. Response should be in a language that client asked at the beginning of the search. Write resolution at the end where best result will be written."""
    
    search_results_context = f"User query: {search_query}\n\nSearch results:\n {results}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": search_results_context}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content 