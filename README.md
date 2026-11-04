# Sistema de Orçamentos — Grupo Dplay

Protótipo inicial (versão 0.1) feito com Python + Streamlit.

## O que já funciona
- Painel inicial com indicadores.
- Cadastro de orçamento com dados do órgão, fornecedor e produto.
- Cálculo automático do valor total.
- Geração de orçamento em PDF com a identidade visual da Dplay.
- Histórico de orçamentos salvos em SQLite.
- Opção de gerar novamente o PDF de um orçamento salvo.

> Esta primeira versão registra um produto por orçamento. A próxima evolução pode incluir vários itens, fotos dos produtos, edição de registros, usuários e armazenamento mais robusto.

## Como executar no GitHub Codespaces

No terminal, dentro desta pasta:

```bash
pip install -r requirements.txt
streamlit run app.py
```

O Codespaces mostrará a opção para abrir a aplicação na porta 8501.

## Arquivos
- `app.py`: código principal.
- `logo.png`: logomarca do Grupo Dplay.
- `requirements.txt`: bibliotecas necessárias.
- `orcamentos_dplay.db`: banco SQLite criado automaticamente na primeira execução.

## Observação
O banco SQLite local é adequado para protótipo e demonstração. Antes de uso simultâneo pela equipe ou publicação como sistema oficial, será necessário planejar hospedagem, backups, controle de acesso e persistência dos dados.
