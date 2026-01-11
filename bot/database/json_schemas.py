"""
JSON Schema Validation for Cascade Configuration System

Provides JSON schema definitions and validation functions for all
JSON fields used in the cascade configuration system and related models.

Schemas:
- StoryFragment.unlock_conditions
- StoryFragment.content_variants
- StoryChoice.consequences
- CascadeConfigPreset.preset_config
- CascadeOperation.operation_details
- BroadcastMessage.reaction_buttons
"""

import logging
from typing import Dict, Any, Tuple, List, Optional
from jsonschema import validate, ValidationError, Draft7Validator

logger = logging.getLogger(__name__)


# =============================================================================
# JSON SCHEMA DEFINITIONS
# =============================================================================

UNLOCK_CONDITIONS_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "required_choices": {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": r"^L[1-6]_[A-Z]+_[0-9]{3}$",
                "description": "Story fragment ID pattern (e.g., L1_INTRO_001)"
            },
            "description": "List of choice IDs required to unlock this fragment"
        },
        "required_flags": {
            "type": "array",
            "items": {
                "type": "string",
                "minLength": 1
            },
            "description": "List of narrative flags required"
        },
        "min_relationship_score": {
            "type": "object",
            "properties": {
                "LUCIEN": {
                    "type": "integer",
                    "minimum": -100,
                    "maximum": 100,
                    "description": "Minimum relationship score with Lucien"
                },
                "DIANA": {
                    "type": "integer",
                    "minimum": -100,
                    "maximum": 100,
                    "description": "Minimum relationship score with Diana"
                }
            },
            "additionalProperties": False
        },
        "besitos_cost": {
            "type": "integer",
            "minimum": 0,
            "description": "Besitos required to unlock this fragment"
        },
        "required_items": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "List of items required to unlock this fragment"
        },
        "min_level": {
            "type": "integer",
            "minimum": 1,
            "maximum": 6,
            "description": "Minimum narrative level required"
        },
        "min_besitos": {
            "type": "integer",
            "minimum": 0,
            "description": "Minimum total besitos required"
        }
    },
    "additionalProperties": False,
    "description": "Conditions that must be met to unlock a story fragment"
}


CONTENT_VARIANTS_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "EXPLORER": {
            "type": "string",
            "description": "Content variant for Explorer archetype"
        },
        "ROMANTIC": {
            "type": "string",
            "description": "Content variant for Romantic archetype"
        },
        "DIRECT": {
            "type": "string",
            "description": "Content variant for Direct archetype"
        },
        "ANALYTICAL": {
            "type": "string",
            "description": "Content variant for Analytical archetype"
        },
        "PERSISTENT": {
            "type": "string",
            "description": "Content variant for Persistent archetype"
        },
        "PATIENT": {
            "type": "string",
            "description": "Content variant for Patient archetype"
        }
    },
    "additionalProperties": False,
    "description": "Content variants based on user archetype"
}


CONSEQUENCES_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "flags_set": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Narrative flags to set when this choice is made"
        },
        "flags_unset": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Narrative flags to unset when this choice is made"
        },
        "archetype_points": {
            "type": "object",
            "properties": {
                "explorer": {"type": "integer"},
                "romantic": {"type": "integer"},
                "direct": {"type": "integer"},
                "analytical": {"type": "integer"},
                "persistent": {"type": "integer"},
                "patient": {"type": "integer"}
            },
            "additionalProperties": False,
            "description": "Archetype points to add/subtract"
        },
        "relationship_change": {
            "type": "object",
            "properties": {
                "LUCIEN": {
                    "type": "integer",
                    "minimum": -100,
                    "maximum": 100
                },
                "DIANA": {
                    "type": "integer",
                    "minimum": -100,
                    "maximum": 100
                }
            },
            "additionalProperties": False,
            "description": "Relationship score changes"
        },
        "besitos_reward": {
            "type": "integer",
            "minimum": 0,
            "description": "Besitos to award for this choice"
        },
        "besitos_cost": {
            "type": "integer",
            "minimum": 0,
            "description": "Besitos to deduct for this choice"
        },
        "items_gained": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Items gained when making this choice"
        },
        "items_lost": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Items lost when making this choice"
        },
        "mission_unlocked": {
            "type": "integer",
            "description": "Mission ID to unlock"
        },
        "fragment_unlocked": {
            "type": "string",
            "pattern": r"^L[1-6]_[A-Z]+_[0-9]{3}$",
            "description": "Fragment ID to unlock"
        }
    },
    "additionalProperties": False,
    "description": "Consequences of making a story choice"
}


CASCADE_PRESET_CONFIG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["entities", "dependencies"],
    "properties": {
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["type", "template"],
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["mission", "reward", "badge", "level", "story_fragment"],
                        "description": "Type of entity to create"
                    },
                    "template": {
                        "type": "object",
                        "description": "Template configuration for this entity"
                    },
                    "name": {
                        "type": "string",
                        "description": "Name for this entity (optional)"
                    }
                },
                "additionalProperties": False
            },
            "description": "List of entities to create in this preset"
        },
        "dependencies": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["from", "to", "type"],
                "properties": {
                    "from": {
                        "type": "string",
                        "description": "Source entity type or index"
                    },
                    "to": {
                        "type": "string",
                        "description": "Target entity type or index"
                    },
                    "type": {
                        "type": "string",
                        "enum": ["auto_level_up", "unlock_reward", "unlock_trigger", "auto_create"],
                        "description": "Type of dependency relationship"
                    }
                },
                "additionalProperties": False
            },
            "description": "Dependency relationships between entities"
        },
        "defaults": {
            "type": "object",
            "properties": {
                "besitos_reward": {"type": "integer", "minimum": 0},
                "mission_benefits": {"type": "string"},
                "level_name": {"type": "string"},
                "badge_icon": {"type": "string"},
                "badge_rarity": {
                    "type": "string",
                    "enum": ["common", "uncommon", "rare", "epic", "legendary"]
                }
            },
            "additionalProperties": True,
            "description": "Default values for entity creation"
        }
    },
    "additionalProperties": False,
    "description": "Cascade configuration preset template"
}


CASCADE_OPERATION_DETAILS_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "entities_created": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "id": {"type": "integer"},
                    "name": {"type": "string"}
                },
                "required": ["type", "id"]
            },
            "description": "List of entities created in this operation"
        },
        "entities_deleted": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "id": {"type": "integer"},
                    "name": {"type": "string"}
                },
                "required": ["type", "id"]
            },
            "description": "List of entities deleted in this operation"
        },
        "dependencies_validated": {
            "type": "integer",
            "minimum": 0,
            "description": "Number of dependencies validated"
        },
        "circular_dependencies_detected": {
            "type": "array",
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "id": {"type": "integer"}
                    }
                }
            },
            "description": "List of circular dependency paths detected"
        },
        "warnings": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Warning messages generated during operation"
        },
        "errors": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Error messages generated during operation"
        }
    },
    "additionalProperties": True,
    "description": "Details of cascade operation execution"
}


BROADCAST_REACTION_BUTTONS_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "array",
    "items": {
        "type": "object",
        "required": ["emoji", "reaction_type_id", "besitos"],
        "properties": {
            "emoji": {
                "type": "string",
                "minLength": 1,
                "maxLength": 10,
                "description": "Emoji to display on button"
            },
            "label": {
                "type": "string",
                "maxLength": 50,
                "description": "Text label for button"
            },
            "reaction_type_id": {
                "type": "integer",
                "minimum": 1,
                "description": "ID of reaction type from reactions table"
            },
            "besitos": {
                "type": "integer",
                "minimum": 0,
                "description": "Besitos awarded for this reaction"
            }
        },
        "additionalProperties": False
    },
    "description": "Reaction buttons for broadcast message"
}


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_json_schema(
    data: Dict[str, Any],
    schema: Dict[str, Any],
    schema_name: str = "unknown"
) -> Tuple[bool, str]:
    """Validate JSON data against schema.

    Args:
        data: JSON data to validate
        schema: JSON schema to validate against
        schema_name: Name of schema (for error messages)

    Returns:
        (is_valid, error_message)
        - is_valid: True if validation passes
        - error_message: Empty string if valid, error message if invalid
    """
    try:
        validate(instance=data, schema=schema)
        logger.debug(f"JSON validation successful for schema: {schema_name}")
        return True, ""
    except ValidationError as e:
        error_path = " -> ".join(str(p) for p in e.path) if e.path else "root"
        error_msg = (
            f"JSON validation error in '{schema_name}' at '{error_path}': {e.message}"
        )
        logger.warning(error_msg)
        return False, error_msg


def validate_unlock_conditions(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate story fragment unlock conditions.

    Args:
        data: unlock_conditions JSON data

    Returns:
        (is_valid, error_message)
    """
    return validate_json_schema(
        data,
        UNLOCK_CONDITIONS_SCHEMA,
        "unlock_conditions"
    )


def validate_content_variants(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate story fragment content variants.

    Args:
        data: content_variants JSON data

    Returns:
        (is_valid, error_message)
    """
    return validate_json_schema(
        data,
        CONTENT_VARIANTS_SCHEMA,
        "content_variants"
    )


def validate_consequences(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate story choice consequences.

    Args:
        data: consequences JSON data

    Returns:
        (is_valid, error_message)
    """
    return validate_json_schema(
        data,
        CONSEQUENCES_SCHEMA,
        "consequences"
    )


def validate_preset_config(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate cascade preset configuration.

    Args:
        data: preset_config JSON data

    Returns:
        (is_valid, error_message)
    """
    return validate_json_schema(
        data,
        CASCADE_PRESET_CONFIG_SCHEMA,
        "preset_config"
    )


def validate_operation_details(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate cascade operation details.

    Args:
        data: operation_details JSON data

    Returns:
        (is_valid, error_message)
    """
    return validate_json_schema(
        data,
        CASCADE_OPERATION_DETAILS_SCHEMA,
        "operation_details"
    )


def validate_broadcast_reaction_buttons(data: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """Validate broadcast reaction buttons configuration.

    Args:
        data: reaction_buttons JSON array

    Returns:
        (is_valid, error_message)
    """
    return validate_json_schema(
        data,
        BROADCAST_REACTION_BUTTONS_SCHEMA,
        "reaction_buttons"
    )


# =============================================================================
# BATCH VALIDATION
# =============================================================================

def validate_story_fragment_data(
    unlock_conditions: Optional[Dict[str, Any]] = None,
    content_variants: Optional[Dict[str, Any]] = None
) -> Tuple[bool, List[str]]:
    """Validate all JSON fields in a story fragment.

    Args:
        unlock_conditions: unlock_conditions JSON data
        content_variants: content_variants JSON data

    Returns:
        (is_valid, error_messages)
        - is_valid: True if all validations pass
        - error_messages: List of error messages (empty if valid)
    """
    errors = []

    if unlock_conditions is not None:
        is_valid, error_msg = validate_unlock_conditions(unlock_conditions)
        if not is_valid:
            errors.append(error_msg)

    if content_variants is not None:
        is_valid, error_msg = validate_content_variants(content_variants)
        if not is_valid:
            errors.append(error_msg)

    is_valid = len(errors) == 0
    return is_valid, errors


def validate_story_choice_data(
    consequences: Optional[Dict[str, Any]] = None
) -> Tuple[bool, List[str]]:
    """Validate all JSON fields in a story choice.

    Args:
        consequences: consequences JSON data

    Returns:
        (is_valid, error_messages)
    """
    errors = []

    if consequences is not None:
        is_valid, error_msg = validate_consequences(consequences)
        if not is_valid:
            errors.append(error_msg)

    is_valid = len(errors) == 0
    return is_valid, errors


# =============================================================================
# SCHEMA COMPILATION (Performance Optimization)
# =============================================================================

# Compile validators once for better performance
_unlock_conditions_validator = Draft7Validator(UNLOCK_CONDITIONS_SCHEMA)
_content_variants_validator = Draft7Validator(CONTENT_VARIANTS_SCHEMA)
_consequences_validator = Draft7Validator(CONSEQUENCES_SCHEMA)
_preset_config_validator = Draft7Validator(CASCADE_PRESET_CONFIG_SCHEMA)
_operation_details_validator = Draft7Validator(CASCADE_OPERATION_DETAILS_SCHEMA)
_reaction_buttons_validator = Draft7Validator(BROADCAST_REACTION_BUTTONS_SCHEMA)


def validate_unlock_conditions_fast(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Fast validation using pre-compiled validator.

    Args:
        data: unlock_conditions JSON data

    Returns:
        (is_valid, error_message)
    """
    try:
        _unlock_conditions_validator.validate(data)
        return True, ""
    except ValidationError as e:
        return False, f"Validation error: {e.message}"


def validate_preset_config_fast(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Fast validation using pre-compiled validator.

    Args:
        data: preset_config JSON data

    Returns:
        (is_valid, error_message)
    """
    try:
        _preset_config_validator.validate(data)
        return True, ""
    except ValidationError as e:
        return False, f"Validation error: {e.message}"
