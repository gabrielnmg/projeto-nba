from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd

# Buscar os últimos jogos da NBA
gamefinder = leaguegamefinder.LeagueGameFinder()
games = gamefinder.get_data_frames()[0]

# Filtrar apenas os jogos da temporada 2024-25
games = games[games['SEASON_ID'] == '22024']  # Temporada 2024-25

# Exibir as primeiras linhas do DataFrame
print(games.head())
