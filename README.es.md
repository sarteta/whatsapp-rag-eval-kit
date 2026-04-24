# whatsapp-rag-eval-kit

[![tests](https://github.com/sarteta/whatsapp-rag-eval-kit/actions/workflows/tests.yml/badge.svg)](https://github.com/sarteta/whatsapp-rag-eval-kit/actions/workflows/tests.yml)

Harness de evaluación en YAML para bots de WhatsApp con RAG. Detecta los
modos de falla que importan en producción: intent incorrecto, información
faltante, frases alucinadas, respuestas lentas, costo de tokens disparado.

Lo armé porque cada clínica / estudio jurídico / inmobiliaria para la que
shippeé un bot terminaba preguntando lo mismo después de la semana de
luna de miel — _"¿cómo sé que esto sigue funcionando?"_ — y ninguna
herramienta de eval existente habla el caso WhatsApp (turnos cortos,
tags de intent, español/portugués, costo por conversación).

## Qué hace

Escribís un YAML con mensajes entrantes + qué esperás que el bot haga.
El kit corre tu bot contra cada caso, verifica cada expectativa, y
genera un reporte en Markdown que podés pegar en Slack / Notion / un
mail al cliente.

```bash
pip install -e .
whatsapp-rag-eval --suite suites/clinic-es.yml --report out/report.md
```

Para la versión completa (todos los checks disponibles, ejemplo de código
para conectar tu bot real, diseño), ver el [README en inglés](./README.md).

## Licencia

MIT © 2026 Santiago Arteta
