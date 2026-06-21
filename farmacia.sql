-- Criação das tabelas

create table produtos (
	id	serial primary key,
	nome	varchar(50) not null,
	categoria	varchar(50) not null,
	valor	numeric(10,2)
);

create table fornecedores (
	cnpj	varchar(14) primary key not null,
	nome	varchar(50) not null,
	telefone	varchar(11) not null,
	constraint	chk_cnpj_format
		check (cnpj ~ '^[0-9]{14}$')
);

create table compras (
	id	serial primary key,
	datacompra	date not null,
	cnpjfornecedor	varchar(14) not null,
	foreign key (cnpjfornecedor) references fornecedores(cnpj),
	constraint	chk_cnpj_format
		check (cnpjfornecedor ~ '^[0-9]{14}$')
);

create table estoque (
	idproduto	int primary key not null,
	quantidade	int not null,
	foreign key (idproduto) references produtos (id)
);

create table itenscompra (
	id	serial primary key,
	idproduto	int not null,
	idcompra	int not null,
	quantidade	int not null,
	precounitario	numeric(10,2) not null,
	subtotal	numeric(10,2) not null,
	foreign key (idproduto) references produtos (id),
	foreign key (idcompra) references compras (id)
);

create table movimentacaoestoque (
	id	serial primary key,
	idproduto	int,
	tipo	varchar(50) not null,
	quantidade	int not null,
	data	date not null,
	idcompra	int not null,
	foreign key (idproduto) references produtos (id),
	foreign key (idcompra) references compras (id)
);

-- Inserção dos dados

insert into fornecedores (cnpj, nome, telefone) values
('11111111000101','Distribuidora Farma Sul','48999990001'),
('22222222000102','MedPlus Distribuidora','48999990002'),
('33333333000103','Saúde Brasil','48999990003'),
('44444444000104','Farmalog','48999990004'),
('55555555000105','BioMedic','48999990005'),
('66666666000106','PharmaTech','48999990006'),
('77777777000107','Drogaria Supply','48999990007'),
('88888888000108','Vida Farma','48999990008'),
('99999999000109','MediCenter','48999990009'),
('10101010000110','Distribuidora Vida','48999990010');

insert into produtos (nome, categoria, valor) values
('Paracetamol 500mg','Analgésico',10.50),
('Ibuprofeno 600mg','Anti-inflamatório',18.90),
('Dipirona 1g','Analgésico',8.00),
('Amoxicilina 500mg','Antibiótico',25.90),
('Xarope para Tosse','Respiratório',15.50),
('Vitamina C','Suplemento',12.00),
('Álcool em Gel','Higiene',7.50),
('Termômetro Digital','Equipamento',35.00),
('Omeprazol 20mg','Digestivo',20.00),
('Loratadina','Antialérgico',14.00);

insert into compras (datacompra, cnpjfornecedor) values
('2026-06-01','11111111000101'),
('2026-06-02','22222222000102'),
('2026-06-03','33333333000103'),
('2026-06-04','44444444000104'),
('2026-06-05','55555555000105'),
('2026-06-06','66666666000106'),
('2026-06-07','77777777000107'),
('2026-06-08','88888888000108'),
('2026-06-09','99999999000109'),
('2026-06-10','10101010000110');

insert into estoque (idproduto, quantidade) values
(1,100),
(2,80),
(3,120),
(4,60),
(5,50),
(6,90),
(7,200),
(8,30),
(9,70),
(10,65);

insert into itenscompra (idproduto, idcompra, quantidade, precounitario, subtotal) values
(1,1,20,8.00,160.00),
(2,2,15,15.00,225.00),
(3,3,30,5.00,150.00),
(4,4,10,22.00,220.00),
(5,5,12,12.00,144.00),
(6,6,20,9.00,180.00),
(7,7,50,5.00,250.00),
(8,8,8,30.00,240.00),
(9,9,14,16.00,224.00),
(10,10,18,10.00,180.00);

insert into movimentacaoestoque (idproduto, tipo, quantidade, data, idcompra) values
(1,'ENTRADA',20,'2026-06-01',1),
(2,'ENTRADA',15,'2026-06-02',2),
(3,'ENTRADA',30,'2026-06-03',3),
(4,'ENTRADA',10,'2026-06-04',4),
(5,'ENTRADA',12,'2026-06-05',5),
(6,'ENTRADA',20,'2026-06-06',6),
(7,'ENTRADA',50,'2026-06-07',7),
(8,'ENTRADA',8,'2026-06-08',8),
(9,'ENTRADA',14,'2026-06-09',9),
(10,'ENTRADA',18,'2026-06-10',10);

-- Criação das Views
create view verificar_estoque as
select produtos.nome, estoque.quantidade
from produtos, estoque
where produtos.id = estoque.idproduto;

create view verificar_compras as
select produtos.nome, itenscompra.quantidade, itenscompra.precounitario, itenscompra.subtotal
from produtos, itenscompra
where produtos.id = itenscompra.idproduto;

create view verificar_movimentacao as
select produtos.nome, movimentacaoestoque.tipo, movimentacaoestoque.data
from produtos, movimentacaoestoque
where produtos.id = movimentacaoestoque.idproduto
order by movimentacaoestoque.id desc;
select * from verificar_movimentacao

-- Criação das procedures
create procedure cadastrar_fornecedor (
	f_cnpj varchar,
	f_nome varchar,
	f_telefone varchar
)
language plpgsql as $$
begin
	if trim(coalesce(f_cnpj, '')) = '' then
		raise exception 'CNPJ do fornecedor não informado!';
	elsif trim(coalesce(f_nome, '')) = '' then
		raise exception 'Nome do fornecedor não foi informado!';
	elsif trim(coalesce(f_telefone, '')) = '' then
		raise exception 'Telefone do fornecedor não foi informado!';
	else
		insert into fornecedores (
			cnpj,
			nome,
			telefone
		) values (
			f_cnpj,
			f_nome,
			f_telefone
		);
	
		raise notice 'Fornecedor cadastrado!';
	end if;
end;
$$;

call cadastrar_fornecedor('64972346180001', 'CIMED', '4840028922');
call cadastrar_fornecedor('', 'Da Esquina', '4821654992'); -- Essa linha vai gerar um erro

create or replace procedure atualizar_estoque (
	cod_produto int,
	nova_quantidade int,
	tipo text
)
language plpgsql as $$
declare
	estoque_produto int;
	tipo_tratado text;
begin
	tipo_tratado = upper(trim(coalesce(tipo, '')));

	if tipo_tratado not in ('SAIDA', 'ENTRADA') then
		raise exception 'Tipo invalido. Utilize "saida" ou "entrada".';
	elsif tipo_tratado = 'SAIDA' then
		select quantidade into estoque_produto
		from estoque where idproduto = cod_produto;

		if coalesce(estoque_produto, 0) < nova_quantidade then
			raise exception 'Produto sem estoque!';
		else
			update estoque
			set quantidade = quantidade - nova_quantidade
			where idproduto = cod_produto;
			raise notice 'Estoque atualizado!';
		end if;
	elsif tipo_tratado = 'ENTRADA' then
		update estoque
		set quantidade = quantidade + nova_quantidade
		where idproduto = cod_produto;
		raise notice 'Estoque atualizado!';
	end if;
end;
$$;

call atualizar_estoque(1, 10, 'entrada');
call atualizar_estoque(4, 10, 'saida');

create procedure cadastrar_produto (
	p_nome	varchar,
	p_categoria	varchar,
	p_valor	numeric
)
language plpgsql as $$
begin
	if trim(coalesce(p_nome, '')) = '' then
		raise notice 'Nome do produto não informado!';
	elsif trim(coalesce(p_categoria, '')) = '' then
		raise notice 'Categoria do produto não informada!';
	elsif coalesce(p_valor, 0) <= 0 then
		raise notice 'Valor do produto não informado!';
	else
		insert into produtos (
			nome,
			categoria,
			valor
		) values (
			p_nome,
			p_categoria,
			p_valor
		);
		raise notice 'Produto cadastrado!';
	end if;
end;
$$;

-- call cadastrar_produto('Allegra', 'Antialérgico', '30');
call cadastrar_produto('Aprazolan', 'Ansiolítico', null); -- Essa linha retorna um erro
select * from produtos order by id

create or replace procedure registrar_compra_completa(
    p_data date,
    p_cnpj varchar(14),
    p_id_produto int,
    p_qtd int,
    p_preco numeric
)
language plpgsql as $$
declare
    v_id_compra int;
begin
    -- validações básicas
    if p_cnpj is null or p_data is null or p_id_produto is null then
        raise exception 'Data, CNPJ e ID do produto são obrigatórios.';
    end if;

    insert into compras (datacompra, cnpjfornecedor)
    values (p_data, p_cnpj)
    returning id into v_id_compra;

    insert into itenscompra (idproduto, idcompra, quantidade, precounitario, subtotal)
    values (p_id_produto, v_id_compra, p_qtd, p_preco, 0);

    update estoque
    set quantidade = quantidade + p_qtd
    where idproduto = p_id_produto;

    insert into movimentacaoestoque (idproduto, tipo, quantidade, data, idcompra)
    values (p_id_produto, 'ENTRADA', p_qtd, p_data, v_id_compra);

    raise notice 'Compra realizada com sucesso! Código da compra: %', v_id_compra;
end;
$$;

-- Criação das Functions

create or replace function consultar_valor_total_estoque( p_id int ) returns text
language plpgsql as $$
declare
	quantidade int;
	prod_nome text;
	valor_total numeric;
	valor_unitario numeric;
begin
	select produtos.nome , estoque.quantidade, produtos.valor
	into prod_nome, quantidade, valor_unitario
	from produtos, estoque
	where produtos.id = p_id	
	and produtos.id = estoque.idproduto;

	valor_total = quantidade * valor_unitario;

	return format(
		'%s tem %s unidades em estoque. Um total de %s.',
		prod_nome,
		quantidade,
		'R$ ' || to_char(valor_total, 'FM99G999D00')); -- Formata para a moeda nacional.
end;
$$;

select consultar_valor_total_estoque(5);

select * from itenscompra

create or replace function calcular_total_compra( id_compra int ) returns text
language plpgsql as $$
declare
	data_compra date;
	nome_fornecedor text;
	total_compras numeric;
begin
	if not exists (select 1 from compras where id = id_compra) then
		raise exception 'Compra nao encontrada.';
	else	
		select compras.datacompra, fornecedores.nome, sum(itenscompra.subtotal)
		into data_compra, nome_fornecedor, total_compras
		from compras
		inner join fornecedores on fornecedores.cnpj = compras.cnpjfornecedor
		inner join itenscompra on itenscompra.idcompra = compras.id
		where compras.id = id_compra
		group by compras.id, compras.datacompra, fornecedores.nome;
	end if;

	return format(E'Compra feita em: %s | Fornecedor: %s | Total da compra: %s',
		to_char(data_compra, 'DD/MM/YYYY'),
		nome_fornecedor,
		'R$ ' || to_char(total_compras, 'FM999G999D00'));
end;
$$;

select calcular_total_compra(8);
select calcular_total_compra(88); -- Retorna erro

create or replace function consultar_estoque( id_produto int ) returns text
language plpgsql as $$
declare
	prod_nome text;
	quantidade int;
begin
	if not exists (select 1 from produtos where id = id_produto) then
		raise exception 'Produto nao encontrado.';
	else
		select produtos.nome, estoque.quantidade
		into prod_nome, quantidade
		from produtos
		inner join estoque on estoque.idproduto = produtos.id
		where produtos.id = id_produto;
	end if;

	return format(E'%s tem %s unidades em estoque.', prod_nome, quantidade);
end;
$$;

select consultar_estoque(8);

-- Criaçao das Triggers

create or replace function trg_calcular_subtotal() returns trigger
language plpgsql as $$
begin
	new.subtotal := new.quantidade * new.precounitario;
	return new;
end;
$$;

create trigger calcular_subtotal
before insert or update
on itenscompra
for each row
execute function trg_calcular_subtotal();

create or replace function trg_validar_estoque() returns trigger
language plpgsql as $$
begin
	if new.quantidade < 0 then
		raise exception 'o estoque nao pode ficar negativo.';
	end if;

	return new;
end;
$$;

create trigger validar_estoque
before insert or update
on estoque
for each row
execute function trg_validar_estoque();

create or replace function trg_criar_estoque() returns trigger
language plpgsql as $$
begin
	insert into estoque (
		idproduto,
		quantidade
	) values (
		new.id,
		0
	);

	return new;
end;
$$;

create trigger criar_estoque_produto
after insert
on produtos
for each row
execute function trg_criar_estoque();

create or replace function trg_log_movimentacao_manual() returns trigger
language plpgsql as $$
declare
    diferenca int;
    tipo_mov varchar(20);
begin
    diferenca = new.quantidade - old.quantidade;

    if diferenca = 0 then
        return new;
    end if;

    if diferenca > 0 then
        tipo_mov = 'ENTRADA';
    else
        tipo_mov = 'SAIDA';
        diferenca = abs(diferenca);
    end if;

    insert into movimentacaoestoque (idproduto, tipo, quantidade, data, idcompra)
    values (new.idproduto, tipo_mov, diferenca, current_date, null);

    return new;
end;
$$;

create trigger log_mov_manual
after update on estoque
for each row
execute function trg_log_movimentacao_manual();

-- update movimentacaoestoque
-- set tipo = 'SAIDA'
-- where id = 15
-- select * from movimentacaoestoque
