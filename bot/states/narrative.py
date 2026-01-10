"""
FSM States para handlers narrativos.

Estados para flujos de narrativa interactiva (historia, elecciones, exploración).
"""
from aiogram.fsm.state import State, StatesGroup


class NarrativeUserStates(StatesGroup):
    """
    Estados para interacciones narrativas del usuario.

    Flujo:
    1. Usuario envía /story
    2. Bot muestra fragmento actual con opciones
    3. Usuario elige opción o releé fragmento
    4. Bot procesa elección y muestra siguiente fragmento
    5. Repetir hasta final del nivel

    Estados:
    - reading_fragment: Usuario leyendo fragmento actual
    - making_choice: Usuario eligiendo opción (tracking de tiempo)

    Features:
    - Tracking de tiempo de elección para detección de arquetipo
    - Soporte para releer fragmentos (Explorer/Analytical detection)
    - Manejo de contenido bloqueado (VIP required)
    """

    # Usuario leyendo fragmento actual
    reading_fragment = State()

    # Usuario eligiendo opción (para tracking de tiempo)
    making_choice = State()
