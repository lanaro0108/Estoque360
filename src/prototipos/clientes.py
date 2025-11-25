from database import conectar

def registrar_venda(cpf_cliente, id_formapgto, produtos):
    """
    produtos = lista de dicts: [{"id_produto":1,"quantidade":2,"valor_unit":25.50}, ...]
    """
    db = conectar()
    cursor = db.cursor()
    cursor.execute("INSERT INTO vendas (id_cliente, id_formapgto) VALUES (?,?)", (cpf_cliente, id_formapgto))
    id_venda = cursor.lastrowid

    for p in produtos:
        #inserir item
        cursor.execute("""
            INSERT INTO vendas_itens (id_venda, id_produto, quantidade, valor_unit)
            VALUES (?,?,?,?)
        """, (id_venda, p["id_produto"], p["quantidade"], p["valor_unit"]))

        #atualizar estoque
        cursor.execute("SELECT quantidade FROM estoque_atual WHERE produto_id=?", (p["id_produto"],))
        resultado = cursor.fetchone()
        if resultado and resultado[0] >= p["quantidade"]:
            nova_qtd = resultado[0] - p["quantidade"]
            cursor.execute("UPDATE estoque_atual SET quantidade=? WHERE produto_id=?", (nova_qtd, p["id_produto"]))
        else:
            raise ValueError(f"Estoque insuficiente para produto {p['id_produto']}")
    db.commit()
    cursor.close()
    db.close()
    return id_venda
