"""
Modelos de base de datos para el sistema narrativo.

Tablas:
- user_narrative_state: Estado de progresión narrativa del usuario
- user_decisions: Historial de decisiones del usuario
- user_behavior_patterns: Patrones de comportamiento detectados
- narrative_consequences: Definición de consecuencias
- applied_consequences: Consecuencias aplicadas a usuarios
- character_relationships: Relaciones usuario-personaje
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime,
    BigInteger, JSON, ForeignKey, Index, Float, Enum, Text
)
from sqlalchemy.orm import relationship

from bot.database.base import Base
from bot.database.enums import (
    NarrativeLevel, DecisionType, PatternType,
    ArchetypeType, ConsequenceType, RelationshipState
)

logger = logging.getLogger(__name__)


class UserNarrativeState(Base):
    """
    Estado de progresión narrativa del usuario.

    Almacena:
    - Nivel actual y escena
    - Puntuaciones de relación (Diana, Lucien)
    - Puntuaciones de arquetipo (4 dimensiones)
    - Flags narrativos (contenido desbloqueado/bloqueado)
    - Historial de decisiones resumido
    """
    __tablename__ = "user_narrative_state"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        BigInteger,
        ForeignKey("users.user_id"),
        unique=True,
        nullable=False,
        index=True
    )

    # Progresión
    current_level = Column(Integer, default=1, nullable=False)
    current_scene_id = Column(String(100), nullable=True)
    current_chapter_id = Column(String(100), nullable=True)

    # Relaciones con personajes (0-100)
    diana_trust = Column(Integer, default=0, nullable=False)
    lucien_respect = Column(Integer, default=0, nullable=False)
    intimacy_level = Column(Integer, default=0, nullable=False)

    # Arquetipos (0-100 cada uno, multidimensional)
    archetype_introspective = Column(Integer, default=0, nullable=False)
    archetype_direct = Column(Integer, default=0, nullable=False)
    archetype_romantic = Column(Integer, default=0, nullable=False)
    archetype_analytical = Column(Integer, default=0, nullable=False)

    # Arquetipo detectado (primario y secundario)
    primary_archetype = Column(
        Enum(ArchetypeType),
        nullable=True
    )
    secondary_archetype = Column(
        Enum(ArchetypeType),
        nullable=True
    )

    # Métricas de comportamiento
    response_speed_avg = Column(Float, default=0.0, nullable=False)  # Segundos promedio
    participation_rate = Column(Float, default=0.0, nullable=False)  # 0.0-1.0
    consistency_score = Column(Integer, default=0, nullable=False)  # 0-100
    total_decisions = Column(Integer, default=0, nullable=False)

    # Flags narrativos (JSON)
    narrative_flags = Column(JSON, default=dict)
    # {
    #   "completed_scenes": ["intro", "first_test"],
    #   "unlocked_content": ["diana_photo_1", "lucien_backstory"],
    #   "blocked_content": {"aggressive_path": "48h"},
    #   "achievements": ["patient_user", "consistent_romantic"],
    #   "special_flags": ["first_impression_introspective"]
    # }

    # Historial resumido de decisiones (JSON)
    decision_summary = Column(JSON, default=dict)
    # {
    #   "first_choice": "introspective",
    #   "memorable_moments": [
    #     {"scene": "intro", "choice": "honest_response", "impact": "diana_trust+10"}
    #   ],
    #   "pattern_history": ["patient", "consistent"]
    # }

    # Timestamps
    last_interaction = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relaciones
    user = relationship("User", uselist=False, lazy="selectin")
    decisions = relationship(
        "UserDecision",
        back_populates="narrative_state",
        cascade="all, delete-orphan"
    )
    patterns = relationship(
        "UserBehaviorPattern",
        back_populates="narrative_state",
        cascade="all, delete-orphan"
    )

    # Índices
    __table_args__ = (
        Index('idx_narrative_level_archetype', 'current_level', 'primary_archetype'),
        Index('idx_narrative_last_interaction', 'last_interaction'),
    )

    # Propiedades calculadas
    @property
    def diana_state(self) -> RelationshipState:
        """Estado actual de relación con Diana."""
        if self.diana_trust >= 70:
            return RelationshipState.DIANA_VULNERABLE
        elif self.diana_trust >= 40:
            return RelationshipState.DIANA_REVEALING
        return RelationshipState.DIANA_MYSTERIOUS

    @property
    def lucien_state(self) -> RelationshipState:
        """Estado actual de relación con Lucien."""
        if self.lucien_respect >= 60:
            return RelationshipState.LUCIEN_TRUSTED
        elif self.lucien_respect >= 30:
            return RelationshipState.LUCIEN_WARMING
        return RelationshipState.LUCIEN_COLD

    @property
    def narrative_level(self) -> NarrativeLevel:
        """Nivel narrativo como enum."""
        return NarrativeLevel(self.current_level)

    @property
    def is_vip_content_accessible(self) -> bool:
        """Indica si el usuario puede acceder a contenido VIP."""
        return self.current_level >= 4

    def get_dominant_archetype(self) -> Optional[ArchetypeType]:
        """Retorna el arquetipo dominante basado en puntuaciones."""
        scores = {
            ArchetypeType.INTROSPECTIVE: self.archetype_introspective,
            ArchetypeType.DIRECT: self.archetype_direct,
            ArchetypeType.ROMANTIC: self.archetype_romantic,
            ArchetypeType.ANALYTICAL: self.archetype_analytical
        }
        if max(scores.values()) == 0:
            return None
        return max(scores, key=scores.get)

    def has_flag(self, flag_type: str, flag_name: str) -> bool:
        """Verifica si tiene un flag específico."""
        flags = self.narrative_flags or {}
        flag_list = flags.get(flag_type, [])
        if isinstance(flag_list, list):
            return flag_name in flag_list
        elif isinstance(flag_list, dict):
            return flag_name in flag_list
        return False

    def add_flag(self, flag_type: str, flag_name: str, value: Any = True) -> None:
        """Agrega un flag narrativo."""
        if self.narrative_flags is None:
            self.narrative_flags = {}

        if flag_type not in self.narrative_flags:
            self.narrative_flags[flag_type] = [] if value is True else {}

        if isinstance(self.narrative_flags[flag_type], list):
            if flag_name not in self.narrative_flags[flag_type]:
                self.narrative_flags[flag_type].append(flag_name)
        else:
            self.narrative_flags[flag_type][flag_name] = value

    def __repr__(self) -> str:
        return (
            f"<UserNarrativeState(user={self.user_id}, level={self.current_level}, "
            f"diana_trust={self.diana_trust}, lucien_respect={self.lucien_respect})>"
        )


class UserDecision(Base):
    """
    Registro de cada decisión narrativa del usuario.

    Almacena:
    - Contexto de la decisión (escena, punto de decisión)
    - Valor de la decisión
    - Tiempo de respuesta
    - Consecuencias inmediatas y diferidas
    """
    __tablename__ = "user_decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Relación con estado narrativo
    narrative_state_id = Column(
        Integer,
        ForeignKey("user_narrative_state.id"),
        nullable=False,
        index=True
    )
    user_id = Column(BigInteger, nullable=False, index=True)

    # Contexto de la decisión
    scene_id = Column(String(100), nullable=False)
    decision_point_id = Column(String(100), nullable=False)
    decision_type = Column(Enum(DecisionType), nullable=False)

    # Valor de la decisión
    decision_key = Column(String(100), nullable=False)  # Identificador de la opción
    decision_value = Column(Text, nullable=True)  # Valor completo (si aplica)

    # Timing
    presented_at = Column(DateTime, nullable=False)
    responded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    response_time_seconds = Column(Integer, nullable=False)

    # Categorización automática
    timing_category = Column(String(20), nullable=True)  # instant/considered/delayed/none
    detected_archetype = Column(Enum(ArchetypeType), nullable=True)

    # Consecuencias (JSON)
    immediate_consequences = Column(JSON, default=dict)
    # {
    #   "diana_trust": 5,
    #   "lucien_respect": -3,
    #   "archetype_introspective": 10,
    #   "next_scene": "cautious_path"
    # }

    delayed_consequences = Column(JSON, default=dict)
    # {
    #   "trigger_at_level": 3,
    #   "content_id": "diana_remembers_patience",
    #   "condition": {"diana_trust": {">=": 40}}
    # }

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones
    narrative_state = relationship("UserNarrativeState", back_populates="decisions")

    # Índices
    __table_args__ = (
        Index('idx_decision_user_created', 'user_id', 'created_at'),
        Index('idx_decision_type_key', 'decision_type', 'decision_key'),
        Index('idx_decision_scene', 'scene_id', 'created_at'),
    )

    @property
    def is_immediate(self) -> bool:
        """Indica si fue una respuesta inmediata (<30s)."""
        return self.response_time_seconds < 30

    @property
    def is_patient(self) -> bool:
        """Indica si fue una respuesta paciente (>5min)."""
        return self.response_time_seconds > 300

    def categorize_timing(self) -> str:
        """Categoriza el tiempo de respuesta."""
        if self.response_time_seconds < 30:
            return "instant"
        elif self.response_time_seconds < 300:
            return "considered"
        elif self.response_time_seconds < 3600:
            return "delayed"
        return "none"

    def __repr__(self) -> str:
        return (
            f"<UserDecision(user={self.user_id}, scene={self.scene_id}, "
            f"key={self.decision_key}, time={self.response_time_seconds}s)>"
        )


class UserBehaviorPattern(Base):
    """
    Patrones de comportamiento detectados del usuario.

    Los patrones se actualizan periódicamente basándose en
    el historial de decisiones.
    """
    __tablename__ = "user_behavior_patterns"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Relación
    narrative_state_id = Column(
        Integer,
        ForeignKey("user_narrative_state.id"),
        nullable=False,
        index=True
    )
    user_id = Column(BigInteger, nullable=False, index=True)

    # Patrón detectado
    pattern_type = Column(Enum(PatternType), nullable=False)
    confidence_score = Column(Float, default=0.0, nullable=False)  # 0.0-1.0
    sample_size = Column(Integer, default=0, nullable=False)  # Decisiones analizadas

    # Contexto del patrón
    first_detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_confirmed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    times_confirmed = Column(Integer, default=1, nullable=False)

    # Estado
    is_active = Column(Boolean, default=True, nullable=False)

    # Metadata adicional (JSON)
    pattern_data = Column(JSON, default=dict)
    # {
    #   "avg_response_time": 45.5,
    #   "dominant_choices": ["introspective", "patient"],
    #   "consistency_window": 10  # últimas N decisiones analizadas
    # }

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relaciones
    narrative_state = relationship("UserNarrativeState", back_populates="patterns")

    # Índices
    __table_args__ = (
        Index('idx_pattern_user_type', 'user_id', 'pattern_type'),
        Index('idx_pattern_active_confidence', 'is_active', 'confidence_score'),
    )

    @property
    def is_strong(self) -> bool:
        """Indica si es un patrón fuerte (>70% confianza, >10 muestras)."""
        return self.confidence_score >= 0.7 and self.sample_size >= 10

    def __repr__(self) -> str:
        return (
            f"<UserBehaviorPattern(user={self.user_id}, type={self.pattern_type.value}, "
            f"confidence={self.confidence_score:.2f})>"
        )


class NarrativeConsequence(Base):
    """
    Definición de consecuencias narrativas.

    Define qué sucede cuando se cumplen ciertas condiciones.
    Usado para:
    - Desbloquear contenido
    - Modificar diálogos
    - Cambiar ramas narrativas
    """
    __tablename__ = "narrative_consequences"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Identificación
    consequence_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Tipo y prioridad
    consequence_type = Column(Enum(ConsequenceType), nullable=False)
    priority = Column(Integer, default=0, nullable=False)  # Mayor = más prioritario

    # Condiciones para aplicar (JSON)
    conditions = Column(JSON, nullable=False)
    # {
    #   "level": {">=": 3},
    #   "diana_trust": {">=": 50},
    #   "pattern": "patient",
    #   "flags": {"has": "completed_first_mission"},
    #   "archetype": {"in": ["romantic", "introspective"]}
    # }

    # Efecto de la consecuencia (JSON)
    effect = Column(JSON, nullable=False)
    # {
    #   "unlock": "diana_secret_scene",
    #   "diana_trust": 10,
    #   "add_flag": {"type": "achievements", "name": "patience_master"},
    #   "dialogue": "diana_remembers_patience"
    # }

    # Cuándo se aplica
    trigger_scene = Column(String(100), nullable=True)  # Si es específico de escena
    trigger_level = Column(Integer, nullable=True)  # Si es específico de nivel
    is_one_time = Column(Boolean, default=True, nullable=False)  # Solo aplica una vez

    # Estado
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Índices
    __table_args__ = (
        Index('idx_consequence_type_active', 'consequence_type', 'is_active'),
        Index('idx_consequence_priority', 'priority'),
    )

    def __repr__(self) -> str:
        return (
            f"<NarrativeConsequence(id={self.consequence_id}, "
            f"type={self.consequence_type.value})>"
        )


class AppliedConsequence(Base):
    """
    Registro de consecuencias aplicadas a usuarios.

    Previene la aplicación duplicada de consecuencias one-time.
    """
    __tablename__ = "applied_consequences"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Relaciones
    user_id = Column(BigInteger, nullable=False, index=True)
    consequence_id = Column(
        String(100),
        ForeignKey("narrative_consequences.consequence_id"),
        nullable=False
    )

    # Cuándo se aplicó
    applied_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    applied_in_scene = Column(String(100), nullable=True)
    applied_at_level = Column(Integer, nullable=True)

    # Resultado (JSON)
    result = Column(JSON, default=dict)
    # {
    #   "effects_applied": ["diana_trust+10", "unlocked:secret_scene"],
    #   "user_state_before": {"diana_trust": 40},
    #   "user_state_after": {"diana_trust": 50}
    # }

    # Índices (único por usuario+consecuencia)
    __table_args__ = (
        Index('idx_applied_user_consequence', 'user_id', 'consequence_id', unique=True),
    )

    def __repr__(self) -> str:
        return (
            f"<AppliedConsequence(user={self.user_id}, "
            f"consequence={self.consequence_id})>"
        )


class CharacterRelationship(Base):
    """
    Relación detallada entre usuario y personaje.

    Almacena el historial de interacciones y momentos
    significativos con cada personaje.
    """
    __tablename__ = "character_relationships"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Usuario y personaje
    user_id = Column(BigInteger, nullable=False, index=True)
    character_name = Column(String(50), nullable=False)  # "diana" o "lucien"

    # Métricas de relación (0-100)
    trust_level = Column(Integer, default=0, nullable=False)
    respect_level = Column(Integer, default=0, nullable=False)
    intimacy_level = Column(Integer, default=0, nullable=False)
    familiarity_level = Column(Integer, default=0, nullable=False)

    # Estado actual
    current_state = Column(Enum(RelationshipState), nullable=True)

    # Historial de momentos significativos (JSON)
    milestone_events = Column(JSON, default=list)
    # [
    #   {"event": "first_meeting", "level": 1, "date": "2026-01-09"},
    #   {"event": "first_vulnerability", "level": 3, "trust_at_time": 45},
    #   {"event": "shared_secret", "level": 5, "content": "childhood_memory"}
    # ]

    # Primera impresión (nunca cambia)
    first_impression = Column(String(100), nullable=True)
    first_meeting_date = Column(DateTime, nullable=True)

    # Recuerdos específicos que el personaje tiene del usuario (JSON)
    character_memories = Column(JSON, default=list)
    # [
    #   {"type": "choice", "scene": "intro", "memory": "fue honesto sobre su incertidumbre"},
    #   {"type": "patience", "context": "esperó 24h", "impact": "positivo"}
    # ]

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Índices
    __table_args__ = (
        Index('idx_relationship_user_character', 'user_id', 'character_name', unique=True),
        Index('idx_relationship_levels', 'trust_level', 'respect_level'),
    )

    def add_memory(self, memory_type: str, content: str, context: Dict = None) -> None:
        """Agrega un recuerdo del personaje sobre el usuario."""
        if self.character_memories is None:
            self.character_memories = []

        memory = {
            "type": memory_type,
            "content": content,
            "date": datetime.utcnow().isoformat()
        }
        if context:
            memory["context"] = context

        self.character_memories.append(memory)

    def add_milestone(self, event: str, level: int, extra_data: Dict = None) -> None:
        """Agrega un evento significativo en la relación."""
        if self.milestone_events is None:
            self.milestone_events = []

        milestone = {
            "event": event,
            "level": level,
            "date": datetime.utcnow().isoformat()
        }
        if extra_data:
            milestone.update(extra_data)

        self.milestone_events.append(milestone)

    def __repr__(self) -> str:
        return (
            f"<CharacterRelationship(user={self.user_id}, "
            f"character={self.character_name}, trust={self.trust_level})>"
        )
