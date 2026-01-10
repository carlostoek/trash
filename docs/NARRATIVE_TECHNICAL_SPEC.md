# DIANABOT NARRATIVE MODULE - COMPLETE TECHNICAL SPECIFICATION

## Executive Summary

This document translates the creative vision for DianaBot's narrative module into a complete, implementable technical specification. The narrative module integrates seamlessly with existing VIP/Free infrastructure, gamification system, and user management.

**Status:** Ready for Implementation
**Dependencies:** Existing models (User, VIPSubscriber, UserGamification, Mission, Reward)
**Integration Points:** SubscriptionService, GamificationService, UserService, BroadcastService

---

## 1. DATA MODELS SPECIFICATION

### 1.1 StoryFragment Model

**Purpose:** Store individual narrative content pieces with branching logic.

```python
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
    unlocks_mission_id = Column(Integer, ForeignKey("missions.id"), nullable=True)
    unlocks_reward_id = Column(Integer, ForeignKey("rewards.id"), nullable=True)

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
```

**Fields Breakdown:**
- **fragment_id**: Unique identifier following convention L{N}_{TYPE}_{NUMBER}
- **narrative_level**: 1-6, determines VIP requirement
- **speaker**: Which character is speaking (Diana/Lucien/Narrator)
- **unlock_conditions**: JSON dict with complex requirements
- **content_variants**: Different text for different user archetypes
- **gamification rewards**: Integration with besitos, missions, items

---

### 1.2 StoryChoice Model

**Purpose:** User decisions that branch the narrative.

```python
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
    fragment = relationship("StoryFragment", back_populates="choices")

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
```

**Fields Breakdown:**
- **display_requirements**: When to show this choice (flags, level, archetype)
- **consequences**: What happens when selected (flags, archetype points, relationships)
- **is_destructive_choice**: Cannot be undone (warn user)
- **choice_emoji**: Visual indicator for the button

---

### 1.3 UserNarrativeProgress Model

**Purpose:** Track user's journey through the 6-level narrative.

```python
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
```

**Fields Breakdown:**
- **current_fragment_id**: Where user is now
- **levels_completed**: Which narrative levels are finished
- **timestamps**: Track completion of key levels (1, 3, 6)
- **achievements**: Special accomplishments discovered

---

### 1.4 UserChoice Model

**Purpose:** Record every decision user makes for analysis and replay.

```python
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
```

**Fields Breakdown:**
- **choice_time_seconds**: Critical for archetype detection
- **consequences_applied**: Snapshot of what changed
- **context**: User state when choice was made

---

### 1.5 NarrativeFlag Model

**Purpose:** Persistent state flags for conditional narrative logic.

```python
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
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Índice compuesto único
    __table_args__ = (
        Index('idx_flag_user_key', 'user_id', 'flag_key', unique=True),
    )

    @property
    def is_active(self) -> bool:
        """¿Está el flag activo (no expirado)?"""
        if self.expires_at is None:
            return True  # Flag permanente
        return datetime.utcnow() < self.expires_at

    def __repr__(self):
        status = "EXPIRED" if not self.is_active else "ACTIVE"
        return f"<NarrativeFlag(user={self.user_id}, {self.flag_key}={self.flag_value}, {status})>"
```

**Fields Breakdown:**
- **flag_key**: Unique identifier for the flag
- **flag_value**: Can store complex values (JSON strings)
- **expires_at**: Optional expiration for temporary flags

---

### 1.6 ArchetypeProfile Model

**Purpose:** Behavioral detection and personality profiling.

```python
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
```

**Fields Breakdown:**
- **archetype_points**: Running score for each archetype
- **archetype_confidence**: How sure we are about the classification
- **behavioral_stats**: Metrics used for detection

---

### 1.7 CharacterRelationship Model

**Purpose:** Track relationship scores with Diana and Lucien.

```python
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
```

**Fields Breakdown:**
- **relationship_score**: Dynamic score affected by user choices
- **milestones**: Timestamps when relationship levels reached
- **relationship_status**: Computed property for display

---

### 1.8 NarrativeUnlock Model

**Purpose:** Track content unlocks and achievements.

```python
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
```

**Fields Breakdown:**
- **unlock_type**: Category of unlocked content
- **unlock_method**: How it was unlocked (choice, VIP, besitos, etc.)
- **unique constraint**: Prevent duplicate unlocks

---

## 2. NARRATIVE SERVICE METHODS

### 2.1 Fragment Management

```python
class NarrativeService:
    """
    Servicio central de gestión narrativa.

    Responsabilidades:
    - Gestión de fragmentos de historia
    - Progresión del usuario
    - Desbloqueo de contenido
    - Integración con gamificación
    """

    async def get_starting_fragment(
        self,
        narrative_level: int = 1
    ) -> Optional[StoryFragment]:
        """
        Obtiene el fragmento inicial de un nivel narrativo.

        Args:
            narrative_level: Nivel de narrativa (1-6)

        Returns:
            StoryFragment inicial o None si no existe
        """

    async def get_fragment(
        self,
        fragment_id: str
    ) -> Optional[StoryFragment]:
        """
        Obtiene un fragmento por ID.

        Args:
            fragment_id: ID del fragmento (ej: "L1_INTRO_001")

        Returns:
            StoryFragment o None
        """

    async def get_fragment_choices(
        self,
        fragment_id: int,
        user_id: int,
        user_flags: List[str]
    ) -> List[StoryChoice]:
        """
        Obtiene las opciones disponibles para un usuario en un fragmento.

        Filtra opciones basado en:
        - Opciones activas
        - Requisitos de flags
        - Requisitos de arquetipo
        - Requisitos de nivel

        Args:
            fragment_id: ID del fragmento
            user_id: ID del usuario
            user_flags: Lista de flags activos del usuario

        Returns:
            Lista de StoryChoice disponibles (ordenadas por sort_order)
        """

    async def get_fragment_content_for_user(
        self,
        fragment: StoryFragment,
        user_archetype: str
    ) -> str:
        """
        Retorna contenido adaptado al arquetipo del usuario.

        Args:
            fragment: StoryFragment
            user_archetype: Arquetipo del usuario

        Returns:
            Contenido textual del fragmento (personalizado si existe variante)
        """
```

### 2.2 User Progression

```python
    async def get_or_create_user_progress(
        self,
        user_id: int
    ) -> UserNarrativeProgress:
        """
        Obtiene o crea el progreso narrativo del usuario.

        Args:
            user_id: ID del usuario

        Returns:
            UserNarrativeProgress
        """

    async def advance_to_next_fragment(
        self,
        user_id: int,
        choice_id: str
    ) -> Tuple[bool, str, Optional[StoryFragment], Dict]:
        """
        Avanza la historia del usuario basado en su elección.

        Flujo completo:
        1. Validar que la elección existe y está disponible
        2. Registrar la elección del usuario
        3. Aplicar consecuencias (flags, items, arquetipo)
        4. Actualizar progreso narrativo
        5. Obtener el siguiente fragmento
        6. Retornar siguiente fragmento + detalles

        Args:
            user_id: ID del usuario
            choice_id: ID de la elección (ej: "L1_INTRO_A")

        Returns:
            Tuple (success, message, next_fragment, details)
            - success: True si avanzó exitosamente
            - message: Mensaje descriptivo
            - next_fragment: Siguiente fragmento o None
            - details: Dict con consecuencias aplicadas
        """

    async def can_access_fragment(
        self,
        user_id: int,
        fragment: StoryFragment,
        user_flags: List[str]
    ) -> Tuple[bool, str]:
        """
        Verifica si un usuario puede acceder a un fragmento.

        Args:
            user_id: ID del usuario
            fragment: StoryFragment a verificar
            user_flags: Lista de flags activos del usuario

        Returns:
            Tuple (can_access, reason)
            - can_access: True si puede acceder
            - reason: Mensaje explicativo si no puede acceder
        """
```

### 2.3 Integration with Gamification

```python
    async def apply_choice_consequences(
        self,
        user_id: int,
        choice: StoryChoice,
        choice_time_seconds: int
    ) -> Dict:
        """
        Aplica todas las consecuencias de una elección.

        Integra con:
        - FlagService (flags)
        - ArchetypeService (puntos de arquetipo)
        - CharacterRelationshipService (relaciones)
        - GamificationService (besitos, items, misiones)

        Args:
            user_id: ID del usuario
            choice: StoryChoice seleccionada
            choice_time_seconds: Tiempo que tomó en elegir

        Returns:
            Dict con todas las consecuencias aplicadas
        """

    async def grant_narrative_rewards(
        self,
        user_id: int,
        fragment: StoryFragment
    ) -> Dict:
        """
        Otorga recompensas de gamificación por completar fragmento.

        Args:
            user_id: ID del usuario
            fragment: StoryFragment completado

        Returns:
            Dict con recompensas otorgadas
        """
```

---

## 3. FLAG SERVICE METHODS

```python
class FlagService:
    """
    Servicio de gestión de flags narrativos.
    """

    async def set_flag(
        self,
        user_id: int,
        flag_key: str,
        flag_value: str = "true",
        expires_at: Optional[datetime] = None
    ) -> NarrativeFlag:
        """
        Establece un flag narrativo para un usuario.

        Args:
            user_id: ID del usuario
            flag_key: Clave del flag (ej: "met_diana")
            flag_value: Valor del flag (default: "true")
            expires_at: Opcional, cuándo expira el flag

        Returns:
            NarrativeFlag creado/actualizado
        """

    async def get_flag(
        self,
        user_id: int,
        flag_key: str
    ) -> Optional[NarrativeFlag]:
        """
        Obtiene un flag narrativo.

        Args:
            user_id: ID del usuario
            flag_key: Clave del flag

        Returns:
            NarrativeFlag o None
        """

    async def has_flag(
        self,
        user_id: int,
        flag_key: str
    ) -> bool:
        """
        Verifica si un usuario tiene un flag activo.

        Args:
            user_id: ID del usuario
            flag_key: Clave del flag

        Returns:
            True si tiene el flag activo
        """

    async def clear_flag(
        self,
        user_id: int,
        flag_key: str
    ) -> bool:
        """
        Elimina un flag narrativo.

        Args:
            user_id: ID del usuario
            flag_key: Clave del flag

        Returns:
            True si se eliminó correctamente
        """

    async def get_all_user_flags(
        self,
        user_id: int
    ) -> List[NarrativeFlag]:
        """
        Obtiene todos los flags activos de un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            Lista de NarrativeFlag activos
        """
```

---

## 4. ARCHETYPE SERVICE METHODS

```python
class ArchetypeService:
    """
    Servicio de detección y gestión de arquetipos de usuario.
    """

    async def get_or_create_archetype_profile(
        self,
        user_id: int
    ) -> ArchetypeProfile:
        """
        Obtiene o crea el perfil de arquetipo del usuario.

        Args:
            user_id: ID del usuario

        Returns:
            ArchetypeProfile
        """

    async def add_archetype_points(
        self,
        user_id: int,
        points_dict: Dict[str, int]
    ) -> None:
        """
        Añade puntos de arquetipo a un usuario.

        Args:
            user_id: ID del usuario
            points_dict: Dict con puntos por arquetipo
                {"romantic": +2, "direct": -1}
        """

    async def record_choice_timing(
        self,
        user_id: int,
        choice_time_seconds: int
    ) -> None:
        """
        Registra el tiempo que tomó un usuario en elegir.

        Usado para detectar arquetipos:
        - Rápido (< 10s) → Direct
        - Medio (10-30s) → Normal
        - Lento (> 30s) → Patient/Analytical

        Args:
            user_id: ID del usuario
            choice_time_seconds: Tiempo en segundos
        """

    async def record_fragment_reread(
        self,
        user_id: int
    ) -> None:
        """
        Registra que un usuario releyó un fragmento.

        Indica: Explorer (leer todo) o Analytical (analizar detalles)

        Args:
            user_id: ID del usuario
        """

    async def get_personalized_content(
        self,
        user_id: int,
        content_variants: Dict[str, str]
    ) -> str:
        """
        Retorna contenido personalizado basado en arquetipo.

        Args:
            user_id: ID del usuario
            content_variants: Dict con variantes por arquetipo

        Returns:
            Contenido personalizado o default si no hay variante
        """
```

---

## 5. CHARACTER RELATIONSHIP SERVICE METHODS

```python
class CharacterRelationshipService:
    """
    Servicio de gestión de relaciones con personajes.
    """

    async def get_relationship(
        self,
        user_id: int,
        character_name: str
    ) -> Optional[CharacterRelationship]:
        """
        Obtiene el estado de relación con un personaje.

        Args:
            user_id: ID del usuario
            character_name: Nombre del personaje ("LUCIEN", "DIANA")

        Returns:
            CharacterRelationship o None
        """

    async def get_or_create_relationship(
        self,
        user_id: int,
        character_name: str
    ) -> CharacterRelationship:
        """
        Obtiene o crea una relación con un personaje.

        Args:
            user_id: ID del usuario
            character_name: Nombre del personaje

        Returns:
            CharacterRelationship
        """

    async def update_relationship_score(
        self,
        user_id: int,
        character_name: str,
        score_change: int
    ) -> CharacterRelationship:
        """
        Actualiza el puntaje de relación con un personaje.

        Args:
            user_id: ID del usuario
            character_name: Nombre del personaje ("LUCIEN", "DIANA")
            score_change: Cambio en el puntaje (positivo o negativo)

        Returns:
            CharacterRelationship actualizado
        """

    async def get_character_dialogue_variant(
        self,
        user_id: int,
        character_name: str,
        dialogue_variants: Dict[str, str]
    ) -> str:
        """
        Retorna variante de diálogo basada en relación.

        Args:
            user_id: ID del usuario
            character_name: Personaje hablando
            dialogue_variants: Dict con variantes por nivel de relación

        Returns:
            Variante apropiada de diálogo
        """
```

---

## 6. STORY ENGINE (COORDINATOR)

```python
class StoryEngine:
    """
    Motor principal de la historia.

    Coordina todos los servicios narrativos para proporcionar
    una experiencia de historia coherente y personalizada.
    """

    def __init__(self, session: AsyncSession, bot: Bot):
        self.session = session
        self.bot = bot

        # Inicializar sub-servicios
        self.narrative = NarrativeService(session, bot)
        self.flags = self.narrative.flags
        self.archetype = self.narrative.archetype
        self.relationships = self.narrative.relationships

    async def get_current_story_state(
        self,
        user_id: int
    ) -> Dict:
        """
        Obtiene el estado completo de la historia del usuario.

        Args:
            user_id: ID del usuario

        Returns:
            Dict con estado completo:
            {
                "current_fragment": StoryFragment,
                "available_choices": [StoryChoice],
                "user_progress": UserNarrativeProgress,
                "user_flags": [str],
                "archetype": ArchetypeProfile,
                "relationships": {
                    "LUCIEN": CharacterRelationship,
                    "DIANA": CharacterRelationship
                },
                "can_continue": bool,
                "unlock_message": str
            }
        """

    async def make_choice(
        self,
        user_id: int,
        choice_id: str,
        choice_time_seconds: int
    ) -> Dict:
        """
        Procesa una elección del usuario.

        Flujo completo:
        1. Registrar tiempo de elección para arquetipo
        2. Avanzar historia (aplicar consecuencias)
        3. Obtener siguiente estado narrativo

        Args:
            user_id: ID del usuario
            choice_id: ID de la elección
            choice_time_seconds: Tiempo que tomó en elegir

        Returns:
            Dict con resultado de la elección
        """

    async def start_narrative(
        self,
        user_id: int,
        start_level: int = 1
    ) -> Dict:
        """
        Inicia o continúa la narrativa para un usuario.

        Args:
            user_id: ID del usuario
            start_level: Nivel inicial (default: 1)

        Returns:
            Dict con estado inicial de la historia
        """

    async def reset_narrative(
        self,
        user_id: int
    ) -> bool:
        """
        Resetea el progreso narrativo del usuario.

        ADVERTENCIA: Esta acción es irreversible.

        Args:
            user_id: ID del usuario

        Returns:
            True si se reseteó correctamente
        """
```

---

## 7. HANDLER SPECIFICATIONS

### 7.1 User Handlers

```python
# bot/handlers/user/narrative.py

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.services.narrative import StoryEngine

narrative_router = Router()
narrative_router.message.filter(F.chat.type == "private")

@narrative_router.message(Command("story"))
async def cmd_start_story(
    message: Message,
    story_engine: StoryEngine
):
    """
    Inicia o continúa la narrativa del usuario.

    Flow:
    1. Obtener estado actual de la historia
    2. Si no hay progreso, iniciar nivel 1
    3. Si hay progreso, continuar desde fragmento actual
    4. Enviar fragmento con opciones
    """
    pass

@narrative_router.callback_query(F.data.startswith("narrative:choice:"))
async def callback_narrative_choice(
    callback: CallbackQuery,
    story_engine: StoryEngine,
    state: FSMContext
):
    """
    Procesa una elección narrativa del usuario.

    Flow:
    1. Extraer choice_id del callback data
    2. Calcular tiempo de elección (desde que se mostró el mensaje)
    3. Procesar elección con story_engine.make_choice()
    4. Enviar siguiente fragmento
    5. Actualizar mensaje anterior
    """
    pass

@narrative_router.callback_query(F.data == "narrative:reread")
async def callback_reread_fragment(
    callback: CallbackQuery,
    story_engine: StoryEngine
):
    """
    Permite al usuario releer el fragmento actual.

    Afecta detección de arquetipo (Explorer/Analytical).
    """
    pass
```

### 7.2 Admin Handlers

```python
# bot/handlers/admin/narrative_editor.py

from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

class NarrativeEditorStates(StatesGroup):
    """FSM states para editor narrativo"""
    waiting_for_fragment_id = State()
    waiting_for_content = State()
    waiting_for_speaker = State()
    waiting_for_media = State()
    waiting_for_unlock_conditions = State()

@admin_router.callback_query(F.data == "admin:narrative:create_fragment")
async def callback_create_fragment_start(
    callback: CallbackQuery,
    state: FSMContext
):
    """
    Inicia wizard de creación de fragmento.

    Wizard Steps:
    1. Solicitar fragment_id (ej: L1_INTRO_001)
    2. Solicitar nivel narrativo (1-6)
    3. Solicitar título
    4. Solicitar contenido de texto
    5. Solicitar speaker (opcional)
    6. Solicitar media (opcional)
    7. Solicitar condiciones de desbloqueo (opcional)
    8. Confirmar y guardar
    """
    pass

@admin_router.callback_query(F.data.startswith("admin:narrative:edit:"))
async def callback_edit_fragment(
    callback: CallbackQuery,
    state: FSMContext
):
    """
    Edita un fragmento existente.

    Carga datos actuales y permite editar campos.
    """
    pass

@admin_router.callback_query(F.data == "admin:narrative:add_choice")
async def callback_add_choice_start(
    callback: CallbackQuery,
    state: FSMContext
):
    """
    Inicia wizard de añadir opción a fragmento.

    Wizard Steps:
    1. Seleccionar fragmento padre
    2. Ingresar texto de opción
    3. Seleccionar fragmento destino
    4. Configurar consecuencias (flags, puntos, relaciones)
    5. Configurar requisitos de visualización
    6. Confirmar y guardar
    """
    pass

@admin_router.callback_query(F.data == "admin:narrative:preview")
async def callback_preview_fragment(
    callback: CallbackQuery,
    story_engine: StoryEngine
):
    """
    Previsualiza un fragmento como si fuera el usuario.

    Útil para testing de contenido antes de publicar.
    """
    pass
```

### 7.3 FSM States for Narrative

```python
# bot/states/narrative.py

class NarrativeUserStates(StatesGroup):
    """Estados FSM para interacciones narrativas del usuario"""
    reading_fragment = State()  # Usuario leyendo fragmento
    making_choice = State()  # Usuario eligiendo opción

class NarrativeAdminStates(StatesGroup):
    """Estados FSM para administración narrativa"""
    # Creación de fragmentos
    creating_fragment_id = State()
    creating_fragment_level = State()
    creating_fragment_title = State()
    creating_fragment_content = State()
    creating_fragment_speaker = State()
    creating_fragment_media = State()
    creating_fragment_conditions = State()

    # Creación de opciones
    creating_choice_text = State()
    creating_choice_target = State()
    creating_choice_consequences = State()
    creating_choice_requirements = State()

    # Edición
    editing_fragment_field = State()
    editing_choice_field = State()
```

---

## 8. INTEGRATION WITH EXISTING SYSTEMS

### 8.1 VIP Subscription Integration

```python
# En NarrativeService.can_access_fragment()

async def can_access_fragment(
    self,
    user_id: int,
    fragment: StoryFragment,
    user_flags: List[str]
) -> Tuple[bool, str]:
    """
    Verifica acceso a fragmento basado en nivel VIP.

    Niveles 1-3: Free (acceso libre)
    Niveles 4-6: VIP (requiere suscripción activa)
    """
    # Verificar nivel VIP
    if fragment.narrative_level >= 4:
        from bot.services.subscription import SubscriptionService
        subscription_service = SubscriptionService(self.session, self.bot)
        is_vip = await subscription_service.is_vip_active(user_id)

        if not is_vip:
            return False, f"🔒 Este contenido requiere suscripción VIP (Nivel {fragment.narrative_level})"

    return True, ""
```

### 8.2 Gamification Integration

```python
# En NarrativeService.advance_to_next_fragment()

async def advance_to_next_fragment(
    self,
    user_id: int,
    choice_id: str
) -> Tuple[bool, str, Optional[StoryFragment], Dict]:
    """
    Integra gamificación al avanzar narrativa.
    """
    # ... lógica existente ...

    # Otorgar besitos del fragmento
    if next_fragment.besitos_reward > 0:
        from bot.services.gamification import GamificationService
        gamification = GamificationService(self.session)
        await gamification.add_besitos(
            user_id=user_id,
            amount=next_fragment.besitos_reward,
            reason=f"Narrativa: {next_fragment.fragment_id}"
        )

    # Desbloquear misión si aplica
    if next_fragment.unlocks_mission_id:
        from bot.services.gamification import GamificationService
        gamification = GamificationService(self.session)
        await gamification.unlock_mission(
            user_id=user_id,
            mission_id=next_fragment.unlocks_mission_id
        )

    return True, message, next_fragment, consequences_applied
```

### 8.3 Inventory Integration

```python
# En NarrativeService.can_access_fragment()

async def can_access_fragment(
    self,
    user_id: int,
    fragment: StoryFragment,
    user_flags: List[str]
) -> Tuple[bool, str]:
    """
    Verifica si usuario tiene items requeridos.
    """
    if fragment.unlock_conditions:
        conditions = fragment.unlock_conditions

        # Verificar items requeridos
        required_items = conditions.get("required_items", [])
        if required_items:
            from bot.services.gamification import GamificationService
            gamification = GamificationService(self.session)
            user_inventory = await gamification.get_user_inventory(user_id)

            user_items = [item.item_code for item in user_inventory]
            if not all(item in user_items for item in required_items):
                return False, f"🔒 Necesitas objetos específicos para esto: {', '.join(required_items)}"

    return True, ""
```

---

## 9. DATABASE MIGRATION SCRIPT

```python
# migrations/add_narrative_models.py

"""
Migración para añadir modelos narrativos a la base de datos existente.

Ejecutar con:
python -m migrations.add_narrative_models
"""

from bot.database.base import Base
from bot.database.engine import engine
from bot.database.models import (
    StoryFragment,
    StoryChoice,
    UserNarrativeProgress,
    UserChoice,
    NarrativeFlag,
    ArchetypeProfile,
    CharacterRelationship,
    NarrativeUnlock
)

async def upgrade():
    """Crea tablas narrativas"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Tablas narrativas creadas exitosamente")

async def downgrade():
    """Elimina tablas narrativas (ROLLBACK)"""
    async with engine.begin() as conn:
        # Orden inverso de dependencias
        await conn.run_sync(lambda: NarrativeUnlock.__table__.drop())
        await conn.run_sync(lambda: CharacterRelationship.__table__.drop())
        await conn.run_sync(lambda: ArchetypeProfile.__table__.drop())
        await conn.run_sync(lambda: NarrativeFlag.__table__.drop())
        await conn.run_sync(lambda: UserChoice.__table__.drop())
        await conn.run_sync(lambda: UserNarrativeProgress.__table__.drop())
        await conn.run_sync(lambda: StoryChoice.__table__.drop())
        await conn.run_sync(lambda: StoryFragment.__table__.drop())

    print("✅ Tablas narrativas eliminadas (rollback)")

if __name__ == "__main__":
    import asyncio
    asyncio.run(upgrade())
```

---

## 10. INITIAL DATA SEEDING

```python
# seeds/seed_narrative_content.py

"""
Seed inicial de contenido narrativo.

Crea fragmentos básicos para:
- Nivel 1: Introducción a Los Kinkys
- Nivel 2: Profundización gratuita
- Nivel 3: Culminación gratuita
"""

from datetime import datetime
from bot.database.engine import get_session
from bot.database.models import (
    StoryFragment,
    StoryChoice
)

async def seed_level_1():
    """Seed nivel 1 - Introducción"""
    async with get_session() as session:
        # Fragmento 1: Bienvenida de Diana
        frag_1 = StoryFragment(
            fragment_id="L1_INTRO_001",
            narrative_level=1,
            title="Bienvenida a Los Kinkys",
            content_text="Bienvenido a Los Kinkys. Has cruzado una línea que muchos ven... pero pocos realmente atraviesan.",
            speaker="DIANA",
            speaker_emotion="mysterious",
            is_starting_fragment=True,
            is_ending_fragment=False,
            besitos_reward=10,
            experience_reward=5,
            active=True,
            sort_order=1,
            created_at=datetime.utcnow()
        )
        session.add(frag_1)

        # Opción A: Reaccionar inmediatamente
        choice_a = StoryChoice(
            choice_id="L1_INTRO_A",
            fragment_id=frag_1.id,
            choice_text="🚪 Descubrir más",
            choice_description="Entrar inmediatamente en el misterio",
            target_fragment_id=2,  # ID del siguiente fragmento
            consequences={
                "flags_set": ["impulsive_choice"],
                "archetype_points": {
                    "direct": +2,
                    "explorer": +1
                },
                "relationship_change": {
                    "DIANA": +2
                },
                "besitos_reward": 5
            },
            sort_order=1,
            active=True
        )
        session.add(choice_a)

        await session.commit()
        print("✅ Nivel 1 seeded")

async def seed_all():
    """Seed todos los niveles iniciales"""
    await seed_level_1()
    # await seed_level_2()
    # await seed_level_3()
    print("✅ Todos los niveles seeded")

if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_all())
```

---

## 11. TESTING STRATEGY

### 11.1 Unit Tests

```python
# tests/test_narrative_service.py

import pytest
from bot.services.narrative import NarrativeService, FlagService
from bot.database.models import StoryFragment, UserNarrativeProgress

@pytest.mark.asyncio
async def test_get_starting_fragment(db_session, bot):
    """Test obtención de fragmento inicial"""
    service = NarrativeService(db_session, bot)

    fragment = await service.get_starting_fragment(narrative_level=1)

    assert fragment is not None
    assert fragment.narrative_level == 1
    assert fragment.is_starting_fragment is True

@pytest.mark.asyncio
async def test_flag_service_set_and_get(db_session):
    """Test servicio de flags"""
    service = FlagService(db_session)

    # Set flag
    flag = await service.set_flag(
        user_id=12345,
        flag_key="test_flag",
        flag_value="active"
    )

    assert flag.flag_key == "test_flag"
    assert flag.flag_value == "active"

    # Get flag
    retrieved = await service.get_flag(12345, "test_flag")
    assert retrieved is not None
    assert retrieved.flag_value == "active"

@pytest.mark.asyncio
async def test_advance_to_next_fragment(db_session, bot):
    """Test avance narrativo"""
    service = NarrativeService(db_session, bot)

    success, message, next_fragment, consequences = await service.advance_to_next_fragment(
        user_id=12345,
        choice_id="L1_INTRO_A"
    )

    assert success is True
    assert next_fragment is not None
    assert "flags_set" in consequences
```

### 11.2 Integration Tests

```python
# tests/test_narrative_integration.py

import pytest
from bot.services.narrative import StoryEngine

@pytest.mark.asyncio
async def test_complete_narrative_flow(db_session, bot):
    """Test flujo narrativo completo"""
    engine = StoryEngine(db_session, bot)

    # 1. Iniciar narrativa
    state = await engine.start_narrative(user_id=12345)
    assert state["can_continue"] is True

    # 2. Hacer elección
    result = await engine.make_choice(
        user_id=12345,
        choice_id="L1_INTRO_A",
        choice_time_seconds=5
    )
    assert result["success"] is True

    # 3. Verificar consecuencias
    assert "flags_set" in result["consequences"]
    assert result["next_fragment"] is not None

@pytest.mark.asyncio
async def test_vip_level_access(db_session, bot):
    """Test acceso a niveles VIP"""
    engine = StoryEngine(db_session, bot)

    # Usuario Free intenta acceder a nivel 4
    state = await engine.get_current_story_state(user_id=12345)

    # Simular fragmento VIP
    vip_fragment = StoryFragment(
        narrative_level=4,
        # ... otros campos
    )

    can_access, reason = await engine.narrative.can_access_fragment(
        user_id=12345,
        fragment=vip_fragment,
        user_flags=[]
    )

    assert can_access is False
    assert "VIP" in reason
```

### 11.3 E2E Tests

```python
# tests/test_narrative_e2e.py

import pytest
from aiogram import Dispatcher
from bot.handlers.user import narrative

@pytest.mark.asyncio
async def test_user_complete_level_1(db_session, bot, test_user):
    """Test usuario completo nivel 1"""
    dp = Dispatcher()

    # 1. Usuario envía /story
    message = test_user("/story")
    await dp.feed_webhook_update(message)

    # 2. Usuario hace click en primera opción
    callback = test_user.callback("narrative:choice:L1_INTRO_A")
    await dp.feed_webhook_update(callback)

    # 3. Verificar que recibió siguiente fragmento
    assert len(test_user.messages) > 1
    assert "siguiente" in test_user.messages[-1].text.lower()
```

---

## 12. VALIDATION CRITERIA

### 12.1 Functional Validation

- [ ] Users can start narrative from level 1
- [ ] Users make choices and story advances correctly
- [ ] VIP users can access levels 4-6
- [ ] Free users are blocked from levels 4-6
- [ ] Choices apply consequences (flags, archetype points, relationships)
- [ ] Archetypes are detected based on behavior
- [ ] Content adapts to user archetype
- [ ] Relationships with Diana/Lucien evolve
- [ ] Narrative integrates with gamification (besitos, items, missions)

### 12.2 Performance Validation

- [ ] Fragment retrieval < 100ms
- [ ] Choice processing < 200ms
- [ ] State calculation < 300ms
- [ ] No N+1 query problems
- [ ] Efficient JSON querying

### 12.3 Data Integrity Validation

- [ ] Users cannot access fragments without proper requirements
- [ ] Choices can only be made once (no duplicate choices)
- [ ] Flags expire correctly
- [ ] Relationship scores bounded (-100 to +100)
- [ ] Archetype confidence calculation accurate

### 12.4 Creative Intent Validation

- [ ] Diana's voice is mysterious and alluring
- [ ] Lucien's voice is formal and evaluative
- [ ] 6-level structure is respected
- [ ] VIP content feels premium and exclusive
- [ ] Free content creates desire for VIP upgrade
- [ ] Emotional journey matches creative vision

---

## 13. IMPLEMENTATION CHECKLIST

### Phase 1: Database Models
- [ ] Add all 8 narrative models to `bot/database/models.py`
- [ ] Run migration script to create tables
- [ ] Verify tables created correctly
- [ ] Seed initial narrative content

### Phase 2: Core Services
- [ ] Implement FlagService completely
- [ ] Implement ArchetypeService completely
- [ ] Implement CharacterRelationshipService completely
- [ ] Implement NarrativeService completely
- [ ] Implement StoryEngine coordinator

### Phase 3: User Handlers
- [ ] Implement `/story` command handler
- [ ] Implement choice callback handler
- [ ] Implement reread functionality
- [ ] Add FSM states for user interactions
- [ ] Create narrative inline keyboards

### Phase 4: Admin Handlers
- [ ] Implement fragment creation wizard
- [ ] Implement fragment editing wizard
- [ ] Implement choice creation wizard
- [ ] Implement preview functionality
- [ ] Add FSM states for admin interactions

### Phase 5: Integration
- [ ] Integrate with SubscriptionService (VIP check)
- [ ] Integrate with GamificationService (besitos, items)
- [ ] Integrate with UserService (role checking)
- [ ] Add narrative to ServiceContainer
- [ ] Update main.py to include narrative router

### Phase 6: Testing
- [ ] Write unit tests for all services
- [ ] Write integration tests for flows
- [ ] Write E2E tests for complete journeys
- [ ] Test VIP access control
- [ ] Test archetype detection accuracy
- [ ] Load test with 100+ concurrent users

### Phase 7: Content Creation
- [ ] Write all level 1 fragments (5-10)
- [ ] Write all level 1 choices
- [ ] Write all level 2 fragments (5-10)
- [ ] Write all level 3 fragments (5-10)
- [ ] Write level 4-6 fragments (VIP content)

---

## 14. SUCCESS METRICS

### Technical Metrics
- **Response Time:** < 300ms for story state retrieval
- **Uptime:** 99.9% availability
- **Error Rate:** < 0.1% of interactions
- **Database Queries:** < 5 queries per interaction

### User Engagement Metrics
- **Completion Rate:** % users who finish level 1
- **VIP Conversion:** % free users who upgrade after level 3
- **Retention:** % users who return after 24 hours
- **Choice Distribution:** Are choices balanced or skewed?

### Creative Metrics
- **Emotional Resonance:** User sentiment analysis
- **Immersion Score:** Average session duration
- **Archetype Accuracy:** Do users agree with their classification?
- **Relationship Depth:** Average relationship score progression

---

## 15. NEXT STEPS AFTER IMPLEMENTATION

1. **Analytics Dashboard**
   - Track user progression through levels
   - Monitor choice distribution
   - Analyze archetype accuracy
   - Measure relationship score trends

2. **Content Management System**
   - Web interface for content creators
   - Visual branching editor
   - Preview and test mode
   - Version control for narrative changes

3. **A/B Testing Framework**
   - Test different fragment texts
   - Test choice wording
   - Test reward amounts
   - Measure impact on VIP conversion

4. **Personalization Engine**
   - Machine learning for archetype detection
   - Dynamic difficulty adjustment
   - Personalized reward calibration
   - Adaptive pacing based on engagement

---

## CONCLUSION

This technical specification provides a complete blueprint for implementing DianaBot's narrative module. It maintains fidelity to the creative vision while providing pragmatic, buildable solutions that integrate seamlessly with existing infrastructure.

**Key Design Decisions:**
1. **Modular Services:** Each narrative concern (flags, archetypes, relationships) has its own service
2. **JSON Flexibility:** Complex data (consequences, conditions) stored as JSON for schema evolution
3. **VIP Integration:** Levels 4-6 naturally gated by existing VIP subscription system
4. **Archetype Detection:** Behavioral data (choice timing, rereads) informs personalization
5. **Relationship Scoring:** Dynamic relationship evolution affects dialogue and options

**Implementation Priority:**
1. Models + Migration (Foundational)
2. Core Services (Business Logic)
3. StoryEngine (Coordination)
4. User Handlers (Experience)
5. Admin Handlers (Content Management)
6. Testing (Quality Assurance)
7. Content Creation (Creative Fulfillment)

This specification is ready for immediate implementation by a development team.
