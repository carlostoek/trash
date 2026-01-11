"""
Migration to add Level 2 to 3 connection.

This adds choices from L2_SUCCESS_003 and L2_PARTIAL_004 to L3_CONTINUE_001.

Usage:
    python -m migrations.add_level_2_to_3_connection
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import select
from bot.database import get_session, init_db
from bot.database.models import StoryFragment, StoryChoice

logger = logging.getLogger(__name__)


async def migrate():
    """Connect Level 2 endings to Level 3."""
    logger.info("🔧 Starting Level 2 to 3 connection migration...")

    await init_db()

    async with get_session() as session:
        # Get Level 2 ending fragments
        l2_success = await session.execute(
            select(StoryFragment).where(
                StoryFragment.fragment_id == "L2_SUCCESS_003"
            )
        )
        l2_success_frag = l2_success.scalar_one_or_none()

        l2_partial = await session.execute(
            select(StoryFragment).where(
                StoryFragment.fragment_id == "L2_PARTIAL_004"
            )
        )
        l2_partial_frag = l2_partial.scalar_one_or_none()

        # Get Level 3 starting fragment
        l3_continue = await session.execute(
            select(StoryFragment).where(
                StoryFragment.fragment_id == "L3_CONTINUE_001"
            )
        )
        l3_continue_frag = l3_continue.scalar_one_or_none()

        if not all([l2_success_frag, l2_partial_frag, l3_continue_frag]):
            logger.error("  ✗ Missing required fragments")
            logger.error(f"    L2_SUCCESS_003: {'✓' if l2_success_frag else '✗'}")
            logger.error(f"    L2_PARTIAL_004: {'✓' if l2_partial_frag else '✗'}")
            logger.error(f"    L3_CONTINUE_001: {'✓' if l3_continue_frag else '✗'}")
            return

        # Add choice from L2_SUCCESS_003 to L3_CONTINUE_001
        stmt_success = select(StoryChoice).where(
            StoryChoice.choice_id == "L2_CONTINUE_A"
        )
        result_success = await session.execute(stmt_success)
        existing_success = result_success.scalar_one_or_none()

        if not existing_success:
            continue_from_success = StoryChoice(
                choice_id="L2_CONTINUE_A",
                fragment_id=l2_success_frag.id,
                target_fragment_id=l3_continue_frag.id,
                choice_text="📖 Continuar al Nivel 3",
                choice_description="Diana quiere conocerte mejor",
                sort_order=1,
                active=True,
                consequences={
                    "flags_set": ["level_2_complete", "l2_observation_success"],
                    "relationship_change": {
                        "DIANA": +10,
                        "LUCIEN": +5
                    },
                    "besitos_reward": 20
                }
            )
            session.add(continue_from_success)
            logger.info("  + Created L2_CONTINUE_A (from L2_SUCCESS_003)")
        else:
            logger.info("  ⊙ L2_CONTINUE_A already exists")

        # Add choice from L2_PARTIAL_004 to L3_CONTINUE_001
        stmt_partial = select(StoryChoice).where(
            StoryChoice.choice_id == "L2_CONTINUE_B"
        )
        result_partial = await session.execute(stmt_partial)
        existing_partial = result_partial.scalar_one_or_none()

        if not existing_partial:
            continue_from_partial = StoryChoice(
                choice_id="L2_CONTINUE_B",
                fragment_id=l2_partial_frag.id,
                target_fragment_id=l3_continue_frag.id,
                choice_text="📖 Continuar al Nivel 3",
                choice_description="A pesar de todo, Diana quiere conocerte",
                sort_order=1,
                active=True,
                consequences={
                    "flags_set": ["level_2_complete", "l2_observation_partial"],
                    "relationship_change": {
                        "DIANA": +5,
                        "LUCIEN": +2
                    },
                    "besitos_reward": 10
                }
            )
            session.add(continue_from_partial)
            logger.info("  + Created L2_CONTINUE_B (from L2_PARTIAL_004)")
        else:
            logger.info("  ⊙ L2_CONTINUE_B already exists")

        # L2_TIMEOUT_005 should allow retrying, no choice to Level 3 needed

        await session.commit()

    logger.info("✅ Migration complete!")
    logger.info("   - Level 2 success -> Level 3")
    logger.info("   - Level 2 partial -> Level 3")


async def main():
    """Main entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )

    try:
        await migrate()
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
