"""
JSON Schemas para el sistema narrativo.

Define las estructuras de datos para:
- Escenas narrativas
- Dialogos con variantes
- Puntos de decision
- Condiciones y consecuencias

Estos schemas se usan para:
1. Validar contenido narrativo importado
2. Documentar la estructura esperada
3. Generar formularios de admin
"""
from typing import TypedDict, List, Optional, Dict, Any, Union
from enum import Enum


# =============================================================================
# ENUMS PARA SCHEMAS
# =============================================================================

class CharacterName(str, Enum):
    """Personajes disponibles."""
    DIANA = "diana"
    LUCIEN = "lucien"
    NARRATOR = "narrator"


class MediaType(str, Enum):
    """Tipos de media soportados."""
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    VOICE = "voice"
    DOCUMENT = "document"


class OptionStyle(str, Enum):
    """Estilos de opciones de respuesta."""
    BUTTON = "button"
    TEXT = "text"
    REACTION = "reaction"


# =============================================================================
# TIPOS PARA CONDICIONES
# =============================================================================

class ComparisonCondition(TypedDict, total=False):
    """Condicion de comparacion numerica."""
    # Exactamente una de estas debe estar presente
    gte: int  # >=
    gt: int   # >
    lte: int  # <=
    lt: int   # <
    eq: int   # ==
    ne: int   # !=


class ListCondition(TypedDict, total=False):
    """Condicion para listas."""
    has: str              # Contiene elemento
    has_all: List[str]    # Contiene todos
    has_any: List[str]    # Contiene alguno
    in_list: List[str]    # Valor esta en lista


class ConditionSchema(TypedDict, total=False):
    """
    Schema de condiciones para desbloquear contenido.

    Ejemplo:
        {
            "level": {">=": 3},
            "diana_trust": {">=": 50},
            "pattern": {"has": "patient"},
            "archetype": {"in": ["romantic", "introspective"]},
            "flags": {"has_all": ["completed_intro", "saw_diana_photo"]},
            "decisions": {"count": {">=": 10}},
            "response_time_avg": {"<": 60}
        }
    """
    # Nivel narrativo
    level: ComparisonCondition

    # Relaciones con personajes
    diana_trust: ComparisonCondition
    lucien_respect: ComparisonCondition
    intimacy_level: ComparisonCondition

    # Arquetipos
    archetype: ListCondition
    primary_archetype: str
    secondary_archetype: str

    # Patrones de comportamiento
    pattern: ListCondition

    # Flags narrativos
    flags: ListCondition
    completed_scenes: ListCondition
    unlocked_content: ListCondition

    # Metricas
    total_decisions: ComparisonCondition
    response_time_avg: ComparisonCondition
    participation_rate: ComparisonCondition

    # Operadores logicos
    and_: List["ConditionSchema"]  # $and
    or_: List["ConditionSchema"]   # $or
    not_: "ConditionSchema"        # $not


# =============================================================================
# TIPOS PARA CONSECUENCIAS
# =============================================================================

class ConsequenceSchema(TypedDict, total=False):
    """
    Schema de consecuencias de decisiones.

    Ejemplo:
        {
            "diana_trust": 5,
            "lucien_respect": -3,
            "archetype_introspective": 10,
            "add_flag": {"type": "achievements", "name": "honest_user"},
            "unlock": "diana_secret_scene",
            "next_scene": "cautious_path"
        }
    """
    # Modificadores de relacion
    diana_trust: int
    lucien_respect: int
    intimacy_level: int

    # Modificadores de arquetipo
    archetype_introspective: int
    archetype_direct: int
    archetype_romantic: int
    archetype_analytical: int

    # Flags
    add_flag: Dict[str, str]  # {"type": "...", "name": "..."}
    remove_flag: Dict[str, str]

    # Desbloqueo de contenido
    unlock: str
    block: str

    # Navegacion
    next_scene: str
    next_dialogue: str
    next_trigger: str

    # Especiales
    add_memory: Dict[str, str]  # {"character": "...", "memory": "..."}
    reward: Dict[str, Any]


# =============================================================================
# TIPOS PARA OPCIONES DE DIALOGO
# =============================================================================

class DialogueOptionSchema(TypedDict, total=False):
    """
    Schema de una opcion de respuesta en un dialogo.

    Ejemplo:
        {
            "key": "honest_response",
            "text": "Decirle la verdad",
            "style": "button",
            "conditions": {"diana_trust": {">=": 20}},
            "consequences": {
                "diana_trust": 10,
                "archetype_direct": 15
            },
            "hidden_text": "Solo visible si cumples condiciones"
        }
    """
    # Identificador unico de la opcion
    key: str  # Required

    # Texto mostrado al usuario
    text: str  # Required

    # Estilo de presentacion
    style: str  # "button" | "text" | "reaction"

    # Condiciones para mostrar esta opcion
    conditions: ConditionSchema

    # Consecuencias de elegir esta opcion
    consequences: ConsequenceSchema

    # Texto alternativo si no cumple condiciones
    hidden_text: str

    # Metadata
    archetype_hint: str  # Arquetipo asociado
    timing_bonus: Dict[str, int]  # Bonus por tiempo de respuesta


# =============================================================================
# TIPOS PARA VARIANTES DE DIALOGO
# =============================================================================

class DialogueVariantSchema(TypedDict, total=False):
    """
    Schema de una variante de dialogo.

    Las variantes permiten personalizar el texto segun el usuario.

    Ejemplo:
        {
            "text": "Texto alternativo para romanticos...",
            "tone": "warm",
            "media": {"type": "photo", "file_id": "..."}
        }
    """
    text: str
    tone: str
    media: Dict[str, str]
    options: List[DialogueOptionSchema]


class DialogueVariantsSchema(TypedDict, total=False):
    """
    Contenedor de variantes por arquetipo/estado.

    Ejemplo:
        {
            "introspective": {"text": "Para introspectivos..."},
            "romantic": {"text": "Para romanticos..."},
            "diana_vulnerable": {"text": "Cuando Diana es vulnerable..."},
            "default": {"text": "Por defecto..."}
        }
    """
    # Por arquetipo
    introspective: DialogueVariantSchema
    direct: DialogueVariantSchema
    romantic: DialogueVariantSchema
    analytical: DialogueVariantSchema

    # Por estado de relacion
    diana_mysterious: DialogueVariantSchema
    diana_revealing: DialogueVariantSchema
    diana_vulnerable: DialogueVariantSchema
    lucien_cold: DialogueVariantSchema
    lucien_warming: DialogueVariantSchema
    lucien_trusted: DialogueVariantSchema

    # Default
    default: DialogueVariantSchema


# =============================================================================
# TIPOS PARA DIALOGOS
# =============================================================================

class MediaSchema(TypedDict, total=False):
    """Schema de media adjunto."""
    type: str  # "photo" | "video" | "audio" | "voice"
    file_id: str
    url: str
    caption: str


class DialogueSchema(TypedDict, total=False):
    """
    Schema completo de un dialogo narrativo.

    Ejemplo:
        {
            "id": "intro_welcome_diana",
            "character": "diana",
            "text": "Bienvenido a mi mundo...",
            "media": {"type": "photo", "file_id": "AgACAgIA..."},
            "options": [
                {"key": "curious", "text": "Cuentame mas..."},
                {"key": "direct", "text": "Quien eres?"}
            ],
            "variants": {
                "romantic": {"text": "Texto para romanticos..."},
                "default": {"text": "Texto por defecto..."}
            },
            "triggers": ["scene_start", "diana_intro"],
            "conditions": {"level": {">=": 1}},
            "on_display": {"diana_trust": 1}
        }
    """
    # Identificacion
    id: str  # Required - Identificador unico
    scene_id: str  # ID de la escena padre

    # Personaje
    character: str  # "diana" | "lucien" | "narrator"

    # Contenido
    text: str  # Texto principal del dialogo
    media: MediaSchema  # Media adjunto opcional

    # Opciones de respuesta
    options: List[DialogueOptionSchema]
    allow_text_input: bool  # Permitir respuesta de texto libre
    text_input_prompt: str  # Prompt para entrada de texto

    # Variantes de personalizacion
    variants: DialogueVariantsSchema

    # Activacion
    triggers: List[str]  # Triggers que activan este dialogo
    conditions: ConditionSchema  # Condiciones para mostrar

    # Efectos automaticos
    on_display: ConsequenceSchema  # Al mostrar el dialogo
    on_timeout: ConsequenceSchema  # Si no responde en X tiempo

    # Configuracion
    timeout_seconds: int  # Tiempo antes de timeout
    order: int  # Orden en la secuencia


# =============================================================================
# TIPOS PARA PUNTOS DE DECISION
# =============================================================================

class DecisionPointSchema(TypedDict, total=False):
    """
    Schema de un punto de decision en una escena.

    Los puntos de decision son momentos donde el usuario debe elegir.

    Ejemplo:
        {
            "id": "intro_first_choice",
            "type": "dialogue",
            "dialogue_id": "intro_choice_1",
            "branches": {
                "honest": "path_honest",
                "curious": "path_curious",
                "silent": "path_silent"
            },
            "timeout_branch": "path_silent",
            "timeout_seconds": 300
        }
    """
    # Identificacion
    id: str  # Required

    # Tipo de decision
    type: str  # "dialogue" | "reaction" | "timed"

    # Referencia al dialogo
    dialogue_id: str

    # Ramas segun eleccion
    branches: Dict[str, str]  # {choice_key: next_scene_or_dialogue}

    # Timeout
    timeout_seconds: int
    timeout_branch: str  # Rama si hay timeout

    # Condiciones
    conditions: ConditionSchema


# =============================================================================
# TIPOS PARA ESCENAS
# =============================================================================

class SceneSchema(TypedDict, total=False):
    """
    Schema completo de una escena narrativa.

    Una escena es una unidad de contenido que contiene dialogos
    y puntos de decision.

    Ejemplo completo:
        {
            "scene_id": "level1_intro",
            "name": "Bienvenida al Mundo",
            "chapter_id": "chapter_1",
            "channel": "los_kinkys",
            "level_required": 1,

            "dialogues": [
                {
                    "id": "intro_1",
                    "character": "lucien",
                    "text": "Bienvenido, nuevo visitante...",
                    "triggers": ["scene_start"]
                },
                {
                    "id": "intro_2",
                    "character": "diana",
                    "text": "No le hagas caso a Lucien...",
                    "triggers": ["intro_1_complete"],
                    "options": [
                        {"key": "curious", "text": "Quien eres?"},
                        {"key": "direct", "text": "Que es este lugar?"}
                    ]
                }
            ],

            "decision_points": [
                {
                    "id": "first_impression",
                    "dialogue_id": "intro_2",
                    "branches": {
                        "curious": "path_curious",
                        "direct": "path_direct"
                    }
                }
            ],

            "conditions": {
                "level": {">=": 1}
            },

            "consequences": [
                {
                    "id": "complete_intro",
                    "trigger": "scene_complete",
                    "effect": {
                        "add_flag": {"type": "completed_scenes", "name": "level1_intro"},
                        "unlock": "level1_mission_1"
                    }
                }
            ],

            "metadata": {
                "author": "creator",
                "version": "1.0",
                "tags": ["intro", "free", "level1"]
            }
        }
    """
    # Identificacion
    scene_id: str  # Required - Identificador unico
    name: str  # Nombre legible
    description: str  # Descripcion para admin

    # Organizacion
    chapter_id: str  # Capitulo padre
    channel: str  # "los_kinkys" | "el_divan"
    order: int  # Orden en el capitulo

    # Requisitos
    level_required: int
    conditions: ConditionSchema

    # Contenido
    dialogues: List[DialogueSchema]
    decision_points: List[DecisionPointSchema]

    # Consecuencias de completar la escena
    consequences: List[Dict[str, Any]]

    # Configuracion
    allow_replay: bool  # Permitir repetir escena
    auto_advance: bool  # Avanzar automaticamente entre dialogos
    advance_delay: int  # Segundos entre dialogos automaticos

    # Metadata
    metadata: Dict[str, Any]


# =============================================================================
# EJEMPLO COMPLETO DE ESCENA
# =============================================================================

EXAMPLE_SCENE: SceneSchema = {
    "scene_id": "level1_intro",
    "name": "Bienvenida al Universo",
    "description": "Primera escena del nivel 1. Introduce a Diana y Lucien.",
    "chapter_id": "chapter_1",
    "channel": "los_kinkys",
    "order": 1,
    "level_required": 1,

    "conditions": {
        "level": {"gte": 1}
    },

    "dialogues": [
        {
            "id": "intro_lucien_1",
            "scene_id": "level1_intro",
            "character": "lucien",
            "text": (
                "Vaya, vaya... Un nuevo visitante.\n\n"
                "No todos los dias alguien encuentra este lugar. "
                "Debo admitir que me intriga saber como llegaste aqui."
            ),
            "triggers": ["level1_intro_start"],
            "order": 1,
            "on_display": {
                "lucien_respect": 1
            }
        },
        {
            "id": "intro_diana_1",
            "scene_id": "level1_intro",
            "character": "diana",
            "text": (
                "No le hagas mucho caso a Lucien. "
                "Le gusta hacerse el misterioso.\n\n"
                "Yo soy Diana. Este es mi mundo... nuestro mundo, si decides quedarte."
            ),
            "media": {
                "type": "photo",
                "file_id": "placeholder_diana_intro"
            },
            "triggers": ["intro_lucien_1_complete"],
            "order": 2,
            "variants": {
                "romantic": {
                    "text": (
                        "No le hagas caso a Lucien, siempre tan serio.\n\n"
                        "Soy Diana. Y algo me dice que tu y yo "
                        "vamos a llevarnos muy bien..."
                    ),
                    "tone": "warm"
                },
                "analytical": {
                    "text": (
                        "Ignora a Lucien por ahora.\n\n"
                        "Me llamo Diana. Si estas aqui, imagino que "
                        "buscas algo mas que entretenimiento superficial."
                    ),
                    "tone": "intrigued"
                },
                "default": {
                    "text": (
                        "No le hagas mucho caso a Lucien.\n\n"
                        "Soy Diana. Bienvenido a mi mundo."
                    )
                }
            }
        },
        {
            "id": "intro_choice_1",
            "scene_id": "level1_intro",
            "character": "diana",
            "text": "Asi que, nuevo visitante... que te trae por aqui?",
            "triggers": ["intro_diana_1_complete"],
            "order": 3,
            "options": [
                {
                    "key": "curious_about_world",
                    "text": "Quiero saber mas sobre este lugar",
                    "archetype_hint": "introspective",
                    "consequences": {
                        "archetype_introspective": 10,
                        "diana_trust": 3,
                        "next_trigger": "path_curious"
                    }
                },
                {
                    "key": "curious_about_diana",
                    "text": "Me intrigas tu, Diana",
                    "archetype_hint": "romantic",
                    "consequences": {
                        "archetype_romantic": 10,
                        "diana_trust": 5,
                        "next_trigger": "path_romantic"
                    }
                },
                {
                    "key": "direct_purpose",
                    "text": "Vine buscando algo especifico",
                    "archetype_hint": "direct",
                    "consequences": {
                        "archetype_direct": 10,
                        "lucien_respect": 3,
                        "next_trigger": "path_direct"
                    }
                },
                {
                    "key": "analytical_observe",
                    "text": "Primero quiero observar y entender",
                    "archetype_hint": "analytical",
                    "consequences": {
                        "archetype_analytical": 10,
                        "lucien_respect": 5,
                        "next_trigger": "path_analytical"
                    }
                }
            ],
            "timeout_seconds": 300,
            "on_timeout": {
                "next_trigger": "path_silent",
                "add_flag": {"type": "special_flags", "name": "silent_first_choice"}
            }
        }
    ],

    "decision_points": [
        {
            "id": "first_impression_choice",
            "type": "dialogue",
            "dialogue_id": "intro_choice_1",
            "branches": {
                "curious_about_world": "scene_curious_world",
                "curious_about_diana": "scene_curious_diana",
                "direct_purpose": "scene_direct_path",
                "analytical_observe": "scene_analytical_path"
            },
            "timeout_branch": "scene_silent_path",
            "timeout_seconds": 300
        }
    ],

    "consequences": [
        {
            "id": "intro_complete",
            "trigger": "scene_complete",
            "effect": {
                "add_flag": {"type": "completed_scenes", "name": "level1_intro"},
                "add_flag": {"type": "achievements", "name": "first_meeting"},
                "unlock": "level1_mission_1"
            }
        }
    ],

    "allow_replay": False,
    "auto_advance": False,

    "metadata": {
        "author": "narrative_team",
        "version": "1.0.0",
        "created_at": "2026-01-09",
        "tags": ["intro", "free", "level1", "character_intro"]
    }
}


# =============================================================================
# VALIDACION DE SCHEMAS
# =============================================================================

def validate_scene(scene_data: Dict[str, Any]) -> List[str]:
    """
    Valida un diccionario contra el schema de escena.

    Args:
        scene_data: Datos de la escena a validar

    Returns:
        List[str]: Lista de errores encontrados (vacia si valido)
    """
    errors = []

    # Campos requeridos
    if "scene_id" not in scene_data:
        errors.append("Falta campo requerido: scene_id")

    if "dialogues" not in scene_data:
        errors.append("Falta campo requerido: dialogues")
    elif not isinstance(scene_data["dialogues"], list):
        errors.append("dialogues debe ser una lista")
    else:
        for i, dialogue in enumerate(scene_data["dialogues"]):
            dialogue_errors = validate_dialogue(dialogue)
            for err in dialogue_errors:
                errors.append(f"dialogues[{i}]: {err}")

    # Validar decision_points si existen
    if "decision_points" in scene_data:
        if not isinstance(scene_data["decision_points"], list):
            errors.append("decision_points debe ser una lista")
        else:
            for i, dp in enumerate(scene_data["decision_points"]):
                if "id" not in dp:
                    errors.append(f"decision_points[{i}]: falta id")
                if "dialogue_id" not in dp:
                    errors.append(f"decision_points[{i}]: falta dialogue_id")

    return errors


def validate_dialogue(dialogue_data: Dict[str, Any]) -> List[str]:
    """
    Valida un diccionario contra el schema de dialogo.

    Args:
        dialogue_data: Datos del dialogo a validar

    Returns:
        List[str]: Lista de errores encontrados
    """
    errors = []

    # Campos requeridos
    if "id" not in dialogue_data:
        errors.append("Falta campo requerido: id")

    if "text" not in dialogue_data and "variants" not in dialogue_data:
        errors.append("Debe tener 'text' o 'variants'")

    # Validar opciones si existen
    if "options" in dialogue_data:
        if not isinstance(dialogue_data["options"], list):
            errors.append("options debe ser una lista")
        else:
            for i, opt in enumerate(dialogue_data["options"]):
                if "key" not in opt:
                    errors.append(f"options[{i}]: falta key")
                if "text" not in opt:
                    errors.append(f"options[{i}]: falta text")

    # Validar character
    if "character" in dialogue_data:
        valid_characters = ["diana", "lucien", "narrator"]
        if dialogue_data["character"] not in valid_characters:
            errors.append(f"character invalido: {dialogue_data['character']}")

    return errors


def validate_conditions(conditions: Dict[str, Any]) -> List[str]:
    """
    Valida un diccionario de condiciones.

    Args:
        conditions: Condiciones a validar

    Returns:
        List[str]: Lista de errores encontrados
    """
    errors = []

    valid_operators = [">=", ">", "<=", "<", "==", "!=", "in", "has", "has_all", "has_any"]
    valid_attributes = [
        "level", "diana_trust", "lucien_respect", "intimacy_level",
        "archetype", "pattern", "flags", "total_decisions",
        "response_time_avg", "participation_rate"
    ]

    for attr, condition in conditions.items():
        if attr.startswith("$"):
            # Operador logico
            if attr not in ["$and", "$or", "$not"]:
                errors.append(f"Operador logico invalido: {attr}")
        elif attr not in valid_attributes:
            errors.append(f"Atributo de condicion invalido: {attr}")

        if isinstance(condition, dict):
            for op in condition.keys():
                if op not in valid_operators:
                    errors.append(f"Operador invalido en {attr}: {op}")

    return errors
