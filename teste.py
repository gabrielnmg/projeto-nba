import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
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

# Função para atualizar o time do jogador selecionado
def update_player_team(event):
    selected_player_name = player_combobox.get()

    # Encontrar o time do jogador selecionado
    selected_player_team = None
    for player in active_players:
        if player['full_name'] == selected_player_name:
            selected_player_team = player['team']
            break
    
    if selected_player_team:
        player_team_label.config(text=f"Time: {selected_player_team}")

# Função para exibir resultados com base no jogador escolhido
def display_results():
    selected_player_name = player_combobox.get()
    selected_stat = stat_combobox.get()
    comparison_value = comparison_combobox.get()

    # Verificar se um número de comparação foi selecionado
    if not comparison_value:
        messagebox.showerror("Erro", "Por favor, selecione um número para comparação.")
        return

    # Converter o número selecionado para inteiro
    comparison_value = int(comparison_value)

    # Encontrar o ID do jogador selecionado e o time
    selected_player_id = None
    selected_player_team = None
    for player in active_players:
        if player['full_name'] == selected_player_name:
            selected_player_id = player['id']
            selected_player_team = player['team']
            break
    
    if not selected_player_id:
        result_label.config(text="Jogador não encontrado.")
        return

    # Atualizar o campo que mostra o time do jogador
    player_team_label.config(text=f"Time: {selected_player_team}")

    # Buscar os últimos 10 jogos do jogador
    gamelog = playergamelog.PlayerGameLog(player_id=selected_player_id, season='2024-25')
    games = gamelog.get_data_frames()[0].head(10)  # Últimos 10 jogos

    # Verificar as colunas para garantir o nome correto das estatísticas
    print("Colunas do DataFrame:", games.columns)  # Imprime as colunas para inspeção

    # Filtrar os resultados pela estatística selecionada
    if selected_stat == "REB":
        stats_column = "REB"
    elif selected_stat == "AST":
        stats_column = "AST"

    # Criar uma nova janela para exibir os resultados
    results_window = tk.Toplevel(root)
    results_window.title(f"Resultados de {selected_player_name}")

    # Criar uma Treeview (tabela) para exibir os resultados
    treeview = ttk.Treeview(results_window, columns=("Data", "Estatística", "Partida", "Resultado"), show="headings")
    treeview.pack(fill=tk.BOTH, expand=True)

    # Definir as colunas da tabela
    treeview.heading("Data", text="Data")
    treeview.heading("Estatística", text=f"{selected_stat}")
    treeview.heading("Partida", text="Partida")
    treeview.heading("Resultado", text="Resultado")

    # Variável para verificar se todos os jogos estão dentro da análise
    all_games_in_analysis = True

    # Preencher a tabela com os resultados
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
        
        # Definir se o jogo está dentro ou fora da análise
        result_text = "Dentro da análise" if game_stat >= comparison_value else "Fora da análise"
        
        if game_stat < comparison_value:
            all_games_in_analysis = False  # Se algum jogo não atender ao critério, altera a variável

        # Inserir os dados na tabela
        treeview.insert("", "end", values=(game_date, game_stat, f"{home_team} x {away_team}", result_text))

    # Adicionar o resultado final ao final da tabela
    result_label_text = "Resultado final: Dentro da análise" if all_games_in_analysis else "Resultado final: Fora da análise"
    
    result_label = tk.Label(results_window, text=result_label_text, fg="green" if all_games_in_analysis else "red")
    result_label.pack()

# Função para filtrar jogadores conforme digitação
def filter_players(event):
    search_term = player_search_var.get().lower()
    filtered_players = [player for player in active_players if search_term in player['full_name'].lower()]
    player_combobox['values'] = [player['full_name'] for player in filtered_players]

# Criando a janela principal com Tkinter
root = tk.Tk()
root.title("NBA Player Stats")

# Obter jogadores ativos
active_players = get_active_players()

# Criar variável para armazenar o texto digitado na busca
player_search_var = tk.StringVar()

# Criar campo de pesquisa de jogadores
player_search_label = tk.Label(root, text="Digite o nome do jogador:")
player_search_label.pack()

player_search_entry = tk.Entry(root, textvariable=player_search_var)
player_search_entry.pack()
player_search_entry.bind('<KeyRelease>', filter_players)  # Filtra a lista enquanto digita

# Criar o campo de seleção de jogador
player_names = [player['full_name'] for player in active_players]
player_combobox = ttk.Combobox(root, values=player_names)
player_combobox.pack()
player_combobox.bind("<<ComboboxSelected>>", update_player_team)  # Atualiza o time quando um jogador é selecionado

# Label para exibir o time do jogador
player_team_label = tk.Label(root, text="Time: Nenhum jogador selecionado")
player_team_label.pack()

# Criar o campo de seleção de estatística
stat_label = tk.Label(root, text="Selecione a estatística (REB ou AST):")
stat_label.pack()

stat_combobox = ttk.Combobox(root, values=["REB", "AST"])
stat_combobox.pack()

# Criar o campo para a lista suspensa de comparação (2 ou 3)
comparison_label = tk.Label(root, text="Selecione o número para comparação:")
comparison_label.pack()

comparison_combobox = ttk.Combobox(root, values=["2", "3"])
comparison_combobox.pack()

# Botão para exibir os resultados
search_button = tk.Button(root, text="Mostrar Resultados", command=display_results)
search_button.pack()

# Iniciar a aplicação Tkinter
root.mainloop()
