#Main
import streamlit as st
from produtos import salvar_produto, salvar_estoque, atualizar_estoque, pegar_id
from fornecedores import registrar_compra, registrar_fornecedor
from clientes import registrar_venda, registrar_cliente
from database import conectar, criar_tabelas
import base64
import os
from dotenv import load_dotenv
import sqlite3

load_dotenv()

criar_tabelas()

# chatbot - tem q colocar nome ainda
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()


client = OpenAI(api_key=os.getenv("api_estoque360_01"))

st.sidebar.subheader("🤖 Assistente Estoque360")

if "mostrar_chat" not in st.session_state:
    st.session_state.mostrar_chat = False

if st.sidebar.button("Clique para falar com o Assistente", key="icone_chat"):
    st.session_state.mostrar_chat = not st.session_state.mostrar_chat

st.sidebar.markdown("<hr>", unsafe_allow_html=True)

if st.session_state.mostrar_chat:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": """
Você é o Assistente Oficial do Sistema Estoque360.

Função:
- Ajudar usuários a cadastrar produtos, gerar códigos, escolher categorias, tamanhos, cores e marcas.
- Explicar como funciona cada etapa do formulário.
- Ajudar a entender erros do sistema (ex: campo vazio, tamanho não selecionado, marca faltando).
- Dar orientações claras e objetivas, sempre focadas no funcionamento do Estoque360.

Regras do seu comportamento:
1. Seja educado, rápido e direto.
2. Não invente informações fora do contexto do sistema.
3. Responda sempre como se estivesse integrado ao Estoque360.
4. Sempre tente entender o que o usuário quer fazer (cadastrar, corrigir erro, entender categoria, etc).
5. Se houver possível erro no cadastro, aponte a causa e diga como resolver.
6. Use linguagem simples e prática.

Funções do sistema conhecidas:
- Categorias: Acessórios, Calçados, Vestuário.
- Cada categoria possui tipos específicos de produto.
- Gêneros disponíveis: Masculino, Feminino, Unissex.
- Sistema gera códigos automáticos AAAA-000.
- Validação impede cadastro sem marca, cor, tamanho (quando aplicável) e tipo de produto.
- Quantidade permite vários códigos gerados.
- Histórico fica armazenado no session_state.lista_codigos.

Seu objetivo:
Guiar o usuário como um atendente real do Estoque360.
"""}

        ]
    pergunta = st.sidebar.text_input("Digite sua pergunta:", key="pergunta_chat")

    if pergunta:
        st.session_state.messages.append({"role": "user", "content": pergunta})

        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages
        )

        resposta_texto = resposta.choices[0].message.content

        st.session_state.messages.append({"role": "assistant", "content": resposta_texto})

        st.sidebar.markdown(f"**Bot:** {resposta_texto}")

try:
    with open("assets/estoque360_master.png", "rb") as f:
        imagem = base64.b64encode(f.read()).decode()
    with open("assets/estoque360_icone__1_-removebg-preview.png", "rb") as f:
        icone = f.read()
    st.set_page_config(page_title="Estoque 360 - Cadastro de produtos",page_icon=icone)
except FileNotFoundError:
    st.set_page_config(page_title="Estoque 360 - Cadastro de produtos")
    imagem = ""

st.markdown(
    f"""
    <div style="display: flex; align-items: center; justify-content: center;">
        {f'<img src="data:image/png;base64,{imagem}" width="90" style="margin-right: 15px;">' if imagem else ''}
        <h1 style="margin: 0;">Estoque360</h1>
    </div>
    """,
    unsafe_allow_html=True
)
def fetch_options(table, column):
    db = conectar()
    cursor = db.cursor()
    cursor.execute(f"SELECT {column} FROM {table}")
    options = [row[0] for row in cursor.fetchall()]
    db.close()
    return options

def fetch_tipos_by_categoria(categoria):
    db = conectar()
    cursor = db.cursor()
    cursor.execute("""
        SELECT tp.nome FROM tipo_produto tp
        JOIN categoria c ON tp.id_categoria = c.id
        WHERE c.nome = ?
    """, (categoria,))
    tipos = [row[0] for row in cursor.fetchall()]
    db.close()
    return tipos

#sidebar para navegação
pagina = st.sidebar.selectbox("Navegar para:", 
                              ["Cadastro de Produtos", "Compras de Fornecedores", "Vendas a Clientes", "Estoque"])

#cadastro de produtos
if pagina == "Cadastro de Produtos":
    st.header("Cadastro de Produtos")

    # Fetch dynamic options
    categorias = fetch_options("categoria", "nome")
    generos = ["masculino", "feminino", "unissex"]

    categoria = st.radio("Categoria", categorias)
    
    # Filtrar tipos de produto pela categoria selecionada
    tipos = fetch_tipos_by_categoria(categoria)
    tipo_produto = st.selectbox("Tipo do produto", tipos)
    
    genero = st.selectbox("Gênero", generos)
    marca = st.text_input("Marca", placeholder="Digite a marca do produto...")
    cor = st.text_input("Cor", placeholder="Digite a cor do produto...")
    tamanho = ""
   
    if categoria == "calçados":
        tamanhos_calcados = [str(t) for t in range(33, 47)]
        tamanho = st.radio("Selecione o tamanho do calçado:", tamanhos_calcados, horizontal=True)

    elif categoria == "vestuário":
        tamanhos_letras = ["PP", "P", "M", "G", "GG", "XG", "XXG", "XXXG"]
        tamanhos_numericos = [str(t) for t in range(34, 61, 2)]
        tamanhos_infantil = [str(t) for t in range(2, 18, 2)]

        # Baseado EXATAMENTE nos tipos que você forneceu (usar lowercase)
        categorias_numericos = ["calças", "shorts", "saia"]
        categorias_letras = [
            "camisas", "camisetas", "blusa moletom",
            "jaqueta", "blazer", "regata"
        ]

        if tipo_produto in categorias_numericos:
            tamanho = st.radio("Selecione o tamanho (numérico):", tamanhos_numericos, horizontal=True)

        elif tipo_produto in categorias_letras:
            tamanho = st.radio("Selecione o tamanho (letras):", tamanhos_letras, horizontal=True)

        elif tipo_produto == "vestidos":
            tamanho = st.radio(
                "Selecione o tamanho:",
                tamanhos_infantil + tamanhos_letras,
                horizontal=True
            )

    precocusto = st.number_input("Preço de custo", min_value=0.0)
    precovenda = st.number_input("Preço de venda", min_value=0.0)
    quantidade = st.number_input("Quantidade", min_value=1, step=1)

    if st.button("Cadastrar Produto"):
        if not marca or not cor:
            st.warning("Marca e Cor são obrigatórios.")
        else:
            produto_id = salvar_produto(categoria, tipo_produto, genero, marca, cor, tamanho, precocusto, precovenda)
            salvar_estoque(produto_id, quantidade)
            st.success(f"Produto {tipo_produto} cadastrado com sucesso!")

#compra de fornecedores
elif pagina == "Compras de Fornecedores":
    st.header("Registrar Compra de Fornecedor")

    tab1, tab2 = st.tabs(["Nova Compra", "Cadastrar Fornecedor"])

    with tab2:
        st.subheader("Cadastrar Novo Fornecedor")
        f_cnpj = st.text_input("CNPJ", placeholder="00.000.000/0000-00")
        f_nome = st.text_input("Nome", placeholder="Insira o nome do fornecedor...")
        f_cep = st.text_input("CEP", placeholder="00000-000")
        f_numero = st.text_input("Número", placeholder="Insira o número...")
        f_comp = st.text_input("Complemento", placeholder="Insira o complemento...")
        f_tel = st.text_input("Telefone", placeholder="(00) 00000-0000")
        f_email = st.text_input("Email", placeholder="email@exemplo.com")
        
        if st.button("Salvar Fornecedor"):
            if f_cnpj and f_nome and f_cep:
                registrar_fornecedor(f_cnpj, f_nome, f_cep, f_numero, f_comp, f_tel, f_email)
                st.success("Fornecedor cadastrado!")
            else:
                st.warning("Preencha os campos obrigatórios.")

    with tab1:
        st.subheader("Registrar Compra")
        cnpj_fornecedor = st.text_input("CNPJ do fornecedor", key="compra_cnpj", placeholder="00.000.000/0000-00")
        
        st.write("Adicionar Produtos")
        if "produtos_compra" not in st.session_state:
            st.session_state.produtos_compra = []

        c_prod_nome = st.text_input("Nome do Produto (Busca por Tipo)") # Simplified search
        c_qtd = st.number_input("Quantidade", min_value=1, step=1, key="c_qtd")
        c_valor = st.number_input("Valor Unitário", min_value=0.0, key="c_valor")

        if st.button("Adicionar Item"):
            db = conectar()
            cursor = db.cursor()
            cursor.execute("SELECT p.id FROM produtos p JOIN tipo_produto tp ON p.id_tipo_produto = tp.id WHERE tp.nome LIKE ?", (f"%{c_prod_nome}%",))
            res = cursor.fetchone()
            db.close()
            
            if res:
                st.session_state.produtos_compra.append({"id_produto": res[0], "quantidade": c_qtd, "valor_unit": c_valor, "nome": c_prod_nome})
                st.success(f"Produto adicionado!")
            else:
                st.warning("Produto não encontrado. Tente o nome exato do tipo.")

        if st.session_state.produtos_compra:
            st.write("Itens na lista:")
            for item in st.session_state.produtos_compra:
                st.write(f"- {item['nome']}: {item['quantidade']} x R$ {item['valor_unit']}")
        
        if st.button("Finalizar Compra"):
            if not st.session_state.produtos_compra:
                st.warning("Lista vazia.")
            else:
                try:
                    id_compra = registrar_compra(cnpj_fornecedor, st.session_state.produtos_compra)
                    st.success(f"Compra {id_compra} registrada!")
                    st.session_state.produtos_compra = []
                except Exception as e:
                    st.error(f"Erro: {e}. Verifique se o fornecedor está cadastrado.")

#vendas a clientes
elif pagina == "Vendas a Clientes":
    st.header("Registrar Venda a Cliente")
    
    tab1, tab2 = st.tabs(["Nova Venda", "Cadastrar Cliente"])
    
    with tab2:
        st.subheader("Cadastrar Novo Cliente")
        c_cpf = st.text_input("CPF", placeholder="000.000.000-00")
        c_nome = st.text_input("Nome", placeholder="Insira o nome do cliente...")
        c_cep = st.text_input("CEP", placeholder="00000-000")
        c_numero = st.text_input("Número", placeholder="Insira o número...")
        c_comp = st.text_input("Complemento", placeholder="Insira o complemento...")
        c_tel = st.text_input("Telefone", placeholder="(00) 00000-0000")
        c_email = st.text_input("Email", placeholder="email@exemplo.com")
        
        if st.button("Salvar Cliente"):
            if c_cpf and c_nome and c_cep:
                registrar_cliente(c_cpf, c_nome, c_cep, c_numero, c_comp, c_tel, c_email)
                st.success("Cliente cadastrado!")
            else:
                st.warning("Preencha os campos obrigatórios.")

    with tab1:
        st.subheader("Registrar Venda")
        cpf_cliente = st.text_input("CPF do Cliente", key="venda_cpf", placeholder="000.000.000-00")
        
        # Fetch payment methods
        db = conectar()
        cursor = db.cursor()
        cursor.execute("SELECT id, formapgto FROM forma_pgto")
        pgtos = {row[1]: row[0] for row in cursor.fetchall()}
        db.close()
        
        pgto_nome = st.selectbox("Forma de Pagamento", list(pgtos.keys()))
        id_formapgto = pgtos[pgto_nome]

        if "produtos_venda" not in st.session_state:
            st.session_state.produtos_venda = []

        v_prod_nome = st.text_input("Nome do Produto (Busca por Tipo)", key="v_prod", placeholder="Insira o nome do tipo do produto...")
        v_qtd = st.number_input("Quantidade", min_value=1, step=1, key="v_qtd")
        v_valor = st.number_input("Valor Unitário", min_value=0.0, key="v_valor")

        if st.button("Adicionar Item à Venda"):
            db = conectar()
            cursor = db.cursor()
            cursor.execute("SELECT p.id FROM produtos p JOIN tipo_produto tp ON p.id_tipo_produto = tp.id WHERE tp.nome LIKE ?", (f"%{v_prod_nome}%",))
            res = cursor.fetchone()
            db.close()
            
            if res:
                st.session_state.produtos_venda.append({"id_produto": res[0], "quantidade": v_qtd, "valor_unit": v_valor, "nome": v_prod_nome})
                st.success(f"Produto adicionado!")
            else:
                st.warning("Produto não encontrado.")

        if st.session_state.produtos_venda:
            st.write("Itens na venda:")
            for item in st.session_state.produtos_venda:
                st.write(f"- {item['nome']}: {item['quantidade']} x R$ {item['valor_unit']}")

        if st.button("Finalizar Venda"):
            if not st.session_state.produtos_venda:
                st.warning("Lista vazia.")
            else:
                try:
                    id_venda = registrar_venda(cpf_cliente, id_formapgto, st.session_state.produtos_venda)
                    st.success(f"Venda {id_venda} registrada!")
                    st.session_state.produtos_venda = []
                except Exception as e:
                    st.error(f"Erro: {e}")

#estoque
elif pagina == "Estoque":
    st.header("Estoque Atual")

    db = conectar()
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute("""
        SELECT p.id, tp.nome as tipo_produto, m.nomemarca as marca, c.nomecor as cor, t.tamanho, e.quantidade
        FROM produtos p
        JOIN tipo_produto tp ON p.id_tipo_produto = tp.id
        JOIN marcas m ON p.id_marca = m.id
        JOIN cores c ON p.id_cor = c.id
        JOIN tamanho t ON p.id_tamanho = t.id
        JOIN estoque_atual e ON p.id = e.produto_id
    """)
    estoque = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    db.close()
    st.table(estoque)
