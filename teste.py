import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd
import time

def get_active_players():
    all_players = players.get_players()
    return [player for player in all_players if player['is_active']]

def display_results(selected_player_name, selected_stat, comparison_value):
    selected_player_id = next((p['id'] for p in active_players if p['full_name'] == selected_player_name), None)
    if not selected_player_id:
        st.error("Jogador não encontrado.")
        return

    gamelog = playergamelog.PlayerGameLog(player_id=selected_player_id, season='2024-25')
    games = gamelog.get_data_frames()[0].head(10)
    stats_column = "REB" if "Rebotes" in selected_stat else "AST"
    
    results = []
    jogos_dentro = 0
    jogos_fora = 0
    
    ultimo_jogo = games.iloc[0] if not games.empty else None
    time_jogador = "Desconhecido"
    if ultimo_jogo is not None:
        time_jogador = ultimo_jogo['MATCHUP'].split()[0]

    for _, game in games.iterrows():
        game_stat = game[stats_column]
        game_date = game['GAME_DATE']
        matchup = game['MATCHUP']
        result_text = "Dentro da análise" if game_stat >= comparison_value else "Fora da análise"
        if game_stat >= comparison_value:
            jogos_dentro += 1
        else:
            jogos_fora += 1
        results.append([game_date, game_stat, matchup, result_text])
    
    results_df = pd.DataFrame(results, columns=["Data", "Estatística", "Partida", "Resultado"])
    
    st.write(f"**Resultados para {selected_player_name} ({time_jogador}) - Estatística: {selected_stat}**")
    st.write(f"**Resultado final: {'Dentro da análise' if jogos_fora == 0 else 'Fora da análise'}**")
    st.write(f"**Jogos dentro da análise:** {jogos_dentro}")
    st.write(f"**Jogos fora da análise:** {jogos_fora}")
    st.write(results_df)

# Obter jogadores ativos
active_players = get_active_players()

def reset_fields():
    st.session_state.selected_player_name = ""
    st.session_state.selected_stat = ""
    st.session_state.comparison_value = 2

if 'reset_page' not in st.session_state:
    st.session_state.reset_page = False

if st.session_state.reset_page:
    reset_fields()
    st.session_state.reset_page = False

selected_player_name = st.selectbox("Selecione o jogador", [""] + [p['full_name'] for p in active_players])
if selected_player_name:
    selected_stat = st.selectbox("Selecione a estatística", ["2+ Rebotes", "2+ Assistências", "3+ Rebotes", "3+ Assistências"])
    comparison_value = int(selected_stat.split("+")[0])
    st.session_state.update({"selected_player_name": selected_player_name, "selected_stat": selected_stat, "comparison_value": comparison_value})
    if st.button("Mostrar Resultados"):
        st.session_state.show_results = True

if st.session_state.get("show_results", False):
    if st.button("Recarregar a página"):
        reset_fields()
        st.session_state.show_results = False
        st.rerun()
    display_results(st.session_state.selected_player_name, st.session_state.selected_stat, st.session_state.comparison_value)
