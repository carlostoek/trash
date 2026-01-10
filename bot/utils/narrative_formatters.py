"""
Narrative Formatters - Utilidades de formateo para contenido narrativo.

Este módulo proporciona funciones para formatear mensajes narrativos
basándose en el personaje, emoción, y variante de arquetipo.

FASE 2 ADDITIONS:
- format_progress_indicator: Barra de progreso visual incrustada
- format_milestone_celebration: Celebraciones de milestones
- format_dynamic_voice: Voz dinámica según relación
- format_rewards_summary: Resumen de recompensas (besitos, XP)
"""
import logging
from typing import Optional, Dict, Any, List, Tuple
from aiogram.types import InlineKeyboardMarkup

from bot.database.models import (
    StoryFragment,
    ArchetypeProfile,
    UserNarrativeProgress,
    CharacterRelationship
)

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
    content = fragment.content_text or ""

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
    if fragment.speaker_emotion:
        emotion_emoji = EMOTION_INDICATORS.get(fragment.speaker_emotion.lower(), "")
        if emotion_emoji:
            header_parts.append(f"<i>({fragment.speaker_emotion.lower()})</i>")

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
        "caption": fragment.content_text  # Usar contenido como caption
    }


# ==============================================================================
# FASE 2: UX POLISH - FUNCIONES MEJORADAS
# ==============================================================================

def format_progress_indicator(
    current_fragment: StoryFragment,
    user_progress: UserNarrativeProgress,
    total_fragments_in_level: Optional[int] = None
) -> str:
    """
    Crea indicador visual de progreso incrustado en mensajes narrativos.

    Args:
        current_fragment: Fragmento actual del usuario
        user_progress: Progreso narrativo del usuario
        total_fragments_in_level: Total de fragmentos en el nivel (si se conoce)

    Returns:
        String con barra de progreso visual

    Example:
        >>> fragment = StoryFragment(narrative_level=1)
        >>> progress = UserNarrativeProgress(fragments_completed=["L1_INTRO_001", "L1_INTRO_002"])
        >>> format_progress_indicator(fragment, progress, total_fragments_in_level=3)
        '\\n\\n📖 Nivel 1 de 6\\n▓▓░ 67% (2/3 fragmentos)'
    """
    level = current_fragment.narrative_level

    # Fragmentos completados en este nivel
    completed = len([
        f for f in user_progress.fragments_completed or []
        if f.startswith(f"L{level}_")
    ])

    # Estimar total si no se proporciona
    if total_fragments_in_level is None:
        # Estimación basada en nivel (más fragmentos en niveles más altos)
        total_fragments_in_level = 3 + (level - 1)  # L1=3, L2=4, L3=5, etc.

    # Calcular porcentaje
    percentage = int((completed / total_fragments_in_level) * 100) if total_fragments_in_level > 0 else 0

    # Crear barra visual
    # 10 segmentos para simplicidad
    segments = 10
    filled_segments = int((completed / total_fragments_in_level) * segments)
    filled = "▓" * filled_segments
    empty = "░" * (segments - filled_segments)

    return (
        f"\n\n📖 Nivel {level} de 6\n"
        f"{filled}{empty} {percentage}% ({completed}/{total_fragments_in_level} fragmentos)"
    )


def format_milestone_celebration(
    milestone_type: str,
    details: Dict[str, Any]
) -> str:
    """
    Genera mensaje de celebración para milestones narrativos.

    Args:
        milestone_type: Tipo de milestone ("level_complete", "archetype_detected",
                           "relationship_milestone", "first_completion")
        details: Dict con detalles del milestone

    Returns:
        String con mensaje de celebración formateado

    Example:
        >>> format_milestone_celebration("level_complete", {"level": 1, "title": "Primeros Pasos"})
        '🎉 **¡FELICIDADES!**\\n\\nHas completado el Nivel 1: "Primeros Pasos"\\n\\n✨ 50 besitos bonus...'
    """
    parts = ["🎉"]

    if milestone_type == "level_complete":
        level = details.get("level", 1)
        title = details.get("title", f"Nivel {level}")
        parts.append(f"<b>¡NIVEL {level} COMPLETADO!</b>\n")
        parts.append(f"Has completado: <i>{title}</i>\n")
        parts.append("\n✨ Has desbloqueado nuevas oportunidades")

    elif milestone_type == "archetype_detected":
        archetype = details.get("archetype", "EXPLORER")
        confidence = details.get("confidence", 50)
        parts.append(f"<b>¡ARQUETIPO DESCUBIERTO!</b>\n")
        parts.append(f"Eres: <i>{archetype}</i> ({confidence}% confianza)\n")
        parts.append("\n🔮 Diana ahora puede adaptarse a quién eres")

    elif milestone_type == "relationship_milestone":
        character = details.get("character", "DIANA")
        milestone = details.get("milestone", "Friendly")
        emoji = "💛" if milestone == "Friendly" else "💕" if milestone == "Romantic Interest" else "❤️"
        parts.append(f"<b>¡NUEVA CONEXIÓN!</b>\n")
        parts.append(f"{emoji} {character} ahora te considera: <i>{milestone}</i>\n")
        parts.append("\n💝 Esto afectará cómo te trata en el futuro")

    elif milestone_type == "first_completion":
        parts.append("<b>¡PRIMERA VEZ!</b>\n")
        parts.append("Has completado este fragmento por primera vez\n")
        parts.append("\n🎁 50 besitos bonus por tu exploración")

    # Añadir rewards si se proporcionan
    if details.get("besitos_reward", 0) > 0:
        parts.append(f"\n🪙 +{details['besitos_reward']} besitos")
    if details.get("xp_reward", 0) > 0:
        parts.append(f"\n⭐ +{details['xp_reward']} XP")
    if details.get("badge"):
        parts.append(f"\n🏅 Badge: {details['badge']}")

    return "\n".join(parts)


def format_dynamic_voice(
    fragment: StoryFragment,
    user_progress: UserNarrativeProgress,
    relationship_diana: Optional[CharacterRelationship],
    archetype: Optional[ArchetypeProfile]
) -> str:
    """
    Formatea mensaje con voz dinámica según relación y arquetipo.

    Args:
        fragment: StoryFragment a formatear
        user_progress: Progreso del usuario
        relationship_diana: Relación con Diana (opcional)
        archetype: Arquetipo del usuario (opcional)

    Returns:
        String con mensaje formateado dinámicamente

    Example:
        >>> # Relación 60 (íntima)
        >>> format_dynamic_voice(fragment, progress, relationship(60), archetype)
        '🌸 <i>(íntima, exclusiva)</i>\\n\\nEntre tú y yo...'
    """
    # Obtener emoji de personaje
    character_emoji = CHARACTER_EMOJIS.get(fragment.speaker, CHARACTER_EMOJIS["UNKNOWN"])

    # Obtener score de relación
    score = relationship_diana.relationship_score if relationship_diana else 0

    # Determinar tono basado en score
    if score < 20:
        # Formal, distante
        tone_indicator = "formal"
        tone_desc = "formal"
    elif score < 40:
        # Amigable, primera vez que trata de tú
        tone_indicator = "amigable"
        tone_desc = "amigable"
    elif score < 60:
        # Vulnerable, confía
        tone_indicator = "cercana"
        tone_desc = "cercana"
    else:
        # Íntima, exclusivo
        tone_indicator = "íntima"
        tone_desc = "íntima, exclusiva"

    # Construir header con tono dinámico
    header_parts = [character_emoji]

    # Añadir indicador de tono/emoción
    if fragment.speaker_emotion:
        emotion_emoji = EMOTION_INDICATORS.get(fragment.speaker_emotion.lower(), "")
        header_parts.append(f"<i>({tone_desc}{f', {fragment.speaker_emotion.lower()}' if emotion_emoji else ''})</i>")
    else:
        header_parts.append(f"<i>({tone_desc})</i>")

    header = " ".join(header_parts)

    # Obtener contenido con variante según tono
    content = fragment.content_text or ""

    # Aplicar variante de tono si existe
    if fragment.content_variants and tone_indicator in fragment.content_variants:
        content = fragment.content_variants[tone_indicator]
    # Aplicar variante de arquetipo si existe
    elif archetype and fragment.content_variants:
        primary = archetype.primary_archetype.lower() if archetype.primary_archetype else "explorer"
        if primary in fragment.content_variants:
            content = fragment.content_variants[primary]

    # Añadir título si existe
    title = f"<b>{fragment.title}</b>\n\n" if fragment.title else ""

    # Añadir nivel narrativo si es nivel 4+ (VIP)
    level_indicator = ""
    if fragment.narrative_level >= 4:
        level_indicator = f"🔒 <b>Nivel VIP {fragment.narrative_level}</b>\n\n"

    # Combinar todo
    message = f"{level_indicator}{title}{header}\n\n{content}"

    return message


def format_choice_feedback(
    choice: Any,  # StoryChoice
    relationship_score: Optional[int] = None
) -> str:
    """
    Genera feedback inmediato tras una elección del usuario.

    Args:
        choice: La elección que hizo el usuario
        relationship_score: Score de relación con personaje (opcional)

    Returns:
        String con feedback visual

    Example:
        >>> choice = StoryChoice(choice_text="Acepto el desafío")
        >>> format_choice_feedback(choice)
        '✨ <b>Elección registrada</b>\\n\\n➜ Acepto el desafío\\n\\n🎯 Nueva información descubierta'
    """
    parts = ["✨ <b>Elección registrada</b>\n"]
    parts.append(f"\n➜ {choice.choice_text}")

    # Añadir consecuencias inmediatas si existen
    if choice.consequences:
        cons = choice.consequences

        # Flags
        if cons.get("flags_set"):
            parts.append("\n\n🎯 Nueva información descubierta")

        # Cambios de relación
        rel_changes = cons.get("relationship_change", {})
        if rel_changes:
            for char, change in rel_changes.items():
                if change > 0:
                    parts.append(f"\n❤️ Mejoró tu relación con {char}")

    return "\n".join(parts)


def format_rewards_summary(
    besitos: int = 0,
    xp: int = 0,
    badges: Optional[List[str]] = None,
    level_complete: bool = False,
    level_number: int = 0
) -> str:
    """
    Genera resumen visual de recompensas ganadas.

    Args:
        besitos: Cantidad de besitos ganados
        xp: Cantidad de XP ganada
        badges: Lista de badges desbloqueados
        level_complete: Si completó un nivel
        level_number: Número del nivel completado

    Returns:
        String con resumen de recompensas

    Example:
        >>> format_rewards_summary(besitos=25, xp=50, badges=["Explorer Iniciado"])
        '\\n\\n💰 **Recompensas**\\n\\n🪙 25 besitos\\n⭐ 50 XP\\n🏅 Explorer Iniciado'
    """
    parts = ["\n\n💰 <b>Recompensas</b>\n"]

    if besitos > 0:
        parts.append(f"🪙 {besitos} besitos")

    if xp > 0:
        parts.append(f"⭐ {xp} XP")

    if badges:
        for badge in badges:
            parts.append(f"🏅 {badge}")

    if level_complete:
        parts.append(f"\n🎖️ Nivel {level_number} completado")

    return "\n".join(parts)


def format_suspense_pause(duration_seconds: int = 2) -> str:
    """
    Genera mensaje de pausa dramática para suspenso.

    Args:
        duration_seconds: Duración de la pausa

    Returns:
        String con indicador de carga dramática

    Example:
        >>> format_suspense_pause(3)
        '···\\n\\n<i>Cargando下一个fragmento...</i>\\n\\n⏳ 3 segundos'
    """
    dots = "···"  # Pausa dramática
    return (
        f"{dots}\n\n"
        f"<i>Algo está a punto de cambiar...</i>\n\n"
        f"⏳ {duration_seconds} segundos"
    )


def format_delayed_consequence(
    past_choice_id: str,
    past_choice_text: str,
    consequence: str
) -> str:
    """
    Genera mensaje de consecuencia retardada activada.

    Args:
        past_choice_id: ID de la elección pasada
        past_choice_text: Texto de la elección pasada
        consequence: Consecuencia que se activa

    Returns:
        String con notificación de consecuencia retardada

    Example:
        >>> format_delayed_consequence("L1_INTRO_A", "Acepto el desafío", "Diana se acuerda")
        '\\n\\n⚡ **Flashback**\\n\\n📖 Recuerdas tu primera elección...\\n\\n"Acepto el desafío"\\n\\nEsa decisión ha echo eco. Diana se acuerda.'
    """
    return (
        "\n\n⚡ <b>Flashback</b>\n\n"
        "📖 Recuerdas una elección pasada...\n\n"
        f"<i>{past_choice_text}</i>\n\n"
        f"Esa decisión ha hecho eco.\n\n{consequence}"
    )
