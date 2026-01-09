"""
Seeds module - Contenido narrativo inicial.
"""
from bot.seeds.level_1_content import LEVEL_1_CHAPTERS, LEVEL_1_SCENES, LEVEL_1_DIALOGUES
from bot.seeds.level_2_content import LEVEL_2_CHAPTERS, LEVEL_2_SCENES, LEVEL_2_DIALOGUES
from bot.seeds.seed_runner import seed_narrative_content, clear_narrative_content

__all__ = [
    "LEVEL_1_CHAPTERS",
    "LEVEL_1_SCENES",
    "LEVEL_1_DIALOGUES",
    "LEVEL_2_CHAPTERS",
    "LEVEL_2_SCENES",
    "LEVEL_2_DIALOGUES",
    "seed_narrative_content",
    "clear_narrative_content",
]
