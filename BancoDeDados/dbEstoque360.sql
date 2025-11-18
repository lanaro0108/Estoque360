-- create database dbestoque360
-- use dbestoque360

create table generos (
    id int not null auto_increment primary key,
    genero enum('masculino', 'feminino', 'unissex') not null
);

create table marcas (
    id int not null auto_increment primary key,
    nomeMarca varchar(60) not null
);

create table cores (
    id int not null auto_increment primary key,
    nomeCor varchar(60) not null
);

create table categoria (
    id int not null auto_increment primary key,
    nome varchar(30) not null unique
);

insert into categoria (nome) values
('calçados'),
('vestuário');

create table tipo_produto (
    id int not null auto_increment primary key,
    nome varchar(40) not null unique,
    id_categoria int not null,
    foreign key (id_categoria) references categoria(id)
);

insert into tipo_produto (nome, id_categoria) values
('calçado adulto', 1),
('calças', 2),
('jaqueta', 2),
('camisas', 2),
('camisetas', 2),
('blusa moletom', 2),
('vestidos', 2);

create table tamanho (
    id int not null auto_increment primary key,
    tamanho varchar(10) not null,
    tipo enum('calcado', 'letra', 'numerico', 'infantil') not null
);

insert into tamanho (tamanho, tipo) values
('33', 'calcado'), ('34', 'calcado'), ('35', 'calcado'),
('36', 'calcado'), ('37', 'calcado'), ('38', 'calcado'),
('39', 'calcado'), ('40', 'calcado'), ('41', 'calcado'),
('42', 'calcado'), ('43', 'calcado'), ('44', 'calcado'),
('45', 'calcado'), ('46', 'calcado');

insert into tamanho (tamanho, tipo) values
('pp', 'letra'), ('p', 'letra'), ('m', 'letra'),
('g', 'letra'), ('gg', 'letra'), ('xg', 'letra'),
('xxg', 'letra'), ('xxxg', 'letra');

insert into tamanho (tamanho, tipo) values
('34', 'numerico'), ('36', 'numerico'), ('38', 'numerico'),
('40', 'numerico'), ('42', 'numerico'), ('44', 'numerico'),
('46', 'numerico'), ('48', 'numerico'), ('50', 'numerico'),
('52', 'numerico'), ('54', 'numerico'), ('56', 'numerico'),
('58', 'numerico'), ('60', 'numerico');

insert into tamanho (tamanho, tipo) values
('2', 'infantil'), ('4', 'infantil'), ('6', 'infantil'),
('8', 'infantil'), ('10', 'infantil'), ('12', 'infantil'),
('14', 'infantil'), ('16', 'infantil');

create table tipo_produto_tamanho (
    id_tipo_produto int not null,
    id_tamanho int not null,
    primary key (id_tipo_produto, id_tamanho),
    foreign key (id_tipo_produto) references tipo_produto(id),
    foreign key (id_tamanho) references tamanho(id)
);

insert into tipo_produto_tamanho (id_tipo_produto, id_tamanho)
select tp.id, t.id from tipo_produto tp
join tamanho t on t.tipo = 'calcado'
where tp.nome = 'calçado adulto';

insert into tipo_produto_tamanho (id_tipo_produto, id_tamanho)
select tp.id, t.id from tipo_produto tp
join tamanho t on t.tipo = 'numerico'
where tp.nome in ('calças', 'jaqueta');

insert into tipo_produto_tamanho (id_tipo_produto, id_tamanho)
select tp.id, t.id from tipo_produto tp
join tamanho t on t.tipo = 'letra'
where tp.nome in ('camisas', 'camisetas', 'blusa moletom');

insert into tipo_produto_tamanho (id_tipo_produto, id_tamanho)
select tp.id, t.id from tipo_produto tp
join tamanho t on t.tipo in ('infantil', 'letra')
where tp.nome = 'vestidos';

create table produtos (
    id int not null auto_increment primary key,
    id_categoria int not null,
    id_genero int not null,
    id_marca int not null,
    id_cor int not null,
    id_tipo_produto int not null,
    id_tamanho int not null,
    precocusto decimal(10, 2) not null,
    precovenda decimal(10, 2) not null,
    foreign key (id_categoria) references categoria(id),
    foreign key (id_genero) references generos(id),
    foreign key (id_marca) references marcas(id),
    foreign key (id_cor) references cores(id),
    foreign key (id_tipo_produto) references tipo_produto(id),
    foreign key (id_tamanho) references tamanho(id)
);

-- Tabelas de localização (removida duplicação de estados)
create table estados (
    id int not null auto_increment primary key,
    sigla char(2) not null,
    nomeEstado varchar(40) not null
);

insert into estados (sigla, nomeEstado) values
('AC', 'Acre'),
('AL', 'Alagoas'),
('AM', 'Amazonas'),
('AP', 'Amapá'),
('BA', 'Bahia'),
('CE', 'Ceará'),
('DF', 'Distrito Federal'),
('ES', 'Espírito Santo'),
('GO', 'Goiás'),
('MA', 'Maranhão'),
('MG', 'Minas Gerais'),
('MS', 'Mato Grosso do Sul'),
('MT', 'Mato Grosso'),
('PA', 'Pará'),
('PB', 'Paraíba'),
('PE', 'Pernambuco'),
('PI', 'Piauí'),
('PR', 'Paraná'),
('RJ', 'Rio de Janeiro'),
('RN', 'Rio Grande do Norte'),
('RO', 'Rondônia'),
('RR', 'Roraima'),
('RS', 'Rio Grande do Sul'),
('SC', 'Santa Catarina'),
('SE', 'Sergipe'),
('SP', 'São Paulo'),
('TO', 'Tocantins');

create table cidades (
    id int not null auto_increment primary key,
    nomeCidade varchar(120) not null,
    id_estado int not null,
    foreign key (id_estado) references estados(id)
);

create table bairros (
    id int not null auto_increment primary key,
    nomeBairro varchar(120) not null
);

create table tiposLogradouro (
    id int not null auto_increment primary key,
    tipoLogradouro varchar(120) not null
);

create table logradouros (
    id int not null auto_increment primary key,
    logradouro varchar(120) not null
);

create table cepNorm (
    cep varchar(10) not null primary key,
    id_estado int not null,
    id_cidade int not null,
    id_bairro int not null,
    id_tipoLogradouro int not null,
    id_logradouro int not null,
    foreign key (id_estado) references estados(id),
    foreign key (id_cidade) references cidades(id),
    foreign key (id_bairro) references bairros(id),
    foreign key (id_tipoLogradouro) references tiposLogradouro(id),
    foreign key (id_logradouro) references logradouros(id)
);

create table enderecos (
    id int not null auto_increment primary key,
    cep varchar(10) not null,
    numero varchar(12) not null,
    complemento varchar(120),
    foreign key (cep) references cepNorm(cep)
);

create table telefones (
    id int not null auto_increment primary key,
    numTelefone varchar(20)
);

create table emails (
    id int not null auto_increment primary key,
    email varchar(120) not null
);

create table fornecedores (
    cnpj varchar(18) not null primary key,
    nome varchar(120),
    id_endereco int not null,
    id_telefone int not null,
    id_email int not null,
    foreign key (id_endereco) references enderecos(id),
    foreign key (id_telefone) references telefones(id),
    foreign key (id_email) references emails(id)
);
