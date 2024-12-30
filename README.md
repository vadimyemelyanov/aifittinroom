# AI Fitting Room
# Version 0.0.1
## Set-university proj demo

This project is a streamlit app for searching wedding dresses. It uses OpenAI API for generating embeddings and searching for dresses. It has a database of dresses and a chatbot for searching. Admin can add dresses to the database.

For verion 0.0.1 it has only shop page with search and filter options. Also its deployed to Streamlit Cloud.

Later versions will be deployed to AWS ECS.

DEMO : https://aifittinroom-zqkwhapp4ukubmz9mtmegqu.streamlit.app

Admin creds: admin/admin


# How to run locally

1. Clone the repository
2. Install dependencies
3. Update .env file
3. Run the app

```bash
git clone https://github.com/aifittinroom/aifittinroom.git
cd aifittinroom
pip install -r requirements.txt
streamlit run app/main.py
```

# Features

- Shop page with search and filter options
- Admin page for adding dresses to the database
- Chatbot for searching dresses
- Embeddings for searching dresses
- Database of dresses
- Deployment to Streamlit Cloud

# TODO
- Deployment to AWS ECS
- Add more features to the shop page
- Optimize embeddings generation
- Optimize search results
