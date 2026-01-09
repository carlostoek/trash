"""
Modelos de base de datos para contenido de escenas y dialogos.

Tablas:
- narrative_chapters: Capitulos narrativos
- narrative_scenes: Escenas dentro de capitulos
- scene_dialogues: Dialogos dentro de escenas con variantes por arquetipo
- dialogue_options: Opciones de respuesta en dialogos
"""
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime,
    JSON, ForeignKey, Index, Float, Enum, Text
)
from sqlalchemy.orm import relationship

from bot.database.base import Base
from bot.database.enums import (
    NarrativeLevel, ArchetypeType, RelationshipState, ConsequenceType
)

logger = logging.getLogger(__name__)


class NarrativeChapter(Base):
    """
    Capitulo narrativo que contiene multiples escenas.

    Estructura:
        Level 1-3 (Los Kinkys):
            chapter_1: Bienvenida - Primer contacto con Lucien
            chapter_2: Profundizacion - Misiones de observacion
            chapter_3: Culminacion - Perfil de deseo
        Level 4-6 (El Divan):
            chapter_4: Entrada VIP - Evaluacion de comprension
            chapter_5: Profundizacion VIP - Dialogos de intimidad
            chapter_6: Archivos de Diana - Culminacion
    """
    __tablename__ = "narrative_chapters"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Identificacion
    chapter_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    subtitle = Column(String(300), nullable=True)

    # Nivel requerido
    required_level = Column(Integer, nullable=False)

    # Atmosfera (del World Builder)
    atmosphere = Column(JSON, default=dict)
    # {
    #   "visual": "Penumbra del bar, luz ambar sobre copas",
    #   "auditory": "Jazz suave, murmullo distante",
    #   "tactile": "Terciopelo de la butaca, frio del vaso",
    #   "olfactory": "Madera, cuero, tabaco vintage",
    #   "emotional": "Anticipacion contenida"
    # }

    # Tempo emocional (del Experience Designer)
    emotional_tempo = Column(String(50), nullable=True)  # allegretto, andante, adagio
    peak_moment = Column(String(200), nullable=True)  # Descripcion del climax
    breathing_room = Column(Boolean, default=False)  # Pausa narrativa

    # Orden y estado
    sequence_order = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones
    scenes = relationship(
        "NarrativeScene",
        back_populates="chapter",
        cascade="all, delete-orphan",
        order_by="NarrativeScene.sequence_order"
    )

    __table_args__ = (
        Index('idx_chapter_level_order', 'required_level', 'sequence_order'),
    )

    def __repr__(self) -> str:
        return f"<NarrativeChapter(id={self.chapter_id}, title={self.title})>"


class NarrativeScene(Base):
    """
    Escena individual dentro de un capitulo.

    Cada escena tiene:
    - Un trigger que la activa
    - Condiciones para mostrarse
    - Dialogos con variantes por arquetipo
    - Consecuencias de las decisiones
    """
    __tablename__ = "narrative_scenes"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Identificacion
    scene_id = Column(String(100), unique=True, nullable=False, index=True)
    chapter_id = Column(
        String(50),
        ForeignKey("narrative_chapters.chapter_id"),
        nullable=False,
        index=True
    )

    # Metadata
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)  # Para referencia interna

    # Personaje principal
    primary_character = Column(String(50), nullable=False)  # "diana", "lucien", "narrator"
    secondary_character = Column(String(50), nullable=True)

    # Trigger y condiciones
    trigger_event = Column(String(100), nullable=False)  # Que activa esta escena
    conditions = Column(JSON, default=dict)
    # {
    #   "level": {">=": 1},
    #   "diana_trust": {">=": 0},
    #   "flags": {"not_has": "skipped_intro"}
    # }

    # Progresion
    next_scene_default = Column(String(100), nullable=True)  # Siguiente escena por defecto
    branching_rules = Column(JSON, default=dict)
    # {
    #   "conditions": [
    #     {"if": {"archetype": "direct"}, "goto": "scene_2a"},
    #     {"if": {"diana_trust": {">=": 30}}, "goto": "scene_2b"}
    #   ],
    #   "default": "scene_2"
    # }

    # Atmosfera especifica de escena (hereda de chapter si no se especifica)
    atmosphere_override = Column(JSON, nullable=True)

    # Orden y estado
    sequence_order = Column(Integer, nullable=False)
    is_checkpoint = Column(Boolean, default=False)  # Punto de guardado narrativo
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones
    chapter = relationship("NarrativeChapter", back_populates="scenes")
    dialogues = relationship(
        "SceneDialogue",
        back_populates="scene",
        cascade="all, delete-orphan",
        order_by="SceneDialogue.sequence_order"
    )

    __table_args__ = (
        Index('idx_scene_chapter_order', 'chapter_id', 'sequence_order'),
        Index('idx_scene_trigger', 'trigger_event'),
    )

    def __repr__(self) -> str:
        return f"<NarrativeScene(id={self.scene_id}, character={self.primary_character})>"


class SceneDialogue(Base):
    """
    Dialogo dentro de una escena con variantes por arquetipo.

    El sistema de variantes permite personalizar:
    - Texto del dialogo segun arquetipo del usuario
    - Tono segun estado de relacion
    - Opciones disponibles segun patrones detectados
    """
    __tablename__ = "scene_dialogues"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Identificacion
    dialogue_id = Column(String(100), unique=True, nullable=False, index=True)
    scene_id = Column(
        String(100),
        ForeignKey("narrative_scenes.scene_id"),
        nullable=False,
        index=True
    )

    # Personaje que habla
    character = Column(String(50), nullable=False)  # "diana", "lucien", "narrator"

    # Texto base (usado si no hay variante especifica)
    base_text = Column(Text, nullable=False)

    # Variantes por arquetipo (JSON)
    archetype_variants = Column(JSON, default=dict)
    # {
    #   "introspective": "Texto para usuarios reflexivos...",
    #   "direct": "Texto para usuarios directos...",
    #   "romantic": "Texto para usuarios romanticos...",
    #   "analytical": "Texto para usuarios analiticos..."
    # }

    # Variantes por estado de relacion (JSON)
    relationship_variants = Column(JSON, default=dict)
    # {
    #   "diana_mysterious": "Cuando Diana aun es misteriosa...",
    #   "diana_revealing": "Cuando Diana empieza a abrirse...",
    #   "diana_vulnerable": "Cuando Diana es vulnerable...",
    #   "lucien_cold": "Cuando Lucien es frio...",
    #   "lucien_warming": "Cuando Lucien se ablanda...",
    #   "lucien_trusted": "Cuando Lucien confia..."
    # }

    # Estilo de entrega
    delivery_style = Column(String(50), default="normal")  # normal, whisper, dramatic, teasing
    typing_delay = Column(Float, default=0.0)  # Segundos de delay "escribiendo..."

    # Media asociada
    media = Column(JSON, nullable=True)
    # {
    #   "type": "photo",  # photo, audio, video, sticker
    #   "file_id": "AgAC...",  # File ID de Telegram
    #   "caption": "Opcional..."
    # }

    # Memorias que este dialogo puede crear
    creates_memory = Column(JSON, nullable=True)
    # {
    #   "character": "diana",
    #   "memory_type": "impression",
    #   "template": "El usuario {action} cuando {context}"
    # }

    # Orden y estado
    sequence_order = Column(Integer, nullable=False)
    requires_response = Column(Boolean, default=False)  # Usuario debe responder
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones
    scene = relationship("NarrativeScene", back_populates="dialogues")
    options = relationship(
        "DialogueOption",
        back_populates="dialogue",
        cascade="all, delete-orphan",
        order_by="DialogueOption.display_order"
    )

    __table_args__ = (
        Index('idx_dialogue_scene_order', 'scene_id', 'sequence_order'),
        Index('idx_dialogue_character', 'character'),
    )

    def get_text_for_user(
        self,
        archetype: Optional[ArchetypeType] = None,
        relationship_state: Optional[RelationshipState] = None
    ) -> str:
        """
        Obtiene el texto apropiado para el usuario.

        Prioridad:
        1. Variante de arquetipo (si existe)
        2. Variante de relacion (si existe)
        3. Texto base
        """
        # Intentar variante de arquetipo
        if archetype and self.archetype_variants:
            variant = self.archetype_variants.get(archetype.value)
            if variant:
                return variant

        # Intentar variante de relacion
        if relationship_state and self.relationship_variants:
            variant = self.relationship_variants.get(relationship_state.value)
            if variant:
                return variant

        return self.base_text

    def __repr__(self) -> str:
        return f"<SceneDialogue(id={self.dialogue_id}, character={self.character})>"


class DialogueOption(Base):
    """
    Opcion de respuesta en un dialogo.

    Cada opcion tiene:
    - Texto visible para el usuario
    - Arquetipo asociado (para tracking)
    - Consecuencias inmediatas y diferidas
    - Siguiente dialogo o escena
    """
    __tablename__ = "dialogue_options"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Identificacion
    option_id = Column(String(100), unique=True, nullable=False, index=True)
    dialogue_id = Column(
        String(100),
        ForeignKey("scene_dialogues.dialogue_id"),
        nullable=False,
        index=True
    )

    # Texto de la opcion
    text = Column(String(500), nullable=False)  # Texto visible al usuario

    # Variantes de texto por arquetipo (opcional)
    text_variants = Column(JSON, nullable=True)
    # {
    #   "introspective": "Quiero reflexionar sobre esto...",
    #   "direct": "Dime la verdad."
    # }

    # Clasificacion
    associated_archetype = Column(Enum(ArchetypeType), nullable=True)  # Que arquetipo representa
    is_default = Column(Boolean, default=False)  # Opcion por defecto si no elige

    # Condiciones para mostrar esta opcion
    visibility_conditions = Column(JSON, nullable=True)
    # {
    #   "diana_trust": {">=": 20},
    #   "pattern": {"has": "patient"}
    # }

    # Consecuencias inmediatas
    immediate_effects = Column(JSON, default=dict)
    # {
    #   "diana_trust": 5,
    #   "lucien_respect": -2,
    #   "archetype_introspective": 10,
    #   "add_flag": {"type": "choices", "name": "chose_honesty"}
    # }

    # Consecuencias diferidas
    delayed_effects = Column(JSON, nullable=True)
    # {
    #   "trigger_at_level": 3,
    #   "effect": {"unlock": "diana_remembers_choice"},
    #   "diana_dialogue": "Recuerdo que elegiste..."
    # }

    # Navegacion
    next_dialogue_id = Column(String(100), nullable=True)  # Siguiente dialogo en escena
    next_scene_id = Column(String(100), nullable=True)  # Saltar a otra escena

    # Memoria que crea la eleccion
    creates_memory = Column(JSON, nullable=True)
    # {
    #   "character": "diana",
    #   "memory_type": "choice",
    #   "content": "eligio la honestidad sobre la comodidad"
    # }

    # Orden y estado
    display_order = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones
    dialogue = relationship("SceneDialogue", back_populates="options")

    __table_args__ = (
        Index('idx_option_dialogue_order', 'dialogue_id', 'display_order'),
        Index('idx_option_archetype', 'associated_archetype'),
    )

    def get_text_for_archetype(self, archetype: Optional[ArchetypeType] = None) -> str:
        """Obtiene el texto apropiado segun arquetipo."""
        if archetype and self.text_variants:
            variant = self.text_variants.get(archetype.value)
            if variant:
                return variant
        return self.text

    def __repr__(self) -> str:
        return f"<DialogueOption(id={self.option_id}, text={self.text[:30]}...)>"
