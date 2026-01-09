"""
Database module - Models, engine y sesiones.
"""
from bot.database.base import Base
from bot.database.models import (
    BotConfig,
    InvitationToken,
    VIPSubscriber,
    FreeChannelRequest,
    User
)
from bot.database.engine import (
    init_db,
    close_db,
    get_session,
    get_engine,
    get_session_factory
)
from bot.database.narrative_models import (
    UserNarrativeState,
    UserDecision,
    UserBehaviorPattern,
    NarrativeConsequence,
    AppliedConsequence,
    CharacterRelationship
)
from bot.database.scene_models import (
    NarrativeChapter,
    NarrativeScene,
    SceneDialogue,
    DialogueOption
)
from bot.database.enums import (
    NarrativeLevel,
    DecisionType,
    PatternType,
    ArchetypeType,
    ConsequenceType,
    RelationshipState,
    UserRole
)

__all__ = [
    # Base
    "Base",

    # Core Models
    "BotConfig",
    "InvitationToken",
    "VIPSubscriber",
    "FreeChannelRequest",
    "User",

    # Narrative Models
    "UserNarrativeState",
    "UserDecision",
    "UserBehaviorPattern",
    "NarrativeConsequence",
    "AppliedConsequence",
    "CharacterRelationship",

    # Scene Models
    "NarrativeChapter",
    "NarrativeScene",
    "SceneDialogue",
    "DialogueOption",

    # Enums
    "NarrativeLevel",
    "DecisionType",
    "PatternType",
    "ArchetypeType",
    "ConsequenceType",
    "RelationshipState",
    "UserRole",

    # Engine & Sessions
    "init_db",
    "close_db",
    "get_session",
    "get_engine",
    "get_session_factory",
]
