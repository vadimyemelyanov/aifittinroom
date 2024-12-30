from openai import OpenAI
import base64

client = OpenAI()

def analyze_dress_image(img_str):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "Analyze this wedding dress and provide detailed specifications in tags for example: \n                 material, color, fabric, close color schemas, style, silhouette, neckline, train length,\n                    suitable body types, occasion recommendations, and any unique features, recommended age group,\n                  and any other relevant information. Response should contain at least 50 unique tags and specifications.  Format it in a way that will be readable and easily analysable by LLM."
            },
            {
                "role": "user",
                "content": {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}
            }
        ],
        response_format={"type": "text"},
        temperature=1,
        max_completion_tokens=3500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
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
    highlight its unique features. Response should be in a language that client asked at the beginning of the search."""
    
    search_results_context = f"User query: {search_query}\n\nSearch results:\n {results}"
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": search_results_context}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content 