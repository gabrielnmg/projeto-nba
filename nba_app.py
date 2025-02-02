import streamlit as st
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playergamelog, playercareerstats
import pandas as pd
import time

# Função para obter o time do jogador a partir das últimas partidas
def get_player_team(player_id, retries=3):
    try:
        career_stats = playercareerstats.PlayerCareerStats(player_id=player_id, timeout=120)
        stats = career_stats.get_data_frames()[0]

        if stats.empty:
            return 'Desconhecido'

        team_name = stats.iloc[0]['TEAM_ABBREVIATION']
        all_teams = teams.get_teams()
        team_full_name = next((team['full_name'] for team in all_teams if team['abbreviation'] == team_name), 'Desconhecido')

        return team_full_name
    except Exception as e:
        print(f"Erro ao obter time do jogador: {e}")
        if retries > 0:
            print(f"Tentando novamente... ({3 - retries} de 3)")
            time.sleep(3)
            return get_player_team(player_id, retries - 1)
        else:
            return 'Desconhecido'

# Função para buscar jogadores ativos da NBA
def get_active_players():
    all_players = players.get_players()
    active_players = []
    for player in all_players:
        if player['is_active']:
            active_players.append({
                'id': player['id'],
                'full_name': player['full_name']
            })
    return active_players

# Função para exibir resultados com base no jogador escolhido
def display_results(selected_player_name, selected_stat, comparison_value):
    selected_player_id = None
    for player in active_players:
        if player['full_name'] == selected_player_name:
            selected_player_id = player['id']
            break
    
    if not selected_player_id:
        st.error("Jogador não encontrado.")
        return

    gamelog = playergamelog.PlayerGameLog(player_id=selected_player_id, season='2024-25')
    games = gamelog.get_data_frames()[0].head(10)

    stats_column = "REB" if "Rebotes" in selected_stat else "AST"
    st.write(f"**Resultados para {selected_player_name} - Estatística: {selected_stat}**")

    results = []
    all_games_in_analysis = True

    for idx, game in games.iterrows():
        game_stat = game[stats_column]
        game_date = game['GAME_DATE']
        matchup = game['MATCHUP']
        teams = matchup.split(" vs ") if " vs " in matchup else [matchup, ""]
        
        home_team = teams[0]
        away_team = teams[1] if len(teams) == 2 else "Desconhecido"
        
        result_text = "Dentro da análise" if game_stat >= comparison_value else "Fora da análise"
        if game_stat < comparison_value:
            all_games_in_analysis = False

        results.append([game_date, game_stat, f"{home_team} x {away_team}", result_text])

    results_df = pd.DataFrame(results, columns=["Data", "Estatística", "Partida", "Resultado"])
    
    # Exibe o resultado da análise acima do relatório
    result_label_text = "Resultado final: Dentro da análise" if all_games_in_analysis else "Resultado final: Fora da análise"
    st.write(result_label_text)
    
    # Exibe o DataFrame com os resultados
    st.write(results_df)

# Obter jogadores ativos
active_players = get_active_players()

# Função para resetar os campos
def reset_fields():
    st.session_state.selected_player_name = ""
    st.session_state.selected_stat = ""
    st.session_state.comparison_value = 2

# Verifica o estado de controle para saber se a página deve ser recarregada
if 'reset_page' not in st.session_state:
    st.session_state.reset_page = False

# Se for necessário, redefine os campos de seleção
if st.session_state.reset_page:
    reset_fields()  # Reseta os campos
    st.session_state.reset_page = False  # Reseta o controle de recarga

# Campo de jogador vazio no início
selected_player_name = st.selectbox("Selecione o jogador", [""] + [player['full_name'] for player in active_players])

# Verifica se foi selecionado um jogador
if selected_player_name:
    selected_player_id = next(player['id'] for player in active_players if player['full_name'] == selected_player_name)

    # Alterando o campo de estatísticas para incluir as opções de comparação
    stat_options = ["2+ Rebotes", "2+ Assistências", "3+ Rebotes", "3+ Assistências"]
    selected_stat = st.selectbox("Selecione a estatística", stat_options)

    # Agora, extrair o número de comparação (2 ou 3) da opção selecionada
    comparison_value = int(selected_stat.split("+")[0])

    # Salva os dados no session_state para persistir
    st.session_state.selected_player_name = selected_player_name
    st.session_state.selected_stat = selected_stat
    st.session_state.comparison_value = comparison_value

    if st.button("Mostrar Resultados"):
        display_results(selected_player_name, selected_stat, comparison_value)

# Adicionando botão para forçar o recarregamento da página
if st.button("Recarregar a página"):
    reset_fields()  # Limpa os campos de seleção
    st.session_state.reset_page = True
    st.rerun()  # Força o recarregamento da página
