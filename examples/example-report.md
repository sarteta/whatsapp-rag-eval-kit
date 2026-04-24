# clinic-es — eval report

_Golden cases for a small LATAM clinic's WhatsApp bot. Spanish (rioplatense)._

**Cases:** 8  
**Passed:** 7  
**Failed:** 1  
**Pass rate:** 87.5%  
**p95 latency:** 2100 ms  
**Total cost:** $0.0116

## Cases

| ID | Inbound | Status | Checks that failed |
|----|---------|--------|--------------------|
| `schedule-001` | Hola, quería saber que horarios de atención tienen | ✅ pass | — |
| `schedule-002` | A qué hora abren hoy? | ✅ pass | — |
| `booking-001` | Quería agendar un turno para la próxima semana | ✅ pass | — |
| `booking-002` | Cómo reservo una cita? | ✅ pass | — |
| `price-001` | Cuánto cuesta la consulta? | ✅ pass | — |
| `cancel-001` | Necesito cancelar el turno que tenía para mañana | ❌ fail | intent, answer_contains |
| `offtopic-001` | Me recomendás un buen libro? | ✅ pass | — |
| `edge-empty-ish` | hola | ✅ pass | — |

## Failure details

### `cancel-001`
**Inbound:** Necesito cancelar el turno que tenía para mañana

**Got:** Podes reservar tu turno desde nuestro sitio web o respondiendo este mensaje con tu DNI y la fecha que preferis.

- ❌ **intent** — expected=cancel_intent got=booking_intent
- ❌ **answer_contains** — missing: ['CANCELAR']

