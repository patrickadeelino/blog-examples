---
book_title: "Integracoes Resilientes: webhooks, filas e retentativas na pratica"
edition: "2a edicao"
chapter: "Capitulo 4 - Webhooks em producao"
section: "4.3 Timeouts e retentativas"
page_start: 118
page_end: 119
---

# 4.3 Timeouts e retentativas em webhooks

Quando um provedor envia um webhook, ele espera uma resposta rapida do consumidor.
Se a conexao expira antes de receber confirmacao, o provedor nao sabe se o evento
falhou antes de chegar, se foi processado parcialmente ou se a resposta se perdeu
no caminho de volta.

Por isso, timeout nao deve ser tratado como erro definitivo. Em geral, ele entra
na mesma familia de falhas temporarias: o provedor registra a tentativa, agenda
uma nova entrega e preserva o mesmo identificador de evento para permitir
deduplicacao no consumidor.

| status | significado | acao recomendada |
| 200 | evento recebido e persistido | encerrar entrega |
| 408 | consumidor nao respondeu dentro do limite | reagendar com backoff |
| 429 | consumidor pediu reducao de ritmo | aplicar espera maior |
| 500 | falha temporaria no consumidor | tentar novamente com limite |

Um payload de entrega deve carregar informacao suficiente para tornar a
retentativa segura:

```json
{
  "event_id": "evt_8f3a",
  "type": "invoice.paid",
  "attempt": 3,
  "occurred_at": "2026-08-11T14:20:00Z"
}
```

O consumidor deve gravar `event_id` antes de executar efeitos irreversiveis.
Se a mesma entrega aparecer de novo depois de um timeout, a aplicacao reconhece
o identificador e evita cobrar, enviar e-mail ou baixar estoque duas vezes.
