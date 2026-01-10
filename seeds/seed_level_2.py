"""
Seed script for Level 2 narrative content.

Level 2: "Observación y Prueba"

This script creates:
- 5 fragments: Return, Challenge, Success, Partial, Timeout
- 2 choices: Accept, Postpone

Usage:
    python -m seeds.seed_level_2
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import select
from bot.database import get_session
from bot.database.models import StoryFragment, StoryChoice

logger = logging.getLogger(__name__)


# Level 2 Fragments
LEVEL_2_FRAGMENTS = [
    {
        "fragment_id": "L2_RETURN_001",
        "narrative_level": 2,
        "title": "El Regreso Observado",
        "content_text": (
            "🌸 <i>(intrigada, divertida)</i>\n\n"
            "Oh... ha regresado.\n\n"
            "Noté que decidiste volver. No es algo que suceda a menudo, "
            "que alguien decida permanecer después del primer encuentro. "
            "Hay una... persistencia en ti que encuentro genuinamente interesante.\n\n"
            "<i>Se acerca un poco más, su mirada curiosa analizando cada detalle.</i>\n\n"
            "¿Sabes? La mayoría se va después de la primera introducción. "
            "Pero tú... tú decidiste quedarte. Eso dice algo sobre ti.\n\n"
            "🎭 *Pista 1*: Diana parece intrigada por tu regreso."
        ),
        "speaker": "DIANA",
        "speaker_emotion": "intrigued_amused",
        "is_starting_fragment": True,
        "sort_order": 0,
        "active": True,
        "besitos_reward": 10
    },
    {
        "fragment_id": "L2_CHALLENGE_002",
        "narrative_level": 2,
        "title": "El Desafío de Observación",
        "content_text": (
            "🎩 <i>(formal, evaluando)</i>\n\n"
            "Bienvenido de nuevo.\n\n"
            "He notado su persistencia. Diana también. Sin embargo, "
            "persistencia por sí sola no es suficiente para acceder a "
            "los verdaderos misterios de este lugar.\n\n"
            "Le propongo una prueba simple: observe.\n\n"
            "Durante los próximos tres días, debe observar con atención "
            "el contenido que compartimos en el canal. Hay detalles... "
            "pistas, podríamos decirlas... que solo quienes verdaderamente "
            "observan pueden descubrir.\n\n"
            "Busque al menos tres pistas ocultas. Si tiene éxito, "
            "Diana se interesará aún más en su caso. Si solo descubre "
            "una o dos... bueno, al menos habrá demostrado esfuerzo.\n\n"
            "⏱️ *Tiene 3 días para encontrar pistas en el canal.*\n\n"
            "🎭 *Pista 2*: Lucien menciona específicamente buscar pistas "
            "en el contenido del canal."
        ),
        "speaker": "LUCIEN",
        "speaker_emotion": "testing",
        "is_starting_fragment": False,
        "sort_order": 1,
        "active": True,
        "besitos_reward": 15
    },
    {
        "fragment_id": "L2_SUCCESS_003",
        "narrative_level": 2,
        "title": "Observación Exitosa",
        "content_text": (
            "🌸 <i>(genuinamente sorprendida, impresionada)</i>\n\n"
            "Lo hiciste.\n\n"
            "Encontraste las pistas. Todas. No esperaba... "
            "de verdad, no esperaba que alguien notara tantos detalles "
            "tan rápidamente.\n\n"
            "<i>Su expresión se suaviza, la curiosidad reemplazando "
            "la reserva habitual.</i>\n\n"
            "Lucien me dijo lo que descubrió. Tienes una capacidad de "
            "observación... es rara. Valiosa. Esas pistas no estaban "
            "puestas al azar; estaban esperando a alguien como tú.\n\n"
            "Tu atención a los detalles... dice mucho de quién eres. "
            "Y eso es algo que quiero explorar más.\n\n"
            "🎁 Has ganado 20 besitos por tu excelencia observadora.\n\n"
            "🔓 *Nueva pista desbloqueada*: Diana quiere conocerte mejor."
        ),
        "speaker": "DIANA",
        "speaker_emotion": "genuine_surprise",
        "is_starting_fragment": False,
        "is_ending_fragment": True,
        "sort_order": 2,
        "active": True,
        "besitos_reward": 20,
        "unlock_conditions": {
            "required_flags": ["l2_observation_complete"],
            "observation_clues_min": 3
        }
    },
    {
        "fragment_id": "L2_PARTIAL_004",
        "narrative_level": 2,
        "title": "Observación Parcial",
        "content_text": (
            "🌸 <i>(alentadora, comprensiva)</i>\n\n"
            "Volví.\n\n"
            "Lucien me dijo que encontraste algunas pistas... no todas, "
            "pero algunas. Y eso también cuenta.\n\n"
            "<i>Su tono es más suave que antes.</i>\n\n"
            "La verdadera observación requiere práctica. Tiempo. Paciencia. "
            "Y demostraste que estás dispuesto a intentarlo, que quieres "
            "entender más allá de lo superficial.\n\n"
            "Esa disposición... esa voluntad de seguir buscando aunque "
            "no todo sea inmediatamente claro... eso también es valioso.\n\n"
            "🎁 Has ganado 10 besitos por tu esfuerzo observador.\n\n"
            "💡 *Consejo*: Continúa observando. Los detalles revelan más "
            "de lo que parece."
        ),
        "speaker": "DIANA",
        "speaker_emotion": "encouraging",
        "is_starting_fragment": False,
        "is_ending_fragment": True,
        "sort_order": 3,
        "active": True,
        "besitos_reward": 10,
        "unlock_conditions": {
            "required_flags": ["l2_observation_partial"],
            "observation_clues_min": 1
        }
    },
    {
        "fragment_id": "L2_TIMEOUT_005",
        "narrative_level": 2,
        "title": "Tiempo Agotado",
        "content_text": (
            "🎩 <i>(decepcionado, formal)</i>\n\n"
            "El tiempo ha concluido.\n\n"
            "Le di tres días. Tres días para observar, para notar, para "
            "descubrir lo que otros pasan por alto. Y parece que... "
            "no fue suficiente.\n\n"
            "<i>Su mirada evalúa sin juzgar.</i>\n\n"
            "No todos están hechos para este tipo de atenciones, supongo. "
            "La observación profunda no es para todos. Requiere algo "
            "que quizás... no está disponible en este momento.\n\n"
            "Sin embargo, la puerta no está cerrada permanentemente. "
            "Si decide volver a intentarlo, sabremos si su dedicación "
            "ha aumentado.\n\n"
            "🎁 Has ganado 5 besitos por tu participación.\n\n"
            "⏳ *La prueba de observación puede repetirse más adelante.*"
        ),
        "speaker": "LUCIEN",
        "speaker_emotion": "disappointed",
        "is_starting_fragment": False,
        "is_ending_fragment": True,
        "sort_order": 4,
        "active": True,
        "besitos_reward": 5,
        "unlock_conditions": {
            "observation_timeout": True
        }
    }
]


# Level 2 Choices
LEVEL_2_CHOICES = [
    {
        "choice_id": "L2_ACCEPT_A",
        "fragment_id_ref": "L2_RETURN_001",
        "target_fragment_id_ref": "L2_CHALLENGE_002",
        "choice_text": "✅ Acepto el desafío de observación",
        "choice_description": "Iniciar la prueba de observación de 3 días",
        "sort_order": 1,
        "active": True,
        "consequences": {
            "flags_set": ["l2_observation_started"],
            "relationship_change": {
                "LUCIEN": +2
            },
            "besitos_reward": 5
        }
    },
    {
        "choice_id": "L2_POSTPONE",
        "fragment_id_ref": "L2_RETURN_001",
        "target_fragment_id_ref": "L2_RETURN_001",  # Returns to same, can retry
        "choice_text": "⏳ Necesito tiempo para decidir",
        "choice_description": "Posponer la decisión, puedes retomar después",
        "sort_order": 2,
        "active": True,
        "consequences": {
            "flags_set": ["l2_postponed"],
            "relationship_change": {
                "LUCIEN": -1
            }
        }
    }
]


async def seed_level_2():
    """Seed Level 2 narrative content."""
    logger.info("🌱 Starting Level 2 narrative seeding...")

    # Initialize database first
    from bot.database import init_db
    await init_db()

    async with get_session() as session:
        # Create fragments
        for frag_data in LEVEL_2_FRAGMENTS:
            # Check if fragment exists
            stmt = select(StoryFragment).where(
                StoryFragment.fragment_id == frag_data["fragment_id"]
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing fragment
                for key, value in frag_data.items():
                    if key != "fragment_id":  # Don't update the ID
                        setattr(existing, key, value)
                logger.info(f"  ✓ Updated fragment: {frag_data['fragment_id']}")
            else:
                # Create new fragment
                fragment = StoryFragment(**frag_data)
                session.add(fragment)
                logger.info(f"  + Created fragment: {frag_data['fragment_id']}")

        # Commit fragments first to get IDs
        await session.commit()

        # Create choices
        for choice_data in LEVEL_2_CHOICES:
            # Check if choice exists
            stmt = select(StoryChoice).where(
                StoryChoice.choice_id == choice_data["choice_id"]
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            # Get fragment IDs by reference
            from_frag_stmt = select(StoryFragment).where(
                StoryFragment.fragment_id == choice_data["fragment_id_ref"]
            )
            from_result = await session.execute(from_frag_stmt)
            from_fragment = from_result.scalar_one_or_none()

            to_frag_stmt = select(StoryFragment).where(
                StoryFragment.fragment_id == choice_data["target_fragment_id_ref"]
            )
            to_result = await session.execute(to_frag_stmt)
            to_fragment = to_result.scalar_one_or_none()

            if not from_fragment or not to_fragment:
                logger.error(f"  ✗ Cannot find fragments for choice {choice_data['choice_id']}")
                continue

            # Prepare choice data
            choice_data_clean = {
                "choice_id": choice_data["choice_id"],
                "fragment_id": from_fragment.id,
                "target_fragment_id": to_fragment.id,
                "choice_text": choice_data["choice_text"],
                "choice_description": choice_data.get("choice_description"),
                "sort_order": choice_data.get("sort_order", 0),
                "active": choice_data.get("active", True),
                "consequences": choice_data.get("consequences")
            }

            if existing:
                # Update existing choice
                for key, value in choice_data_clean.items():
                    if key != "choice_id":
                        setattr(existing, key, value)
                logger.info(f"  ✓ Updated choice: {choice_data['choice_id']}")
            else:
                # Create new choice
                choice = StoryChoice(**choice_data_clean)
                session.add(choice)
                logger.info(f"  + Created choice: {choice_data['choice_id']}")

        await session.commit()

    logger.info("✅ Level 2 narrative seeding complete!")
    logger.info(f"   - {len(LEVEL_2_FRAGMENTS)} fragments")
    logger.info(f"   - {len(LEVEL_2_CHOICES)} choices")


async def main():
    """Main entry point."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )

    # Run seeding
    try:
        await seed_level_2()
    except Exception as e:
        logger.error(f"Seeding failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
