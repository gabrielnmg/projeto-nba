import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

# Função para buscar jogadores ativos da NBA
def get_active_players():
    all_players = players.get_players()  # Obtém todos os jogadores registrados
    active_players = []
    for player in all_players:
        if player['is_active']:  # Filtra apenas jogadores ativos
            active_players.append({
                'id': player['id'],
                'full_name': player['full_name'],
                'team': player['team'] if 'team' in player else 'Desconhecido'  # Adiciona a informação do time
            })
    return active_players

# Função para exibir resultados com base no jogador escolhido
def display_results(selected_player_name, selected_stat, comparison_value):
    # Encontrar o ID do jogador selecionado e o time
    selected_player_id = None
    selected_player_team = None
    for player in active_players:
        if player['full_name'] == selected_player_name:
            selected_player_id = player['id']
            selected_player_team = player['team']
            break
    
    if not selected_player_id:
        st.error("Jogador não encontrado.")
        return

    # Atualizar o campo que mostra o time do jogador
    st.write(f"Time: {selected_player_team}")

    # Buscar os últimos 10 jogos do jogador
    gamelog = playergamelog.PlayerGameLog(player_id=selected_player_id, season='2024-25')
    games = gamelog.get_data_frames()[0].head(10)  # Últimos 10 jogos

    # Filtrar os resultados pela estatística selecionada
    if selected_stat == "REB":
        stats_column = "REB"
    elif selected_stat == "AST":
        stats_column = "AST"

    # Exibir os resultados
    st.write(f"Resultados para {selected_player_name} - Estatística: {selected_stat}")

    # Criar DataFrame para exibir como tabela
    results = []
    all_games_in_analysis = True

    for idx, game in games.iterrows():
        game_stat = game[stats_column]
        game_date = game['GAME_DATE']
        
        # Extrair os times da coluna 'MATCHUP', que tem o formato "TIME1 vs TIME2"
        matchup = game['MATCHUP']
        teams = matchup.split(" vs ") if " vs " in matchup else [matchup, ""]  # Verificar se existe "vs"
        
        if len(teams) == 2:
            home_team = teams[0]
            away_team = teams[1]
        else:
            home_team = teams[0]
            away_team = "Desconhecido"  # Caso não tenha o "vs" ou formato inesperado
        
        game_stat_color = "green" if game_stat >= comparison_value else "red"
        
        result_text = "Dentro da análise" if game_stat >= comparison_value else "Fora da análise"
        
        if game_stat < comparison_value:
            all_games_in_analysis = False  # Se algum jogo não atender ao critério, altera a variável

        results.append([game_date, game_stat, f"{home_team} x {away_team}", result_text])

    # Exibir a tabela de resultados
    results_df = pd.DataFrame(results, columns=["Data", "Estatística", "Partida", "Resultado"])
    st.write(results_df)

    # Adicionar o resultado final
    result_label_text = "Resultado final: Dentro da análise" if all_games_in_analysis else "Resultado final: Fora da análise"
    st.write(result_label_text)

# Obter jogadores ativos
active_players = get_active_players()

# Interface com o Streamlit
st.title("NBA Player Stats")

# Campo de seleção de jogador
selected_player_name = st.selectbox("Selecione o jogador", [player['full_name'] for player in active_players])

# Exibir o time do jogador selecionado
selected_player = next(player for player in active_players if player['full_name'] == selected_player_name)
st.write(f"Time: {selected_player['team']}")

# Campo de seleção de estatística
selected_stat = st.selectbox("Selecione a estatística", ["REB", "AST"])

# Campo de comparação (2 ou 3)
comparison_value = st.selectbox("Selecione o número para comparação", [2, 3])

# Botão para exibir os resultados
if st.button("Mostrar Resultados"):
    display_results(selected_player_name, selected_stat, comparison_value)
