import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
current_year = pd.to_datetime('now').year

# Virtual environment setup instructions
st.sidebar.title('Setup Instructions')
st.sidebar.write("""
1. Create a virtual environment: `python -m venv env`
2. Activate the virtual environment: `env\\Scripts\\activate` (Windows) or `source env/bin/activate` (Mac/Linux)
3. Install dependencies: `pip install -r requirements.txt`
4. Run the Streamlit app: `streamlit run app.py`
""")

# Load the dataset
@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)

# Normalize and capitalize the data
def clean_data(df):
    df['Title'] = df['Title'].str.lower().str.strip().str.title()
    df['Genre'] = df['Genre'].str.lower().str.strip().str.title().str.split(',').str[0]
    df['Director'] = df['Director'].str.lower().str.strip().str.title()
    df['Cast'] = df['Cast'].str.lower().str.strip().str.title()
    df['Votes'] = df['Votes'].str.replace(',', '').astype(float)
    df['Review Count'] = pd.to_numeric(df['Review Count'], errors='coerce')
    return df

# Filter rows where Nicolas Cage is mentioned in the Cast
def filter_cage_movies(df):
    return df[df['Cast'].str.contains('Nicolas Cage', case=False, na=False)].copy()

# Remove duplicates based on Title and Year
def remove_duplicates(df):
    return df.drop_duplicates(subset=['Title', 'Year'])

# Create a new column for 5-year intervals
def create_year_intervals(df):
    df = df.dropna(subset=['Year'])  # Drop rows where 'Year' is NaN
    df['Year Interval'] = (df['Year'] // 5) * 5
    df['Year Interval'] = df['Year Interval'].astype(int)
    return df

# Calculate the number of complete decades
def calculate_decades(df):
    earliest_year = df['Year'].min()
    latest_year = df['Year'].max()
    decades = (latest_year - earliest_year + 1) // 10
    return decades, earliest_year, latest_year

# Main function to run the app
def main():
    df = load_data('imdb-movies-dataset.csv')  # Ensure the file is in the same directory as this script
    df = clean_data(df)

    cage_movies = filter_cage_movies(df)
    cage_movies = remove_duplicates(cage_movies)
    cage_movies = create_year_intervals(cage_movies)

    # Calculate decades
    decades, earliest_year, latest_year = calculate_decades(cage_movies)
    decade_text = f"{decades} decades" if decades != 4 else "4 decades"
    
    st.title(f'Nicolas Cage: A Journey Through Film Spanning {decade_text}')
    st.image("https://m.media-amazon.com/images/M/MV5BMzY5YTYwODAtZjY4Yi00OGY5LTk0MTAtNWRhNDc1NWQ4ZGI1XkEyXkFqcGdeQXVyMTUzMTg2ODkz._V1_QL75_UX500_CR0,0,500,281_.jpg", caption="Nicolas Cage iconic performances")

    st.write(f"Nicolas Cage is one of Hollywood's most enigmatic and versatile actors. With a career spanning {decade_text} (from {earliest_year} to {latest_year}), he's played a wide range of characters in a variety of genres.")
    
    cage_movies['Year'] = pd.to_numeric(cage_movies['Year'], errors='coerce')
    cage_movies = create_year_intervals(cage_movies)

    # Calculate the top genre dynamically
    unique_genres = cage_movies[['Title', 'Genre']].drop_duplicates()
    genre_counts = unique_genres['Genre'].value_counts()
    top_genre = genre_counts.idxmax()

    total_movies = len(cage_movies)
    top_genre_count = cage_movies[cage_movies['Genre'] == top_genre].shape[0]
    first_movie = cage_movies.sort_values(by='Year').iloc[0]
    first_movie_year = int(first_movie['Year'])
    first_movie_title = first_movie['Title']

    upcoming_movies = df[(df['Year'] >= current_year + 1) & (df['Cast'].str.contains('Nicolas Cage', case=False, na=False))]

    summary_paragraph = f"""
    He has performed in a total of {total_movies} movies. His main genre is {top_genre}, having been part of {top_genre_count} movies in this genre. 
    He first appeared in a movie in the year {first_movie_year}, with the title "{first_movie_title}". 
    """

    if not upcoming_movies.empty:
        summary_paragraph += "Here are his future premiers:\n\n"
        for idx, movie in upcoming_movies.iterrows():
            movie_title = movie['Title']
            movie_year = int(movie['Year'])
            movie_url = movie.get('url', '#')
            summary_paragraph += f"- [{movie_title}]({movie_url}) ({movie_year})\n"
    else:
        summary_paragraph += "There are no movies scheduled for 2025 or later."

    st.write(summary_paragraph)

    st.subheader('From Ka-Boom to Ha-ha')
    st.write("Nicolas Cage has never shied away from experimenting with different genres. From action-packed thrillers to dramatic roles, let's see which genres he has dominated over the years.")

    genre_counts = unique_genres['Genre'].value_counts()
    top_genre = genre_counts.idxmax()
    genre_counts = genre_counts.reindex([top_genre] + [g for g in genre_counts.index if g != top_genre]).dropna()

    fig, ax = plt.subplots()
    sns.barplot(x=genre_counts.values, y=genre_counts.index, ax=ax, palette='viridis')
    ax.set_title('Genre Distribution')
    ax.set_xlabel('Number of Movies')
    ax.set_ylabel('Genre')

    for i, v in enumerate(genre_counts.values):
        ax.text(v + 0.5, i, str(v), color='black', va='center')

    st.pyplot(fig)

    top_genres = genre_counts.nlargest(3).index.tolist()

    st.subheader('Top Rated Movies')
    st.write("Nicolas Cage has undoubtedly delivered some stellar performances. Here are the top-rated movies starring Nicolas Cage.")
    top_rated = cage_movies.sort_values(by='Rating', ascending=False).head(10)
    top_rated['Year'] = top_rated['Year'].astype(int)
    top_rated['Rating'] = top_rated['Rating'].round(1)
    top_rated = top_rated[['Title', 'Year', 'Rating']].reset_index(drop=True)
    top_rated['Rating'] = top_rated['Rating'].map('{:.1f}'.format)

    st.table(top_rated.style.set_properties(**{'text-align': 'center'}))

    st.write("Cage's movies have seen a range of ratings over the years. Let's take a look at how his movies are rated and see the distribution of ratings.")

    rating_bins = pd.cut(cage_movies['Rating'], bins=[2, 3, 4, 5, 6, 7, 8], right=False)
    rating_counts = rating_bins.value_counts().sort_index()

    labels = [f'{int(bin.left)}' for bin in rating_counts.index]

    fig, ax = plt.subplots()
    sns.barplot(x=labels, y=rating_counts.values, ax=ax, palette='viridis', edgecolor='black')
    ax.set_title('Ratings Distribution')
    ax.set_xlabel('Rating')
    ax.set_ylabel('Number of Movies')

    for i, v in enumerate(rating_counts.values):
        ax.text(i, v + 0.1, str(v), color='black', ha='center')

    st.pyplot(fig)

    st.subheader('Top 3 Genres Ranked by Ratings')
    st.write("Let's see how the top 3 genres for Nicolas Cage's movies rank based on their average ratings and average votes per movie.")
    top_genre_ratings_votes = cage_movies[cage_movies['Genre'].isin(top_genres)].groupby('Genre').agg({'Rating': 'mean', 'Votes': 'mean'}).loc[top_genres]

    fig, ax1 = plt.subplots()
    sns.barplot(x=top_genre_ratings_votes.index, y=top_genre_ratings_votes['Rating'], ax=ax1, palette='viridis')
    ax2 = ax1.twinx()
    sns.lineplot(x=top_genre_ratings_votes.index, y=top_genre_ratings_votes['Votes'], ax=ax2, color='red', marker='o', linestyle='-', linewidth=2)

    ax1.set_ylabel('Average Rating')
    ax2.set_ylabel('Average Votes per Movie')
    ax1.set_xlabel('Genre')
    ax1.set_title('Top 3 Genres Ranked by Ratings and Votes')

    for i, v in enumerate(top_genre_ratings_votes['Rating']):
        ax1.text(i, v + 0.1, f'{v:.1f}', color='black', ha='center')

    for i, v in enumerate(top_genre_ratings_votes['Votes']):
        ax2.text(i, v, f'{int(v)}', color='red', ha='center')

    st.pyplot(fig)

    st.subheader('Critical Reception by 5-Year Intervals')
    st.write("Beyond audience ratings, let's take a look at the critical reception of Nicolas Cage's movies through their Metascores and review counts over 5-year intervals.")

    avg_metascore_reviews_by_interval = cage_movies.groupby('Year Interval').agg({'Metascore': 'mean', 'Review Count': 'sum'}).dropna()

    fig, ax1 = plt.subplots()
    sns.barplot(x=avg_metascore_reviews_by_interval.index.astype(str), y=avg_metascore_reviews_by_interval['Metascore'], ax=ax1, palette='viridis')
    ax2 = ax1.twinx()
    sns.lineplot(x=avg_metascore_reviews_by_interval.index.astype(str), y=avg_metascore_reviews_by_interval['Review Count'], ax=ax2, color='red', marker='o', linestyle='-', linewidth=2)

    ax1.set_ylabel('Average Metascore')
    ax2.set_ylabel('Total Review Count')
    ax1.set_xlabel('Year Interval')
    ax1.set_title('Critical Reception by 5-Year Intervals')

    for i, (x, y) in enumerate(zip(avg_metascore_reviews_by_interval.index, avg_metascore_reviews_by_interval['Metascore'])):
        ax1.text(i, y + 0.5, f'{int(y)}', color='black', ha='center')

    for i, (x, y) in enumerate(zip(avg_metascore_reviews_by_interval.index, avg_metascore_reviews_by_interval['Review Count'])):
        ax2.text(i, y, f'{int(y)}', color='red', ha='center')

    st.pyplot(fig)

    st.subheader(f'{top_genre} Genre: Ratings and Reviews by 5-Year Intervals')
    st.write(f"Let's dive deeper into the {top_genre}, which is Nic's most dominant genre and see how the ratings and reviews evolved over 5-year intervals.")

    top_genre_movies = cage_movies[cage_movies['Genre'] == top_genre]
    avg_rating_reviews_by_interval = top_genre_movies.groupby('Year Interval').agg({'Rating': 'mean', 'Review Count': 'sum'}).dropna()

    fig, ax1 = plt.subplots()
    sns.barplot(x=avg_rating_reviews_by_interval.index.astype(str), y=avg_rating_reviews_by_interval['Rating'], ax=ax1, palette='viridis')
    ax2 = ax1.twinx()
    sns.lineplot(x=avg_rating_reviews_by_interval.index.astype(str), y=avg_rating_reviews_by_interval['Review Count'], ax=ax2, color='red', marker='o', linestyle='-', linewidth=2)

    ax1.set_ylabel('Average Rating')
    ax2.set_ylabel('Total Review Count')
    ax1.set_xlabel('Year Interval')
    ax1.set_title(f'{top_genre} Genre: Ratings and Reviews by 5-Year Intervals')

    for i, (x, y) in enumerate(zip(avg_rating_reviews_by_interval.index, avg_rating_reviews_by_interval['Rating'])):
        ax1.text(i, y + 0.1, f'{y:.1f}', color='black', ha='center')

    for i, (x, y) in enumerate(zip(avg_rating_reviews_by_interval.index, avg_rating_reviews_by_interval['Review Count'])):
        ax2.text(i, y, f'{int(y)}', color='red', ha='center')

    st.pyplot(fig)

    st.subheader('Summary and Conclusions')
    st.write(f"""
    Starting in {first_movie_year} and over the past four decades, Nicolas Cage has showcased his versatility across a wide range of genres in {total_movies} movies. His most dominant genre is {top_genre}, with {top_genre_count} performances. Cage's movies have seen a diverse range of audience and critical receptions, with notable highs in both ratings and review counts.

    In conclusion, Nicolas Cage's career is a testament to his ability to adapt and excel captivating audiences and critics alike. As we look forward to his upcoming movies, it's evident that Cage's legacy in the film industry will continue to grow.

    Thank you for exploring Nicolas Cage's filmography with us. Stay tuned for more updates and insights!
    """)

    st.markdown("[View this project on GitHub](https://github.com/felixamado/MadKudu)")

if __name__ == "__main__":
    main()
