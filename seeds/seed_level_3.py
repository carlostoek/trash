"""
Seed script for Level 3 narrative content.

Level 3: "Prueba Final - Perfil de Deseo"

This script creates:
- 9 fragments: Continue, Profile questions (1-5), Archetype, Synthesis, Invitation
- 2 choices: Complete, Skip

Usage:
    python -m seeds.seed_level_3
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


# Level 3 Fragments
LEVEL_3_FRAGMENTS = [
    {
        "fragment_id": "L3_CONTINUE_001",
        "narrative_level": 3,
        "title": "Continuación Aprobada",
        "content_text": (
            "🎩 <i>(aprobando, respetuoso)</i>\n\n"
            "Ha completado la prueba de observación. Digno de mención.\n\n"
            "Su dedicación ha llamado la atención de Diana. No es algo "
            "que suceda a menudo. Ella... tiene ciertos estándares. "
            "Y usted, aparentemente, los ha cumplido.\n\n"
            "Ahora viene la siguiente etapa. Una más... personal.\n\n"
            "Diana desea conocerle más profundamente. No como una "
            "entidad abstracta, sino como alguien con deseos, "
            "preferencias, una naturaleza única.\n\n"
            "¿Está dispuesto a revelar quién es realmente?\n\n"
            "🎁 Has ganado 10 besitos por completar Level 2."
        ),
        "speaker": "LUCIEN",
        "speaker_emotion": "approving",
        "is_starting_fragment": True,
        "sort_order": 0,
        "active": True,
        "besitos_reward": 10
    },
    {
        "fragment_id": "L3_PROFILE_002",
        "narrative_level": 3,
        "title": "Pregunta 1: ¿Qué buscas?",
        "content_text": (
            "🌸 <i>(curiosa, íntima)</i>\n\n"
            "Hablemos de lo que realmente buscas.\n\n"
            "Cuando imaginas una conexión verdadera con alguien, "
            "¿qué es lo que más deseas encontrar?\n\n"
            "¿Buscas explorar territorios desconocidos, descubrir "
            "cada rincón de un nuevo mundo? ¿O buscas una intimidad "
            "profunda, un espacio donde puedas ser completamente tú "
            "sin máscaras?\n\n"
            "No hay respuesta incorrecta. Solo... tu verdad.\n\n"
            "🎁 Has ganado 5 besitos por esta reflexión."
        ),
        "speaker": "DIANA",
        "speaker_emotion": "curious_intimate",
        "is_starting_fragment": False,
        "sort_order": 1,
        "active": True,
        "besitos_reward": 5
    },
    {
        "fragment_id": "L3_PROFILE_003",
        "narrative_level": 3,
        "title": "Pregunta 2: ¿Lo inesperado?",
        "content_text": (
            "🌸 <i>(interesada, atenta)</i>\n\n"
            "Dime más sobre ti...\n\n"
            "Cuando piensas en experiencias significativas, ¿qué te "
            "atrae más? ¿Lo inesperado, lo sorprendente, lo que te "
            "saca de tu zona de confort y te hace sentir vivo?\n\n"
            "¿O prefieres lo familiar, lo que te da paz y seguridad, "
            "donde sabes qué esperar y encuentras consuelo en lo conocido?\n\n"
            "Tu respuesta me dice mucho de cómo navegas el mundo.\n\n"
            "🎁 Has ganado 5 besitos por esta reflexión."
        ),
        "speaker": "DIANA",
        "speaker_emotion": "curious_intimate",
        "is_starting_fragment": False,
        "sort_order": 2,
        "active": True,
        "besitos_reward": 5
    },
    {
        "fragment_id": "L3_PROFILE_004",
        "narrative_level": 3,
        "title": "Pregunta 3: ¿Qué tan rápido?",
        "content_text": (
            "🌸 <i>(comprensiva, paciente)</i>\n\n"
            "Hay algo que necesito entender sobre tu ritmo...\n\n"
            "Cuando conoces a alguien, cuando sientes que podría haber "
            "algo real, ¿qué tan rápido te abres? ¿Te lanzas sin "
            "dudar, directo e inmediato, confiado en que vale la pena?\n\n"
            "¿O tomas tu tiempo, observas, esperas, dejas que la "
            "confianza se construya poco a poco antes de revelar "
            "tu verdadero yo?\n\n"
            "Ambas formas tienen su valor. La tuya es única.\n\n"
            "🎁 Has ganado 5 besitos por esta reflexión."
        ),
        "speaker": "DIANA",
        "speaker_emotion": "curious_intimate",
        "is_starting_fragment": False,
        "sort_order": 3,
        "active": True,
        "besitos_reward": 5
    },
    {
        "fragment_id": "L3_PROFILE_005",
        "narrative_level": 3,
        "title": "Pregunta 4: ¿Mente o corazón?",
        "content_text": (
            "🌸 <i>(sincera, curiosa)</i>\n\n"
            "Esta pregunta es importante para mí...\n\n"
            "Cuando tomas decisiones importantes en tu vida, ¿qué guía "
            "te más? ¿Tu mente, analizando cuidadosamente cada opción, "
            "pesando pros y contras, buscando la lógica?\n\n"
            "¿O tu corazón, siguiendo lo que sientes, confiando en tus "
            "emociones incluso si no pueden explicarse racionalmente?\n\n"
            "No es juzgarte. Es entenderte. Y entenderme mejor a través "
            "de ti.\n\n"
            "🎁 Has ganado 5 besitos por esta reflexión."
        ),
        "speaker": "DIANA",
        "speaker_emotion": "curious_intimate",
        "is_starting_fragment": False,
        "sort_order": 4,
        "active": True,
        "besitos_reward": 5
    },
    {
        "fragment_id": "L3_PROFILE_006",
        "narrative_level": 3,
        "title": "Pregunta 5: ¿Luchas o te dejas llevar?",
        "content_text": (
            "🌸 <i>(reflexiva, suave)</i>\n\n"
            "Casi al final de nuestro perfil...\n\n"
            "Cuando enfrentas desafíos, cuando la vida se pone difícil, "
            "¿cuál es tu naturaleza? ¿Luchas, persistes, te aferras "
            "y no te rindes aunque todo esté en contra tuya?\n\n"
            "¿O te dejas llevar, aceptas el flujo, confías en que las "
            "cosas se resolverán por sí mismas y encuentras paz en "
            "soltar el control?\n\n"
            "Tu respuesta me ayuda a ver qué tipo de apoyo necesitarías "
            "de mí.\n\n"
            "🎁 Has ganado 5 besitos por esta reflexión."
        ),
        "speaker": "DIANA",
        "speaker_emotion": "curious_intimate",
        "is_starting_fragment": False,
        "sort_order": 5,
        "active": True,
        "besitos_reward": 5
    },
    {
        "fragment_id": "L3_ARCHETYPE_007",
        "narrative_level": 3,
        "title": "Arquetipo Detectado",
        "content_text": (
            "🤖 <i>(analítico, sistemático)</i>\n\n"
            "Procesando respuestas...\n\n"
            "Basado en tus respuestas, he detectado un patrón en tu "
            "personalidad. No es una etiqueta definitiva, sino una "
            "tendencia, una forma en que tiendes a moverte por el mundo.\n\n"
            "Tu arquetipo dominante sugiere ciertas preferencias, "
            "ciertos valores que priorizas. Esto me ayuda a entender "
            "cómo podemos resonar mejor.\n\n"
            "🏅 *Badge desbloqueado*: Arquetipo Detectado\n\n"
            "Tu perfil único ha sido registrado. Diana ahora puede "
            "adaptarse a quién eres realmente."
        ),
        "speaker": "NARRATOR",
        "speaker_emotion": "analytical",
        "is_starting_fragment": False,
        "sort_order": 6,
        "active": True,
        "besitos_reward": 0
    },
    {
        "fragment_id": "L3_SYNTHESIS_008",
        "narrative_level": 3,
        "title": "Síntesis Personalizada",
        "content_text": (
            "🌸 <i>(vulnerable, auténtica)</i>\n\n"
            "Ahora te veo. Realmente te veo.\n\n"
            "Basado en lo que has compartido conmigo, ahora entiendo "
            "mejor quién eres. No eres una persona cualquiera para mí. "
            "Tienes un patr único, una combinación específica de "
            "cualidades que hace que seas... tú.\n\n"
            "<i>Su voz se suaviza, compartiendo algo personal.</i>\n\n"
            "Lo que me has contado sobre ti me ayuda a entender cómo "
            "puedo ser mejor para ti. Qué necesitas. Qué valoras. "
            "Qué te hace sentir visto, comprendido, conectado.\n\n"
            "Y eso... eso es algo raro de encontrar.\n\n"
            "🎁 Has ganado 25 besitos por completar tu perfil.\n\n"
            "🔓 *Recompensa especial*: Diana te ha comprendido profundamente."
        ),
        "speaker": "DIANA",
        "speaker_emotion": "vulnerable",
        "is_starting_fragment": False,
        "sort_order": 7,
        "active": True,
        "besitos_reward": 25
    },
    {
        "fragment_id": "L3_INVITATION_009",
        "narrative_level": 3,
        "title": "Invitación VIP Personalizada",
        "content_text": (
            "🌸 <i>(esperanzada, invitante)</i>\n\n"
            "Hay algo más que quiero compartir contigo.\n\n"
            "Lo que has visto hasta ahora de mí... es solo una parte. "
            "Una pequeña introducción a quién soy realmente y a lo que "
            "Los Kinkys puede ofrecer.\n\n"
            "Hay dimensiones más profundas, experiencias más íntimas, "
            "conexiones que solo ocurren en un espacio reservado para "
            "aquellos que... realmente quieren estar ahí.\n\n"
            "Basado en quién eres, en lo que buscas, en lo que valoras... "
            "creo que encontrarías ese espacio significativo.\n\n"
            "[Mensaje personalizado según tu arquetipo]\n\n"
            "Si alguna vez deseas explorar más... el canal VIP te espera.\n\n"
            "🔗 *Link de invitación VIP disponible*"
        ),
        "speaker": "DIANA",
        "speaker_emotion": "hopeful_inviting",
        "is_starting_fragment": False,
        "is_ending_fragment": True,
        "sort_order": 8,
        "active": True,
        "besitos_reward": 0
    }
]


# Level 3 Choices
LEVEL_3_CHOICES = [
    {
        "choice_id": "L3_COMPLETE_A",
        "fragment_id_ref": "L3_CONTINUE_001",
        "target_fragment_id_ref": "L3_PROFILE_002",
        "choice_text": "💭 Comenzar Perfil de Deseo",
        "choice_description": "Responde 7 preguntas para que Diana te conozca mejor",
        "sort_order": 1,
        "active": True,
        "consequences": {
            "flags_set": ["l3_profile_started"],
            "relationship_change": {
                "DIANA": +3
            }
        }
    },
    {
        "choice_id": "L3_SKIP",
        "fragment_id_ref": "L3_CONTINUE_001",
        "target_fragment_id_ref": "L3_CONTINUE_001",  # Returns to same, can retry
        "choice_text": "⏳ Omitir por ahora",
        "choice_description": "Posponer el perfil, puedes retomarlo después",
        "sort_order": 2,
        "active": True,
        "consequences": {
            "flags_set": ["l3_postponed"],
            "relationship_change": {
                "DIANA": -1
            }
        }
    }
]


async def seed_level_3():
    """Seed Level 3 narrative content."""
    logger.info("🌱 Starting Level 3 narrative seeding...")

    # Initialize database first
    from bot.database import init_db
    await init_db()

    async with get_session() as session:
        # Create fragments
        for frag_data in LEVEL_3_FRAGMENTS:
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
        for choice_data in LEVEL_3_CHOICES:
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

    logger.info("✅ Level 3 narrative seeding complete!")
    logger.info(f"   - {len(LEVEL_3_FRAGMENTS)} fragments")
    logger.info(f"   - {len(LEVEL_3_CHOICES)} choices")


async def main():
    """Main entry point."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )

    # Run seeding
    try:
        await seed_level_3()
    except Exception as e:
        logger.error(f"Seeding failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
