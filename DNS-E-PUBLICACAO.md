# Publicar `murundu.eng.br` — passo a passo

Duas metades: uma é minha (repositório, Pages), outra é sua (DNS no
Registro.br e o botão do HTTPS). A ordem importa — **o DNS antes do HTTPS**.

⚠️ **Nada disto acontece antes de o conteúdo real entrar na página.** Enquanto
houver marcador `⟨PREENCHER⟩`, `python verificar.py` reprova e o site não sobe.

---

## Etapa 1 — preencher o conteúdo (você)

Abra `PENDENCIAS-DE-CONTEUDO.md`: cada linha aponta um marcador
`⟨PREENCHER: …⟩` dentro do `index.html`. Substitua o marcador inteiro,
incluindo os sinais `⟨` e `⟩`, pelo texto real.

Depois, na pasta do projeto:

```bash
python verificar.py
```

Ele só passa quando não sobrar nenhum marcador. A última linha diz contra o
que ele mediu.

---

## Etapa 2 — repositório e GitHub Pages (eu)

1. Crio `engphcg/murundu-consultoria` **público** (o Pages gratuito exige
   repositório público) e envio os arquivos.
2. Em *Settings → Pages*, ligo a publicação a partir da branch `main`, pasta
   raiz. O arquivo `CNAME`, que já está no repositório com a linha
   `murundu.eng.br`, faz o GitHub reconhecer o domínio.
3. Nesse momento o GitHub começa a checar o DNS — e vai reclamar até a
   Etapa 3 estar feita. É esperado.

---

## Etapa 3 — DNS no Registro.br (você)

Entre em <https://registro.br>, faça login, abra o domínio **murundu.eng.br**
e vá em **DNS → Editar Zona** (dependendo da tela, aparece como *"Alterar
servidores DNS / Usar os servidores do Registro.br"*; use os do Registro.br).

Crie **nove** registros. Copie os valores exatamente como estão.

### 3.1 — Quatro registros `A` no domínio raiz

Deixe o campo do nome/host **vazio** (ou `@`, se a tela exigir algo):

| Tipo | Nome | Valor |
|---|---|---|
| A | *(vazio)* | `185.199.108.153` |
| A | *(vazio)* | `185.199.109.153` |
| A | *(vazio)* | `185.199.110.153` |
| A | *(vazio)* | `185.199.111.153` |

### 3.2 — Quatro registros `AAAA` no domínio raiz (IPv6)

Mesma regra para o nome. Não são opcionais na prática: sem eles, quem estiver
numa rede só-IPv6 não abre o site.

| Tipo | Nome | Valor |
|---|---|---|
| AAAA | *(vazio)* | `2606:50c0:8000::153` |
| AAAA | *(vazio)* | `2606:50c0:8001::153` |
| AAAA | *(vazio)* | `2606:50c0:8002::153` |
| AAAA | *(vazio)* | `2606:50c0:8003::153` |

### 3.3 — Um registro `CNAME` para o `www`

| Tipo | Nome | Valor |
|---|---|---|
| CNAME | `www` | `engphcg.github.io.` |

⛔ **Sem o nome do repositório** — é `engphcg.github.io`, nunca
`engphcg.github.io/murundu-consultoria`. O ponto final no fim é como o
Registro.br marca nome absoluto; se a tela recusar o ponto, tire-o.

Salve a zona. A propagação costuma levar de alguns minutos a algumas horas.

---

## Etapa 4 — conferir a propagação (eu, ou você)

```bash
nslookup murundu.eng.br
nslookup www.murundu.eng.br
```

O primeiro tem de devolver os quatro IPs `185.199.*`; o segundo, o
`engphcg.github.io`. Enquanto devolver outra coisa, ainda não propagou —
espere, não mexa nos registros.

---

## Etapa 5 — ligar o HTTPS (você, e só depois da Etapa 4)

Em *Settings → Pages* do repositório, marque **"Enforce HTTPS"**.

⚠️ **A caixa fica cinza e não clicável enquanto o certificado não é emitido**,
e ele só é emitido depois que o DNS aponta certo. Se estiver cinza, volte à
Etapa 4. Não é erro — é ordem.

---

## O que fica de fora, de propósito

- **Sem formulário de contato.** Não há servidor: o contato é WhatsApp e
  e-mail, que funcionam sem backend. O formulário do Brevo é decisão sua e
  pode entrar depois — a página está preparada para receber a seção.
- **Sem analytics, sem cookie, sem requisição a terceiros.** A página não
  coleta nada, e é isso que o rodapé afirma. Se um dia entrar medição de
  acesso, a frase do rodapé muda no mesmo commit.
- **Sem e-mail `@murundu.eng.br`.** O Pages serve páginas, não e-mail. Se
  quiser um endereço no domínio, é serviço separado (e exige registros MX na
  mesma zona da Etapa 3).
