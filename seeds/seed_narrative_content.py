"""
Seed script for Level 1 narrative content - "Los Kinkys"

This script seeds the database with the complete Level 1 narrative story,
including fragments, choices, and consequences based on the creative script.

Usage:
    python -m seeds.seed_narrative_content

Level 1 Structure:
    - Scene 1: Diana's Welcome (L1_INTRO_001)
    - Scene 2: Lucien's Challenge (L1_INTRO_002)
    - Scene 3A: Quick Response (L1_RESPONSE_QUICK)
    - Scene 3B: Patient Response (L1_RESPONSE_PATIENT)
    - Scene 4: First Clue (L1_FIRST_CLUE)
"""
import asyncio
import logging
from datetime import datetime, UTC

from sqlalchemy import select
from bot.database.engine import init_db, get_session
from bot.database.models import StoryFragment, StoryChoice

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# =============================================================================
# NARRATIVE CONTENT - LEVEL 1
# =============================================================================

LEVEL_1_FRAGMENTS = [
    {
        "fragment_id": "L1_INTRO_001",
        "title": "Bienvenida de Diana",
        "narrative_level": 1,
        "content_text": """🌸 **Diana:**
*[Voz susurrante, como quien comparte un secreto]*

Bienvenido a Los Kinkys.
Has cruzado una línea que muchos ven... pero pocos realmente atraviesan.

Puedo sentir tu curiosidad desde aquí. Es... intrigante.
No todos llegan con esa misma hambre en los ojos.

Este lugar responde a quienes saben que algunas puertas solo se abren desde adentro.
Y yo... bueno, yo solo me revelo ante quienes comprenden que lo más valioso nunca se entrega fácilmente.

*[Pausa, como si estuviera evaluando al usuario]*

Algo me dice que tú podrías ser diferente.
Pero eso... eso está por verse.""",
        "speaker": "DIANA",
        "speaker_emotion": "mysterious",
        "is_starting_fragment": True,
        "is_ending_fragment": False,
        "sort_order": 1,
    },
    {
        "fragment_id": "L1_INTRO_002",
        "title": "Lucien y el Primer Desafío",
        "narrative_level": 1,
        "content_text": """🎩 **Lucien:**
Ah, otro visitante de Diana.
Permíteme presentarme: Lucien, guardián de los secretos que ella no cuenta... todavía.

Veo que Diana ya plantó esa semilla de curiosidad en ti. Lo noto en cómo llegaste hasta aquí.
Pero la curiosidad sin acción es solo... voyeurismo pasivo.

Diana observa. Siempre observa.
Y lo que más le fascina no es la obediencia ciega, sino la intención detrás de cada gesto.

**Misión:** Reacciona al último mensaje del canal. Pero hazlo porque realmente quieres entender, no porque se te ordena.""",
        "speaker": "LUCIEN",
        "speaker_emotion": "formal",
        "is_starting_fragment": False,
        "is_ending_fragment": False,
        "sort_order": 2,
        "besitos_reward": 10,
    },
    {
        "fragment_id": "L1_RESPONSE_QUICK",
        "title": "Respuesta para Usuario que Reacciona Inmediatamente",
        "narrative_level": 1,
        "content_text": """🎩 **Lucien:**
Interesante... reaccionaste sin dudar. Hay algo hermoso en esa espontaneidad.
Diana aprecia a quienes no se pierden en la sobreanalización.

*[Diana aparece brevemente]*

🌸 **Diana:**
*[Con una sonrisa apenas perceptible]*
Impulsivo... pero no imprudente. Hay una diferencia que pocos entienden.
Me gusta eso de ti.

**Entrega: Mochila del Viajero + Pista 1**

🎩 **Lucien:**
Tu Mochila del Viajero. Dentro encontrarás tu primera pista.
Diana la eligió específicamente para alguien como tú: alguien que actúa cuando siente que algo es correcto.""",
        "speaker": "LUCIEN",
        "speaker_emotion": "approving",
        "is_starting_fragment": False,
        "is_ending_fragment": False,
        "sort_order": 3,
        "besitos_reward": 15,
        "unlocks_reward_id": None,  # Will be set to "mochila_viajero" reward
    },
    {
        "fragment_id": "L1_RESPONSE_PATIENT",
        "title": "Respuesta para Usuario que Toma Tiempo",
        "narrative_level": 1,
        "content_text": """🎩 **Lucien:**
Hmm... te tomaste tu tiempo. Observaste, evaluaste, consideraste.
Hay sabiduría en esa paciencia que Diana encuentra... seductora.

*[Diana aparece brevemente]*

🌸 **Diana:**
*[Con mirada pensativa]*
Me fascina cómo algunos saben que lo genuino no debe apresurarse.
Tu manera de aproximarte dice más de ti que cualquier reacción impulsiva.

**Entrega: Mochila del Viajero + Pista 1**

🎩 **Lucien:**
Tu Mochila del Viajero. La pista que encontrarás dentro fue seleccionada para alguien que comprende que los mejores secretos se revelan a quienes saben esperar el momento correcto.""",
        "speaker": "LUCIEN",
        "speaker_emotion": "appreciative",
        "is_starting_fragment": False,
        "is_ending_fragment": False,
        "sort_order": 4,
        "besitos_reward": 15,
        "unlocks_reward_id": None,  # Will be set to "mochila_viajero" reward
    },
    {
        "fragment_id": "L1_FIRST_CLUE",
        "title": "La Primera Pista",
        "narrative_level": 1,
        "content_text": """🎩 **Lucien:**
*[Presentando el mapa fragmentado]*

Un mapa incompleto. Pero claro... solo tienes la mitad.
Diana no cree en las respuestas fáciles.

*[Diana se materializa por un momento]*

🌸 **Diana:**
*[Mirando directamente al usuario]*
La otra mitad... no existe en este mundo que conoces.
Está donde las reglas cambian, donde yo puedo ser... más de lo que aquí me permito ser.

¿Estás preparado para buscar en lugares donde no todos pueden entrar?
Porque una vez que cruces completamente hacia mí... no hay vuelta atrás.

**Misión Continua:** Las pistas aparecen cuando Diana siente que estás listo. No hay horarios. No hay garantías. Solo... conexión.""",
        "speaker": "LUCIEN",
        "speaker_emotion": "mysterious",
        "is_starting_fragment": False,
        "is_ending_fragment": True,
        "sort_order": 5,
        "besitos_reward": 20,
        "experience_reward": 50,
    },
]

LEVEL_1_CHOICES = [
    {
        "choice_id": "L1_INTRO_A",
        "fragment_id_ref": "L1_INTRO_001",  # From this fragment
        "target_fragment_id_ref": "L1_INTRO_002",  # To this fragment
        "choice_text": "🚪 Descubrir más",
        "choice_description": "Cruzar el umbral hacia lo desconocido",
        "choice_emoji": "🚪",
        "sort_order": 1,
        "consequences": {
            "flags_set": ["impulsive_choice", "met_lucien"],
            "archetype_points": {
                "direct": 2,
                "explorer": 1
            },
            "relationship_change": {
                "DIANA": 2
            }
        }
    },
    {
        "choice_id": "L1_INTRO_B",
        "fragment_id_ref": "L1_INTRO_002",  # From this fragment
        "target_fragment_id_ref": "L1_RESPONSE_QUICK",  # To this fragment (default)
        "choice_text": "✨ Entendido",
        "choice_description": "Aceptar el desafío de Lucien",
        "choice_emoji": "✨",
        "sort_order": 1,
        "consequences": {
            "flags_set": ["accepted_lucien_challenge"],
            "besitos_reward": 10
        }
    },
]


# =============================================================================
# SEED FUNCTIONS
# =============================================================================

async def seed_level_1_fragments() -> None:
    """
    Seed Level 1 narrative fragments to the database.

    Creates or updates fragments with proper IDs and content.
    """
    async with get_session() as session:
        created_count = 0
        updated_count = 0

        for fragment_data in LEVEL_1_FRAGMENTS:
            # Check if fragment already exists
            stmt = select(StoryFragment).where(
                StoryFragment.fragment_id == fragment_data["fragment_id"]
            )
            result = await session.execute(stmt)
            existing_fragment = result.scalar_one_or_none()

            if existing_fragment:
                # Update existing fragment
                for key, value in fragment_data.items():
                    setattr(existing_fragment, key, value)
                updated_count += 1
                logger.info(f"✏️  Updated fragment: {fragment_data['fragment_id']}")
            else:
                # Create new fragment
                fragment = StoryFragment(**fragment_data)
                session.add(fragment)
                created_count += 1
                logger.info(f"✅ Created fragment: {fragment_data['fragment_id']}")

        await session.commit()
        logger.info(f"✅ Level 1 fragments seeded: {created_count} created, {updated_count} updated")


async def seed_level_1_choices() -> None:
    """
    Seed Level 1 narrative choices to the database.

    Creates choices with proper fragment references and consequences.
    This must run AFTER fragments are seeded, so we can resolve IDs.
    """
    async with get_session() as session:
        created_count = 0
        updated_count = 0

        for choice_data in LEVEL_1_CHOICES:
            # Get fragment IDs from references
            from_fragment_id = choice_data.pop("fragment_id_ref")
            to_fragment_id = choice_data.pop("target_fragment_id_ref")

            # Query fragment IDs
            stmt_from = select(StoryFragment.id).where(
                StoryFragment.fragment_id == from_fragment_id
            )
            stmt_to = select(StoryFragment.id).where(
                StoryFragment.fragment_id == to_fragment_id
            )

            result_from = await session.execute(stmt_from)
            from_id = result_from.scalar_one()

            result_to = await session.execute(stmt_to)
            to_id = result_to.scalar_one()

            # Set the actual IDs
            choice_data["fragment_id"] = from_id
            choice_data["target_fragment_id"] = to_id

            # Check if choice already exists
            stmt = select(StoryChoice).where(
                StoryChoice.choice_id == choice_data["choice_id"]
            )
            result = await session.execute(stmt)
            existing_choice = result.scalar_one_or_none()

            if existing_choice:
                # Update existing choice
                for key, value in choice_data.items():
                    setattr(existing_choice, key, value)
                updated_count += 1
                logger.info(f"✏️  Updated choice: {choice_data['choice_id']}")
            else:
                # Create new choice
                choice = StoryChoice(**choice_data)
                session.add(choice)
                created_count += 1
                logger.info(f"✅ Created choice: {choice_data['choice_id']}")

        await session.commit()
        logger.info(f"✅ Level 1 choices seeded: {created_count} created, {updated_count} updated")


async def verify_level_1_content() -> None:
    """
    Verify that Level 1 content was seeded correctly.

    Checks that all fragments and choices exist and are properly linked.
    """
    async with get_session() as session:
        # Verify fragments
        stmt_fragments = select(StoryFragment).where(
            StoryFragment.narrative_level == 1
        ).order_by(StoryFragment.sort_order)

        result = await session.execute(stmt_fragments)
        fragments = result.scalars().all()

        logger.info(f"\n{'='*60}")
        logger.info("LEVEL 1 NARRATIVE CONTENT VERIFICATION")
        logger.info(f"{'='*60}\n")

        logger.info(f"📜 Fragments found: {len(fragments)}")
        for frag in fragments:
            ending_mark = " [ENDING]" if frag.is_ending_fragment else ""
            starting_mark = " [STARTING]" if frag.is_starting_fragment else ""
            logger.info(
                f"  • {frag.fragment_id}: {frag.title}"
                f"{starting_mark}{ending_mark}"
            )

        # Verify choices
        stmt_choices = select(StoryChoice)
        result = await session.execute(stmt_choices)
        choices = result.scalars().all()

        logger.info(f"\n🔗 Choices found: {len(choices)}")
        for choice in choices:
            logger.info(f"  • {choice.choice_id}: {choice.choice_text}")

        # Verify starting fragments
        stmt_start = select(StoryFragment).where(
            StoryFragment.narrative_level == 1,
            StoryFragment.is_starting_fragment == True
        )
        result = await session.execute(stmt_start)
        starting_fragments = result.scalars().all()

        if starting_fragments:
            logger.info(f"\n✅ Starting fragments ({len(starting_fragments)}):")
            for frag in starting_fragments:
                logger.info(f"  • {frag.fragment_id}")
        else:
            logger.warning("\n⚠️  No starting fragment found for Level 1!")

        # Verify ending fragments
        stmt_end = select(StoryFragment).where(
            StoryFragment.narrative_level == 1,
            StoryFragment.is_ending_fragment == True
        )
        result = await session.execute(stmt_end)
        ending_fragments = result.scalars().all()

        if ending_fragments:
            logger.info(f"✅ Ending fragments ({len(ending_fragments)}):")
            for frag in ending_fragments:
                logger.info(f"  • {frag.fragment_id}")
        else:
            logger.warning("⚠️  No ending fragment found for Level 1!")

        logger.info(f"\n{'='*60}\n")


async def main():
    """
    Main seed function.

    Initializes database, seeds Level 1 content, and verifies results.
    """
    logger.info("🌱 Starting Level 1 narrative content seed...\n")

    # Initialize database
    await init_db()
    logger.info("✅ Database initialized\n")

    # Seed fragments
    logger.info("📜 Seeding Level 1 fragments...")
    await seed_level_1_fragments()
    logger.info("")

    # Seed choices (must be after fragments)
    logger.info("🔗 Seeding Level 1 choices...")
    await seed_level_1_choices()
    logger.info("")

    # Verify content
    logger.info("🔍 Verifying seeded content...")
    await verify_level_1_content()

    logger.info("🎉 Level 1 narrative content seeded successfully!")
    logger.info("\nNext steps:")
    logger.info("  1. Test the narrative flow with /start command")
    logger.info("  2. Verify fragment transitions work correctly")
    logger.info("  3. Check that rewards and consequences are applied")


if __name__ == "__main__":
    asyncio.run(main())
