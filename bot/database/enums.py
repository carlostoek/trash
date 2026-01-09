"""
Enums para el sistema.

Define enumeraciones usadas en los modelos.
"""
from enum import Enum


class NarrativeLevel(int, Enum):
    """
    Niveles de progresión narrativa.

    Estructura:
        1-3: Los Kinkys (canal Free) - Introducción y evaluación
        4-6: El Diván (canal VIP) - Intimidad profunda
    """
    LEVEL_1 = 1  # Bienvenida, primer contacto con Lucien
    LEVEL_2 = 2  # Profundización gratuita, misiones de observación
    LEVEL_3 = 3  # Culminación gratuita, perfil de deseo
    LEVEL_4 = 4  # Entrada VIP, evaluación de comprensión
    LEVEL_5 = 5  # Profundización VIP, diálogos de intimidad
    LEVEL_6 = 6  # Archivos de Diana, culminación

    @property
    def channel(self) -> str:
        """Retorna el canal correspondiente al nivel."""
        return "los_kinkys" if self.value <= 3 else "el_divan"

    @property
    def is_vip_required(self) -> bool:
        """Indica si requiere suscripción VIP."""
        return self.value >= 4


class DecisionType(str, Enum):
    """
    Tipos de decisiones que puede tomar el usuario.

    Categories:
        TIMING: Velocidad de respuesta (inmediato/considerado/tardío)
        CONTENT: Contenido de la elección (qué selecciona)
        REACTION: Reacciones a mensajes (emojis)
        DIALOGUE: Respuestas en diálogos
        MISSION: Completar misiones/desafíos
    """
    TIMING = "timing"
    CONTENT = "content"
    REACTION = "reaction"
    DIALOGUE = "dialogue"
    MISSION = "mission"


class PatternType(str, Enum):
    """
    Patrones de comportamiento detectados.

    Patterns:
        IMPULSIVE: Responde muy rápido (<30s)
        PATIENT: Toma su tiempo (>5min)
        CONSISTENT: Mismo arquetipo en múltiples decisiones
        ERRATIC: Cambia frecuentemente de estilo
        ENGAGED: Alta participación
        PASSIVE: Baja participación
    """
    IMPULSIVE = "impulsive"
    PATIENT = "patient"
    CONSISTENT = "consistent"
    ERRATIC = "erratic"
    ENGAGED = "engaged"
    PASSIVE = "passive"


class ArchetypeType(str, Enum):
    """
    Arquetipos de personalidad del usuario.

    Cada usuario tiene un arquetipo primario y uno secundario.
    Los personajes (Diana, Lucien) adaptan su diálogo según el arquetipo.

    Archetypes:
        INTROSPECTIVE: Reflexivo, pregunta "por qué"
        DIRECT: Honesto, sin juegos, va al grano
        ROMANTIC: Enfocado en conexión emocional
        ANALYTICAL: Busca patrones y reglas
    """
    INTROSPECTIVE = "introspective"
    DIRECT = "direct"
    ROMANTIC = "romantic"
    ANALYTICAL = "analytical"

    @property
    def diana_response_style(self) -> str:
        """Cómo Diana responde a este arquetipo."""
        styles = {
            ArchetypeType.INTROSPECTIVE: "opens_inner_world",
            ArchetypeType.DIRECT: "appreciates_honesty",
            ArchetypeType.ROMANTIC: "leans_into_seduction",
            ArchetypeType.ANALYTICAL: "challenges_intellectually"
        }
        return styles[self]

    @property
    def lucien_response_style(self) -> str:
        """Cómo Lucien responde a este arquetipo."""
        styles = {
            ArchetypeType.INTROSPECTIVE: "respects_depth",
            ArchetypeType.DIRECT: "respects_clarity",
            ArchetypeType.ROMANTIC: "warns_gently",
            ArchetypeType.ANALYTICAL: "appreciates_intelligence"
        }
        return styles[self]


class ConsequenceType(str, Enum):
    """
    Tipos de consecuencias de las decisiones.

    Types:
        UNLOCK: Desbloquea contenido
        BLOCK: Bloquea contenido temporal o permanentemente
        MODIFY: Modifica diálogo o escena
        BRANCH: Cambia rama narrativa
        REWARD: Otorga recompensa
        RELATIONSHIP: Modifica relación con personaje
    """
    UNLOCK = "unlock"
    BLOCK = "block"
    MODIFY = "modify"
    BRANCH = "branch"
    REWARD = "reward"
    RELATIONSHIP = "relationship"


class RelationshipState(str, Enum):
    """
    Estados de relación con los personajes.

    Diana States:
        MYSTERIOUS: < 40 confianza
        REVEALING: 40-70 confianza
        VULNERABLE: > 70 confianza

    Lucien States:
        COLD: < 30 respeto
        WARMING: 30-60 respeto
        TRUSTED: > 60 respeto
    """
    # Diana states
    DIANA_MYSTERIOUS = "diana_mysterious"
    DIANA_REVEALING = "diana_revealing"
    DIANA_VULNERABLE = "diana_vulnerable"

    # Lucien states
    LUCIEN_COLD = "lucien_cold"
    LUCIEN_WARMING = "lucien_warming"
    LUCIEN_TRUSTED = "lucien_trusted"


class UserRole(str, Enum):
    """
    Roles de usuario en el sistema.

    Roles:
        FREE: Usuario con acceso al canal Free (default)
        VIP: Usuario con suscripción VIP activa
        ADMIN: Administrador del bot

    Transiciones automáticas:
        - Nuevo usuario → FREE
        - Activar token VIP → VIP
        - Expirar suscripción → FREE
        - Asignación manual → ADMIN
    """

    FREE = "free"
    VIP = "vip"
    ADMIN = "admin"

    def __str__(self) -> str:
        """Retorna valor string del enum."""
        return self.value

    @property
    def display_name(self) -> str:
        """Retorna nombre legible del rol."""
        names = {
            UserRole.FREE: "Usuario Free",
            UserRole.VIP: "Usuario VIP",
            UserRole.ADMIN: "Administrador"
        }
        return names[self]

    @property
    def emoji(self) -> str:
        """Retorna emoji del rol."""
        emojis = {
            UserRole.FREE: "🆓",
            UserRole.VIP: "⭐",
            UserRole.ADMIN: "👑"
        }
        return emojis[self]
