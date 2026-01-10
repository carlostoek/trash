"""
Comprehensive test suite for narrative models and services.

Tests cover:
- Model creation and properties
- Service layer functionality
- Integration between services
- Edge cases and error handling

Total: 18+ tests
"""
import pytest
import time
import random
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

from sqlalchemy import select

from bot.database.models import (
    StoryFragment,
    StoryChoice,
    UserNarrativeProgress,
    UserChoice,
    NarrativeUnlock,
    NarrativeFlag,
    ArchetypeProfile,
    CharacterRelationship,
    User
)
from bot.services.narrative import (
    FlagService,
    ArchetypeService,
    CharacterRelationshipService,
    NarrativeService,
    StoryEngine
)
from bot.database import get_session


# Helper to generate unique user IDs per test
_counter = 0
def get_unique_user_id():
    global _counter
    _counter += 1
    return int(time.time() * 1000) + _counter


# ==============================================================================
# MODEL TESTS (Unit)
# ==============================================================================

class TestStoryFragmentModel:
    """Test StoryFragment model creation and properties."""

    @pytest.mark.asyncio
    async def test_story_fragment_creation(self):
        """Test creating a story fragment with all fields."""
        async with get_session() as session:
            # Use unique fragment_id with timestamp and random to avoid collisions
            fragment_id = f"TEST_FRAG_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
            fragment = StoryFragment(
                fragment_id=fragment_id,
                narrative_level=1,
                title="Bienvenida a Los Kinkys",
                content_text="Bienvenido al mundo de Diana y Lucien...",
                speaker="NARRATOR",
                speaker_emotion="mysterious",
                is_starting_fragment=True,
                is_ending_fragment=False,
                besitos_reward=10,
                experience_reward=50,
                active=True,
                sort_order=1
            )

            session.add(fragment)
            await session.commit()

            # Retrieve and verify
            stmt = select(StoryFragment).where(StoryFragment.fragment_id == fragment_id)
            result = await session.execute(stmt)
            retrieved = result.scalar_one()

            assert retrieved.fragment_id == fragment_id
            assert retrieved.narrative_level == 1
            assert retrieved.title == "Bienvenida a Los Kinkys"
            assert retrieved.speaker == "NARRATOR"
            assert retrieved.is_starting_fragment is True
            assert retrieved.besitos_reward == 10
            assert retrieved.active is True

    @pytest.mark.asyncio
    async def test_story_fragment_json_fields(self):
        """Test JSON fields in story fragment."""
        async with get_session() as session:
            # Use unique fragment_id with timestamp and random to avoid collisions
            fragment_id = f"TEST_FRAG_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
            unlock_conditions = {
                "required_choices": ["L1_INTRO_A"],
                "required_flags": ["met_diana"],
                "besitos_cost": 100
            }

            content_variants = {
                "EXPLORER": "Texto para exploradores...",
                "ROMANTIC": "Texto para románticos..."
            }

            fragment = StoryFragment(
                fragment_id=fragment_id,
                narrative_level=2,
                title="Branching Path",
                unlock_conditions=unlock_conditions,
                content_variants=content_variants,
                active=True
            )

            session.add(fragment)
            await session.commit()

            stmt = select(StoryFragment).where(StoryFragment.fragment_id == fragment_id)
            result = await session.execute(stmt)
            retrieved = result.scalar_one()

            assert retrieved.unlock_conditions == unlock_conditions
            assert retrieved.content_variants == content_variants
            assert retrieved.unlock_conditions["besitos_cost"] == 100


class TestUserNarrativeProgressModel:
    """Test UserNarrativeProgress model and properties."""

    @pytest.mark.asyncio
    async def test_completion_percentage_property(self):
        """Test completion_percentage property calculation."""
        async with get_session() as session:
            user_id = get_unique_user_id()
            user = User(user_id=user_id, first_name="Test", role="FREE")
            session.add(user)
            await session.flush()

            progress = UserNarrativeProgress(
                user_id=user_id,
                levels_completed=[1, 2, 3]  # 3 out of 6 levels
            )

            session.add(progress)
            await session.commit()

            assert progress.completion_percentage == 50.0  # 3/6 * 100

    @pytest.mark.asyncio
    async def test_is_vip_content_unlocked_property(self):
        """Test is_vip_content_unlocked property."""
        async with get_session() as session:
            # Test with level 3 (should be False)
            user1_id = get_unique_user_id()
            user1 = User(user_id=user1_id, first_name="Test1", role="FREE")
            session.add(user1)
            await session.flush()

            progress1 = UserNarrativeProgress(
                user_id=user1_id,
                max_narrative_level_reached=3
            )
            session.add(progress1)
            await session.commit()
            assert progress1.is_vip_content_unlocked is False

            # Test with level 4 (should be True)
            user2_id = get_unique_user_id()
            user2 = User(user_id=user2_id, first_name="Test2", role="FREE")
            session.add(user2)
            await session.flush()

            progress2 = UserNarrativeProgress(
                user_id=user2_id,
                max_narrative_level_reached=4
            )
            session.add(progress2)
            await session.commit()
            assert progress2.is_vip_content_unlocked is True


class TestNarrativeFlagModel:
    """Test NarrativeFlag model and is_active property."""

    @pytest.mark.asyncio
    async def test_flag_is_active_permanent(self):
        """Test is_active property for permanent flag (no expiration)."""
        async with get_session() as session:
            user_id = get_unique_user_id()
            user = User(user_id=user_id, first_name="Test", role="FREE")
            session.add(user)
            await session.flush()

            flag = NarrativeFlag(
                user_id=user_id,
                flag_key="met_diana",
                flag_value="true",
                expires_at=None  # Permanent flag
            )

            session.add(flag)
            await session.commit()

            assert flag.is_active is True

    @pytest.mark.asyncio
    async def test_flag_is_active_with_expiration(self):
        """Test is_active property for temporary flag."""
        async with get_session() as session:
            # Expired flag
            user1_id = get_unique_user_id()
            user1 = User(user_id=user1_id, first_name="Test1", role="FREE")
            session.add(user1)
            await session.flush()

            expired_flag = NarrativeFlag(
                user_id=user1_id,
                flag_key="temporary_buff",
                flag_value="active",
                expires_at=datetime.utcnow() - timedelta(hours=1)  # Use naive datetime (model uses utcnow())
            )

            session.add(expired_flag)
            await session.commit()
            assert expired_flag.is_active is False

            # Active flag
            user2_id = get_unique_user_id()
            user2 = User(user_id=user2_id, first_name="Test2", role="FREE")
            session.add(user2)
            await session.flush()

            active_flag = NarrativeFlag(
                user_id=user2_id,
                flag_key="active_buff",
                flag_value="active",
                expires_at=datetime.utcnow() + timedelta(hours=1)  # Use naive datetime
            )

            session.add(active_flag)
            await session.commit()
            assert active_flag.is_active is True


class TestArchetypeProfileModel:
    """Test ArchetypeProfile model and archetype_points."""

    @pytest.mark.asyncio
    async def test_archetype_points_json_field(self):
        """Test that archetype_points JSON field serializes correctly."""
        async with get_session() as session:
            user_id = get_unique_user_id()
            user = User(user_id=user_id, first_name="Test", role="FREE")
            session.add(user)
            await session.flush()

            points = {
                "explorer": 10,
                "romantic": 15,
                "direct": 5
            }

            profile = ArchetypeProfile(
                user_id=user_id,
                archetype_points=points
            )

            session.add(profile)
            await session.commit()

            # Retrieve and verify JSON persists
            stmt = select(ArchetypeProfile).where(ArchetypeProfile.user_id == user_id)
            result = await session.execute(stmt)
            retrieved = result.scalar_one()

            assert retrieved.archetype_points == points
            assert isinstance(retrieved.archetype_points, dict)


class TestCharacterRelationshipModel:
    """Test CharacterRelationship model and relationship_status property."""

    @pytest.mark.asyncio
    async def test_relationship_status_property(self):
        """Test relationship_status property for different score ranges."""
        async with get_session() as session:
            user = User(user_id=get_unique_user_id(), first_name="Test", role="FREE")
            session.add(user)
            await session.flush()

            # Test different score ranges
            test_cases = [
                (90, "Deep Intimacy"),
                (65, "Romantic Interest"),
                (45, "Close Friend"),
                (25, "Friendly"),
                (0, "Neutral"),
                (-30, "Distant"),
                (-75, "Hostile")
            ]

            for score, expected_status in test_cases:
                relationship = CharacterRelationship(
                    user_id=get_unique_user_id(),
                    character_name=f"TEST_{score}",
                    relationship_score=score
                )

                session.add(relationship)
                await session.commit()

                assert relationship.relationship_status == expected_status

                # Clean up for next test
                await session.delete(relationship)
                await session.commit()


class TestNarrativeUnlockModel:
    """Test NarrativeUnlock model and unique constraint."""

    @pytest.mark.asyncio
    async def test_narrative_unlock_creation(self):
        """Test creating a narrative unlock."""
        async with get_session() as session:
            user_id = get_unique_user_id()
            user = User(user_id=user_id, first_name="Test", role="FREE")
            session.add(user)
            await session.flush()

            unlock = NarrativeUnlock(
                user_id=user_id,
                unlock_type="fragment",
                unlock_id="L1_SECRET_001",
                unlock_method="choice",
                unlock_source="chose_romantic_path"
            )

            session.add(unlock)
            await session.commit()

            stmt = select(NarrativeUnlock).where(
                (NarrativeUnlock.user_id == user_id) &
                (NarrativeUnlock.unlock_type == "fragment") &
                (NarrativeUnlock.unlock_id == "L1_SECRET_001")
            )
            result = await session.execute(stmt)
            retrieved = result.scalar_one()

            assert retrieved.unlock_type == "fragment"
            assert retrieved.unlock_id == "L1_SECRET_001"
            assert retrieved.unlock_method == "choice"


# ==============================================================================
# SERVICE TESTS (Integration)
# ==============================================================================

class TestFlagService:
    """Test FlagService functionality."""

    @pytest.mark.asyncio
    async def test_set_flag(self):
        """Test setting a narrative flag."""
        async with get_session() as session:
            service = FlagService(session)

            user_id = get_unique_user_id()
            flag = await service.set_flag(
                user_id=user_id,
                flag_key="met_diana",
                flag_value="true"
            )

            assert flag.user_id == user_id
            assert flag.flag_key == "met_diana"
            assert flag.flag_value == "true"
            assert flag.expires_at is None

    @pytest.mark.asyncio
    async def test_get_flag(self):
        """Test retrieving a narrative flag."""
        async with get_session() as session:
            service = FlagService(session)

            # Set a flag first
            user_id = get_unique_user_id()
            await service.set_flag(user_id=user_id, flag_key="test_flag")

            # Retrieve it
            flag = await service.get_flag(user_id=user_id, flag_key="test_flag")

            assert flag is not None
            assert flag.flag_key == "test_flag"

    @pytest.mark.asyncio
    async def test_has_flag(self):
        """Test checking if user has a flag."""
        async with get_session() as session:
            service = FlagService(session)

            user_id = get_unique_user_id()

            # Before setting
            has_before = await service.has_flag(user_id=user_id, flag_key="test_flag")
            assert has_before is False

            # After setting
            await service.set_flag(user_id=user_id, flag_key="test_flag")
            has_after = await service.has_flag(user_id=user_id, flag_key="test_flag")
            assert has_after is True

    @pytest.mark.asyncio
    async def test_clear_flag(self):
        """Test clearing a narrative flag."""
        async with get_session() as session:
            service = FlagService(session)

            # Set a flag
            user_id = get_unique_user_id()
            await service.set_flag(user_id=user_id, flag_key="test_flag")

            # Clear it
            cleared = await service.clear_flag(user_id=user_id, flag_key="test_flag")
            assert cleared is True

            # Verify it's gone
            flag = await service.get_flag(user_id=user_id, flag_key="test_flag")
            assert flag is None


class TestArchetypeService:
    """Test ArchetypeService functionality."""

    @pytest.mark.asyncio
    async def test_get_or_create_archetype_profile(self):
        """Test getting or creating archetype profile."""
        async with get_session() as session:
            service = ArchetypeService(session)

            user_id = get_unique_user_id()

            # First call creates profile
            profile1 = await service.get_or_create_archetype_profile(user_id=user_id)
            assert profile1.primary_archetype == "EXPLORER"
            assert profile1.archetype_confidence == 30

            # Second call returns existing profile
            profile2 = await service.get_or_create_archetype_profile(user_id=user_id)
            assert profile1.id == profile2.id

    @pytest.mark.asyncio
    async def test_add_archetype_points(self):
        """Test adding archetype points."""
        async with get_session() as session:
            service = ArchetypeService(session)

            user_id = get_unique_user_id()

            # Create profile
            profile = await service.get_or_create_archetype_profile(user_id=user_id)

            # Add points
            await service.add_archetype_points(
                user_id=user_id,
                points_dict={"romantic": +5, "direct": -2}
            )

            # Verify points updated - need to reload from DB
            updated_profile = await service.get_or_create_archetype_profile(user_id=user_id)
            assert updated_profile.archetype_points["romantic"] == 5
            assert updated_profile.archetype_points["direct"] == -2


class TestCharacterRelationshipService:
    """Test CharacterRelationshipService functionality."""

    @pytest.mark.asyncio
    async def test_get_or_create_relationship(self):
        """Test getting or creating a relationship."""
        async with get_session() as session:
            service = CharacterRelationshipService(session)

            user_id = get_unique_user_id()

            # First call creates
            rel1 = await service.get_or_create_relationship(user_id=user_id, character_name="LUCIEN")
            assert rel1.relationship_score == 0

            # Second call returns existing
            rel2 = await service.get_or_create_relationship(user_id=user_id, character_name="LUCIEN")
            assert rel1.id == rel2.id

    @pytest.mark.asyncio
    async def test_update_relationship_score(self):
        """Test updating relationship score."""
        async with get_session() as session:
            service = CharacterRelationshipService(session)

            user_id = get_unique_user_id()

            # Create relationship
            rel = await service.get_or_create_relationship(user_id=user_id, character_name="DIANA")

            # Update score
            updated = await service.update_relationship_score(
                user_id=user_id,
                character_name="DIANA",
                score_change=+50
            )

            assert updated.relationship_score == 50
            assert updated.interaction_count == 2

    @pytest.mark.asyncio
    async def test_relationship_score_bounds(self):
        """Test that relationship score is bounded between -100 and +100."""
        async with get_session() as session:
            service = CharacterRelationshipService(session)

            user_id = get_unique_user_id()

            # Create relationship
            rel = await service.get_or_create_relationship(user_id=user_id, character_name="LUCIEN")

            # Try to exceed upper bound
            updated1 = await service.update_relationship_score(user_id=user_id, character_name="LUCIEN", score_change=+200)
            assert updated1.relationship_score == 100  # Capped at 100

            # Try to exceed lower bound
            updated2 = await service.update_relationship_score(user_id=user_id, character_name="LUCIEN", score_change=-250)
            assert updated2.relationship_score == -100  # Capped at -100


class TestNarrativeService:
    """Test NarrativeService functionality."""

    @pytest.mark.asyncio
    async def test_get_starting_fragment(self, mock_bot):
        """Test getting starting fragment for a level."""
        async with get_session() as session:
            service = NarrativeService(session, mock_bot)

            # Use unique narrative_level to avoid conflicts with existing fragments
            # We use a high random number (90-999) that won't conflict with normal game levels (1-6)
            unique_level = random.randint(90, 999)

            # Create starting fragment with unique ID and level
            fragment_id = f"TEST_START_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
            fragment = StoryFragment(
                fragment_id=fragment_id,
                narrative_level=unique_level,
                title="Test Level Start",
                is_starting_fragment=True,
                active=True
            )
            session.add(fragment)
            await session.commit()

            # Get it
            retrieved = await service.get_starting_fragment(narrative_level=unique_level)
            assert retrieved is not None
            assert retrieved.fragment_id == fragment_id

    @pytest.mark.asyncio
    async def test_get_fragment(self, mock_bot):
        """Test getting fragment by ID."""
        async with get_session() as session:
            service = NarrativeService(session, mock_bot)

            # Create fragment with unique ID
            fragment_id = f"TEST_GET_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
            fragment = StoryFragment(
                fragment_id=fragment_id,
                narrative_level=1,
                title="Test Fragment",
                active=True
            )
            session.add(fragment)
            await session.commit()

            # Get it
            retrieved = await service.get_fragment(fragment_id=fragment_id)
            assert retrieved is not None
            assert retrieved.title == "Test Fragment"


# ==============================================================================
# RUN TESTS
# ==============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
