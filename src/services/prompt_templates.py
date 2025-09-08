"""Prompt templates for optimized thinking sequence."""

PROMPT_TEMPLATES = {
    1: {
        "name": "Identificación del Sustrato",
        "template": """Para la pregunta del usuario: "{user_question}". Identifica exclusivamente los 2-3 campos de conocimiento (sustratos) más relevantes para abordarla. Responde solo con los nombres de dichos campos separados por comas.""",
        "expected_output": "Campo1, Campo2, Campo3"
    },

    2: {
        "name": "La Naturaleza del Problema",
        "template": """La pregunta "{user_question}" se enmarca en los sustratos: {response_1}. Desde la lógica interna de estos campos, explica en un párrafo muy breve por qué esta pregunta es paradójica, contraintuitiva o fundamentalmente desafiante. No des soluciones aún.""",
        "expected_output": "Un párrafo explicando la paradoja central"
    },

    3: {
        "name": "Tesis de Trabajo Inicial",
        "template": """Basándote en la paradoja identificada ({response_2}), formula una única tesis de trabajo que responda de manera tentativa a la pregunta original. Máximo dos oraciones. Debe ser una afirmación audaz y falseable.""",
        "expected_output": "Una tesis concisa y falsable"
    },

    4: {
        "name": "Iteración y Divergencia Controlada",
        "template": """Tu tesis actual es: {response_3}. Ahora, descártala deliberadamente. Genera una nueva tesis de trabajo que diverja radicalmente de la anterior (ej.: enfócate en factores culturales en lugar de institucionales, o en psicología cognitiva en lugar de economía). En un párrafo breve, explica por qué este nuevo enfoque podría ser más sólido o complementario.""",
        "expected_output": "Nueva tesis + explicación de por qué es mejor"
    },

    5: {
        "name": "Stress-Test y Síntesis",
        "template": """Somete la nueva tesis ({response_4}) a una única y fuerte crítica. Luego, en una sola oración, sintetiza el "Insight Principal" que sobrevive a este desafío. No narres el diálogo, solo presenta la crítica y el insight.""",
        "expected_output": "Crítica + Insight Principal en una oración"
    },

    6: {
        "name": "Alegoría Intuitiva",
        "template": """Tomando el "Insight Principal" ({response_5}), crea una analogía o metáfora simple y poderosa que lo capture. No expliques la metáfora, solo preséntala.""",
        "expected_output": "Una metáfora o analogía simple"
    },

    7: {
        "name": "Perspectiva del Sustrato Puro",
        "template": """Reformula el "Insight Principal" ({response_5}) utilizando únicamente la lógica y terminología de uno de los sustratos originales ({response_1}), como si fueras ese sistema pensando.""",
        "expected_output": "Reformulación desde la perspectiva de un sustrato específico"
    },

    8: {
        "name": "Gran Síntesis Final y TL;DR",
        "template": """Integra las siguientes piezas para responder de forma definitiva y clara a la pregunta original: "{user_question}".

- La paradoja central: {response_2}
- El insight sintetizado: {response_5}
- La alegoría: {response_6}
- La perspectiva del sistema: {response_7}

Estructura tu respuesta final en dos partes:
1. **Gran Síntesis:** Una narrativa coherente que construya desde lo simple hasta el momento "¡Eureka!".
2. **TL;DR:** Un párrafo final, epigramático y libre de jerga, que destile la verdad fundamental.""",
        "expected_output": "Respuesta completa con Gran Síntesis + TL;DR"
    }
}

def get_prompt_template(step_number: int) -> dict:
    """Get prompt template for a specific step."""
    return PROMPT_TEMPLATES.get(step_number, {})

def get_all_prompts() -> dict:
    """Get all prompt templates."""
    return PROMPT_TEMPLATES