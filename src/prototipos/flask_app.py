import csv
import io
import os
from typing import Iterable, List

from dotenv import load_dotenv
from flask import (
    Flask,
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from clientes import registrar_cliente, registrar_venda
from database import conectar, criar_tabelas
from fornecedores import registrar_compra, registrar_fornecedor
from produtos import salvar_estoque, salvar_produto

load_dotenv()


def create_app() -> Flask:
    criar_tabelas()

    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev")

    def fetch_options(table: str, column: str) -> List[str]:
        db = conectar()
        cursor = db.cursor()
        cursor.execute(f"SELECT {column} FROM {table}")
        options = [row[0] for row in cursor.fetchall()]
        db.close()
        return options

    def fetch_tipos_by_categoria(categoria: str) -> List[str]:
        if not categoria:
            return []

        db = conectar()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT tp.nome FROM tipo_produto tp
            JOIN categoria c ON tp.id_categoria = c.id
            WHERE c.nome = ?
            ORDER BY tp.nome
            """,
            (categoria,),
        )
        tipos = [row[0] for row in cursor.fetchall()]
        db.close()
        return tipos

    def gerar_csv(nome_arquivo: str, cabecalho: Iterable[str], linhas: Iterable[Iterable]) -> Response:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(cabecalho)
        for linha in linhas:
            writer.writerow(linha)
        resposta = Response(buffer.getvalue(), mimetype="text/csv")
        resposta.headers["Content-Disposition"] = f"attachment; filename={nome_arquivo}"
        buffer.close()
        return resposta

    def buscar_produto_por_tipo(nome_tipo: str) -> int | None:
        db = conectar()
        cursor = db.cursor()
        cursor.execute(
            "SELECT p.id FROM produtos p JOIN tipo_produto tp ON p.id_tipo_produto = tp.id WHERE tp.nome LIKE ?",
            (f"%{nome_tipo}%",),
        )
        resultado = cursor.fetchone()
        db.close()
        return resultado[0] if resultado else None

    def extrair_lista(nome_chave: str) -> List[dict]:
        lista = session.get(nome_chave, [])
        if not isinstance(lista, list):
            lista = []
        return lista

    def contar_registros(tabela: str) -> int:
        db = conectar()
        cursor = db.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
        total = cursor.fetchone()[0]
        cursor.close()
        db.close()
        return total

    @app.route("/")
    def index():
        return redirect(url_for("produtos"))

    @app.route("/preview")
    def preview():
        demo_produto = {
            "categoria": "vestuário",
            "tipo": "camisetas",
            "genero": "unissex",
            "tamanhos": ["PP", "P", "M", "G", "GG"],
            "campos_obrigatorios": ["marca", "cor", "tamanho"],
        }

        demo_compra = {
            "fornecedor": "00.000.000/0000-00",
            "itens": [{"nome": "camisetas", "quantidade": 20, "valor_unit": 29.9}],
        }

        demo_venda = {
            "cliente": "000.000.000-00",
            "forma_pgto": "Cartão de crédito",
            "itens": [{"nome": "camisetas", "quantidade": 2, "valor_unit": 59.9}],
        }

        demo_estoque = [
            {"tipo_produto": "camisetas", "marca": "Acme", "cor": "preta", "tamanho": "M", "quantidade": 50},
            {"tipo_produto": "calças", "marca": "Acme", "cor": "azul", "tamanho": "42", "quantidade": 12},
        ]

        return render_template(
            "preview.html",
            demo_produto=demo_produto,
            demo_compra=demo_compra,
            demo_venda=demo_venda,
            demo_estoque=demo_estoque,
        )

    @app.route("/downloads")
    def downloads():
        contagens = {
            "produtos": contar_registros("produtos"),
            "compras": contar_registros("compras_fornecedor"),
            "vendas": contar_registros("vendas"),
            "estoque": contar_registros("estoque_atual"),
        }
        return render_template("downloads.html", contagens=contagens)

    @app.route("/downloads/<alvo>.csv")
    def baixar_csv(alvo: str):
        db = conectar()
        cursor = db.cursor()

        if alvo == "produtos":
            cursor.execute(
                """
                SELECT p.id, c.nome as categoria, tp.nome as tipo, g.genero, m.nomemarca, cor.nomecor, t.tamanho,
                       p.precocusto, p.precovenda
                FROM produtos p
                LEFT JOIN categoria c ON p.id_categoria = c.id
                LEFT JOIN tipo_produto tp ON p.id_tipo_produto = tp.id
                LEFT JOIN generos g ON p.id_genero = g.id
                LEFT JOIN marcas m ON p.id_marca = m.id
                LEFT JOIN cores cor ON p.id_cor = cor.id
                LEFT JOIN tamanho t ON p.id_tamanho = t.id
                ORDER BY p.id DESC
                """
            )
            linhas = cursor.fetchall()
            cabecalho = [
                "id",
                "categoria",
                "tipo",
                "genero",
                "marca",
                "cor",
                "tamanho",
                "preco_custo",
                "preco_venda",
            ]
            resposta = gerar_csv("produtos.csv", cabecalho, linhas)

        elif alvo == "estoque":
            cursor.execute(
                """
                SELECT p.id, tp.nome as tipo_produto, m.nomemarca as marca, c.nomecor as cor, t.tamanho, e.quantidade
                FROM produtos p
                JOIN tipo_produto tp ON p.id_tipo_produto = tp.id
                JOIN marcas m ON p.id_marca = m.id
                JOIN cores c ON p.id_cor = c.id
                JOIN tamanho t ON p.id_tamanho = t.id
                JOIN estoque_atual e ON p.id = e.produto_id
                ORDER BY tp.nome, m.nomemarca
                """
            )
            linhas = cursor.fetchall()
            cabecalho = ["produto_id", "tipo", "marca", "cor", "tamanho", "quantidade"]
            resposta = gerar_csv("estoque.csv", cabecalho, linhas)

        elif alvo == "compras":
            cursor.execute(
                """
                SELECT cf.id, cf.cnpj_fornecedor, tp.nome as tipo_produto, m.nomemarca, c.nomecor, t.tamanho,
                       itens.quantidade, itens.valor_unit
                FROM compras_fornecedor cf
                JOIN compras_fornecedor_itens itens ON cf.id = itens.id_compra
                JOIN produtos p ON itens.id_produto = p.id
                LEFT JOIN tipo_produto tp ON p.id_tipo_produto = tp.id
                LEFT JOIN marcas m ON p.id_marca = m.id
                LEFT JOIN cores c ON p.id_cor = c.id
                LEFT JOIN tamanho t ON p.id_tamanho = t.id
                ORDER BY cf.id DESC
                """
            )
            linhas = cursor.fetchall()
            cabecalho = [
                "id_compra",
                "cnpj_fornecedor",
                "tipo_produto",
                "marca",
                "cor",
                "tamanho",
                "quantidade",
                "valor_unit",
            ]
            resposta = gerar_csv("compras.csv", cabecalho, linhas)

        elif alvo == "vendas":
            cursor.execute(
                """
                SELECT v.id, v.id_cliente, v.id_formapgto, tp.nome as tipo_produto, m.nomemarca, c.nomecor, t.tamanho,
                       itens.quantidade, itens.valor_unit
                FROM vendas v
                JOIN vendas_itens itens ON v.id = itens.id_venda
                JOIN produtos p ON itens.id_produto = p.id
                LEFT JOIN tipo_produto tp ON p.id_tipo_produto = tp.id
                LEFT JOIN marcas m ON p.id_marca = m.id
                LEFT JOIN cores c ON p.id_cor = c.id
                LEFT JOIN tamanho t ON p.id_tamanho = t.id
                ORDER BY v.id DESC
                """
            )
            linhas = cursor.fetchall()
            cabecalho = [
                "id_venda",
                "cpf_cliente",
                "id_forma_pgto",
                "tipo_produto",
                "marca",
                "cor",
                "tamanho",
                "quantidade",
                "valor_unit",
            ]
            resposta = gerar_csv("vendas.csv", cabecalho, linhas)

        else:
            resposta = redirect(url_for("downloads"))

        cursor.close()
        db.close()
        return resposta

    @app.route("/api/tipos")
    def api_tipos():
        categoria = request.args.get("categoria", "")
        return jsonify({"tipos": fetch_tipos_by_categoria(categoria)})

    @app.route("/produtos", methods=["GET", "POST"])
    def produtos():
        categorias = fetch_options("categoria", "nome")
        generos = ["masculino", "feminino", "unissex"]
        categoria = request.form.get("categoria") or (categorias[0] if categorias else "")
        tipos = fetch_tipos_by_categoria(categoria)
        tipo_produto = request.form.get("tipo_produto") or (tipos[0] if tipos else "")
        genero = request.form.get("genero") or generos[0]
        marca = request.form.get("marca", "")
        cor = request.form.get("cor", "")
        tamanho = request.form.get("tamanho", "")

        tamanho_opcoes: List[str] = []
        tamanho_rotulo = ""

        if categoria == "calçados":
            tamanho_rotulo = "Selecione o tamanho do calçado"
            tamanho_opcoes = [str(t) for t in range(33, 47)]
        elif categoria == "vestuário":
            tamanhos_letras = ["PP", "P", "M", "G", "GG", "XG", "XXG", "XXXG"]
            tamanhos_numericos = [str(t) for t in range(34, 61, 2)]
            tamanhos_infantil = [str(t) for t in range(2, 18, 2)]

            categorias_numericos = ["calças", "shorts", "saia"]
            categorias_letras = [
                "camisas",
                "camisetas",
                "blusa moletom",
                "jaqueta",
                "blazer",
                "regata",
            ]

            if tipo_produto in categorias_numericos:
                tamanho_rotulo = "Selecione o tamanho (numérico)"
                tamanho_opcoes = tamanhos_numericos
            elif tipo_produto in categorias_letras:
                tamanho_rotulo = "Selecione o tamanho (letras)"
                tamanho_opcoes = tamanhos_letras
            elif tipo_produto == "vestidos":
                tamanho_rotulo = "Selecione o tamanho"
                tamanho_opcoes = tamanhos_infantil + tamanhos_letras

        if request.method == "POST" and request.form.get("action") == "salvar_produto":
            precocusto = request.form.get("precocusto", type=float)
            precovenda = request.form.get("precovenda", type=float)
            quantidade = request.form.get("quantidade", type=int)

            if not marca or not cor:
                flash("Marca e Cor são obrigatórios.", "warning")
            elif not tamanho_opcoes and categoria in {"calçados", "vestuário"}:
                flash("Selecione um tamanho válido para a categoria escolhida.", "warning")
            else:
                produto_id = salvar_produto(
                    categoria,
                    tipo_produto,
                    genero,
                    marca,
                    cor,
                    tamanho,
                    precocusto or 0.0,
                    precovenda or 0.0,
                )
                salvar_estoque(produto_id, quantidade or 1)
                flash(f"Produto {tipo_produto} cadastrado com sucesso!", "success")
                return redirect(url_for("produtos"))

        return render_template(
            "produtos.html",
            categorias=categorias,
            generos=generos,
            categoria=categoria,
            tipos=tipos,
            tipo_produto=tipo_produto,
            genero_selecionado=genero,
            marca=marca,
            cor=cor,
            tamanho=tamanho,
            tamanho_opcoes=tamanho_opcoes,
            tamanho_rotulo=tamanho_rotulo,
        )

    @app.route("/compras", methods=["GET", "POST"])
    def compras():
        produtos_compra = extrair_lista("produtos_compra")
        if request.method == "POST":
            action = request.form.get("action")
            if action == "registrar_fornecedor":
                cnpj = request.form.get("f_cnpj", "")
                nome = request.form.get("f_nome", "")
                cep = request.form.get("f_cep", "")
                if cnpj and nome and cep:
                    registrar_fornecedor(
                        cnpj,
                        nome,
                        cep,
                        request.form.get("f_numero", ""),
                        request.form.get("f_comp", ""),
                        request.form.get("f_tel", ""),
                        request.form.get("f_email", ""),
                    )
                    flash("Fornecedor cadastrado!", "success")
                else:
                    flash("Preencha os campos obrigatórios do fornecedor.", "warning")

            elif action == "adicionar_item":
                nome_tipo = request.form.get("c_prod_nome", "")
                quantidade = request.form.get("c_qtd", type=int) or 0
                valor_unit = request.form.get("c_valor", type=float) or 0.0
                produto_id = buscar_produto_por_tipo(nome_tipo)

                if produto_id:
                    produtos_compra.append(
                        {
                            "id_produto": produto_id,
                            "quantidade": quantidade,
                            "valor_unit": valor_unit,
                            "nome": nome_tipo,
                        }
                    )
                    flash("Produto adicionado à compra!", "success")
                else:
                    flash("Produto não encontrado. Tente o nome exato do tipo.", "warning")

            elif action == "finalizar_compra":
                cnpj_fornecedor = request.form.get("compra_cnpj", "")
                if produtos_compra:
                    try:
                        compra_id = registrar_compra(cnpj_fornecedor, produtos_compra)
                        flash(f"Compra {compra_id} registrada!", "success")
                        produtos_compra = []
                    except Exception as exc:  # noqa: BLE001
                        flash(f"Erro ao registrar compra: {exc}. Verifique o fornecedor.", "danger")
                else:
                    flash("A lista de itens está vazia.", "warning")

            session["produtos_compra"] = produtos_compra
            return redirect(url_for("compras"))

        return render_template("compras.html", produtos_compra=produtos_compra)

    @app.route("/vendas", methods=["GET", "POST"])
    def vendas():
        produtos_venda = extrair_lista("produtos_venda")

        db = conectar()
        cursor = db.cursor()
        cursor.execute("SELECT id, formapgto FROM forma_pgto")
        pgtos = {row[1]: row[0] for row in cursor.fetchall()}
        db.close()

        if request.method == "POST":
            action = request.form.get("action")
            if action == "registrar_cliente":
                cpf = request.form.get("c_cpf", "")
                nome = request.form.get("c_nome", "")
                cep = request.form.get("c_cep", "")
                if cpf and nome and cep:
                    registrar_cliente(
                        cpf,
                        nome,
                        cep,
                        request.form.get("c_numero", ""),
                        request.form.get("c_comp", ""),
                        request.form.get("c_tel", ""),
                        request.form.get("c_email", ""),
                    )
                    flash("Cliente cadastrado!", "success")
                else:
                    flash("Preencha os campos obrigatórios do cliente.", "warning")

            elif action == "adicionar_item_venda":
                nome_tipo = request.form.get("v_prod_nome", "")
                quantidade = request.form.get("v_qtd", type=int) or 0
                valor_unit = request.form.get("v_valor", type=float) or 0.0
                produto_id = buscar_produto_por_tipo(nome_tipo)

                if produto_id:
                    produtos_venda.append(
                        {
                            "id_produto": produto_id,
                            "quantidade": quantidade,
                            "valor_unit": valor_unit,
                            "nome": nome_tipo,
                        }
                    )
                    flash("Produto adicionado à venda!", "success")
                else:
                    flash("Produto não encontrado.", "warning")

            elif action == "finalizar_venda":
                cpf_cliente = request.form.get("venda_cpf", "")
                pgto_nome = request.form.get("pgto_nome", "")
                id_formapgto = pgtos.get(pgto_nome)

                if produtos_venda and id_formapgto:
                    try:
                        venda_id = registrar_venda(cpf_cliente, id_formapgto, produtos_venda)
                        flash(f"Venda {venda_id} registrada!", "success")
                        produtos_venda = []
                    except Exception as exc:  # noqa: BLE001
                        flash(f"Erro ao registrar venda: {exc}", "danger")
                else:
                    flash("Inclua itens e selecione a forma de pagamento.", "warning")

            session["produtos_venda"] = produtos_venda
            return redirect(url_for("vendas"))

        return render_template("vendas.html", produtos_venda=produtos_venda, pgtos=list(pgtos.keys()))

    @app.route("/estoque")
    def estoque():
        db = conectar()
        db.row_factory = None
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT p.id, tp.nome as tipo_produto, m.nomemarca as marca, c.nomecor as cor, t.tamanho, e.quantidade
            FROM produtos p
            JOIN tipo_produto tp ON p.id_tipo_produto = tp.id
            JOIN marcas m ON p.id_marca = m.id
            JOIN cores c ON p.id_cor = c.id
            JOIN tamanho t ON p.id_tamanho = t.id
            JOIN estoque_atual e ON p.id = e.produto_id
            ORDER BY tp.nome, m.nomemarca
            """
        )
        estoque_atual = cursor.fetchall()
        cursor.close()
        db.close()

        return render_template("estoque.html", estoque=estoque_atual)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
