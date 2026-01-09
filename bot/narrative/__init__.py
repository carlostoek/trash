"""
Modulo de narrativa interactiva.

Componentes:
- schemas: Definiciones de estructuras JSON para contenido narrativo
- loader: Carga y cache de contenido narrativo (TODO)
- renderer: Renderizado de dialogos para Telegram (TODO)

El motor principal esta en bot/services/narrative.py
"""
from bot.narrative.schemas import (
    SceneSchema,
    DialogueSchema,
    DialogueOptionSchema,
    ConditionSchema,
    ConsequenceSchema,
    validate_scene,
    validate_dialogue,
    validate_conditions,
    EXAMPLE_SCENE
)

__all__ = [
    "SceneSchema",
    "DialogueSchema",
    "DialogueOptionSchema",
    "ConditionSchema",
    "ConsequenceSchema",
    "validate_scene",
    "validate_dialogue",
    "validate_conditions",
    "EXAMPLE_SCENE"
]
