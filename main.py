import shutil
import sqlite3
import csv
import os
from pathlib import Path
from datetime import datetime

# Configuração dos diretórios
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
BACKUP_DIR = BASE_DIR / 'backups'
EXPORT_DIR = BASE_DIR / 'exports'

# Criar diretórios se não existirem
DATA_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)
EXPORT_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / 'livraria.db'

def criar_conexao():
    return sqlite3.connect(DB_PATH)

def criar_tabela():
    conn = criar_conexao()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS livros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        autor TEXT NOT NULL,
        ano_publicacao INTEGER,
        preco REAL
    )
    ''')
    conn.commit()
    conn.close()

def adicionar_livro(titulo, autor, ano_publicacao, preco):
    conn = criar_conexao()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO livros (titulo, autor, ano_publicacao, preco) VALUES (?, ?, ?, ?)',
                   (titulo, autor, ano_publicacao, preco))
    conn.commit()
    conn.close()
    fazer_backup()

def exibir_livros():
    conn = criar_conexao()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM livros')
    livros = cursor.fetchall()
    conn.close()
    return livros

def atualizar_preco(id, novo_preco):
    conn = criar_conexao()
    cursor = conn.cursor()
    cursor.execute('UPDATE livros SET preco = ? WHERE id = ?', (novo_preco, id))
    conn.commit()
    conn.close()
    fazer_backup()

def remover_livro(id):
    conn = criar_conexao()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM livros WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    fazer_backup()

def buscar_por_autor(autor):
    conn = criar_conexao()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM livros WHERE autor LIKE ?', (f'%{autor}%',))
    livros = cursor.fetchall()
    conn.close()
    return livros

def exportar_para_csv():
    livros = exibir_livros()
    export_file = EXPORT_DIR / 'livros_exportados.csv'
    with open(export_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Título', 'Autor', 'Ano de Publicação', 'Preço'])
        writer.writerows(livros)

def importar_de_csv():
    import_file = EXPORT_DIR / 'livros_exportados.csv'
    conn = criar_conexao()
    cursor = conn.cursor()
    with open(import_file, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Pular o cabeçalho
        for row in csv_reader:
            cursor.execute('INSERT INTO livros (titulo, autor, ano_publicacao, preco) VALUES (?, ?, ?, ?)',
                           (row[1], row[2], int(row[3]), float(row[4])))
    conn.commit()
    conn.close()
    fazer_backup()

def fazer_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f'backup_livraria_{timestamp}.db'
    
    # Fechar todas as conexões com o banco de dados
    conn = criar_conexao()
    conn.close()
    
    # Copiar o arquivo do banco de dados
    shutil.copy2(DB_PATH, backup_file)
    
    limpar_backups_antigos()

def limpar_backups_antigos():
    backups = sorted(BACKUP_DIR.glob('backup_livraria_*.db'), key=os.path.getmtime, reverse=True)
    while len(backups) > 5:
        oldest_backup = backups.pop()
        oldest_backup.unlink()


def menu():
    while True:
        print("\n1. Adicionar novo livro")
        print("2. Exibir todos os livros")
        print("3. Atualizar preço de um livro")
        print("4. Remover um livro")
        print("5. Buscar livros por autor")
        print("6. Exportar dados para CSV")
        print("7. Importar dados de CSV")
        print("8. Fazer backup do banco de dados")
        print("9. Sair")
        
        escolha = input("Escolha uma opção: ")
        
        if escolha == '1':
            titulo = input("Título do livro: ")
            autor = input("Autor do livro: ")
            ano = int(input("Ano de publicação: "))
            preco = float(input("Preço do livro: "))
            adicionar_livro(titulo, autor, ano, preco)
            print("Livro adicionado com sucesso!")
        
        elif escolha == '2':
            livros = exibir_livros()
            for livro in livros:
                print(livro)
        
        elif escolha == '3':
            id = int(input("ID do livro: "))
            novo_preco = float(input("Novo preço: "))
            atualizar_preco(id, novo_preco)
            print("Preço atualizado com sucesso!")
        
        elif escolha == '4':
            id = int(input("ID do livro a ser removido: "))
            remover_livro(id)
            print("Livro removido com sucesso!")
        
        elif escolha == '5':
            autor = input("Nome do autor: ")
            livros = buscar_por_autor(autor)
            for livro in livros:
                print(livro)
        
        elif escolha == '6':
            exportar_para_csv()
            print("Dados exportados para CSV com sucesso!")
        
        elif escolha == '7':
            importar_de_csv()
            print("Dados importados do CSV com sucesso!")
        
        elif escolha == '8':
            fazer_backup()
            print("Backup realizado com sucesso!")
        
        elif escolha == '9':
            print("Saindo do sistema...")
            break
        
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    criar_tabela()
    menu()