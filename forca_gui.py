"""Jogo da Forca com interface grafica em Tkinter."""

from __future__ import annotations

import json
import random
import unicodedata
import tkinter as tk
from pathlib import Path
from tkinter import messagebox
from typing import Iterable


AZUL_ESCURO = "#173b75"
AZUL = "#2563eb"
AZUL_CLARO = "#dbeafe"
FUNDO = "#edf5ff"
TEXTO = "#243b5a"
CINZA = "#94a3b8"
VERDE = "#15803d"
VERMELHO = "#dc2626"
MAX_ERROS = 6
ARQUIVO_PALAVRAS = Path(__file__).with_name("palavras.txt")
ARQUIVO_ESTATISTICAS = Path(__file__).with_name("estatisticas.json")


def normalizar_letra(letra: str) -> str:
    """Converte uma letra acentuada para sua forma ASCII maiuscula."""
    decomposicao = unicodedata.normalize("NFD", letra.upper())
    return "".join(char for char in decomposicao if not unicodedata.combining(char))


def carregar_palavras(arquivo: str | Path) -> list[str]:
    """Carrega palavras nao vazias de um arquivo de texto UTF-8."""
    caminho = Path(arquivo)
    with caminho.open("r", encoding="utf-8-sig") as entrada:
        palavras = [linha.strip() for linha in entrada if linha.strip()]
    if not palavras:
        raise ValueError(f"Nenhuma palavra encontrada em {caminho}.")
    return palavras


def escolher_palavra(lista: list[str]) -> str:
    """Escolhe uma palavra aleatoria da lista."""
    if not lista:
        raise ValueError("A lista de palavras nao pode estar vazia.")
    return random.choice(lista)


def atualizar_display(palavra: str, letras_tentadas: Iterable[str]) -> str:
    """Monta o display, mantendo ocultas as letras ainda nao tentadas."""
    tentadas = {normalizar_letra(letra) for letra in letras_tentadas}
    caracteres = []
    for caractere in palavra:
        if not caractere.isalpha() or normalizar_letra(caractere) in tentadas:
            caracteres.append(caractere.upper() if caractere.isalpha() else caractere)
        else:
            caracteres.append("_")
    return " ".join(caracteres)


def verificar_vitoria(palavra: str, letras_tentadas: Iterable[str]) -> bool:
    """Retorna se todas as letras da palavra ja foram descobertas."""
    tentadas = {normalizar_letra(letra) for letra in letras_tentadas}
    letras_da_palavra = {
        normalizar_letra(caractere) for caractere in palavra if caractere.isalpha()
    }
    return bool(letras_da_palavra) and letras_da_palavra.issubset(tentadas)


def desenhar_boneco(
    canvas: tk.Canvas,
    erros: int,
    *,
    completo: bool = False,
    derrotado: bool = False,
) -> None:
    """Desenha a forca e ate seis partes do boneco no canvas."""
    canvas.delete("all")
    canvas.create_line(55, 286, 255, 286, fill=AZUL_ESCURO, width=8, capstyle=tk.ROUND)
    canvas.create_line(95, 282, 95, 40, fill=AZUL_ESCURO, width=8, capstyle=tk.ROUND)
    canvas.create_line(91, 42, 205, 42, fill=AZUL_ESCURO, width=8, capstyle=tk.ROUND)
    canvas.create_line(201, 40, 201, 76, fill=AZUL_ESCURO, width=5, tags="rope")
    canvas.create_line(95, 88, 140, 42, fill=AZUL_ESCURO, width=6, capstyle=tk.ROUND)
    canvas.create_text(
        155, 316, text="Cada erro revela uma parte", fill="#64748b", font=("Segoe UI", 10)
    )

    partes_visiveis = MAX_ERROS if completo else min(max(erros, 0), MAX_ERROS)
    if partes_visiveis == 0:
        return

    canvas.create_oval(181, 78, 221, 118, outline=AZUL_ESCURO, width=4, tags="person")
    if partes_visiveis >= 2:
        canvas.create_line(201, 118, 201, 183, fill=AZUL_ESCURO, width=4, tags="person")
    if partes_visiveis >= 3:
        canvas.create_line(201, 132, 173, 158, fill=AZUL_ESCURO, width=4, tags="person")
    if partes_visiveis >= 4:
        canvas.create_line(201, 132, 229, 158, fill=AZUL_ESCURO, width=4, tags="person")
    if partes_visiveis >= 5:
        canvas.create_line(201, 182, 177, 220, fill=AZUL_ESCURO, width=4, tags="person")
    if partes_visiveis >= 6:
        canvas.create_line(201, 182, 225, 220, fill=AZUL_ESCURO, width=4, tags="person")

    if derrotado:
        cor_olhos = VERMELHO
        canvas.create_line(188, 88, 194, 94, fill=cor_olhos, width=3, tags="person")
        canvas.create_line(194, 88, 188, 94, fill=cor_olhos, width=3, tags="person")
        canvas.create_line(208, 88, 214, 94, fill=cor_olhos, width=3, tags="person")
        canvas.create_line(214, 88, 208, 94, fill=cor_olhos, width=3, tags="person")
        canvas.create_arc(
            191, 97, 211, 112, start=20, extent=140, style=tk.ARC,
            outline=cor_olhos, width=2, tags="person"
        )
    else:
        canvas.create_oval(190, 89, 193, 92, fill=AZUL_ESCURO, outline="", tags="person")
        canvas.create_oval(209, 89, 212, 92, fill=AZUL_ESCURO, outline="", tags="person")
        canvas.create_arc(
            191, 94, 211, 110, start=200, extent=140, style=tk.ARC,
            outline=AZUL_ESCURO, width=2, tags="person"
        )


class BotaoArredondado(tk.Canvas):
    """Botao desenhado em canvas para manter cantos arredondados."""

    def __init__(
        self,
        master: tk.Misc,
        texto: str,
        comando,
        *,
        largura: int,
        altura: int,
        cor: str = AZUL,
        cor_texto: str = "white",
        fonte: tuple[str, int, str] = ("Segoe UI", 10, "bold"),
    ) -> None:
        super().__init__(
            master,
            width=largura,
            height=altura,
            background=master.cget("background"),
            highlightthickness=0,
            borderwidth=0,
            cursor="hand2",
        )
        self.comando = comando
        self.texto = texto
        self.cor = cor
        self.cor_texto = cor_texto
        self.fonte = fonte
        self.habilitado = True
        self._desenhar()
        self.bind("<Button-1>", self._clicar)
        self.bind("<Enter>", self._entrar)
        self.bind("<Leave>", self._sair)

    def _retangulo_arredondado(self, cor: str) -> None:
        raio = min(12, self.winfo_reqheight() // 2)
        largura = int(self.cget("width"))
        altura = int(self.cget("height"))
        self.delete("all")
        self.create_rectangle(raio, 0, largura - raio, altura, fill=cor, outline="")
        self.create_rectangle(0, raio, largura, altura - raio, fill=cor, outline="")
        for x, y in (
            (0, 0),
            (largura - 2 * raio, 0),
            (0, altura - 2 * raio),
            (largura - 2 * raio, altura - 2 * raio),
        ):
            self.create_oval(x, y, x + 2 * raio, y + 2 * raio, fill=cor, outline="")
        self.create_text(
            largura / 2,
            altura / 2,
            text=self.texto,
            fill=self.cor_texto if self.habilitado else "#e2e8f0",
            font=self.fonte,
        )

    def _desenhar(self, hover: bool = False) -> None:
        cor = self.cor if self.habilitado else CINZA
        if hover and self.habilitado:
            cor = AZUL_ESCURO
        self._retangulo_arredondado(cor)

    def _clicar(self, _evento: tk.Event) -> None:
        if self.habilitado:
            self.comando()

    def _entrar(self, _evento: tk.Event) -> None:
        self._desenhar(hover=True)

    def _sair(self, _evento: tk.Event) -> None:
        self._desenhar()

    def configurar(self, *, texto: str | None = None, habilitado: bool | None = None) -> None:
        if texto is not None:
            self.texto = texto
        if habilitado is not None:
            self.habilitado = habilitado
        self._desenhar()


def carregar_estatisticas(arquivo: str | Path) -> tuple[int, int]:
    """Carrega vitorias e derrotas, ou usa zeros se ainda nao ha arquivo."""
    caminho = Path(arquivo)
    try:
        with caminho.open("r", encoding="utf-8") as entrada:
            dados = json.load(entrada)
    except FileNotFoundError:
        return 0, 0
    return max(0, int(dados.get("vitorias", 0))), max(0, int(dados.get("derrotas", 0)))


def salvar_estatisticas(
    vitorias: int, derrotas: int, arquivo: str | Path = ARQUIVO_ESTATISTICAS
) -> None:
    """Salva os totais de vitorias e derrotas em JSON."""
    caminho = Path(arquivo)
    dados = {"vitorias": vitorias, "derrotas": derrotas}
    with caminho.open("w", encoding="utf-8") as saida:
        json.dump(dados, saida, ensure_ascii=False, indent=2)
        saida.write("\n")


class JogoDaForca:
    """Controla a interface e o estado de uma partida."""

    def __init__(self, raiz: tk.Tk, palavras: list[str]) -> None:
        self.raiz = raiz
        self.palavras = palavras
        self.palavra = ""
        self.letras_tentadas: set[str] = set()
        self.erros = 0
        self.dica_usada = False
        self.finalizado = False
        self.animacao: str | None = None
        self.vitorias, self.derrotas = carregar_estatisticas(ARQUIVO_ESTATISTICAS)

        self.raiz.title("Jogo da Forca")
        self.raiz.configure(background=FUNDO)
        self.raiz.minsize(820, 690)
        self.raiz.geometry("980x760")
        self.raiz.bind("<KeyPress>", self._tecla_pressionada)
        self._criar_interface()
        self.novo_jogo()

    def _criar_interface(self) -> None:
        principal = tk.Frame(self.raiz, background=FUNDO, padx=24, pady=20)
        principal.pack(fill="both", expand=True)

        tk.Label(
            principal,
            text="JOGO DA FORCA",
            font=("Segoe UI", 25, "bold"),
            foreground=AZUL_ESCURO,
            background=FUNDO,
        ).pack(anchor="w")
        tk.Label(
            principal,
            text="Descubra a palavra antes que as seis tentativas acabem.",
            font=("Segoe UI", 11),
            foreground="#52677f",
            background=FUNDO,
        ).pack(anchor="w", pady=(1, 16))

        conteudo = tk.Frame(principal, background=FUNDO)
        conteudo.pack(fill="both", expand=True)
        conteudo.columnconfigure(0, weight=3, uniform="colunas")
        conteudo.columnconfigure(1, weight=2, uniform="colunas")
        conteudo.rowconfigure(0, weight=1)

        esquerda = tk.Frame(conteudo, background=FUNDO)
        esquerda.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        direita = tk.Frame(conteudo, background=FUNDO)
        direita.grid(row=0, column=1, sticky="nsew")

        cartao_palavra = tk.Frame(
            esquerda, background="white", padx=18, pady=16,
            highlightbackground="#d6e5f7", highlightthickness=1,
        )
        cartao_palavra.pack(fill="x")
        tk.Label(
            cartao_palavra,
            text="PALAVRA",
            font=("Segoe UI", 9, "bold"),
            foreground="#64748b",
            background="white",
        ).pack(anchor="w")
        self.display_palavra = tk.StringVar()
        tk.Label(
            cartao_palavra,
            textvariable=self.display_palavra,
            font=("Consolas", 24, "bold"),
            foreground=AZUL_ESCURO,
            background="white",
            pady=8,
            wraplength=500,
            justify="center",
        ).pack(fill="x")

        linha_status = tk.Frame(esquerda, background=FUNDO)
        linha_status.pack(fill="x", pady=(12, 8))
        self.status = tk.StringVar()
        tk.Label(
            linha_status,
            textvariable=self.status,
            font=("Segoe UI", 11, "bold"),
            foreground=AZUL_ESCURO,
            background=FUNDO,
        ).pack(side="left")
        self.tentativas = tk.StringVar()
        tk.Label(
            linha_status,
            textvariable=self.tentativas,
            font=("Segoe UI", 11, "bold"),
            foreground=AZUL,
            background=FUNDO,
        ).pack(side="right")

        tk.Label(
            esquerda,
            text="TECLADO",
            font=("Segoe UI", 9, "bold"),
            foreground="#64748b",
            background=FUNDO,
        ).pack(anchor="w", pady=(8, 6))
        teclado = tk.Frame(esquerda, background=FUNDO)
        teclado.pack(anchor="center")
        self.botoes_letras: dict[str, BotaoArredondado] = {}
        for indice, letra in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
            botao = BotaoArredondado(
                teclado,
                letra,
                lambda l=letra: self._tentar_letra(l),
                largura=40,
                altura=38,
                cor=AZUL_CLARO,
                cor_texto=AZUL_ESCURO,
                fonte=("Segoe UI", 10, "bold"),
            )
            botao.grid(row=indice // 7, column=indice % 7, padx=3, pady=4)
            self.botoes_letras[letra] = botao

        painel_boneco = tk.Frame(
            direita, background="white", padx=10, pady=10,
            highlightbackground="#d6e5f7", highlightthickness=1,
        )
        painel_boneco.pack(fill="both", expand=True)
        self.canvas_boneco = tk.Canvas(
            painel_boneco, width=310, height=330, background="white",
            highlightthickness=0,
        )
        self.canvas_boneco.pack(fill="both", expand=True)

        acoes = tk.Frame(direita, background=FUNDO)
        acoes.pack(fill="x", pady=(12, 0))
        self.botao_novo = BotaoArredondado(
            acoes, "Novo Jogo", self.novo_jogo, largura=118, altura=42
        )
        self.botao_novo.grid(row=0, column=0, padx=(0, 7), pady=4, sticky="ew")
        self.botao_dica = BotaoArredondado(
            acoes, "Dica", self.dar_dica, largura=82, altura=42,
            cor=AZUL_CLARO, cor_texto=AZUL_ESCURO,
        )
        self.botao_dica.grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        self.botao_desistir = BotaoArredondado(
            acoes, "Desistir", self.desistir, largura=94, altura=42,
            cor="#dbeafe", cor_texto=AZUL_ESCURO,
        )
        self.botao_desistir.grid(row=0, column=2, padx=(7, 0), pady=4, sticky="ew")
        for coluna in range(3):
            acoes.columnconfigure(coluna, weight=1)

        self.estatisticas = tk.StringVar()
        tk.Label(
            principal,
            textvariable=self.estatisticas,
            font=("Segoe UI", 10, "bold"),
            foreground="#52677f",
            background=FUNDO,
            pady=10,
        ).pack(anchor="w")

    def _atualizar_interface(self) -> None:
        self.display_palavra.set(atualizar_display(self.palavra, self.letras_tentadas))
        self.tentativas.set(f"Tentativas restantes: {MAX_ERROS - self.erros}")
        self.estatisticas.set(
            f"Vitorias: {self.vitorias}    |    Derrotas: {self.derrotas}"
        )
        for letra, botao in self.botoes_letras.items():
            botao.configurar(habilitado=not self.finalizado and letra not in self.letras_tentadas)
        self.botao_dica.configurar(
            habilitado=not self.finalizado and not self.dica_usada
        )
        self.botao_desistir.configurar(habilitado=not self.finalizado)

    def _tecla_pressionada(self, evento: tk.Event) -> None:
        letra = normalizar_letra(evento.char)
        if len(letra) == 1 and letra in self.botoes_letras:
            self._tentar_letra(letra)

    def _tentar_letra(self, letra: str) -> None:
        if self.finalizado:
            return
        letra = normalizar_letra(letra)
        if len(letra) != 1 or letra not in self.botoes_letras or letra in self.letras_tentadas:
            return
        self.letras_tentadas.add(letra)
        letras_da_palavra = {normalizar_letra(char) for char in self.palavra if char.isalpha()}
        if letra not in letras_da_palavra:
            self.erros += 1
        self._atualizar_interface()

        if verificar_vitoria(self.palavra, self.letras_tentadas):
            self._encerrar(vitoria=True)
        elif self.erros >= MAX_ERROS:
            self._encerrar(vitoria=False)
        else:
            desenhar_boneco(self.canvas_boneco, self.erros)

    def dar_dica(self) -> None:
        if self.finalizado or self.dica_usada:
            return
        reveladas = {
            normalizar_letra(char)
            for char in self.palavra
            if char.isalpha() and normalizar_letra(char) in self.letras_tentadas
        }
        restantes = sorted(
            {
                normalizar_letra(char)
                for char in self.palavra
                if char.isalpha() and normalizar_letra(char) not in reveladas
            }
        )
        self.dica_usada = True
        if not restantes:
            self.status.set("Todas as letras ja foram reveladas.")
            self._atualizar_interface()
            return
        self.letras_tentadas.add(random.choice(restantes))
        self.status.set("Dica: uma letra foi revelada, sem penalidade.")
        self._atualizar_interface()
        if verificar_vitoria(self.palavra, self.letras_tentadas):
            self._encerrar(vitoria=True)
        else:
            desenhar_boneco(self.canvas_boneco, self.erros)

    def desistir(self) -> None:
        if self.finalizado:
            return
        if messagebox.askyesno("Desistir", "Deseja encerrar a partida? Isso contara como derrota."):
            self._encerrar(vitoria=False, desistiu=True)

    def _encerrar(self, *, vitoria: bool, desistiu: bool = False) -> None:
        self.finalizado = True
        if vitoria:
            self.vitorias += 1
            self.status.set("Voce venceu! O bonequinho escapou!")
            desenhar_boneco(self.canvas_boneco, self.erros, completo=True)
            self.canvas_boneco.delete("rope")
            self._animar_fuga(0)
        else:
            self.derrotas += 1
            self.status.set(
                f"Voce desistiu. A palavra era {self.palavra.upper()}."
                if desistiu
                else f"Fim de jogo! A palavra era {self.palavra.upper()}."
            )
            desenhar_boneco(
                self.canvas_boneco, MAX_ERROS, completo=True, derrotado=True
            )

        try:
            salvar_estatisticas(self.vitorias, self.derrotas, ARQUIVO_ESTATISTICAS)
        except OSError as erro:
            messagebox.showerror(
                "Erro ao salvar estatisticas",
                f"A partida foi registrada nesta sessao, mas nao foi possivel salvar "
                f"o arquivo de estatisticas:\n{erro}",
            )
        self._atualizar_interface()

    def _animar_fuga(self, passo: int) -> None:
        if passo >= 16:
            self.animacao = None
            return
        self.canvas_boneco.move("person", 0, 7)
        self.animacao = self.raiz.after(35, lambda: self._animar_fuga(passo + 1))

    def novo_jogo(self) -> None:
        if self.animacao is not None:
            self.raiz.after_cancel(self.animacao)
            self.animacao = None
        self.palavra = escolher_palavra(self.palavras)
        self.letras_tentadas.clear()
        self.erros = 0
        self.dica_usada = False
        self.finalizado = False
        self.status.set("Escolha uma letra para comecar.")
        desenhar_boneco(self.canvas_boneco, self.erros)
        self._atualizar_interface()


def main() -> None:
    raiz = tk.Tk()
    try:
        palavras = carregar_palavras(ARQUIVO_PALAVRAS)
    except (OSError, ValueError) as erro:
        messagebox.showerror("Erro ao carregar palavras", str(erro), parent=raiz)
        raiz.destroy()
        raise
    JogoDaForca(raiz, palavras)
    raiz.mainloop()


if __name__ == "__main__":
    main()
