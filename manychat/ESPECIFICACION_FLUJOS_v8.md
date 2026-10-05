# Especificación de flujos ManyChat · SOP v8 (Mr. Abundancia)

Fuente: `docs/SOP_Instagram_Mr_Abundancia_v8.docx` (texto en `docs/SOP_v8_texto_extraido.txt`).
Los textos entre comillas son los vigentes de la v8, copiados del documento. Las marcas **VERIFICAR** son capacidades o límites de ManyChat/Instagram que hay que confirmar en la cuenta. Las marcas **PENDIENTE** son datos que el documento no trae.

## 0. Antes de tocar nada
1. Respaldo: `python3 scripts/manychat_api.py backup`. Además, en el editor, **duplicar** cada flujo que se modifica (ESCALAR, EVENTO, SESIÓN, Nuevo seguidor, seguimientos 24 h / 72 h) con el sufijo ` [v7 respaldo]` y dejarlo sin disparador.
2. Reversión: volver a asignar los disparadores a los flujos ` [v7 respaldo]` y desactivar los ` v8`.
3. No se borran contactos, historial ni etiquetas v7 (`FACT_<1500`, `FACT_1500_10000`, `FACT_>10000`, `FOLLOWUP_AUDIO_24H`, `FOLLOWUP_72H`).
4. Configurar la zona horaria de la cuenta: hora de Puerto Rico (America/Puerto_Rico). **VERIFICAR** el valor actual.
5. Etiquetas y campos: `python3 scripts/manychat_api.py setup` y luego con `--apply`.

## 1. Subflujos compartidos (crearlos primero)

### F-DIAG · Diagnóstico de 3 preguntas (sección 3)
- **P1:** "Vamos 🔥 Pregunta 1 de 3: ¿tu negocio ya está facturando?" → [Sí, ya factura] [Estoy empezando] [Aún no tengo]
  - Al entrar: `diag_paso = 0`; etiqueta `M1_TOCO`.
  - Sí → `NEGOCIO_ACTIVO`, `diag_paso = 1` → P2.
  - Estoy empezando → `NEGOCIO_INICIO` → flujo v7 de la sección 8 (sin cambios).
  - Aún no tengo → `SIN_NEGOCIO` → flujo v7 de la sección 9 (sin cambios).
- **P2:** "¿En qué rango está tu facturación mensual? (en USD)" → [Menos de $3K] [$3K a $10K] [$10K a $30K] [Más de $30K]
  - Cada botón pone su etiqueta `FACT_<3K` / `FACT_3K_10K` / `FACT_10K_30K` / `FACT_30K+`, carga `fact_rango` y `diag_paso = 2` → P3.
- **P3:** "Última: ¿qué es lo que más está frenando tu crecimiento hoy?" → [Conseguir clientes] [Cerrar ventas] [Equipo y procesos] [Todo depende de mí] [Finanzas]
  - Etiqueta `FRENO_CLIENTES` / `FRENO_VENTAS` / `FRENO_EQUIPO` / `FRENO_DUENO` / `FRENO_FINANZAS`, carga `freno`, `diag_paso = 3`, etiqueta `DIAG_COMPLETO` → F-ENTREGA.
- **VERIFICAR:** cantidad máxima de botones por mensaje en Instagram. P2, y sobre todo P3, tienen más de 3 opciones: si la tarjeta no admite tantos botones, usar **respuestas rápidas**.
- **Abandono (+30 min):** Smart Delay de 30 min en paralelo, seguido de una condición `diag_paso` < 3 y sin `DIAG_COMPLETO` → poner `ABANDONO_P{diag_paso+1}` → "Te quedaste a una pregunta de tu diagnóstico 👇" y repetir los botones de la pregunta pendiente.

### F-ENTREGA · Diagnóstico + ruteo (secciones 18 y 19)
1. Mensaje según el freno, con el texto exacto de la sección 19 (5 variantes, condición por etiqueta FRENO_*).
2. Smart Delay de 3 segundos.
3. Mensaje según la facturación (sección 18):
   - `FACT_30K+` → texto PRIORIDAD/AGENDA. Asignar conversación a la setter, notificar a la setter y a **Dirección Comercial** (PENDIENTE: contacto). Etiquetas `SETEO_ACTIVO`; `etapa = Seteo activo`. Objetivo: respuesta humana en 5 min.
   - `FACT_10K_30K` → mismo texto PRIORIDAD/AGENDA. Asignar y notificar a la setter. `SETEO_ACTIVO`. Objetivo: 15 min.
   - `FACT_3K_10K` → texto EVALUACIÓN. Asignar y notificar a la setter. Etiquetas `EVALUACION` y `SETEO_ACTIVO`. Objetivo: 15 min.
   - `FACT_<3K` → texto NUTRICIÓN con `{{link_clase}}` (PENDIENTE) y el Canal. Etiqueta `NUTRICION`; `etapa = Nutricion`. **No** se asigna a la setter.
4. Fuera de horario (fuera de lunes a sábado, 9:00 a.m. a 9:00 p.m. de Puerto Rico): variante "…te escribe mañana a primera hora, antes de las 9:30 a.m.". **VERIFICAR** qué condición de fecha y hora ofrece ManyChat; si no hay ninguna, mandar la variante de horario y cubrir la de fuera de horario con una regla.
5. `{{setter}}` = campo `setter`. Si al momento del envío todavía no hay setter asignada, usar el texto "una persona de mi equipo" (decisión técnica registrada).

## 2. ESCALAR (sección 3)
- Disparador: comentario o DM con ESCALAR (sin cambios; reutilizar el disparador existente). Al entrar: `IG_ESCALAR`, `origen = IG_ESCALAR`.
- Respuesta pública: cargar las 3 variantes A/B/C del documento para que roten.
- Randomizer 50/50:
  - **A** (`M1_A`): "Hola {{nombre}} 👋 Soy Mr. Abundancia. Vi tu comentario. Armé un diagnóstico de 3 preguntas que te dice cuál de los 10 sistemas está frenando tu negocio. Toma 30 segundos. ¿Te lo mando?" [Sí, mándamelo] → F-DIAG P1.
  - **B** (`M1_B`): "Hola {{nombre}} 👋 Vi tu comentario. Para decirte exactamente cómo escalar tu negocio necesito saber una cosa primero: ¿tu negocio ya está facturando?" [Sí, ya factura] → `M1_TOCO`, `NEGOCIO_ACTIVO` → F-DIAG P2 · [Estoy empezando] → sección 8.
- Se quita el link del Canal del primer mensaje: pasa a NUTRICIÓN.
- Sin respuesta (sección 10, solo palabras clave):
  - +2 h, si no tiene `M1_TOCO`: "{{nombre}}, ¿te lo mando? Son 3 preguntas y 30 segundos 👇" [Sí, mándamelo]
  - +20 h desde el primer mensaje, si todavía no tiene `M1_TOCO`: "Te escribo por última vez por aquí 🙏 La mayoría de los empresarios que hacen el diagnóstico descubren que su freno no es el que creían. ¿Lo hacemos?" [Sí, dale]
  - Después: asignar a la setter para el seguimiento **humano** del día 2 (intro + audio v7, etiqueta `FOLLOWUP_AUDIO_D2`) y del día 4 ("¿Pudiste escucharme? 👀…", etiqueta `FOLLOWUP_D4`). Sin respuesta al día 4: `NUTRICION`. Estos envíos los hace una persona desde la bandeja de entrada y no se automatizan.

## 3. DIAGNÓSTICO en historias (sección 6, palanca complementaria)
- Disparador: respuesta a una historia o DM con la palabra DIAGNÓSTICO (también "DIAGNOSTICO", sin tilde). Al entrar: `IG_HISTORIA`, `origen = IG_HISTORIA` → F-DIAG P1.

## 4. EVENTO (sección 4)
- Disparador sin cambios. Al entrar: `IG_EVENTO`, `origen = IG_EVENTO`.
- **0A:** "🔥 Te paso toda la info del próximo encuentro. Una pregunta antes, porque el pase VIP es solo para dueños: ¿Eres dueño o socio de un negocio activo?" [Sí, soy dueño/socio] [Todavía no]
  - Todavía no → `EVENTO_NO_DUENO` → información de entrada general, sin la oferta VIP 2x1. **PENDIENTE:** el SOP no incluye ese texto; usar el existente en la cuenta si lo hay.
- **0B:** "Perfecto. ¿En qué rango factura tu negocio al mes? Así te ubicamos en la mesa correcta de networking." [4 rangos] → etiquetas FACT_* y `fact_rango` → Mensaje 1 v7 → Mensaje 2 v7 (sin cambios).
- Para los closers: exportar o filtrar contactos con `IG_EVENTO` + `EVENTO_DUENO` + FACT_* antes de cada evento.

## 5. SESIÓN (sección 5)
- Mensaje inicial sin cambios. En "Sí, ya está activo" se reemplazan los botones por los 4 rangos v8 (el texto no cambia).
- La "Siguiente pregunta" no cambia. **VERIFICAR** el límite de caracteres por botón; si corta el texto, usar las versiones cortas de la P3.
- Se elimina el cierre "¿Te funciona mejor mañana en la mañana o en la tarde?". En su lugar:
  - +$10K: "Perfecto. Por lo que me cuentas, tiene sentido revisar tu caso con el equipo. Te escribo en unos minutos para coordinar el horario. 🙌"
  - $3K a $10K: "Gracias. Voy a revisar tu caso y te escribo hoy mismo."
  - <$3K: mensaje NUTRICIÓN.
  - Para $3K o más: asignar a la setter y notificarla (+$30K también a Dirección Comercial).

## 6. Nuevo seguidor (sección 6)
- Disparador sin cambios. Al entrar: `IG_NUEVO_SEGUIDOR`, `origen = IG_NUEVO_SEGUIDOR`.
- Smart Delay de **7 minutos** (decisión técnica: valor fijo dentro del rango de 5 a 10 minutos).
- Randomizer 50/50:
  - **A** `SEG_A`: "{{nombre}}, gracias por seguirme 🙌 Te tengo un regalo de bienvenida: un diagnóstico de 30 segundos que te dice cuál de los 10 sistemas está frenando tu negocio. ¿Te lo mando?" [Sí, mándamelo] → `SEG_TOCO` → F-DIAG P1.
  - **B** `SEG_B`: audio (**PENDIENTE: grabación**) + "¿Ya tienes un negocio facturando? 👇" [Sí, ya factura] → `SEG_TOCO`, `NEGOCIO_ACTIVO` → P2 · [Todavía no] → `SEG_TOCO` → ruta de las secciones 8 y 9.
  - Mientras el audio no exista, la rama B queda en 0% y A en 100%. El SOP dice "iniciar con esto la primera semana de octubre" para la versión A.
- Sin respuesta:
  - +3 h, si no tiene `SEG_TOCO`: "{{nombre}}, ¿te lo mando? Son 30 segundos y te dice dónde está el freno de tu negocio 👇" [Sí, mándamelo]
  - +20 h: "Último mensaje por aquí 🙏 Si tienes un negocio, en 30 segundos te digo qué lo está frenando. ¿Lo hacemos?" [Sí, dale]
  - Después: `SEG_FRIO`. Sin seguimiento manual.
- La setter solo entra si el seguidor completa el diagnóstico con $3K o más (F-ENTREGA).

## 7. Desactivar
- Los envíos automáticos de 24 h y 72 h de la v7 (sección 10). Antes, contar en el historial cuántos se enviaron realmente.

## 8. Tareas humanas (no se automatizan)
- Seteo según la sección 12 (2 preguntas nuevas, 6 criterios de CALIFICADO, cierre con dos horarios, WhatsApp).
- Primer mensaje de la setter, nota de voz a las 2 h y último mensaje al día siguiente (sección 6).
- Confirmación de la sesión por WhatsApp y llamada (sección 20). **PENDIENTE:** integración de WhatsApp y video.

## 9. Pruebas (3 cuentas internas, sección 21)
| # | Caso | Esperado |
|---|------|----------|
| 1 | Comentar ESCALAR → A → Sí → Más de $30K → Finanzas | Respuesta pública, M1_A, M1_TOCO, FACT_30K+, FRENO_FINANZAS, DIAG_COMPLETO, texto Finanzas + PRIORIDAD, asignación y aviso a Dirección Comercial |
| 2 | ESCALAR → B → $3K a $10K → Ventas | M1_B, EVALUACION, asignación a la setter |
| 3 | ESCALAR → Menos de $3K | NUTRICION, clase + Canal, sin asignación |
| 4 | ESCALAR → abandonar en P2 | A los 30 min, ABANDONO_P2 y repetición de P2 |
| 5 | ESCALAR sin tocar | Recordatorios de +2 h y +20 h; ninguno si ya tocó |
| 6 | EVENTO → Todavía no | Sin oferta VIP |
| 7 | SESIÓN → activo → $10K a $30K | Sin propuesta de horarios; asignación |
| 8 | Seguir la cuenta | Mensaje a los 7 min, SEG_A o SEG_B |
| 9 | DIAGNÓSTICO en historia | IG_HISTORIA → P1 |
