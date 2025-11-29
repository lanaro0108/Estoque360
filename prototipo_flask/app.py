from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import criar_tabelas, conectar
from produtos import salvar_produto, salvar_estoque
from fornecedores import registrar_fornecedor, registrar_compra
from clientes import registrar_cliente, registrar_venda
from openai import OpenAI
import os

client = OpenAI()

app = Flask(__name__)
app.secret_key = "segredo"  # necessário para mensagens flash

criar_tabelas()

@app.route("/")
def index():
    return render_template("index.html")

#produtos
@app.route("/produtos", methods=["GET", "POST"])
def produtos():
    if request.method == "POST":
        categoria = request.form["categoria"]
        tipo = request.form["tipo"]
        genero = request.form["genero"]
        marca = request.form["marca"]
        cor = request.form["cor"]
        tamanho = request.form["tamanho"]
        preco_custo = float(request.form["preco_custo"])
        preco_venda = float(request.form["preco_venda"])
        quantidade = int(request.form["quantidade"])

        produto_id = salvar_produto(categoria, tipo, genero, marca, cor, tamanho, preco_custo, preco_venda)
        salvar_estoque(produto_id, quantidade)

        flash("Produto cadastrado com sucesso!")
        return redirect(url_for("produtos"))

    return render_template("produtos.html")

#fornecedores
@app.route("/fornecedores", methods=["GET", "POST"])
def fornecedores():
    if request.method == "POST":
        cnpj = request.form["cnpj"]
        nome = request.form["nome"]
        cep = request.form["cep"]
        numero = request.form["numero"]
        complemento = request.form["complemento"]
        telefone = request.form["telefone"]
        email = request.form["email"]

        registrar_fornecedor(cnpj, nome, cep, numero, complemento, telefone, email)

        flash("Fornecedor cadastrado!")
        return redirect(url_for("fornecedores"))

    return render_template("fornecedores.html")

#compras
@app.route("/compras", methods=["GET", "POST"])
def compras():
    if request.method == "POST":
        cnpj = request.form["cnpj"]
        id_produto = int(request.form["produto"])
        quantidade = int(request.form["quantidade"])
        valor_unit = float(request.form["valor"])

        itens = [{"id_produto": id_produto, "quantidade": quantidade, "valor_unit": valor_unit}]
        registrar_compra(cnpj, itens)

        flash("Compra registrada!")
        return redirect(url_for("compras"))

    return render_template("compras.html")

#clientes
@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    if request.method == "POST":
        cpf = request.form["cpf"]
        nome = request.form["nome"]
        cep = request.form["cep"]
        numero = request.form["numero"]
        complemento = request.form["complemento"]
        telefone = request.form["telefone"]
        email = request.form["email"]

        registrar_cliente(cpf, nome, cep, numero, complemento, telefone, email)

        flash("Cliente cadastrado!")
        return redirect(url_for("clientes"))

    return render_template("clientes.html")

#vendas
@app.route("/vendas", methods=["GET", "POST"])
def vendas():
    if request.method == "POST":
        cpf = request.form["cpf"]
        id_produto = int(request.form["produto"])
        quantidade = int(request.form["quantidade"])
        valor_unit = float(request.form["valor"])
        id_forma_pgto = int(request.form["pgto"])

        itens = [{"id_produto": id_produto, "quantidade": quantidade, "valor_unit": valor_unit}]
        registrar_venda(cpf, id_forma_pgto, itens)

        flash("Venda registrada!")
        return redirect(url_for("vendas"))

    return render_template("vendas.html")

#estoque
@app.route("/estoque")
def estoque():
    db = conectar()
    cursor = db.cursor()
    cursor.execute("""
        SELECT p.id, tp.nome, m.nomemarca, c.nomecor, t.tamanho, e.quantidade
        FROM produtos p
        JOIN tipo_produto tp ON p.id_tipo_produto = tp.id
        JOIN marcas m ON p.id_marca = m.id
        JOIN cores c ON p.id_cor = c.id
        JOIN tamanho t ON p.id_tamanho = t.id
        JOIN estoque_atual e ON p.id = e.produto_id
    """)
    dados = cursor.fetchall()
    db.close()
    return render_template("estoque.html", estoque=dados)

@app.route("/chatbot", methods=["POST"])
def chatbot():

    # pega o texto enviado pelo usuário
    user_text = request.form["mensagem"]

    # prompt do Estoque360 (conciso e profissional)
    system_prompt = {
    "role": "system",
    "content": """
Você é o Assistente Oficial do Estoque360.  
Seu trabalho é ajudar o usuário a utilizar o sistema de forma clara, direta e profissional.

IMPORTANTE — NUNCA FAZER:
- Nunca invente menus, botões, telas ou campos que o Estoque360 NÃO possui.
- Nunca fale “Adicionar Produto”, “Imagem do produto”, “Código do produto”, “Verificar produto”, “Editar produto” ou qualquer ação que não exista.
- Nunca explique funcionalidades genéricas de outros sistemas.
- Nunca escreva textos longos, repetitivos ou poluídos.
- Nunca diga que é uma IA.

O QUE EXISTE DE VERDADE NO ESTOQUE360:

----------------------------
CADASTRO DE PRODUTOS
Página: /produtos
Campos reais:
- categoria
- tipo do produto
- gênero
- marca
- cor
- tamanho
- preço de custo
- preço de venda
- quantidade

Como funciona:
1. Usuário preenche esses campos.
2. Clica no botão **Cadastrar Produto**.
3. O produto é salvo e o estoque é atualizado automaticamente.

----------------------------
CADASTRO DE CLIENTES
Campos:
- CPF
- nome
- CEP
- número
- complemento
- telefone
- email

----------------------------
CADASTRO DE FORNECEDORES
Campos:
- CNPJ
- nome
- CEP
- número
- complemento
- telefone
- email

----------------------------
REGISTRO DE COMPRA
Campos necessários:
- CNPJ do fornecedor
- ID do produto
- quantidade
- valor unitário

Efeito:
- Gera entrada no estoque.

----------------------------
REGISTRO DE VENDA
Campos necessários:
- CPF do cliente
- ID do produto
- quantidade
- valor unitário
- forma de pagamento (id)

Efeito:
- Gera saída do estoque.

----------------------------
ESTOQUE
O sistema exibe:
- ID
- tipo do produto
- marca
- cor
- tamanho
- quantidade atual

----------------------------
COMPORTAMENTO DO ASSISTENTE
- Sempre responda de forma curta e objetiva.
- Sempre explique com base no funcionamento REAL do Estoque360.
- Se o usuário cometer um erro (ex: esquecer campo obrigatório), explique como corrigir.
- Se a pergunta estiver confusa, peça esclarecimento.
- Nunca use termos genéricos como “vá na opção adicionar”, “insira código”, “clique na imagem”.
- Seja educado, direto e profissional.
"""
}


    # envia para o modelo (sem histórico)
    resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            system_prompt,
            {"role": "user", "content": user_text}
        ]
    )

    bot_texto = resposta.choices[0].message.content

    # não guardamos histórico — resposta sempre limpa
    session["last_answer"] = bot_texto

    return redirect(request.referrer)

if __name__ == "__main__":
    app.run(debug=True)