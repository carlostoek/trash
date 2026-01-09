"""
Narrative Service - Motor de narrativa interactiva.

Responsabilidades:
- Gestionar estado narrativo del usuario (nivel, escena, relaciones)
- Registrar y analizar decisiones del usuario
- Detectar patrones de comportamiento y arquetipos
- Gestionar relaciones con personajes (Diana, Lucien)
- Seleccionar y entregar contenido personalizado
- Aplicar consecuencias narrativas

Arquitectura:
    NarrativeService (orquestador)
        -> ConditionEvaluator (evalua condiciones complejas)
        -> PatternAnalyzer (detecta patrones de comportamiento)
        -> DialogueSelector (selecciona variantes de dialogo)
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.database.enums import (
    NarrativeLevel, DecisionType, PatternType,
    ArchetypeType, ConsequenceType, RelationshipState
)
from bot.database.narrative_models import (
    UserNarrativeState, UserDecision, UserBehaviorPattern,
    NarrativeConsequence, AppliedConsequence, CharacterRelationship
)

logger = logging.getLogger(__name__)


class NarrativeService:
    """
    Servicio principal del motor narrativo.

    Gestiona todo el ciclo de vida narrativo del usuario:
    - Estado y progresion
    - Decisiones y consecuencias
    - Patrones y arquetipos
    - Relaciones con personajes
    - Seleccion de contenido personalizado

    Uso:
        service = NarrativeService(session)

        # Obtener estado del usuario
        state = await service.get_or_create_state(user_id)

        # Registrar decision
        decision = await service.record_decision(
            user_id=123,
            scene_id="intro",
            decision_type=DecisionType.DIALOGUE,
            key="honest_response",
            value="Le conte la verdad",
            response_time=45
        )

        # Obtener siguiente dialogo
        dialogue = await service.get_next_dialogue(user_id, "intro_complete")
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el servicio narrativo.

        Args:
            session: Sesion de base de datos SQLAlchemy async
        """
        self._session = session
        self._condition_evaluator = ConditionEvaluator(session)
        self._pattern_analyzer = PatternAnalyzer()
        self._dialogue_selector = DialogueSelector(session)

        logger.debug("NarrativeService inicializado")

    # =========================================================================
    # ESTADO DEL USUARIO
    # =========================================================================

    async def get_or_create_state(self, user_id: int) -> UserNarrativeState:
        """
        Obtiene o crea el estado narrativo del usuario.

        Si el usuario no tiene estado previo, crea uno con valores
        por defecto (nivel 1, sin arquetipos, relaciones en 0).

        Args:
            user_id: ID del usuario de Telegram

        Returns:
            UserNarrativeState: Estado narrativo del usuario

        Example:
            state = await service.get_or_create_state(123456789)
            print(f"Usuario en nivel {state.current_level}")
        """
        # Buscar estado existente
        result = await self._session.execute(
            select(UserNarrativeState)
            .where(UserNarrativeState.user_id == user_id)
            .options(
                selectinload(UserNarrativeState.decisions),
                selectinload(UserNarrativeState.patterns)
            )
        )
        state = result.scalar_one_or_none()

        if state is not None:
            # Actualizar ultima interaccion
            state.last_interaction = datetime.utcnow()
            logger.debug(f"Estado narrativo recuperado: user={user_id}, level={state.current_level}")
            return state

        # Crear nuevo estado
        state = UserNarrativeState(
            user_id=user_id,
            current_level=1,
            diana_trust=0,
            lucien_respect=0,
            intimacy_level=0,
            archetype_introspective=0,
            archetype_direct=0,
            archetype_romantic=0,
            archetype_analytical=0,
            narrative_flags={
                "completed_scenes": [],
                "unlocked_content": [],
                "blocked_content": {},
                "achievements": [],
                "special_flags": []
            },
            decision_summary={
                "first_choice": None,
                "memorable_moments": [],
                "pattern_history": []
            }
        )

        self._session.add(state)
        await self._session.flush()  # Para obtener el ID

        logger.info(f"Nuevo estado narrativo creado: user={user_id}")
        return state

    async def update_level(
        self,
        user_id: int,
        new_level: int,
        scene_id: Optional[str] = None
    ) -> UserNarrativeState:
        """
        Actualiza el nivel narrativo del usuario.

        Valida que el nuevo nivel sea valido (1-6) y registra
        la escena actual si se proporciona.

        Args:
            user_id: ID del usuario
            new_level: Nuevo nivel (1-6)
            scene_id: ID de la escena actual (opcional)

        Returns:
            UserNarrativeState: Estado actualizado

        Raises:
            ValueError: Si new_level no esta entre 1 y 6
        """
        if not 1 <= new_level <= 6:
            raise ValueError(f"Nivel invalido: {new_level}. Debe ser 1-6.")

        state = await self.get_or_create_state(user_id)
        old_level = state.current_level

        state.current_level = new_level
        if scene_id:
            state.current_scene_id = scene_id
        state.last_interaction = datetime.utcnow()

        # Registrar transicion de nivel en flags
        if old_level != new_level:
            state.add_flag("special_flags", f"reached_level_{new_level}")
            logger.info(
                f"Nivel actualizado: user={user_id}, "
                f"{old_level} -> {new_level}"
            )

        return state

    async def set_current_scene(
        self,
        user_id: int,
        scene_id: str,
        chapter_id: Optional[str] = None
    ) -> UserNarrativeState:
        """
        Establece la escena actual del usuario.

        Registra la escena como completada si ya habia una anterior
        y actualiza el progreso.

        Args:
            user_id: ID del usuario
            scene_id: ID de la nueva escena
            chapter_id: ID del capitulo (opcional)

        Returns:
            UserNarrativeState: Estado actualizado
        """
        state = await self.get_or_create_state(user_id)

        # Marcar escena anterior como completada
        if state.current_scene_id and state.current_scene_id != scene_id:
            state.add_flag("completed_scenes", state.current_scene_id)

        state.current_scene_id = scene_id
        if chapter_id:
            state.current_chapter_id = chapter_id
        state.last_interaction = datetime.utcnow()

        logger.debug(f"Escena actualizada: user={user_id}, scene={scene_id}")
        return state

    # =========================================================================
    # DECISIONES
    # =========================================================================

    async def record_decision(
        self,
        user_id: int,
        scene_id: str,
        decision_type: DecisionType,
        key: str,
        value: Optional[str] = None,
        response_time: int = 0,
        presented_at: Optional[datetime] = None,
        immediate_consequences: Optional[Dict] = None,
        delayed_consequences: Optional[Dict] = None
    ) -> UserDecision:
        """
        Registra una decision narrativa del usuario.

        Crea un registro de la decision con su contexto completo:
        - Tiempo de respuesta (para detectar patrones)
        - Consecuencias inmediatas (aplicadas ahora)
        - Consecuencias diferidas (aplicadas despues)

        Automaticamente:
        - Categoriza el timing (instant/considered/delayed)
        - Detecta arquetipo de la decision
        - Actualiza metricas del usuario
        - Aplica consecuencias inmediatas

        Args:
            user_id: ID del usuario
            scene_id: ID de la escena donde ocurrio
            decision_type: Tipo de decision (TIMING, CONTENT, REACTION, etc.)
            key: Identificador de la opcion elegida
            value: Valor completo de la decision (opcional)
            response_time: Tiempo de respuesta en segundos
            presented_at: Cuando se presento la decision (default: now - response_time)
            immediate_consequences: Efectos a aplicar inmediatamente
            delayed_consequences: Efectos a aplicar despues

        Returns:
            UserDecision: Registro de la decision

        Example:
            decision = await service.record_decision(
                user_id=123,
                scene_id="intro_q1",
                decision_type=DecisionType.DIALOGUE,
                key="honest_answer",
                response_time=45,
                immediate_consequences={
                    "diana_trust": 5,
                    "archetype_introspective": 10
                }
            )
        """
        state = await self.get_or_create_state(user_id)

        # Calcular presented_at si no se proporciono
        if presented_at is None:
            presented_at = datetime.utcnow() - timedelta(seconds=response_time)

        # Crear registro de decision
        decision = UserDecision(
            narrative_state_id=state.id,
            user_id=user_id,
            scene_id=scene_id,
            decision_point_id=f"{scene_id}_{key}",
            decision_type=decision_type,
            decision_key=key,
            decision_value=value,
            presented_at=presented_at,
            responded_at=datetime.utcnow(),
            response_time_seconds=response_time,
            immediate_consequences=immediate_consequences or {},
            delayed_consequences=delayed_consequences or {}
        )

        # Categorizar timing
        decision.timing_category = decision.categorize_timing()

        # Detectar arquetipo de esta decision
        decision.detected_archetype = self._detect_decision_archetype(key, value)

        self._session.add(decision)

        # Actualizar metricas del estado
        state.total_decisions += 1
        state.last_interaction = datetime.utcnow()

        # Actualizar promedio de tiempo de respuesta
        if state.total_decisions == 1:
            state.response_speed_avg = float(response_time)
        else:
            # Media movil ponderada
            state.response_speed_avg = (
                state.response_speed_avg * 0.8 + float(response_time) * 0.2
            )

        # Registrar primera decision
        if state.decision_summary.get("first_choice") is None:
            state.decision_summary["first_choice"] = key

        # Aplicar consecuencias inmediatas
        if immediate_consequences:
            await self._apply_immediate_consequences(state, immediate_consequences)

        logger.info(
            f"Decision registrada: user={user_id}, scene={scene_id}, "
            f"key={key}, time={response_time}s"
        )

        return decision

    async def get_decision_history(
        self,
        user_id: int,
        limit: int = 20,
        scene_id: Optional[str] = None,
        decision_type: Optional[DecisionType] = None
    ) -> List[UserDecision]:
        """
        Obtiene el historial de decisiones del usuario.

        Permite filtrar por escena y tipo de decision.
        Ordenado por fecha descendente (mas recientes primero).

        Args:
            user_id: ID del usuario
            limit: Maximo de decisiones a retornar (default: 20)
            scene_id: Filtrar por escena (opcional)
            decision_type: Filtrar por tipo (opcional)

        Returns:
            List[UserDecision]: Lista de decisiones
        """
        query = (
            select(UserDecision)
            .where(UserDecision.user_id == user_id)
            .order_by(UserDecision.created_at.desc())
            .limit(limit)
        )

        if scene_id:
            query = query.where(UserDecision.scene_id == scene_id)

        if decision_type:
            query = query.where(UserDecision.decision_type == decision_type)

        result = await self._session.execute(query)
        return list(result.scalars().all())

    # =========================================================================
    # PATRONES Y ARQUETIPOS
    # =========================================================================

    async def analyze_patterns(self, user_id: int) -> List[PatternType]:
        """
        Analiza los patrones de comportamiento del usuario.

        Examina el historial de decisiones y detecta patrones como:
        - IMPULSIVE: Responde muy rapido (<30s)
        - PATIENT: Toma su tiempo (>5min)
        - CONSISTENT: Mismo arquetipo en multiples decisiones
        - ERRATIC: Cambia frecuentemente de estilo
        - ENGAGED: Alta participacion
        - PASSIVE: Baja participacion

        Los patrones detectados se almacenan en la BD para uso futuro.

        Args:
            user_id: ID del usuario

        Returns:
            List[PatternType]: Patrones activos detectados
        """
        decisions = await self.get_decision_history(user_id, limit=50)

        if len(decisions) < 5:
            logger.debug(f"Pocas decisiones para analisis: user={user_id}")
            return []

        state = await self.get_or_create_state(user_id)
        detected_patterns = self._pattern_analyzer.analyze(decisions)

        # Actualizar/crear registros de patrones en BD
        for pattern_type, confidence in detected_patterns:
            await self._update_pattern_record(
                state.id, user_id, pattern_type, confidence, len(decisions)
            )

        # Actualizar historial de patrones en decision_summary
        pattern_names = [p.value for p, _ in detected_patterns if _ >= 0.6]
        if pattern_names:
            state.decision_summary["pattern_history"] = pattern_names[-5:]

        logger.info(
            f"Patrones analizados: user={user_id}, "
            f"detectados={[p.value for p, c in detected_patterns if c >= 0.5]}"
        )

        return [p for p, c in detected_patterns if c >= 0.5]

    async def detect_archetype(
        self,
        user_id: int
    ) -> Tuple[Optional[ArchetypeType], Optional[ArchetypeType]]:
        """
        Detecta el arquetipo primario y secundario del usuario.

        Basado en:
        - Historial de decisiones
        - Patrones de comportamiento
        - Puntuaciones acumuladas por arquetipo

        Args:
            user_id: ID del usuario

        Returns:
            Tuple[Optional[ArchetypeType], Optional[ArchetypeType]]:
                (arquetipo_primario, arquetipo_secundario)
                Retorna None si no hay suficientes datos
        """
        state = await self.get_or_create_state(user_id)
        scores = self.get_archetype_scores_from_state(state)

        if sum(scores.values()) == 0:
            return None, None

        # Ordenar por puntuacion
        sorted_archetypes = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        primary = sorted_archetypes[0][0] if sorted_archetypes[0][1] > 0 else None
        secondary = sorted_archetypes[1][0] if len(sorted_archetypes) > 1 and sorted_archetypes[1][1] > 0 else None

        # Actualizar en estado si cambio
        if state.primary_archetype != primary or state.secondary_archetype != secondary:
            state.primary_archetype = primary
            state.secondary_archetype = secondary
            logger.info(
                f"Arquetipos actualizados: user={user_id}, "
                f"primary={primary}, secondary={secondary}"
            )

        return primary, secondary

    async def get_archetype_scores(self, user_id: int) -> Dict[ArchetypeType, int]:
        """
        Obtiene las puntuaciones de arquetipos del usuario.

        Cada arquetipo tiene un score de 0-100 basado en las
        decisiones del usuario.

        Args:
            user_id: ID del usuario

        Returns:
            Dict[ArchetypeType, int]: Puntuaciones por arquetipo
        """
        state = await self.get_or_create_state(user_id)
        return self.get_archetype_scores_from_state(state)

    def get_archetype_scores_from_state(
        self,
        state: UserNarrativeState
    ) -> Dict[ArchetypeType, int]:
        """
        Extrae puntuaciones de arquetipos desde el estado.

        Helper method para evitar queries adicionales.

        Args:
            state: Estado narrativo del usuario

        Returns:
            Dict[ArchetypeType, int]: Puntuaciones
        """
        return {
            ArchetypeType.INTROSPECTIVE: state.archetype_introspective,
            ArchetypeType.DIRECT: state.archetype_direct,
            ArchetypeType.ROMANTIC: state.archetype_romantic,
            ArchetypeType.ANALYTICAL: state.archetype_analytical
        }

    # =========================================================================
    # RELACIONES CON PERSONAJES
    # =========================================================================

    async def update_relationship(
        self,
        user_id: int,
        character: str,
        attribute: str,
        delta: int
    ) -> CharacterRelationship:
        """
        Actualiza un atributo de relacion con un personaje.

        Los atributos disponibles son:
        - trust_level: Confianza (0-100)
        - respect_level: Respeto (0-100)
        - intimacy_level: Intimidad (0-100)
        - familiarity_level: Familiaridad (0-100)

        El delta puede ser positivo o negativo, y el resultado
        se limita al rango 0-100.

        Args:
            user_id: ID del usuario
            character: Nombre del personaje ("diana" o "lucien")
            attribute: Atributo a modificar
            delta: Cambio a aplicar (puede ser negativo)

        Returns:
            CharacterRelationship: Relacion actualizada

        Raises:
            ValueError: Si el personaje o atributo no es valido
        """
        if character.lower() not in ("diana", "lucien"):
            raise ValueError(f"Personaje invalido: {character}")

        valid_attributes = ["trust_level", "respect_level", "intimacy_level", "familiarity_level"]
        if attribute not in valid_attributes:
            raise ValueError(f"Atributo invalido: {attribute}")

        character = character.lower()

        # Obtener o crear relacion
        result = await self._session.execute(
            select(CharacterRelationship)
            .where(
                CharacterRelationship.user_id == user_id,
                CharacterRelationship.character_name == character
            )
        )
        relationship = result.scalar_one_or_none()

        if relationship is None:
            relationship = CharacterRelationship(
                user_id=user_id,
                character_name=character,
                first_meeting_date=datetime.utcnow()
            )
            self._session.add(relationship)
            await self._session.flush()

        # Aplicar delta con limites
        current_value = getattr(relationship, attribute)
        new_value = max(0, min(100, current_value + delta))
        setattr(relationship, attribute, new_value)

        # Actualizar estado de relacion
        relationship.current_state = self._calculate_relationship_state(
            character, relationship
        )

        # Tambien actualizar el estado narrativo para queries rapidas
        state = await self.get_or_create_state(user_id)
        if character == "diana":
            state.diana_trust = relationship.trust_level
        else:
            state.lucien_respect = relationship.respect_level

        logger.debug(
            f"Relacion actualizada: user={user_id}, "
            f"{character}.{attribute}: {current_value} -> {new_value}"
        )

        return relationship

    async def get_diana_state(self, user_id: int) -> RelationshipState:
        """
        Obtiene el estado de relacion con Diana.

        Estados posibles:
        - DIANA_MYSTERIOUS: < 40 confianza
        - DIANA_REVEALING: 40-70 confianza
        - DIANA_VULNERABLE: > 70 confianza

        Args:
            user_id: ID del usuario

        Returns:
            RelationshipState: Estado actual con Diana
        """
        state = await self.get_or_create_state(user_id)
        return state.diana_state

    async def get_lucien_state(self, user_id: int) -> RelationshipState:
        """
        Obtiene el estado de relacion con Lucien.

        Estados posibles:
        - LUCIEN_COLD: < 30 respeto
        - LUCIEN_WARMING: 30-60 respeto
        - LUCIEN_TRUSTED: > 60 respeto

        Args:
            user_id: ID del usuario

        Returns:
            RelationshipState: Estado actual con Lucien
        """
        state = await self.get_or_create_state(user_id)
        return state.lucien_state

    # =========================================================================
    # CONTENIDO Y DIALOGOS
    # =========================================================================

    async def get_next_dialogue(
        self,
        user_id: int,
        trigger: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene el siguiente dialogo basado en el trigger y estado del usuario.

        El dialogo se selecciona y personaliza segun:
        - Arquetipo del usuario
        - Estado de relaciones
        - Historial de decisiones
        - Patrones detectados

        Args:
            user_id: ID del usuario
            trigger: Trigger que activa el dialogo

        Returns:
            Optional[Dict]: Dialogo con variantes aplicadas, o None si no hay

        Example:
            dialogue = await service.get_next_dialogue(123, "intro_complete")
            if dialogue:
                await bot.send_message(user_id, dialogue["text"])
        """
        state = await self.get_or_create_state(user_id)

        # Obtener dialogo base
        dialogue = await self._dialogue_selector.select_dialogue(
            user_id=user_id,
            trigger=trigger,
            state=state
        )

        if dialogue is None:
            logger.debug(f"No hay dialogo para trigger: {trigger}")
            return None

        logger.debug(
            f"Dialogo seleccionado: user={user_id}, "
            f"trigger={trigger}, id={dialogue.get('id')}"
        )

        return dialogue

    async def check_unlock_conditions(
        self,
        user_id: int,
        content_id: str
    ) -> bool:
        """
        Verifica si el usuario cumple condiciones para desbloquear contenido.

        Evalua todas las condiciones asociadas al content_id:
        - Nivel minimo
        - Confianza/respeto con personajes
        - Patrones requeridos
        - Arquetipos compatibles
        - Flags narrativos

        Args:
            user_id: ID del usuario
            content_id: ID del contenido a verificar

        Returns:
            bool: True si puede acceder, False si no
        """
        state = await self.get_or_create_state(user_id)

        # Verificar si ya esta desbloqueado
        if state.has_flag("unlocked_content", content_id):
            return True

        # Verificar si esta bloqueado
        if state.has_flag("blocked_content", content_id):
            return False

        # Buscar consecuencia que desbloquea este contenido
        result = await self._session.execute(
            select(NarrativeConsequence)
            .where(
                NarrativeConsequence.is_active == True,
                NarrativeConsequence.consequence_type == ConsequenceType.UNLOCK
            )
        )
        consequences = result.scalars().all()

        for consequence in consequences:
            effect = consequence.effect or {}
            if effect.get("unlock") == content_id:
                # Evaluar condiciones
                if await self._condition_evaluator.evaluate(user_id, consequence.conditions):
                    return True

        return False

    async def apply_consequence(
        self,
        user_id: int,
        consequence_id: str
    ) -> Dict[str, Any]:
        """
        Aplica una consecuencia narrativa al usuario.

        Verifica que:
        - La consecuencia existe y esta activa
        - El usuario cumple las condiciones
        - No se ha aplicado antes (si es one-time)

        Args:
            user_id: ID del usuario
            consequence_id: ID de la consecuencia a aplicar

        Returns:
            Dict: Resultado de la aplicacion con efectos aplicados

        Raises:
            ValueError: Si la consecuencia no existe o no cumple condiciones
        """
        # Buscar consecuencia
        result = await self._session.execute(
            select(NarrativeConsequence)
            .where(NarrativeConsequence.consequence_id == consequence_id)
        )
        consequence = result.scalar_one_or_none()

        if consequence is None:
            raise ValueError(f"Consecuencia no encontrada: {consequence_id}")

        if not consequence.is_active:
            raise ValueError(f"Consecuencia inactiva: {consequence_id}")

        # Verificar si ya fue aplicada (one-time)
        if consequence.is_one_time:
            applied_result = await self._session.execute(
                select(AppliedConsequence)
                .where(
                    AppliedConsequence.user_id == user_id,
                    AppliedConsequence.consequence_id == consequence_id
                )
            )
            if applied_result.scalar_one_or_none() is not None:
                logger.debug(f"Consecuencia ya aplicada: {consequence_id}")
                return {"already_applied": True}

        # Verificar condiciones
        if not await self._condition_evaluator.evaluate(user_id, consequence.conditions):
            raise ValueError(f"Condiciones no cumplidas para: {consequence_id}")

        # Aplicar efectos
        state = await self.get_or_create_state(user_id)
        state_before = {
            "diana_trust": state.diana_trust,
            "lucien_respect": state.lucien_respect,
            "level": state.current_level
        }

        effects_applied = await self._apply_consequence_effects(
            state, consequence.effect
        )

        state_after = {
            "diana_trust": state.diana_trust,
            "lucien_respect": state.lucien_respect,
            "level": state.current_level
        }

        # Registrar aplicacion
        applied = AppliedConsequence(
            user_id=user_id,
            consequence_id=consequence_id,
            applied_in_scene=state.current_scene_id,
            applied_at_level=state.current_level,
            result={
                "effects_applied": effects_applied,
                "user_state_before": state_before,
                "user_state_after": state_after
            }
        )
        self._session.add(applied)

        logger.info(
            f"Consecuencia aplicada: user={user_id}, "
            f"consequence={consequence_id}, effects={effects_applied}"
        )

        return {
            "consequence_id": consequence_id,
            "effects_applied": effects_applied,
            "state_before": state_before,
            "state_after": state_after
        }

    # =========================================================================
    # MEMORIA DE PERSONAJES
    # =========================================================================

    async def add_character_memory(
        self,
        user_id: int,
        character: str,
        memory_type: str,
        content: str,
        context: Optional[Dict] = None
    ) -> CharacterRelationship:
        """
        Agrega un recuerdo que el personaje tiene del usuario.

        Los recuerdos permiten que los personajes referencien
        interacciones pasadas en dialogos futuros.

        Args:
            user_id: ID del usuario
            character: Nombre del personaje ("diana" o "lucien")
            memory_type: Tipo de recuerdo ("choice", "patience", "honesty", etc.)
            content: Descripcion del recuerdo
            context: Contexto adicional (opcional)

        Returns:
            CharacterRelationship: Relacion actualizada
        """
        character = character.lower()

        # Obtener o crear relacion
        result = await self._session.execute(
            select(CharacterRelationship)
            .where(
                CharacterRelationship.user_id == user_id,
                CharacterRelationship.character_name == character
            )
        )
        relationship = result.scalar_one_or_none()

        if relationship is None:
            relationship = CharacterRelationship(
                user_id=user_id,
                character_name=character,
                first_meeting_date=datetime.utcnow()
            )
            self._session.add(relationship)
            await self._session.flush()

        # Agregar recuerdo
        relationship.add_memory(memory_type, content, context)

        logger.debug(
            f"Memoria agregada: user={user_id}, "
            f"{character} recuerda: {memory_type}"
        )

        return relationship

    async def get_character_memories(
        self,
        user_id: int,
        character: str
    ) -> List[Dict]:
        """
        Obtiene los recuerdos que un personaje tiene del usuario.

        Args:
            user_id: ID del usuario
            character: Nombre del personaje

        Returns:
            List[Dict]: Lista de recuerdos
        """
        character = character.lower()

        result = await self._session.execute(
            select(CharacterRelationship)
            .where(
                CharacterRelationship.user_id == user_id,
                CharacterRelationship.character_name == character
            )
        )
        relationship = result.scalar_one_or_none()

        if relationship is None:
            return []

        return relationship.character_memories or []

    # =========================================================================
    # METODOS PRIVADOS
    # =========================================================================

    def _detect_decision_archetype(
        self,
        key: str,
        value: Optional[str]
    ) -> Optional[ArchetypeType]:
        """
        Detecta el arquetipo asociado a una decision.

        Mapea claves de decision a arquetipos basandose en
        convenciones de nombres.
        """
        key_lower = key.lower()

        # Mapeo por prefijos/sufijos comunes
        archetype_keywords = {
            ArchetypeType.INTROSPECTIVE: ["reflect", "think", "why", "curious", "wonder"],
            ArchetypeType.DIRECT: ["honest", "direct", "tell", "truth", "straight"],
            ArchetypeType.ROMANTIC: ["feel", "heart", "connect", "love", "emotion"],
            ArchetypeType.ANALYTICAL: ["logic", "analyze", "reason", "pattern", "understand"]
        }

        for archetype, keywords in archetype_keywords.items():
            if any(kw in key_lower for kw in keywords):
                return archetype

        return None

    async def _apply_immediate_consequences(
        self,
        state: UserNarrativeState,
        consequences: Dict[str, Any]
    ) -> None:
        """Aplica consecuencias inmediatas al estado."""
        for key, value in consequences.items():
            if key == "diana_trust":
                state.diana_trust = max(0, min(100, state.diana_trust + value))
            elif key == "lucien_respect":
                state.lucien_respect = max(0, min(100, state.lucien_respect + value))
            elif key == "intimacy_level":
                state.intimacy_level = max(0, min(100, state.intimacy_level + value))
            elif key.startswith("archetype_"):
                archetype_attr = key
                current = getattr(state, archetype_attr, 0)
                setattr(state, archetype_attr, max(0, min(100, current + value)))
            elif key == "add_flag":
                flag_type = value.get("type")
                flag_name = value.get("name")
                if flag_type and flag_name:
                    state.add_flag(flag_type, flag_name)

    async def _apply_consequence_effects(
        self,
        state: UserNarrativeState,
        effect: Dict[str, Any]
    ) -> List[str]:
        """Aplica efectos de una consecuencia y retorna lista de efectos aplicados."""
        effects_applied = []

        for key, value in effect.items():
            if key == "unlock":
                state.add_flag("unlocked_content", value)
                effects_applied.append(f"unlocked:{value}")
            elif key == "block":
                state.add_flag("blocked_content", value)
                effects_applied.append(f"blocked:{value}")
            elif key == "diana_trust":
                state.diana_trust = max(0, min(100, state.diana_trust + value))
                effects_applied.append(f"diana_trust+{value}")
            elif key == "lucien_respect":
                state.lucien_respect = max(0, min(100, state.lucien_respect + value))
                effects_applied.append(f"lucien_respect+{value}")
            elif key == "add_flag":
                flag_type = value.get("type")
                flag_name = value.get("name")
                if flag_type and flag_name:
                    state.add_flag(flag_type, flag_name)
                    effects_applied.append(f"flag:{flag_type}.{flag_name}")
            elif key == "set_level":
                state.current_level = value
                effects_applied.append(f"level={value}")

        return effects_applied

    async def _update_pattern_record(
        self,
        state_id: int,
        user_id: int,
        pattern_type: PatternType,
        confidence: float,
        sample_size: int
    ) -> None:
        """Actualiza o crea registro de patron en BD."""
        result = await self._session.execute(
            select(UserBehaviorPattern)
            .where(
                UserBehaviorPattern.narrative_state_id == state_id,
                UserBehaviorPattern.pattern_type == pattern_type
            )
        )
        pattern = result.scalar_one_or_none()

        if pattern is None:
            pattern = UserBehaviorPattern(
                narrative_state_id=state_id,
                user_id=user_id,
                pattern_type=pattern_type,
                confidence_score=confidence,
                sample_size=sample_size
            )
            self._session.add(pattern)
        else:
            pattern.confidence_score = confidence
            pattern.sample_size = sample_size
            pattern.last_confirmed_at = datetime.utcnow()
            pattern.times_confirmed += 1
            pattern.is_active = confidence >= 0.5

    def _calculate_relationship_state(
        self,
        character: str,
        relationship: CharacterRelationship
    ) -> RelationshipState:
        """Calcula el estado de relacion basado en metricas."""
        if character == "diana":
            if relationship.trust_level >= 70:
                return RelationshipState.DIANA_VULNERABLE
            elif relationship.trust_level >= 40:
                return RelationshipState.DIANA_REVEALING
            return RelationshipState.DIANA_MYSTERIOUS
        else:  # lucien
            if relationship.respect_level >= 60:
                return RelationshipState.LUCIEN_TRUSTED
            elif relationship.respect_level >= 30:
                return RelationshipState.LUCIEN_WARMING
            return RelationshipState.LUCIEN_COLD


class ConditionEvaluator:
    """
    Evaluador de condiciones narrativas.

    Evalua condiciones complejas usando un DSL JSON flexible.

    Formatos soportados:
        {"level": {">=": 3}}
        {"diana_trust": {">=": 50}}
        {"pattern": {"has": "patient"}}
        {"archetype": {"in": ["romantic", "introspective"]}}
        {"flags": {"has_all": ["completed_intro", "saw_diana_photo"]}}
        {"decisions": {"count": {">=": 10}}}
        {"response_time_avg": {"<": 60}}

    Operadores logicos:
        {"$and": [cond1, cond2]}
        {"$or": [cond1, cond2]}
        {"$not": cond}
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el evaluador.

        Args:
            session: Sesion de base de datos
        """
        self._session = session

    async def evaluate(
        self,
        user_id: int,
        conditions: Dict[str, Any]
    ) -> bool:
        """
        Evalua un conjunto de condiciones para un usuario.

        Todas las condiciones de nivel superior se evaluan con AND
        implicito, a menos que se use $or explicito.

        Args:
            user_id: ID del usuario
            conditions: Diccionario de condiciones

        Returns:
            bool: True si todas las condiciones se cumplen

        Example:
            result = await evaluator.evaluate(123, {
                "level": {">=": 3},
                "diana_trust": {">=": 50},
                "archetype": {"in": ["romantic"]}
            })
        """
        if not conditions:
            return True

        # Obtener estado del usuario
        result = await self._session.execute(
            select(UserNarrativeState)
            .where(UserNarrativeState.user_id == user_id)
            .options(selectinload(UserNarrativeState.patterns))
        )
        state = result.scalar_one_or_none()

        if state is None:
            logger.debug(f"No hay estado narrativo para user={user_id}")
            return False

        # Evaluar cada condicion
        for key, condition in conditions.items():
            if key.startswith("$"):
                # Operador logico
                if not await self._evaluate_logical(user_id, state, key, condition):
                    return False
            else:
                # Condicion de atributo
                if not self._evaluate_attribute(state, key, condition):
                    return False

        return True

    async def _evaluate_logical(
        self,
        user_id: int,
        state: UserNarrativeState,
        operator: str,
        conditions: Any
    ) -> bool:
        """Evalua operadores logicos."""
        if operator == "$and":
            for cond in conditions:
                if not await self.evaluate(user_id, cond):
                    return False
            return True

        elif operator == "$or":
            for cond in conditions:
                if await self.evaluate(user_id, cond):
                    return True
            return False

        elif operator == "$not":
            return not await self.evaluate(user_id, conditions)

        logger.warning(f"Operador logico desconocido: {operator}")
        return False

    def _evaluate_attribute(
        self,
        state: UserNarrativeState,
        attribute: str,
        condition: Any
    ) -> bool:
        """Evalua una condicion de atributo."""
        # Obtener valor actual del atributo
        value = self._get_attribute_value(state, attribute)

        if value is None:
            logger.debug(f"Atributo no encontrado: {attribute}")
            return False

        # Evaluar condicion
        if isinstance(condition, dict):
            return self._evaluate_comparison(value, condition)
        else:
            # Comparacion directa de igualdad
            return value == condition

    def _get_attribute_value(
        self,
        state: UserNarrativeState,
        attribute: str
    ) -> Any:
        """Obtiene el valor de un atributo del estado."""
        # Atributos directos
        direct_attrs = {
            "level": state.current_level,
            "diana_trust": state.diana_trust,
            "lucien_respect": state.lucien_respect,
            "intimacy_level": state.intimacy_level,
            "response_time_avg": state.response_speed_avg,
            "participation_rate": state.participation_rate,
            "total_decisions": state.total_decisions,
            "primary_archetype": state.primary_archetype.value if state.primary_archetype else None,
            "secondary_archetype": state.secondary_archetype.value if state.secondary_archetype else None
        }

        if attribute in direct_attrs:
            return direct_attrs[attribute]

        # Flags
        if attribute == "flags":
            return state.narrative_flags or {}

        # Patrones activos
        if attribute == "pattern":
            return [
                p.pattern_type.value
                for p in (state.patterns or [])
                if p.is_active and p.confidence_score >= 0.5
            ]

        # Arquetipo (para comparacion "in")
        if attribute == "archetype":
            archetypes = []
            if state.primary_archetype:
                archetypes.append(state.primary_archetype.value)
            if state.secondary_archetype:
                archetypes.append(state.secondary_archetype.value)
            return archetypes

        # Decisions (para conteo)
        if attribute == "decisions":
            return {"count": state.total_decisions}

        return None

    def _evaluate_comparison(
        self,
        value: Any,
        condition: Dict[str, Any]
    ) -> bool:
        """Evalua operadores de comparacion."""
        for op, target in condition.items():
            if op == ">=":
                if not (isinstance(value, (int, float)) and value >= target):
                    return False
            elif op == ">":
                if not (isinstance(value, (int, float)) and value > target):
                    return False
            elif op == "<=":
                if not (isinstance(value, (int, float)) and value <= target):
                    return False
            elif op == "<":
                if not (isinstance(value, (int, float)) and value < target):
                    return False
            elif op == "==":
                if value != target:
                    return False
            elif op == "!=":
                if value == target:
                    return False
            elif op == "in":
                if isinstance(value, list):
                    if not any(v in target for v in value):
                        return False
                elif value not in target:
                    return False
            elif op == "has":
                if isinstance(value, list):
                    if target not in value:
                        return False
                elif isinstance(value, dict):
                    if target not in value:
                        return False
                else:
                    return False
            elif op == "has_all":
                if isinstance(value, dict):
                    value = list(value.keys())
                if not isinstance(value, list):
                    return False
                if not all(t in value for t in target):
                    return False
            elif op == "has_any":
                if isinstance(value, dict):
                    value = list(value.keys())
                if not isinstance(value, list):
                    return False
                if not any(t in value for t in target):
                    return False
            elif op == "count":
                # Para evaluar {"decisions": {"count": {">=": 10}}}
                if isinstance(value, dict) and "count" in value:
                    return self._evaluate_comparison(value["count"], target)
                return False
            else:
                logger.warning(f"Operador de comparacion desconocido: {op}")
                return False

        return True


class PatternAnalyzer:
    """
    Analizador de patrones de comportamiento.

    Analiza el historial de decisiones para detectar patrones
    consistentes en el comportamiento del usuario.

    Patrones detectados:
        IMPULSIVE: Responde muy rapido (<30s en >60% de decisiones)
        PATIENT: Toma su tiempo (>5min en >40% de decisiones)
        CONSISTENT: Mismo arquetipo en >70% de decisiones
        ERRATIC: Cambia de arquetipo frecuentemente
        ENGAGED: Alta frecuencia de interaccion
        PASSIVE: Baja frecuencia de interaccion
    """

    # Umbrales configurables
    IMPULSIVE_THRESHOLD = 30  # segundos
    PATIENT_THRESHOLD = 300  # segundos (5 min)
    CONSISTENCY_THRESHOLD = 0.7  # 70%

    def analyze(
        self,
        decisions: List[UserDecision]
    ) -> List[Tuple[PatternType, float]]:
        """
        Analiza decisiones y retorna patrones detectados con confianza.

        Args:
            decisions: Lista de decisiones a analizar

        Returns:
            List[Tuple[PatternType, float]]: Lista de (patron, confianza)
                donde confianza es 0.0-1.0
        """
        if len(decisions) < 5:
            return []

        patterns = []

        # Detectar patrones de timing
        impulsive_conf = self._detect_impulsive(decisions)
        if impulsive_conf > 0.3:
            patterns.append((PatternType.IMPULSIVE, impulsive_conf))

        patient_conf = self._detect_patient(decisions)
        if patient_conf > 0.3:
            patterns.append((PatternType.PATIENT, patient_conf))

        # Detectar consistencia/erratico
        consistent_conf = self._detect_consistent(decisions)
        if consistent_conf > 0.5:
            patterns.append((PatternType.CONSISTENT, consistent_conf))
        elif consistent_conf < 0.3:
            patterns.append((PatternType.ERRATIC, 1.0 - consistent_conf))

        # Detectar engagement
        engaged_conf, passive_conf = self._detect_engagement(decisions)
        if engaged_conf > 0.5:
            patterns.append((PatternType.ENGAGED, engaged_conf))
        if passive_conf > 0.5:
            patterns.append((PatternType.PASSIVE, passive_conf))

        return patterns

    def _detect_impulsive(self, decisions: List[UserDecision]) -> float:
        """
        Detecta patron impulsivo.

        Confianza basada en porcentaje de respuestas rapidas.
        """
        if not decisions:
            return 0.0

        fast_count = sum(
            1 for d in decisions
            if d.response_time_seconds < self.IMPULSIVE_THRESHOLD
        )

        return fast_count / len(decisions)

    def _detect_patient(self, decisions: List[UserDecision]) -> float:
        """
        Detecta patron paciente.

        Confianza basada en porcentaje de respuestas lentas.
        """
        if not decisions:
            return 0.0

        slow_count = sum(
            1 for d in decisions
            if d.response_time_seconds > self.PATIENT_THRESHOLD
        )

        return slow_count / len(decisions)

    def _detect_consistent(self, decisions: List[UserDecision]) -> float:
        """
        Detecta consistencia en arquetipos elegidos.

        Retorna porcentaje de decisiones con el arquetipo mas comun.
        """
        if not decisions:
            return 0.0

        # Contar arquetipos
        archetype_counts: Dict[Optional[ArchetypeType], int] = {}
        for d in decisions:
            archetype = d.detected_archetype
            archetype_counts[archetype] = archetype_counts.get(archetype, 0) + 1

        # Excluir None
        archetype_counts.pop(None, None)

        if not archetype_counts:
            return 0.5  # Sin datos suficientes, asumir neutral

        max_count = max(archetype_counts.values())
        return max_count / len(decisions)

    def _detect_engagement(
        self,
        decisions: List[UserDecision]
    ) -> Tuple[float, float]:
        """
        Detecta nivel de engagement.

        Basado en frecuencia de interaccion y participacion.

        Returns:
            Tuple[float, float]: (engaged_confidence, passive_confidence)
        """
        if len(decisions) < 2:
            return 0.0, 0.0

        # Calcular frecuencia promedio entre decisiones
        sorted_decisions = sorted(decisions, key=lambda d: d.created_at)
        time_gaps = []

        for i in range(1, len(sorted_decisions)):
            gap = (
                sorted_decisions[i].created_at -
                sorted_decisions[i-1].created_at
            ).total_seconds() / 3600  # En horas
            time_gaps.append(gap)

        if not time_gaps:
            return 0.0, 0.0

        avg_gap = sum(time_gaps) / len(time_gaps)

        # Engaged: interacciones frecuentes (promedio < 6 horas)
        # Passive: interacciones espaciadas (promedio > 48 horas)
        if avg_gap < 6:
            engaged_conf = min(1.0, (6 - avg_gap) / 6)
            return engaged_conf, 0.0
        elif avg_gap > 48:
            passive_conf = min(1.0, (avg_gap - 48) / 48)
            return 0.0, passive_conf

        return 0.0, 0.0

    def calculate_archetype_scores(
        self,
        decisions: List[UserDecision]
    ) -> Dict[ArchetypeType, int]:
        """
        Calcula puntuaciones de arquetipos basado en decisiones.

        Args:
            decisions: Lista de decisiones

        Returns:
            Dict[ArchetypeType, int]: Puntuaciones (0-100)
        """
        scores = {
            ArchetypeType.INTROSPECTIVE: 0,
            ArchetypeType.DIRECT: 0,
            ArchetypeType.ROMANTIC: 0,
            ArchetypeType.ANALYTICAL: 0
        }

        if not decisions:
            return scores

        for d in decisions:
            if d.detected_archetype:
                # Puntos por decision con arquetipo detectado
                scores[d.detected_archetype] += 10

                # Bonus por consistencia
                if d.timing_category == "considered":
                    scores[d.detected_archetype] += 2

        # Normalizar a 0-100
        max_possible = len(decisions) * 12
        if max_possible > 0:
            for archetype in scores:
                scores[archetype] = min(100, int(scores[archetype] / max_possible * 100))

        return scores


class DialogueSelector:
    """
    Selector de dialogos personalizados.

    Selecciona y personaliza dialogos basandose en:
    - Trigger solicitado
    - Arquetipo del usuario
    - Estado de relaciones
    - Patrones de comportamiento
    - Historial de decisiones

    Los dialogos pueden tener multiples variantes que se seleccionan
    automaticamente segun el contexto del usuario.
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el selector.

        Args:
            session: Sesion de base de datos
        """
        self._session = session

    async def select_dialogue(
        self,
        user_id: int,
        trigger: str,
        state: UserNarrativeState
    ) -> Optional[Dict[str, Any]]:
        """
        Selecciona el dialogo apropiado para el usuario.

        Busca dialogos que coincidan con el trigger y selecciona
        la variante mas apropiada segun el estado del usuario.

        Args:
            user_id: ID del usuario
            trigger: Trigger que activa el dialogo
            state: Estado narrativo actual

        Returns:
            Optional[Dict]: Dialogo con variantes aplicadas

        Schema de retorno:
            {
                "id": "dialogue_id",
                "character": "diana",
                "text": "Texto personalizado...",
                "options": [...],
                "media": {...},
                "metadata": {...}
            }
        """
        # Buscar dialogos por trigger
        # (En implementacion real, esto seria una query a la BD de contenido)
        dialogue_data = await self._find_dialogue_by_trigger(trigger)

        if dialogue_data is None:
            return None

        # Seleccionar variante segun arquetipo
        selected_variant = self._select_variant(dialogue_data, state)

        # Aplicar personalizacion
        personalized = self._personalize_dialogue(selected_variant, state)

        return personalized

    async def _find_dialogue_by_trigger(
        self,
        trigger: str
    ) -> Optional[Dict[str, Any]]:
        """
        Busca un dialogo por su trigger.

        En implementacion completa, esto consultaria una tabla
        de contenido narrativo.
        """
        # Placeholder - en implementacion real seria query a BD
        # Por ahora retorna None para indicar que no hay dialogos cargados
        return None

    def _select_variant(
        self,
        dialogue_data: Dict[str, Any],
        state: UserNarrativeState
    ) -> Dict[str, Any]:
        """
        Selecciona la variante de dialogo mas apropiada.

        Criterios de seleccion (en orden de prioridad):
        1. Variante especifica para arquetipo primario
        2. Variante especifica para arquetipo secundario
        3. Variante para estado de relacion
        4. Variante por defecto
        """
        variants = dialogue_data.get("variants", {})

        if not variants:
            return dialogue_data

        # Intentar variante por arquetipo primario
        if state.primary_archetype:
            archetype_key = state.primary_archetype.value
            if archetype_key in variants:
                return {**dialogue_data, **variants[archetype_key]}

        # Intentar variante por arquetipo secundario
        if state.secondary_archetype:
            archetype_key = state.secondary_archetype.value
            if archetype_key in variants:
                return {**dialogue_data, **variants[archetype_key]}

        # Intentar variante por estado de relacion
        diana_state = state.diana_state.value
        if diana_state in variants:
            return {**dialogue_data, **variants[diana_state]}

        lucien_state = state.lucien_state.value
        if lucien_state in variants:
            return {**dialogue_data, **variants[lucien_state]}

        # Variante por defecto
        if "default" in variants:
            return {**dialogue_data, **variants["default"]}

        return dialogue_data

    def _personalize_dialogue(
        self,
        dialogue: Dict[str, Any],
        state: UserNarrativeState
    ) -> Dict[str, Any]:
        """
        Aplica personalizacion al texto del dialogo.

        Reemplaza placeholders como:
        - {user_archetype}: Arquetipo primario
        - {diana_state}: Estado de relacion con Diana
        - {level}: Nivel actual
        - {trust}: Nivel de confianza con Diana
        """
        result = dialogue.copy()

        if "text" in result and isinstance(result["text"], str):
            text = result["text"]

            # Reemplazos disponibles
            replacements = {
                "{user_archetype}": (
                    state.primary_archetype.value
                    if state.primary_archetype else "unknown"
                ),
                "{diana_state}": state.diana_state.value,
                "{lucien_state}": state.lucien_state.value,
                "{level}": str(state.current_level),
                "{trust}": str(state.diana_trust),
                "{respect}": str(state.lucien_respect),
                "{intimacy}": str(state.intimacy_level)
            }

            for placeholder, value in replacements.items():
                text = text.replace(placeholder, value)

            result["text"] = text

        return result
