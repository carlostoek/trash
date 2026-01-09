# NARRATIVE SYSTEM - TECHNICAL ARCHITECTURE

## CONCEPT TRANSLATION

```
CONCEPT: Branching story system where user decisions modify the narrative,
         with intimacy tracking, archetype detection, and dynamic content unlocking.

CORE MECHANICS EXTRACTED:
1. User narrative state persistence (level, scene, flags, relationships)
2. Decision recording with timing analysis
3. Behavior pattern detection (impulsive/patient/consistent/erratic)
4. Dynamic condition evaluation for content gating
5. Consequence application based on decision patterns
6. Archetype detection for personalization

TECHNICAL TRANSLATION:
- SQLAlchemy async models for state persistence
- NarrativeService for business logic
- ConditionEvaluator for flexible rule matching
- Integration with existing ServiceContainer pattern
- Alembic migrations for schema changes
```

---

## 1. DATABASE MODELS (SQLAlchemy)

### 1.1 Enums for Narrative System

**File:** `bot/narrative/database/enums.py`

```python
"""
Enums para el sistema narrativo.

Define tipos y estados usados en el sistema de narrativa.
"""
from enum import Enum


class NarrativeLevel(int, Enum):
    """
    Niveles de progresion narrativa (1-6).

    Cada nivel desbloquea contenido mas profundo:
        LEVEL_1: Conocimiento inicial
        LEVEL_2: Primeras misiones
        LEVEL_3: Acceso a secretos
        LEVEL_4: Confianza establecida
        LEVEL_5: Contenido exclusivo
        LEVEL_6: Inner circle
    """
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5
    LEVEL_6 = 6

    @property
    def display_name(self) -> str:
        """Retorna nombre legible del nivel."""
        names = {
            1: "Novato",
            2: "Explorador",
            3: "Iniciado",
            4: "Confidente",
            5: "Elite",
            6: "Inner Circle"
        }
        return names[self.value]


class DecisionType(str, Enum):
    """
    Tipos de decisiones que el usuario puede tomar.

    Tipos:
        TIMING: Decisiones basadas en tiempo de respuesta
        CONTENT: Eleccion de contenido/opcion
        REACTION: Reaccion a eventos/mensajes
        DIALOGUE: Respuesta en dialogos
        MISSION: Eleccion en misiones
    """
    TIMING = "timing"
    CONTENT = "content"
    REACTION = "reaction"
    DIALOGUE = "dialogue"
    MISSION = "mission"

    def __str__(self) -> str:
        return self.value


class PatternType(str, Enum):
    """
    Tipos de patrones de comportamiento detectados.

    Patrones:
        IMPULSIVE: Respuestas rapidas, poco reflexivas
        PATIENT: Toma tiempo para decidir
        CONSISTENT: Patrones estables de comportamiento
        ERRATIC: Comportamiento impredecible
        EXPLORATORY: Busca todas las opciones
        FOCUSED: Se enfoca en un camino
    """
    IMPULSIVE = "impulsive"
    PATIENT = "patient"
    CONSISTENT = "consistent"
    ERRATIC = "erratic"
    EXPLORATORY = "exploratory"
    FOCUSED = "focused"

    def __str__(self) -> str:
        return self.value

    @property
    def description(self) -> str:
        """Descripcion del patron."""
        descriptions = {
            "impulsive": "Responde rapidamente sin mucha reflexion",
            "patient": "Se toma su tiempo para pensar",
            "consistent": "Mantiene un patron de comportamiento estable",
            "erratic": "Comportamiento impredecible y variado",
            "exploratory": "Busca explorar todas las opciones",
            "focused": "Se enfoca en un camino especifico"
        }
        return descriptions[self.value]


class ConsequenceType(str, Enum):
    """
    Tipos de consecuencias que aplican a decisiones.

    Tipos:
        UNLOCK: Desbloquea contenido nuevo
        BLOCK: Bloquea contenido temporalmente
        MODIFY: Modifica estado o valores
        BRANCH: Cambia el flujo narrativo
        REWARD: Otorga recompensa (puntos, items)
        RELATIONSHIP: Modifica relacion con personaje
    """
    UNLOCK = "unlock"
    BLOCK = "block"
    MODIFY = "modify"
    BRANCH = "branch"
    REWARD = "reward"
    RELATIONSHIP = "relationship"

    def __str__(self) -> str:
        return self.value


class ArchetypeType(str, Enum):
    """
    Arquetipos de usuario detectados por comportamiento.

    Arquetipos:
        ROMANTIC: Busca conexion emocional
        ADVENTURER: Busca nuevas experiencias
        COLLECTOR: Quiere desbloquear todo
        INTROSPECTIVE: Reflexivo y profundo
        SOCIAL: Busca interaccion
        ACHIEVER: Orientado a logros
    """
    ROMANTIC = "romantic"
    ADVENTURER = "adventurer"
    COLLECTOR = "collector"
    INTROSPECTIVE = "introspective"
    SOCIAL = "social"
    ACHIEVER = "achiever"

    def __str__(self) -> str:
        return self.value

    @property
    def emoji(self) -> str:
        """Emoji del arquetipo."""
        emojis = {
            "romantic": "💕",
            "adventurer": "🗺️",
            "collector": "📚",
            "introspective": "🔮",
            "social": "👥",
            "achiever": "🏆"
        }
        return emojis[self.value]
```

---

### 1.2 Core Narrative Models

**File:** `bot/narrative/database/models.py`

```python
"""
Modelos de base de datos para el sistema narrativo.

Tablas:
- user_narrative_state: Estado narrativo del usuario
- user_decisions: Historial de decisiones
- user_behavior_patterns: Patrones de comportamiento detectados
- narrative_consequences: Consecuencias de patrones de decision
- character_relationships: Relaciones usuario-personaje
"""
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime,
    BigInteger, JSON, ForeignKey, Index, Float, Enum, Text
)
from sqlalchemy.orm import relationship

from bot.database.base import Base
from bot.narrative.database.enums import (
    NarrativeLevel, DecisionType, PatternType,
    ConsequenceType, ArchetypeType
)

logger = logging.getLogger(__name__)


class UserNarrativeState(Base):
    """
    Estado narrativo del usuario.

    Rastrea la posicion y progreso del usuario en la narrativa:
    - Nivel actual (1-6)
    - Escena actual
    - Flags de contenido desbloqueado
    - Scores de relaciones con personajes
    - Arquetipo detectado

    Este es el modelo central para personalizar la experiencia.

    Attributes:
        user_id: ID de Telegram del usuario (FK a users)
        current_level: Nivel narrativo actual (1-6)
        current_scene_id: ID de la escena actual (nullable)
        current_chapter_id: ID del capitulo actual (nullable)
        narrative_flags: JSON con flags de progreso
        relationship_scores: JSON con scores por personaje
        archetype: Arquetipo detectado del usuario
        archetype_confidence: Confianza en deteccion (0.0-1.0)
        total_decisions: Contador de decisiones tomadas
        last_interaction: Ultima interaccion con narrativa
        created_at: Fecha de creacion del estado
        updated_at: Ultima actualizacion
    """
    __tablename__ = "user_narrative_state"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Usuario (FK a users)
    user_id = Column(
        BigInteger,
        ForeignKey("users.user_id"),
        unique=True,
        nullable=False,
        index=True
    )

    # Progresion
    current_level = Column(
        Integer,
        nullable=False,
        default=1
    )
    current_scene_id = Column(Integer, nullable=True)
    current_chapter_id = Column(Integer, nullable=True)

    # Estado narrativo (JSON)
    narrative_flags = Column(
        JSON,
        nullable=False,
        default=dict
    )
    # Ejemplo: {
    #   "completed_scenes": ["intro", "first_mission"],
    #   "unlocked_content": ["secret_1", "lore_piece_3"],
    #   "achievements": ["first_choice", "fast_responder"],
    #   "active_missions": ["mission_1"],
    #   "story_branches": {"branch_a": true}
    # }

    # Relaciones con personajes (JSON)
    relationship_scores = Column(
        JSON,
        nullable=False,
        default=dict
    )
    # Ejemplo: {
    #   "diana": {"trust": 50, "respect": 30, "intimacy": 20},
    #   "lucien": {"trust": 40, "respect": 60, "intimacy": 10}
    # }

    # Arquetipo
    archetype = Column(
        Enum(ArchetypeType),
        nullable=True
    )
    archetype_confidence = Column(
        Float,
        nullable=False,
        default=0.0
    )

    # Estadisticas
    total_decisions = Column(Integer, nullable=False, default=0)
    total_interactions = Column(Integer, nullable=False, default=0)

    # Timestamps
    last_interaction = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relaciones SQLAlchemy
    user = relationship("User", uselist=False, lazy="selectin")
    decisions = relationship(
        "UserDecision",
        back_populates="narrative_state",
        cascade="all, delete-orphan"
    )
    behavior_patterns = relationship(
        "UserBehaviorPattern",
        back_populates="narrative_state",
        cascade="all, delete-orphan"
    )

    # Indices
    __table_args__ = (
        Index('idx_narrative_level_archetype', 'current_level', 'archetype'),
        Index('idx_narrative_last_interaction', 'last_interaction'),
    )

    # === Helper Methods ===

    def get_flag(self, flag_name: str) -> Any:
        """Obtiene un flag especifico."""
        return self.narrative_flags.get(flag_name)

    def set_flag(self, flag_name: str, value: Any) -> None:
        """Establece un flag (requiere commit)."""
        if self.narrative_flags is None:
            self.narrative_flags = {}
        self.narrative_flags[flag_name] = value

    def has_flag(self, flag_name: str) -> bool:
        """Verifica si tiene un flag."""
        if self.narrative_flags is None:
            return False
        return flag_name in self.narrative_flags

    def add_to_list_flag(self, flag_name: str, value: str) -> None:
        """Agrega valor a un flag tipo lista."""
        if self.narrative_flags is None:
            self.narrative_flags = {}
        if flag_name not in self.narrative_flags:
            self.narrative_flags[flag_name] = []
        if value not in self.narrative_flags[flag_name]:
            self.narrative_flags[flag_name].append(value)

    def get_relationship_score(
        self,
        character: str,
        attribute: str = "trust"
    ) -> int:
        """Obtiene score de relacion con personaje."""
        if self.relationship_scores is None:
            return 0
        char_scores = self.relationship_scores.get(character, {})
        return char_scores.get(attribute, 0)

    def update_relationship_score(
        self,
        character: str,
        attribute: str,
        delta: int
    ) -> int:
        """
        Actualiza score de relacion (requiere commit).

        Args:
            character: Nombre del personaje
            attribute: Atributo (trust, respect, intimacy)
            delta: Cambio (+/-)

        Returns:
            Nuevo valor del score
        """
        if self.relationship_scores is None:
            self.relationship_scores = {}
        if character not in self.relationship_scores:
            self.relationship_scores[character] = {}

        current = self.relationship_scores[character].get(attribute, 0)
        new_value = max(0, min(100, current + delta))  # Clamp 0-100
        self.relationship_scores[character][attribute] = new_value

        return new_value

    def can_access_level(self, required_level: int) -> bool:
        """Verifica si puede acceder a un nivel."""
        return self.current_level >= required_level

    def __repr__(self) -> str:
        return (
            f"<UserNarrativeState(user_id={self.user_id}, "
            f"level={self.current_level}, archetype={self.archetype})>"
        )


class UserDecision(Base):
    """
    Registro de decisiones del usuario.

    Cada decision se registra con:
    - Contexto (escena, capitulo)
    - Tipo de decision
    - Valor elegido
    - Tiempo de respuesta (para analisis de patrones)

    Attributes:
        id: ID unico
        user_id: ID del usuario
        narrative_state_id: FK al estado narrativo
        scene_id: ID de la escena donde se tomo
        chapter_id: ID del capitulo (opcional)
        decision_type: Tipo de decision (timing/content/reaction)
        decision_key: Identificador de la decision
        decision_value: Valor elegido
        alternatives: JSON con alternativas disponibles
        response_time_seconds: Tiempo para decidir
        context_data: JSON con contexto adicional
        created_at: Cuando se tomo la decision
    """
    __tablename__ = "user_decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Usuario
    user_id = Column(BigInteger, nullable=False, index=True)

    # FK al estado narrativo
    narrative_state_id = Column(
        Integer,
        ForeignKey("user_narrative_state.id"),
        nullable=False
    )

    # Contexto
    scene_id = Column(Integer, nullable=True)
    chapter_id = Column(Integer, nullable=True)
    dialogue_id = Column(Integer, nullable=True)

    # Decision
    decision_type = Column(
        Enum(DecisionType),
        nullable=False
    )
    decision_key = Column(String(100), nullable=False)  # ej: "first_choice"
    decision_value = Column(String(500), nullable=False)  # lo que eligio

    # Alternativas disponibles (para analisis)
    alternatives = Column(JSON, nullable=True)
    # Ejemplo: ["option_a", "option_b", "option_c"]

    # Timing
    response_time_seconds = Column(Float, nullable=True)

    # Contexto adicional
    context_data = Column(JSON, nullable=True)
    # Ejemplo: {
    #   "trigger": "button_click",
    #   "previous_scene": "intro",
    #   "user_level_at_time": 2
    # }

    # Timestamp
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relaciones
    narrative_state = relationship(
        "UserNarrativeState",
        back_populates="decisions"
    )

    # Indices
    __table_args__ = (
        Index('idx_decision_user_created', 'user_id', 'created_at'),
        Index('idx_decision_type_key', 'decision_type', 'decision_key'),
        Index('idx_decision_scene', 'scene_id', 'created_at'),
    )

    def __repr__(self) -> str:
        return (
            f"<UserDecision(user={self.user_id}, "
            f"type={self.decision_type}, key={self.decision_key})>"
        )


class UserBehaviorPattern(Base):
    """
    Patrones de comportamiento agregados del usuario.

    Se calculan periodicamente analizando las decisiones:
    - Tiempo promedio de respuesta
    - Consistencia en elecciones
    - Tendencias de comportamiento

    Attributes:
        id: ID unico
        user_id: ID del usuario
        narrative_state_id: FK al estado narrativo
        pattern_type: Tipo de patron detectado
        confidence_score: Confianza en la deteccion (0.0-1.0)
        sample_size: Numero de decisiones analizadas
        pattern_data: JSON con metricas del patron
        active: Si el patron sigue activo
        detected_at: Cuando se detecto
        updated_at: Ultima actualizacion
    """
    __tablename__ = "user_behavior_patterns"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Usuario
    user_id = Column(BigInteger, nullable=False, index=True)

    # FK al estado narrativo
    narrative_state_id = Column(
        Integer,
        ForeignKey("user_narrative_state.id"),
        nullable=False
    )

    # Patron
    pattern_type = Column(
        Enum(PatternType),
        nullable=False
    )
    confidence_score = Column(Float, nullable=False, default=0.0)
    sample_size = Column(Integer, nullable=False, default=0)

    # Datos del patron (metricas)
    pattern_data = Column(JSON, nullable=True)
    # Ejemplo para "impulsive": {
    #   "avg_response_time": 2.3,
    #   "quick_decisions_ratio": 0.85,
    #   "variance": 1.2
    # }

    # Estado
    active = Column(Boolean, nullable=False, default=True)

    # Timestamps
    detected_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relaciones
    narrative_state = relationship(
        "UserNarrativeState",
        back_populates="behavior_patterns"
    )

    # Indices
    __table_args__ = (
        Index('idx_pattern_user_type', 'user_id', 'pattern_type'),
        Index('idx_pattern_active', 'active', 'confidence_score'),
    )

    def is_significant(self, threshold: float = 0.7) -> bool:
        """Verifica si el patron es significativo."""
        return self.confidence_score >= threshold and self.sample_size >= 10

    def __repr__(self) -> str:
        return (
            f"<UserBehaviorPattern(user={self.user_id}, "
            f"type={self.pattern_type}, confidence={self.confidence_score:.2f})>"
        )


class NarrativeConsequence(Base):
    """
    Consecuencias predefinidas basadas en patrones de decision.

    Define que pasa cuando un usuario cumple ciertas condiciones:
    - Desbloquear contenido
    - Modificar relaciones
    - Cambiar flujo narrativo

    Attributes:
        id: ID unico
        name: Nombre descriptivo
        description: Descripcion de la consecuencia
        decision_pattern: JSON con condiciones a evaluar
        consequence_type: Tipo de consecuencia
        consequence_data: JSON con datos de la consecuencia
        priority: Prioridad de evaluacion (mayor = primero)
        active: Si esta activa
        created_at: Fecha de creacion
    """
    __tablename__ = "narrative_consequences"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Identificacion
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    # Condiciones (JSON)
    decision_pattern = Column(JSON, nullable=False)
    # Ejemplo: {
    #   "level": {">=": 3},
    #   "trust_diana": {">=": 50},
    #   "pattern": "patient",
    #   "flags": {"has": "completed_first_mission"},
    #   "archetype": {"in": ["romantic", "introspective"]}
    # }

    # Consecuencia
    consequence_type = Column(
        Enum(ConsequenceType),
        nullable=False
    )
    consequence_data = Column(JSON, nullable=False)
    # Ejemplo para UNLOCK: {
    #   "content_id": "secret_scene_1",
    #   "notification": "Has desbloqueado una escena secreta!"
    # }

    # Configuracion
    priority = Column(Integer, nullable=False, default=0)
    active = Column(Boolean, nullable=False, default=True)
    one_time = Column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Indices
    __table_args__ = (
        Index('idx_consequence_type_active', 'consequence_type', 'active'),
        Index('idx_consequence_priority', 'priority'),
    )

    def __repr__(self) -> str:
        return (
            f"<NarrativeConsequence(name={self.name}, "
            f"type={self.consequence_type})>"
        )


class CharacterRelationship(Base):
    """
    Relaciones detalladas usuario-personaje.

    Extiende los scores basicos con historial y eventos.

    Attributes:
        id: ID unico
        user_id: ID del usuario
        character_id: ID del personaje (FK a storyboard_characters)
        character_name: Nombre del personaje (denormalizado para queries)
        trust_level: Nivel de confianza (0-100)
        respect_level: Nivel de respeto (0-100)
        intimacy_level: Nivel de intimidad (0-100)
        interaction_count: Numero de interacciones
        milestone_events: JSON con eventos importantes
        current_status: Estado actual de la relacion
        last_interaction: Ultima interaccion
    """
    __tablename__ = "character_relationships"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Usuario
    user_id = Column(BigInteger, nullable=False, index=True)

    # Personaje
    character_id = Column(Integer, nullable=True)  # FK opcional a storyboard
    character_name = Column(String(50), nullable=False)

    # Scores
    trust_level = Column(Integer, nullable=False, default=0)
    respect_level = Column(Integer, nullable=False, default=0)
    intimacy_level = Column(Integer, nullable=False, default=0)

    # Estadisticas
    interaction_count = Column(Integer, nullable=False, default=0)

    # Eventos importantes (JSON)
    milestone_events = Column(JSON, nullable=False, default=list)
    # Ejemplo: [
    #   {"event": "first_meeting", "date": "2024-01-01", "impact": 10},
    #   {"event": "completed_mission_together", "date": "2024-01-05", "impact": 20}
    # ]

    # Estado
    current_status = Column(String(50), nullable=False, default="neutral")
    # Estados: "neutral", "friendly", "close", "intimate", "conflicted"

    # Timestamps
    last_interaction = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Indices
    __table_args__ = (
        Index('idx_relationship_user_char', 'user_id', 'character_name', unique=True),
        Index('idx_relationship_levels', 'trust_level', 'intimacy_level'),
    )

    @property
    def overall_score(self) -> int:
        """Score general de la relacion (promedio ponderado)."""
        return int(
            (self.trust_level * 0.4) +
            (self.respect_level * 0.3) +
            (self.intimacy_level * 0.3)
        )

    def add_milestone(self, event: str, impact: int) -> None:
        """Agrega un evento importante."""
        if self.milestone_events is None:
            self.milestone_events = []
        self.milestone_events.append({
            "event": event,
            "date": datetime.utcnow().isoformat(),
            "impact": impact
        })

    def __repr__(self) -> str:
        return (
            f"<CharacterRelationship(user={self.user_id}, "
            f"character={self.character_name}, overall={self.overall_score})>"
        )


class AppliedConsequence(Base):
    """
    Registro de consecuencias aplicadas a usuarios.

    Evita aplicar la misma consecuencia multiples veces.

    Attributes:
        id: ID unico
        user_id: ID del usuario
        consequence_id: FK a la consecuencia
        applied_at: Cuando se aplico
        result_data: JSON con resultado de aplicacion
    """
    __tablename__ = "applied_consequences"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(BigInteger, nullable=False, index=True)
    consequence_id = Column(
        Integer,
        ForeignKey("narrative_consequences.id"),
        nullable=False
    )

    applied_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    result_data = Column(JSON, nullable=True)

    # Relacion
    consequence = relationship("NarrativeConsequence", lazy="selectin")

    # Indice compuesto para evitar duplicados
    __table_args__ = (
        Index(
            'idx_applied_user_consequence',
            'user_id', 'consequence_id',
            unique=True
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<AppliedConsequence(user={self.user_id}, "
            f"consequence={self.consequence_id})>"
        )
```

---

## 2. SERVICE LAYER

### 2.1 NarrativeService Interface

**File:** `bot/narrative/services/narrative_service.py`

```python
"""
NarrativeService - Servicio central del sistema narrativo.

Responsabilidades:
- Gestionar estado narrativo de usuarios
- Registrar y analizar decisiones
- Detectar patrones de comportamiento
- Evaluar condiciones y aplicar consecuencias
- Gestionar relaciones con personajes

Patron: Service Layer con Dependency Injection
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from statistics import mean, stdev

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.narrative.database.models import (
    UserNarrativeState,
    UserDecision,
    UserBehaviorPattern,
    NarrativeConsequence,
    CharacterRelationship,
    AppliedConsequence
)
from bot.narrative.database.enums import (
    DecisionType, PatternType, ConsequenceType, ArchetypeType
)

logger = logging.getLogger(__name__)


class NarrativeService:
    """
    Servicio principal para gestion de narrativa.

    Ejemplo de uso:
        container = ServiceContainer(session, bot)
        state = await container.narrative.get_user_state(user_id)
        await container.narrative.record_decision(
            user_id=user_id,
            scene_id=1,
            decision_type=DecisionType.CONTENT,
            decision_key="first_choice",
            decision_value="option_a",
            response_time=3.5
        )
    """

    # === Thresholds de configuracion ===
    PATTERN_MIN_SAMPLES = 10
    PATTERN_CONFIDENCE_THRESHOLD = 0.7
    IMPULSIVE_TIME_THRESHOLD = 3.0  # segundos
    PATIENT_TIME_THRESHOLD = 15.0  # segundos
    ARCHETYPE_MIN_DECISIONS = 20

    def __init__(self, session: AsyncSession):
        """
        Inicializa el servicio.

        Args:
            session: Sesion de base de datos SQLAlchemy async
        """
        self.session = session
        logger.debug("NarrativeService inicializado")

    # =========================================
    # USER STATE MANAGEMENT
    # =========================================

    async def get_user_state(
        self,
        user_id: int,
        create_if_missing: bool = True
    ) -> Optional[UserNarrativeState]:
        """
        Obtiene el estado narrativo de un usuario.

        Si no existe y create_if_missing=True, crea uno nuevo
        con valores por defecto.

        Args:
            user_id: ID de Telegram del usuario
            create_if_missing: Crear estado si no existe

        Returns:
            UserNarrativeState o None si no existe y no crear
        """
        result = await self.session.execute(
            select(UserNarrativeState)
            .where(UserNarrativeState.user_id == user_id)
            .options(
                selectinload(UserNarrativeState.decisions),
                selectinload(UserNarrativeState.behavior_patterns)
            )
        )
        state = result.scalar_one_or_none()

        if state is None and create_if_missing:
            state = UserNarrativeState(
                user_id=user_id,
                current_level=1,
                narrative_flags={
                    "completed_scenes": [],
                    "unlocked_content": [],
                    "achievements": [],
                    "active_missions": []
                },
                relationship_scores={},
                total_decisions=0,
                total_interactions=0
            )
            self.session.add(state)
            await self.session.flush()
            logger.info(f"Nuevo estado narrativo creado para user {user_id}")

        return state

    async def update_user_level(
        self,
        user_id: int,
        new_level: int
    ) -> UserNarrativeState:
        """
        Actualiza el nivel narrativo del usuario.

        Args:
            user_id: ID del usuario
            new_level: Nuevo nivel (1-6)

        Returns:
            Estado actualizado

        Raises:
            ValueError: Si nivel invalido
        """
        if not 1 <= new_level <= 6:
            raise ValueError(f"Nivel invalido: {new_level}. Debe ser 1-6")

        state = await self.get_user_state(user_id)
        old_level = state.current_level
        state.current_level = new_level

        if new_level > old_level:
            state.add_to_list_flag("achievements", f"reached_level_{new_level}")
            logger.info(
                f"Usuario {user_id} subio de nivel: {old_level} -> {new_level}"
            )

        return state

    async def set_current_scene(
        self,
        user_id: int,
        scene_id: int,
        chapter_id: Optional[int] = None
    ) -> UserNarrativeState:
        """
        Establece la escena actual del usuario.

        Args:
            user_id: ID del usuario
            scene_id: ID de la escena
            chapter_id: ID del capitulo (opcional)

        Returns:
            Estado actualizado
        """
        state = await self.get_user_state(user_id)
        state.current_scene_id = scene_id
        if chapter_id:
            state.current_chapter_id = chapter_id
        state.last_interaction = datetime.utcnow()
        state.total_interactions += 1

        return state

    # =========================================
    # DECISION RECORDING
    # =========================================

    async def record_decision(
        self,
        user_id: int,
        scene_id: Optional[int],
        decision_type: DecisionType,
        decision_key: str,
        decision_value: str,
        response_time: Optional[float] = None,
        alternatives: Optional[List[str]] = None,
        context_data: Optional[Dict] = None
    ) -> UserDecision:
        """
        Registra una decision del usuario.

        Cada decision se almacena para:
        - Analisis de patrones
        - Deteccion de arquetipo
        - Aplicacion de consecuencias

        Args:
            user_id: ID del usuario
            scene_id: ID de la escena (puede ser None)
            decision_type: Tipo de decision
            decision_key: Identificador unico de la decision
            decision_value: Valor/opcion elegida
            response_time: Tiempo de respuesta en segundos
            alternatives: Lista de alternativas disponibles
            context_data: Datos adicionales de contexto

        Returns:
            UserDecision creada
        """
        state = await self.get_user_state(user_id)

        decision = UserDecision(
            user_id=user_id,
            narrative_state_id=state.id,
            scene_id=scene_id,
            chapter_id=state.current_chapter_id,
            decision_type=decision_type,
            decision_key=decision_key,
            decision_value=decision_value,
            response_time_seconds=response_time,
            alternatives=alternatives,
            context_data=context_data or {
                "user_level_at_time": state.current_level,
                "archetype_at_time": state.archetype.value if state.archetype else None
            }
        )

        self.session.add(decision)

        # Actualizar contadores
        state.total_decisions += 1
        state.last_interaction = datetime.utcnow()

        logger.debug(
            f"Decision registrada: user={user_id}, "
            f"key={decision_key}, value={decision_value}"
        )

        return decision

    async def get_user_decisions(
        self,
        user_id: int,
        limit: int = 100,
        decision_type: Optional[DecisionType] = None,
        since: Optional[datetime] = None
    ) -> List[UserDecision]:
        """
        Obtiene historial de decisiones del usuario.

        Args:
            user_id: ID del usuario
            limit: Maximo de resultados
            decision_type: Filtrar por tipo
            since: Solo decisiones desde esta fecha

        Returns:
            Lista de decisiones ordenadas por fecha desc
        """
        query = (
            select(UserDecision)
            .where(UserDecision.user_id == user_id)
            .order_by(UserDecision.created_at.desc())
            .limit(limit)
        )

        if decision_type:
            query = query.where(UserDecision.decision_type == decision_type)

        if since:
            query = query.where(UserDecision.created_at >= since)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    # =========================================
    # PATTERN ANALYSIS
    # =========================================

    async def analyze_patterns(
        self,
        user_id: int,
        force_update: bool = False
    ) -> List[UserBehaviorPattern]:
        """
        Analiza y detecta patrones de comportamiento del usuario.

        Analiza:
        - Tiempo de respuesta (impulsive vs patient)
        - Consistencia en elecciones
        - Tendencias de exploracion

        Args:
            user_id: ID del usuario
            force_update: Forzar re-analisis aunque existan patrones

        Returns:
            Lista de patrones detectados
        """
        state = await self.get_user_state(user_id)

        # Verificar si necesita analisis
        if not force_update:
            existing = await self._get_active_patterns(user_id)
            if existing and state.total_decisions < self.PATTERN_MIN_SAMPLES * 2:
                return existing

        # Obtener decisiones recientes
        decisions = await self.get_user_decisions(
            user_id,
            limit=100,
            since=datetime.utcnow() - timedelta(days=30)
        )

        if len(decisions) < self.PATTERN_MIN_SAMPLES:
            logger.debug(
                f"Insuficientes decisiones para analizar "
                f"({len(decisions)}/{self.PATTERN_MIN_SAMPLES})"
            )
            return []

        detected_patterns = []

        # Analizar timing
        timing_pattern = await self._analyze_timing_pattern(
            state, decisions
        )
        if timing_pattern:
            detected_patterns.append(timing_pattern)

        # Analizar consistencia
        consistency_pattern = await self._analyze_consistency_pattern(
            state, decisions
        )
        if consistency_pattern:
            detected_patterns.append(consistency_pattern)

        logger.info(
            f"Patrones detectados para user {user_id}: "
            f"{[p.pattern_type.value for p in detected_patterns]}"
        )

        return detected_patterns

    async def _analyze_timing_pattern(
        self,
        state: UserNarrativeState,
        decisions: List[UserDecision]
    ) -> Optional[UserBehaviorPattern]:
        """Analiza patron de timing (impulsive/patient)."""
        timed_decisions = [
            d for d in decisions
            if d.response_time_seconds is not None
        ]

        if len(timed_decisions) < self.PATTERN_MIN_SAMPLES:
            return None

        times = [d.response_time_seconds for d in timed_decisions]
        avg_time = mean(times)
        time_variance = stdev(times) if len(times) > 1 else 0

        # Determinar patron
        if avg_time <= self.IMPULSIVE_TIME_THRESHOLD:
            pattern_type = PatternType.IMPULSIVE
            quick_ratio = sum(1 for t in times if t <= 3) / len(times)
            confidence = min(0.95, quick_ratio)
        elif avg_time >= self.PATIENT_TIME_THRESHOLD:
            pattern_type = PatternType.PATIENT
            slow_ratio = sum(1 for t in times if t >= 10) / len(times)
            confidence = min(0.95, slow_ratio)
        else:
            return None  # No pattern detected

        # Crear o actualizar patron
        pattern = await self._upsert_pattern(
            state=state,
            pattern_type=pattern_type,
            confidence=confidence,
            sample_size=len(timed_decisions),
            pattern_data={
                "avg_response_time": round(avg_time, 2),
                "variance": round(time_variance, 2),
                "sample_count": len(timed_decisions)
            }
        )

        return pattern

    async def _analyze_consistency_pattern(
        self,
        state: UserNarrativeState,
        decisions: List[UserDecision]
    ) -> Optional[UserBehaviorPattern]:
        """Analiza consistencia en elecciones."""
        # Agrupar por decision_key
        decision_groups: Dict[str, List[str]] = {}
        for d in decisions:
            if d.decision_key not in decision_groups:
                decision_groups[d.decision_key] = []
            decision_groups[d.decision_key].append(d.decision_value)

        # Calcular consistencia
        consistencies = []
        for key, values in decision_groups.items():
            if len(values) >= 2:
                # Frecuencia del valor mas comun
                most_common = max(set(values), key=values.count)
                consistency = values.count(most_common) / len(values)
                consistencies.append(consistency)

        if not consistencies:
            return None

        avg_consistency = mean(consistencies)

        if avg_consistency >= 0.8:
            pattern_type = PatternType.CONSISTENT
            confidence = avg_consistency
        elif avg_consistency <= 0.4:
            pattern_type = PatternType.ERRATIC
            confidence = 1 - avg_consistency
        else:
            return None

        pattern = await self._upsert_pattern(
            state=state,
            pattern_type=pattern_type,
            confidence=confidence,
            sample_size=len(decisions),
            pattern_data={
                "avg_consistency": round(avg_consistency, 2),
                "decision_groups_analyzed": len(decision_groups)
            }
        )

        return pattern

    async def _upsert_pattern(
        self,
        state: UserNarrativeState,
        pattern_type: PatternType,
        confidence: float,
        sample_size: int,
        pattern_data: Dict
    ) -> UserBehaviorPattern:
        """Crea o actualiza un patron de comportamiento."""
        # Buscar existente
        result = await self.session.execute(
            select(UserBehaviorPattern)
            .where(
                UserBehaviorPattern.user_id == state.user_id,
                UserBehaviorPattern.pattern_type == pattern_type
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.confidence_score = confidence
            existing.sample_size = sample_size
            existing.pattern_data = pattern_data
            existing.active = True
            return existing

        pattern = UserBehaviorPattern(
            user_id=state.user_id,
            narrative_state_id=state.id,
            pattern_type=pattern_type,
            confidence_score=confidence,
            sample_size=sample_size,
            pattern_data=pattern_data,
            active=True
        )
        self.session.add(pattern)

        return pattern

    async def _get_active_patterns(
        self,
        user_id: int
    ) -> List[UserBehaviorPattern]:
        """Obtiene patrones activos del usuario."""
        result = await self.session.execute(
            select(UserBehaviorPattern)
            .where(
                UserBehaviorPattern.user_id == user_id,
                UserBehaviorPattern.active == True
            )
        )
        return list(result.scalars().all())

    # =========================================
    # ARCHETYPE DETECTION
    # =========================================

    async def detect_archetype(
        self,
        user_id: int
    ) -> Optional[ArchetypeType]:
        """
        Detecta el arquetipo del usuario basado en patrones y decisiones.

        Arquetipos se basan en:
        - Patrones de comportamiento
        - Preferencias de contenido
        - Interacciones con personajes

        Args:
            user_id: ID del usuario

        Returns:
            ArchetypeType detectado o None si insuficientes datos
        """
        state = await self.get_user_state(user_id)

        if state.total_decisions < self.ARCHETYPE_MIN_DECISIONS:
            logger.debug(
                f"Insuficientes decisiones para detectar arquetipo: "
                f"{state.total_decisions}/{self.ARCHETYPE_MIN_DECISIONS}"
            )
            return None

        # Obtener patrones
        patterns = await self._get_active_patterns(user_id)
        pattern_types = {p.pattern_type: p.confidence_score for p in patterns}

        # Obtener decisiones recientes
        decisions = await self.get_user_decisions(user_id, limit=50)

        # Calcular scores por arquetipo
        archetype_scores: Dict[ArchetypeType, float] = {
            ArchetypeType.ROMANTIC: 0.0,
            ArchetypeType.ADVENTURER: 0.0,
            ArchetypeType.COLLECTOR: 0.0,
            ArchetypeType.INTROSPECTIVE: 0.0,
            ArchetypeType.SOCIAL: 0.0,
            ArchetypeType.ACHIEVER: 0.0
        }

        # Factor 1: Patrones de comportamiento
        if PatternType.PATIENT in pattern_types:
            archetype_scores[ArchetypeType.INTROSPECTIVE] += 0.3
            archetype_scores[ArchetypeType.ROMANTIC] += 0.2

        if PatternType.IMPULSIVE in pattern_types:
            archetype_scores[ArchetypeType.ADVENTURER] += 0.3

        if PatternType.CONSISTENT in pattern_types:
            archetype_scores[ArchetypeType.ACHIEVER] += 0.2

        if PatternType.EXPLORATORY in pattern_types:
            archetype_scores[ArchetypeType.COLLECTOR] += 0.4
            archetype_scores[ArchetypeType.ADVENTURER] += 0.2

        # Factor 2: Relaciones con personajes
        relationship_scores = state.relationship_scores or {}
        total_intimacy = sum(
            char.get("intimacy", 0)
            for char in relationship_scores.values()
        )
        if total_intimacy > 100:
            archetype_scores[ArchetypeType.ROMANTIC] += 0.3

        total_trust = sum(
            char.get("trust", 0)
            for char in relationship_scores.values()
        )
        if total_trust > 150:
            archetype_scores[ArchetypeType.SOCIAL] += 0.3

        # Factor 3: Contenido desbloqueado
        unlocked = state.get_flag("unlocked_content") or []
        if len(unlocked) > 10:
            archetype_scores[ArchetypeType.COLLECTOR] += 0.3

        # Factor 4: Logros
        achievements = state.get_flag("achievements") or []
        if len(achievements) > 5:
            archetype_scores[ArchetypeType.ACHIEVER] += 0.3

        # Seleccionar arquetipo con mayor score
        best_archetype = max(archetype_scores, key=archetype_scores.get)
        confidence = archetype_scores[best_archetype]

        if confidence >= 0.3:  # Threshold minimo
            state.archetype = best_archetype
            state.archetype_confidence = min(0.95, confidence)

            logger.info(
                f"Arquetipo detectado para user {user_id}: "
                f"{best_archetype.value} (confidence={confidence:.2f})"
            )

            return best_archetype

        return None

    # =========================================
    # DIALOGUE & CONTENT RETRIEVAL
    # =========================================

    async def get_next_dialogue(
        self,
        user_id: int,
        trigger: str
    ) -> Optional[Dict]:
        """
        Obtiene el siguiente dialogo basado en trigger y estado del usuario.

        Evalua condiciones del dialogo contra el estado del usuario.

        Args:
            user_id: ID del usuario
            trigger: Trigger que activa el dialogo

        Returns:
            Dict con datos del dialogo o None si no hay match
        """
        state = await self.get_user_state(user_id)

        # Buscar dialogos con este trigger
        # (Integracion con storyboard existente)
        from docs.storyboard import storyboard_manager

        dialogue = storyboard_manager.find_dialogue_by_trigger(
            trigger, user_id
        )

        if dialogue is None:
            return None

        # Verificar condiciones
        conditions = dialogue.get("conditions", {})
        if not await self.check_conditions(user_id, conditions):
            return None

        return dialogue

    async def check_unlock_conditions(
        self,
        user_id: int,
        content_id: str
    ) -> bool:
        """
        Verifica si el usuario puede acceder a contenido especifico.

        Args:
            user_id: ID del usuario
            content_id: ID del contenido

        Returns:
            True si puede acceder, False si no
        """
        state = await self.get_user_state(user_id)

        # Verificar si ya desbloqueado
        unlocked = state.get_flag("unlocked_content") or []
        if content_id in unlocked:
            return True

        # Buscar consecuencia de unlock para este contenido
        result = await self.session.execute(
            select(NarrativeConsequence)
            .where(
                NarrativeConsequence.consequence_type == ConsequenceType.UNLOCK,
                NarrativeConsequence.active == True
            )
        )
        consequences = result.scalars().all()

        for consequence in consequences:
            data = consequence.consequence_data or {}
            if data.get("content_id") == content_id:
                # Verificar condiciones
                if await self.check_conditions(
                    user_id,
                    consequence.decision_pattern
                ):
                    return True

        return False

    # =========================================
    # CONDITION EVALUATION
    # =========================================

    async def check_conditions(
        self,
        user_id: int,
        conditions: Dict[str, Any]
    ) -> bool:
        """
        Evalua un conjunto de condiciones contra el estado del usuario.

        Condiciones soportadas:
        - "level": {">=": 3} - Nivel narrativo
        - "trust_diana": {">=": 50} - Score de relacion
        - "pattern": "patient" - Patron de comportamiento
        - "flags": {"has": "flag_name"} - Flags narrativos
        - "archetype": {"in": ["romantic"]} - Arquetipo
        - "decisions": {"count": {">=": 10}} - Conteo decisiones

        Args:
            user_id: ID del usuario
            conditions: Dict de condiciones a evaluar

        Returns:
            True si todas las condiciones se cumplen
        """
        if not conditions:
            return True

        state = await self.get_user_state(user_id)
        evaluator = ConditionEvaluator(state, self)

        return await evaluator.evaluate_all(conditions)

    # =========================================
    # RELATIONSHIP MANAGEMENT
    # =========================================

    async def update_relationship(
        self,
        user_id: int,
        character: str,
        attribute: str,
        delta: int
    ) -> int:
        """
        Actualiza la relacion del usuario con un personaje.

        Args:
            user_id: ID del usuario
            character: Nombre del personaje
            attribute: Atributo (trust, respect, intimacy)
            delta: Cambio (+/-)

        Returns:
            Nuevo valor del atributo
        """
        state = await self.get_user_state(user_id)
        new_value = state.update_relationship_score(character, attribute, delta)

        # Actualizar CharacterRelationship detallada
        result = await self.session.execute(
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
                character_name=character
            )
            self.session.add(relationship)

        # Actualizar atributo
        if attribute == "trust":
            relationship.trust_level = new_value
        elif attribute == "respect":
            relationship.respect_level = new_value
        elif attribute == "intimacy":
            relationship.intimacy_level = new_value

        relationship.interaction_count += 1
        relationship.last_interaction = datetime.utcnow()

        # Actualizar status basado en overall score
        overall = relationship.overall_score
        if overall >= 80:
            relationship.current_status = "intimate"
        elif overall >= 60:
            relationship.current_status = "close"
        elif overall >= 40:
            relationship.current_status = "friendly"
        else:
            relationship.current_status = "neutral"

        logger.debug(
            f"Relacion actualizada: user={user_id}, "
            f"character={character}, {attribute}={new_value}"
        )

        return new_value

    async def get_character_relationship(
        self,
        user_id: int,
        character: str
    ) -> Optional[CharacterRelationship]:
        """Obtiene la relacion detallada con un personaje."""
        result = await self.session.execute(
            select(CharacterRelationship)
            .where(
                CharacterRelationship.user_id == user_id,
                CharacterRelationship.character_name == character
            )
        )
        return result.scalar_one_or_none()

    # =========================================
    # CONSEQUENCE APPLICATION
    # =========================================

    async def apply_pending_consequences(
        self,
        user_id: int
    ) -> List[Dict]:
        """
        Evalua y aplica consecuencias pendientes para el usuario.

        Busca consecuencias activas cuyas condiciones se cumplan
        y que no hayan sido aplicadas previamente.

        Args:
            user_id: ID del usuario

        Returns:
            Lista de consecuencias aplicadas con sus resultados
        """
        state = await self.get_user_state(user_id)
        applied_results = []

        # Obtener consecuencias activas ordenadas por prioridad
        result = await self.session.execute(
            select(NarrativeConsequence)
            .where(NarrativeConsequence.active == True)
            .order_by(NarrativeConsequence.priority.desc())
        )
        consequences = result.scalars().all()

        for consequence in consequences:
            # Verificar si ya fue aplicada (para one_time)
            if consequence.one_time:
                already_applied = await self._check_consequence_applied(
                    user_id, consequence.id
                )
                if already_applied:
                    continue

            # Evaluar condiciones
            if not await self.check_conditions(
                user_id,
                consequence.decision_pattern
            ):
                continue

            # Aplicar consecuencia
            result_data = await self._apply_consequence(
                state, consequence
            )

            # Registrar aplicacion
            if consequence.one_time:
                applied = AppliedConsequence(
                    user_id=user_id,
                    consequence_id=consequence.id,
                    result_data=result_data
                )
                self.session.add(applied)

            applied_results.append({
                "consequence_id": consequence.id,
                "name": consequence.name,
                "type": consequence.consequence_type.value,
                "result": result_data
            })

            logger.info(
                f"Consecuencia aplicada: user={user_id}, "
                f"consequence={consequence.name}"
            )

        return applied_results

    async def _check_consequence_applied(
        self,
        user_id: int,
        consequence_id: int
    ) -> bool:
        """Verifica si una consecuencia ya fue aplicada."""
        result = await self.session.execute(
            select(AppliedConsequence)
            .where(
                AppliedConsequence.user_id == user_id,
                AppliedConsequence.consequence_id == consequence_id
            )
        )
        return result.scalar_one_or_none() is not None

    async def _apply_consequence(
        self,
        state: UserNarrativeState,
        consequence: NarrativeConsequence
    ) -> Dict:
        """Aplica una consecuencia especifica."""
        data = consequence.consequence_data
        result = {}

        if consequence.consequence_type == ConsequenceType.UNLOCK:
            content_id = data.get("content_id")
            if content_id:
                state.add_to_list_flag("unlocked_content", content_id)
                result["unlocked"] = content_id
                result["notification"] = data.get("notification")

        elif consequence.consequence_type == ConsequenceType.MODIFY:
            if "level_change" in data:
                state.current_level = min(6, max(1,
                    state.current_level + data["level_change"]
                ))
                result["new_level"] = state.current_level

            if "flag_set" in data:
                for flag, value in data["flag_set"].items():
                    state.set_flag(flag, value)
                result["flags_set"] = list(data["flag_set"].keys())

        elif consequence.consequence_type == ConsequenceType.RELATIONSHIP:
            character = data.get("character")
            changes = data.get("changes", {})
            for attr, delta in changes.items():
                new_val = state.update_relationship_score(
                    character, attr, delta
                )
                result[f"{character}_{attr}"] = new_val

        elif consequence.consequence_type == ConsequenceType.BRANCH:
            branch_id = data.get("branch_id")
            if branch_id:
                state.set_flag(f"story_branch_{branch_id}", True)
                result["branch_activated"] = branch_id

        elif consequence.consequence_type == ConsequenceType.REWARD:
            # Integracion con sistema de gamificacion
            if "besitos" in data:
                result["besitos_awarded"] = data["besitos"]
            if "achievement" in data:
                state.add_to_list_flag("achievements", data["achievement"])
                result["achievement_unlocked"] = data["achievement"]

        return result


# =========================================
# CONDITION EVALUATOR
# =========================================

class ConditionEvaluator:
    """
    Evaluador flexible de condiciones narrativas.

    Soporta multiples operadores y tipos de condicion.

    Ejemplo de condiciones:
        {
            "level": {">=": 3},
            "trust_diana": {">=": 50},
            "pattern": "patient",
            "flags": {"has": "completed_first_mission"},
            "archetype": {"in": ["romantic", "introspective"]},
            "decisions": {"count": {">=": 10}}
        }
    """

    def __init__(
        self,
        state: UserNarrativeState,
        service: NarrativeService
    ):
        self.state = state
        self.service = service

    async def evaluate_all(self, conditions: Dict[str, Any]) -> bool:
        """Evalua todas las condiciones (AND logico)."""
        for key, condition in conditions.items():
            if not await self._evaluate_single(key, condition):
                return False
        return True

    async def _evaluate_single(
        self,
        key: str,
        condition: Any
    ) -> bool:
        """Evalua una condicion individual."""

        # Nivel narrativo
        if key == "level":
            return self._compare_numeric(
                self.state.current_level,
                condition
            )

        # Relaciones con personajes (trust_diana, respect_lucien, etc)
        if key.startswith(("trust_", "respect_", "intimacy_")):
            parts = key.split("_", 1)
            attribute = parts[0]
            character = parts[1]
            value = self.state.get_relationship_score(character, attribute)
            return self._compare_numeric(value, condition)

        # Patron de comportamiento
        if key == "pattern":
            patterns = await self.service._get_active_patterns(
                self.state.user_id
            )
            pattern_types = [p.pattern_type.value for p in patterns]
            if isinstance(condition, str):
                return condition in pattern_types
            elif isinstance(condition, dict) and "in" in condition:
                return any(p in condition["in"] for p in pattern_types)
            return False

        # Flags narrativos
        if key == "flags":
            return self._evaluate_flags(condition)

        # Arquetipo
        if key == "archetype":
            if self.state.archetype is None:
                return False
            archetype_value = self.state.archetype.value
            if isinstance(condition, str):
                return archetype_value == condition
            elif isinstance(condition, dict) and "in" in condition:
                return archetype_value in condition["in"]
            return False

        # Conteo de decisiones
        if key == "decisions":
            return self._compare_numeric(
                self.state.total_decisions,
                condition.get("count", condition)
            )

        # Escena completada
        if key == "completed_scene":
            completed = self.state.get_flag("completed_scenes") or []
            return condition in completed

        # Contenido desbloqueado
        if key == "unlocked":
            unlocked = self.state.get_flag("unlocked_content") or []
            return condition in unlocked

        # Achievement
        if key == "achievement":
            achievements = self.state.get_flag("achievements") or []
            return condition in achievements

        logger.warning(f"Condicion desconocida: {key}")
        return True  # Condiciones desconocidas pasan por defecto

    def _compare_numeric(
        self,
        value: int,
        condition: Any
    ) -> bool:
        """Compara valor numerico con condicion."""
        if isinstance(condition, int):
            return value == condition

        if isinstance(condition, dict):
            for op, target in condition.items():
                if op == ">=" and value < target:
                    return False
                if op == ">" and value <= target:
                    return False
                if op == "<=" and value > target:
                    return False
                if op == "<" and value >= target:
                    return False
                if op == "==" and value != target:
                    return False
                if op == "!=" and value == target:
                    return False

        return True

    def _evaluate_flags(self, condition: Dict) -> bool:
        """Evalua condiciones de flags."""
        if "has" in condition:
            flag_name = condition["has"]
            return self.state.has_flag(flag_name)

        if "has_all" in condition:
            for flag in condition["has_all"]:
                if not self.state.has_flag(flag):
                    return False
            return True

        if "has_any" in condition:
            for flag in condition["has_any"]:
                if self.state.has_flag(flag):
                    return True
            return False

        if "not_has" in condition:
            flag_name = condition["not_has"]
            return not self.state.has_flag(flag_name)

        return True
```

---

## 3. SERVICE CONTAINER INTEGRATION

**File:** `bot/services/container.py` (add to existing)

```python
    # ===== NARRATIVE SERVICE =====

    @property
    def narrative(self):
        """
        Service de gestion narrativa.

        Se carga lazy (solo en primer acceso).

        Returns:
            NarrativeService: Instancia del service
        """
        if self._narrative_service is None:
            from bot.narrative.services.narrative_service import NarrativeService
            logger.debug("Lazy loading: NarrativeService")
            self._narrative_service = NarrativeService(self._session)

        return self._narrative_service
```

---

## 4. HANDLER INTEGRATION EXAMPLES

### 4.1 Integration with /start Handler

**File:** `bot/handlers/user/start.py` (modifications)

```python
from bot.narrative.database.enums import DecisionType


async def cmd_start(message: Message, session: AsyncSession) -> None:
    """
    Handler /start con integracion narrativa.

    Detecta deep links de tokens y estado narrativo del usuario.
    """
    user_id = message.from_user.id
    container = ServiceContainer(session, message.bot)

    # Obtener o crear estado narrativo
    narrative_state = await container.narrative.get_user_state(user_id)

    # Registrar interaccion inicial
    await container.narrative.record_decision(
        user_id=user_id,
        scene_id=None,
        decision_type=DecisionType.CONTENT,
        decision_key="bot_start",
        decision_value="initiated",
        context_data={"source": "start_command"}
    )

    # Verificar rol y estado
    if Config.is_admin(user_id):
        await _send_admin_welcome(message, container)
    elif await container.subscription.is_vip_active(user_id):
        await _send_vip_welcome(message, container, narrative_state)
    else:
        await _send_user_welcome(message, container, narrative_state)

    # Aplicar consecuencias pendientes (si hay)
    applied = await container.narrative.apply_pending_consequences(user_id)
    if applied:
        for consequence in applied:
            if consequence.get("result", {}).get("notification"):
                await message.answer(
                    consequence["result"]["notification"],
                    parse_mode="HTML"
                )


async def _send_user_welcome(
    message: Message,
    container: ServiceContainer,
    state: UserNarrativeState
) -> None:
    """Envia bienvenida personalizada segun estado narrativo."""
    level = state.current_level
    archetype = state.archetype

    if level == 1:
        # Usuario nuevo - narrativa de introduccion
        dialogue = await container.narrative.get_next_dialogue(
            message.from_user.id,
            trigger="first_welcome"
        )
        if dialogue:
            await message.answer(
                dialogue["message"],
                parse_mode="HTML"
            )
            return

    # Usuarios recurrentes - mensaje personalizado por arquetipo
    welcome_messages = {
        "romantic": "Es bueno verte de nuevo... te extrane.",
        "adventurer": "Listo para una nueva aventura?",
        "collector": "Hay nuevos secretos esperandote.",
        "introspective": "Bienvenido de vuelta a tu espacio.",
        "achiever": "Tienes nuevos logros por desbloquear!",
    }

    msg = welcome_messages.get(
        archetype.value if archetype else None,
        "Bienvenido de vuelta!"
    )

    await message.answer(msg, parse_mode="HTML")
```

### 4.2 Callback Handler with Decision Recording

```python
from datetime import datetime

# Almacenar timestamp cuando se muestra la pregunta
user_decision_timestamps: Dict[int, datetime] = {}


@router.callback_query(F.data.startswith("choice:"))
async def handle_narrative_choice(
    callback: CallbackQuery,
    session: AsyncSession
) -> None:
    """
    Handler para elecciones narrativas.

    Callback data format: "choice:{scene_id}:{choice_key}:{value}"
    """
    user_id = callback.from_user.id
    container = ServiceContainer(session, callback.bot)

    # Parsear callback data
    parts = callback.data.split(":")
    scene_id = int(parts[1])
    choice_key = parts[2]
    choice_value = parts[3]

    # Calcular tiempo de respuesta
    response_time = None
    if user_id in user_decision_timestamps:
        delta = datetime.utcnow() - user_decision_timestamps[user_id]
        response_time = delta.total_seconds()
        del user_decision_timestamps[user_id]

    # Registrar decision
    await container.narrative.record_decision(
        user_id=user_id,
        scene_id=scene_id,
        decision_type=DecisionType.CONTENT,
        decision_key=choice_key,
        decision_value=choice_value,
        response_time=response_time,
        alternatives=["option_a", "option_b", "option_c"]  # Obtener de scene
    )

    # Actualizar escena
    await container.narrative.set_current_scene(user_id, scene_id)

    # Obtener siguiente dialogo basado en eleccion
    next_dialogue = await container.narrative.get_next_dialogue(
        user_id,
        trigger=f"after_{choice_key}_{choice_value}"
    )

    if next_dialogue:
        # Ejecutar acciones del dialogo
        actions = next_dialogue.get("actions", {})
        await _execute_dialogue_actions(container, user_id, actions)

        # Mostrar siguiente mensaje
        await callback.message.edit_text(
            next_dialogue["message"],
            parse_mode="HTML",
            reply_markup=_build_choice_keyboard(next_dialogue)
        )

    # Analizar patrones periodicamente
    state = await container.narrative.get_user_state(user_id)
    if state.total_decisions % 10 == 0:
        await container.narrative.analyze_patterns(user_id)
        await container.narrative.detect_archetype(user_id)

    await callback.answer()


async def _execute_dialogue_actions(
    container: ServiceContainer,
    user_id: int,
    actions: Dict
) -> None:
    """Ejecuta acciones de un dialogo."""
    if "relationship" in actions:
        for character, changes in actions["relationship"].items():
            for attr, delta in changes.items():
                await container.narrative.update_relationship(
                    user_id, character, attr, delta
                )

    if "unlock" in actions:
        state = await container.narrative.get_user_state(user_id)
        state.add_to_list_flag("unlocked_content", actions["unlock"])

    if "level_up" in actions:
        state = await container.narrative.get_user_state(user_id)
        await container.narrative.update_user_level(
            user_id, state.current_level + 1
        )
```

---

## 5. MIGRATION SQL

**File:** `alembic/versions/006_add_narrative_system.py`

```python
"""Add narrative system tables

Revision ID: 006_narrative_system
Revises: 005_add_custom_reactions_system
Create Date: 2024-XX-XX

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers
revision = '006_narrative_system'
down_revision = '005_add_custom_reactions_system'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # === ENUMS (SQLite usa strings) ===
    # narrative_level, decision_type, pattern_type, consequence_type, archetype_type

    # === USER NARRATIVE STATE ===
    op.create_table(
        'user_narrative_state',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('current_level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('current_scene_id', sa.Integer(), nullable=True),
        sa.Column('current_chapter_id', sa.Integer(), nullable=True),
        sa.Column('narrative_flags', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('relationship_scores', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('archetype', sa.String(50), nullable=True),
        sa.Column('archetype_confidence', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_decisions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_interactions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_interaction', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_narrative_user_id', 'user_narrative_state', ['user_id'], unique=True)
    op.create_index('idx_narrative_level_archetype', 'user_narrative_state', ['current_level', 'archetype'])
    op.create_index('idx_narrative_last_interaction', 'user_narrative_state', ['last_interaction'])

    # === USER DECISIONS ===
    op.create_table(
        'user_decisions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('narrative_state_id', sa.Integer(), nullable=False),
        sa.Column('scene_id', sa.Integer(), nullable=True),
        sa.Column('chapter_id', sa.Integer(), nullable=True),
        sa.Column('dialogue_id', sa.Integer(), nullable=True),
        sa.Column('decision_type', sa.String(20), nullable=False),
        sa.Column('decision_key', sa.String(100), nullable=False),
        sa.Column('decision_value', sa.String(500), nullable=False),
        sa.Column('alternatives', sa.JSON(), nullable=True),
        sa.Column('response_time_seconds', sa.Float(), nullable=True),
        sa.Column('context_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['narrative_state_id'], ['user_narrative_state.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_decision_user_created', 'user_decisions', ['user_id', 'created_at'])
    op.create_index('idx_decision_type_key', 'user_decisions', ['decision_type', 'decision_key'])
    op.create_index('idx_decision_scene', 'user_decisions', ['scene_id', 'created_at'])

    # === USER BEHAVIOR PATTERNS ===
    op.create_table(
        'user_behavior_patterns',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('narrative_state_id', sa.Integer(), nullable=False),
        sa.Column('pattern_type', sa.String(30), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('sample_size', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('pattern_data', sa.JSON(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('detected_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['narrative_state_id'], ['user_narrative_state.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_pattern_user_type', 'user_behavior_patterns', ['user_id', 'pattern_type'])
    op.create_index('idx_pattern_active', 'user_behavior_patterns', ['active', 'confidence_score'])

    # === NARRATIVE CONSEQUENCES ===
    op.create_table(
        'narrative_consequences',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('decision_pattern', sa.JSON(), nullable=False),
        sa.Column('consequence_type', sa.String(30), nullable=False),
        sa.Column('consequence_data', sa.JSON(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('one_time', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('idx_consequence_type_active', 'narrative_consequences', ['consequence_type', 'active'])
    op.create_index('idx_consequence_priority', 'narrative_consequences', ['priority'])

    # === CHARACTER RELATIONSHIPS ===
    op.create_table(
        'character_relationships',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=True),
        sa.Column('character_name', sa.String(50), nullable=False),
        sa.Column('trust_level', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('respect_level', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('intimacy_level', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('interaction_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('milestone_events', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('current_status', sa.String(50), nullable=False, server_default="'neutral'"),
        sa.Column('last_interaction', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_relationship_user_char', 'character_relationships', ['user_id', 'character_name'], unique=True)
    op.create_index('idx_relationship_levels', 'character_relationships', ['trust_level', 'intimacy_level'])

    # === APPLIED CONSEQUENCES ===
    op.create_table(
        'applied_consequences',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('consequence_id', sa.Integer(), nullable=False),
        sa.Column('applied_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('result_data', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['consequence_id'], ['narrative_consequences.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_applied_user_consequence', 'applied_consequences', ['user_id', 'consequence_id'], unique=True)


def downgrade() -> None:
    op.drop_table('applied_consequences')
    op.drop_table('character_relationships')
    op.drop_table('narrative_consequences')
    op.drop_table('user_behavior_patterns')
    op.drop_table('user_decisions')
    op.drop_table('user_narrative_state')
```

---

## 6. SEED DATA SCRIPT

**File:** `scripts/seed_narrative_consequences.py`

```python
"""
Script para crear consecuencias narrativas predeterminadas.

Ejecutar:
    python scripts/seed_narrative_consequences.py
"""
import asyncio
import sys
sys.path.insert(0, '.')

from bot.database.engine import get_session, init_db
from bot.narrative.database.models import NarrativeConsequence
from bot.narrative.database.enums import ConsequenceType


async def seed_consequences():
    """Crea consecuencias narrativas iniciales."""
    await init_db()

    async with get_session() as session:
        consequences = [
            # === UNLOCK CONSEQUENCES ===
            NarrativeConsequence(
                name="unlock_secret_scene_1",
                description="Desbloquea primera escena secreta al alcanzar nivel 3 con confianza Diana",
                decision_pattern={
                    "level": {">=": 3},
                    "trust_diana": {">=": 50}
                },
                consequence_type=ConsequenceType.UNLOCK,
                consequence_data={
                    "content_id": "secret_scene_1",
                    "notification": "Has desbloqueado una escena secreta con Diana!"
                },
                priority=10,
                one_time=True
            ),
            NarrativeConsequence(
                name="unlock_lucien_backstory",
                description="Desbloquea historia de fondo de Lucien",
                decision_pattern={
                    "level": {">=": 4},
                    "respect_lucien": {">=": 60},
                    "pattern": {"in": ["patient", "consistent"]}
                },
                consequence_type=ConsequenceType.UNLOCK,
                consequence_data={
                    "content_id": "lucien_backstory",
                    "notification": "Lucien decide compartir su historia contigo..."
                },
                priority=10,
                one_time=True
            ),

            # === RELATIONSHIP CONSEQUENCES ===
            NarrativeConsequence(
                name="patient_bonus_diana",
                description="Bonus de relacion con Diana para usuarios pacientes",
                decision_pattern={
                    "pattern": "patient",
                    "decisions": {"count": {">=": 20}}
                },
                consequence_type=ConsequenceType.RELATIONSHIP,
                consequence_data={
                    "character": "diana",
                    "changes": {"trust": 10, "intimacy": 5}
                },
                priority=5,
                one_time=True
            ),

            # === BRANCH CONSEQUENCES ===
            NarrativeConsequence(
                name="romantic_path_unlock",
                description="Desbloquea rama romantica para arquetipos romanticos",
                decision_pattern={
                    "archetype": {"in": ["romantic"]},
                    "intimacy_diana": {">=": 40}
                },
                consequence_type=ConsequenceType.BRANCH,
                consequence_data={
                    "branch_id": "romantic_diana",
                    "notification": "Se ha desbloqueado un nuevo camino..."
                },
                priority=15,
                one_time=True
            ),

            # === REWARD CONSEQUENCES ===
            NarrativeConsequence(
                name="first_mission_reward",
                description="Recompensa por completar primera mision",
                decision_pattern={
                    "flags": {"has": "completed_first_mission"}
                },
                consequence_type=ConsequenceType.REWARD,
                consequence_data={
                    "besitos": 100,
                    "achievement": "mission_master"
                },
                priority=5,
                one_time=True
            ),

            # === LEVEL PROGRESSION ===
            NarrativeConsequence(
                name="auto_level_2",
                description="Auto level up al completar introduccion",
                decision_pattern={
                    "level": {"==": 1},
                    "completed_scene": "intro_complete",
                    "decisions": {"count": {">=": 5}}
                },
                consequence_type=ConsequenceType.MODIFY,
                consequence_data={
                    "level_change": 1,
                    "flag_set": {"intro_graduated": True}
                },
                priority=20,
                one_time=True
            )
        ]

        for consequence in consequences:
            session.add(consequence)

        await session.commit()
        print(f"Creadas {len(consequences)} consecuencias narrativas")


if __name__ == "__main__":
    asyncio.run(seed_consequences())
```

---

## 7. INTEGRATION SUMMARY

### Architecture Overview

```
User Interaction
      |
      v
+------------------+
|  Telegram Bot    |
|  (aiogram 3.x)   |
+------------------+
      |
      v
+------------------+
| Handler Layer    |
| - start.py       |
| - choices.py     |
| - reactions.py   |
+------------------+
      |
      v
+------------------+
| ServiceContainer |
| (DI + Lazy Load) |
+------------------+
      |
      +---> NarrativeService
      |         |
      |         +---> ConditionEvaluator
      |         +---> PatternAnalyzer
      |         +---> ArchetypeDetector
      |
      +---> SubscriptionService
      +---> ChannelService
      +---> ConfigService
      |
      v
+------------------+
| Database Layer   |
| (SQLAlchemy)     |
+------------------+
      |
      v
+------------------+
| SQLite WAL Mode  |
+------------------+
```

### Data Flow for Decision

```
1. User clicks choice button
      |
2. Handler parses callback_data
      |
3. Calculate response_time from stored timestamp
      |
4. Call narrative.record_decision()
      |
5. Update user state (scene, interactions)
      |
6. Every N decisions: analyze_patterns()
      |
7. Every M decisions: detect_archetype()
      |
8. Check and apply_pending_consequences()
      |
9. Get next_dialogue based on trigger
      |
10. Execute dialogue actions (relationships, unlocks)
      |
11. Render next message with choices
```

### Key Integration Points

| Component | Integration |
|-----------|-------------|
| `/start` | Get/create narrative state, record interaction |
| Callback handlers | Record decisions with timing |
| Message handlers | Pattern detection triggers |
| Background tasks | Periodic pattern analysis, consequence checks |
| Storyboard system | Dialogue conditions use NarrativeService |
| Gamification | Besitos rewards via consequences |

---

## 8. TESTING RECOMMENDATIONS

### Unit Tests

```python
# tests/test_narrative_service.py

@pytest.mark.asyncio
async def test_get_user_state_creates_new():
    """Test que se crea estado para usuario nuevo."""
    state = await service.get_user_state(user_id=12345)
    assert state is not None
    assert state.current_level == 1
    assert state.total_decisions == 0

@pytest.mark.asyncio
async def test_record_decision_updates_counters():
    """Test que record_decision incrementa contadores."""
    await service.record_decision(
        user_id=12345,
        scene_id=1,
        decision_type=DecisionType.CONTENT,
        decision_key="test",
        decision_value="a"
    )
    state = await service.get_user_state(12345)
    assert state.total_decisions == 1

@pytest.mark.asyncio
async def test_condition_evaluator_level():
    """Test evaluacion de condicion de nivel."""
    state = UserNarrativeState(current_level=3)
    evaluator = ConditionEvaluator(state, service)

    assert await evaluator._evaluate_single("level", {">=": 3})
    assert await evaluator._evaluate_single("level", {">=": 2})
    assert not await evaluator._evaluate_single("level", {">=": 4})

@pytest.mark.asyncio
async def test_pattern_detection_impulsive():
    """Test deteccion de patron impulsivo."""
    # Crear decisiones con tiempos rapidos
    for i in range(15):
        await service.record_decision(
            user_id=12345,
            scene_id=1,
            decision_type=DecisionType.CONTENT,
            decision_key=f"choice_{i}",
            decision_value="quick",
            response_time=1.5  # < 3 seconds
        )

    patterns = await service.analyze_patterns(12345)
    pattern_types = [p.pattern_type for p in patterns]
    assert PatternType.IMPULSIVE in pattern_types
```

---

## 9. FINAL NOTES

### Performance Considerations

1. **Indexes**: All query-heavy columns have indexes
2. **Lazy Loading**: Services load only when needed
3. **JSON columns**: Use for flexible schema without joins
4. **Batch operations**: Pattern analysis processes multiple decisions

### Security Considerations

1. **User isolation**: All queries filter by user_id
2. **Input validation**: Decision values are limited length
3. **No raw SQL**: Uses SQLAlchemy ORM exclusively

### Extensibility

1. **New patterns**: Add to PatternType enum
2. **New conditions**: Extend ConditionEvaluator
3. **New consequences**: Add ConsequenceType cases
4. **New archetypes**: Update detection logic

This architecture maintains the creative intent of the narrative system while providing a robust, scalable technical foundation.
