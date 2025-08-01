import pandas as pd
from bs4 import BeautifulSoup
import requests
hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 Edg/97.0.1072.76'}

# Load the dataset
df = pd.read_csv('newdataset.csv')


# Function to extract IMDb score from IMDb link
def get_movie_info(imdb_link):
    try:
        url_data = requests.get(imdb_link, headers=hdr).text
        s_data = BeautifulSoup(url_data, 'html.parser')

        # Find the meta tags containing the movie title, year, and IMDb rating
        title_meta = s_data.find("meta", property="twitter:title")
        image_meta = s_data.find("meta", property="twitter:image:alt")
        
        if not title_meta or not image_meta:
            return "IMDb rating not found"
        
        title_content = title_meta["content"]
        image_content = image_meta["content"]
        
        # Extracting the title, year, and rating from the content
        title, info = title_content.split(" (")
        year = info.split(") ")[0]
        rating = info.split(") ")[1].split(" ")[1]
        
        # Extracting director, cast, and story from the image content
        director = "Director: " + image_content.split(": Directed by ")[1].split(". With")[0].strip()
        cast = "Cast: " + image_content.split(". With ")[1].split(". ")[0].strip()
        story = "Story: " + image_content.split(". With ")[1].split(". ")[1].split(". ")[0].strip()
        
        return f"{rating}"
    
    except Exception as e:
        return "An error occurred while fetching movie info"


# Apply the function to create the 'imdb_scores' column
df['imdb_scores'] = df['movie_imdb_link'].apply(get_movie_info)

# Display the first five rows with IMDb scores
print(df[['genres', 'movie_title', 'movie_imdb_link', 'imdb_scores']].head())

# Save the updated dataset
df.to_csv('newdataset.csv', index=False)