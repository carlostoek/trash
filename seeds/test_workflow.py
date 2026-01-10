#!/usr/bin/env python3
"""
Complete workflow test for Level 1 narrative content seeding.

This script demonstrates the complete workflow:
1. Seed Level 1 content
2. Validate seeded content
3. Display narrative flow

Usage:
    python -m seeds.test_workflow
"""
import asyncio
import logging
from sqlalchemy import select

from bot.database.engine import init_db, get_session
from bot.database.models import StoryFragment, StoryChoice

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def print_header(title: str) -> None:
    """Print a formatted header."""
    logger.info("\n" + "="*70)
    logger.info(f"  {title}")
    logger.info("="*70 + "\n")


def print_fragment_details(fragment: StoryFragment) -> None:
    """Print detailed fragment information."""
    start_marker = " 🚀 START" if fragment.is_starting_fragment else ""
    end_marker = " 🏁 END" if fragment.is_ending_fragment else ""

    logger.info(f"📜 {fragment.fragment_id}: {fragment.title}{start_marker}{end_marker}")
    logger.info(f"   Speaker: {fragment.speaker or 'Narrator'}")
    logger.info(f"   Emotion: {fragment.speaker_emotion or 'neutral'}")
    logger.info(f"   Level: {fragment.narrative_level}")
    logger.info(f"   Rewards: {fragment.besitos_reward} besitos, {fragment.experience_reward} XP")
    logger.info(f"   Active: {'✅' if fragment.active else '❌'}")


def print_choice_details(choice: StoryChoice, from_frag: StoryFragment, to_frag: StoryFragment) -> None:
    """Print detailed choice information."""
    logger.info(f"\n🔗 {choice.choice_id}: {choice.choice_text} {choice.choice_emoji or ''}")
    logger.info(f"   From: {from_frag.fragment_id} ({from_frag.title})")
    logger.info(f"   To: {to_frag.fragment_id} ({to_frag.title})")

    if choice.consequences:
        logger.info(f"   Consequences:")
        if "flags_set" in choice.consequences:
            logger.info(f"      • Flags: {', '.join(choice.consequences['flags_set'])}")
        if "archetype_points" in choice.consequences:
            points = choice.consequences["archetype_points"]
            logger.info(f"      • Archetype: {points}")
        if "relationship_change" in choice.consequences:
            rel = choice.consequences["relationship_change"]
            logger.info(f"      • Relationships: {rel}")
        if "besitos_reward" in choice.consequences:
            logger.info(f"      • Reward: {choice.consequences['besitos_reward']} besitos")


async def display_narrative_flow() -> None:
    """Display the complete narrative flow for Level 1."""
    print_header("LEVEL 1 NARRATIVE FLOW")

    async with get_session() as session:
        # Get all Level 1 fragments in order
        stmt = select(StoryFragment).where(
            StoryFragment.narrative_level == 1,
            StoryFragment.fragment_id.like("L1_%")
        ).order_by(StoryFragment.sort_order)

        result = await session.execute(stmt)
        fragments = result.scalars().all()

        # Get all choices
        stmt_choices = select(StoryChoice)
        result = await session.execute(stmt_choices)
        choices = result.scalars().all()

        # Create a mapping of fragment IDs to choices
        choices_by_fragment = {}
        for choice in choices:
            if choice.fragment_id not in choices_by_fragment:
                choices_by_fragment[choice.fragment_id] = []
            choices_by_fragment[choice.fragment_id].append(choice)

        # Display narrative flow
        for i, fragment in enumerate(fragments, 1):
            print(f"\n{'─'*70}")
            logger.info(f"SCENE {i}: {fragment.title}")
            print(f"{'─'*70}")
            print_fragment_details(fragment)

            # Display content preview
            if fragment.content_text:
                lines = fragment.content_text.split('\n')
                preview = '\n   '.join(lines[:3])
                logger.info(f"\n   Preview:")
                logger.info(f"   {preview}...")

            # Display choices from this fragment
            if fragment.id in choices_by_fragment:
                logger.info(f"\n   📝 Choices:")
                for choice in choices_by_fragment[fragment.id]:
                    # Get target fragment
                    stmt_target = select(StoryFragment).where(
                        StoryFragment.id == choice.target_fragment_id
                    )
                    result_target = await session.execute(stmt_target)
                    target = result_target.scalar_one_or_none()

                    if target:
                        logger.info(f"      • {choice.choice_text} → {target.fragment_id}")


async def show_statistics() -> None:
    """Display statistics about seeded content."""
    print_header("CONTENT STATISTICS")

    async with get_session() as session:
        # Count fragments
        stmt_frags = select(StoryFragment).where(
            StoryFragment.narrative_level == 1,
            StoryFragment.fragment_id.like("L1_%")
        )
        result = await session.execute(stmt_frags)
        fragments = result.scalars().all()

        # Count choices
        stmt_choices = select(StoryChoice)
        result = await session.execute(stmt_choices)
        choices = result.scalars().all()

        # Calculate totals
        total_besitos = sum(f.besitos_reward for f in fragments)
        total_xp = sum(f.experience_reward for f in fragments)
        total_words = sum(len(f.content_text.split()) if f.content_text else 0 for f in fragments)

        # Speaker breakdown
        speakers = {}
        for frag in fragments:
            speaker = frag.speaker or "NARRATOR"
            speakers[speaker] = speakers.get(speaker, 0) + 1

        logger.info(f"📊 Fragments: {len(fragments)}")
        logger.info(f"🔗 Choices: {len(choices)}")
        logger.info(f"💰 Total Besitos: {total_besitos}")
        logger.info(f"⭐ Total XP: {total_xp}")
        logger.info(f"📝 Total Words: {total_words}")

        logger.info(f"\n👥 Speakers:")
        for speaker, count in sorted(speakers.items()):
            logger.info(f"   • {speaker}: {count} fragment(s)")

        # Starting/Ending fragments
        starting = [f for f in fragments if f.is_starting_fragment]
        ending = [f for f in fragments if f.is_ending_fragment]

        logger.info(f"\n🚀 Starting Fragments: {len(starting)}")
        for frag in starting:
            logger.info(f"   • {frag.fragment_id}")

        logger.info(f"\n🏁 Ending Fragments: {len(ending)}")
        for frag in ending:
            logger.info(f"   • {frag.fragment_id}")


async def show_content_preview() -> None:
    """Show preview of actual content."""
    print_header("CONTENT PREVIEW")

    async with get_session() as session:
        # Get Diana's welcome message
        stmt = select(StoryFragment).where(
            StoryFragment.fragment_id == "L1_INTRO_001"
        )
        result = await session.execute(stmt)
        fragment = result.scalar_one_or_none()

        if fragment and fragment.content_text:
            logger.info("🌸 Diana's Welcome Message:")
            logger.info("─"*70)
            logger.info(fragment.content_text[:500] + "...")
            logger.info("─"*70)


async def main():
    """Run complete workflow test."""
    logger.info("\n" + "="*70)
    logger.info("  LEVEL 1 NARRATIVE CONTENT - COMPLETE WORKFLOW TEST")
    logger.info("="*70)

    # Initialize database
    logger.info("\n🔧 Initializing database...")
    await init_db()
    logger.info("✅ Database initialized")

    # Show statistics
    await show_statistics()

    # Show content preview
    await show_content_preview()

    # Display narrative flow
    await display_narrative_flow()

    # Final summary
    print_header("WORKFLOW COMPLETE")
    logger.info("✅ Level 1 narrative content is ready!")
    logger.info("\nNext steps:")
    logger.info("   1. Implement narrative handlers in bot/handlers/narrative/")
    logger.info("   2. Integrate with gamification system")
    logger.info("   3. Test end-to-end user flow")
    logger.info("   4. Deploy to production")
    logger.info("\n" + "="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
