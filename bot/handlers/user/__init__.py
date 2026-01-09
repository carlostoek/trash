"""
User handlers module.
"""
# Importar routers
from bot.handlers.user.start import user_router
from bot.handlers.user.narrative import narrative_router

# Importar handlers adicionales para que sus decoradores se ejecuten
# IMPORTANTE: Estos imports ejecutan los decoradores @user_router.callback_query()
import bot.handlers.user.vip_flow
import bot.handlers.user.free_join_request

__all__ = ["user_router", "narrative_router"]
