"""
Migration script to add narrative models to the database.

This migration creates all 8 narrative tables:
1. story_fragments - Fragmentos de historia interactiva
2. story_choices - Opciones de decisión en fragmentos
3. user_narrative_progress - Progreso narrativo de usuarios
4. user_choices - Registro de decisiones tomadas
5. narrative_unlocks - Contenido desbloqueado por usuarios
6. narrative_flags - Flags narrativos persistentes
7. archetype_profiles - Perfiles de detección de personalidad
8. character_relationships - Relaciones con personajes (Lucien, Diana)

Usage:
    python -m migrations.add_narrative_models upgrade
    python -m migrations.add_narrative_models downgrade
"""
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text, inspect
from bot.database.engine import get_engine, get_session_factory
from bot.database.base import Base
from bot.database.models import (
    StoryFragment,
    StoryChoice,
    UserNarrativeProgress,
    UserChoice,
    NarrativeUnlock,
    NarrativeFlag,
    ArchetypeProfile,
    CharacterRelationship
)

logger = logging.getLogger(__name__)


# List of narrative models in dependency order
NARRATIVE_MODELS = [
    StoryFragment,
    StoryChoice,
    UserNarrativeProgress,
    UserChoice,
    NarrativeUnlock,
    NarrativeFlag,
    ArchetypeProfile,
    CharacterRelationship
]


def _get_existing_tables() -> set[str]:
    """
    Get set of existing table names in the database.

    Returns:
        Set of table names that already exist
    """
    engine = get_engine()
    inspector = inspect(engine)

    # For async engine, we need to run sync inspection
    import asyncio

    async def get_tables():
        async with engine.connect() as conn:
            # Use run_sync to run synchronous inspection
            def _get_tables_inspect(sync_conn):
                insp = inspect(sync_conn)
                return set(insp.get_table_names())

            return await conn.run_sync(_get_tables_inspect)

    return asyncio.run(get_tables())


async def upgrade() -> None:
    """
    Create all narrative tables in the database.

    This function:
    1. Checks which narrative tables already exist
    2. Creates only the missing tables
    3. Logs the results

    Safe to run multiple times - will skip existing tables.
    """
    from bot.database import get_session

    logger.info("🔧 Starting narrative models migration (upgrade)...")

    # Get existing tables
    existing_tables = _get_existing_tables()

    # Determine which tables need to be created
    tables_to_create = []
    for model in NARRATIVE_MODELS:
        if model.__tablename__ not in existing_tables:
            tables_to_create.append(model)
            logger.info(f"  ✓ Will create table: {model.__tablename__}")
        else:
            logger.info(f"  ⊙ Table already exists: {model.__tablename__}")

    if not tables_to_create:
        logger.info("✅ All narrative tables already exist. Nothing to do.")
        return

    # Create the tables
    engine = get_engine()

    async with engine.begin() as conn:
        for model in tables_to_create:
            try:
                # Create the table
                await conn.run_sync(
                    lambda sync_conn: model.__table__.create(sync_conn, checkfirst=True)
                )
                logger.info(f"  ✅ Created table: {model.__tablename__}")
            except Exception as e:
                logger.error(f"  ❌ Error creating table {model.__tablename__}: {e}")
                raise

    # Verify creation
    logger.info("🔍 Verifying table creation...")
    all_existing = _get_existing_tables()

    created_count = 0
    for model in NARRATIVE_MODELS:
        table_name = model.__tablename__
        if table_name in all_existing:
            created_count += 1
            logger.info(f"  ✓ Verified: {table_name}")
        else:
            logger.error(f"  ✗ Failed to create: {table_name}")

    logger.info(f"✅ Migration complete! {created_count}/{len(NARRATIVE_MODELS)} narrative tables exist.")


async def downgrade() -> None:
    """
    Drop all narrative tables from the database.

    WARNING: This will delete all narrative data!
    Use with caution in production environments.

    This function:
    1. Drops all narrative tables
    2. Logs the results

    Safe to run multiple times - will skip non-existent tables.
    """
    from bot.database import get_session

    logger.warning("⚠️  Starting narrative models migration (downgrade)...")
    logger.warning("⚠️  This will DELETE all narrative data!")

    # Get existing tables
    existing_tables = _get_existing_tables()

    # Determine which tables need to be dropped
    tables_to_drop = []
    for model in reversed(NARRATIVE_MODELS):  # Reverse order for FK constraints
        if model.__tablename__ in existing_tables:
            tables_to_drop.append(model)
            logger.info(f"  ✓ Will drop table: {model.__tablename__}")
        else:
            logger.info(f"  ⊙ Table doesn't exist: {model.__tablename__}")

    if not tables_to_drop:
        logger.info("✅ No narrative tables exist. Nothing to drop.")
        return

    # Drop the tables
    engine = get_engine()

    async with engine.begin() as conn:
        for model in tables_to_drop:
            try:
                # Drop the table
                await conn.run_sync(
                    lambda sync_conn: model.__table__.drop(sync_conn, checkfirst=True)
                )
                logger.info(f"  ✅ Dropped table: {model.__tablename__}")
            except Exception as e:
                logger.error(f"  ❌ Error dropping table {model.__tablename__}: {e}")
                raise

    # Verify deletion
    logger.info("🔍 Verifying table deletion...")
    all_existing = _get_existing_tables()

    dropped_count = 0
    for model in NARRATIVE_MODELS:
        table_name = model.__tablename__
        if table_name not in all_existing:
            dropped_count += 1
            logger.info(f"  ✓ Verified dropped: {table_name}")
        else:
            logger.error(f"  ✗ Failed to drop: {table_name}")

    logger.info(f"✅ Downgrade complete! {dropped_count}/{len(NARRATIVE_MODELS)} narrative tables dropped.")


async def verify_migration() -> dict[str, bool]:
    """
    Verify that all narrative tables exist and are properly structured.

    Returns:
        Dict mapping table names to bool (True if exists and valid)
    """
    from bot.database import get_session

    logger.info("🔍 Verifying narrative models migration...")

    engine = get_engine()
    existing_tables = _get_existing_tables()

    results = {}

    async with engine.begin() as conn:
        for model in NARRATIVE_MODELS:
            table_name = model.__tablename__

            if table_name not in existing_tables:
                results[table_name] = False
                logger.error(f"  ✗ Table missing: {table_name}")
                continue

            # Check table structure by querying column info
            def check_table_structure(sync_conn):
                insp = inspect(sync_conn)
                columns = insp.get_columns(table_name)

                # Check that table has columns
                if not columns:
                    return False

                # Log column count for verification
                logger.debug(f"  ✓ Table {table_name} has {len(columns)} columns")
                return True

            try:
                is_valid = await conn.run_sync(check_table_structure)
                results[table_name] = is_valid

                if is_valid:
                    logger.info(f"  ✅ Table verified: {table_name}")
                else:
                    logger.error(f"  ✗ Table invalid: {table_name}")

            except Exception as e:
                results[table_name] = False
                logger.error(f"  ✗ Error verifying table {table_name}: {e}")

    # Summary
    total = len(NARRATIVE_MODELS)
    valid = sum(1 for v in results.values() if v)

    logger.info(f"📊 Verification complete: {valid}/{total} tables valid")

    return results


async def main():
    """
    Main entry point for the migration script.

    Usage:
        python -m migrations.add_narrative_models upgrade
        python -m migrations.add_narrative_models downgrade
        python -m migrations.add_narrative_models verify
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Migration script for narrative models"
    )
    parser.add_argument(
        "command",
        choices=["upgrade", "downgrade", "verify"],
        help="Command to execute"
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )

    # Initialize database if not already initialized
    try:
        from bot.database import init_db
        await init_db()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)

    # Execute command
    try:
        if args.command == "upgrade":
            await upgrade()
        elif args.command == "downgrade":
            await downgrade()
        elif args.command == "verify":
            results = await verify_migration()

            # Exit with error code if any table is invalid
            if not all(results.values()):
                sys.exit(1)

    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
