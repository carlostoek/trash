#!/usr/bin/env python3
"""
Debug script to investigate empty narrative content issue.

This script diagnoses why /story command shows empty content.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import select
from bot.database import get_session, init_db
from bot.database.models import StoryFragment, StoryChoice, BotConfig


async def debug_narrative_content():
    """Debug narrative content issue."""

    print("=" * 80)
    print("🔍 NARRATIVE CONTENT DEBUG SCRIPT")
    print("=" * 80)
    print()

    # Initialize database
    print("📊 Initializing database connection...")
    await init_db()
    print()

    async with get_session() as session:
        # ========================================
        # 1. QUERY L1_INTRO_001 FRAGMENT
        # ========================================
        print("🔍 STEP 1: Querying L1_INTRO_001 fragment...")
        print("-" * 80)

        result = await session.execute(
            select(StoryFragment).where(
                StoryFragment.fragment_id == "L1_INTRO_001"
            )
        )
        fragment = result.scalar_one_or_none()

        if fragment:
            print(f"✅ Fragment Found!")
            print(f"   fragment_id: {fragment.fragment_id}")
            print(f"   title: {fragment.title}")
            print(f"   content_text: '{fragment.content_text}'")
            print(f"   content_text length: {len(fragment.content_text) if fragment.content_text else 0}")
            print(f"   content_text type: {type(fragment.content_text)}")
            print(f"   speaker: {fragment.speaker}")
            print(f"   speaker_emotion: {fragment.speaker_emotion}")
            print(f"   content_variants: {fragment.content_variants}")
            print(f"   narrative_level: {fragment.narrative_level}")
            print(f"   sort_order: {fragment.sort_order}")
            print(f"   is_starting_fragment: {fragment.is_starting_fragment}")
            print(f"   is_ending_fragment: {fragment.is_ending_fragment}")
            print(f"   active: {fragment.active}")
            print(f"   created_at: {fragment.created_at}")
        else:
            print("❌ Fragment L1_INTRO_001 NOT FOUND!")
        print()

        # ========================================
        # 2. QUERY CHOICES FOR L1_INTRO_001
        # ========================================
        print("🔍 STEP 2: Querying choices for L1_INTRO_001...")
        print("-" * 80)

        if fragment:
            result = await session.execute(
                select(StoryChoice).where(
                    StoryChoice.fragment_id == fragment.id
                )
            )
            choices = result.scalars().all()

            print(f"📊 Found {len(choices)} choices:")
            for choice in choices:
                print(f"   📌 Choice ID: {choice.choice_id}")
                print(f"      Text: {choice.choice_text}")
                print(f"      Emoji: {choice.choice_emoji}")
                print(f"      Target Fragment ID: {choice.target_fragment_id}")
                print(f"      Sort Order: {choice.sort_order}")
                print()
        else:
            print("❌ Cannot query choices - fragment not found")
        print()

        # ========================================
        # 3. CHECK ALL STARTING FRAGMENTS FOR LEVEL 1
        # ========================================
        print("🔍 STEP 3: Checking ALL starting fragments for Level 1...")
        print("-" * 80)

        result = await session.execute(
            select(StoryFragment).where(
                StoryFragment.narrative_level == 1,
                StoryFragment.is_starting_fragment == True
            ).order_by(StoryFragment.sort_order)
        )
        starting_fragments = result.scalars().all()

        print(f"📊 Found {len(starting_fragments)} starting fragments for Level 1:")
        for frag in starting_fragments:
            print(f"   📌 Fragment ID: {frag.fragment_id}")
            print(f"      Title: {frag.title}")
            print(f"      Content: '{frag.content_text[:50] if frag.content_text else 'EMPTY'}...'")
            print(f"      Sort Order: {frag.sort_order}")
            print(f"      Active: {frag.active}")
            print()

        # ========================================
        # 4. CHECK WHAT get_starting_fragment WOULD RETURN
        # ========================================
        print("🔍 STEP 4: Simulating get_starting_fragment() logic...")
        print("-" * 80)

        from bot.services.narrative import NarrativeService

        # Get or create config
        result = await session.execute(select(BotConfig).where(BotConfig.id == 1))
        config = result.scalar_one_or_none()
        if config:
            # BotConfig doesn't have current_narrative_level, it's in UserNarrativeProgress
            print(f"✅ BotConfig found")
            print(f"   current_narrative_level field doesn't exist in BotConfig")
            print(f"   Narrative level is tracked per-user in UserNarrativeProgress")
        else:
            print("⚠️  Config not found - using default level 1")

        result = await session.execute(
            select(StoryFragment)
            .where(
                StoryFragment.narrative_level == 1,  # Always use level 1 for starting fragment
                StoryFragment.is_starting_fragment == True,
                StoryFragment.active == True
            )
            .order_by(StoryFragment.sort_order)
            .limit(1)
        )
        actual_fragment = result.scalar_one_or_none()

        if actual_fragment:
            print(f"✅ get_starting_fragment() would return:")
            print(f"   Fragment ID: {actual_fragment.fragment_id}")
            print(f"   Title: {actual_fragment.title}")
            print(f"   Content: '{actual_fragment.content_text}'")
            print(f"   Content Length: {len(actual_fragment.content_text) if actual_fragment.content_text else 0}")
            print(f"   Content Empty: {actual_fragment.content_text is None or actual_fragment.content_text == ''}")
        else:
            print("❌ get_starting_fragment() would return None!")
        print()

        # ========================================
        # 5. CHECK ALL FRAGMENTS IN LEVEL 1
        # ========================================
        print("🔍 STEP 5: Checking ALL fragments in Level 1...")
        print("-" * 80)

        result = await session.execute(
            select(StoryFragment).where(
                StoryFragment.narrative_level == 1
            ).order_by(StoryFragment.sort_order, StoryFragment.fragment_id)
        )
        all_fragments = result.scalars().all()

        print(f"📊 Found {len(all_fragments)} total fragments in Level 1:")
        for frag in all_fragments:
            content_preview = (frag.content_text[:40] + "...") if frag.content_text and len(frag.content_text) > 40 else (frag.content_text or "EMPTY")
            print(f"   📌 {frag.fragment_id}")
            print(f"      Title: {frag.title}")
            print(f"      Content: '{content_preview}'")
            print(f"      Starting: {frag.is_starting_fragment}")
            print(f"      Active: {frag.active}")
            print(f"      Sort: {frag.sort_order}")
            print()

        # ========================================
        # 6. DIAGNOSIS SUMMARY
        # ========================================
        print("=" * 80)
        print("📋 DIAGNOSIS SUMMARY")
        print("=" * 80)
        print()

        issues = []

        if not fragment:
            issues.append("❌ L1_INTRO_001 fragment does not exist in database")
        elif not fragment.content_text or fragment.content_text.strip() == "":
            issues.append(f"❌ L1_INTRO_001 exists but content_text is EMPTY or None")
            issues.append(f"   Value: '{fragment.content_text}'")

        if fragment and not choices:
            issues.append("❌ L1_INTRO_001 has NO choices defined")

        if len(starting_fragments) > 1:
            issues.append(f"⚠️  Multiple starting fragments found ({len(starting_fragments)})")
            issues.append("   This might cause ambiguity in which fragment is used")

        if actual_fragment and actual_fragment.fragment_id != "L1_INTRO_001":
            issues.append(f"⚠️  get_starting_fragment() returns '{actual_fragment.fragment_id}', NOT 'L1_INTRO_001'")
            issues.append(f"   This might be intentional or a bug")

        if actual_fragment and (not actual_fragment.content_text or actual_fragment.content_text.strip() == ""):
            issues.append(f"❌ THE FRAGMENT BEING RETURNED ('{actual_fragment.fragment_id}') HAS EMPTY CONTENT!")
            issues.append(f"   This is why /story shows empty text")

        if not issues:
            print("✅ No obvious issues detected!")
            print()
            print("Possible causes:")
            print("  - Content might be loaded from a different source")
            print("  - There might be caching issues")
            print("  - The narrative service might have different logic")
        else:
            print("ISSUES FOUND:")
            for issue in issues:
                print(f"  {issue}")

        print()
        print("=" * 80)
        print("🔍 DEBUG COMPLETE")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(debug_narrative_content())
