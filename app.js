const API_URL = "https://openrouter.ai/api/v1/chat/completions";
const KEY_STORAGE = "quechua.apiKey";
const MODEL_STORAGE = "quechua.model";
const DEFAULT_MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free";
const TIMEOUT_MS = 60000;

const PROMPTS = {
  "es-qu": {
    sureno:
      "Eres un traductor experto en quechua sureño (Cusco-Collao). Traduce del español al quechua sureño. Responde únicamente con la traducción, sin explicaciones ni comillas. Usa la forma más natural y común; si no existe una palabra directa, adapta el sentido.",
    boliviano:
      "Eres un traductor experto en quechua boliviano. Traduce del español al quechua boliviano. Responde únicamente con la traducción, sin explicaciones ni comillas. Usa la forma más natural y común; si no existe una palabra directa, adapta el sentido.",
  },
  "qu-es": {
    sureno:
      "Eres un traductor experto en quechua sureño (Cusco-Collao). Traduce del quechua sureño al español. Responde únicamente con la traducción, sin explicaciones ni comillas. Respeta el sentido cultural de la frase.",
    boliviano:
      "Eres un traductor experto en quechua boliviano. Traduce del quechua boliviano al español. Responde únicamente con la traducción, sin explicaciones ni comillas. Respeta el sentido cultural de la frase.",
  },
};

const EXAMPLES = {
  "es-qu": ["Buenos días", "¿Cómo estás?", "Gracias por tu ayuda"],
  "qu-es": ["Allin p'unchay", "Imata ruwanki?", "Tupananchiskama"],
};

const $ = (id) => document.getElementById(id);

const els = {
  apiKey: $("apiKey"),
  toggleKey: $("toggleKey"),
  input: $("input"),
  translate: $("translate"),
  examples: $("examples"),
  result: $("result"),
  output: $("output"),
  copy: $("copy"),
  meta: $("meta"),
  error: $("error"),
  model: $("model"),
  variant: $("variant"),
  web: $("web"),
  dirButtons: Array.from(document.querySelectorAll(".seg")),
};

const state = {
  direction: "es-qu",
  loading: false,
};

const storage = {
  get(key) {
    try {
      return localStorage.getItem(key);
    } catch {
      return null;
    }
  },
  set(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch {
      /* localStorage puede estar bloqueado */
    }
  },
  remove(key) {
    try {
      localStorage.removeItem(key);
    } catch {
      /* localStorage puede estar bloqueado */
    }
  },
};

class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function setDirection(direction) {
  state.direction = direction;

  for (const button of els.dirButtons) {
    const active = button.dataset.dir === direction;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  }

  els.input.placeholder =
    direction === "es-qu"
      ? "Escribe una frase en español…"
      : "Escribe una frase en quechua…";

  renderExamples();
}

function renderExamples() {
  els.examples.replaceChildren();

  for (const phrase of EXAMPLES[state.direction]) {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "chip";
    chip.textContent = phrase;
    chip.addEventListener("click", () => {
      els.input.value = phrase;
      els.input.focus();
    });
    els.examples.appendChild(chip);
  }
}

function setLoading(loading) {
  state.loading = loading;
  els.translate.disabled = loading;
  els.translate.textContent = loading ? "Traduciendo…" : "Traducir";
  els.input.disabled = loading;
}

function showError(message) {
  els.error.textContent = message;
  els.error.hidden = false;
}

function clearError() {
  els.error.textContent = "";
  els.error.hidden = true;
}

function showResult(text, model, usage) {
  els.output.textContent = text;

  const meta = [model];
  if (usage && usage.total_tokens) meta.push(`${usage.total_tokens} tokens`);
  els.meta.textContent = meta.join(" · ");

  els.result.hidden = false;
  els.result.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function friendlyError(status, detail) {
  if (status === 401) {
    return "API key inválida o revocada. Revísala en openrouter.ai/keys.";
  }
  if (status === 402) {
    return "La cuenta no tiene créditos. Usa un modelo gratuito (:free) o agrega saldo en OpenRouter.";
  }
  if (status === 403) {
    return "OpenRouter bloqueó la solicitud (403). Revisa tu key o el modelo elegido.";
  }
  if (status === 404) {
    return "No se encontró ese modelo. Revisa el ID en openrouter.ai/models.";
  }
  if (status === 429) {
    return "Límite de solicitudes alcanzado (429). Los modelos gratuitos tienen un cupo diario: espera un poco o cambia de modelo.";
  }
  if (status >= 500) {
    return `OpenRouter tuvo un error (${status}). Intenta de nuevo en unos segundos.`;
  }
  return `Error ${status}: ${detail}`;
}

async function translate() {
  if (state.loading) return;

  clearError();

  const text = els.input.value.trim();
  const apiKey = els.apiKey.value.trim();
  const model = els.model.value.trim() || DEFAULT_MODEL;

  if (!apiKey) {
    showError("Primero pega tu API key de OpenRouter.");
    els.apiKey.focus();
    return;
  }

  if (!text) {
    showError("Escribe algo para traducir.");
    els.input.focus();
    return;
  }

  els.result.hidden = true;

  const direction = state.direction;
  const prompt = PROMPTS[direction][els.variant.value] || PROMPTS[direction].sureno;

  const body = {
    model,
    messages: [
      { role: "system", content: prompt },
      { role: "user", content: text },
    ],
    temperature: 0.2,
  };

  if (els.web.checked) {
    body.plugins = [{ id: "web", max_results: 3 }];
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS);

  setLoading(true);

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
        "X-Title": "Traductor Quechua",
      },
      body: JSON.stringify(body),
      signal: controller.signal,
    });

    let data = null;
    try {
      data = await response.json();
    } catch {
      /* respuesta sin JSON */
    }

    if (!response.ok) {
      const detail = data && data.error && data.error.message;
      throw new ApiError(response.status, detail || `Error HTTP ${response.status}`);
    }

    const content = data && data.choices && data.choices[0] && data.choices[0].message
      ? data.choices[0].message.content
      : "";

    if (!content || !content.trim()) {
      throw new Error("La respuesta llegó vacía. Intenta de nuevo.");
    }

    showResult(content.trim(), model, data.usage);
    storage.set(MODEL_STORAGE, model);
  } catch (error) {
    if (error.name === "AbortError") {
      showError("La solicitud tardó más de 60 segundos. Intenta otra vez.");
    } else if (error instanceof ApiError) {
      showError(friendlyError(error.status, error.message));
    } else {
      showError("No se pudo conectar con OpenRouter. Revisa tu conexión e inténtalo de nuevo.");
      console.error(error);
    }
  } finally {
    clearTimeout(timeout);
    setLoading(false);
  }
}

async function copyOutput() {
  const text = els.output.textContent;
  if (!text) return;

  let copied = false;

  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      copied = true;
    }
  } catch {
    /* probar el método clásico */
  }

  if (!copied) {
    try {
      const temp = document.createElement("textarea");
      temp.value = text;
      temp.setAttribute("readonly", "");
      temp.style.position = "fixed";
      temp.style.opacity = "0";
      document.body.appendChild(temp);
      temp.select();
      copied = document.execCommand("copy");
      temp.remove();
    } catch {
      copied = false;
    }
  }

  if (!copied) {
    showError("No se pudo copiar. Selecciona el texto manualmente.");
    return;
  }

  els.copy.textContent = "¡Copiado!";
  setTimeout(() => {
    els.copy.textContent = "Copiar";
  }, 1500);
}

function init() {
  const savedKey = storage.get(KEY_STORAGE);
  if (savedKey) els.apiKey.value = savedKey;

  const savedModel = storage.get(MODEL_STORAGE);
  if (savedModel) els.model.value = savedModel;

  els.apiKey.addEventListener("input", () => {
    const value = els.apiKey.value.trim();
    if (value) storage.set(KEY_STORAGE, value);
    else storage.remove(KEY_STORAGE);
  });

  els.toggleKey.addEventListener("click", () => {
    const visible = els.apiKey.type === "text";
    els.apiKey.type = visible ? "password" : "text";
    els.toggleKey.textContent = visible ? "Ver" : "Ocultar";
    els.toggleKey.setAttribute(
      "aria-label",
      visible ? "Mostrar API key" : "Ocultar API key"
    );
  });

  els.model.addEventListener("change", () => {
    const value = els.model.value.trim();
    if (value) storage.set(MODEL_STORAGE, value);
  });

  for (const button of els.dirButtons) {
    button.addEventListener("click", () => setDirection(button.dataset.dir));
  }

  els.translate.addEventListener("click", translate);
  els.copy.addEventListener("click", copyOutput);

  els.input.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
      event.preventDefault();
      translate();
    }
  });

  setDirection("es-qu");
}

init();
