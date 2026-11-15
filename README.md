# TAREFA-03

TAREFA 03 - JOGO DA FORCA COM INTERFACE GRÁFICA INE5201 - Introdução à
Ciência da Computação com Python

## Jogo da Forca

Jogo de forca para desktop feito em Python e Tkinter. A interface tem tons de
azul, botões arredondados, teclado virtual A-Z e suporte ao teclado físico.

## Requisitos

- Python 3.10 ou superior
- Tkinter (incluído nas instalações oficiais do Python para Windows e macOS;
  em algumas distribuições Linux, pode ser necessário instalar o pacote Tk)

O projeto não usa dependências externas.

## Como executar

No terminal, a partir desta pasta:

```bash
python forca_gui.py
```

O jogo carrega as palavras de `palavras.txt`, localizado ao lado de
`forca_gui.py`. O arquivo incluído contém mais de 50 palavras em UTF-8, uma por
linha. Para adicionar palavras, basta acrescentar linhas não vazias ao arquivo.

## Como jogar

1. Clique em uma letra do teclado virtual ou pressione uma tecla A-Z.
2. Cada letra incorreta revela uma das seis partes do boneco. Letras repetidas
   são ignoradas e não consomem tentativas.
3. Use **Dica** uma vez por partida para revelar uma letra oculta sem penalidade.
4. Acerte todas as letras antes de seis erros para vencer. Na vitória, o
   bonequinho desce da forca e sobrevive.
5. **Desistir** pede confirmação e, se confirmada, encerra a partida como
   derrota. **Novo Jogo** inicia outra partida.

Ao perder, o boneco aparece com olhos em X e a palavra é revelada. Letras
digitadas sem acento correspondem às letras acentuadas equivalentes.

## Estatísticas

Os totais de vitórias e derrotas são guardados em `estatisticas.json` junto aos
arquivos do jogo, criado automaticamente ao concluir a primeira partida.

## Arquivos

- `forca_gui.py` — funções do jogo, interface e loop de eventos.
- `palavras.txt` — lista de palavras para sorteio.
