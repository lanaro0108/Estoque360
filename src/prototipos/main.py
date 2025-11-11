import streamlit as st
import base64
import random
import string
import pandas as pd
import os

with open("estoque360_master.png", "rb") as f:
    imagem = base64.b64encode(f.read()).decode()

st.markdown(
    f"""
    <div style="display: flex; align-items: center; justify-content: center;">
        <img src="data:image/png;base64,{imagem}" width="90" style="margin-right: 15px;">
        <h1 style="margin: 0;">Estoque360</h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<h3 style='text-align: center;'>Adicionar Produtos</h3>", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Selecione a categoria do produto:")
categoria = st.sidebar.radio("Categoria do produto:", ("Acessórios", "Calçados", "Vestuário"))

# Tipo do produto
if categoria == "Acessórios":
    tipo_produto = st.selectbox(
        "Selecione o tipo do Produto:",
        options=["Bolsas", "Cintos", "Chapéus", "Lenços", "Óculos de sol"],
        index=None,
        placeholder="Selecione o produto..."
    )

elif categoria == "Calçados":
    tipo_produto = st.selectbox(
        "Selecione o tipo do Produto:",
        options=["Tênis", "Sandálias", "Botas", "Sapatos", "Sapatilhas"],
        index=None,
        placeholder="Selecione o produto..."
    )

else:
    tipo_produto = st.selectbox(
        "Selecione o tipo do Produto:",
        options=["Camisas", "Calças", "Vestidos", "Blusa Moletom", "Jaqueta", "Camisetas"],
        index=None,
        placeholder="Selecione o produto..."
    )

# Gênero
genero = st.radio("Gênero do produto:", ("Masculino", "Feminino", "Unissex"))

# Marca
marca = st.text_input("Digite a Marca do Produto", placeholder="Digite a Marca do Produto...")

# Cor
cor = st.text_input("Digite a Cor Principal do Produto", placeholder="Digite a Cor Principal do Produto...")

# Tamanho
tamanho = ""
if categoria == "Calçados":
    tamanhos_calcados = [str(t) for t in range(33, 47)]
    tamanho = st.radio("Selecione o tamanho do calçado:", tamanhos_calcados, horizontal=True)

elif categoria == "Vestuário":
    tamanhos_letras = ["PP", "P", "M", "G", "GG", "XG", "XXG", "XXXG"]
    tamanhos_numericos = [str(t) for t in range(34, 61, 2)]
    tamanhos_infantil = [str(t) for t in range(2, 18, 2)]

    if tipo_produto in ["Calças", "Jaqueta"]:
        tamanho = st.radio("Selecione o tamanho (numérico):", tamanhos_numericos, horizontal=True)
    elif tipo_produto in ["Camisas", "Camisetas", "Blusa Moletom"]:
        tamanho = st.radio("Selecione o tamanho (letras):", tamanhos_letras, horizontal=True)
    elif tipo_produto == "Vestidos":
        tamanho = st.radio("Selecione o tamanho (infantil ou adulto):", tamanhos_infantil + tamanhos_letras, horizontal=True)

# Quantidade
quantidade = st.number_input("Quantidade:", min_value=1, step=1)

# Lista de códigos
if "lista_codigos" not in st.session_state:
    st.session_state.lista_codigos = []

def gerar_codigo():
    while True:
        letras = ''.join(random.choices(string.ascii_uppercase, k=4))
        numeros = ''.join(random.choices(string.digits, k=3))
        codigo = letras + "-" + numeros
        if codigo not in st.session_state.lista_codigos:
            return codigo

if st.button("Cadastrar o Produto", key="gerar_codigos"):
    erros = []
    if tipo_produto is None:
        erros.append("Por favor, selecione um tipo de produto válido.")
    if not marca:
        erros.append("Por favor, digite a marca do produto.")
    if not cor:
        erros.append("Por favor, digite a cor do produto.")
    if categoria in ["Calçados", "Vestuário"] and not tamanho:
        erros.append("Por favor, selecione um tamanho.")

    if erros:
        for erro in erros:
            st.warning(erro)
    else:
        for _ in range(quantidade):
            codigo = gerar_codigo()
            st.session_state.lista_codigos.append(codigo)
        st.success(f"✅ {quantidade} produto(s) cadastrado(s) com sucesso!")
        st.write("Códigos gerados:", st.session_state.lista_codigos[-quantidade:])

if st.session_state.lista_codigos:
    st.markdown("### 📦 Códigos cadastrados:")
    st.write(st.session_state.lista_codigos)

PASTA_DADOS = "data"
os.makedirs(PASTA_DADOS, exist_ok=True)
ARQUIVO = os.path.join(PASTA_DADOS, "estoque.csv")

def salvar_produto(categoria, tipo_produto, genero, marca, cor, tamanho, quantidade, codigos):
    novo_registro = {
        "Categoria": categoria,
        "Tipo": tipo_produto,
        "Gênero": genero,
        "Marca": marca,
        "Cor": cor,
        "Tamanho": tamanho,
        "Quantidade": quantidade,
        "Códigos": ", ".join(codigos)
    }
    try:
        if os.path.exists(ARQUIVO):
            df_existente = pd.read_csv(ARQUIVO)
            df = pd.concat([df_existente, pd.DataFrame([novo_registro])], ignore_index=True)
        else:
            df = pd.DataFrame([novo_registro])

        df.to_csv(ARQUIVO, index=False)
        st.success(f"📁 Produto salvo com sucesso em: `{ARQUIVO}`")
        st.dataframe(df.tail())
    except Exception as e:
        st.error(f"❌ Erro ao salvar o arquivo: {e}")

if st.button("Salvar no Arquivo", key="salvar_csv"):
    erros = []
    if tipo_produto is None:
        erros.append("Por favor, selecione um tipo de produto válido.")
    if not marca:
        erros.append("Por favor, digite a marca do produto.")
    if not cor:
        erros.append("Por favor, digite a cor do produto.")
    if categoria in ["Calçados", "Vestuário"] and not tamanho:
        erros.append("Por favor, selecione um tamanho.")
    if not st.session_state.lista_codigos:
        erros.append("Nenhum produto foi cadastrado para salvar.")

    if erros:
        for erro in erros:
            st.warning(erro)
    else:
        salvar_produto(categoria, tipo_produto, genero, marca, cor, tamanho,
                       quantidade, st.session_state.lista_codigos[-quantidade:])
        st.session_state.lista_codigos = []