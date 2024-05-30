import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from imdb import IMDb, IMDbDataAccessError
from concurrent.futures import ThreadPoolExecutor
import asyncio
import aiohttp
import time

# Virtual environment setup instructions
st.sidebar.title('Setup Instructions')
st.sidebar.write("""
1. Create a virtual environment: `python -m venv env`
2. Activate the virtual environment: `source env/bin/activate` (Mac/Linux) or `env\\Scripts\\activate` (Windows)
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

# Validate movie years using IMDb asynchronously
async def validate_year(row, ia, session):
    title = row['Title']
    original_year = row['Year']
    try:
        movies = await ia.search_movie_async(title, session)
        if movies:
            for movie in movies:
                await ia.update_async(movie, session)
                if 'Nicolas Cage' in [person['name'] for person in movie.get('cast', [])]:
                    year = movie.get('year')
                    if year and year != original_year:
                        return year
    except (IMDbDataAccessError, Exception):
        pass
    return original_year

# Main async function to validate years
async def validate_years_async(df, max_time=25):
    validated_years = []
    start_time = time.time()
    progress_bar = st.progress(0)
    total = len(df)
    facts = [
        "He bought two king cobras, and this ended poorly. He was dismayed to find that the snakes kept trying to attack him, and then neighbors complained till he gave them up.",
        "He came to a fan's defense when Vince Neil attacked her. Attacked her physically, that is. Though, Cage may also have been doing this for Neil's sake.",
        "Cage chooses his diet based on animals' mating habits. He avoids pork, because he says pigs have dirty sex, but he eats fish and poultry, since fish and birds mate respectably.",
        "He really wants to do a musical. So we put together some choices for which one would suit him best.",
        "His healing hands saved a shooting victim. He was riding in an ambulance to prepare for his role as an EMT in Martin Scorsese's Bringing Out the Dead, then things got a little too real.",
        "He was the first choice to play Aragorn in Lord of the Rings.",
        "He lost a $100,000 treasure at sea. His fiancée, Lisa Marie Presley, chucked her engagement ring off his yacht, and divers never managed to retrieve it.",
        "An antiques dealer auctioned off 'proof' Cage is a vampire, for $1 million. This was a Civil War–era photo featuring someone who looked like Cage.",
        "Nicolas Cage was once bailed out of jail by Dog the Bounty Hunter. Police booked him after a drunken night in New Orleans, but the charges fortunately didn't stick.",
        "Bad Lieutenant featured a hallucinatory iguana, who bit director Werner Herzog. This was not in the screenplay, and it's debatable just why Herzog included this.",
        "Cage actually tried to find the Holy Grail. After traveling the world, he concluded that the grail only made sense as a metaphor.",
        "During the filming of Vampire's Kiss, he ate a cockroach for real.",
        "His comedy is sometimes intentional, and sometimes very much not. Consider the brilliant intentional comedy of Adaptation, and the also brilliant unintentional comedy of Face/Off.",
        "He's spent millions (to rehabilitate child soldiers). Not all his vanished money has gone to arcane relics. He's also known for giving a bunch to charity, including $2 million to Amnesty International.",
        "He crashed a Nicolas Cage film festival. He read Edgar Allan Poe to the audience, unprompted, then stayed to view five of his own movies back-to-back.",
        "He once did magic mushrooms with his cat. Said Cage, the cat kept raiding the fridge, so he decided they must do shrooms together, resulting in an hours-long shared trip."
    ]
    fact_placeholder = st.empty()

    async with aiohttp.ClientSession() as session:
        ia = IMDb(asyncio=True)
        tasks = [validate_year(row, ia, session) for _, row in df.iterrows()]

        for i, task in enumerate(asyncio.as_completed(tasks)):
            if time.time() - start_time > max_time:
                st.warning("Validation process stopped due to time constraints. Remaining values will use the original data.")
                break
            try:
                result = await task
            except (asyncio.TimeoutError, Exception):
                result = None
            fact = facts[i % len(facts)] if facts else "No fact available."
            fact_placeholder.info(f"Enjoy some Nic Cage's fun facts while I validate the data in IMDb: \n\n{fact}")
            validated_years.append(result if result is not None else df.iloc[i]['Year'])
            progress_bar.progress(len(validated_years) / total)
            await asyncio.sleep(8)  # To display facts for a while
            fact_placeholder.empty()

    df['Validated Year'] = validated_years
    df['Year'] = df['Validated Year'].combine_first(df['Year'])
    df.drop(columns=['Validated Year'], inplace=True)
    return df

# Create a new column for 5-year intervals
def create_year_intervals(df):
    df = df.dropna(subset=['Year'])
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
    df = load_data('imdb-movies-dataset.csv')
    df = clean_data(df)

    cage_movies = df[df['Cast'].str.contains('Nicolas Cage', case=False, na=False)].copy()
    
    start_time = time.time()
    cage_movies = asyncio.run(validate_years_async(cage_movies, max_time=20))
    end_time = time.time()
    st.success(f'Validation completed in {end_time - start_time:.2f} seconds.')

    cage_movies = create_year_intervals(cage_movies)
    decades, earliest_year, latest_year = calculate_decades(cage_movies)
    decade_text = f"{decades} decades" if decades != 4 else "4 decades"

    st.title(f'Nicolas Cage: A Journey Through Film Spanning {decade_text}')
    st.image("https://m.media-amazon.com/images/M/MV5BMzY5YTYwODAtZjY4Yi00OG
