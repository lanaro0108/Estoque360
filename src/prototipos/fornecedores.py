from database import conectar

def registrar_compra(cnpj_fornecedor, produtos): 
    """
    produtos = lista de dicts: [{"id_produto":1,"quantidade":5,"valor_unit":10.50}, ...]
    """
    db = conectar()
    cursor = db.cursor()
    cursor.execute("INSERT INTO compras_fornecedor (cnpj_fornecedor) VALUES (?)", (cnpj_fornecedor,))
    id_compra = cursor.lastrowid

    for p in produtos:
        cursor.execute("""
            INSERT INTO compras_fornecedor_itens (id_compra, id_produto, quantidade, valor_unit)
            VALUES (?,?,?,?)
        """, (id_compra, p["id_produto"], p["quantidade"], p["valor_unit"]))
        #atualizar estoque
        cursor.execute("SELECT quantidade FROM estoque_atual WHERE produto_id=?", (p["id_produto"],))
        resultado = cursor.fetchone()
        if resultado:
            nova_qtd = resultado[0] + p["quantidade"]
            cursor.execute("UPDATE estoque_atual SET quantidade=? WHERE produto_id=?", (nova_qtd, p["id_produto"]))
        else:
            cursor.execute("INSERT INTO estoque_atual (produto_id, quantidade) VALUES (?,?)", (p["id_produto"], p["quantidade"]))
    db.commit()
    cursor.close()
    db.close()
    return id_compra