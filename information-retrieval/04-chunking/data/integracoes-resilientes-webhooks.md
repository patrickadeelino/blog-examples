---
book_title: "Integrações Resilientes: webhooks, filas e retentativas na prática"
edition: "2ª edição"
chapter: "Capítulo 4 - Webhooks em produção"
section: "4.3 Timeouts e retentativas"
page_start: 118
page_end: 119
---

# 4.3 Timeouts e retentativas em webhooks

Quando um provedor envia um webhook, ele espera uma resposta rápida do consumidor.
Se a conexão expira antes de receber confirmação, o provedor não sabe se o evento
falhou antes de chegar, se foi processado parcialmente ou se a resposta se perdeu
no caminho de volta.

Por isso, timeout não deve ser tratado como erro definitivo. Em geral, ele entra
na mesma família de falhas temporárias: o provedor registra a tentativa, agenda
uma nova entrega e preserva o mesmo identificador de evento para permitir
deduplicação no consumidor.

| status | significado | ação recomendada |
| --- | --- | --- |
| 200 | evento recebido e persistido | encerrar entrega |
| 408 | consumidor não respondeu dentro do limite | reagendar com backoff |
| 429 | consumidor pediu redução de ritmo | aplicar espera maior |
| 500 | falha temporária no consumidor | tentar novamente com limite |

Um payload de entrega deve carregar informação suficiente para tornar a
retentativa segura:

```json
{
  "event_id": "evt_8f3a",
  "type": "invoice.paid",
  "attempt": 3,
  "occurred_at": "2026-08-11T14:20:00Z"
}
```

O consumidor deve gravar `event_id` antes de executar efeitos irreversíveis.
Se a mesma entrega aparecer de novo depois de um timeout, a aplicação reconhece
o identificador e evita cobrar, enviar e-mail ou baixar estoque duas vezes.
