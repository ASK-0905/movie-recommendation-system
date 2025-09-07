# app.py
import json
import streamlit as st
from recommend import df, recommend_movies

# Extract all unique genres from the dataset
all_genres = set()
for genre_list in df['Genre'].dropna():
    for genre in genre_list.split(","):
        all_genres.add(genre.strip())

all_genres = sorted(all_genres)

from omdb_utils import get_movie_details


config = json.load(open("config.json"))

# OMDB api key
OMDB_API_KEY = config["OMDB_API_KEY"]

st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Punugulus Movie Recommender ")

if st.button("📋 Show My Ratings"):
    if st.session_state["ratings"]:
        st.write(st.session_state["ratings"])
    else:
        st.info("No ratings saved yet.")

st.subheader("🎥 Filter by Genre")

# Genre selection dropdown
selected_genre = st.selectbox("Choose a genre:", ["-- All Genres --"] + all_genres)

# Filter movies based on selected genre
if selected_genre == "-- All Genres --":
    filtered_movies = sorted(df['Movie'].dropna().unique())
else:
    filtered_movies = sorted(
        df[df['Genre'].str.contains(selected_genre, case=False, na=False)]['Movie'].dropna().unique()
    )

# Movie selection dropdown (based on genre)
selected_movie = st.selectbox("🎬 Select a movie:", filtered_movies)


# # Using 'title' instead of 'song' now
# movie_list = sorted(df['Movie'].dropna().unique())


# selected_movie = st.selectbox("🎬 Select a movie:", movie_list)

# Initialize rating dictionary in session state
if "ratings" not in st.session_state:
    st.session_state["ratings"] = {}

# Let the user give a rating for the selected movie
user_rating = st.slider(f"⭐ Rate {selected_movie} (0-10):", 0, 10, 5)

if st.button("💾 Save Rating"):
    st.session_state["ratings"][selected_movie] = user_rating
    st.success(f"Saved rating {user_rating} for {selected_movie}")


# if st.button("🚀 Recommend Similar Movies"):
#     with st.spinner("Finding similar movies..."):
#         recommendations = recommend_movies(selected_movie)
#         if recommendations is None or recommendations.empty:
#             st.warning("Sorry, no recommendations found.")
#         else:
#             st.success("Top similar movies:")
#             for _, row in recommendations.iterrows():
#                 movie_title = row['Movie']
#                 plot, poster = get_movie_details(movie_title, OMDB_API_KEY)

#                 with st.container():
#                     col1, col2 = st.columns([1, 3])
#                     with col1:
#                         if poster != "N/A":
#                             st.image(poster, width=100)
#                         else:
#                             st.write("❌ No Poster Found")
#                     with col2:
#                         st.markdown(f"### {movie_title}")
#                         st.markdown(f"*{plot}*" if plot != "N/A" else "_Plot not available_")
if st.button("🚀 Recommend Similar Movies"):
    with st.spinner("Finding similar movies..."):
        recommendations = recommend_movies(selected_movie)
        if recommendations is None or recommendations.empty:
            st.warning("Sorry, no recommendations found.")
        else:
            # Filter out movies rated below 6 by the user
            disliked_movies = {movie for movie, rating in st.session_state["ratings"].items() if rating < 6}
            filtered_recommendations = recommendations[~recommendations['Movie'].isin(disliked_movies)]

            if filtered_recommendations.empty:
                st.warning("All similar movies are either disliked or rated below your threshold.")
            else:
                st.success("Top similar movies:")
                for _, row in filtered_recommendations.iterrows():
                    movie_title = row['Movie']
                    plot, poster = get_movie_details(movie_title, OMDB_API_KEY)

                    with st.container():
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            if poster != "N/A":
                                st.image(poster, width=100)
                            else:
                                st.write("❌ No Poster Found")
                        with col2:
                            st.markdown(f"### {movie_title}")
                            st.markdown(f"*{plot}*" if plot != "N/A" else "_Plot not available_")
