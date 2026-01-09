"""
Seed Runner - Carga contenido narrativo en la base de datos.

Uso:
    python -m bot.seeds.seed_runner

O desde codigo:
    from bot.seeds import seed_narrative_content
    await seed_narrative_content()
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional

from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.engine import init_db, close_db, get_session, get_engine
from bot.database.base import Base
from bot.database.scene_models import (
    NarrativeChapter,
    NarrativeScene,
    SceneDialogue,
    DialogueOption
)
from bot.database.enums import ArchetypeType

logger = logging.getLogger(__name__)


async def recreate_narrative_tables() -> None:
    """
    Elimina y recrea las tablas de escenas narrativas.

    Usar cuando el esquema de las tablas cambia.
    """
    engine = get_engine()

    # Tablas a recrear (en orden inverso por FK)
    tables_to_recreate = [
        DialogueOption.__table__,
        SceneDialogue.__table__,
        NarrativeScene.__table__,
        NarrativeChapter.__table__,
    ]

    async with engine.begin() as conn:
        # Eliminar tablas existentes
        for table in tables_to_recreate:
            try:
                await conn.execute(text(f"DROP TABLE IF EXISTS {table.name}"))
                logger.info(f"Tabla {table.name} eliminada")
            except Exception as e:
                logger.warning(f"Error eliminando tabla {table.name}: {e}")

        # Recrear tablas
        for table in reversed(tables_to_recreate):
            await conn.run_sync(lambda sync_conn: table.create(sync_conn, checkfirst=True))
            logger.info(f"Tabla {table.name} creada")

    logger.info("Tablas narrativas recreadas correctamente")


async def seed_narrative_content(
    clear_existing: bool = True,
    levels: Optional[List[int]] = None
) -> Dict[str, int]:
    """
    Carga contenido narrativo en la base de datos.

    Args:
        clear_existing: Si True, elimina contenido existente primero
        levels: Lista de niveles a cargar (default: [1, 2])

    Returns:
        Dict con conteo de elementos creados
    """
    from bot.seeds.level_1_content import (
        LEVEL_1_CHAPTERS, LEVEL_1_SCENES,
        LEVEL_1_DIALOGUES, LEVEL_1_OPTIONS
    )
    from bot.seeds.level_2_content import (
        LEVEL_2_CHAPTERS, LEVEL_2_SCENES,
        LEVEL_2_DIALOGUES, LEVEL_2_OPTIONS
    )

    if levels is None:
        levels = [1, 2]

    stats = {
        "chapters": 0,
        "scenes": 0,
        "dialogues": 0,
        "options": 0
    }

    async with get_session() as session:
        if clear_existing:
            await clear_narrative_content(session)

        # Cargar Level 1
        if 1 in levels:
            l1_stats = await _seed_level_content(
                session,
                LEVEL_1_CHAPTERS,
                LEVEL_1_SCENES,
                LEVEL_1_DIALOGUES,
                LEVEL_1_OPTIONS
            )
            for key in stats:
                stats[key] += l1_stats[key]

        # Cargar Level 2
        if 2 in levels:
            l2_stats = await _seed_level_content(
                session,
                LEVEL_2_CHAPTERS,
                LEVEL_2_SCENES,
                LEVEL_2_DIALOGUES,
                LEVEL_2_OPTIONS
            )
            for key in stats:
                stats[key] += l2_stats[key]

        await session.commit()

    logger.info(
        f"Contenido narrativo cargado: "
        f"{stats['chapters']} chapters, "
        f"{stats['scenes']} scenes, "
        f"{stats['dialogues']} dialogues, "
        f"{stats['options']} options"
    )

    return stats


async def _seed_level_content(
    session: AsyncSession,
    chapters: List[Dict],
    scenes: List[Dict],
    dialogues: List[Dict],
    options: List[Dict]
) -> Dict[str, int]:
    """Carga contenido de un nivel especifico."""
    stats = {
        "chapters": 0,
        "scenes": 0,
        "dialogues": 0,
        "options": 0
    }

    # 1. Crear chapters
    for chapter_data in chapters:
        chapter = NarrativeChapter(**chapter_data)
        session.add(chapter)
        stats["chapters"] += 1

    await session.flush()

    # 2. Crear scenes
    for scene_data in scenes:
        scene = NarrativeScene(**scene_data)
        session.add(scene)
        stats["scenes"] += 1

    await session.flush()

    # 3. Crear dialogues
    for dialogue_data in dialogues:
        dialogue = SceneDialogue(**dialogue_data)
        session.add(dialogue)
        stats["dialogues"] += 1

    await session.flush()

    # 4. Crear options
    for option_data in options:
        # Convertir archetype string a enum
        if "associated_archetype" in option_data and option_data["associated_archetype"]:
            archetype_str = option_data["associated_archetype"]
            if isinstance(archetype_str, str):
                option_data["associated_archetype"] = ArchetypeType(archetype_str)

        option = DialogueOption(**option_data)
        session.add(option)
        stats["options"] += 1

    await session.flush()

    return stats


async def clear_narrative_content(session: Optional[AsyncSession] = None) -> None:
    """
    Elimina todo el contenido narrativo de la base de datos.

    Args:
        session: Sesion existente o None para crear una nueva
    """
    own_session = session is None

    if own_session:
        async with get_session() as session:
            await _do_clear(session)
            await session.commit()
    else:
        await _do_clear(session)


async def _do_clear(session: AsyncSession) -> None:
    """Ejecuta el borrado de contenido."""
    # Orden inverso por FK constraints
    await session.execute(delete(DialogueOption))
    await session.execute(delete(SceneDialogue))
    await session.execute(delete(NarrativeScene))
    await session.execute(delete(NarrativeChapter))
    logger.info("Contenido narrativo eliminado")


async def verify_content() -> Dict[str, int]:
    """
    Verifica el contenido cargado en la base de datos.

    Returns:
        Dict con conteo de elementos por tipo
    """
    from sqlalchemy import func

    async with get_session() as session:
        chapters = await session.execute(
            select(func.count(NarrativeChapter.id))
        )
        scenes = await session.execute(
            select(func.count(NarrativeScene.id))
        )
        dialogues = await session.execute(
            select(func.count(SceneDialogue.id))
        )
        options = await session.execute(
            select(func.count(DialogueOption.id))
        )

        return {
            "chapters": chapters.scalar(),
            "scenes": scenes.scalar(),
            "dialogues": dialogues.scalar(),
            "options": options.scalar()
        }


async def get_scene_preview(scene_id: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene una vista previa de una escena con sus dialogos.

    Args:
        scene_id: ID de la escena

    Returns:
        Dict con datos de la escena o None si no existe
    """
    async with get_session() as session:
        result = await session.execute(
            select(NarrativeScene)
            .where(NarrativeScene.scene_id == scene_id)
        )
        scene = result.scalar_one_or_none()

        if scene is None:
            return None

        # Obtener dialogos
        dialogues_result = await session.execute(
            select(SceneDialogue)
            .where(SceneDialogue.scene_id == scene_id)
            .order_by(SceneDialogue.sequence_order)
        )
        dialogues = dialogues_result.scalars().all()

        # Obtener opciones para cada dialogo
        dialogue_previews = []
        for d in dialogues:
            options_result = await session.execute(
                select(DialogueOption)
                .where(DialogueOption.dialogue_id == d.dialogue_id)
                .order_by(DialogueOption.display_order)
            )
            options = options_result.scalars().all()

            dialogue_previews.append({
                "id": d.dialogue_id,
                "character": d.character,
                "text": d.base_text[:100] + "..." if len(d.base_text) > 100 else d.base_text,
                "has_variants": bool(d.archetype_variants),
                "requires_response": d.requires_response,
                "options": [
                    {"id": o.option_id, "text": o.text[:50] + "..." if len(o.text) > 50 else o.text}
                    for o in options
                ]
            })

        return {
            "scene_id": scene.scene_id,
            "title": scene.title,
            "character": scene.primary_character,
            "dialogues": dialogue_previews
        }


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

async def main():
    """CLI entry point."""
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    print("=" * 60)
    print("NARRATIVE CONTENT SEED RUNNER")
    print("=" * 60)

    # Verificar argumentos
    clear = "--no-clear" not in sys.argv
    verify_only = "--verify" in sys.argv
    recreate_tables = "--recreate-tables" in sys.argv

    try:
        await init_db()

        # Recrear tablas si se solicita o si hay error de esquema
        if recreate_tables:
            print("\nRecreando tablas narrativas...")
            await recreate_narrative_tables()

        if verify_only:
            print("\nVerificando contenido existente...")
            stats = await verify_content()
            print(f"\nContenido actual:")
            print(f"  - Chapters:  {stats['chapters']}")
            print(f"  - Scenes:    {stats['scenes']}")
            print(f"  - Dialogues: {stats['dialogues']}")
            print(f"  - Options:   {stats['options']}")
        else:
            try:
                print(f"\nCargando contenido (clear_existing={clear})...")
                stats = await seed_narrative_content(clear_existing=clear)
            except Exception as e:
                if "no column named" in str(e) or "no such column" in str(e):
                    print("\nEsquema de tablas desactualizado. Recreando tablas...")
                    await recreate_narrative_tables()
                    print("\nReintentando carga de contenido...")
                    stats = await seed_narrative_content(clear_existing=clear)
                else:
                    raise

            print(f"\nContenido cargado:")
            print(f"  - Chapters:  {stats['chapters']}")
            print(f"  - Scenes:    {stats['scenes']}")
            print(f"  - Dialogues: {stats['dialogues']}")
            print(f"  - Options:   {stats['options']}")

            # Vista previa
            print("\n" + "-" * 60)
            print("VISTA PREVIA - Escena L1_S1_llegada:")
            print("-" * 60)
            preview = await get_scene_preview("L1_S1_llegada")
            if preview:
                print(f"Titulo: {preview['title']}")
                print(f"Personaje: {preview['character']}")
                print(f"Dialogos: {len(preview['dialogues'])}")
                for d in preview['dialogues']:
                    print(f"  [{d['character']}] {d['text']}")
                    if d['options']:
                        for o in d['options']:
                            print(f"    -> {o['text']}")

        print("\n" + "=" * 60)
        print("COMPLETADO")
        print("=" * 60)

    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
