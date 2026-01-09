"""
Handlers de narrativa interactiva para usuarios.

Integra el sistema narrativo con aiogram para:
- Procesar decisiones del usuario (callbacks)
- Entregar dialogos personalizados
- Gestionar flujos de escenas
- Trackear tiempo de respuesta

Uso:
    from bot.handlers.user.narrative import narrative_router
    dp.include_router(narrative_router)
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from aiogram import Router, F, Bot
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.narrative import NarrativeService
from bot.database.enums import DecisionType, ArchetypeType

logger = logging.getLogger(__name__)

# Router para handlers narrativos
narrative_router = Router(name="narrative")


class NarrativeStates(StatesGroup):
    """Estados FSM para flujos narrativos."""

    # Usuario esta en una escena esperando respuesta
    in_scene = State()

    # Usuario tiene decision pendiente
    awaiting_choice = State()

    # Usuario en dialogo con personaje
    in_dialogue = State()


# =============================================================================
# HELPER: CREAR SERVICIO NARRATIVO
# =============================================================================

def get_narrative_service(session: AsyncSession) -> NarrativeService:
    """
    Factory para obtener el servicio narrativo.

    En produccion, esto se integraria con el ServiceContainer.

    Args:
        session: Sesion de base de datos

    Returns:
        NarrativeService: Instancia del servicio
    """
    return NarrativeService(session)


# =============================================================================
# HANDLER: PROCESAR DECISIONES NARRATIVAS
# =============================================================================

@narrative_router.callback_query(F.data.startswith("choice:"))
async def handle_narrative_choice(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot
) -> None:
    """
    Procesa una decision narrativa del usuario.

    Callback data format: choice:{scene_id}:{choice_key}

    Flujo:
    1. Extraer datos del callback
    2. Calcular tiempo de respuesta
    3. Registrar decision en BD
    4. Aplicar consecuencias
    5. Obtener siguiente dialogo
    6. Enviar respuesta

    Args:
        callback: CallbackQuery de Telegram
        state: Contexto FSM
        session: Sesion de BD (inyectada por middleware)
        bot: Bot de Telegram
    """
    user_id = callback.from_user.id

    # 1. Extraer datos del callback
    # Format: choice:{scene_id}:{choice_key}
    parts = callback.data.split(":")
    if len(parts) < 3:
        await callback.answer("Error: formato de decision invalido")
        logger.error(f"Formato de callback invalido: {callback.data}")
        return

    scene_id = parts[1]
    choice_key = parts[2]

    logger.debug(
        f"Procesando decision: user={user_id}, "
        f"scene={scene_id}, choice={choice_key}"
    )

    # 2. Calcular tiempo de respuesta
    fsm_data = await state.get_data()
    presented_at = fsm_data.get("choice_presented_at")

    if presented_at:
        presented_dt = datetime.fromisoformat(presented_at)
        response_time = int((datetime.utcnow() - presented_dt).total_seconds())
    else:
        response_time = 0
        logger.warning(f"No hay presented_at para decision: {callback.data}")

    # 3. Registrar decision
    service = get_narrative_service(session)

    # Obtener consecuencias de la decision (en produccion, de la BD de contenido)
    consequences = await _get_choice_consequences(scene_id, choice_key)

    decision = await service.record_decision(
        user_id=user_id,
        scene_id=scene_id,
        decision_type=DecisionType.DIALOGUE,
        key=choice_key,
        value=callback.data,
        response_time=response_time,
        immediate_consequences=consequences.get("immediate", {}),
        delayed_consequences=consequences.get("delayed", {})
    )

    # 4. Analizar patrones periodicamente
    user_state = await service.get_or_create_state(user_id)
    if user_state.total_decisions % 5 == 0:
        # Analizar cada 5 decisiones
        await service.analyze_patterns(user_id)
        await service.detect_archetype(user_id)

    # 5. Obtener siguiente dialogo
    next_trigger = consequences.get("next_trigger", f"{scene_id}_after_{choice_key}")
    next_dialogue = await service.get_next_dialogue(user_id, next_trigger)

    # 6. Enviar respuesta
    await callback.answer()  # Quitar loading del boton

    if next_dialogue:
        await _send_dialogue(callback.message, next_dialogue, state)
    else:
        # Enviar respuesta por defecto o continuar escena
        await _send_choice_feedback(callback.message, choice_key, consequences)

    await session.commit()


@narrative_router.callback_query(F.data.startswith("react:"))
async def handle_narrative_reaction(
    callback: CallbackQuery,
    session: AsyncSession
) -> None:
    """
    Procesa una reaccion del usuario a contenido narrativo.

    Callback data format: react:{content_id}:{reaction_emoji}

    Las reacciones son mas simples que las decisiones:
    - No tienen consecuencias directas
    - Afectan arquetipos y patrones
    - Pueden desbloquear contenido especial

    Args:
        callback: CallbackQuery de Telegram
        session: Sesion de BD
    """
    user_id = callback.from_user.id

    # Extraer datos
    parts = callback.data.split(":")
    if len(parts) < 3:
        await callback.answer("Error: formato de reaccion invalido")
        return

    content_id = parts[1]
    reaction = parts[2]

    service = get_narrative_service(session)

    # Registrar como decision tipo REACTION
    await service.record_decision(
        user_id=user_id,
        scene_id=content_id,
        decision_type=DecisionType.REACTION,
        key=reaction,
        response_time=0  # Reacciones no tienen timing significativo
    )

    # Feedback al usuario
    await callback.answer(f"Reaccion registrada: {reaction}")

    await session.commit()


# =============================================================================
# HANDLER: INICIAR ESCENA
# =============================================================================

@narrative_router.callback_query(F.data.startswith("scene:"))
async def handle_start_scene(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession
) -> None:
    """
    Inicia una escena narrativa.

    Callback data format: scene:{scene_id}

    Flujo:
    1. Verificar condiciones de acceso
    2. Actualizar estado del usuario
    3. Enviar primer dialogo de la escena
    4. Configurar FSM

    Args:
        callback: CallbackQuery de Telegram
        state: Contexto FSM
        session: Sesion de BD
    """
    user_id = callback.from_user.id

    # Extraer scene_id
    parts = callback.data.split(":")
    if len(parts) < 2:
        await callback.answer("Error: escena invalida")
        return

    scene_id = parts[1]

    service = get_narrative_service(session)

    # Verificar si puede acceder
    can_access = await service.check_unlock_conditions(user_id, scene_id)
    if not can_access:
        await callback.answer(
            "Aun no puedes acceder a esta escena",
            show_alert=True
        )
        return

    # Actualizar estado
    await service.set_current_scene(user_id, scene_id)

    # Configurar FSM
    await state.set_state(NarrativeStates.in_scene)
    await state.update_data(
        current_scene=scene_id,
        scene_started_at=datetime.utcnow().isoformat()
    )

    # Obtener primer dialogo
    dialogue = await service.get_next_dialogue(user_id, f"{scene_id}_start")

    await callback.answer()

    if dialogue:
        await _send_dialogue(callback.message, dialogue, state)
    else:
        # Escena no tiene dialogos configurados
        await callback.message.edit_text(
            f"Escena: {scene_id}\n\n"
            "[Contenido pendiente de configuracion]"
        )

    await session.commit()


# =============================================================================
# HANDLER: MENSAJE DE TEXTO EN DIALOGO
# =============================================================================

@narrative_router.message(NarrativeStates.in_dialogue)
async def handle_dialogue_text_input(
    message: Message,
    state: FSMContext,
    session: AsyncSession
) -> None:
    """
    Procesa entrada de texto durante un dialogo.

    Algunos dialogos permiten respuestas de texto libre en lugar
    de opciones predefinidas.

    Args:
        message: Mensaje de texto del usuario
        state: Contexto FSM
        session: Sesion de BD
    """
    user_id = message.from_user.id
    text = message.text

    fsm_data = await state.get_data()
    scene_id = fsm_data.get("current_scene", "unknown")
    dialogue_id = fsm_data.get("current_dialogue", "unknown")

    service = get_narrative_service(session)

    # Registrar como decision tipo DIALOGUE con valor de texto
    await service.record_decision(
        user_id=user_id,
        scene_id=scene_id,
        decision_type=DecisionType.DIALOGUE,
        key=f"{dialogue_id}_text",
        value=text[:500],  # Limitar longitud
        response_time=0
    )

    # Agregar como memoria del personaje
    character = fsm_data.get("current_character", "diana")
    await service.add_character_memory(
        user_id=user_id,
        character=character,
        memory_type="user_said",
        content=text[:200],
        context={"scene": scene_id, "dialogue": dialogue_id}
    )

    # Obtener respuesta del personaje
    next_dialogue = await service.get_next_dialogue(
        user_id,
        f"{dialogue_id}_response"
    )

    if next_dialogue:
        await _send_dialogue(message, next_dialogue, state)
    else:
        # Respuesta generica
        await message.answer(
            "Tu respuesta ha sido registrada.\n\n"
            "[El personaje procesara tu mensaje...]"
        )

    await session.commit()


# =============================================================================
# HELPERS: ENVIO DE DIALOGOS
# =============================================================================

async def _send_dialogue(
    message: Message,
    dialogue: Dict[str, Any],
    state: FSMContext
) -> Message:
    """
    Envia un dialogo al usuario.

    Formatea el mensaje segun el tipo de dialogo y crea
    los botones de opciones si es necesario.

    Args:
        message: Mensaje de referencia (para edit o reply)
        dialogue: Datos del dialogo
        state: Contexto FSM

    Returns:
        Message: Mensaje enviado
    """
    text = dialogue.get("text", "[Sin contenido]")
    character = dialogue.get("character", "narrator")
    options = dialogue.get("options", [])
    media = dialogue.get("media")

    # Formatear texto con nombre del personaje
    if character != "narrator":
        formatted_text = f"<b>{character.title()}:</b>\n\n{text}"
    else:
        formatted_text = text

    # Crear keyboard si hay opciones
    keyboard = None
    if options:
        buttons = []
        for opt in options:
            callback_data = f"choice:{dialogue.get('scene_id', 'unknown')}:{opt['key']}"
            buttons.append([
                InlineKeyboardButton(
                    text=opt.get("text", opt["key"]),
                    callback_data=callback_data
                )
            ])
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        # Guardar timestamp para calcular tiempo de respuesta
        await state.update_data(
            choice_presented_at=datetime.utcnow().isoformat(),
            current_dialogue=dialogue.get("id")
        )

    # Enviar mensaje
    if media and media.get("type") == "photo":
        # Mensaje con foto
        sent = await message.answer_photo(
            photo=media["file_id"],
            caption=formatted_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        # Mensaje de texto
        try:
            # Intentar editar si es callback
            sent = await message.edit_text(
                formatted_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        except Exception:
            # Si no se puede editar, enviar nuevo
            sent = await message.answer(
                formatted_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )

    return sent


async def _send_choice_feedback(
    message: Message,
    choice_key: str,
    consequences: Dict[str, Any]
) -> None:
    """
    Envia feedback despues de una decision.

    Muestra al usuario el efecto inmediato de su decision
    sin revelar mecanicas internas.
    """
    # Mapear consecuencias a feedback amigable
    feedback_parts = []

    immediate = consequences.get("immediate", {})

    if "diana_trust" in immediate:
        delta = immediate["diana_trust"]
        if delta > 0:
            feedback_parts.append("Diana parece apreciar tu respuesta.")
        elif delta < 0:
            feedback_parts.append("Diana parece distante.")

    if "lucien_respect" in immediate:
        delta = immediate["lucien_respect"]
        if delta > 0:
            feedback_parts.append("Lucien asiente con aprobacion.")
        elif delta < 0:
            feedback_parts.append("Lucien te mira con curiosidad.")

    if not feedback_parts:
        feedback_parts.append("Tu eleccion ha sido registrada.")

    feedback_text = "\n".join(feedback_parts)

    try:
        await message.edit_text(
            f"<i>{feedback_text}</i>",
            parse_mode="HTML"
        )
    except Exception:
        await message.answer(
            f"<i>{feedback_text}</i>",
            parse_mode="HTML"
        )


async def _get_choice_consequences(
    scene_id: str,
    choice_key: str
) -> Dict[str, Any]:
    """
    Obtiene las consecuencias de una eleccion.

    En produccion, esto consultaria la BD de contenido narrativo.
    Por ahora retorna estructura vacia.

    Args:
        scene_id: ID de la escena
        choice_key: Clave de la eleccion

    Returns:
        Dict con consecuencias inmediatas, diferidas y next_trigger
    """
    # Placeholder - en implementacion real seria query a BD
    # Mapeo basico por convencion de nombres
    consequences: Dict[str, Any] = {
        "immediate": {},
        "delayed": {},
        "next_trigger": f"{scene_id}_after_{choice_key}"
    }

    # Inferir consecuencias por nombre de choice
    choice_lower = choice_key.lower()

    if "honest" in choice_lower or "truth" in choice_lower:
        consequences["immediate"]["diana_trust"] = 5
        consequences["immediate"]["archetype_direct"] = 10

    elif "curious" in choice_lower or "why" in choice_lower:
        consequences["immediate"]["archetype_introspective"] = 10

    elif "feel" in choice_lower or "emotion" in choice_lower:
        consequences["immediate"]["archetype_romantic"] = 10
        consequences["immediate"]["diana_trust"] = 3

    elif "logic" in choice_lower or "reason" in choice_lower:
        consequences["immediate"]["archetype_analytical"] = 10
        consequences["immediate"]["lucien_respect"] = 3

    return consequences


# =============================================================================
# FUNCIONES UTILITARIAS PARA HANDLERS EXTERNOS
# =============================================================================

async def trigger_narrative_event(
    user_id: int,
    trigger: str,
    session: AsyncSession,
    bot: Bot
) -> bool:
    """
    Dispara un evento narrativo desde otros handlers.

    Permite que cualquier handler del bot dispare contenido
    narrativo cuando sea apropiado.

    Args:
        user_id: ID del usuario
        trigger: Trigger del evento
        session: Sesion de BD
        bot: Bot de Telegram

    Returns:
        bool: True si se envio contenido, False si no habia

    Example:
        # En handler de bienvenida
        await trigger_narrative_event(
            user_id=message.from_user.id,
            trigger="first_vip_login",
            session=session,
            bot=message.bot
        )
    """
    service = get_narrative_service(session)
    dialogue = await service.get_next_dialogue(user_id, trigger)

    if dialogue is None:
        return False

    text = dialogue.get("text", "")
    character = dialogue.get("character", "narrator")

    if character != "narrator":
        text = f"<b>{character.title()}:</b>\n\n{text}"

    try:
        await bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode="HTML"
        )
        return True
    except Exception as e:
        logger.error(f"Error enviando evento narrativo: {e}")
        return False


async def get_user_narrative_summary(
    user_id: int,
    session: AsyncSession
) -> Dict[str, Any]:
    """
    Obtiene resumen del estado narrativo del usuario.

    Util para dashboards y debugging.

    Args:
        user_id: ID del usuario
        session: Sesion de BD

    Returns:
        Dict con resumen del estado
    """
    service = get_narrative_service(session)
    state = await service.get_or_create_state(user_id)

    return {
        "level": state.current_level,
        "scene": state.current_scene_id,
        "diana_trust": state.diana_trust,
        "diana_state": state.diana_state.value,
        "lucien_respect": state.lucien_respect,
        "lucien_state": state.lucien_state.value,
        "primary_archetype": (
            state.primary_archetype.value if state.primary_archetype else None
        ),
        "secondary_archetype": (
            state.secondary_archetype.value if state.secondary_archetype else None
        ),
        "total_decisions": state.total_decisions,
        "flags": state.narrative_flags
    }
