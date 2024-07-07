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

# Clean data
df_table = df_table.loc[:, ~df_table.columns.str.contains('^Unnamed')]
df_fixtures = df_fixtures.loc[:, ~df_fixtures.columns.str.contains('^Unnamed')]
df_fixtures["Wk"] = df_fixtures["Wk"].astype(int)

# Title of the dashboard
st.title('Football Analytics Dashboard')

# Sidebar navigation
st.sidebar.title("Statistics")
navigation = st.sidebar.selectbox("Go to",
                                  ["Standings",
                                   "Fixtures",
                                   "Nationality Distribution",
                                   "Discipline Data",
                                   "Player Dictionary",
                                   "Top Performers (Offensive)",
                                   "Goal Contribution"])

# Define a color theme
color_theme = px.colors.qualitative.Dark24

# Display selected page
if navigation == "Standings":
    st.header('League Standings')

    # Display the league table
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

elif navigation == "Player Dictionary":
    st.header('Player Dictionary')

    selected_player = st.selectbox('Select a player', df_player_stat['Player'].unique())

    if selected_player:
        player_data = df_player_stat[df_player_stat['Player'] == selected_player].iloc[0]
        st.write(f"**Name:** {player_data['Player']}")
        st.write(f"**Position:** {player_data['Pos']}")
        st.write(f"**Country:** {player_data['Nation']}")
        st.write(f"**Age:** {player_data['Age']}")
        st.write(f"**Team:** {player_data['Squad']}")
        st.write(f"**Goals:** {player_data['Gls']}")
        st.write(f"**Assists:** {player_data['Ast']}")
        st.write(f"**Goals + Assists:** {player_data['G+A']}")
        st.write(f"**Non-Penalty Goals:** {player_data['G-PK']}")
        st.write(f"**Expected Goals (xG):** {player_data['xG']}")
        st.write(f"**Progressive Passes:** {player_data['PrgP']}")
elif navigation == "Fixtures":
    st.header('Fixtures')

    # Dropdown filter for week
    weeks = df_fixtures['Wk'].unique()
    selected_week = st.selectbox('Select week', weeks)

    # Filter dataframe based on selected week
    filtered_fixtures = df_fixtures[df_fixtures['Wk'] == selected_week]

    # Display the filtered dataframe
    st.dataframe(filtered_fixtures)

elif navigation == "Top Performers (Offensive)":
    st.header('Top Performers (Offensive)')

    # Extract top scorers
    top_scorers = df_player_stat[['Player', 'Gls']].sort_values(by='Gls', ascending=False).head(10)

    # Plotting the top scorers
    fig, ax = plt.subplots()
    ax.barh(top_scorers['Player'], top_scorers['Gls'], color=color_theme[0])
    for i in ax.patches:
        ax.text(i.get_width() + 0.2, i.get_y() + i.get_height()/2, str(i.get_width()), ha='center', va='center')
    ax.set_xlabel('Goals')
    ax.set_ylabel('Player')
    ax.set_title('Top 10 Goal Scorers')
    plt.gca().invert_yaxis()  # To display the highest scorer on top
    st.pyplot(fig)

    # Extract top assist providers
    top_assists = df_player_stat[['Player', 'Ast']].sort_values(by='Ast', ascending=False).head(10)

    # Plotting the top assist providers
    fig, ax = plt.subplots()
    ax.barh(top_assists['Player'], top_assists['Ast'], color=color_theme[1])
    for i in ax.patches:
        ax.text(i.get_width() + 0.2, i.get_y() + i.get_height()/2, str(i.get_width()), ha='center', va='center')
    ax.set_xlabel('Assists')
    ax.set_ylabel('Player')
    ax.set_title('Top 10 Assist Providers')
    plt.gca().invert_yaxis()
    st.pyplot(fig)

    # Extract top players with most xG
    top_xg = df_player_stat[['Player', 'xG']].sort_values(by='xG', ascending=False).head(10)

    # Plotting the top players with most xG
    fig, ax = plt.subplots()
    ax.barh(top_xg['Player'], top_xg['xG'], color=color_theme[2])
    for i in ax.patches:
        ax.text(i.get_width() + 0.2, i.get_y() + i.get_height()/2, str(i.get_width()), ha='center', va='center')
    ax.set_xlabel('xG')
    ax.set_ylabel('Player')
    ax.set_title('Top 10 Players with Most xG')
    plt.gca().invert_yaxis()
    st.pyplot(fig)

    # Extract top players with most penalties scored
    top_pk = df_player_stat[['Player', 'PK']].sort_values(by='PK', ascending=False).head(10)

    # Plotting the top players with most penalties scored
    fig, ax = plt.subplots()
    ax.barh(top_pk['Player'], top_pk['PK'], color=color_theme[3])
    for i in ax.patches:
        ax.text(i.get_width() + 0.2, i.get_y() + i.get_height() / 2, str(i.get_width()), ha='center', va='center')
    ax.set_xlabel('Penalties')
    ax.set_ylabel('Player')
    ax.set_title('Top 10 Players with Most Penalties Scored')
    plt.gca().invert_yaxis()
    st.pyplot(fig)

elif navigation == "Nationality Distribution":
    st.header('Nationality Distribution')

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
    fig.update_traces(showlegend=False)
    # Display the choropleth map
    st.plotly_chart(fig)

elif navigation == "Goal Contribution":
    st.header('Goal Contribution')

    # Calculate a metric for goal contribution (e.g., goals + assists)
    df_player_stat['GoalContribution'] = df_player_stat['Gls'] + df_player_stat['Ast']

    # Select the top 20 players based on goal contribution
    top_players = df_player_stat.nlargest(500, 'GoalContribution')

    # Create a scatterplot with size corresponding to goal contribution
    fig = px.scatter(top_players, x='Ast', y='Gls', size='GoalContribution',
                     labels={'Ast': 'Number of Assists', 'Gls': 'Number of Goals'},
                     hover_name='Player',
                     color_discrete_sequence=color_theme)

    # Customize the layout for better readability
    fig.update_traces(marker=dict(line=dict(width=2, color='DarkSlateGray')), selector=dict(mode='markers'))

    # Display the scatterplot
    st.plotly_chart(fig)