"""
Narrative Delivery Service - Entrega de contenido narrativo.

Conecta los modelos de escenas (scene_models) con el motor narrativo
para entregar contenido personalizado al usuario.

Responsabilidades:
- Obtener escenas y diálogos de la BD
- Personalizar contenido según arquetipo/relación
- Preparar opciones de respuesta con callbacks
- Trackear progresión entre escenas
"""
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.database.scene_models import (
    NarrativeChapter,
    NarrativeScene,
    SceneDialogue,
    DialogueOption
)
from bot.database.narrative_models import UserNarrativeState
from bot.database.enums import ArchetypeType, RelationshipState

logger = logging.getLogger(__name__)


class NarrativeDeliveryService:
    """
    Servicio de entrega de contenido narrativo.

    Lee escenas y diálogos de la BD y los prepara para ser
    enviados al usuario con personalización.

    Uso:
        delivery = NarrativeDeliveryService(session)
        scene = await delivery.get_scene("L1_S1_llegada")
        dialogues = await delivery.get_scene_dialogues(
            scene_id="L1_S1_llegada",
            user_state=state
        )
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el servicio de delivery.

        Args:
            session: Sesión de base de datos SQLAlchemy async
        """
        self._session = session
        logger.debug("NarrativeDeliveryService inicializado")

    # =========================================================================
    # CHAPTERS
    # =========================================================================

    async def get_chapter(self, chapter_id: str) -> Optional[NarrativeChapter]:
        """
        Obtiene un capítulo por su ID.

        Args:
            chapter_id: ID del capítulo

        Returns:
            NarrativeChapter o None si no existe
        """
        result = await self._session.execute(
            select(NarrativeChapter)
            .where(NarrativeChapter.chapter_id == chapter_id)
            .options(selectinload(NarrativeChapter.scenes))
        )
        return result.scalar_one_or_none()

    async def get_chapters_for_level(self, level: int) -> List[NarrativeChapter]:
        """
        Obtiene capítulos disponibles para un nivel.

        Args:
            level: Nivel narrativo (1-6)

        Returns:
            Lista de capítulos
        """
        result = await self._session.execute(
            select(NarrativeChapter)
            .where(
                NarrativeChapter.required_level <= level,
                NarrativeChapter.is_active == True
            )
            .order_by(NarrativeChapter.sequence_order)
        )
        return list(result.scalars().all())

    # =========================================================================
    # SCENES
    # =========================================================================

    async def get_scene(self, scene_id: str) -> Optional[NarrativeScene]:
        """
        Obtiene una escena por su ID.

        Args:
            scene_id: ID de la escena

        Returns:
            NarrativeScene o None si no existe
        """
        result = await self._session.execute(
            select(NarrativeScene)
            .where(NarrativeScene.scene_id == scene_id)
            .options(selectinload(NarrativeScene.dialogues))
        )
        return result.scalar_one_or_none()

    async def get_scene_by_trigger(self, trigger: str) -> Optional[NarrativeScene]:
        """
        Obtiene una escena por su trigger.

        Args:
            trigger: Trigger de activación

        Returns:
            NarrativeScene o None
        """
        result = await self._session.execute(
            select(NarrativeScene)
            .where(
                NarrativeScene.trigger_event == trigger,
                NarrativeScene.is_active == True
            )
        )
        return result.scalar_one_or_none()

    async def get_first_scene_for_chapter(
        self,
        chapter_id: str
    ) -> Optional[NarrativeScene]:
        """
        Obtiene la primera escena de un capítulo.

        Args:
            chapter_id: ID del capítulo

        Returns:
            Primera escena o None
        """
        result = await self._session.execute(
            select(NarrativeScene)
            .where(
                NarrativeScene.chapter_id == chapter_id,
                NarrativeScene.is_active == True
            )
            .order_by(NarrativeScene.sequence_order)
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_next_scene(
        self,
        current_scene_id: str,
        user_state: UserNarrativeState,
        decision_key: Optional[str] = None
    ) -> Optional[NarrativeScene]:
        """
        Obtiene la siguiente escena basándose en el estado del usuario.

        Evalúa las reglas de branching para determinar la siguiente escena.

        Args:
            current_scene_id: ID de la escena actual
            user_state: Estado narrativo del usuario
            decision_key: Clave de la última decisión (opcional)

        Returns:
            Siguiente escena o None
        """
        current_scene = await self.get_scene(current_scene_id)
        if current_scene is None:
            return None

        branching = current_scene.branching_rules or {}
        next_scene_id = current_scene.next_scene_default

        # Evaluar condiciones de branching
        conditions = branching.get("conditions", [])
        for cond in conditions:
            if await self._evaluate_branch_condition(cond, user_state, decision_key):
                next_scene_id = cond.get("goto")
                break

        if next_scene_id is None:
            return None

        return await self.get_scene(next_scene_id)

    # =========================================================================
    # DIALOGUES
    # =========================================================================

    async def get_scene_dialogues(
        self,
        scene_id: str,
        user_state: Optional[UserNarrativeState] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene diálogos de una escena personalizados para el usuario.

        Args:
            scene_id: ID de la escena
            user_state: Estado del usuario para personalización

        Returns:
            Lista de diálogos formateados
        """
        result = await self._session.execute(
            select(SceneDialogue)
            .where(
                SceneDialogue.scene_id == scene_id,
                SceneDialogue.is_active == True
            )
            .options(selectinload(SceneDialogue.options))
            .order_by(SceneDialogue.sequence_order)
        )
        dialogues = result.scalars().all()

        formatted_dialogues = []
        for dialogue in dialogues:
            formatted = await self._format_dialogue(dialogue, user_state)
            formatted_dialogues.append(formatted)

        return formatted_dialogues

    async def get_dialogue(self, dialogue_id: str) -> Optional[SceneDialogue]:
        """
        Obtiene un diálogo por su ID.

        Args:
            dialogue_id: ID del diálogo

        Returns:
            SceneDialogue o None
        """
        result = await self._session.execute(
            select(SceneDialogue)
            .where(SceneDialogue.dialogue_id == dialogue_id)
            .options(selectinload(SceneDialogue.options))
        )
        return result.scalar_one_or_none()

    async def get_formatted_dialogue(
        self,
        dialogue_id: str,
        user_state: Optional[UserNarrativeState] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene un diálogo formateado y personalizado.

        Args:
            dialogue_id: ID del diálogo
            user_state: Estado del usuario

        Returns:
            Dict con diálogo formateado o None
        """
        dialogue = await self.get_dialogue(dialogue_id)
        if dialogue is None:
            return None

        return await self._format_dialogue(dialogue, user_state)

    # =========================================================================
    # OPTIONS
    # =========================================================================

    async def get_option(self, option_id: str) -> Optional[DialogueOption]:
        """
        Obtiene una opción de diálogo por su ID.

        Args:
            option_id: ID de la opción

        Returns:
            DialogueOption o None
        """
        result = await self._session.execute(
            select(DialogueOption)
            .where(DialogueOption.option_id == option_id)
        )
        return result.scalar_one_or_none()

    async def get_option_consequences(
        self,
        option_id: str
    ) -> Dict[str, Any]:
        """
        Obtiene las consecuencias de una opción.

        Args:
            option_id: ID de la opción

        Returns:
            Dict con immediate y delayed effects
        """
        option = await self.get_option(option_id)
        if option is None:
            return {"immediate": {}, "delayed": {}}

        return {
            "immediate": option.immediate_effects or {},
            "delayed": option.delayed_effects or {},
            "next_scene_id": option.next_scene_id,
            "next_dialogue_id": option.next_dialogue_id,
            "creates_memory": option.creates_memory
        }

    # =========================================================================
    # NARRATIVE FLOW
    # =========================================================================

    async def start_narrative(
        self,
        user_id: int
    ) -> Tuple[Optional[NarrativeScene], Optional[Dict[str, Any]]]:
        """
        Inicia la narrativa para un usuario nuevo.

        Retorna la primera escena (L1_S1_llegada) y su primer diálogo.

        Args:
            user_id: ID del usuario

        Returns:
            Tuple de (escena, primer_dialogo) o (None, None)
        """
        # Obtener primera escena del nivel 1
        first_scene = await self.get_scene("L1_S1_llegada")
        if first_scene is None:
            logger.warning("No se encontró la escena inicial L1_S1_llegada")
            return None, None

        # Obtener diálogos de la escena
        dialogues = await self.get_scene_dialogues(first_scene.scene_id, None)
        first_dialogue = dialogues[0] if dialogues else None

        return first_scene, first_dialogue

    async def continue_narrative(
        self,
        user_state: UserNarrativeState,
        decision_key: Optional[str] = None
    ) -> Tuple[Optional[NarrativeScene], Optional[Dict[str, Any]]]:
        """
        Continúa la narrativa desde el estado actual.

        Args:
            user_state: Estado narrativo del usuario
            decision_key: Última decisión tomada

        Returns:
            Tuple de (siguiente_escena, primer_dialogo)
        """
        current_scene_id = user_state.current_scene_id

        if current_scene_id is None:
            # Usuario no tiene escena, iniciar desde el principio
            return await self.start_narrative(user_state.user_id)

        # Obtener siguiente escena
        next_scene = await self.get_next_scene(
            current_scene_id,
            user_state,
            decision_key
        )

        if next_scene is None:
            return None, None

        # Obtener diálogos
        dialogues = await self.get_scene_dialogues(
            next_scene.scene_id,
            user_state
        )
        first_dialogue = dialogues[0] if dialogues else None

        return next_scene, first_dialogue

    async def get_pending_dialogue_index(
        self,
        scene_id: str,
        user_state: UserNarrativeState
    ) -> int:
        """
        Obtiene el índice del siguiente diálogo pendiente.

        Basado en el progreso del usuario en la escena.

        Args:
            scene_id: ID de la escena
            user_state: Estado del usuario

        Returns:
            Índice del diálogo (0 si es el primero)
        """
        # Por ahora simple: buscar en flags narrativos
        flags = user_state.narrative_flags or {}
        dialogue_progress = flags.get("dialogue_progress", {})
        return dialogue_progress.get(scene_id, 0)

    # =========================================================================
    # FORMATTERS
    # =========================================================================

    async def _format_dialogue(
        self,
        dialogue: SceneDialogue,
        user_state: Optional[UserNarrativeState]
    ) -> Dict[str, Any]:
        """
        Formatea un diálogo para envío con personalización.

        Args:
            dialogue: Modelo de diálogo
            user_state: Estado del usuario

        Returns:
            Dict formateado para envío
        """
        # Determinar arquetipo y estado de relación
        archetype = None
        relationship_state = None

        if user_state:
            archetype = user_state.primary_archetype
            if dialogue.character == "diana":
                relationship_state = user_state.diana_state
            elif dialogue.character == "lucien":
                relationship_state = user_state.lucien_state

        # Obtener texto personalizado
        text = dialogue.get_text_for_user(archetype, relationship_state)

        # Formatear opciones
        options = []
        for opt in (dialogue.options or []):
            # Verificar visibilidad
            if opt.visibility_conditions and user_state:
                if not await self._evaluate_visibility(
                    opt.visibility_conditions,
                    user_state
                ):
                    continue

            option_text = opt.get_text_for_archetype(archetype)
            options.append({
                "id": opt.option_id,
                "key": opt.option_id,
                "text": option_text,
                "archetype": opt.associated_archetype.value if opt.associated_archetype else None
            })

        return {
            "id": dialogue.dialogue_id,
            "scene_id": dialogue.scene_id,
            "character": dialogue.character,
            "text": text,
            "delivery_style": dialogue.delivery_style,
            "typing_delay": dialogue.typing_delay,
            "media": dialogue.media,
            "options": options,
            "requires_response": dialogue.requires_response,
            "creates_memory": dialogue.creates_memory
        }

    async def _evaluate_branch_condition(
        self,
        condition: Dict[str, Any],
        user_state: UserNarrativeState,
        decision_key: Optional[str]
    ) -> bool:
        """
        Evalúa una condición de branching.

        Args:
            condition: Condición a evaluar
            user_state: Estado del usuario
            decision_key: Última decisión

        Returns:
            True si la condición se cumple
        """
        if_clause = condition.get("if", {})

        # Evaluar por decisión
        if "decision" in if_clause:
            return decision_key == if_clause["decision"]

        # Evaluar por flags
        if "flags" in if_clause:
            flags_cond = if_clause["flags"]
            user_flags = user_state.narrative_flags or {}

            if "has" in flags_cond:
                flag_name = flags_cond["has"]
                # Buscar en todos los tipos de flags
                for flag_list in user_flags.values():
                    if isinstance(flag_list, list) and flag_name in flag_list:
                        return True
                return False

        # Evaluar por arquetipo
        if "archetype" in if_clause:
            arch_cond = if_clause["archetype"]
            if isinstance(arch_cond, dict) and "in" in arch_cond:
                user_arch = user_state.primary_archetype
                if user_arch:
                    return user_arch.value in arch_cond["in"]

        # Evaluar por nivel de confianza/respeto
        if "diana_trust" in if_clause:
            return self._evaluate_numeric_condition(
                user_state.diana_trust,
                if_clause["diana_trust"]
            )

        if "lucien_respect" in if_clause:
            return self._evaluate_numeric_condition(
                user_state.lucien_respect,
                if_clause["lucien_respect"]
            )

        return False

    async def _evaluate_visibility(
        self,
        conditions: Dict[str, Any],
        user_state: UserNarrativeState
    ) -> bool:
        """
        Evalúa condiciones de visibilidad de una opción.

        Args:
            conditions: Condiciones de visibilidad
            user_state: Estado del usuario

        Returns:
            True si la opción debe mostrarse
        """
        for key, value in conditions.items():
            if key == "diana_trust":
                if not self._evaluate_numeric_condition(
                    user_state.diana_trust, value
                ):
                    return False
            elif key == "lucien_respect":
                if not self._evaluate_numeric_condition(
                    user_state.lucien_respect, value
                ):
                    return False
            elif key == "pattern":
                # Verificar patrón
                patterns = user_state.patterns or []
                active_patterns = [
                    p.pattern_type.value for p in patterns
                    if p.is_active
                ]
                if "has" in value:
                    if value["has"] not in active_patterns:
                        return False

        return True

    def _evaluate_numeric_condition(
        self,
        value: int,
        condition: Dict[str, int]
    ) -> bool:
        """
        Evalúa una condición numérica.

        Args:
            value: Valor actual
            condition: Dict con operador y valor

        Returns:
            True si se cumple
        """
        for op, target in condition.items():
            if op == ">=" and not value >= target:
                return False
            elif op == ">" and not value > target:
                return False
            elif op == "<=" and not value <= target:
                return False
            elif op == "<" and not value < target:
                return False
            elif op == "==" and not value == target:
                return False

        return True
