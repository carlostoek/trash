#!/usr/bin/env python3
"""
Clean up test fragments from the database.

This script removes test fragments that are interfering with the narrative.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import select, delete
from bot.database import get_session, init_db
from bot.database.models import StoryFragment, StoryChoice


async def cleanup_test_fragments():
    """Remove test fragments and ensure L1_INTRO_001 is the starting fragment."""

    print("=" * 80)
    print("🧹 CLEANUP TEST FRAGMENTS")
    print("=" * 80)
    print()

    # Initialize database
    print("📊 Initializing database connection...")
    await init_db()
    print()

    async with get_session() as session:
        # ========================================
        # 1. IDENTIFY TEST FRAGMENTS
        # ========================================
        print("🔍 STEP 1: Identifying test fragments...")
        print("-" * 80)

        # Find all test fragments
        result = await session.execute(
            select(StoryFragment).where(
                StoryFragment.fragment_id.like("TEST_%")
            )
        )
        test_fragments = result.scalars().all()

        print(f"📊 Found {len(test_fragments)} test fragments:")
        for frag in test_fragments:
            print(f"   🗑️  {frag.fragment_id} (Level {frag.narrative_level}, Sort {frag.sort_order})")
        print()

        # ========================================
        # 2. IDENTIFY PROBLEMATIC FRAGMENTS
        # ========================================
        print("🔍 STEP 2: Identifying problematic fragments...")
        print("-" * 80)

        # Find L1_START and other empty starting fragments
        result = await session.execute(
            select(StoryFragment).where(
                StoryFragment.narrative_level == 1,
                StoryFragment.is_starting_fragment == True,
                StoryFragment.fragment_id != "L1_INTRO_001"
            ).order_by(StoryFragment.sort_order)
        )
        problematic_fragments = result.scalars().all()

        print(f"📊 Found {len(problematic_fragments)} problematic starting fragments:")
        for frag in problematic_fragments:
            content_status = "EMPTY" if not frag.content_text else f"has content ({len(frag.content_text)} chars)"
            print(f"   ⚠️  {frag.fragment_id} (Sort {frag.sort_order}, {content_status})")
        print()

        # ========================================
        # 3. DELETE TEST FRAGMENTS
        # ========================================
        print("🔍 STEP 3: Deleting test fragments...")
        print("-" * 80)

        # Delete test choices first (foreign key constraint)
        test_fragment_ids = [f.id for f in test_fragments]
        if test_fragment_ids:
            await session.execute(
                delete(StoryChoice).where(
                    StoryChoice.fragment_id.in_(test_fragment_ids)
                )
            )
            print(f"✅ Deleted choices for test fragments")

        # Delete test fragments
        if test_fragments:
            await session.execute(
                delete(StoryFragment).where(
                    StoryFragment.fragment_id.like("TEST_%")
                )
            )
            print(f"✅ Deleted {len(test_fragments)} test fragments")
        print()

        # ========================================
        # 4. DELETE L1_START AND OTHER EMPTY STARTING FRAGMENTS
        # ========================================
        print("🔍 STEP 4: Deleting L1_START and other empty starting fragments...")
        print("-" * 80)

        if problematic_fragments:
            problematic_ids = [f.id for f in problematic_fragments]

            # Delete choices first
            await session.execute(
                delete(StoryChoice).where(
                    StoryChoice.fragment_id.in_(problematic_ids)
                )
            )
            print(f"✅ Deleted choices for problematic fragments")

            # Delete fragments
            await session.execute(
                delete(StoryFragment).where(
                    StoryFragment.id.in_(problematic_ids)
                )
            )
            print(f"✅ Deleted {len(problematic_fragments)} problematic fragments")
        print()

        # ========================================
        # 5. ENSURE L1_INTRO_001 IS THE ONLY STARTING FRAGMENT
        # ========================================
        print("🔍 STEP 5: Ensuring L1_INTRO_001 is the only starting fragment...")
        print("-" * 80)

        # Get L1_INTRO_001
        result = await session.execute(
            select(StoryFragment).where(
                StoryFragment.fragment_id == "L1_INTRO_001"
            )
        )
        l1_intro = result.scalar_one_or_none()

        if l1_intro:
            # Ensure it has sort_order=0 and is_starting_fragment=True
            l1_intro.sort_order = 0
            l1_intro.is_starting_fragment = True
            l1_intro.active = True
            print(f"✅ Updated L1_INTRO_001:")
            print(f"   - sort_order: {l1_intro.sort_order}")
            print(f"   - is_starting_fragment: {l1_intro.is_starting_fragment}")
            print(f"   - active: {l1_intro.active}")
            print(f"   - content_text length: {len(l1_intro.content_text) if l1_intro.content_text else 0}")
        else:
            print("❌ L1_INTRO_001 not found!")
        print()

        # ========================================
        # 6. VERIFY CLEANUP
        # ========================================
        print("🔍 STEP 6: Verifying cleanup...")
        print("-" * 80)

        # Check remaining starting fragments
        result = await session.execute(
            select(StoryFragment).where(
                StoryFragment.narrative_level == 1,
                StoryFragment.is_starting_fragment == True
            ).order_by(StoryFragment.sort_order)
        )
        remaining_starting = result.scalars().all()

        print(f"📊 Remaining starting fragments for Level 1: {len(remaining_starting)}")
        for frag in remaining_starting:
            content_preview = (frag.content_text[:50] + "...") if frag.content_text and len(frag.content_text) > 50 else (frag.content_text or "EMPTY")
            print(f"   📌 {frag.fragment_id}")
            print(f"      Sort: {frag.sort_order}, Active: {frag.active}")
            print(f"      Content: '{content_preview}'")
        print()

        # Commit all changes
        print("💾 Committing changes...")
        await session.commit()
        print("✅ Changes committed!")
        print()

        print("=" * 80)
        print("🧹 CLEANUP COMPLETE")
        print("=" * 80)
        print()
        print("✅ Test fragments deleted")
        print("✅ L1_INTRO_001 is now the only starting fragment")
        print("✅ /story command should now work correctly")


if __name__ == "__main__":
    asyncio.run(cleanup_test_fragments())
