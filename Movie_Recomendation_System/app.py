import streamlit as st
import json
from Classifier import KNearestNeighbours
from operator import itemgetter
import numpy as np
from bs4 import BeautifulSoup
import requests
import io
from PIL import Image
from urllib.request import urlopen

# Load data and movies list from corresponding JSON files
with open(r'.\Data\data.json', 'r+', encoding='utf-8') as f:
    data = json.load(f)
with open(r'.\Data\titles.json', 'r+', encoding='utf-8') as f:
    movie_titles = json.load(f)

hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (HTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 Edg/97.0.1072.76'}

# Function to fetch movie poster
def movie_poster_fetcher(imdb_link):
    try:
        # Display Movie Poster
        url_data = requests.get(imdb_link, headers=hdr).text
        s_data = BeautifulSoup(url_data, 'html.parser')
        imdb_dp = s_data.find("meta", property="og:image")

        if imdb_dp is not None and 'content' in imdb_dp.attrs:
            movie_poster_link = imdb_dp['content']
            u = urlopen(movie_poster_link)
            raw_data = u.read()
            image = Image.open(io.BytesIO(raw_data))  # Use Image instead of PIL.Image
            image = image.resize((158, 301))
            st.image(image, use_column_width=False)
        else:
            st.write("Movie poster not found.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Function to get movie information
def get_movie_info(imdb_link):
    try:
        url_data = requests.get(imdb_link, headers=hdr).text
        s_data = BeautifulSoup(url_data, 'html.parser')

        # Find the meta tags containing the movie title, year, and IMDb rating
        title_meta = s_data.find("meta", property="twitter:title")
        image_meta = s_data.find("meta", property="twitter:image:alt")
        
        if not title_meta or not image_meta:
            return "Title info not found", "Director info not found", "Cast info not found", "Story info not found", "Release year not found", "IMDb rating not found", ""
        
        title_content = title_meta["content"]
        image_content = image_meta["content"]
        
        # Extracting the title, year, and rating from the content
        title, info = title_content.split(" (")
        year = info.split(") ")[0]
        rating = info.split(") ")[1].split(" ")[1]
        imdb_genres = "Genres: " + info.split("| ")[1].strip()

        # Extracting director, cast, and story from the image content
        director = "Director: " + image_content.split(": Directed by ")[1].split(". With")[0].strip()
        cast = "Cast: " + image_content.split(". With ")[1].split(". ")[0].strip()
        story = "Story: " + image_content.split(". With ")[1].split(". ")[1].split(". ")[0].strip()

        return director, cast, story, f"Release Year: {year}", f"IMDb Rating: {rating}", imdb_genres
    
    except Exception as e:
        return "An error occurred while fetching movie info", "", "", "", "", "", ""

def knn(test_point, k):
    # Create dummy target variable for the KNN Classifier
    target = [0 for item in movie_titles]
    # Instantiate object for the Classifier
    model = KNearestNeighbours(data, target, test_point, k=k)
    # Run the algorithm
    model.fit()
    # Distances to most distant movie
    max_dist = sorted(model.distances, key=itemgetter(0))[-1]
    # Print list of 10 recommendations < Change value of k for a different number >
    table = list()
    for i in model.indices:
        # Returns back movie title and imdb link
        table.append([movie_titles[i][0], movie_titles[i][2]])
    return table

if __name__ == '__main__':
    img1 = Image.open('./meta/logo.jpg')
    img1 = img1.resize((550, 250))
    st.image(img1, use_column_width=True)  # Adjusted to use_column_width=True
    genres = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Drama', 'Family',
              'Fantasy', 'History', 'Horror', 'Musical', 'Mystery', 'Music', 'Romance', 'Sci-Fi', 'Sport', 'Thriller', 'War']
    movies = [title[0] for title in movie_titles]
    st.header('Movie Recommendation System')
    apps = ['--Select--', 'Movie based', 'Genre based']
    app_options = st.selectbox('Select application:', apps)

    if app_options == 'Movie based':
        movie_select = st.selectbox('Select movie:', ['--Select--'] + movies)
        if movie_select == '--Select--':
            st.write('Select a movie')
        else:
            n = st.number_input('Number of movies:', min_value=5, max_value=20, step=1)
            genres = data[movies.index(movie_select)]
            test_point = genres
            table = knn(test_point, n)
            c = 0 
            for movie, link in table:
                c += 1
                # Displays movie title with link to imdb
                st.markdown(f"({c}) [{movie}]({link})")
                movie_poster_fetcher(link)
                director, cast, story, release_year, rating, imdb_genres = get_movie_info(link)
                st.markdown(imdb_genres)
                st.markdown(release_year)
                st.markdown(director)
                st.markdown(cast)
                st.markdown(story)
                st.markdown('IMDB Rating: ' + str(rating) + '⭐')

    elif app_options == apps[2]:
        options = st.multiselect('Select genres:', genres)
        if options:
            imdb_score = st.slider('IMDb score:', 1, 10, 8)
            n = st.number_input('Number of movies:', min_value=5, max_value=20, step=1)
            test_point = [1 if genre in options else 0 for genre in genres]
            test_point.append(imdb_score)
            table = knn(test_point, n)
            c = 0
            for movie, link in table:
                c += 1
                # Displays movie title with link to imdb
                st.markdown(f"({c}) [{movie}]({link})")
                movie_poster_fetcher(link)
                director, cast, story, release_year, rating, imdb_genres = get_movie_info(link)
                st.markdown(imdb_genres)
                st.markdown(release_year)
                st.markdown(director)
                st.markdown(cast)
                st.markdown(story)
                st.markdown('IMDB Rating: ' + str(rating) + '⭐')

        else:
            st.write("This is a simple Movie Recommender application. "
                     "You can select the genres and change the IMDb score.")
