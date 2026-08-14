---
book_title: "Integrações Resilientes: webhooks, filas e retentativas na prática"
edition: "2ª edição"
chapter: "Capítulo 4 - Webhooks em produção"
section: "Decisões de entrega e recuperação"
page_start: 118
page_end: 126
---

# 4.1 O que uma entrega precisa garantir

Um webhook conecta dois sistemas que não compartilham o mesmo relógio, a mesma rede ou a mesma visão sobre o estado de um evento.

O provedor precisa entregar uma notificação, enquanto o consumidor precisa decidir quando recebeu informação suficiente para executar uma mudança.

Uma integração resiliente trata a entrega como um processo observável, com estado, tentativas e identificadores que permitam investigar o que aconteceu.

O objetivo não é eliminar toda falha, mas tornar cada falha compreensível e permitir que o sistema se recupere sem repetir efeitos irreversíveis.

# 4.2 Timeouts e confirmação

Quando um provedor envia um webhook, ele espera uma resposta rápida do consumidor para confirmar que a mensagem foi recebida.

Se a conexão expira antes da confirmação, o provedor não sabe se o evento falhou antes de chegar, foi processado parcialmente ou teve apenas a resposta perdida.

Um timeout deve ser tratado como uma falha temporária de comunicação, porque a ausência de resposta não prova que nenhuma operação aconteceu.

O consumidor precisa registrar o identificador do evento e o resultado observado para que uma nova entrega possa ser comparada com a tentativa anterior.

Uma resposta rápida pode confirmar apenas o recebimento e deixar o processamento mais demorado para uma fila interna, desde que essa decisão apareça nos logs.

# 4.3 Retentativas e backoff

Depois de uma falha temporária, o provedor pode agendar uma nova tentativa usando o mesmo identificador de evento.

Retentar imediatamente aumenta a pressão sobre um consumidor que talvez ainda esteja sem capacidade para responder.

O backoff exponencial aumenta progressivamente o intervalo entre tentativas e reduz a concentração de tráfego durante uma instabilidade.

Um limite de tentativas evita que uma mensagem permaneça indefinidamente em um ciclo de entrega sem encaminhamento para uma fila de falhas.

O intervalo entre tentativas deve incluir alguma variação para evitar que muitos eventos voltem ao mesmo tempo depois de uma interrupção comum.

# 4.4 Idempotência e duplicidade

Uma nova entrega pode chegar depois de o consumidor ter executado a operação, mesmo quando a resposta de confirmação não voltou ao provedor.

Por isso, o consumidor deve persistir o `event_id` antes de executar efeitos que não podem ser repetidos com segurança.

Quando o mesmo identificador aparece novamente, a aplicação consulta o registro anterior e devolve uma resposta compatível sem cobrar ou enviar a mesma notificação duas vezes.

Idempotência não significa ignorar toda mensagem repetida: o sistema precisa distinguir uma repetição do mesmo evento de um novo evento com dados atualizados.

Uma chave de deduplicação precisa ter escopo e tempo de retenção definidos, porque um identificador reutilizado não deve bloquear uma entrega legítima no futuro.

O payload deve carregar dados estáveis, como `event_id`, tipo e instante de ocorrência, para que o consumidor consiga tomar essa decisão sem depender apenas da ordem de chegada.

# 4.5 Rate limit e capacidade

Um consumidor pode responder com 429 quando recebeu mais eventos do que consegue processar dentro da capacidade atual.

Esse retorno não indica que o evento é inválido. Ele informa que a próxima tentativa precisa respeitar uma política de espera maior.

O provedor deve observar a capacidade anunciada pelo consumidor e reduzir o ritmo sem abandonar silenciosamente os eventos pendentes.

Uma fila desacopla a chegada do webhook do processamento final, mas também cria a responsabilidade de acompanhar atraso, tamanho e idade das mensagens.

Quando a fila cresce continuamente, aumentar retentativas sem aumentar capacidade apenas transforma a sobrecarga em um atraso maior.

O backpressure funciona quando o sinal de capacidade percorre o caminho completo, da fila ou consumidor até o agendador de novas entregas.

# 4.6 Observabilidade da entrega

Cada tentativa deve registrar `event_id`, tentativa, resultado, latência e motivo da próxima ação.

Logs estruturados permitem separar timeout, recusa por limite de ritmo, erro temporário e falha definitiva sem depender de frases livres.

Métricas de taxa de sucesso, idade da fila e quantidade de tentativas mostram se a recuperação está funcionando ou apenas acumulando trabalho.

Um alerta útil combina o sintoma com o contexto, como aumento de timeouts em um consumidor específico durante uma janela de deploy.

O histórico de uma entrega precisa levar o operador da primeira tentativa até o estado atual sem perder o capítulo, a seção e o identificador do evento.

# 4.7 Decisões combinadas

Timeout, retentativa e idempotência formam uma cadeia: a falta de confirmação dispara a tentativa, e a deduplicação protege o efeito repetido.

Rate limit e backpressure tratam a capacidade do consumidor, enquanto a fila preserva eventos que não podem ser processados imediatamente.

Observabilidade conecta essas decisões ao diagnóstico, porque um número de tentativa sem o motivo da espera não explica o comportamento do sistema.

Uma política de entrega confiável combina tempo de espera, limite de tentativas, chave de deduplicação, capacidade e sinais operacionais.

O desenho final deve deixar claro qual unidade pode ser repetida, qual efeito precisa ser protegido e qual evidência permite reconstruir a história de cada evento.
