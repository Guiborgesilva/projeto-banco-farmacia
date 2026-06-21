import unicodedata
import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from psycopg2 import Error

# ================= CONFIGURAÇÕES DO BANCO =================
DB_HOST = "localhost"
DB_NAME = "farmacia"
DB_USER = "postgres"
DB_PASSWORD = "123456"

# ================= CLASSE DE CONEXÃO COM O BANCO =================
class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
        )

    def executar_procedure(self, proc_name, params):
        """Executa procedures de qualquer tamanho dinamicamente"""
        try:
            cur = self.conn.cursor()
            # Cria a quantidade exata de '%s' baseado no tamanho da lista de parâmetros
            placeholders = ", ".join(["%s"] * len(params))
            cur.execute(f"CALL {proc_name}({placeholders})", params)
            self.conn.commit()
            
            mensagem = ""
            if self.conn.notices:
                mensagem = "\n".join(n.strip() for n in self.conn.notices)
            return True, mensagem
        except Error as e:
            self.conn.rollback()
            return False, str(e).split("\n")[0]

    def executar_funcao(self, func_name, param):
        """Executa functions e retorna (Status, Mensagem)"""
        try:
            cur = self.conn.cursor()
            cur.execute(f"SELECT {func_name}(%s)", (param,))
            resultado = cur.fetchone()[0]
            return True, resultado
        except Error as e:
            return False, str(e).split("\n")[0]

    def buscar_tabela(self, query):
        """Busca dados para popular as Views (Treeview)"""
        try:
            cur = self.conn.cursor()
            cur.execute(query)
            colunas = [desc[0] for desc in cur.description]
            dados = cur.fetchall()
            return True, colunas, dados
        except Error as e:
            return False, str(e), []

# ================= SISTEMA GRÁFICO (TKINTER) =================
class SistemaFarmacia(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Configurações da Janela Principal (Estilo Antigo)
        self.title("Sistema de Gerenciamento - Farmácia [Versão 1.0]")
        self.geometry("800x600")
        self.configure(bg="#C0C0C0") # Cinza clássico do Windows antigo
        
        # Força o estilo antigo dos botões
        self.option_add('*TCombobox*Listbox.background', '#FFFFFF')
        style = ttk.Style(self)
        style.theme_use('clam') # 'clam' ou 'default' dão essa cara mais quadrada e antiga

        self.db = Database()
        self.container = tk.Frame(self, bg="#C0C0C0")
        self.container.pack(fill="both", expand=True)

        self.criar_menu()
        self.frames = {}
        self.mostrar_frame("home")

    def criar_menu(self):
        menubar = tk.Menu(self)
        
        menu_cadastros = tk.Menu(menubar, tearoff=0)
        menu_cadastros.add_command(label="Cadastrar Fornecedor", command=lambda: self.mostrar_frame("cad_fornecedor"))
        menu_cadastros.add_command(label="Cadastrar Produto", command=lambda: self.mostrar_frame("cad_produto"))
        menu_cadastros.add_separator()
        menu_cadastros.add_command(label="Listar Produtos (IDs)", command=lambda: self.mostrar_frame("list_produtos"))
        
        menu_estoque = tk.Menu(menubar, tearoff=0)
        menu_estoque.add_command(label="Atualizar Estoque", command=lambda: self.mostrar_frame("atualizar_estoque"))
        menu_estoque.add_command(label="Consultar Estoque", command=lambda: self.mostrar_frame("cons_estoque"))
        menu_estoque.add_command(label="Consultar Valor Total", command=lambda: self.mostrar_frame("cons_valor_total"))
        
        menu_compras = tk.Menu(menubar, tearoff=0)
        menu_compras.add_command(label="Calcular Total Compra", command=lambda: self.mostrar_frame("calc_total_compra"))
        menu_compras.add_command(label="Registrar Nova Compra", command=lambda: self.mostrar_frame("reg_compra"))

        menu_relatorios = tk.Menu(menubar, tearoff=0)
        menu_relatorios.add_command(label="View: Estoque Geral", command=lambda: self.mostrar_frame("view_estoque"))
        menu_relatorios.add_command(label="View: Itens de Compras", command=lambda: self.mostrar_frame("view_compras"))
        menu_relatorios.add_command(label="View: Movimentações", command=lambda: self.mostrar_frame("view_movimentacao"))

        menubar.add_cascade(label="Cadastros", menu=menu_cadastros)
        menubar.add_cascade(label="Estoque", menu=menu_estoque)
        menubar.add_cascade(label="Compras", menu=menu_compras)
        menubar.add_cascade(label="Relatórios (Views)", menu=menu_relatorios)

        self.config(menu=menubar)

        # Barra de Status no rodapé (Clássico dos sistemas antigos)
        self.status_bar = tk.Label(self, text="Pronto", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#E0E0E0")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def mostrar_frame(self, nome_frame):
        # Destroi o frame atual para limpar a tela
        for widget in self.container.winfo_children():
            widget.destroy()

        self.status_bar.config(text=f"Seção: {nome_frame.replace('_', ' ').upper()}")

        # Direciona para a função que constrói a tela
        if nome_frame == "home": self.tela_home()
        elif nome_frame == "cad_fornecedor": self.tela_cad_fornecedor()
        elif nome_frame == "cad_produto": self.tela_cad_produto()
        elif nome_frame == "atualizar_estoque": self.tela_atualizar_estoque()
        elif nome_frame == "cons_estoque": self.tela_consulta_generica("consultar_estoque", "Consultar Estoque", "ID do Produto:")
        elif nome_frame == "cons_valor_total": self.tela_consulta_generica("consultar_valor_total_estoque", "Consultar Valor Total", "ID do Produto:")
        elif nome_frame == "calc_total_compra": self.tela_consulta_generica("calcular_total_compra", "Calcular Total Compra", "ID da Compra:")
        elif nome_frame == "list_produtos": self.tela_view("SELECT id, nome, categoria, valor FROM produtos ORDER BY id")
        elif nome_frame == "view_estoque": self.tela_view("SELECT * FROM verificar_estoque")
        elif nome_frame == "view_compras": self.tela_view("SELECT * FROM verificar_compras")
        elif nome_frame == "view_movimentacao": self.tela_view("SELECT * FROM verificar_movimentacao")
        elif nome_frame == "reg_compra": self.tela_registrar_compra()

    # ================= TELAS (FRAMES) =================

    def tela_home(self):
        tk.Label(self.container, text="SISTEMA DE FARMÁCIA", font=("Helvetica", 24, "bold"), bg="#C0C0C0").pack(pady=100)
        tk.Label(self.container, text="Use o menu superior para navegar.", font=("Helvetica", 12), bg="#C0C0C0").pack()

    def tela_cad_fornecedor(self):
        self.formulario_padrao(
            titulo="Cadastrar Fornecedor",
            campos=[("CNPJ (14 números):", "cnpj"), ("Nome:", "nome"), ("Telefone (11 números):", "tel")],
            nome_procedure="cadastrar_fornecedor"
        )

    def tela_cad_produto(self):
        self.formulario_padrao(
            titulo="Cadastrar Produto",
            campos=[("Nome do Produto:", "nome"), ("Categoria:", "cat"), ("Valor (ex: 10.50):", "valor")],
            nome_procedure="cadastrar_produto"
        )

    def tela_atualizar_estoque(self):
        frame = tk.Frame(self.container, bg="#C0C0C0")
        frame.pack(padx=20, pady=20)

        tk.Label(frame, text="Atualizar Estoque (Entrada/Saída)", font=("Helvetica", 14, "bold"), bg="#C0C0C0").grid(row=0, column=0, columnspan=2, pady=10)

        labels = ["ID do Produto:", "Quantidade:", "Tipo ('entrada' ou 'saida'):"]
        entradas = []
        for i, texto in enumerate(labels, start=1):
            tk.Label(frame, text=texto, bg="#C0C0C0").grid(row=i, column=0, sticky="w", pady=5)
            e = tk.Entry(frame, width=40)
            e.grid(row=i, column=1, pady=5, padx=10)
            e.bind("<Return>", lambda event: executar()) # <--- ENTER AQUI
            entradas.append(e)

        def executar():
            params = [e.get().strip() for e in entradas]
            if not all(params): return messagebox.showerror("Erro", "Preencha todos os campos.")
            
            tipo_digitado = params[2]
            tipo_sem_acento = ''.join(c for c in unicodedata.normalize('NFD', tipo_digitado) if not unicodedata.combining(c))
            params[2] = tipo_sem_acento.upper()
            
            sucesso, msg = self.db.executar_procedure("atualizar_estoque", params)
            if sucesso:
                messagebox.showinfo("Sucesso", msg)
                for e in entradas: e.delete(0, tk.END)
            else:
                messagebox.showerror("Erro no Banco", msg)

        tk.Button(frame, text="Executar", width=15, command=executar).grid(row=len(labels)+1, column=0, columnspan=2, pady=15)

    def tela_consulta_generica(self, nome_func, titulo_texto, label_input):
        frame = tk.Frame(self.container, bg="#C0C0C0")
        frame.pack(padx=20, pady=20)

        tk.Label(frame, text=titulo_texto, font=("Helvetica", 14, "bold"), bg="#C0C0C0").grid(row=0, column=0, columnspan=2, pady=10)
        tk.Label(frame, text=label_input, bg="#C0C0C0").grid(row=1, column=0, sticky="w", pady=5)
        
        entrada = tk.Entry(frame, width=40)
        entrada.grid(row=1, column=1, pady=5, padx=10)
        entrada.bind("<Return>", lambda event: executar()) # <--- ENTER AQUI

        resultado_text = tk.Text(frame, height=5, width=60, state=tk.DISABLED)
        resultado_text.grid(row=3, column=0, columnspan=2, pady=10)

        def executar():
            id_pesquisa = entrada.get().strip()
            if not id_pesquisa: return messagebox.showerror("Erro", "Informe o ID.")
            
            sucesso, msg = self.db.executar_funcao(nome_func, id_pesquisa)
            resultado_text.config(state=tk.NORMAL)
            resultado_text.delete(1.0, tk.END)
            if sucesso:
                resultado_text.insert(tk.END, msg)
            else:
                resultado_text.insert(tk.END, f"ERRO: {msg}")
            resultado_text.config(state=tk.DISABLED)

        tk.Button(frame, text="Consultar", width=15, command=executar).grid(row=2, column=0, columnspan=2, pady=10)

    def tela_view(self, query_sql):
        frame = tk.Frame(self.container, bg="#C0C0C0")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Cria a Treeview (Tabela)
        tree = ttk.Treeview(frame, show="headings")
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Busca dados
        sucesso, colunas, dados = self.db.buscar_tabela(query_sql)

        if sucesso:
            tree["columns"] = colunas
            for col in colunas:
                tree.heading(col, text=col)
                tree.column(col, width=150, anchor="center")
            
            for linha in dados:
                tree.insert("", "end", values=linha)
        else:
            messagebox.showerror("Erro ao carregar View", colunas) # 'colunas' traz a msg de erro aqui

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # ================= UTILITÁRIOS =================

    def formulario_padrao(self, titulo, campos, nome_procedure):
        """Cria telas de formulário dinamicamente"""
        frame = tk.Frame(self.container, bg="#C0C0C0")
        frame.pack(padx=20, pady=20)

        tk.Label(frame, text=titulo, font=("Helvetica", 14, "bold"), bg="#C0C0C0").grid(row=0, column=0, columnspan=2, pady=10)
        
        entradas = []
        for i, (texto_label, chave) in enumerate(campos, start=1):
            tk.Label(frame, text=texto_label, bg="#C0C0C0").grid(row=i, column=0, sticky="w", pady=5)
            e = tk.Entry(frame, width=40)
            e.grid(row=i, column=1, pady=5, padx=10)
            e.bind("<Return>", lambda event: executar())
            entradas.append(e)

        def executar():
            params = [e.get().strip() for e in entradas]
            if not all(params): return messagebox.showerror("Erro", "Preencha todos os campos.")
            
            sucesso, msg = self.db.executar_procedure(nome_procedure, params)
            if sucesso:
                messagebox.showinfo("Sucesso", msg)
                for e in entradas: e.delete(0, tk.END)
            else:
                messagebox.showerror("Erro no Banco", msg)

        tk.Button(frame, text="Cadastrar", width=15, command=executar).grid(row=len(campos)+1, column=0, columnspan=2, pady=15)

    def tela_registrar_compra(self):
        frame = tk.Frame(self.container, bg="#C0C0C0")
        frame.pack(padx=20, pady=20)

        tk.Label(frame, text="Registrar Compra de Fornecedor", font=("Helvetica", 14, "bold"), bg="#C0C0C0").grid(row=0, column=0, columnspan=2, pady=10)
        
        _, _, fornecedores = self.db.buscar_tabela("SELECT cnpj, nome FROM fornecedores ORDER BY nome")
        lista_forn = [f"{row[0]} - {row[1]}" for row in fornecedores]

        _, _, produtos = self.db.buscar_tabela("SELECT id, nome FROM produtos ORDER BY nome")
        lista_prod = [f"{row[0]} - {row[1]}" for row in produtos]

        tk.Label(frame, text="Data (DD/MM/AAAA):", bg="#C0C0C0").grid(row=1, column=0, sticky="w", pady=5)
        entry_data = tk.Entry(frame, width=43)
        entry_data.grid(row=1, column=1, pady=5, padx=10)

        def aplicar_mascara(event):
            # ADICIONADO 'Return' AQUI PARA O ENTER FUNCIONAR
            if event.keysym in ('BackSpace', 'Delete', 'Left', 'Right', 'Shift_L', 'Shift_R', 'Return'):
                return
            
            if not event.char.isdigit():
                return "break" 
            
            texto_atual = entry_data.get().replace("/", "") + event.char
            texto_atual = texto_atual[:8]
            
            novo_texto = ""
            for i, c in enumerate(texto_atual):
                if i == 2 or i == 4:
                    novo_texto += "/"
                novo_texto += c
                
            entry_data.delete(0, tk.END)
            entry_data.insert(0, novo_texto)
            return "break" 

        entry_data.bind("<Key>", aplicar_mascara)
        entry_data.bind("<Return>", lambda event: executar()) # <--- ENTER AQUI

        tk.Label(frame, text="Fornecedor:", bg="#C0C0C0").grid(row=2, column=0, sticky="w", pady=5)
        combo_forn = ttk.Combobox(frame, values=lista_forn, width=40, state="readonly")
        combo_forn.grid(row=2, column=1, pady=5, padx=10)

        tk.Label(frame, text="Produto:", bg="#C0C0C0").grid(row=3, column=0, sticky="w", pady=5)
        combo_prod = ttk.Combobox(frame, values=lista_prod, width=40, state="readonly")
        combo_prod.grid(row=3, column=1, pady=5, padx=10)

        tk.Label(frame, text="Quantidade:", bg="#C0C0C0").grid(row=4, column=0, sticky="w", pady=5)
        entry_qtd = tk.Entry(frame, width=43)
        entry_qtd.grid(row=4, column=1, pady=5, padx=10)
        entry_qtd.bind("<Return>", lambda event: executar()) # <--- ENTER AQUI

        tk.Label(frame, text="Preço Unitário (ex: 15.50):", bg="#C0C0C0").grid(row=5, column=0, sticky="w", pady=5)
        entry_preco = tk.Entry(frame, width=43)
        entry_preco.grid(row=5, column=1, pady=5, padx=10)
        entry_preco.bind("<Return>", lambda event: executar()) # <--- ENTER AQUI

        def executar():
            data_digitada = entry_data.get().strip()
            forn_selecionado = combo_forn.get().strip()
            prod_selecionado = combo_prod.get().strip()
            qtd = entry_qtd.get().strip()
            preco = entry_preco.get().strip()

            if not all([data_digitada, forn_selecionado, prod_selecionado, qtd, preco]):
                return messagebox.showerror("Erro", "Preencha todos os campos.")

            try:
                dia, mes, ano = data_digitada.split('/')
                data_formatada_banco = f"{ano}-{mes}-{dia}"
            except ValueError:
                return messagebox.showerror("Erro", "Formato de data inválido.")

            try:
                cnpj = forn_selecionado.split(' - ')[0]
                id_produto = int(prod_selecionado.split(' - ')[0])
            except:
                return messagebox.showerror("Erro", "Erro ao processar Fornecedor ou Produto.")

            try:
                preco_float = float(preco.replace(',', '.'))
            except ValueError:
                return messagebox.showerror("Erro", "Valor do preço inválido.")

            params = [data_formatada_banco, cnpj, id_produto, qtd, preco_float]

            sucesso, msg = self.db.executar_procedure("registrar_compra_completa", params)
            if sucesso:
                messagebox.showinfo("Sucesso", msg)
                entry_data.delete(0, tk.END)
                combo_forn.set('')
                combo_prod.set('')
                entry_qtd.delete(0, tk.END)
                entry_preco.delete(0, tk.END)
            else:
                messagebox.showerror("Erro no Banco", msg)

        tk.Button(frame, text="Registrar Compra", width=20, command=executar).grid(row=6, column=0, columnspan=2, pady=15)

# ================= INICIAR O SISTEMA =================
if __name__ == "__main__":
    app = SistemaFarmacia()
    app.mainloop()