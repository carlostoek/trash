"""
Narrative Formatters - Utilidades de formateo para contenido narrativo.

Este módulo proporciona funciones para formatear mensajes narrativos
basándose en el personaje, emoción, y variante de arquetipo.
"""
import logging
from typing import Optional, Dict, Any
from aiogram.types import InlineKeyboardMarkup

from bot.database.models import StoryFragment, ArchetypeProfile

logger = logging.getLogger(__name__)


# Character voice formatting
CHARACTER_EMOJIS = {
    "DIANA": "🌸",
    "LUCIEN": "🎩",
    "NARRATOR": "📖",
    "UNKNOWN": "💭"
}

EMOTION_INDICATORS = {
    "happy": "😊",
    "sad": "😢",
    "angry": "😠",
    "fearful": "😨",
    "surprised": "😲",
    "confused": "😕",
    "excited": "🤩",
    "calm": "😌",
    "tense": "😬",
    "romantic": "💕",
    "mysterious": "🌙"
}


def format_narrative_message(
    fragment: StoryFragment,
    archetype: Optional[ArchetypeProfile] = None
) -> str:
    """
    Formatea un mensaje narrativo basado en el fragmento y arquetipo.

    Args:
        fragment: StoryFragment a formatear
        archetype: ArchetypeProfile del usuario (opcional)

    Returns:
        String con el mensaje formateado para Telegram

    Example:
        >>> fragment = StoryFragment(
        ...     speaker="DIANA",
        ...     emotion="happy",
        ...     content="Hello there!",
        ...     content_variants={}
        ... )
        >>> format_narrative_message(fragment)
        '🌸 <i>(feliz)</i>\\n\\nHello there!'
    """
    # 1. Determinar emoji de personaje
    character_emoji = CHARACTER_EMOJIS.get(fragment.speaker, CHARACTER_EMOJIS["UNKNOWN"])

    # 2. Obtener contenido con variante de arquetipo si existe
    content = fragment.content

    if archetype and fragment.content_variants:
        # Buscar variante específica del arquetipo
        primary = archetype.primary_archetype.lower() if archetype.primary_archetype else "explorer"
        secondary = archetype.secondary_archetype.lower() if archetype.secondary_archetype else None

        # Intentar primario primero, luego secundario
        if primary in fragment.content_variants:
            content = fragment.content_variants[primary]
            logger.debug(f"Using {primary} variant for fragment {fragment.fragment_id}")
        elif secondary and secondary in fragment.content_variants:
            content = fragment.content_variants[secondary]
            logger.debug(f"Using {secondary} variant for fragment {fragment.fragment_id}")

    # 3. Construir header
    header_parts = [character_emoji]

    # Añadir indicador de emoción si existe
    if fragment.emotion:
        emotion_emoji = EMOTION_INDICATORS.get(fragment.emotion.lower(), "")
        if emotion_emoji:
            header_parts.append(f"<i>({fragment.emotion.lower()})</i>")

    # 4. Construir mensaje completo
    header = " ".join(header_parts) if len(header_parts) > 1 else character_emoji

    # Añadir título si existe
    title = f"<b>{fragment.title}</b>\n\n" if fragment.title else ""

    # Añadir nivel narrativo si es nivel 4+ (VIP)
    level_indicator = ""
    if fragment.narrative_level >= 4:
        level_indicator = f"🔒 <b>Nivel VIP {fragment.narrative_level}</b>\n\n"

    # Combinar todo
    message = f"{level_indicator}{title}{header}\n\n{content}"

    return message


def format_choice_button_text(choice, archetype: Optional[ArchetypeProfile] = None) -> str:
    """
    Formatea el texto de un botón de elección.

    Args:
        choice: StoryChoice a formatear
        archetype: ArchetypeProfile del usuario (opcional)

    Returns:
        String con el texto del botón formateado

    Example:
        >>> choice = StoryChoice(
        ...     choice_text="Follow her",
        ...     choice_emoji="👣",
        ...     text_variants={}
        ... )
        >>> format_choice_button_text(choice)
        '👣 Follow her'
    """
    # Obtener texto con variante de arquetipo
    text = choice.choice_text

    if archetype and choice.text_variants:
        primary = archetype.primary_archetype.lower() if archetype.primary_archetype else "explorer"
        secondary = archetype.secondary_archetype.lower() if archetype.secondary_archetype else None

        if primary in choice.text_variants:
            text = choice.text_variants[primary]
        elif secondary and secondary in choice.text_variants:
            text = choice.text_variants[secondary]

    # Añadir emoji si existe
    if choice.choice_emoji:
        return f"{choice.choice_emoji} {text}"

    return text


def format_unlock_message(fragment: StoryFragment, unlock_reason: str) -> str:
    """
    Formatea un mensaje de contenido bloqueado.

    Args:
        fragment: StoryFragment que está bloqueado
        unlock_reason: Razón del bloqueo

    Returns:
        String con el mensaje de bloqueo formateado

    Example:
        >>> fragment = StoryFragment(narrative_level=4, title="The Secret")
        >>> format_unlock_message(fragment, "VIP required")
        '🔒 <b>Contenido Bloqueado</b>\\n\\nThe Secret\\n\\n🔒 VIP required'
    """
    title = fragment.title if fragment.title else "Fragmento Bloqueado"

    message = (
        f"🔒 <b>Contenido Bloqueado</b>\n\n"
        f"{title}\n\n"
        f"{unlock_reason}"
    )

    return message


def format_consequences_message(consequences: Dict[str, Any]) -> str:
    """
    Formatea un mensaje con las consecuencias aplicadas.

    Args:
        consequences: Dict con consecuencias aplicadas
            {
                "flags_set": ["flag1", "flag2"],
                "flags_unset": ["flag3"],
                "archetype_points": {"romantic": +2},
                "relationship_changes": {"LUCIEN": +5}
            }

    Returns:
        String con las consecuencias formateadas

    Example:
        >>> consequences = {
        ...     "flags_set": ["met_diana"],
        ...     "archetype_points": {"romantic": +2}
        ... }
        >>> format_consequences_message(consequences)
        '✨ <b>Consecuencias:</b>\\n\\n🎯 Nueva información descubierta\\n💕 +2 puntos Romántico'
    """
    parts = ["✨ <b>Consecuencias:</b>\n"]

    # Flags establecidos
    if consequences.get("flags_set"):
        parts.append("🎯 Nueva información descubierta")

    # Puntos de arquetipo
    archetype_points = consequences.get("archetype_points", {})
    if archetype_points:
        for archetype, points in archetype_points.items():
            if points > 0:
                archetype_name = archetype.capitalize()
                emoji = {
                    "romantic": "💕",
                    "direct": "⚡",
                    "explorer": "🔍",
                    "analytical": "🧠",
                    "patient": "⏳",
                    "persistent": "💪"
                }.get(archetype.lower(), "📊")

                parts.append(f"{emoji} +{points} puntos {archetype_name}")

    # Cambios de relación
    relationship_changes = consequences.get("relationship_changes", {})
    if relationship_changes:
        for character, change in relationship_changes.items():
            character_name = character.capitalize()
            if change > 0:
                parts.append(f"❤️ Mejoró relación con {character_name}")
            elif change < 0:
                parts.append(f"💔 Empeoró relación con {character_name}")

    return "\n".join(parts) if len(parts) > 1 else ""


def format_story_status(progress, archetype, relationships: Dict[str, Any]) -> str:
    """
    Formatea el estado actual de la historia del usuario.

    Args:
        progress: UserNarrativeProgress del usuario
        archetype: ArchetypeProfile del usuario
        relationships: Dict con relaciones {"LUCIEN": relationship, "DIANA": relationship}

    Returns:
        String con el estado formateado

    Example:
        >>> format_story_status(progress, archetype, relationships)
        '📖 <b>Estado de Historia</b>\\n\\n📍 Nivel actual: 3\\n🎯 Arquetipo: Explorador...'
    """
    parts = ["📖 <b>Estado de Historia</b>\n"]

    # Nivel actual
    parts.append(f"\n📍 Nivel actual: {progress.current_narrative_level}")

    # Niveles completados
    if progress.levels_completed:
        levels_str = ", ".join(map(str, sorted(progress.levels_completed)))
        parts.append(f"✅ Niveles completados: {levels_str}")

    # Arquetipo
    if archetype:
        confidence = archetype.archetype_confidence or 0
        archetype_name = archetype.primary_archetype or "EXPLORER"
        parts.append(f"\n🎯 Arquetipo: {archetype_name} ({confidence}%)")

        if archetype.secondary_archetype:
            parts.append(f"   Secundario: {archetype.secondary_archetype}")

    # Relaciones
    if relationships:
        parts.append("\n💝 Relaciones:")

        for character_name, relationship in relationships.items():
            if relationship:
                score = relationship.relationship_score or 0
                status = relationship.relationship_status or "Desconocido"

                # Emoji basado en score
                if score >= 60:
                    emoji = "💕"  # Romántico
                elif score >= 40:
                    emoji = "💛"  # Buen amigo
                elif score >= 20:
                    emoji = "🤝"  # Amigo
                elif score >= 0:
                    emoji = "😐"  # Conocido
                else:
                    emoji = "💔"  # Negativo

                parts.append(f"   {emoji} {character_name}: {status} ({score})")

    # Estadísticas
    parts.append(f"\n📊 Estadísticas:")
    parts.append(f"   Elecciones totales: {progress.total_choices_made}")
    parts.append(f"   Fragmentos vistos: {len(progress.fragments_completed)}")

    return "\n".join(parts)


def escape_html(text: str) -> str:
    """
    Escapa caracteres especiales HTML para mensajes de Telegram.

    Args:
        text: Texto a escapar

    Returns:
        Texto con caracteres HTML escapados

    Example:
        >>> escape_html("<b>Hello</b>")
        '&lt;b&gt;Hello&lt;/b&gt;'
    """
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
    )


def format_multimedia_fragment(fragment: StoryFragment) -> Optional[Dict[str, Any]]:
    """
    Formatea información multimedia de un fragmento.

    Args:
        fragment: StoryFragment con multimedia

    Returns:
        Dict con tipo y file_id, o None si no hay multimedia

    Example:
        >>> fragment = StoryFragment(media_type="photo", media_file_id="AgAD...")
        >>> format_multimedia_fragment(fragment)
        {'type': 'photo', 'file_id': 'AgAD...'}
    """
    if not fragment.media_type or not fragment.media_file_id:
        return None

    return {
        "type": fragment.media_type,  # 'photo' o 'video'
        "file_id": fragment.media_file_id,
        "caption": fragment.content  # Usar contenido como caption
    }
