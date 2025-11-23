import streamlit as st
import base64
import random
import string

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

st.sidebar.title("Selecione a categoria do produto:")
categoria = st.sidebar.radio("Categoria do produto:", ("Acessórios", "Calçados", "Vestuário"))

if categoria == "Acessórios":
    tipo_produto = st.selectbox(
        "Selecione o tipo do Produto:",
        options=["Bolsas", "Cintos", "Chapéus", "Lenços", "Óculos de sol"],
        index=0,
        placeholder="Selecione o produto..."
    )
elif categoria == "Calçados":
    tipo_produto = st.selectbox(
        "Selecione o tipo do Produto:",
        options=["Tênis", "Sandálias", "Botas", "Sapatos", "Sapatilhas"],
        index=0,
        placeholder="Selecione o produto..."
    )
else:
    tipo_produto = st.selectbox(
        "Selecione o tipo do Produto:",
        options=["Camisas", "Calças", "Vestidos", "Blusa Moletom", "Jaqueta", "Camisetas"],
        index=0,
        placeholder="Selecione o produto..."
    )

genero = st.radio("Gênero do produto:", ("Masculino", "Feminino", "Unissex"))

marca = st.text_input("Digite a Marca do Produto", placeholder="Digite a Marca do Produto...")

cor = st.text_input("Digite a Cor Principal do Produto", placeholder="Digite a Cor Principal do Produto...")

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

quantidade = st.number_input("Quantidade:", min_value=1, step=1)

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

    if not tipo_produto:
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
        novos_codigos = []
        for _ in range(quantidade):
            codigo = gerar_codigo()
            st.session_state.lista_codigos.append(codigo)
            novos_codigos.append(codigo)

        st.success(f"{quantidade} produto(s) cadastrado(s) com sucesso.")
        st.write("Código(s) gerado(s):", novos_codigos)

if st.session_state.lista_codigos:
    st.markdown("Código(s) cadastrados:")
    st.write(st.session_state.lista_codigos)


# chatbot - tem q colocar nome ainda
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 Assistente Estoque360")

if "mostrar_chat" not in st.session_state:
    st.session_state.mostrar_chat = False

if st.sidebar.button("🛍️ Clique para falar com o Assistente", key="icone_chat"):
    st.session_state.mostrar_chat = not st.session_state.mostrar_chat

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
