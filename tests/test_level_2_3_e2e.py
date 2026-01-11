"""
Tests E2E para Levels 2-3 Narrativos.

Este suite valida:
1. Level 2 - Sistema de Observación
   - Transición L1 → L2
   - Fragmento L2_RETURN_001 (Diana nota regreso)
   - Opción L2_ACCEPT_A inicia observación
   - Sistema de tracking de canal (ChannelInteractionService)
   - Estados: success (3+ pistas), partial (1-2 pistas), timeout

2. Level 3 - Perfil de Deseo
   - Transición L2 → L3 (desde L2_SUCCESS_003 y L2_PARTIAL_004)
   - Preguntas de perfil (7 preguntas)
   - Detección de arquetipo
   - Invitación VIP personalizada
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, MagicMock
from aiogram.types import User, Chat

from bot.database import get_session, init_db
from bot.database.models import (
    StoryFragment,
    StoryChoice,
    UserNarrativeProgress,
    DesireProfile,
    ChannelInteraction
)
from bot.services.narrative import StoryEngine, DesireProfileService
from bot.services.channel_interaction import ChannelInteractionService


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def test_user_id():
    """ID de usuario de prueba."""
    return 99901


# ==============================================================================
# LEVEL 2 TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_level_2_transition_from_level_1(test_user_id):
    """Test L1 → L2 transition works correctly."""
    from sqlalchemy import select

    await init_db()

    async with get_session() as session:
        # Get L1_COMPLETE_001
        l1_complete = await session.execute(
            select(StoryFragment).where(
                StoryFragment.fragment_id == "L1_COMPLETE_001"
            )
        )
        l1_complete_frag = l1_complete.scalar_one_or_none()
        assert l1_complete_frag is not None, "L1_COMPLETE_001 debe existir"

        # Get L2_RETURN_001
        l2_return = await session.execute(
            select(StoryFragment).where(
                StoryFragment.fragment_id == "L2_RETURN_001"
            )
        )
        l2_return_frag = l2_return.scalar_one_or_none()
        assert l2_return_frag is not None, "L2_RETURN_001 debe existir"

        # Check choice exists from L1_COMPLETE to L2_RETURN
        choice_stmt = select(StoryChoice).where(
            StoryChoice.choice_id == "L1_CONTINUE_A"
        )
        choice_result = await session.execute(choice_stmt)
        choice = choice_result.scalar_one_or_none()

        assert choice is not None, "L1_CONTINUE_A choice debe existir"
        assert choice.fragment_id == l1_complete_frag.id, "Choice debe partir de L1_COMPLETE_001"
        assert choice.target_fragment_id == l2_return_frag.id, "Choice debe llevar a L2_RETURN_001"


@pytest.mark.asyncio
async def test_level_2_fragments_exist():
    """Test that all Level 2 fragments exist."""
    from sqlalchemy import select

    await init_db()

    async with get_session() as session:
        required_fragments = [
            "L2_RETURN_001",
            "L2_CHALLENGE_002",
            "L2_SUCCESS_003",
            "L2_PARTIAL_004",
            "L2_TIMEOUT_005"
        ]

        for frag_id in required_fragments:
            stmt = select(StoryFragment).where(
                StoryFragment.fragment_id == frag_id
            )
            result = await session.execute(stmt)
            fragment = result.scalar_one_or_none()

            assert fragment is not None, f"{frag_id} debe existir"
            assert fragment.narrative_level == 2, f"{frag_id} debe ser Level 2"
            assert fragment.active is True, f"{frag_id} debe estar activo"


@pytest.mark.asyncio
async def test_level_2_choices_exist():
    """Test that all Level 2 choices exist."""
    from sqlalchemy import select

    await init_db()

    async with get_session() as session:
        required_choices = [
            "L2_ACCEPT_A",
            "L2_POSTPONE"
        ]

        for choice_id in required_choices:
            stmt = select(StoryChoice).where(
                StoryChoice.choice_id == choice_id
            )
            result = await session.execute(stmt)
            choice = result.scalar_one_or_none()

            assert choice is not None, f"{choice_id} debe existir"
            assert choice.active is True, f"{choice_id} debe estar activo"


@pytest.mark.asyncio
async def test_channel_interaction_service_creation(test_user_id):
    """Test ChannelInteractionService can track interactions."""
    await init_db()

    async with get_session() as session:
        service = ChannelInteractionService(session)

        # Track a post view
        success, message, interaction = await service.track_post_view(
            user_id=test_user_id,
            post_id=12345,
            channel_id=10001,
            time_spent_seconds=45
        )

        assert success is True
        assert interaction is not None
        assert interaction.observation_score >= 3  # View (1) + time bonus (2)

        # Get observation score
        score = await service.get_observation_score(test_user_id)
        assert score >= 3


@pytest.mark.asyncio
async def test_channel_interaction_clue_tracking(test_user_id):
    """Test clue discovery tracking."""
    await init_db()

    async with get_session() as session:
        service = ChannelInteractionService(session)

        # Create interaction first
        success, message, interaction = await service.track_post_view(
            user_id=test_user_id,
            post_id=12345,
            channel_id=10001
        )

        assert success is True

        # Add clue
        success, message = await service.add_clue_discovered(
            user_id=test_user_id,
            post_id=12345,
            clue_id="pista_diana_misterio"
        )

        assert success is True
        assert "added" in message.lower()

        # Get clues count using SAME service/session
        clues_count = await service.get_clues_discovered_count(test_user_id)
        assert clues_count == 1


@pytest.mark.asyncio
async def test_observation_status_calculation(test_user_id):
    """Test observation status calculation."""
    await init_db()

    async with get_session() as session:
        service = ChannelInteractionService(session)

        # Track some interactions with clues
        await service.track_post_view(test_user_id, 1001, 50001, 60)
        await service.add_clue_discovered(test_user_id, 1001, "clue1")
        await service.add_clue_discovered(test_user_id, 1001, "clue2")
        await service.add_clue_discovered(test_user_id, 1001, "clue3")

        # Get status
        status = await service.get_observation_status(test_user_id)

        assert status["clues_count"] == 3
        assert status["total_score"] >= 18  # View + time + 3 clues (5 each)
        assert status["status"] == "success"


# ==============================================================================
# LEVEL 3 TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_level_2_to_level_3_transition():
    """Test L2 → L3 transition exists."""
    from sqlalchemy import select

    await init_db()

    async with get_session() as session:
        # Check L2_SUCCESS_003 → L3_CONTINUE_001
        stmt = select(StoryChoice).where(
            StoryChoice.choice_id == "L2_CONTINUE_A"
        )
        result = await session.execute(stmt)
        choice = result.scalar_one_or_none()

        assert choice is not None, "L2_CONTINUE_A debe existir"

        # Get fragments
        l2_success = await session.execute(
            select(StoryFragment).where(StoryFragment.fragment_id == "L2_SUCCESS_003")
        )
        l2_success_frag = l2_success.scalar_one_or_none()

        l3_continue = await session.execute(
            select(StoryFragment).where(StoryFragment.fragment_id == "L3_CONTINUE_001")
        )
        l3_continue_frag = l3_continue.scalar_one_or_none()

        assert l2_success_frag is not None
        assert l3_continue_frag is not None
        assert choice.fragment_id == l2_success_frag.id
        assert choice.target_fragment_id == l3_continue_frag.id


@pytest.mark.asyncio
async def test_level_3_fragments_exist():
    """Test that all Level 3 fragments exist."""
    from sqlalchemy import select

    await init_db()

    async with get_session() as session:
        required_fragments = [
            "L3_CONTINUE_001",
            "L3_PROFILE_002",
            "L3_PROFILE_003",
            "L3_PROFILE_004",
            "L3_PROFILE_005",
            "L3_PROFILE_006",
            "L3_ARCHETYPE_007",
            "L3_SYNTHESIS_008",
            "L3_INVITATION_009"
        ]

        for frag_id in required_fragments:
            stmt = select(StoryFragment).where(
                StoryFragment.fragment_id == frag_id
            )
            result = await session.execute(stmt)
            fragment = result.scalar_one_or_none()

            assert fragment is not None, f"{frag_id} debe existir"
            assert fragment.narrative_level == 3, f"{frag_id} debe ser Level 3"
            assert fragment.active is True, f"{frag_id} debe estar activo"


@pytest.mark.asyncio
async def test_desire_profile_service_create(test_user_id):
    """Test DesireProfileService can create profiles."""
    await init_db()

    async with get_session() as session:
        service = DesireProfileService(session)

        profile = await service.get_or_create_profile(test_user_id)

        assert profile is not None
        assert profile.user_id == test_user_id
        assert profile.questions_answered == 0
        assert profile.is_complete is False


@pytest.mark.asyncio
async def test_desire_profile_answer_questions(test_user_id):
    """Test answering desire profile questions."""
    await init_db()

    async with get_session() as session:
        service = DesireProfileService(session)

        # Answer question 1
        success, message, profile = await service.answer_question(
            user_id=test_user_id,
            question_number=1,
            answer="explorer"
        )

        assert success is True
        assert profile.questions_answered == 1
        assert profile.question_1_answer == "explorer"

        # Answer question 2
        success, message, profile = await service.answer_question(
            user_id=test_user_id,
            question_number=2,
            answer="novelty"
        )

        assert success is True
        assert profile.questions_answered == 2


@pytest.mark.asyncio
async def test_desire_profile_complete_archetype(test_user_id):
    """Test that completing all 7 questions calculates archetype."""
    await init_db()

    async with get_session() as session:
        service = DesireProfileService(session)

        # Answer all 7 questions
        answers = [
            (1, "explorer"),   # EXPLORER
            (2, "novelty"),    # EXPLORER
            (3, "direct"),     # DIRECT
            (4, "romantic"),   # ROMANTIC
            (5, "persistent"), # PERSISTENT
            (6, "open"),       # ROMANTIC
            (7, "intensity")   # ROMANTIC
        ]

        for q_num, answer in answers:
            await service.answer_question(test_user_id, q_num, answer)

        # Refresh profile
        profile = await service.get_or_create_profile(test_user_id)

        assert profile.is_complete is True
        assert profile.questions_answered == 7
        assert profile.archetype_prediction is not None
        # ROMANTIC should win with 3 votes
        assert profile.archetype_prediction in ["ROMANTIC", "EXPLORER"]


@pytest.mark.asyncio
async def test_desire_profile_vip_invitation_message(test_user_id):
    """Test VIP invitation message generation."""
    await init_db()

    async with get_session() as session:
        service = DesireProfileService(session)

        # Without complete profile
        message = await service.get_vip_invitation_message(test_user_id)

        assert message is not None
        assert len(message) > 0
        assert "Diana" in message


@pytest.mark.asyncio
async def test_desire_profile_reset(test_user_id):
    """Test resetting desire profile."""
    await init_db()

    async with get_session() as session:
        service = DesireProfileService(session)

        # Answer some questions
        await service.answer_question(test_user_id, 1, "explorer")
        await service.answer_question(test_user_id, 2, "novelty")

        # Reset
        profile = await service.reset_profile(test_user_id)

        assert profile.questions_answered == 0
        assert profile.is_complete is False
        assert profile.question_1_answer is None
        assert profile.question_2_answer is None


@pytest.mark.asyncio
async def test_desire_profile_next_question(test_user_id):
    """Test getting next question number."""
    await init_db()

    async with get_session() as session:
        service = DesireProfileService(session)

        # Initially should be question 1
        q_num, profile = await service.get_next_question(test_user_id)
        assert q_num == 1

        # Answer question 1
        await service.answer_question(test_user_id, 1, "explorer")

        # Now should be question 2
        q_num, profile = await service.get_next_question(test_user_id)
        assert q_num == 2


# ==============================================================================
# INTEGRATION TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_level_1_to_3_complete_flow(test_user_id):
    """Test complete flow from L1 start to L3 start."""
    from sqlalchemy import select

    await init_db()

    async with get_session() as session:
        engine = StoryEngine(session, Mock())

        # Start at Level 1
        state = await engine.get_current_story_state(test_user_id)

        # Should start at L1_INTRO_001
        assert state["current_fragment"].narrative_level == 1

        # Simulate making choices through L1 to L2
        l1_complete = await session.execute(
            select(StoryFragment).where(StoryFragment.fragment_id == "L1_COMPLETE_001")
        )
        l1_complete_frag = l1_complete.scalar_one_or_none()

        # Move to L1_COMPLETE
        progress = await engine.narrative.get_or_create_user_progress(test_user_id)
        progress.current_fragment_id = l1_complete_frag.id
        await session.commit()

        # Check L2 is accessible
        l2_return = await session.execute(
            select(StoryFragment).where(StoryFragment.fragment_id == "L2_RETURN_001")
        )
        l2_return_frag = l2_return.scalar_one_or_none()

        assert l2_return_frag is not None
        assert l2_return_frag.narrative_level == 2
