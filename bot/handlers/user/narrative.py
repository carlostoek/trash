"""
Narrative User Handlers - Sistema interactivo de historia.

Este módulo implementa los handlers para la narrativa interactiva del bot.
Los usuarios pueden leer fragmentos de historia, tomar decisiones, y ver
cómo sus elecciones afectan el desarrollo de la trama.

Features:
- Sistema de historia ramificada con elecciones múltiples
- Detección de arquetipo de usuario basado en comportamiento
- Relaciones con personajes (Diana, Lucien)
- Contenido VIP bloqueado para niveles 4-6
- Función de releer para exploradores/analíticos
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import (
    StoryFragment,
    StoryChoice,
    UserNarrativeProgress,
    ArchetypeProfile,
    CharacterRelationship
)
from bot.middlewares import DatabaseMiddleware
from bot.services.narrative import StoryEngine
from bot.states.narrative import NarrativeUserStates
from bot.utils.narrative_formatters import (
    format_narrative_message,
    format_unlock_message,
    format_consequences_message,
    format_story_status,
    format_multimedia_fragment,
    format_progress_indicator,
    format_dynamic_voice,
    format_milestone_celebration,
    format_choice_feedback,
    format_rewards_summary
)
from bot.utils.keyboards import create_narrative_keyboard

logger = logging.getLogger(__name__)

# Router para handlers narrativos
narrative_router = Router(name="narrative")

# Aplicar middleware de database
narrative_router.message.middleware(DatabaseMiddleware())
narrative_router.callback_query.middleware(DatabaseMiddleware())


# ==============================================================================
# COMMAND HANDLERS
# ==============================================================================

@narrative_router.message(Command("story"))
async def cmd_story(message: Message, session: AsyncSession):
    """
    Handler del comando /story - Inicia o continúa la historia del usuario.

    Comportamiento:
    - Si es la primera vez → Muestra fragmento inicial del Nivel 1
    - Si ya tiene progreso → Muestra fragmento actual
    - Si el fragmento está bloqueado → Muestra mensaje de desbloqueo
    - Si es VIP required → Muestra mensaje de suscripción

    Args:
        message: Mensaje del usuario
        session: Sesión de BD (inyectada por middleware)
    """
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Viajero"

    logger.info(f"📖 Usuario {user_id} ({user_name}) inició historia")

    try:
        # Crear motor de historia
        engine = StoryEngine(session, message.bot)

        # Obtener estado actual de la historia
        story_state = await engine.get_current_story_state(user_id)

        # Verificar si hay error
        if "error" in story_state:
            await message.answer(
                "❌ <b>Error</b>\n\n"
                "No hay contenido narrativo disponible en este momento.\n"
                "Por favor intenta más tarde.",
                parse_mode="HTML"
            )
            return

        # Verificar si puede continuar
        if not story_state.get("can_continue", False):
            unlock_message = story_state.get("unlock_message", "")
            await message.answer(
                unlock_message,
                parse_mode="HTML"
            )
            return

        # Extraer información del estado
        current_fragment: StoryFragment = story_state["current_fragment"]
        available_choices: list[StoryChoice] = story_state["available_choices"]
        archetype: ArchetypeProfile = story_state["archetype"]
        user_progress: UserNarrativeProgress = story_state["user_progress"]
        relationships: Dict[str, CharacterRelationship] = story_state.get("relationships", {})

        # FASE 2: Obtener relación con Diana para voz dinámica
        relationship_diana = relationships.get("DIANA")

        # Enviar fragmento actual
        await _send_fragment_to_user(
            message=message,
            fragment=current_fragment,
            choices=available_choices,
            archetype=archetype,
            user_progress=user_progress,
            relationship_diana=relationship_diana
        )

        # Entrar en estado de lectura (si FSM está disponible)
        try:
            from aiogram.fsm.context import FSMContext
            state = FSMContext.get_current(message)
            if state:
                await state.set_state(NarrativeUserStates.reading_fragment)
                # Guardar timestamp para tracking de tiempo de elección
                await state.update_data(fragment_start_time=datetime.now(timezone.utc))
        except Exception as fsm_error:
            logger.debug(f"⚠️ FSM no disponible: {fsm_error}")

    except Exception as e:
        logger.error(f"❌ Error en cmd_story para usuario {user_id}: {e}", exc_info=True)
        await message.answer(
            "❌ <b>Error</b>\n\n"
            "Ocurrió un error al cargar la historia. "
            "Por favor intenta nuevamente.",
            parse_mode="HTML"
        )


# ==============================================================================
# CALLBACK HANDLERS
# ==============================================================================

@narrative_router.callback_query(lambda c: c.data.startswith("narrative:choice:"))
async def callback_narrative_choice(callback: CallbackQuery, session: AsyncSession):
    """
    Handler para selección de opción narrativa.

    Procesa:
    1. Calcula tiempo que tomó el usuario en elegir (para arquetipo)
    2. Aplica consecuencias de la elección (flags, arquetipos, relaciones)
    3. Avanza al siguiente fragmento
    4. Muestra consecuencias aplicadas
    5. Envía siguiente fragmento con opciones

    Args:
        callback: CallbackQuery del usuario
        session: Sesión de BD (inyectada por middleware)
    """
    user_id = callback.from_user.id
    choice_id = callback.data.split(":")[-1]  # Extraer choice_id

    logger.info(f"🎯 Usuario {user_id} eligió opción: {choice_id}")

    try:
        # Obtener estado FSM para calcular tiempo de elección (si está disponible)
        choice_time_seconds = 0
        try:
            from aiogram.fsm.context import FSMContext
            state = FSMContext.get_current(callback)

            if state:
                state_data = await state.get_data()
                fragment_start_time = state_data.get("fragment_start_time")

                if fragment_start_time:
                    # Calcular tiempo de elección en segundos
                    time_diff = datetime.now(timezone.utc) - fragment_start_time
                    choice_time_seconds = int(time_diff.total_seconds())
                    logger.debug(f"⏱️ Usuario {user_id} tardó {choice_time_seconds}s en elegir")
        except Exception as fsm_error:
            logger.debug(f"⚠️ FSM no disponible para tracking de tiempo: {fsm_error}")

        # Crear motor de historia
        engine = StoryEngine(session, callback.bot)

        # Procesar elección
        result = await engine.make_choice(
            user_id=user_id,
            choice_id=choice_id,
            choice_time_seconds=choice_time_seconds
        )

        # Verificar si la elección fue exitosa
        if not result.get("success", False):
            await callback.answer(
                f"❌ {result.get('message', 'Opción no válida')}",
                show_alert=True
            )
            return

        # Confirmar la elección
        await callback.answer("✨ Opción registrada")

        # Obtener información del resultado
        next_fragment: StoryFragment = result.get("next_fragment")
        consequences: Dict = result.get("consequences", {})
        next_state: Dict = result.get("next_state", {})

        # Editar mensaje anterior con consecuencias
        if consequences:
            consequences_text = format_consequences_message(consequences)
            if consequences_text:
                try:
                    await callback.message.edit_text(
                        f"{callback.message.text}\n\n{consequences_text}",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.warning(f"⚠️ No se pudo editar mensaje con consecuencias: {e}")

        # Verificar si el siguiente fragmento está bloqueado
        if not next_state.get("can_continue", False):
            unlock_message = next_state.get("unlock_message", "")
            await callback.message.answer(
                unlock_message,
                parse_mode="HTML"
            )
            return

        # Extraer información del siguiente estado
        available_choices: list[StoryChoice] = next_state["available_choices"]
        archetype: ArchetypeProfile = next_state["archetype"]
        user_progress: UserNarrativeProgress = next_state["user_progress"]
        relationships: Dict[str, CharacterRelationship] = next_state.get("relationships", {})

        # FASE 2: Obtener relación con Diana para voz dinámica
        relationship_diana = relationships.get("DIANA")

        # Enviar siguiente fragmento
        await _send_fragment_to_user(
            message=callback.message,
            fragment=next_fragment,
            choices=available_choices,
            archetype=archetype,
            user_progress=user_progress,
            relationship_diana=relationship_diana
        )

        # Actualizar estado FSM (si está disponible)
        try:
            from aiogram.fsm.context import FSMContext
            state = FSMContext.get_current(callback)
            if state:
                await state.set_state(NarrativeUserStates.reading_fragment)
                await state.update_data(fragment_start_time=datetime.now(timezone.utc))
        except Exception as fsm_error:
            logger.debug(f"⚠️ FSM no disponible: {fsm_error}")

    except Exception as e:
        logger.error(f"❌ Error en callback_narrative_choice para usuario {user_id}: {e}", exc_info=True)
        await callback.answer(
            "❌ Error al procesar tu elección",
            show_alert=True
        )


@narrative_router.callback_query(lambda c: c.data == "narrative:reread")
async def callback_narrative_reread(callback: CallbackQuery, session: AsyncSession):
    """
    Handler para releer el fragmento actual.

    Función para usuarios que quieren:
    - Releer para entender mejor (Analytical)
    - Explorar contenido (Explorer)
    - Disfrutar nuevamente

    Registra la acción para detección de arquetipo.

    Args:
        callback: CallbackQuery del usuario
        session: Sesión de BD (inyectada por middleware)
    """
    user_id = callback.from_user.id

    logger.info(f"📖 Usuario {user_id} releyendo fragmento")

    try:
        # Crear motor de historia
        engine = StoryEngine(session, callback.bot)

        # Obtener estado actual
        story_state = await engine.get_current_story_state(user_id)

        if not story_state.get("can_continue", False):
            await callback.answer(
                "🔒 No puedes releer este fragmento",
                show_alert=True
            )
            return

        # Registrar relectura para detección de arquetipo
        await engine.archetype.record_fragment_reread(user_id)

        # Extraer información
        current_fragment: StoryFragment = story_state["current_fragment"]
        available_choices: list[StoryChoice] = story_state["available_choices"]
        archetype: ArchetypeProfile = story_state["archetype"]
        user_progress: UserNarrativeProgress = story_state["user_progress"]
        relationships: Dict[str, CharacterRelationship] = story_state.get("relationships", {})

        # FASE 2: Obtener relación con Diana para voz dinámica
        relationship_diana = relationships.get("DIANA")

        # Responder al callback
        await callback.answer("📖 Fragmento mostrado nuevamente")

        # Enviar fragmento nuevamente (nuevo mensaje)
        await _send_fragment_to_user(
            message=callback.message,
            fragment=current_fragment,
            choices=available_choices,
            archetype=archetype,
            user_progress=user_progress,
            relationship_diana=relationship_diana,
            is_reread=True
        )

    except Exception as e:
        logger.error(f"❌ Error en callback_narrative_reread para usuario {user_id}: {e}", exc_info=True)
        await callback.answer(
            "❌ Error al releer fragmento",
            show_alert=True
        )


@narrative_router.callback_query(lambda c: c.data == "narrative:status")
async def callback_narrative_status(callback: CallbackQuery, session: AsyncSession):
    """
    Handler para ver el estado de progreso narrativo del usuario.

    Muestra:
    - Nivel actual
    - Niveles completados
    - Arquetipo detectado
    - Relaciones con personajes
    - Estadísticas (elecciones, fragmentos vistos)

    Args:
        callback: CallbackQuery del usuario
        session: Sesión de BD (inyectada por middleware)
    """
    user_id = callback.from_user.id

    logger.info(f"📊 Usuario {user_id} consultando estado narrativo")

    try:
        # Crear motor de historia
        engine = StoryEngine(session, callback.bot)

        # Obtener estado actual
        story_state = await engine.get_current_story_state(user_id)

        # Extraer información
        progress: UserNarrativeProgress = story_state["user_progress"]
        archetype: ArchetypeProfile = story_state["archetype"]
        relationships: Dict[str, CharacterRelationship] = story_state["relationships"]

        # Formatear estado
        status_text = format_story_status(progress, archetype, relationships)

        # Responder al callback
        await callback.answer()

        # Editar mensaje actual con estado
        try:
            await callback.message.edit_text(
                status_text,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.warning(f"⚠️ No se pudo editar mensaje: {e}")
            # Si no se puede editar, enviar nuevo mensaje
            await callback.message.answer(
                status_text,
                parse_mode="HTML"
            )

    except Exception as e:
        logger.error(f"❌ Error en callback_narrative_status para usuario {user_id}: {e}", exc_info=True)
        await callback.answer(
            "❌ Error al obtener estado",
            show_alert=True
        )


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

async def _send_fragment_to_user(
    message: Message,
    fragment: StoryFragment,
    choices: list[StoryChoice],
    archetype: Optional[ArchetypeProfile] = None,
    user_progress: Optional[UserNarrativeProgress] = None,
    relationship_diana: Optional[CharacterRelationship] = None,
    is_reread: bool = False
) -> None:
    """
    Envía un fragmento narrativo al usuario con formato y keyboard.

    FASE 2 ENHANCED: Ahora incluye:
    - Indicador de progreso visual incrustado
    - Voz dinámica según relación con Diana
    - Formato mejorado con recompensas visuales

    Args:
        message: Mensaje de Telegram (para responder)
        fragment: StoryFragment a enviar
        choices: Lista de StoryChoice disponibles
        archetype: ArchetypeProfile del usuario (opcional)
        user_progress: UserNarrativeProgress del usuario (opcional)
        relationship_diana: CharacterRelationship con Diana (opcional)
        is_reread: Si es una relectura (para logging)
    """
    # FASE 2: Usar voz dinámica si hay relación disponible
    if relationship_diana and fragment.speaker == "DIANA":
        formatted_message = format_dynamic_voice(
            fragment,
            user_progress or UserNarrativeProgress(),
            relationship_diana,
            archetype
        )
    else:
        formatted_message = format_narrative_message(fragment, archetype)

    # FASE 2: Añadir indicador de progreso si hay progreso disponible
    if user_progress:
        progress_indicator = format_progress_indicator(fragment, user_progress)
        formatted_message += progress_indicator

    # Crear keyboard con opciones
    keyboard = create_narrative_keyboard(
        available_choices=choices,
        current_fragment=fragment,
        can_reread=not fragment.is_starting_fragment
    )

    # Verificar si hay multimedia
    multimedia = format_multimedia_fragment(fragment)

    try:
        if multimedia:
            # Enviar con multimedia (foto o video)
            if multimedia["type"] == "photo":
                await message.answer_photo(
                    photo=multimedia["file_id"],
                    caption=formatted_message,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            elif multimedia["type"] == "video":
                await message.answer_video(
                    video=multimedia["file_id"],
                    caption=formatted_message,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
        else:
            # Enviar solo texto
            await message.answer(
                formatted_message,
                reply_markup=keyboard,
                parse_mode="HTML"
            )

        action = "releyó" if is_reread else "vió"
        logger.debug(f"📖 Usuario {message.from_user.id} {action} fragmento {fragment.fragment_id}")

    except Exception as e:
        logger.error(f"❌ Error enviando fragmento {fragment.fragment_id}: {e}", exc_info=True)

        # Fallback: enviar solo texto si falla multimedia
        try:
            await message.answer(
                formatted_message,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        except Exception as fallback_error:
            logger.error(f"❌ Error en fallback enviando fragmento: {fallback_error}", exc_info=True)
