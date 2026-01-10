"""
Modelos de base de datos para el bot VIP/Free.

Tablas Core:
- bot_config: Configuración global del bot (singleton)
- users: Usuarios del sistema con roles (FREE/VIP/ADMIN)
- vip_subscribers: Suscriptores del canal VIP
- invitation_tokens: Tokens de invitación generados
- free_channel_requests: Solicitudes de acceso al canal Free
- subscription_plans: Planes de suscripción/tarifas configurables
- broadcast_messages: Mensajes de broadcasting con gamificación

Tablas Narrativa:
- story_fragments: Fragmentos de historia interactiva
- story_choices: Opciones de decisión en fragmentos
- user_narrative_progress: Progreso narrativo de usuarios
- user_choices: Registro de decisiones tomadas
- narrative_unlocks: Contenido desbloqueado por usuarios
- narrative_flags: Flags narrativos persistentes
- archetype_profiles: Perfiles de detección de personalidad
- character_relationships: Relaciones con personajes (Lucien, Diana)
- desire_profiles: Perfiles de Deseo (Level 3 - 7 preguntas psicológicas)
- channel_interactions: Tracking de observaciones en canales (Level 2)
"""
import logging
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text,
    BigInteger, JSON, ForeignKey, Index, Float, Enum
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from bot.database.base import Base
from bot.database.enums import UserRole

logger = logging.getLogger(__name__)


class BotConfig(Base):
    """
    Configuración global del bot (tabla singleton - solo 1 registro).

    Almacena:
    - IDs de canales VIP y Free
    - Configuración de tiempo de espera
    - Configuración de reacciones
    - Tarifas de suscripción
    """
    __tablename__ = "bot_config"

    id = Column(Integer, primary_key=True, default=1)

    # Canales
    vip_channel_id = Column(String(50), nullable=True)  # ID del canal VIP
    free_channel_id = Column(String(50), nullable=True)  # ID del canal Free

    # Configuración
    wait_time_minutes = Column(Integer, default=5)  # Tiempo espera Free

    # Mensaje de bienvenida Free (con variables: {user_name}, {channel_name}, {wait_time})
    free_welcome_message = Column(
        String(1000),
        nullable=True,
        default="Hola {user_name}, tu solicitud de acceso a {channel_name} ha sido registrada. Debes esperar {wait_time} minutos antes de ser aprobado."
    )

    # Reacciones (JSON arrays de emojis)
    vip_reactions = Column(JSON, default=list)   # ["👍", "❤️", "🔥"]
    free_reactions = Column(JSON, default=list)  # ["👍", "👎"]

    # Tarifas (JSON object)
    subscription_fees = Column(
        JSON,
        default=lambda: {"monthly": 10, "yearly": 100}
    )

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return (
            f"<BotConfig(vip={self.vip_channel_id}, "
            f"free={self.free_channel_id}, wait={self.wait_time_minutes}min)>"
        )


class User(Base):
    """
    Modelo de usuario del sistema.

    Representa un usuario que ha interactuado con el bot.
    Almacena información básica y su rol actual.

    Attributes:
        user_id: ID único de Telegram (Primary Key)
        username: Username de Telegram (puede ser None)
        first_name: Nombre del usuario
        last_name: Apellido (puede ser None)
        role: Rol actual del usuario (FREE/VIP/ADMIN)
        created_at: Fecha de primer contacto con el bot
        updated_at: Última actualización de datos

    Relaciones:
        vip_subscription: Suscripción VIP si existe
        free_requests: Solicitudes al canal Free
    """

    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
    role = Column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.FREE
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones (se definen después en VIPSubscriber y FreeChannelRequest)

    @property
    def full_name(self) -> str:
        """Retorna nombre completo del usuario."""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    @property
    def mention(self) -> str:
        """Retorna mention HTML del usuario."""
        return f'<a href="tg://user?id={self.user_id}">{self.full_name}</a>'

    @property
    def is_admin(self) -> bool:
        """Verifica si el usuario es admin."""
        return self.role == UserRole.ADMIN

    @property
    def is_vip(self) -> bool:
        """Verifica si el usuario es VIP."""
        return self.role == UserRole.VIP

    @property
    def is_free(self) -> bool:
        """Verifica si el usuario es Free."""
        return self.role == UserRole.FREE

    def __repr__(self) -> str:
        return (
            f"<User(user_id={self.user_id}, username='{self.username}', "
            f"role={self.role.value})>"
        )


class SubscriptionPlan(Base):
    """
    Modelo de planes de suscripción/tarifas.

    Representa un plan que el admin configura con nombre, duración y precio.
    Los tokens VIP se generan vinculados a un plan específico.

    Attributes:
        id: ID único del plan
        name: Nombre del plan (ej: "Plan Mensual", "Plan Anual")
        duration_days: Duración en días del plan
        price: Precio del plan (en USD u otra moneda)
        currency: Símbolo de moneda (default: "$")
        active: Si el plan está activo (visible para generar tokens)
        created_at: Fecha de creación
        created_by: User ID del admin que creó el plan

    Relaciones:
        tokens: Tokens generados con este plan
    """
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    duration_days = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False, default="$")
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(BigInteger, nullable=False)

    # Relación con tokens
    tokens = relationship(
        "InvitationToken",
        back_populates="plan",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<SubscriptionPlan(id={self.id}, name='{self.name}', "
            f"days={self.duration_days}, price={self.price})>"
        )


class InvitationToken(Base):
    """
    Tokens de invitación generados por administradores.

    Cada token:
    - Es único (16 caracteres alfanuméricos)
    - Tiene duración limitada (expira después de X horas)
    - Se marca como "usado" al ser canjeado
    - Registra quién lo generó y quién lo usó
    - Puede estar asociado a un plan de suscripción
    """
    __tablename__ = "invitation_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Token único
    token = Column(String(16), unique=True, nullable=False, index=True)

    # Generación
    generated_by = Column(BigInteger, nullable=False)  # User ID del admin
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration_hours = Column(Integer, default=24, nullable=False)  # Duración en horas

    # Uso
    used = Column(Boolean, default=False, nullable=False, index=True)
    used_by = Column(BigInteger, nullable=True)  # User ID que canjeó
    used_at = Column(DateTime, nullable=True)

    # Plan asociado (nullable para compatibilidad con tokens antiguos)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=True)
    plan = relationship("SubscriptionPlan", back_populates="tokens")

    # Relación: 1 Token → Many Subscribers
    subscribers = relationship(
        "VIPSubscriber",
        back_populates="token",
        cascade="all, delete-orphan"
    )

    # Índice compuesto para queries de tokens no usados
    __table_args__ = (
        Index('idx_token_used_created', 'used', 'created_at'),
    )

    def is_expired(self) -> bool:
        """Verifica si el token ha expirado"""
        from datetime import timedelta
        expiry_time = self.created_at + timedelta(hours=self.duration_hours)
        return datetime.utcnow() > expiry_time

    def is_valid(self) -> bool:
        """Verifica si el token es válido (no usado y no expirado)"""
        return not self.used and not self.is_expired()

    def __repr__(self):
        status = "USADO" if self.used else ("EXPIRADO" if self.is_expired() else "VÁLIDO")
        return f"<Token({self.token[:8]}... - {status})>"


class VIPSubscriber(Base):
    """
    Suscriptores del canal VIP.

    Cada suscriptor:
    - Canjeó un token de invitación
    - Tiene fecha de expiración
    - Puede estar activo o expirado
    """
    __tablename__ = "vip_subscribers"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Usuario
    user_id = Column(BigInteger, ForeignKey("users.user_id"), unique=True, nullable=False, index=True)  # ID Telegram

    # Suscripción
    join_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    expiry_date = Column(DateTime, nullable=False)  # Fecha de expiración
    status = Column(
        String(20),
        default="active",
        nullable=False,
        index=True
    )  # "active" o "expired"

    # Token usado
    token_id = Column(Integer, ForeignKey("invitation_tokens.id"), nullable=False)
    token = relationship("InvitationToken", back_populates="subscribers")

    # Usuario (relación inversa)
    user = relationship("User", uselist=False, lazy="selectin")

    # Índice compuesto para buscar activos próximos a expirar
    __table_args__ = (
        Index('idx_status_expiry', 'status', 'expiry_date'),
    )

    def is_expired(self) -> bool:
        """Verifica si la suscripción ha expirado"""
        return datetime.utcnow() > self.expiry_date

    def days_remaining(self) -> int:
        """Retorna días restantes de suscripción (negativo si expirado)"""
        delta = self.expiry_date - datetime.utcnow()
        return delta.days

    def __repr__(self):
        days = self.days_remaining()
        return f"<VIPSubscriber(user={self.user_id}, status={self.status}, days={days})>"


class FreeChannelRequest(Base):
    """
    Solicitudes de acceso al canal Free (cola de espera).

    Cada solicitud:
    - Se crea cuando un usuario solicita acceso
    - Se procesa después de N minutos de espera
    - Se marca como "procesada" al enviar invitación
    """
    __tablename__ = "free_channel_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Usuario
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False, index=True)  # ID Telegram
    user = relationship("User", uselist=False, lazy="selectin")

    # Solicitud
    request_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed = Column(Boolean, default=False, nullable=False, index=True)
    processed_at = Column(DateTime, nullable=True)

    # Índice compuesto para queries de pendientes por fecha
    __table_args__ = (
        Index('idx_user_date', 'user_id', 'request_date'),
        Index('idx_processed_date', 'processed', 'request_date'),
    )

    def minutes_since_request(self) -> int:
        """Retorna minutos transcurridos desde la solicitud"""
        delta = datetime.utcnow() - self.request_date
        return int(delta.total_seconds() / 60)

    def is_ready(self, wait_time_minutes: int) -> bool:
        """Verifica si la solicitud cumplió el tiempo de espera"""
        return self.minutes_since_request() >= wait_time_minutes

    def __repr__(self):
        status = "PROCESADA" if self.processed else f"PENDIENTE ({self.minutes_since_request()}min)"
        return f"<FreeRequest(user={self.user_id}, {status})>"


class BroadcastMessage(Base):
    """
    Registro de mensajes de broadcasting enviados con gamificación.

    Cada registro:
    - Almacena información del mensaje enviado (texto, media)
    - Configuración de gamificación (botones de reacción)
    - Protección de contenido
    - Cache de estadísticas de reacciones
    """
    __tablename__ = "broadcast_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Identificación del mensaje
    message_id = Column(BigInteger, nullable=False)  # ID del mensaje en Telegram
    chat_id = Column(BigInteger, nullable=False)  # ID del canal donde se envió

    # Contenido
    content_type = Column(String(20), nullable=False)  # "text", "photo", "video"
    content_text = Column(String(4096), nullable=True)  # Texto del mensaje
    media_file_id = Column(String(200), nullable=True)  # File ID de Telegram (si es media)

    # Auditoría
    sent_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)  # Admin que envió
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Gamificación
    gamification_enabled = Column(Boolean, default=False, nullable=False)
    reaction_buttons = Column(JSON, default=list)  # Lista de configs: [{"emoji": "👍", "label": "...", "reaction_type_id": 1, "besitos": 10}]
    content_protected = Column(Boolean, default=False, nullable=False)  # Protección anti-forward

    # Cache de estadísticas
    total_reactions = Column(Integer, default=0, nullable=False)
    unique_reactors = Column(Integer, default=0, nullable=False)

    # Relación con usuario
    sender = relationship("User", uselist=False, lazy="selectin")

    # Índices para optimización
    __table_args__ = (
        Index('idx_chat_message', 'chat_id', 'message_id', unique=True),
        Index('idx_sent_at', 'sent_at'),
        Index('idx_gamification_enabled', 'gamification_enabled'),
    )

    def __repr__(self):
        return (
            f"<BroadcastMessage(id={self.id}, chat_id={self.chat_id}, "
            f"message_id={self.message_id}, gamification={self.gamification_enabled})>"
        )


# ==============================================================================
# MODELOS NARRATIVOS - Story System
# ==============================================================================

class StoryFragment(Base):
    """
    Fragmento de historia narrativa.

    Almacena contenido narrativo que puede ser:
    - Texto simple
    - Texto con imagen/vídeo
    - Diálogos de personajes (Diana, Lucien)
    - Fragmentos de ramificación con múltiples opciones

    Estructura de Niveles:
    - Niveles 1-3: Free (acceso libre)
    - Niveles 4-6: VIP (requiere suscripción activa)

    ID Convention: L{N}_{TYPE}_{NUMBER}
    Examples:
    - L1_INTRO_001: Level 1, Introduction, fragment 1
    - L4_DIVAN_015: Level 4, Diván, fragment 15
    - L6_FINAL_001: Level 6, Final, fragment 1
    """
    __tablename__ = "story_fragments"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Identificación única
    fragment_id = Column(String(50), unique=True, nullable=False, index=True)
    # Ej: "L1_INTRO_001", "L4_DIVAN_015"

    # Contenido Narrativo
    narrative_level = Column(Integer, nullable=False, index=True)  # 1-6
    title = Column(String(200), nullable=False)  # Ej: "Bienvenida a Los Kinkys"
    content_text = Column(Text, nullable=True)  # Texto del fragmento

    # Contenido multimedia (opcional)
    media_type = Column(String(20), nullable=True)  # "photo", "video", "audio", None
    media_file_id = Column(String(300), nullable=True)  # Telegram file_id
    media_url = Column(String(500), nullable=True)  # URL externa (backup)

    # Personaje hablante (si aplica)
    speaker = Column(String(50), nullable=True)  # "DIANA", "LUCIEN", "NARRATOR", None
    speaker_emotion = Column(String(50), nullable=True)  # "mysterious", "formal", "vulnerable"

    # Estructura del fragmento
    is_starting_fragment = Column(Boolean, default=False, nullable=False)
    is_ending_fragment = Column(Boolean, default=False, nullable=False)

    # Condiciones de desbloqueo (JSON)
    unlock_conditions = Column(JSON, nullable=True)
    # Example:
    # {
    #   "required_choices": ["L1_INTRO_A", "L1_INTRO_B"],
    #   "required_flags": ["met_diana", "completed_level_1"],
    #   "min_relationship_score": {
    #     "LUCIEN": 20,
    #     "DIANA": 10
    #   },
    #   "besitos_cost": 100,
    #   "required_items": ["mochila_viajero"]
    # }

    # Variantes de contenido basadas en arquetipo (JSON)
    content_variants = Column(JSON, nullable=True)
    # Example:
    # {
    #   "EXPLORER": "content_explorer_text",
    #   "ROMANTIC": "content_romantic_text",
    #   "DIRECT": "content_direct_text"
    # }

    # Metadatos de gamificación
    besitos_reward = Column(Integer, default=0, nullable=False)  # Besitos al completar
    experience_reward = Column(Integer, default=0, nullable=False)  # XP al completar
    unlocks_mission_id = Column(Integer, nullable=True)  # FK to missions
    unlocks_reward_id = Column(Integer, nullable=True)  # FK to rewards

    # Estado
    active = Column(Boolean, default=True, nullable=False, index=True)
    sort_order = Column(Integer, default=0, nullable=False)  # Orden en nivel

    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)

    # Relaciones
    choices = relationship(
        "StoryChoice",
        back_populates="fragment",
        foreign_keys="[StoryChoice.fragment_id]",
        cascade="all, delete-orphan",
        order_by="StoryChoice.sort_order"
    )

    # Índices
    __table_args__ = (
        Index('idx_fragment_level_active', 'narrative_level', 'active'),
        Index('idx_fragment_starting', 'is_starting_fragment', 'narrative_level'),
    )

    def __repr__(self):
        return f"<StoryFragment({self.fragment_id}, Level {self.narrative_level}, Speaker: {self.speaker})>"


class StoryChoice(Base):
    """
    Opción de decisión en un fragmento narrativo.

    Cada opción:
    - Tiene texto descriptivo
    - Lleva a un fragmento destino
    - Aplica consecuencias (flags, arquetipo, relaciones)
    - Puede tener requisitos para mostrarse
    """
    __tablename__ = "story_choices"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Identificación única
    choice_id = Column(String(50), unique=True, nullable=False, index=True)
    # Ej: "L1_INTRO_A", "L1_INTRO_B", "L4_DIVAN_ROMANTIC"

    # Relación con fragmento padre
    fragment_id = Column(Integer, ForeignKey("story_fragments.id"), nullable=False)
    fragment = relationship(
        "StoryFragment",
        back_populates="choices",
        foreign_keys=[fragment_id]
    )

    # Contenido de la opción
    choice_text = Column(String(300), nullable=False)  # Texto del botón
    choice_description = Column(Text, nullable=True)  # Descripción extendida (tooltip)

    # Destino
    target_fragment_id = Column(Integer, ForeignKey("story_fragments.id"), nullable=False)

    # Requisitos de visualización (JSON)
    display_requirements = Column(JSON, nullable=True)
    # Example:
    # {
    #   "required_flags": ["met_diana"],
    #   "min_level": 2,
    #   "required_archetype": "ROMANTIC",
    #   "min_besitos": 500
    # }

    # Consecuencias de elegir esta opción (JSON)
    consequences = Column(JSON, nullable=True)
    # Example:
    # {
    #   "flags_set": ["met_diana", "chose_romantic_path"],
    #   "flags_unset": ["first_interaction"],
    #   "archetype_points": {
    #     "romantic": +2,
    #     "direct": -1
    #   },
    #   "relationship_change": {
    #     "DIANA": +5,
    #     "LUCIEN": -2
    #   },
    #   "besitos_reward": 50,
    #   "items_gained": ["pista_1_mapa"],
    #   "items_lost": ["intro_map"],
    #   "mission_unlocked": 15
    # }

    # Configuración
    sort_order = Column(Integer, default=0, nullable=False)  # Orden de visualización
    active = Column(Boolean, default=True, nullable=False)

    # Metadatos
    is_destructive_choice = Column(Boolean, default=False)  # ¿Es irreversible?
    choice_emoji = Column(String(10), nullable=True)  # Ej: "🚪", "🔍", "💋"

    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Índices
    __table_args__ = (
        Index('idx_choice_fragment', 'fragment_id', 'sort_order'),
    )

    def __repr__(self):
        return f"<StoryChoice({self.choice_id} → {self.target_fragment_id})>"


class UserNarrativeProgress(Base):
    """
    Progreso narrativo del usuario.

    Rastrea:
    - Nivel actual y máximo alcanzado
    - Fragmentos completados
    - Niveles finalizados
    - Tiempos de dedicación
    """
    __tablename__ = "user_narrative_progress"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Usuario (1:1 relationship)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), unique=True, nullable=False, index=True)
    user = relationship("User", uselist=False, lazy="selectin")

    # Progreso actual
    current_fragment_id = Column(Integer, ForeignKey("story_fragments.id"), nullable=True)
    current_narrative_level = Column(Integer, default=1, nullable=False)
    max_narrative_level_reached = Column(Integer, default=1, nullable=False)

    # Fragmentos y niveles completados
    fragments_completed = Column(JSON, default=list)  # [fragment_id, fragment_id, ...]
    levels_completed = Column(JSON, default=list)  # [1, 2, 3, ...]

    # Estadísticas
    total_choices_made = Column(Integer, default=0, nullable=False)
    total_play_time_seconds = Column(Integer, default=0, nullable=False)
    total_rereads = Column(Integer, default=0, nullable=False)

    # Timestamps de nivel completado
    completed_level_1_at = Column(DateTime, nullable=True)
    completed_level_3_at = Column(DateTime, nullable=True)
    completed_level_6_at = Column(DateTime, nullable=True)

    # Estado
    last_played_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Logros específicos
    discovered_all_secrets = Column(Boolean, default=False)  # ¿Encontró todos los secretos?
    completed_perfect_run = Column(Boolean, default=False)  # ¿Nivel perfecto sin errores?

    # Índices
    __table_args__ = (
        Index('idx_progress_level', 'current_narrative_level'),
        Index('idx_progress_max_level', 'max_narrative_level_reached'),
    )

    @property
    def completion_percentage(self) -> float:
        """Porcentaje de niveles completados (1-6)"""
        return (len(self.levels_completed) / 6) * 100

    @property
    def is_vip_content_unlocked(self) -> bool:
        """¿Ha desbloqueado contenido VIP (nivel 4+)?"""
        return self.max_narrative_level_reached >= 4

    def __repr__(self):
        return f"<UserNarrativeProgress(user={self.user_id}, Level={self.current_narrative_level}/{self.max_narrative_level_reached})>"


class UserChoice(Base):
    """
    Registro de decisiones del usuario.

    Almacena cada elección para:
    - Análisis de comportamiento
    - Reconstitución del camino narrativo
    - Detección de arquetipos
    - Estadísticas y debugging
    """
    __tablename__ = "user_choices"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Usuario
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False, index=True)

    # Elección realizada
    choice_id = Column(String(50), nullable=False, index=True)  # Ej: "L1_INTRO_A"
    fragment_id = Column(Integer, ForeignKey("story_fragments.id"), nullable=False)

    # Tiempo de decisión
    choice_time_seconds = Column(Integer, nullable=False)  # Cuánto tardó en elegir
    made_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Consecuencias aplicadas (JSON)
    consequences_applied = Column(JSON, nullable=True)
    # Snapshot de consecuencias aplicadas en ese momento

    # Contexto de la elección
    user_level_at_choice = Column(Integer, nullable=False)  # Nivel narrativo del usuario
    user_archetype_at_choice = Column(String(50), nullable=True)  # Arquetipo detectado

    # Índices
    __table_args__ = (
        Index('idx_user_choice_date', 'user_id', 'made_at'),
        Index('idx_user_choice_fragment', 'user_id', 'fragment_id'),
    )

    def __repr__(self):
        return f"<UserChoice(user={self.user_id}, choice={self.choice_id}, time={self.choice_time_seconds}s)>"


class NarrativeFlag(Base):
    """
    Flag narrativo persistente.

    Los flags controlan:
    - Disponibilidad de opciones futuras
    - Fragmentos desbloqueados
    - Diálogos adaptativos
    - Estado de misiones

    Pueden expirar (flags temporales) o ser permanentes.
    """
    __tablename__ = "narrative_flags"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Usuario
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False, index=True)

    # Flag
    flag_key = Column(String(100), nullable=False)  # Ej: "met_diana", "found_secret_map"
    flag_value = Column(String(500), nullable=True)  # Valor (default: "true")

    # Expiración (opcional)
    expires_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda ctx: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda ctx: datetime.now(timezone.utc), onupdate=lambda ctx: datetime.now(timezone.utc))

    # Índice compuesto único
    __table_args__ = (
        Index('idx_flag_user_key', 'user_id', 'flag_key', unique=True),
    )

    @property
    def is_active(self) -> bool:
        """¿Está el flag activo (no expirado)?"""
        if self.expires_at is None:
            return True  # Flag permanente
        return datetime.now(timezone.utc) < self.expires_at

    def __repr__(self):
        status = "EXPIRED" if not self.is_active else "ACTIVE"
        return f"<NarrativeFlag(user={self.user_id}, {self.flag_key}={self.flag_value}, {status})>"


class ArchetypeProfile(Base):
    """
    Perfil de arquetipo de usuario.

    6 Arquetipos detectados:
    1. EXPLORER: Le gusta descubrir, explorar todas las opciones
    2. DIRECT: Toma decisiones rápidas, va al grano
    3. ROMANTIC: Busca conexiones emocionales, opciones románticas
    4. ANALYTICAL: Piensa mucho, elige opciones lógicas
    5. PERSISTENT: No se rinde, reintenta caminos difíciles
    6. PATIENT: Toma su tiempo, lee todo antes de elegir

    Detección basada en:
    - Tiempo de decisión
    - Opciones elegidas
    - Relectura de fragmentos
    - Patrones de navegación
    """
    __tablename__ = "archetype_profiles"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Usuario (1:1)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), unique=True, nullable=False, index=True)
    user = relationship("User", uselist=False, lazy="selectin")

    # Arquetipos detectados
    primary_archetype = Column(String(20), nullable=False, default="EXPLORER")
    secondary_archetype = Column(String(20), nullable=True)  # Arquetipo secundario

    # Puntos por arquetipo (JSON)
    archetype_points = Column(JSON, default=dict)
    # {
    #   "explorer": 15,
    #   "romantic": 8,
    #   "direct": 3,
    #   "analytical": 5,
    #   "persistent": 2,
    #   "patient": 7
    # }

    # Confianza en la detección (0-100)
    archetype_confidence = Column(Integer, default=0, nullable=False)
    # 0-30: Baja confianza (insuficiente data)
    # 31-70: Confianza media (tendencia clara)
    # 71-100: Alta confianza (patrón confirmado)

    # Estadísticas de comportamiento
    average_choice_time_seconds = Column(Integer, default=0, nullable=False)
    total_choices_analyzed = Column(Integer, default=0, nullable=False)
    reread_fragments_count = Column(Integer, default=0, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_analyzed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return (
            f"<ArchetypeProfile(user={self.user_id}, "
            f"primary={self.primary_archetype}, "
            f"confidence={self.archetype_confidence}%)>"
        )


class CharacterRelationship(Base):
    """
    Relación del usuario con personajes (Diana, Lucien).

    Score: -100 a +100
    - Negativo: Antipatía, desconfianza
    - Neutral (0): Indiferente
    - Positivo: Atracción, confianza, intimidad

    Hitos:
    - 40+: Close Friend
    - 60+: Romantic Interest
    - 80+: Deep Intimacy
    """
    __tablename__ = "character_relationships"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Usuario
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False, index=True)

    # Personaje
    character_name = Column(String(50), nullable=False)  # "LUCIEN", "DIANA"

    # Score de relación
    relationship_score = Column(Integer, default=0, nullable=False)  # -100 a +100

    # Hitos alcanzados
    became_close_friend_at = Column(DateTime, nullable=True)  # Score >= 40
    became_romantic_at = Column(DateTime, nullable=True)  # Score >= 60

    # Estadísticas de interacción
    interaction_count = Column(Integer, default=0, nullable=False)
    first_met_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_interaction_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Índice compuesto único
    __table_args__ = (
        Index('idx_relationship_user_character', 'user_id', 'character_name', unique=True),
    )

    @property
    def relationship_status(self) -> str:
        """Estado de relación basado en score"""
        if self.relationship_score >= 80:
            return "Deep Intimacy"
        elif self.relationship_score >= 60:
            return "Romantic Interest"
        elif self.relationship_score >= 40:
            return "Close Friend"
        elif self.relationship_score >= 20:
            return "Friendly"
        elif self.relationship_score >= -20:
            return "Neutral"
        elif self.relationship_score >= -50:
            return "Distant"
        else:
            return "Hostile"

    def __repr__(self):
        return (
            f"<CharacterRelationship(user={self.user_id}, "
            f"character={self.character_name}, "
            f"score={self.relationship_score}, "
            f"status={self.relationship_status})>"
        )


class NarrativeUnlock(Base):
    """
    Contenido narrativo desbloqueado por usuario.

    Tipos de desbloqueos:
    - Fragmentos ocultos
    - Rutas alternativas
    - Secretos y easter eggs
    - Logros narrativos
    """
    __tablename__ = "narrative_unlocks"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Usuario
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False, index=True)

    # Contenido desbloqueado
    unlock_type = Column(String(50), nullable=False)  # "fragment", "secret", "achievement", "route"
    unlock_id = Column(String(100), nullable=False)  # ID del contenido

    # Método de desbloqueo
    unlock_method = Column(String(50), nullable=False)  # "choice", "flag", "item", "besitos", "vip"
    unlock_source = Column(String(100), nullable=True)  # Qué lo desbloqueó (ej: "chose_romantic_path")

    # Timestamps
    unlocked_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Índice compuesto único (un usuario no puede desbloquear lo mismo dos veces)
    __table_args__ = (
        Index('idx_unlock_user_type_id', 'user_id', 'unlock_type', 'unlock_id', unique=True),
    )

    def __repr__(self):
        return f"<NarrativeUnlock(user={self.user_id}, type={self.unlock_type}, id={self.unlock_id})>"


class DesireProfile(Base):
    """
    Perfil de Deseo del usuario - Nivel 3.

    Sistema de 7 preguntas psicológicas para detectar arquetipo:
    1. ¿Qué buscas en una conexión? (Explorer/Intimate)
    2. ¿Prefieres lo inesperado o lo familiar? (Novelty/Comfort)
    3. ¿Qué tan rápido te abres? (Direct/Patient)
    4. ¿Mente o corazón? (Analytical/Romantic)
    5. ¿Luchas o te dejas llevar? (Persistent/Yield)
    6. ¿Secretos o transparencia? (Private/Open)
    7. ¿Pasión o plenitud? (Intensity/Peace)

    Este perfil genera:
    - Detección de arquetipo primario
    - Invitación VIP personalizada
    - Contenido adaptativo en niveles 4-6
    """
    __tablename__ = "desire_profiles"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Usuario (1:1)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), unique=True, nullable=False, index=True)
    user = relationship("User", uselist=False, lazy="selectin")

    # Respuestas a las 7 preguntas
    # P1: ¿Qué buscas en una conexión?
    question_1_answer = Column(String(50), nullable=True)  # "explorer" / "intimate"

    # P2: ¿Prefieres lo inesperado o lo familiar?
    question_2_answer = Column(String(50), nullable=True)  # "novelty" / "comfort"

    # P3: ¿Qué tan rápido te abres?
    question_3_answer = Column(String(50), nullable=True)  # "direct" / "patient"

    # P4: ¿Mente o corazón?
    question_4_answer = Column(String(50), nullable=True)  # "analytical" / "romantic"

    # P5: ¿Luchas o te dejas llevar?
    question_5_answer = Column(String(50), nullable=True)  # "persistent" / "yield"

    # P6: ¿Secretos o transparencia?
    question_6_answer = Column(String(50), nullable=True)  # "private" / "open"

    # P7: ¿Pasión o plenitud?
    question_7_answer = Column(String(50), nullable=True)  # "intensity" / "peace"

    # Arquetipo detectado (calculado)
    archetype_prediction = Column(String(50), nullable=True)  # "ROMANTIC", "EXPLORER", etc.
    archetype_confidence = Column(Integer, default=0, nullable=False)  # 0-100

    # Estado de completitud
    is_complete = Column(Boolean, default=False, nullable=False)  # True cuando respondió las 7
    questions_answered = Column(Integer, default=0, nullable=False)  # 0-7

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    last_answered_at = Column(DateTime, nullable=True)

    # Índices
    __table_args__ = (
        Index('idx_desire_complete', 'is_complete'),
        Index('idx_desire_archetype', 'archetype_prediction'),
    )

    @property
    def completion_percentage(self) -> int:
        """Porcentaje de preguntas respondidas (0-100)"""
        return int((self.questions_answered / 7) * 100)

    @property
    def next_question_number(self) -> int:
        """Número de la siguiente pregunta a responder (1-8, 8 = completado)"""
        return self.questions_answered + 1 if self.questions_answered < 7 else 8

    def __repr__(self):
        status = "COMPLETE" if self.is_complete else f"{self.questions_answered}/7"
        return (
            f"<DesireProfile(user={self.user_id}, "
            f"archetype={self.archetype_prediction}, "
            f"status={status})>"
        )


class ChannelInteraction(Base):
    """
    Registro de interacciones de usuario en canales - Sistema de Observación (Level 2).

    Utilizado para rastrear:
    - Posts vistos por el usuario en el canal
    - Tiempo dedicado en el canal
    - Reacciones a contenido
    - Pistas descubiertas

    El score de observación determina:
    - Si el usuario pasó la prueba de Level 2
    - Qué fragmentos se desbloquean (success vs partial)
    - Recompensas y badges obtenidos
    """
    __tablename__ = "channel_interactions"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Usuario
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False, index=True)
    user = relationship("User", uselist=False, lazy="selectin")

    # Post interactuado
    post_id = Column(BigInteger, nullable=False, index=True)  # ID del mensaje en Telegram
    channel_id = Column(BigInteger, nullable=False, index=True)  # ID del canal
    fragment_id_ref = Column(String(50), nullable=True)  # Referencia a fragmento narrativo (si aplica)

    # Tipo de interacción
    interaction_type = Column(String(20), nullable=False)  # "view", "reaction", "comment", "forward"

    # Datos de la interacción
    interaction_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    time_spent_seconds = Column(Integer, default=0, nullable=False)  # Tiempo en el post

    # Pistas descubiertas (JSON)
    clues_discovered = Column(JSON, default=list)  # ["pista_1", "pista_2", ...]
    # Las pistas son detalles sutiles en el contenido del canal

    # Observación scoring
    observation_score = Column(Integer, default=0, nullable=False)  # Puntos por esta interacción
    # View: +1 punto
    # Time > 30s: +2 puntos
    # Reacción: +2 puntos
    # Pista descubierta: +5 puntos

    # Metadatos
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Índices
    __table_args__ = (
        Index('idx_channel_user_post', 'user_id', 'post_id'),
        Index('idx_channel_user_score', 'user_id', 'observation_score'),
        Index('idx_channel_timestamp', 'interaction_timestamp'),
    )

    def __repr__(self):
        return (
            f"<ChannelInteraction(user={self.user_id}, "
            f"post={self.post_id}, "
            f"type={self.interaction_type}, "
            f"score={self.observation_score})>"
        )
