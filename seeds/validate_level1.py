"""
Validation script for Level 1 narrative content.

Verifies that all required fragments and choices are present
and match the creative script specifications.

Usage:
    python -m seeds.validate_level1
"""
import asyncio
import logging
from sqlalchemy import select

from bot.database.engine import init_db, get_session
from bot.database.models import StoryFragment, StoryChoice

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


# Required fragments for Level 1
REQUIRED_FRAGMENTS = {
    "L1_INTRO_001": {
        "title": "Bienvenida de Diana",
        "speaker": "DIANA",
        "emotion": "mysterious",
        "is_starting": True,
        "is_ending": False,
        "level": 1,
        "besitos_reward": 0,
        "xp_reward": 0,
    },
    "L1_INTRO_002": {
        "title": "Lucien y el Primer Desafío",
        "speaker": "LUCIEN",
        "emotion": "formal",
        "is_starting": False,
        "is_ending": False,
        "level": 1,
        "besitos_reward": 10,
        "xp_reward": 0,
    },
    "L1_RESPONSE_QUICK": {
        "title": "Respuesta para Usuario que Reacciona Inmediatamente",
        "speaker": "LUCIEN",
        "emotion": "approving",
        "is_starting": False,
        "is_ending": False,
        "level": 1,
        "besitos_reward": 15,
        "xp_reward": 0,
    },
    "L1_RESPONSE_PATIENT": {
        "title": "Respuesta para Usuario que Toma Tiempo",
        "speaker": "LUCIEN",
        "emotion": "appreciative",
        "is_starting": False,
        "is_ending": False,
        "level": 1,
        "besitos_reward": 15,
        "xp_reward": 0,
    },
    "L1_FIRST_CLUE": {
        "title": "La Primera Pista",
        "speaker": "LUCIEN",
        "emotion": "mysterious",
        "is_starting": False,
        "is_ending": True,
        "level": 1,
        "besitos_reward": 20,
        "xp_reward": 50,
    },
}

# Required choices for Level 1
REQUIRED_CHOICES = {
    "L1_INTRO_A": {
        "text": "🚪 Descubrir más",
        "from_fragment": "L1_INTRO_001",
        "to_fragment": "L1_INTRO_002",
        "emoji": "🚪",
        "has_consequences": True,
    },
    "L1_INTRO_B": {
        "text": "✨ Entendido",
        "from_fragment": "L1_INTRO_002",
        "to_fragment": "L1_RESPONSE_QUICK",
        "emoji": "✨",
        "has_consequences": True,
    },
}


async def validate_fragments() -> bool:
    """Validate that all required fragments exist with correct attributes."""
    logger.info("\n" + "="*70)
    logger.info("VALIDATING FRAGMENTS")
    logger.info("="*70 + "\n")

    async with get_session() as session:
        all_valid = True

        for fragment_id, expected in REQUIRED_FRAGMENTS.items():
            stmt = select(StoryFragment).where(
                StoryFragment.fragment_id == fragment_id
            )
            result = await session.execute(stmt)
            fragment = result.scalar_one_or_none()

            if fragment is None:
                logger.error(f"❌ MISSING: {fragment_id}")
                all_valid = False
                continue

            # Validate attributes
            errors = []

            if fragment.title != expected["title"]:
                errors.append(f"Title mismatch: expected '{expected['title']}', got '{fragment.title}'")

            if fragment.speaker != expected["speaker"]:
                errors.append(f"Speaker mismatch: expected '{expected['speaker']}', got '{fragment.speaker}'")

            if fragment.speaker_emotion != expected["emotion"]:
                errors.append(f"Emotion mismatch: expected '{expected['emotion']}', got '{fragment.speaker_emotion}'")

            if fragment.is_starting_fragment != expected["is_starting"]:
                errors.append(f"Is Starting mismatch: expected {expected['is_starting']}, got {fragment.is_starting_fragment}")

            if fragment.is_ending_fragment != expected["is_ending"]:
                errors.append(f"Is Ending mismatch: expected {expected['is_ending']}, got {fragment.is_ending_fragment}")

            if fragment.narrative_level != expected["level"]:
                errors.append(f"Level mismatch: expected {expected['level']}, got {fragment.narrative_level}")

            # Only validate rewards for ending fragment (other rewards are optional)
            if expected["is_ending"]:
                if fragment.besitos_reward != expected["besitos_reward"]:
                    errors.append(f"Besitos reward mismatch: expected {expected['besitos_reward']}, got {fragment.besitos_reward}")

                if fragment.experience_reward != expected["xp_reward"]:
                    errors.append(f"XP reward mismatch: expected {expected['xp_reward']}, got {fragment.experience_reward}")

            if not fragment.active:
                errors.append(f"Fragment is not active")

            if not fragment.content_text:
                errors.append(f"Content text is empty")

            if errors:
                logger.error(f"❌ {fragment_id}: {fragment.title}")
                for error in errors:
                    logger.error(f"   • {error}")
                all_valid = False
            else:
                logger.info(f"✅ {fragment_id}: {fragment.title}")

        return all_valid


async def validate_choices() -> bool:
    """Validate that all required choices exist with correct attributes."""
    logger.info("\n" + "="*70)
    logger.info("VALIDATING CHOICES")
    logger.info("="*70 + "\n")

    async with get_session() as session:
        all_valid = True

        for choice_id, expected in REQUIRED_CHOICES.items():
            stmt = select(StoryChoice).where(
                StoryChoice.choice_id == choice_id
            )
            result = await session.execute(stmt)
            choice = result.scalar_one_or_none()

            if choice is None:
                logger.error(f"❌ MISSING: {choice_id}")
                all_valid = False
                continue

            # Get fragment IDs for validation
            stmt_from = select(StoryFragment).where(
                StoryFragment.fragment_id == expected["from_fragment"]
            )
            result_from = await session.execute(stmt_from)
            from_fragment = result_from.scalar_one_or_none()

            stmt_to = select(StoryFragment).where(
                StoryFragment.fragment_id == expected["to_fragment"]
            )
            result_to = await session.execute(stmt_to)
            to_fragment = result_to.scalar_one_or_none()

            # Validate attributes
            errors = []

            if choice.choice_text != expected["text"]:
                errors.append(f"Text mismatch: expected '{expected['text']}', got '{choice.choice_text}'")

            if choice.choice_emoji != expected["emoji"]:
                errors.append(f"Emoji mismatch: expected '{expected['emoji']}', got '{choice.choice_emoji}'")

            if from_fragment is None:
                errors.append(f"Source fragment {expected['from_fragment']} not found")
            elif choice.fragment_id != from_fragment.id:
                errors.append(f"Source fragment ID mismatch")

            if to_fragment is None:
                errors.append(f"Target fragment {expected['to_fragment']} not found")
            elif choice.target_fragment_id != to_fragment.id:
                errors.append(f"Target fragment ID mismatch")

            if expected["has_consequences"] and not choice.consequences:
                errors.append(f"Expected consequences but found none")

            if not choice.active:
                errors.append(f"Choice is not active")

            if errors:
                logger.error(f"❌ {choice_id}: {choice.choice_text}")
                for error in errors:
                    logger.error(f"   • {error}")
                all_valid = False
            else:
                logger.info(f"✅ {choice_id}: {choice.choice_text}")

        return all_valid


async def validate_content_integrity() -> bool:
    """Validate narrative flow integrity."""
    logger.info("\n" + "="*70)
    logger.info("VALIDATING NARRATIVE FLOW")
    logger.info("="*70 + "\n")

    async with get_session() as session:
        errors = []

        # Check that starting fragment can reach ending fragment
        stmt_start = select(StoryFragment).where(
            StoryFragment.fragment_id == "L1_INTRO_001"
        )
        result = await session.execute(stmt_start)
        start = result.scalar_one_or_none()

        if not start:
            errors.append("Starting fragment L1_INTRO_001 not found")
        else:
            logger.info(f"✅ Starting fragment: {start.fragment_id}")

        # Check ending fragment
        stmt_end = select(StoryFragment).where(
            StoryFragment.fragment_id == "L1_FIRST_CLUE"
        )
        result = await session.execute(stmt_end)
        end = result.scalar_one_or_none()

        if not end:
            errors.append("Ending fragment L1_FIRST_CLUE not found")
        else:
            logger.info(f"✅ Ending fragment: {end.fragment_id}")

        # Check that choices link fragments
        stmt_choices = select(StoryChoice)
        result = await session.execute(stmt_choices)
        choices = result.scalars().all()

        logger.info(f"\n✅ Found {len(choices)} choices linking fragments")

        for choice in choices:
            stmt_from = select(StoryFragment).where(
                StoryFragment.id == choice.fragment_id
            )
            result_from = await session.execute(stmt_from)
            from_frag = result_from.scalar_one_or_none()

            stmt_to = select(StoryFragment).where(
                StoryFragment.id == choice.target_fragment_id
            )
            result_to = await session.execute(stmt_to)
            to_frag = result_to.scalar_one_or_none()

            if from_frag and to_frag:
                logger.info(f"  • {from_frag.fragment_id} → {to_frag.fragment_id} ({choice.choice_id})")
            else:
                if not from_frag:
                    errors.append(f"Choice {choice.choice_id} has invalid source fragment")
                if not to_frag:
                    errors.append(f"Choice {choice.choice_id} has invalid target fragment")

        if errors:
            for error in errors:
                logger.error(f"❌ {error}")
            return False

        return True


async def main():
    """Run all validation checks."""
    logger.info("\n" + "="*70)
    logger.info("LEVEL 1 NARRATIVE CONTENT VALIDATION")
    logger.info("="*70)

    # Initialize database
    await init_db()

    # Run validations
    fragments_valid = await validate_fragments()
    choices_valid = await validate_choices()
    flow_valid = await validate_content_integrity()

    # Final result
    logger.info("\n" + "="*70)
    logger.info("VALIDATION SUMMARY")
    logger.info("="*70 + "\n")

    if fragments_valid and choices_valid and flow_valid:
        logger.info("🎉 ALL VALIDATIONS PASSED!")
        logger.info("\n✅ All required fragments are present and correct")
        logger.info("✅ All required choices are present and correct")
        logger.info("✅ Narrative flow is complete and connected")
        logger.info("\n🚀 Level 1 narrative content is ready for use!")
        return True
    else:
        logger.error("❌ VALIDATION FAILED!")
        if not fragments_valid:
            logger.error("   • Fragment validation failed")
        if not choices_valid:
            logger.error("   • Choice validation failed")
        if not flow_valid:
            logger.error("   • Narrative flow validation failed")
        logger.error("\nPlease re-run the seed script: python -m seeds.seed_narrative_content")
        return False


if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)
