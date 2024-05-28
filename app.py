import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
df = pd.read_csv('imdb-movies-dataset.csv')

# Normalize and capitalize the data: convert to lowercase, trim whitespace, and capitalize
df['Title'] = df['Title'].str.lower().str.strip().str.title()
df['Genre'] = df['Genre'].str.lower().str.strip().str.title().str.split(',').str[0]  # Take only the first genre
df['Director'] = df['Director'].str.lower().str.strip().str.title()
df['Cast'] = df['Cast'].str.lower().str.strip().str.title()

# Clean Votes column and convert to numeric
df['Votes'] = df['Votes'].str.replace(',', '').astype(float)
df['Review Count'] = pd.to_numeric(df['Review Count'], errors='coerce')

# Filter rows where Nicolas Cage is mentioned in the Cast
cage_movies = df[df['Cast'].str.contains('Nicolas Cage', case=False, na=False)].copy()

# Remove duplicates based on Title and Year
unique_movies = cage_movies.drop_duplicates(subset=['Title', 'Year'])

# Filter for the last 30 years
current_year = pd.to_datetime('now').year
unique_movies = unique_movies[unique_movies['Year'] >= current_year - 30]

# Create a new column for 5-year intervals
unique_movies['Year Interval'] = (unique_movies['Year'] // 5) * 5
unique_movies['Year Interval'] = unique_movies['Year Interval'].astype(int)

# Streamlit app
st.title('Nicolas Cage: A Journey Through Film')

st.image("https://m.media-amazon.com/images/M/MV5BMzY5YTYwODAtZjY4Yi00OGY5LTk0MTAtNWRhNDc1NWQ4ZGI1XkEyXkFqcGdeQXVyMTUzMTg2ODkz._V1_QL75_UX500_CR0,0,500,281_.jpg", caption="Nicolas Cage iconic performances")

st.write("""
Nicolas Cage is one of Hollywood's most enigmatic and versatile actors. 
With a career spanning decades, he's played a wide range of characters in a variety of genres.""")

# Ensure 'Year' is a numeric type
unique_movies['Year'] = pd.to_numeric(unique_movies['Year'], errors='coerce')

# Filter for the last 30 years and exclude future years
current_year = pd.to_datetime('now').year
unique_movies = unique_movies[(unique_movies['Year'] >= current_year - 30) & (unique_movies['Year'] <= current_year)]

# Create a new column for 5-year intervals
unique_movies['Year Interval'] = (unique_movies['Year'] // 5) * 5
unique_movies['Year Interval'] = unique_movies['Year Interval'].astype(int)

# Calculate the top genre dynamically
unique_genres = unique_movies[['Title', 'Genre']].drop_duplicates()
genre_counts = unique_genres['Genre'].value_counts()
top_genre = genre_counts.idxmax()

# Summary paragraph about Nicolas Cage
total_movies = len(unique_movies)
top_genre_count = unique_movies[unique_movies['Genre'] == top_genre].shape[0]
first_movie = unique_movies.sort_values(by='Year').iloc[0]
first_movie_year = int(first_movie['Year'])
first_movie_title = first_movie['Title']

# Find Nicolas Cage's movies scheduled for 2025 or later
next_year = 2025
upcoming_movies = df[(df['Year'] >= next_year) & (df['Cast'].str.contains('Nicolas Cage', case=False, na=False))]

# Construct the paragraph
summary_paragraph = f"""
Nicolas Cage is an actor who has performed in a total of {total_movies} movies. His main genre is {top_genre}, having been part of {top_genre_count} movies in this genre. 
He first appeared in a movie in the year {first_movie_year}, with the title "{first_movie_title}". 
"""

if not upcoming_movies.empty:
    summary_paragraph += "Here are the movies that are scheduled for 2025 and later:\n\n"
    for idx, movie in upcoming_movies.iterrows():
        movie_title = movie['Title']
        movie_year = int(movie['Year'])
        movie_url = movie.get('url', '#')  # Use a placeholder URL if 'url' is not available
        summary_paragraph += f"- [{movie_title}]({movie_url}) ({movie_year})\n"
else:
    summary_paragraph += "These are future Nic Cage's premiers:"

# Display the paragraph
st.write(summary_paragraph)


# Genre distribution
st.subheader('From Ka-Boom to Haha')
st.write("""
Nicolas Cage has never shied away from experimenting with different genres. 
From action-packed thrillers to dramatic roles, let's see which genres he has dominated over the years.
""")
unique_genres = unique_movies[['Title', 'Genre']].drop_duplicates()

# Get genre counts and ensure the top genre is dynamically selected
genre_counts = unique_genres['Genre'].value_counts()
top_genre = genre_counts.idxmax()
genre_counts = genre_counts.reindex([top_genre] + [g for g in genre_counts.index if g != top_genre]).dropna()

fig, ax = plt.subplots()
sns.barplot(x=genre_counts.values, y=genre_counts.index, ax=ax, palette='viridis')
ax.set_title('Genre Distribution')
ax.set_xlabel('Number of Movies')
ax.set_ylabel('Genre')

# Annotate the bars with the counts
for i, v in enumerate(genre_counts.values):
    ax.text(v + 0.5, i, str(v), color='black', va='center')

st.pyplot(fig)

# Top 3 genres
top_genres = genre_counts.nlargest(3).index.tolist()

# Top rated movies
st.subheader('Top Rated Movies')
st.write("""
Nicolas Cage has undoubtedly delivered some stellar performances. Here are the top-rated movies starring Nicolas Cage.
""")
top_rated = unique_movies.sort_values(by='Rating', ascending=False).head(10)
top_rated['Year'] = top_rated['Year'].astype(int)
top_rated['Rating'] = top_rated['Rating'].round(1)
top_rated = top_rated[['Title', 'Year', 'Rating']].reset_index(drop=True)

# Format the dataframe to show only one decimal place for ratings
top_rated['Rating'] = top_rated['Rating'].map('{:.1f}'.format)

st.table(top_rated.style.set_properties(**{'text-align': 'center'}))


# Ratings distribution
st.write("""Cage's movies have seen a range of ratings over the years. 
Let's take a look at how his movies are rated and see the distribution of ratings.
""")

# Bin the ratings by 1.0 intervals
rating_bins = pd.cut(unique_movies['Rating'], bins=[2, 3, 4, 5, 6, 7, 8], right=False)
rating_counts = rating_bins.value_counts().sort_index()

# Create labels for the mid-point of each bin
labels = [f'{int(bin.left)}' for bin in rating_counts.index]

# Plotting the distribution
fig, ax = plt.subplots()
sns.barplot(x=labels, y=rating_counts.values, ax=ax, palette='viridis', edgecolor='black')
ax.set_title('Ratings Distribution')
ax.set_xlabel('Rating')
ax.set_ylabel('Number of Movies')

# Annotate the bars with counts
for i, v in enumerate(rating_counts.values):
    ax.text(i, v + 0.1, str(v), color='black', ha='center')

st.pyplot(fig)



# Top 3 genres ranked by ratings
st.subheader('Top 3 Genres Ranked by Ratings')
st.write("""
Let's see how the top 3 genres for Nicolas Cage's movies rank based on their average ratings and average votes per movie.
""")
top_genre_ratings_votes = unique_movies[unique_movies['Genre'].isin(top_genres)].groupby('Genre').agg({'Rating': 'mean', 'Votes': 'mean'}).loc[top_genres]

fig, ax1 = plt.subplots()
sns.barplot(x=top_genre_ratings_votes.index, y=top_genre_ratings_votes['Rating'], ax=ax1, palette='viridis')
ax2 = ax1.twinx()
sns.lineplot(x=top_genre_ratings_votes.index, y=top_genre_ratings_votes['Votes'], ax=ax2, color='red', marker='o', linestyle='-', linewidth=2)

ax1.set_ylabel('Average Rating')
ax2.set_ylabel('Average Votes per Movie')
ax1.set_xlabel('Genre')
ax1.set_title('Top 3 Genres Ranked by Ratings and Votes')

# Annotate the bars with the average ratings
for i, v in enumerate(top_genre_ratings_votes['Rating']):
    ax1.text(i, v + 0.1, f'{v:.1f}', color='black', ha='center')

# Annotate the line with the average votes
for i, v in enumerate(top_genre_ratings_votes['Votes']):
    ax2.text(i, v, f'{int(v)}', color='red', ha='center')

st.pyplot(fig)

# Critical Reception by 5-Year Intervals
st.subheader('Critical Reception by 5-Year Intervals')
st.write("""
Beyond audience ratings, let's take a look at the critical reception of Nicolas Cage's movies through their Metascores and review counts over 5-year intervals.
""")

# Calculate the average Metascore per 5-year interval
avg_metascore_reviews_by_interval = unique_movies.groupby('Year Interval').agg({'Metascore': 'mean', 'Review Count': 'sum'}).dropna()

# Filter for the last 30 years
avg_metascore_reviews_by_interval = avg_metascore_reviews_by_interval[avg_metascore_reviews_by_interval.index >= current_year - 30]
avg_metascore_reviews_by_interval = avg_metascore_reviews_by_interval[avg_metascore_reviews_by_interval.index <= current_year]

fig, ax1 = plt.subplots()
sns.barplot(x=avg_metascore_reviews_by_interval.index.astype(str), y=avg_metascore_reviews_by_interval['Metascore'], ax=ax1, palette='viridis')
ax2 = ax1.twinx()
sns.lineplot(x=avg_metascore_reviews_by_interval.index.astype(str), y=avg_metascore_reviews_by_interval['Review Count'], ax=ax2, color='red', marker='o', linestyle='-', linewidth=2)

ax1.set_ylabel('Average Metascore')
ax2.set_ylabel('Total Review Count')
ax1.set_xlabel('Year Interval')
ax1.set_title('Critical Reception by 5-Year Intervals')

# Annotate the bars with the average Metascores
for i, (x, y) in enumerate(zip(avg_metascore_reviews_by_interval.index, avg_metascore_reviews_by_interval['Metascore'])):
    ax1.text(i, y + 0.5, f'{int(y)}', color='black', ha='center')

# Annotate the line with the total review count
for i, (x, y) in enumerate(zip(avg_metascore_reviews_by_interval.index, avg_metascore_reviews_by_interval['Review Count'])):
    ax2.text(i, y, f'{int(y)}', color='red', ha='center')

st.pyplot(fig)

# Additional chart for the top genre by 5-Year Intervals
st.subheader(f'{top_genre} Genre: Ratings and Reviews by 5-Year Intervals')
st.write(f"""
Let's dive deeper into the {top_genre}, which is Nic's most dominant genre and see how the ratings and reviews evolved over 5-year intervals.
""")

top_genre_movies = unique_movies[unique_movies['Genre'] == top_genre]
avg_rating_reviews_by_interval = top_genre_movies.groupby('Year Interval').agg({'Rating': 'mean', 'Review Count': 'sum'}).dropna()

# Filter for the last 30 years
avg_rating_reviews_by_interval = avg_rating_reviews_by_interval[avg_rating_reviews_by_interval.index >= current_year - 30]
avg_metascore_reviews_by_interval = avg_metascore_reviews_by_interval[avg_metascore_reviews_by_interval.index <= current_year]

fig, ax1 = plt.subplots()
sns.barplot(x=avg_rating_reviews_by_interval.index.astype(str), y=avg_rating_reviews_by_interval['Rating'], ax=ax1, palette='viridis')
ax2 = ax1.twinx()
sns.lineplot(x=avg_rating_reviews_by_interval.index.astype(str), y=avg_rating_reviews_by_interval['Review Count'], ax=ax2, color='red', marker='o', linestyle='-', linewidth=2)

ax1.set_ylabel('Average Rating')
ax2.set_ylabel('Total Review Count')
ax1.set_xlabel('Year Interval')
ax1.set_title(f'{top_genre} Genre: Ratings and Reviews by 5-Year Intervals')

# Annotate the bars with the average ratings
for i, (x, y) in enumerate(zip(avg_rating_reviews_by_interval.index, avg_rating_reviews_by_interval['Rating'])):
    ax1.text(i, y + 0.1, f'{y:.1f}', color='black', ha='center')

# Annotate the line with the total review count
for i, (x, y) in enumerate(zip(avg_rating_reviews_by_interval.index, avg_rating_reviews_by_interval['Review Count'])):
    ax2.text(i, y, f'{int(y)}', color='red', ha='center')

st.pyplot(fig)
