"""
Cascade Configuration System - Database Models

This module defines the database models for the cascade configuration system,
which enables automatic creation and management of dependent entities (missions,
rewards, levels, badges, story fragments).

Tables:
- CascadeDependency: Tracks explicit dependency relationships
- CascadeOperation: Audit log for cascade operations
- CascadeConfigPreset: Predefined configuration templates
"""

import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text,
    BigInteger, JSON, ForeignKey, Index, Enum
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from bot.database.base import Base

logger = logging.getLogger(__name__)


class CascadeDependency(Base):
    """Explicit dependency relationship for cascade configuration.

    Tracks which entities depend on others to enable:
    - Cascade deletion (delete Mission → delete dependent Rewards)
    - Dependency validation (prevent circular dependencies)
    - Impact analysis (show what will be affected by deletion)
    - Auto-creation workflow (create dependents automatically)

    Attributes:
        id: Unique identifier
        dependent_type: Type of dependent entity (mission, reward, badge, level, story_fragment)
        dependent_id: ID of dependent entity
        prerequisite_type: Type of prerequisite entity
        prerequisite_id: ID of prerequisite entity
        dependency_type: Type of dependency (auto_create, manual_link, unlock_trigger)
        created_by: User ID of admin who created dependency
        created_at: Timestamp when dependency was created

    Example:
        Mission(id=5) depends_on Level(id=3)
        Reward(id=10) depends_on Mission(id=5)
    """
    __tablename__ = "cascade_dependencies"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Dependent entity (the child)
    dependent_type = Column(String(50), nullable=False)  # "mission", "reward", "badge", "level", "story_fragment"
    dependent_id = Column(Integer, nullable=False)  # ID of the dependent entity

    # Prerequisite entity (the parent)
    prerequisite_type = Column(String(50), nullable=False)  # "mission", "reward", "level", etc
    prerequisite_id = Column(Integer, nullable=False)  # ID of the prerequisite entity

    # Dependency metadata
    dependency_type = Column(String(50), nullable=False)  # "auto_create", "manual_link", "unlock_trigger"
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Índices compuestos
    __table_args__ = (
        Index(
            'idx_cascade_dependent',
            'dependent_type', 'dependent_id'
        ),
        Index(
            'idx_cascade_prerequisite',
            'prerequisite_type', 'prerequisite_id'
        ),
        Index(
            'idx_cascade_unique',
            'dependent_type', 'dependent_id', 'prerequisite_type', 'prerequisite_id',
            unique=True  # Prevent duplicate dependency records
        ),
        Index(
            'idx_cascade_type',
            'dependency_type'
        ),
    )

    @property
    def dependent_key(self) -> str:
        """Return key for dependent entity."""
        return f"{self.dependent_type}:{self.dependent_id}"

    @property
    def prerequisite_key(self) -> str:
        """Return key for prerequisite entity."""
        return f"{self.prerequisite_type}:{self.prerequisite_id}"

    def __repr__(self):
        return (
            f"<CascadeDependency({self.dependent_key} → {self.prerequisite_key}, "
            f"type={self.dependency_type})>"
        )


class CascadeOperation(Base):
    """Audit log for cascade configuration operations.

    Tracks all operations performed by the cascade system:
    - Auto-creation of dependent entities
    - Cascade deletions
    - Dependency validations
    - Failed operations (for debugging)

    Enables:
    - Rollback of operations
    - Debugging cascade workflows
    - Audit trail for admin actions
    - Performance monitoring

    Attributes:
        id: Unique identifier
        operation_type: Type of operation (auto_create, cascade_delete, validate, rollback)
        entity_type: Type of affected entity
        entity_id: ID of affected entity (null for batch ops)
        triggered_by: User ID of admin or null (system)
        trigger_type: What triggered operation (manual_create, auto_cascade, admin_delete)
        trigger_entity_type: Type of entity that triggered operation
        trigger_entity_id: ID of trigger entity
        status: Operation result (success, failed, partial, rolled_back)
        error_message: Error details if failed
        operation_details: JSON with operation-specific data
        started_at: Operation start timestamp
        completed_at: Operation completion timestamp
        duration_ms: Operation duration in milliseconds
        rolled_back: Whether operation was rolled back
        rollback_operation_id: ID of rollback operation
    """
    __tablename__ = "cascade_operations_log"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Operation details
    operation_type = Column(String(50), nullable=False)  # "auto_create", "cascade_delete", "validate", "rollback"
    entity_type = Column(String(50), nullable=False)  # "mission", "reward", "level", etc
    entity_id = Column(Integer, nullable=True)  # ID of affected entity (null for batch ops)

    # Operation metadata
    triggered_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)  # Admin user_id or null (system)
    trigger_type = Column(String(50), nullable=False)  # "manual_create", "auto_cascade", "admin_delete"
    trigger_entity_type = Column(String(50), nullable=True)  # What triggered this operation
    trigger_entity_id = Column(Integer, nullable=True)  # ID of trigger entity

    # Operation result
    status = Column(String(20), nullable=False)  # "success", "failed", "partial", "rolled_back"
    error_message = Column(Text, nullable=True)  # Error details if failed

    # Operation details (JSON)
    operation_details = Column(JSON, nullable=True)
    # Example:
    # {
    #   "entities_created": [
    #     {"type": "reward", "id": 15, "name": "Badge X"},
    #     {"type": "level", "id": 5, "name": "Level Y"}
    #   ],
    #   "entities_deleted": [
    #     {"type": "mission", "id": 10, "name": "Mission Z"}
    #   ],
    #   "dependencies_validated": 5,
    #   "circular_dependencies_detected": []
    # }

    # Timing
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)  # Operation duration in milliseconds

    # Rollback support
    rolled_back = Column(Boolean, default=False, nullable=False)
    rollback_operation_id = Column(Integer, nullable=True)  # ID of rollback operation

    # Índices
    __table_args__ = (
        Index('idx_cascade_op_entity', 'entity_type', 'entity_id'),
        Index('idx_cascade_op_trigger', 'trigger_entity_type', 'trigger_entity_id'),
        Index('idx_cascade_op_status', 'status'),
        Index('idx_cascade_op_date', 'started_at'),
        Index('idx_cascade_op_user', 'triggered_by'),
    )

    @property
    def is_success(self) -> bool:
        """Check if operation completed successfully."""
        return self.status == "success"

    @property
    def is_failed(self) -> bool:
        """Check if operation failed."""
        return self.status == "failed"

    @property
    def duration_seconds(self) -> Optional[float]:
        """Return operation duration in seconds."""
        if self.duration_ms is None:
            return None
        return self.duration_ms / 1000.0

    @property
    def entities_created_count(self) -> int:
        """Return number of entities created in this operation."""
        if self.operation_details is None:
            return 0
        return len(self.operation_details.get("entities_created", []))

    @property
    def entities_deleted_count(self) -> int:
        """Return number of entities deleted in this operation."""
        if self.operation_details is None:
            return 0
        return len(self.operation_details.get("entities_deleted", []))

    def __repr__(self):
        return (
            f"<CascadeOperation(id={self.id}, type={self.operation_type}, "
            f"entity={self.entity_type}:{self.entity_id}, status={self.status})>"
        )


class CascadeConfigPreset(Base):
    """Predefined cascade configuration template.

    Stores common cascade patterns that admins can quickly apply:
    - Mission + Level + Badge (standard quest pattern)
    - Mission + Multiple Rewards (achievement pattern)
    - Story Sequence (narrative chain pattern)
    - Level-Up Chain (progression pattern)

    Benefits:
    - Faster configuration (apply preset instead of manual setup)
    - Consistency (all admins use same patterns)
    - Best practices (presets encode proven configurations)
    - Reduced errors (no manual entity linking)

    Attributes:
        id: Unique identifier
        name: Unique preset name (machine-readable)
        display_name: Human-readable display name
        description: Detailed description
        category: Category (gamification, narrative, progression, achievement)
        tags: List of tags for filtering
        preset_config: JSON configuration with entities and dependencies
        is_active: Whether preset is available for use
        is_system: Whether preset is system-defined (cannot be deleted)
        usage_count: Number of times preset has been used
        version: Semantic version string
        created_by: User ID of admin who created preset
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "cascade_config_presets"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Preset identification
    name = Column(String(100), unique=True, nullable=False)  # "standard_quest", "achievement_bundle"
    display_name = Column(String(200), nullable=False)  # "Standard Quest (Mission + Level + Badge)"
    description = Column(Text, nullable=True)  # Detailed description

    # Category
    category = Column(String(50), nullable=False)  # "gamification", "narrative", "progression", "achievement"
    tags = Column(JSON, default=list)  # ["popular", "beginner_friendly", "vip_content"]

    # Preset configuration (JSON)
    preset_config = Column(JSON, nullable=False)
    # Example:
    # {
    #   "entities": [
    #     {"type": "mission", "template": {"mission_type": "daily", "repeatable": true}},
    #     {"type": "level", "template": {"auto_unlock": true}},
    #     {"type": "badge", "template": {"rarity": "common"}}
    #   ],
    #   "dependencies": [
    #     {"from": "mission", "to": "level", "type": "auto_level_up"},
    #     {"from": "mission", "to": "badge", "type": "unlock_reward"}
    #   ],
    #   "defaults": {
    #     "besitos_reward": 100,
    #     "mission_benefits": "Access to VIP channel"
    #   }
    # }

    # Preset metadata
    is_active = Column(Boolean, default=True, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)  # System presets cannot be deleted
    usage_count = Column(Integer, default=0, nullable=False)  # Track popularity

    # Versioning
    version = Column(String(20), nullable=False, default="1.0")  # Semantic versioning
    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda ctx: datetime.now(timezone.utc))

    # Índices
    __table_args__ = (
        Index('idx_cascade_preset_category', 'category'),
        Index('idx_cascade_preset_active', 'is_active', 'is_system'),
        Index('idx_cascade_preset_usage', 'usage_count'),
    )

    @property
    def entity_types(self) -> List[str]:
        """Return list of entity types in this preset."""
        if self.preset_config is None or "entities" not in self.preset_config:
            return []
        return [entity["type"] for entity in self.preset_config["entities"]]

    @property
    def dependency_count(self) -> int:
        """Return number of dependencies in this preset."""
        if self.preset_config is None or "dependencies" not in self.preset_config:
            return 0
        return len(self.preset_config["dependencies"])

    @property
    def is_popular(self) -> bool:
        """Check if preset is popular (used > 10 times)."""
        return self.usage_count > 10

    def increment_usage(self) -> None:
        """Increment usage count (called when preset is applied)."""
        self.usage_count += 1
        self.updated_at = datetime.now(timezone.utc)

    def __repr__(self):
        return (
            f"<CascadeConfigPreset(name='{self.name}', "
            f"category='{self.category}', "
            f"usage={self.usage_count}, "
            f"version={self.version})>"
        )


# Valid entity types for cascade configuration
VALID_CASCADE_ENTITY_TYPES = [
    "mission",
    "reward",
    "badge",
    "level",
    "story_fragment",
    "user_gamification",
    "broadcast_message"
]

# Valid dependency types
VALID_DEPENDENCY_TYPES = [
    "auto_create",      # Automatically created when parent is created
    "manual_link",      # Manually linked by admin
    "unlock_trigger",   # Unlocked when parent condition is met
    "auto_level_up",    # Mission auto-level-up to Level
    "unlock_reward"     # Mission unlocks Reward
]

# Valid operation types
VALID_OPERATION_TYPES = [
    "auto_create",      # Auto-creation of dependent entities
    "cascade_delete",   # Cascade deletion of dependents
    "validate",         # Validation of dependencies
    "rollback",         # Rollback of previous operation
    "migrate"           # Migration of existing dependencies
]

# Valid operation statuses
VALID_OPERATION_STATUSES = [
    "success",          # Operation completed successfully
    "failed",           # Operation failed
    "partial",          # Partial completion (some entities created)
    "rolled_back"       # Operation was rolled back
]


def validate_cascade_entity_type(entity_type: str) -> bool:
    """Validate entity type for cascade configuration.

    Args:
        entity_type: Type to validate

    Returns:
        True if valid, False otherwise
    """
    return entity_type in VALID_CASCADE_ENTITY_TYPES


def validate_dependency_type(dependency_type: str) -> bool:
    """Validate dependency type.

    Args:
        dependency_type: Type to validate

    Returns:
        True if valid, False otherwise
    """
    return dependency_type in VALID_DEPENDENCY_TYPES


def validate_operation_type(operation_type: str) -> bool:
    """Validate operation type.

    Args:
        operation_type: Type to validate

    Returns:
        True if valid, False otherwise
    """
    return operation_type in VALID_OPERATION_TYPES


def validate_operation_status(status: str) -> bool:
    """Validate operation status.

    Args:
        status: Status to validate

    Returns:
        True if valid, False otherwise
    """
    return status in VALID_OPERATION_STATUSES
