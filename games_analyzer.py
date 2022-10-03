import pandas as pd
from ics import Calendar, Event, DisplayAlarm
from datetime import timedelta

games = pd.read_csv('games.csv')
teams = pd.read_csv('teams.csv')

full_games = games

for i, game in full_games.iterrows():
    full_games.loc[i, 'Entrata Palestra'] = teams.loc[teams.loc[:, 'Squadra'] == game['Squadra in casa'], 'Orario Entrata'].values[0]
    full_games.loc[i, 'Luogo'] = teams.loc[teams.loc[:, 'Squadra'] == game['Squadra in casa'], 'Palestra'].values[0].replace(u'\xa0', ' ') + ', ' + teams.loc[teams.loc[:, 'Squadra'] == game['Squadra in casa'], 'Luogo'].values[0].replace(u'\xa0', u' ')
    full_games.loc[i, 'Link'] = teams.loc[teams.loc[:, 'Squadra'] == game['Squadra in casa'], 'Link maps'].values[0]
    full_games.loc[i, 'Note'] = str(teams.loc[teams.loc[:, 'Squadra'] == game['Squadra in casa'], 'Note'].values[0]).replace(u'\xa0', u' ')

full_games['Datetime'] = full_games['Giorno'] + ' ' + full_games['Entrata Palestra']
full_games['Datetime'] = pd.to_datetime(full_games['Datetime'], format='%d.%m.%y %H:%M')
full_games['Datetime'] = full_games['Datetime'].dt.tz_localize('Europe/Zurich')

for team in set(teams['Squadra']):
    lcl_games = full_games.loc[(full_games.loc[:, 'Squadra in casa'] == team) | (full_games.loc[:, 'Squadra ospite'] == team), :]
    lcl_games = lcl_games.loc[lcl_games.loc[:, 'Squadra ospite'] != 'RIPOSO', :]

    calendar_name = 'output/' + team + '.ics'
    c = Calendar(creator='Dario Marvin')

    for r in lcl_games.iterrows():
        r = r[1]

        e = Event()

        e.name = 'Partita CAT ' + str(r['Partita']) + ': ' + r['Squadra in casa'] + ' vs ' + r['Squadra ospite']
        e.begin = r['Datetime']
        e.duration = timedelta(hours=4)
        e.location = r['Luogo'] + ', ' + r['Link']
        e.description = str(r['Note'])
        e.alarms = [DisplayAlarm(trigger=timedelta(hours=-24)), DisplayAlarm(trigger=timedelta(hours=-2))]

        c.events.add(e)

    with open(calendar_name, 'w') as my_file:
        my_file.writelines(c.serialize_iter())
