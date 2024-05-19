import streamlit as st
import pandas as pd
import re
import plotly.express as px

df_matches = pd.read_csv('matches.csv')
df_deliveries = pd.read_csv('deliveries.csv')

# preprocessing the 'matches' dataset
df_matches['season'].replace(to_replace={
    re.compile(r'2007/08'): '2008',
    re.compile(r'2009/10'): '2010',
    re.compile(r'2020/21'): '2020'
}, inplace=True, regex=True)

df_matches['season'] = df_matches['season'].astype('int64')
df_matches['date'] = pd.to_datetime(df_matches['date'])

df_matches['super_over'] = df_matches['super_over'].replace('Y', 1)
df_matches['super_over'] = df_matches['super_over'].replace('N', 0)

# How many runs are scored in each IPL Season from IPL 2008 to 2023
def scored_runs(year, df_matches):
    sum_of_target_runs = df_matches[df_matches['season'] == year]['target_runs'].sum()
    rows = df_matches[(df_matches['season'] == year) & (df_matches['result'] == 'runs')]
    result_margin = rows['target_runs'] - rows['result_margin']
    
    total_runs = sum_of_target_runs + result_margin.sum()
    return total_runs


# How many total wickets have been fallen of during all IPL seasons
def total_wickets(year, df_deliveries, df_matches):
    ids_of_matches_in_a_season = df_matches[df_matches['season'] == year]['id']
    total_wickets_in_season = 0  # Initialize the total wickets count for the season
    for i in ids_of_matches_in_a_season:
        wickets_in_session = df_deliveries[(df_deliveries['match_id'] == i) & (df_deliveries['is_wicket'] == 1)].shape[0]
        total_wickets_in_season += wickets_in_session  # Accumulate the wickets for the season
    return total_wickets_in_season


# How winning the toss would lead to winn ing the match (correlation)
dataframe = pd.DataFrame(columns=['Matches', 'Quantity'])

for i in range(1024):
    dataframe.loc[i, 'Matches'] = f'Match{i}'

def create_dataframe(df_matches):
    for i in range(len(df_matches)):
        if df_matches.iloc[i]['toss_winner'] == df_matches.iloc[i]['winner']:
            dataframe.loc[i, 'Quantity'] = 1
        else:
            dataframe.loc[i, 'Quantity'] = 0
    return dataframe

# Best Bowling Team for a particular year
def best_batting_team(year, df_matches):
    total_runs = df_matches[(df_matches['season'] == year) & (df_matches['toss_decision'] == 'bat')].groupby('toss_winner')['target_runs'].sum()
    return total_runs

# Best Bowling Team for a particular year
wickets_for_all_teams = []
def best_bowling_team(year, df_matches, df_deliveries):
    ids_for_a_year = df_matches[df_matches['season'] == year]['id']
    
    for i in ids_for_a_year:
        wickets_for_1st_innings = df_deliveries[(df_deliveries['match_id'] == i) & (df_deliveries['inning'] == 1)].groupby('bowling_team')['is_wicket'].sum()
        wickets_for_2nd_innings = df_deliveries[(df_deliveries['match_id'] == i) & (df_deliveries['inning'] == 2)].groupby('bowling_team')['is_wicket'].sum()
        
        wickets_for_all_teams.append((wickets_for_1st_innings, wickets_for_2nd_innings))
    
    return wickets_for_all_teams

# Top 15 Best Batsman for selected season
batters = []
def best_batsman_over_season(year, df_matches, df_deliveries):
    ids_for_a_year = df_matches[df_matches['season'] == year]['id']
    for i in ids_for_a_year:
        batters_for_1st_innings = df_deliveries[(df_deliveries['match_id'] == i) & (df_deliveries['inning'] == 1)].groupby('batter')['batsman_runs'].sum()
        batters_for_2nd_innings = df_deliveries[(df_deliveries['match_id'] == i) & (df_deliveries['inning'] == 2)].groupby('batter')['batsman_runs'].sum()
        
        batters.append((batters_for_1st_innings, batters_for_2nd_innings))
    
    return batters

# Top 15 Best Bowlers for a selected season
bowlers_data = []
def best_bowlers_of_a_season(year, df_matches, df_deliveries):
    id_of_matches_of_seasons = df_matches[df_matches['season'] == year]['id']
    for i in id_of_matches_of_seasons:
        wickets_for_1st_innings = df_deliveries[(df_deliveries['match_id'] == i) & (df_deliveries['inning'] == 1)].groupby('bowler')['is_wicket'].sum()
        wickets_for_2nd_innings = df_deliveries[(df_deliveries['match_id'] == i) & (df_deliveries['inning'] == 2)].groupby('bowler')['is_wicket'].sum()
        
        bowlers_data.append((wickets_for_1st_innings, wickets_for_2nd_innings))
        
    return bowlers_data

# Match Wise Analysis
def match_wise_analysis(year, match_no, df_matches):
    match_data = pd.DataFrame(df_matches[df_matches['season'] == year].iloc[match_no])
    match_data = match_data.iloc[[2, 3, 4, 5, 6, 7, 8, 9, 10, 11], :]
    match_data.columns = [['Specifications']]
    match_data.reset_index(inplace=True)
    match_data.columns = ['Specifications', 'Details']

    return match_data

# st.title('IPL Data Analytics')

st.sidebar.header('IPL Data Analytics (2008-2023)')
user_menu = st.sidebar.radio(
    'Select an Option',
    ('Overall Analysis','Team-wise Analysis','Player wise Analysis', 'Match Analysis')
)

if user_menu == "Overall Analysis":
    st.title('Overall IPL Analysis')
    
    # We are showing here, how many total runs are scored in every season
    st.header('Total Runs Scored in Each IPL Season (Both Innings)')
    total_runs_per_season = {}

    for year in range(2008, 2024):
        total_runs_per_season[year] = scored_runs(year, df_matches)
        
    print(total_runs_per_season)

    df_total_runs_per_season = pd.DataFrame(total_runs_per_season.items(), columns=['Season', 'Total Runs'])
    fig = px.line(df_total_runs_per_season, x='Season', y='Total Runs', title='Total Runs Scored in Each IPL Season')
    st.plotly_chart(fig)

    # How many total wickets have been fallen of during all IPL seasons
    st.header('Total Wickets in all IPL Sessions (Both Innings)')
    total_wickets_in_all_sessions = {}

    for year in range(2008, 2024):
        total_wickets_in_all_sessions[year] = total_wickets(year, df_deliveries, df_matches)
    total_wickets_in_all_sessions = pd.DataFrame(total_wickets_in_all_sessions.items(), columns=['Year', 'No. of Wickets'])

    fig4 = px.line(total_wickets_in_all_sessions, x='Year', y='No. of Wickets', title='Total No. of wickets in all sessions')
    st.plotly_chart(fig4)
    
    # Here, we are accessing, most famous cities where these matches are happening.
    st.header('No. of time a match happened in a city')

    total_cities = pd.DataFrame(df_matches['city'].value_counts().items(), columns=['City', 'No.of times'])
    fig2 = px.bar(total_cities, x='No.of times', y='City', title='No. of time a match happened in a city')
    st.plotly_chart(fig2)

    # Here, we are accessing, most famous grounds where these matches are happening.
    st.header('No. of time a match happened in a ground')

    filtered_venues = df_matches['venue'].value_counts() > 15
    venue_value_counts_filtered = df_matches['venue'].value_counts()[filtered_venues]

    total_grounds = pd.DataFrame(venue_value_counts_filtered.items(), columns=['Venue', 'No.of times'])
    fig3 = px.bar(total_grounds, x='No.of times', y='Venue', title='No. of time a match happened in a ground')
    st.plotly_chart(fig3)

    # Correlation of Winning the toss with winning the match
    st.header('Correlation of Winning the toss with winning the match')
    toss_with_win = create_dataframe(df_matches)
    fig4 = px.bar(toss_with_win, x='Quantity', y='Matches', title='Correlation of Winning the toss with winning the match')
    st.plotly_chart(fig4)

elif user_menu == 'Team-wise Analysis':
    st.title('Team-wise Analysis')

    st.header('All IPL Finals from 2008 to 2023')
    ipl_finals = df_matches[df_matches['match_type'] == 'Final'][['season', 'winner']]
    st.table(ipl_finals)

    selected_season = st.sidebar.selectbox('Select the Season', df_matches['season'].unique())

    # Best Batting Team for a particular year
    st.header(f'Best Batting Teams for {selected_season}')
    total_runs = best_batting_team(selected_season, df_matches)
    st.bar_chart(total_runs)

    # Best Bowling Team for a particular year
    st.header(f'Best Bowling Teams for {selected_season}')
    new_data = best_bowling_team(selected_season, df_matches, df_deliveries)

    cleaned_data = []

    for pair in new_data:
        for index, row in pair[0].items():
            cleaned_data.append((index, row))
        for index, row in pair[1].items():
            cleaned_data.append((index, row))

    data = pd.DataFrame(cleaned_data, columns=[['Team Name', 'Wickets']])

    data.columns = data.columns.get_level_values(0)
    data = data.groupby(('Team Name'))['Wickets'].sum()

    st.bar_chart(data)

    # Number of times a team has won the matches
    st.header('No, of times a team has won the matches (2008 to 2023)')
    new_data = df_matches['winner'].value_counts()
    st.bar_chart(new_data)

elif user_menu == 'Player wise Analysis':
    st.title('Player Wise Analysis')

    st.header('Player of the Match (2008 to 2023)')
    filtered_data = df_matches['player_of_match'].value_counts() > 10
    player_of_matches = df_matches['player_of_match'].value_counts()[filtered_data]
    st.bar_chart(player_of_matches)

    # Top 15 Best Batsman for selected season
    selected_year = st.sidebar.selectbox('Select a Season', df_matches['season'].unique())

    new_data = best_batsman_over_season(selected_year, df_matches, df_deliveries)

    cleaned_data = []

    for pair in new_data:
        for index, row in pair[0].items():
            cleaned_data.append((index, row))
        for index, row in pair[1].items():
            cleaned_data.append((index, row))

    data = pd.DataFrame(cleaned_data, columns=[['Player Name', 'Runs']])
    data.columns = [col[0] for col in data.columns]

    grouped_data = data.groupby('Player Name')['Runs'].sum().reset_index()
    grouped_data = grouped_data.sort_values('Runs', ascending=False)
    grouped_data = grouped_data.iloc[0:16, :]

    st.header(f'Top 15 Best Batsman for {selected_year} season')
    st.table(grouped_data)

    # Top 15 Best Bowlers for a selected season
    new_data2 = best_bowlers_of_a_season(selected_year, df_matches, df_deliveries)

    cleaned_data2 = []

    for pair in new_data2:
        for index, row in pair[0].items():
            cleaned_data2.append((index, row))
        for index, row in pair[1].items():
            cleaned_data2.append((index, row))

    data = pd.DataFrame(cleaned_data2, columns=[['Player Name', 'Wickets']])
    data.columns = [col[0] for col in data.columns]

    grouped_data = data.groupby('Player Name')['Wickets'].sum().reset_index()
    grouped_data = grouped_data.sort_values('Wickets', ascending=False)
    grouped_data = grouped_data.iloc[0:16, :]

    st.header(f'Top 15 Best Bowlers for {selected_year} season')
    st.table(grouped_data)

    #Top 15 Bowlers with Lowest Economy (2008 - 2023)
    bowling_data = df_deliveries[['bowler', 'total_runs']]
    balls_a_baller_has_throwen = pd.DataFrame(bowling_data['bowler'].value_counts())

    imp_data = pd.DataFrame(bowling_data.groupby('bowler')['total_runs'].sum())
    new_data = balls_a_baller_has_throwen.merge(imp_data, on='bowler')

    new_data['overs_bowled'] = new_data['count'] / 6
    new_data['economy'] = new_data['total_runs'] / new_data['overs_bowled']

    filtered_data = new_data[new_data['count'] > 1000]
    filtered_data.reset_index(inplace=True)

    data = filtered_data[['bowler', 'economy']]
    data = data.sort_values('economy')
    data = data.iloc[0:16, :]

    st.header('Top 15 Bowlers with Lowest Economy (2008 - 2023)')
    st.table(data)

elif user_menu == 'Match Analysis':
    st.title('Match Analysis')

    selected_year = st.sidebar.selectbox('Select a Season', df_matches['season'].unique())
    total_matches_played = len(df_matches[df_matches['season'] == selected_year])

    all_match_no = []
    for i in range(total_matches_played):
        all_match_no.append(i)

    selected_match_no = st.sidebar.selectbox('Select the Mstch Number', all_match_no)

    match_data = match_wise_analysis(selected_year, selected_match_no, df_matches)
    st.table(match_data)


# So, guys, here is our IPL Analytical Web App, Now, we just have to deploy it on render or any other hosting platform.