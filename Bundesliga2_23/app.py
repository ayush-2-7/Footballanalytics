import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

# Load data
df_discipline = pd.read_csv('discipline.csv', header=1)
df_player_stat = pd.read_csv('player_stat.csv').dropna()
df_nationalities = pd.read_csv('nationalities.csv')
df_fixtures = pd.read_csv('fixtures.csv')
df_table = pd.read_csv('table.csv')

# Title of the dashboard
st.title('Football Analytics Dashboard')

# Sidebar navigation
st.sidebar.title("Navigation")
navigation = st.sidebar.radio("Go to",
                              ["Standings",
                               "Discipline Data",
                               "Player Statistics",
                               "Nationalities",
                               "Fixtures",
                               "League Table",
                               "Top Scorers",
                               "Nationality Distribution",
                               "Goal Contribution",
                               "Radar Chart"])

# Define a color theme
color_theme = px.colors.qualitative.Dark24

# Display selected page
if navigation == "Standings":
    st.header('League Standings')

    # Display the league table
    st.subheader('League Table')
    st.dataframe(df_table)

    # Filter teams
    teams = df_table['Team'].unique()
    selected_teams = st.multiselect('Select teams to display', teams, default=teams)

    # Filter the dataframe based on selected teams
    filtered_df = df_table[df_table['Team'].isin(selected_teams)]

    # Visualize GF vs xG
    st.subheader('GF vs xG')
    fig_gf_xg = px.bar(filtered_df, x='Team', y=['GF', 'xG'], barmode='group',
                       labels={'value': 'Goals', 'variable': 'Metrics'},
                       title='Goals For (GF) vs Expected Goals (xG)',
                       color_discrete_sequence=color_theme)
    st.plotly_chart(fig_gf_xg)

    # Visualize GA vs xGA
    st.subheader('GA vs xGA')
    fig_ga_xga = px.bar(filtered_df, x='Team', y=['GA', 'xGA'], barmode='group',
                        labels={'value': 'Goals Against', 'variable': 'Metrics'},
                        title='Goals Against (GA) vs Expected Goals Against (xGA)',
                        color_discrete_sequence=color_theme)
    st.plotly_chart(fig_ga_xga)

    # Visualize GD vs xGD
    st.subheader('GD vs xGD')
    filtered_df['GD'] = filtered_df['GF'] - filtered_df['GA']
    filtered_df['xGD'] = filtered_df['xG'] - filtered_df['xGA']
    fig_gd_xgd = px.bar(filtered_df, x='Team', y=['GD', 'xGD'], barmode='group',
                        labels={'value': 'Goal Difference', 'variable': 'Metrics'},
                        title='Goal Difference (GD) vs Expected Goal Difference (xGD)',
                        color_discrete_sequence=color_theme)
    st.plotly_chart(fig_gd_xgd)

elif navigation == "Discipline Data":
    st.header('Discipline Data')

    # Calculate the total number of yellow and red cards for each club
    discipline_by_club = df_discipline.groupby('Squad')[['CrdY', 'CrdR']].sum().reset_index()

    # Calculate a total discipline score for each club (sum of yellow and red cards)
    discipline_by_club['DisciplineScore'] = discipline_by_club['CrdY'] + discipline_by_club['CrdR']

    # Create a treemap
    fig = px.treemap(discipline_by_club,
                     path=['Squad'],
                     values='DisciplineScore',
                     title='Club Discipline - Treemap',
                     labels={'Squad': 'Club', 'DisciplineScore': 'Discipline Score'},
                     color_discrete_sequence=color_theme)

    # Customize the layout for better readability
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=30))

    # Display the treemap
    st.plotly_chart(fig)

elif navigation == "Player Statistics":
    st.header('Player Statistics')
    st.dataframe(df_player_stat.head())

elif navigation == "Nationalities":
    st.header('Nationalities')

    # Create a choropleth map
    fig = px.choropleth(df_nationalities,
                        locations="Nation",
                        locationmode='country names',
                        color="# Players",
                        hover_name="Nation",
                        color_continuous_scale=px.colors.sequential.Plasma,
                        title='Player Distribution Around the World')

    # Customize the layout to hide the color bar
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=30), coloraxis_showscale=False)

    # Display the choropleth map
    st.plotly_chart(fig)

elif navigation == "Fixtures":
    st.header('Fixtures')

    # Dropdown filter for week
    weeks = df_fixtures['Wk'].unique()
    selected_week = st.selectbox('Select week', weeks)

    # Filter dataframe based on selected week
    filtered_fixtures = df_fixtures[df_fixtures['Wk'] == selected_week]

    # Display the filtered dataframe
    st.dataframe(filtered_fixtures)

elif navigation == "League Table":
    st.header('League Table')
    st.dataframe(df_table.head())

elif navigation == "Top Scorers":
    st.header('Top Scorers')

    # Extract top scorers
    top_scorers = df_player_stat[['Player', 'Gls']].sort_values(by='Gls', ascending=False).head(10)

    # Plotting the top scorers
    fig, ax = plt.subplots()
    ax.barh(top_scorers['Player'], top_scorers['Gls'], color=color_theme[0])
    ax.set_xlabel('Goals')
    ax.set_ylabel('Player')
    ax.set_title('Top 10 Goal Scorers')
    plt.gca().invert_yaxis()  # To display the highest scorer on top
    st.pyplot(fig)

elif navigation == "Nationality Distribution":
    st.header('Nationality Distribution')

    # Extract nationality distribution
    nationality_counts = df_nationalities['Nationality'].value_counts()

    # Plotting the nationality distribution
    fig, ax = plt.subplots()
    ax.pie(nationality_counts, labels=nationality_counts.index, autopct='%1.1f%%', startangle=90, colors=color_theme)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.set_title('Nationality Distribution of Players')
    st.pyplot(fig)

elif navigation == "Goal Contribution":
    st.header('Goal Contribution')

    # Calculate a metric for goal contribution (e.g., goals + assists)
    df_player_stat['GoalContribution'] = df_player_stat['Gls'] + df_player_stat['Ast']

    # Select the top 20 players based on goal contribution
    top_players = df_player_stat.nlargest(20, 'GoalContribution')

    # Create a scatterplot with size corresponding to goal contribution
    fig = px.scatter(top_players, x='Ast', y='Gls', size='GoalContribution',
                     labels={'Ast': 'Number of Assists', 'Gls': 'Number of Goals'},
                     title='Scatterplot: Top 20 Players - Goal Contribution',
                     hover_name='Player',
                     color_discrete_sequence=color_theme)

    # Customize the layout for better readability
    fig.update_traces(marker=dict(line=dict(width=2, color='DarkSlateGray')), selector=dict(mode='markers'))

    # Display the scatterplot
    st.plotly_chart(fig)

elif navigation == "Radar Chart":
    st.header('Player Comparison - Radar Chart')

    # Sort players by 'Gls' in descending order
    sorted_players = df_player_stat.sort_values(by='Gls', ascending=False)['Player'].unique()
    selected_players = st.multiselect('Select players to compare', sorted_players, default=sorted_players[:2])

    # Filter dataframe based on selected players
    filtered_players = df_player_stat[df_player_stat['Player'].isin(selected_players)]

    # Parameters for the radar chart
    radar_params = ['Gls', 'Ast', 'G+A', 'G-PK', 'xG', 'PrgP']

    # Create the radar chart
    fig = go.Figure()

    for player in selected_players:
        player_data = filtered_players[filtered_players['Player'] == player]
        fig.add_trace(go.Scatterpolar(
            r=player_data[radar_params].values.flatten().tolist(),
            theta=radar_params,
            fill='toself',
            name=player
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, filtered_players[radar_params].max().max()]
            )),
        showlegend=True,
        title='Player Comparison'
    )

    # Display the radar chart
    st.plotly_chart(fig)


