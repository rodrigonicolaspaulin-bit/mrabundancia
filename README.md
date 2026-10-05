# Mr. Abundancia · Implementación del SOP v8 de Instagram en ManyChat

- `docs/`: SOP v8 (.docx) y su texto extraído.
- `manychat/ESPECIFICACION_FLUJOS_v8.md`: qué crear o cambiar en cada flujo, con los textos vigentes de la v8, el respaldo y la reversión, las dependencias pendientes y el plan de pruebas.
- `manychat/config_v8.json`: etiquetas, campos personalizados y campos del bot de la v8.
- `scripts/manychat_api.py`: respaldo de solo lectura (`backup`) y alta de etiquetas y campos (`setup`, simulación por defecto; `--apply` solo crea lo que falta, nunca borra).

Estado: los flujos todavía no se cargaron en ManyChat. Esta sesión corre en la nube, sin acceso al navegador del usuario y con la API de ManyChat bloqueada por la política de red.
