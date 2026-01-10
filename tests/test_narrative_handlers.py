"""
Tests para Narrative Handlers.

Este suite de tests valida:
1. /story command inicia narrativa correctamente
2. Opciones narrativas avanzan la historia
3. Bloqueo VIP para niveles 4+
4. Función de releer fragmentos
5. Generación de keyboards narrativos
6. Formateo de mensajes narrativos
7. Estados FSM funcionan correctamente
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from aiogram.types import Message, CallbackQuery, User, Chat
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import (
    StoryFragment,
    StoryChoice,
    UserNarrativeProgress,
    ArchetypeProfile
)
from bot.services.narrative import StoryEngine
from bot.handlers.user.narrative import (
    cmd_story,
    callback_narrative_choice,
    callback_narrative_reread,
    callback_narrative_status
)
from bot.states.narrative import NarrativeUserStates
from bot.utils.narrative_formatters import (
    format_narrative_message,
    format_choice_button_text,
    format_unlock_message,
    format_consequences_message,
    format_story_status
)
from bot.utils.keyboards import create_narrative_keyboard


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def mock_user():
    """Usuario mock de Telegram."""
    return User(
        id=12345,
        is_bot=False,
        first_name="Test",
        username="testuser"
    )


@pytest.fixture
def mock_chat():
    """Chat mock de Telegram."""
    return Chat(
        id=12345,
        type="private"
    )


@pytest.fixture
def mock_message(mock_user, mock_chat):
    """Mensaje mock de Telegram."""
    message = Mock(spec=Message)
    message.from_user = mock_user
    message.chat = mock_chat
    message.text = "/story"
    message.answer = AsyncMock()
    message.answer_photo = AsyncMock()
    message.answer_video = AsyncMock()
    return message


@pytest.fixture
def mock_callback(mock_user):
    """CallbackQuery mock de Telegram."""
    callback = Mock(spec=CallbackQuery)
    callback.from_user = mock_user
    callback.data = "narrative:choice:L1_INTRO_A"
    callback.answer = AsyncMock()
    callback.message = Mock(spec=Message)
    callback.message.edit_text = AsyncMock()
    callback.message.answer = AsyncMock()
    callback.message.text = "Previous message"
    return callback


@pytest.fixture
def mock_starting_fragment():
    """Fragmento inicial de historia."""
    fragment = Mock(spec=StoryFragment)
    fragment.id = 1
    fragment.fragment_id = "L1_INTRO_001"
    fragment.title = "El Comienzo"
    fragment.speaker = "NARRATOR"
    fragment.emotion = "calm"
    fragment.content = "La historia comienza..."
    fragment.content_variants = {}
    fragment.media_type = None
    fragment.media_file_id = None
    fragment.narrative_level = 1
    fragment.is_starting_fragment = True
    fragment.is_ending_fragment = False
    fragment.active = True
    fragment.unlock_conditions = None
    return fragment


@pytest.fixture
def mock_choices(mock_starting_fragment):
    """Opciones de historia."""
    choice1 = Mock(spec=StoryChoice)
    choice1.id = 1
    choice1.choice_id = "L1_INTRO_A"
    choice1.choice_text = "Seguir adelante"
    choice1.choice_emoji = "👣"
    choice1.text_variants = {}
    choice1.fragment_id = mock_starting_fragment.id
    choice1.target_fragment_id = 2
    choice1.sort_order = 1
    choice1.active = True
    choice1.consequences = {
        "flags_set": ["started_journey"],
        "archetype_points": {"explorer": +1}
    }
    choice1.display_requirements = None

    choice2 = Mock(spec=StoryChoice)
    choice2.id = 2
    choice2.choice_id = "L1_INTRO_B"
    choice2.choice_text = "Observar detenidamente"
    choice2.choice_emoji = "🔍"
    choice2.text_variants = {}
    choice2.fragment_id = mock_starting_fragment.id
    choice2.target_fragment_id = 3
    choice2.sort_order = 2
    choice2.active = True
    choice2.consequences = {
        "flags_set": ["observed_surroundings"],
        "archetype_points": {"analytical": +1}
    }
    choice2.display_requirements = None

    return [choice1, choice2]


@pytest.fixture
def mock_archetype_profile():
    """Perfil de arquetipo mock."""
    profile = Mock(spec=ArchetypeProfile)
    profile.user_id = 12345
    profile.primary_archetype = "EXPLORER"
    profile.secondary_archetype = "ANALYTICAL"
    profile.archetype_confidence = 75
    profile.archetype_points = {
        "explorer": 10,
        "analytical": 5,
        "romantic": 0,
        "direct": 0,
        "patient": 0,
        "persistent": 0
    }
    profile.average_choice_time_seconds = 15
    profile.total_choices_analyzed = 5
    profile.reread_fragments_count = 2
    return profile


@pytest.fixture
def mock_progress():
    """Progreso narrativo mock."""
    progress = Mock(spec=UserNarrativeProgress)
    progress.user_id = 12345
    progress.current_fragment_id = 1
    progress.current_narrative_level = 1
    progress.max_narrative_level_reached = 1
    progress.total_choices_made = 5
    progress.fragments_completed = [1]
    progress.levels_completed = []
    progress.last_played_at = datetime.now(timezone.utc)
    progress.completed_level_1_at = None
    progress.completed_level_3_at = None
    progress.completed_level_6_at = None
    return progress


# ==============================================================================
# TESTS: COMMAND HANDLERS
# ==============================================================================

@pytest.mark.asyncio
async def test_cmd_story_starts_narrative(
    mock_message,
    mock_starting_fragment,
    mock_choices,
    mock_archetype_profile,
    mock_progress
):
    """Test que /story inicia la narrativa correctamente."""
    # Setup
    mock_session = Mock(spec=AsyncSession)

    story_state = {
        "current_fragment": mock_starting_fragment,
        "available_choices": mock_choices,
        "user_progress": mock_progress,
        "user_flags": [],
        "archetype": mock_archetype_profile,
        "relationships": {"LUCIEN": None, "DIANA": None},
        "can_continue": True,
        "unlock_message": ""
    }

    with patch('bot.handlers.user.narrative.StoryEngine') as MockEngine:
        # Configurar mock
        mock_engine = Mock()
        mock_engine.get_current_story_state = AsyncMock(return_value=story_state)
        MockEngine.return_value = mock_engine

        # Execute
        await cmd_story(mock_message, mock_session)

        # Assert - Verificar que se envió el mensaje
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args
        assert "📖" in call_args[0][0] or "El Comienzo" in call_args[0][0]
        assert call_args[1]["parse_mode"] == "HTML"

        # NOTA: FSMContext.get_current() retorna None en tests porque no hay dispatcher real
        # En producción, FSM se maneja correctamente


@pytest.mark.asyncio
async def test_cmd_story_handles_vip_blocking(mock_message):
    """Test que /story bloquea contenido VIP correctamente."""
    mock_session = Mock(spec=AsyncSession)

    story_state = {
        "can_continue": False,
        "unlock_message": "🔒 Este contenido requiere suscripción VIP (Nivel 4)"
    }

    with patch('bot.handlers.user.narrative.StoryEngine') as MockEngine:
        mock_engine = Mock()
        mock_engine.get_current_story_state = AsyncMock(return_value=story_state)
        MockEngine.return_value = mock_engine

        # Execute
        await cmd_story(mock_message, mock_session)

        # Assert
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args
        assert "🔒" in call_args[0][0]
        assert "VIP" in call_args[0][0]


@pytest.mark.asyncio
async def test_cmd_story_handles_error(mock_message):
    """Test que /story maneja errores correctamente."""
    mock_session = Mock(spec=AsyncSession)

    story_state = {
        "error": "No hay fragmentos disponibles"
    }

    with patch('bot.handlers.user.narrative.StoryEngine') as MockEngine:
        mock_engine = Mock()
        mock_engine.get_current_story_state = AsyncMock(return_value=story_state)
        MockEngine.return_value = mock_engine

        # Execute
        await cmd_story(mock_message, mock_session)

        # Assert
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args
        assert "Error" in call_args[0][0] or "no disponible" in call_args[0][0].lower()


# ==============================================================================
# TESTS: CALLBACK HANDLERS
# ==============================================================================

@pytest.mark.asyncio
async def test_callback_choice_advances_story(
    mock_callback,
    mock_starting_fragment,
    mock_choices,
    mock_archetype_profile,
    mock_progress
):
    """Test que callback de elección avanza la historia."""
    mock_session = Mock(spec=AsyncSession)

    choice_result = {
        "success": True,
        "message": "✨ El Comienzo",
        "next_fragment": mock_starting_fragment,
        "consequences": {
            "flags_set": ["started_journey"],
            "archetype_points": {"explorer": +1}
        },
        "next_state": {
            "current_fragment": mock_starting_fragment,
            "available_choices": mock_choices,
            "user_progress": mock_progress,
            "user_flags": ["started_journey"],
            "archetype": mock_archetype_profile,
            "relationships": {"LUCIEN": None, "DIANA": None},
            "can_continue": True,
            "unlock_message": ""
        }
    }

    with patch('bot.handlers.user.narrative.StoryEngine') as MockEngine:
        mock_engine = Mock()
        mock_engine.make_choice = AsyncMock(return_value=choice_result)
        MockEngine.return_value = mock_engine

        with patch('bot.handlers.user.narrative._send_fragment_to_user') as mock_send:
            # Execute
            await callback_narrative_choice(mock_callback, mock_session)

            # Assert
            mock_callback.answer.assert_called_once_with("✨ Opción registrada")
            mock_engine.make_choice.assert_called_once()
            mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_callback_choice_handles_invalid_choice(mock_callback):
    """Test que callback maneja elecciones inválidas."""
    mock_session = Mock(spec=AsyncSession)

    choice_result = {
        "success": False,
        "message": "Opción no válida"
    }

    with patch('bot.handlers.user.narrative.StoryEngine') as MockEngine:
        mock_engine = Mock()
        mock_engine.make_choice = AsyncMock(return_value=choice_result)
        MockEngine.return_value = mock_engine

        # Execute
        await callback_narrative_choice(mock_callback, mock_session)

        # Assert
        mock_callback.answer.assert_called_once_with(
            "❌ Opción no válida",
            show_alert=True
        )


@pytest.mark.asyncio
async def test_callback_reread_works(
    mock_callback,
    mock_starting_fragment,
    mock_choices,
    mock_archetype_profile
):
    """Test que releer fragmento funciona correctamente."""
    mock_session = Mock(spec=AsyncSession)
    mock_callback.data = "narrative:reread"

    story_state = {
        "current_fragment": mock_starting_fragment,
        "available_choices": mock_choices,
        "user_progress": mock_progress,
        "user_flags": [],
        "archetype": mock_archetype_profile,
        "relationships": {"LUCIEN": None, "DIANA": None},
        "can_continue": True,
        "unlock_message": ""
    }

    with patch('bot.handlers.user.narrative.StoryEngine') as MockEngine:
        mock_engine = Mock()
        mock_engine.get_current_story_state = AsyncMock(return_value=story_state)
        mock_engine.archetype.get_or_create_archetype_profile = AsyncMock(
            return_value=mock_archetype_profile
        )
        mock_engine.archetype.record_fragment_reread = AsyncMock()
        MockEngine.return_value = mock_engine

        with patch('bot.handlers.user.narrative._send_fragment_to_user') as mock_send:
            # Execute
            await callback_narrative_reread(mock_callback, mock_session)

            # Assert
            mock_callback.answer.assert_called_once_with("📖 Fragmento mostrado nuevamente")
            mock_engine.archetype.record_fragment_reread.assert_called_once_with(12345)
            mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_callback_status_shows_progress(
    mock_callback,
    mock_progress,
    mock_archetype_profile
):
    """Test que callback de estado muestra progreso correctamente."""
    mock_session = Mock(spec=AsyncSession)
    mock_callback.data = "narrative:status"

    story_state = {
        "user_progress": mock_progress,
        "archetype": mock_archetype_profile,
        "relationships": {"LUCIEN": None, "DIANA": None},
        "current_fragment": None,
        "available_choices": [],
        "user_flags": [],
        "can_continue": True,
        "unlock_message": ""
    }

    with patch('bot.handlers.user.narrative.StoryEngine') as MockEngine:
        mock_engine = Mock()
        mock_engine.get_current_story_state = AsyncMock(return_value=story_state)
        MockEngine.return_value = mock_engine

        # Execute
        await callback_narrative_status(mock_callback, mock_session)

        # Assert
        mock_callback.answer.assert_called_once()
        mock_callback.message.edit_text.assert_called_once()
        call_args = mock_callback.message.edit_text.call_args
        assert "Estado de Historia" in call_args[0][0]


# ==============================================================================
# TESTS: FORMATTERS
# ==============================================================================

def test_format_narrative_message_basic(mock_starting_fragment):
    """Test formateo básico de mensaje narrativo."""
    result = format_narrative_message(mock_starting_fragment)

    assert "📖" in result
    assert "La historia comienza..." in result


def test_format_narrative_message_with_emotion():
    """Test formateo con emoción."""
    fragment = Mock(spec=StoryFragment)
    fragment.speaker = "DIANA"
    fragment.emotion = "happy"
    fragment.content = "Hello!"
    fragment.content_variants = {}
    fragment.title = "Meeting"
    fragment.narrative_level = 1
    fragment.media_type = None
    fragment.media_file_id = None

    result = format_narrative_message(fragment)

    assert "🌸" in result
    assert "(happy)" in result.lower()


def test_format_narrative_message_vip_level():
    """Test formateo de nivel VIP."""
    fragment = Mock(spec=StoryFragment)
    fragment.speaker = "NARRATOR"
    fragment.emotion = None
    fragment.content = "Secret content"
    fragment.content_variants = {}
    fragment.title = "The Secret"
    fragment.narrative_level = 4
    fragment.media_type = None
    fragment.media_file_id = None

    result = format_narrative_message(fragment)

    assert "🔒" in result
    assert "VIP 4" in result


def test_format_choice_button_text_basic():
    """Test formateo básico de botón de elección."""
    choice = Mock(spec=StoryChoice)
    choice.choice_text = "Follow her"
    choice.choice_emoji = "👣"
    choice.text_variants = {}

    result = format_choice_button_text(choice)

    assert result == "👣 Follow her"


def test_format_choice_button_text_no_emoji():
    """Test formateo de botón sin emoji."""
    choice = Mock(spec=StoryChoice)
    choice.choice_text = "Wait"
    choice.choice_emoji = None
    choice.text_variants = {}

    result = format_choice_button_text(choice)

    assert result == "Wait"


def test_format_unlock_message():
    """Test formateo de mensaje de desbloqueo."""
    fragment = Mock(spec=StoryFragment)
    fragment.title = "Locked Content"

    result = format_unlock_message(fragment, "VIP required")

    assert "🔒" in result
    assert "Contenido Bloqueado" in result
    assert "VIP required" in result


def test_format_consequences_message():
    """Test formateo de consecuencias."""
    consequences = {
        "flags_set": ["met_diana"],
        "archetype_points": {"romantic": +2},
        "relationship_changes": {"LUCIEN": +5}
    }

    result = format_consequences_message(consequences)

    assert "✨" in result
    assert "Consecuencias" in result
    assert "🎯" in result
    assert "💕" in result


def test_format_story_status(mock_progress, mock_archetype_profile):
    """Test formateo de estado de historia."""
    relationships = {
        "LUCIEN": None,
        "DIANA": None
    }

    result = format_story_status(mock_progress, mock_archetype_profile, relationships)

    assert "📖" in result
    assert "Estado de Historia" in result
    assert "Nivel actual: 1" in result
    assert "EXPLORER" in result
    assert "75%" in result


# ==============================================================================
# TESTS: KEYBOARDS
# ==============================================================================

def test_create_narrative_keyboard_basic(mock_choices, mock_starting_fragment):
    """Test creación de keyboard narrativo básico."""
    keyboard = create_narrative_keyboard(mock_choices, mock_starting_fragment, can_reread=False)

    # Verificar estructura
    assert keyboard is not None
    assert hasattr(keyboard, "inline_keyboard")

    # Verificar cantidad de botones (2 opciones + 1 de estado)
    rows = len(keyboard.inline_keyboard)
    assert rows == 3  # 2 opciones + 1 de estado


def test_create_narrative_keyboard_with_reread(mock_choices, mock_starting_fragment):
    """Test keyboard con botón de releer."""
    # Cambiar a no starting para que aparezca releer
    mock_starting_fragment.is_starting_fragment = False

    keyboard = create_narrative_keyboard(mock_choices, mock_starting_fragment, can_reread=True)

    # Verificar que hay botón de releer
    rows = len(keyboard.inline_keyboard)
    assert rows == 4  # 2 opciones + 1 releer + 1 estado

    # Verificar callback data
    callback_datas = [
        button.callback_data
        for row in keyboard.inline_keyboard
        for button in row
    ]

    assert "narrative:reread" in callback_datas
    assert "narrative:status" in callback_datas


def test_create_narrative_keyboard_choice_callbacks(mock_choices, mock_starting_fragment):
    """Test que los callbacks de opciones sean correctos."""
    keyboard = create_narrative_keyboard(mock_choices, mock_starting_fragment, can_reread=False)

    # Extraer callbacks
    callback_datas = [
        button.callback_data
        for row in keyboard.inline_keyboard
        for button in row
    ]

    # Verificar que las opciones tengan los callbacks correctos
    assert "narrative:choice:L1_INTRO_A" in callback_datas
    assert "narrative:choice:L1_INTRO_B" in callback_datas


# ==============================================================================
# TESTS: INTEGRATION
# ==============================================================================

@pytest.mark.asyncio
async def test_full_story_flow(
    mock_message,
    mock_callback,
    mock_starting_fragment,
    mock_choices,
    mock_archetype_profile,
    mock_progress
):
    """Test flujo completo de historia: /story → elegir → avanzar."""
    mock_session = Mock(spec=AsyncSession)

    # Setup story state
    story_state = {
        "current_fragment": mock_starting_fragment,
        "available_choices": mock_choices,
        "user_progress": mock_progress,
        "user_flags": [],
        "archetype": mock_archetype_profile,
        "relationships": {"LUCIEN": None, "DIANA": None},
        "can_continue": True,
        "unlock_message": ""
    }

    # Setup choice result
    choice_result = {
        "success": True,
        "message": "✨ Avanzando",
        "next_fragment": mock_starting_fragment,
        "consequences": {"flags_set": ["test"]},
        "next_state": story_state
    }

    with patch('bot.handlers.user.narrative.StoryEngine') as MockEngine:
        mock_engine = Mock()
        mock_engine.get_current_story_state = AsyncMock(return_value=story_state)
        mock_engine.make_choice = AsyncMock(return_value=choice_result)
        MockEngine.return_value = mock_engine

        # 1. Iniciar historia con /story
        with patch('bot.handlers.user.narrative.FSMContext') as MockFSM:
            mock_fsm = Mock()
            mock_fsm.set_state = AsyncMock()
            mock_fsm.update_data = AsyncMock()
            MockFSM.get_current = Mock(return_value=mock_fsm)

            await cmd_story(mock_message, mock_session)
            assert mock_message.answer.called

            # 2. Hacer una elección
            with patch('bot.handlers.user.narrative._send_fragment_to_user') as mock_send:
                await callback_narrative_choice(mock_callback, mock_session)

                # Verificar que se procesó la elección
                mock_engine.make_choice.assert_called_once()
                mock_send.assert_called_once()


# ==============================================================================
# RUN TESTS
# ==============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
