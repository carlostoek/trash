"""
Migration to add Level 1 ending fragment and connect to Level 2.

This adds:
1. L1_COMPLETE_001: Ending fragment of Level 1
2. Updates L1_INTRO_002 choices to lead to L1_COMPLETE_001
3. Adds choice from L1_COMPLETE_001 to L2_RETURN_001

Usage:
    python -m migrations.add_level_1_to_2_connection
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


L1_COMPLETE_FRAGMENT = {
    "fragment_id": "L1_COMPLETE_001",
    "narrative_level": 1,
    "title": "Nivel 1 Completado",
    "content_text": (
        "🌸 <i>(sonriente, satisfecha)</i>\n\n"
        "Has completado tu primera interacción con nosotros.\n\n"
        "No es algo que tome a la ligera. Has cruzado el umbral "
        "de Los Kinkys, has escuchado mi bienvenida, has respondido "
        "a Lucien... y estás aquí.\n\n"
        "<i>Su mirada evalúa con interés.</i>\n\n"
        "Esto es solo el comienzo. Hay más profundidades que explorar, "
        "misterios que descubrir, conexiones que fortalecer. "
        "Si deseas continuar, si sientes curiosidad por lo que hay "
        "más allá de esta primera introducción...\n\n"
        "Bienvenido al siguiente nivel.\n\n"
        "✨ Has completado el Nivel 1.\n"
        "🎁 50 besitos ganados.\n\n"
        "📖 El Nivel 2 te espera..."
    ),
    "speaker": "DIANA",
    "speaker_emotion": "satisfied_welcoming",
    "is_starting_fragment": False,
    "is_ending_fragment": True,
    "sort_order": 2,
    "active": True,
    "besitos_reward": 50
}


async def migrate():
    """Add Level 1 ending and connect to Level 2."""
    logger.info("🔧 Starting Level 1 to 2 connection migration...")

    await init_db()

    async with get_session() as session:
        # 1. Create L1_COMPLETE_001 if it doesn't exist
        stmt = select(StoryFragment).where(
            StoryFragment.fragment_id == "L1_COMPLETE_001"
        )
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()

        if not existing:
            complete_fragment = StoryFragment(**L1_COMPLETE_FRAGMENT)
            session.add(complete_fragment)
            await session.flush()  # Get the ID
            logger.info("  + Created L1_COMPLETE_001")
        else:
            logger.info("  ⊙ L1_COMPLETE_001 already exists")

        # 2. Update L1_INTRO_002 choices to point to L1_COMPLETE_001
        l1_complete = await session.execute(
            select(StoryFragment).where(
                StoryFragment.fragment_id == "L1_COMPLETE_001"
            )
        )
        l1_complete_frag = l1_complete.scalar_one_or_none()

        if l1_complete_frag:
            # Update L1_INTRO_A choice
            stmt_a = select(StoryChoice).where(
                StoryChoice.choice_id == "L1_INTRO_A"
            )
            result_a = await session.execute(stmt_a)
            choice_a = result_a.scalar_one_or_none()

            if choice_a:
                choice_a.target_fragment_id = l1_complete_frag.id
                logger.info("  ✓ Updated L1_INTRO_A -> L1_COMPLETE_001")

            # Update L1_INTRO_B choice
            stmt_b = select(StoryChoice).where(
                StoryChoice.choice_id == "L1_INTRO_B"
            )
            result_b = await session.execute(stmt_b)
            choice_b = result_b.scalar_one_or_none()

            if choice_b:
                choice_b.target_fragment_id = l1_complete_frag.id
                logger.info("  ✓ Updated L1_INTRO_B -> L1_COMPLETE_001")

        # 3. Add choice from L1_COMPLETE_001 to L2_RETURN_001
        l2_return = await session.execute(
            select(StoryFragment).where(
                StoryFragment.fragment_id == "L2_RETURN_001"
            )
        )
        l2_return_frag = l2_return.scalar_one_or_none()

        if l1_complete_frag and l2_return_frag:
            # Check if choice already exists
            stmt_cont = select(StoryChoice).where(
                StoryChoice.choice_id == "L1_CONTINUE_A"
            )
            result_cont = await session.execute(stmt_cont)
            existing_cont = result_cont.scalar_one_or_none()

            if not existing_cont:
                continue_choice = StoryChoice(
                    choice_id="L1_CONTINUE_A",
                    fragment_id=l1_complete_frag.id,
                    target_fragment_id=l2_return_frag.id,
                    choice_text="📖 Continuar al Nivel 2",
                    choice_description="Explora el siguiente nivel de la historia",
                    sort_order=1,
                    active=True,
                    consequences={
                        "flags_set": ["level_1_complete"],
                        "relationship_change": {
                            "DIANA": +5,
                            "LUCIEN": +3
                        }
                    }
                )
                session.add(continue_choice)
                logger.info("  + Created L1_CONTINUE_A -> L2_RETURN_001")
            else:
                logger.info("  ⊙ L1_CONTINUE_A already exists")

        await session.commit()

    logger.info("✅ Migration complete!")
    logger.info("   - Level 1 now has ending fragment")
    logger.info("   - Level 1 connects to Level 2")


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
