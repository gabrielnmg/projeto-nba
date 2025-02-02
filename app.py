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
                'full_name': player['full_name']
            })
    return active_players

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

    # Encontrar o ID do jogador selecionado
    selected_player_id = None
    for player in active_players:
        if player['full_name'] == selected_player_name:
            selected_player_id = player['id']
            break
    
    if not selected_player_id:
        result_label.config(text="Jogador não encontrado.")
        return

    # Buscar os últimos 10 jogos do jogador
    gamelog = playergamelog.PlayerGameLog(player_id=selected_player_id, season='2024-25')
    games = gamelog.get_data_frames()[0].head(10)  # Últimos 10 jogos

    # Filtrar os resultados pela estatística selecionada
    if selected_stat == "REB":
        stats_column = "REB"
    elif selected_stat == "AST":
        stats_column = "AST"

    # Criar a tabela com os resultados e destacar conforme a comparação
    result_text = f"Últimos 10 jogos de {selected_player_name} - Estatísticas de {selected_stat}:\n\n"
    
    result_table = []
    all_games_in_analysis = True  # Variável para verificar se todos os jogos atendem ao critério
    for idx, game in games.iterrows():
        game_stat = game[stats_column]
        game_date = game['GAME_DATE']
        
        # Verificar se o valor da estatística atende ao critério de comparação
        if game_stat >= comparison_value:
            row_color = "green"
        else:
            row_color = "red"
            all_games_in_analysis = False  # Se algum jogo não atender, altera a variável
        
        # Adicionar a linha à tabela de resultados
        result_table.append((game_date, game_stat, row_color))

    # Exibir os resultados em uma tabela
    for i, (game_date, game_stat, color) in enumerate(result_table):
        result_text += f"Jogo {i + 1}: {game_date} - {game_stat} {selected_stat} "
        result_text += f"(Resultado: {'Dentro da análise' if color == 'green' else 'Fora da análise'})\n"
    
    # Adicionar o resumo final
    if all_games_in_analysis:
        result_text += "\nResultado final: Dentro da análise"
    else:
        result_text += "\nResultado final: Fora da análise"
    
    result_label.config(text=result_text)

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

# Label para exibir os resultados
result_label = tk.Label(root, text="")
result_label.pack()

# Iniciar a aplicação Tkinter
root.mainloop()
