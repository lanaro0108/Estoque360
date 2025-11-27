-- create database dbestoque360
-- use dbestoque360

create table generos (
    id int auto_increment primary key,
    genero enum('masculino','feminino','unissex') not null
);

insert into generos (genero) values 
('masculino'), ('feminino'), ('unissex');

create table marcas (
    id int auto_increment primary key,
    nomemarca varchar(255) not null
);

create table cores (
    id int auto_increment primary key,
    nomecor varchar(255) not null
);

create table categoria (
    id int auto_increment primary key,
    nome varchar(255) not null unique
);

insert into categoria (nome) values ('calçados'), ('vestuário');

create table tipo_produto (
    id int auto_increment primary key,
    nome varchar(255) not null unique,
    id_categoria int not null,
    foreign key (id_categoria) references categoria(id)
);

insert into tipo_produto (nome, id_categoria) values
('tênis', 1), ('chuteira', 1), ('sapatênis', 1), ('sandália', 1),
('chinelo', 1), ('bota', 1), ('sapato social', 1), ('crocs', 1),
('calças', 2), ('camisas', 2), ('camisetas', 2), ('blusa moletom', 2),
('vestidos', 2), ('shorts', 2), ('saia', 2), ('jaqueta', 2),
('blazer', 2), ('regata', 2);

create table tamanho (
    id int auto_increment primary key,
    tamanho varchar(20) not null,
    tipo enum('calcado','letra','numerico','infantil') not null
);

insert into tamanho (tamanho, tipo) values
('33','calcado'), ('34','calcado'), ('35','calcado'), ('36','calcado'),
('37','calcado'), ('38','calcado'), ('39','calcado'), ('40','calcado'),
('41','calcado'), ('42','calcado'), ('43','calcado'), ('44','calcado'),
('45','calcado'), ('46','calcado'),
('pp','letra'), ('p','letra'), ('m','letra'), ('g','letra'),
('gg','letra'), ('xg','letra'), ('xxg','letra'), ('xxxg','letra'),
('34','numerico'), ('36','numerico'), ('38','numerico'), ('40','numerico'),
('42','numerico'), ('44','numerico'), ('46','numerico'), ('48','numerico'),
('50','numerico'), ('52','numerico'), ('54','numerico'), ('56','numerico'),
('58','numerico'), ('60','numerico'),
('2','infantil'), ('4','infantil'), ('6','infantil'), ('8','infantil'),
('10','infantil'), ('12','infantil'), ('14','infantil'), ('16','infantil');

create table tipo_produto_tamanho (
    id_tipo_produto int not null,
    id_tamanho int not null,
    primary key (id_tipo_produto, id_tamanho),
    foreign key (id_tipo_produto) references tipo_produto(id),
    foreign key (id_tamanho) references tamanho(id)
);

create table produtos (
    id int auto_increment primary key,
    id_categoria int not null,
    id_genero int not null,
    id_marca int not null,
    id_cor int not null,
    id_tipo_produto int not null,
    id_tamanho int not null,
    precocusto decimal(10,2) not null,
    precovenda decimal(10,2) not null,
    foreign key (id_categoria) references categoria(id),
    foreign key (id_genero) references generos(id),
    foreign key (id_marca) references marcas(id),
    foreign key (id_cor) references cores(id),
    foreign key (id_tipo_produto) references tipo_produto(id),
    foreign key (id_tamanho) references tamanho(id)
);

create table estados (
    id int auto_increment primary key,
    sigla char(2) not null,
    nomeestado varchar(255) not null
);

insert into estados (sigla, nomeestado) values
('ac','acre'),('al','alagoas'),('am','amazonas'),('ap','amapá'),
('ba','bahia'),('ce','ceará'),('df','distrito federal'),('es','espírito santo'),
('go','goiás'),('ma','maranhão'),('mg','minas gerais'),('ms','mato grosso do sul'),
('mt','mato grosso'),('pa','pará'),('pb','paraíba'),('pe','pernambuco'),
('pi','piauí'),('pr','paraná'),('rj','rio de janeiro'),('rn','rio grande do norte'),
('ro','rondônia'),('rr','roraima'),('rs','rio grande do sul'),
('sc','santa catarina'),('se','sergipe'),('sp','são paulo'),('to','tocantins');

create table cidades (
    id int auto_increment primary key,
    nomecidade varchar(255) not null,
    id_estado int not null,
    foreign key (id_estado) references estados(id)
);

create table bairros (
    id int auto_increment primary key,
    nomebairro varchar(255) not null
);

create table tiposlogradouro (
    id int auto_increment primary key,
    tipologradouro varchar(255) not null
);

create table logradouros (
    id int auto_increment primary key,
    logradouro varchar(255) not null
);

create table cepnorm (
    cep varchar(20) primary key,
    id_estado int not null,
    id_cidade int not null,
    id_bairro int not null,
    id_tipologradouro int not null,
    id_logradouro int not null,
    foreign key (id_estado) references estados(id),
    foreign key (id_cidade) references cidades(id),
    foreign key (id_bairro) references bairros(id),
    foreign key (id_tipologradouro) references tiposlogradouro(id),
    foreign key (id_logradouro) references logradouros(id)
);

create table enderecos (
    id int auto_increment primary key,
    cep varchar(20) not null,
    numero varchar(20) not null,
    complemento varchar(255),
    foreign key (cep) references cepnorm(cep)
);

create table telefones (
    id int auto_increment primary key,
    numtelefone varchar(50) not null
);

create table emails (
    id int auto_increment primary key,
    email varchar(255) not null
);

create table fornecedores (
    cnpj varchar(20) primary key,
    nome varchar(255) not null,
    id_endereco int not null,
    id_telefone int not null,
    id_email int not null,
    foreign key (id_endereco) references enderecos(id),
    foreign key (id_telefone) references telefones(id),
    foreign key (id_email) references emails(id)
);

create table clientes (
    cpf varchar(20) primary key,
    nome varchar(255) not null,
    id_endereco int not null,
    id_telefone int not null,
    id_email int not null,
    foreign key (id_endereco) references enderecos(id),
    foreign key (id_telefone) references telefones(id),
    foreign key (id_email) references emails(id)
);

create table forma_pgto (
    id int auto_increment primary key,
    formapgto varchar(50) not null
);

insert into forma_pgto (formapgto) values
('dinheiro'), ('cartão de crédito'), ('cartão de débito'), ('pix');

create table vendas (
    id int auto_increment primary key,
    id_cliente varchar(20) not null,
    id_formapgto int not null,
    data_venda timestamp default current_timestamp,
    foreign key (id_cliente) references clientes(cpf),
    foreign key (id_formapgto) references forma_pgto(id)
);

create table vendas_itens (
    id int auto_increment primary key,
    id_venda int not null,
    id_produto int not null,
    quantidade int not null,
    valor_unit decimal(10,2) not null,
    foreign key (id_venda) references vendas(id),
    foreign key (id_produto) references produtos(id)
);

create table compras_fornecedor (
    id int auto_increment primary key,
    cnpj_fornecedor varchar(20) not null,
    data_compra timestamp default current_timestamp,
    nota_fiscal varchar(255),
    foreign key (cnpj_fornecedor) references fornecedores(cnpj)
);

create table compras_fornecedor_itens (
    id int auto_increment primary key,
    id_compra int not null,
    id_produto int not null,
    quantidade int not null,
    valor_unit decimal(10,2) not null,
    foreign key (id_compra) references compras_fornecedor(id),
    foreign key (id_produto) references produtos(id)
);

create table estoque_atual (
    id int auto_increment primary key,
    produto_id int not null,
    quantidade int not null,
    foreign key (produto_id) references produtos(id)
);

create table balanco_financeiro (
    id int auto_increment primary key,
    data_movimento timestamp not null,
    tipo enum('entrada','saida') not null,
    valor decimal(10,2) not null,
    referencia varchar(255) not null
);
