import streamlit as st
import pickle
import requests
import base64
from pathlib import Path

def set_bg(image_path):
    if not Path(image_path).is_file():
        st.error(f"Background image file not found at: {image_path}")
        return

    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    page_bg_img = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{encoded_string}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

def fetch_movie_details(movie_name):
    api_key = '70a24a13a16925eb3257320307164cfa'
    search_url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_name}'
    response = requests.get(search_url)
    data = response.json()

    if data['results']:
        movie_id = data['results'][0]['id']
        poster_url = f"https://image.tmdb.org/t/p/w500{data['results'][0]['poster_path']}"

        movie_details_url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&append_to_response=credits'
        movie_details_response = requests.get(movie_details_url)
        movie_details_data = movie_details_response.json()

        overview = movie_details_data.get('overview', 'Overview not available')
        rating = movie_details_data.get('vote_average', 'Rating not available')
        cast = [actor['name'] for actor in
                movie_details_data.get('credits', {}).get('cast', [])[:5]]  # Top 5 cast members

        return poster_url, overview, rating, cast
    else:
        return "https://via.placeholder.com/150", "No Overview", "No Rating", []

def recommend(movie, movies, similary):
    index = movies[movies['Movie_name'] == movie].index[0]
    distances = sorted(list(enumerate(similary[index])), reverse=True, key=lambda x: x[1])
    recommended_movies = [movies.iloc[i[0]].Movie_name for i in distances[1:15]]
    return recommended_movies

def add_chatbot():
    chatbot_html = f"""
    <script>
        function openChatbot() {{
            const chatbotFrame = document.getElementById("chatbot-frame");
            chatbotFrame.style.display = chatbotFrame.style.display === "none" ? "block" : "none";
        }}
    </script>
    <style>
        .chatbot-icon {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background-color: #007bff;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            justify-content: center;
            align-items: center;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            z-index: 1000;
        }}
        .chatbot-icon img {{
            width: 40px;
            height: 40px;
        }}
        #chatbot-frame {{
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 300px;
            height: 400px;
            border: none;
            display: none;
            z-index: 1000;
        }}
    </style>
    <div class="chatbot-icon" onclick="openChatbot()">
        <img src="https://cdn-icons-png.flaticon.com/512/2331/2331985.png" alt="Chatbot Icon">
    </div>
    <iframe id="chatbot-frame" src="https://your-hosted-backend-url/chatbot"></iframe>
    """
    st.markdown(chatbot_html, unsafe_allow_html=True)

def movie_recommendation_page():
    # Load movie data
    movies = pickle.load(open("movies (1).pkl", "rb"))
    similary = pickle.load(open("similary (1).pkl", "rb"))

    set_bg("b8.jpg")
    st.markdown(
        "<h1 style='text-align: center; color: white;'>WatchWise - A Cineworld</h1>",
        unsafe_allow_html=True
    )

    selected_movie_name = st.selectbox("Select Movie", movies['Movie_name'].values)

    if st.button("Recommend"):
        recommendations = recommend(selected_movie_name, movies, similary)
        st.subheader("Recommended Movies:")

        for i in range(0, 15, 5):
            cols = st.columns(5)
            for col, j in zip(cols, range(i, i + 5)):
                if j < len(recommendations):
                    movie_title = recommendations[j]
                    poster_url, overview, rating, cast = fetch_movie_details(movie_title)

                    with col:
                        st.image(poster_url, width=130)
                        st.write(movie_title)

    # Add Chatbot
    add_chatbot()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.error("Please log in to access the movie recommendation page.")
else:
    movie_recommendation_page()
