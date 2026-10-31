# Traductor Quechua

Traductor español ⇄ quechua construido sobre [OpenRouter](https://openrouter.ai).
Nació del cuaderno de investigación `investigacion/Untitled1.ipynb` y ahora
funciona como página web, sin frameworks ni build.

## Cómo usarlo

1. Consigue una API key en <https://openrouter.ai/keys>.
2. Abre `index.html` en el navegador (doble clic). No hace falta instalar nada.
   Si tu navegador bloquea la página por abrirse como archivo local, puedes
   servirla con la extensión **Live Server** de VS Code o con
   `python -m http.server 8000` (si tienes Python) y entrar a
   <http://localhost:8000>.
3. Pega la key (se guarda solo en tu navegador), escribe una frase y pulsa
   **Traducir** (o `Ctrl + Enter`).

## Archivos

- `index.html` — estructura y controles.
- `style.css` — diseño mínimo, con modo claro/oscuro automático.
- `app.js` — llamada a OpenRouter, prompts y manejo de errores.
- `investigacion/Untitled1.ipynb` — cuaderno original de investigación.

## Cómo hace la llamada

`app.js` envía un `POST` a `https://openrouter.ai/api/v1/chat/completions` con:

- el modelo elegido (por defecto `nvidia/nemotron-3-ultra-550b-a55b:free`);
- un mensaje `system` con el prompt de traducción y un mensaje `user` con el
  texto a traducir;
- opcionalmente el plugin `web` de OpenRouter (búsqueda), desde **Ajustes**.

Es el equivalente web de `preguntar()` y `preguntar_con_la_web()` del notebook.
La diferencia es que aquí no se mantiene el historial de la conversación: cada
traducción es una llamada independiente.

## Seguridad

La key se guarda en el `localStorage` del navegador y viaja directamente a
OpenRouter. Es aceptable para uso personal o local, pero **no publiques esta
página tal cual en Internet**: cualquiera podría usar tu key.

Para un despliegue público, mueve la llamada a un backend pequeño que guarde la
key en una variable de entorno y exponga tu propio endpoint.

## Problemas comunes

- **429 — demasiadas solicitudes**: los modelos `:free` tienen un cupo diario.
  Espera un poco o cambia de modelo en **Ajustes**.
- **401 — API key inválida**: revísala en <https://openrouter.ai/keys>.
- **402 — sin créditos**: usa un modelo `:free` o agrega saldo.
- **No conecta**: revisa tu conexión o prueba sirviendo la página con
  `python -m http.server`.
- **El modelo no existe (404)**: verifica el ID en
  <https://openrouter.ai/models>. La lista de modelos gratuitos cambia con el
  tiempo.

## Nota

Las traducciones las genera un modelo de IA y pueden contener errores,
especialmente en una lengua con tanta variación regional como el quechua.
