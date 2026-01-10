"""
Servicios del módulo narrativo.

Este módulo implementa:
- NarrativeService: Gestión de fragmentos y progreso narrativo
- FlagService: Gestión de flags narrativos persistentes
- ArchetypeService: Detección de arquetipos de usuario
- StoryEngine: Coordinador de todos los servicios narrativos
"""
import logging
from datetime import datetime, timezone
from typing import Optional, List, Tuple, Dict

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot

from bot.database.models import (
    StoryFragment,
    StoryChoice,
    UserNarrativeProgress,
    UserChoice,
    NarrativeUnlock,
    NarrativeFlag,
    ArchetypeProfile,
    CharacterRelationship,
    User
)

logger = logging.getLogger(__name__)


# ==============================================================================
# FLAG SERVICE - Gestión de flags narrativos
# ==============================================================================

class FlagService:
    """
    Servicio de gestión de flags narrativos.

    Los flags son estados persistentes que afectan:
    - Disponibilidad de opciones futuras
    - Fragmentos desbloqueados
    - Diálogos adaptativos
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def set_flag(
        self,
        user_id: int,
        flag_key: str,
        flag_value: str = "true",
        expires_at: Optional[datetime] = None
    ) -> NarrativeFlag:
        """
        Establece un flag narrativo para un usuario.

        Args:
            user_id: ID del usuario
            flag_key: Clave del flag (ej: "met_diana")
            flag_value: Valor del flag (default: "true")
            expires_at: Opcional, cuándo expira el flag

        Returns:
            NarrativeFlag creado/actualizado
        """
        # Buscar si ya existe
        stmt = select(NarrativeFlag).where(
            and_(
                NarrativeFlag.user_id == user_id,
                NarrativeFlag.flag_key == flag_key
            )
        )
        result = await self.session.execute(stmt)
        flag = result.scalar_one_or_none()

        if flag:
            # Actualizar flag existente
            flag.flag_value = flag_value
            flag.expires_at = expires_at
        else:
            # Crear nuevo flag
            flag = NarrativeFlag(
                user_id=user_id,
                flag_key=flag_key,
                flag_value=flag_value,
                expires_at=expires_at
            )
            self.session.add(flag)

        await self.session.commit()
        await self.session.refresh(flag)

        logger.debug(f"Flag '{flag_key}' set to '{flag_value}' for user {user_id}")
        return flag

    async def get_flag(
        self,
        user_id: int,
        flag_key: str
    ) -> Optional[NarrativeFlag]:
        """
        Obtiene un flag narrativo.

        Args:
            user_id: ID del usuario
            flag_key: Clave del flag

        Returns:
            NarrativeFlag o None
        """
        stmt = select(NarrativeFlag).where(
            and_(
                NarrativeFlag.user_id == user_id,
                NarrativeFlag.flag_key == flag_key
            )
        )
        result = await self.session.execute(stmt)
        flag = result.scalar_one_or_none()

        # Verificar si el flag está activo (no expiró)
        if flag and not flag.is_active:
            # Flag expirado, eliminarlo
            await self.session.delete(flag)
            await self.session.commit()
            return None

        return flag

    async def has_flag(
        self,
        user_id: int,
        flag_key: str
    ) -> bool:
        """
        Verifica si un usuario tiene un flag activo.

        Args:
            user_id: ID del usuario
            flag_key: Clave del flag

        Returns:
            True si tiene el flag activo
        """
        flag = await self.get_flag(user_id, flag_key)
        return flag is not None

    async def clear_flag(
        self,
        user_id: int,
        flag_key: str
    ) -> bool:
        """
        Elimina un flag narrativo.

        Args:
            user_id: ID del usuario
            flag_key: Clave del flag

        Returns:
            True si se eliminó correctamente
        """
        stmt = select(NarrativeFlag).where(
            and_(
                NarrativeFlag.user_id == user_id,
                NarrativeFlag.flag_key == flag_key
            )
        )
        result = await self.session.execute(stmt)
        flag = result.scalar_one_or_none()

        if flag:
            await self.session.delete(flag)
            await self.session.commit()
            logger.debug(f"Flag '{flag_key}' cleared for user {user_id}")
            return True

        return False

    async def get_all_user_flags(
        self,
        user_id: int
    ) -> List[NarrativeFlag]:
        """
        Obtiene todos los flags activos de un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            Lista de NarrativeFlag activos
        """
        stmt = select(NarrativeFlag).where(
            NarrativeFlag.user_id == user_id
        )
        result = await self.session.execute(stmt)
        flags = result.scalars().all()

        # Filtrar flags expirados
        active_flags = [f for f in flags if f.is_active]

        return active_flags


# ==============================================================================
# ARCHETYPE SERVICE - Detección de personalidad
# ==============================================================================

class ArchetypeService:
    """
    Servicio de detección y gestión de arquetipos de usuario.

    6 Arquetipos principales:
    1. EXPLORER: Le gusta descubrir, explorar todas las opciones
    2. DIRECT: Tomado decisiones rápidas, va al grano
    3. ROMANTIC: Busca conexiones emocionales, opciones románticas
    4. ANALYTICAL: Piensa mucho, elige opciones lógicas
    5. PERSISTENT: No se rinde, reintenta caminos difíciles
    6. PATIENT: Toma su tiempo, lee todo antes de elegir
    """

    # Definición de arquetipos
    ARCHETYPES = {
        "EXPLORER": "Explorador - Le gusta descubrir todas las opciones",
        "DIRECT": "Directo - Va al grano, decisiones rápidas",
        "ROMANTIC": "Romántico - Busca conexiones emocionales",
        "ANALYTICAL": "Analítico - Piensa mucho, elige lógica",
        "PERSISTENT": "Persistente - No se rinde, reintenta",
        "PATIENT": "Paciente - Toma su tiempo, lee todo"
    }

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_archetype_profile(
        self,
        user_id: int
    ) -> ArchetypeProfile:
        """
        Obtiene o crea el perfil de arquetipo del usuario.

        Args:
            user_id: ID del usuario

        Returns:
            ArchetypeProfile
        """
        stmt = select(ArchetypeProfile).where(
            ArchetypeProfile.user_id == user_id
        )
        result = await self.session.execute(stmt)
        profile = result.scalar_one_or_none()

        if not profile:
            # Crear perfil con puntos iniciales
            profile = ArchetypeProfile(
                user_id=user_id,
                primary_archetype="EXPLORER",
                archetype_points={
                    "explorer": 0,
                    "direct": 0,
                    "romantic": 0,
                    "analytical": 0,
                    "persistent": 0,
                    "patient": 0
                },
                archetype_confidence=30  # Baja confianza inicialmente
            )
            self.session.add(profile)
            await self.session.commit()
            await self.session.refresh(profile)

            logger.info(f"Created archetype profile for user {user_id}")

        return profile

    async def add_archetype_points(
        self,
        user_id: int,
        points_dict: Dict[str, int]
    ) -> None:
        """
        Añade puntos de arquetipo a un usuario.

        Args:
            user_id: ID del usuario
            points_dict: Dict con puntos por arquetipo
                {"romantic": +2, "direct": -1}
        """
        profile = await self.get_or_create_archetype_profile(user_id)

        # Actualizar puntos
        for archetype, points in points_dict.items():
            archetype_lower = archetype.lower()
            if archetype_lower in profile.archetype_points:
                profile.archetype_points[archetype_lower] += points

        # Recalcular arquetipo primario
        await self._recalculate_archetype(profile)

        profile.last_analyzed_at = datetime.now(timezone.utc)
        await self.session.commit()

        logger.debug(
            f"Updated archetype points for user {user_id}: "
            f"{points_dict} -> Primary: {profile.primary_archetype}"
        )

    async def _recalculate_archetype(
        self,
        profile: ArchetypeProfile
    ) -> None:
        """
        Recalcula el arquetipo primario basado en puntos.

        Args:
            profile: ArchetypeProfile a recalcular
        """
        points = profile.archetype_points

        # Encontrar arquetipo con mayor puntaje
        max_points = 0
        primary = profile.primary_archetype

        for archetype, pts in points.items():
            if pts > max_points:
                max_points = pts
                primary = archetype.upper()

        # Calcular confianza basada en diferencia con segundo lugar
        sorted_archetypes = sorted(
            points.items(),
            key=lambda x: x[1],
            reverse=True
        )

        if len(sorted_archetypes) >= 2:
            first_place = sorted_archetypes[0][1]
            second_place = sorted_archetypes[1][1]
            confidence = min(100, (first_place - second_place) * 5 + 50)
        else:
            confidence = 100

        profile.primary_archetype = primary
        profile.archetype_confidence = confidence

        # Buscar arquetipo secundario
        if len(sorted_archetypes) >= 2:
            secondary = sorted_archetypes[1][0].upper()
            if sorted_archetypes[1][1] > 0:
                profile.secondary_archetype = secondary
            else:
                profile.secondary_archetype = None
        else:
            profile.secondary_archetype = None

    async def record_choice_timing(
        self,
        user_id: int,
        choice_time_seconds: int
    ) -> None:
        """
        Registra el tiempo que tomó un usuario en elegir.

        Usado para detectar arquetipos:
        - Rápido (< 10s) → Direct
        - Medio (10-30s) → Normal
        - Lento (> 30s) → Patient/Analytical

        Args:
            user_id: ID del usuario
            choice_time_seconds: Tiempo en segundos
        """
        profile = await self.get_or_create_archetype_profile(user_id)

        # Actualizar promedio móvil
        current_avg = profile.average_choice_time_seconds
        total_analyzed = profile.total_choices_analyzed

        if total_analyzed > 0:
            new_avg = (
                (current_avg * total_analyzed + choice_time_seconds) /
                (total_analyzed + 1)
            )
        else:
            new_avg = choice_time_seconds

        profile.average_choice_time_seconds = int(new_avg)
        profile.total_choices_analyzed += 1

        # Añadir puntos basado en tiempo
        if choice_time_seconds < 10:
            # Decisión rápida → Direct
            await self.add_archetype_points(user_id, {"direct": +1})
        elif choice_time_seconds > 30:
            # Decisión lenta → Patient
            await self.add_archetype_points(user_id, {"patient": +1})

        await self.session.commit()

    async def record_fragment_reread(
        self,
        user_id: int
    ) -> None:
        """
        Registra que un usuario releyó un fragmento.

        Indica: Explorer (leer todo) o Analytical (analizar detalles)

        Args:
            user_id: ID del usuario
        """
        profile = await self.get_or_create_archetype_profile(user_id)
        profile.reread_fragments_count += 1

        # Añadir puntos de Explorer/Analytical
        await self.add_archetype_points(user_id, {
            "explorer": +1,
            "analytical": +1
        })

        await self.session.commit()


# ==============================================================================
# CHARACTER RELATIONSHIP SERVICE - Gestión de relaciones
# ==============================================================================

class CharacterRelationshipService:
    """
    Servicio de gestión de relaciones con personajes (Lucien, Diana).
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_relationship(
        self,
        user_id: int,
        character_name: str
    ) -> Optional[CharacterRelationship]:
        """
        Obtiene el estado de relación con un personaje.

        Args:
            user_id: ID del usuario
            character_name: Nombre del personaje ("LUCIEN", "DIANA")

        Returns:
            CharacterRelationship o None
        """
        stmt = select(CharacterRelationship).where(
            and_(
                CharacterRelationship.user_id == user_id,
                CharacterRelationship.character_name == character_name.upper()
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create_relationship(
        self,
        user_id: int,
        character_name: str
    ) -> CharacterRelationship:
        """
        Obtiene o crea una relación con un personaje.

        Args:
            user_id: ID del usuario
            character_name: Nombre del personaje

        Returns:
            CharacterRelationship
        """
        relationship = await self.get_relationship(user_id, character_name)

        if not relationship:
            relationship = CharacterRelationship(
                user_id=user_id,
                character_name=character_name.upper(),
                relationship_score=0,
                first_met_at=datetime.now(timezone.utc),
                interaction_count=1,
                last_interaction_at=datetime.now(timezone.utc)
            )
            self.session.add(relationship)
            await self.session.commit()
            await self.session.refresh(relationship)

            logger.info(f"Created relationship for user {user_id} with {character_name}")

        return relationship

    async def update_relationship_score(
        self,
        user_id: int,
        character_name: str,
        score_change: int
    ) -> CharacterRelationship:
        """
        Actualiza el puntaje de relación con un personaje.

        Args:
            user_id: ID del usuario
            character_name: Nombre del personaje ("LUCIEN", "DIANA")
            score_change: Cambio en el puntaje (positivo o negativo)

        Returns:
            CharacterRelationship actualizado
        """
        relationship = await self.get_or_create_relationship(user_id, character_name)

        # Actualizar score
        relationship.relationship_score += score_change
        relationship.last_interaction_at = datetime.now(timezone.utc)
        relationship.interaction_count += 1

        # Limitar score a rango -100 a +100
        relationship.relationship_score = max(-100, min(100, relationship.relationship_score))

        # Actualizar hitos
        if relationship.relationship_score >= 60 and not relationship.became_romantic_at:
            relationship.became_romantic_at = datetime.now(timezone.utc)
        if relationship.relationship_score >= 40 and not relationship.became_close_friend_at:
            relationship.became_close_friend_at = datetime.now(timezone.utc)

        await self.session.commit()
        await self.session.refresh(relationship)

        logger.debug(
            f"Updated relationship for user {user_id} with {character_name}: "
            f"score={relationship.relationship_score} ({relationship.relationship_status})"
        )

        return relationship


# ==============================================================================
# NARRATIVE SERVICE - Servicio core de narrativa
# ==============================================================================

class NarrativeService:
    """
    Servicio central de gestión narrativa.

    Responsabilidades:
    - Gestión de fragmentos de historia
    - Progresión del usuario
    - Desbloqueo de contenido
    - Integración con gamificación
    """

    def __init__(self, session: AsyncSession, bot: Bot):
        self.session = session
        self.bot = bot
        self.flags = FlagService(session)
        self.archetype = ArchetypeService(session)
        self.relationships = CharacterRelationshipService(session)

    # ========================================
    # FRAGMENT MANAGEMENT
    # ========================================

    async def get_starting_fragment(
        self,
        narrative_level: int = 1
    ) -> Optional[StoryFragment]:
        """
        Obtiene el fragmento inicial de un nivel narrativo.

        Args:
            narrative_level: Nivel de narrativa (1-6)

        Returns:
            StoryFragment inicial o None si no existe
        """
        stmt = select(StoryFragment).where(
            and_(
                StoryFragment.narrative_level == narrative_level,
                StoryFragment.is_starting_fragment == True,
                StoryFragment.active == True
            )
        ).order_by(StoryFragment.sort_order)
        result = await self.session.execute(stmt)
        # Use first() for robustness - if multiple starting fragments exist, take first by sort_order
        return result.scalars().first()

    async def get_fragment(
        self,
        fragment_id: str
    ) -> Optional[StoryFragment]:
        """
        Obtiene un fragmento por ID.

        Args:
            fragment_id: ID del fragmento (ej: "L1_INTRO_001")

        Returns:
            StoryFragment o None
        """
        stmt = select(StoryFragment).where(
            and_(
                StoryFragment.fragment_id == fragment_id,
                StoryFragment.active == True
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_fragment_choices(
        self,
        fragment_id: int,
        user_id: int,
        user_flags: List[str]
    ) -> List[StoryChoice]:
        """
        Obtiene las opciones disponibles para un usuario en un fragmento.

        Filtra opciones basado en:
        - Opciones activas
        - Requisitos de flags

        Args:
            fragment_id: ID del fragmento
            user_id: ID del usuario
            user_flags: Lista de flags activos del usuario

        Returns:
            Lista de StoryChoice disponibles (ordenadas por sort_order)
        """
        # Obtener todas las opciones del fragmento
        stmt = select(StoryChoice).where(
            and_(
                StoryChoice.fragment_id == fragment_id,
                StoryChoice.active == True
            )
        ).order_by(StoryChoice.sort_order)

        result = await self.session.execute(stmt)
        all_choices = result.scalars().all()

        # Filtrar por requisitos
        available_choices = []
        for choice in all_choices:
            if choice.display_requirements:
                requirements = choice.display_requirements

                # Verificar flags requeridos
                required_flags = requirements.get("required_flags", [])
                if not all(flag in user_flags for flag in required_flags):
                    continue

            available_choices.append(choice)

        return available_choices

    # ========================================
    # USER PROGRESSION
    # ========================================

    async def get_or_create_user_progress(
        self,
        user_id: int
    ) -> UserNarrativeProgress:
        """
        Obtiene o crea el progreso narrativo del usuario.

        Args:
            user_id: ID del usuario

        Returns:
            UserNarrativeProgress
        """
        stmt = select(UserNarrativeProgress).where(
            UserNarrativeProgress.user_id == user_id
        )
        result = await self.session.execute(stmt)
        progress = result.scalar_one_or_none()

        if not progress:
            # Crear progreso inicial
            starting_fragment = await self.get_starting_fragment(narrative_level=1)

            progress = UserNarrativeProgress(
                user_id=user_id,
                current_fragment_id=starting_fragment.id if starting_fragment else None,
                current_narrative_level=1,
                max_narrative_level_reached=1
            )
            self.session.add(progress)
            await self.session.commit()
            await self.session.refresh(progress)

            logger.info(f"Created narrative progress for user {user_id}")

        return progress

    async def advance_to_next_fragment(
        self,
        user_id: int,
        choice_id: str,
        choice_time_seconds: int = 0
    ) -> Tuple[bool, str, Optional[StoryFragment], Dict]:
        """
        Avanza la historia del usuario basado en su elección.

        Flujo completo:
        1. Validar que la elección existe y está disponible
        2. Registrar la elección del usuario
        3. Aplicar consecuencias (flags, items, arquetipo)
        4. Actualizar progreso narrativo
        5. Obtener el siguiente fragmento
        6. Retornar siguiente fragmento + detalles

        Args:
            user_id: ID del usuario
            choice_id: ID de la elección (ej: "L1_INTRO_A")
            choice_time_seconds: Tiempo que tomó el usuario en elegir (para arquetipo)

        Returns:
            Tuple (success, message, next_fragment, details)
            - success: True si avanzó exitosamente
            - message: Mensaje descriptivo
            - next_fragment: Siguiente fragmento o None
            - details: Dict con consecuencias aplicadas
        """
        # 1. Obtener la elección
        choice_stmt = select(StoryChoice).where(
            StoryChoice.choice_id == choice_id
        )
        choice_result = await self.session.execute(choice_stmt)
        choice = choice_result.scalar_one_or_none()

        if not choice:
            return False, "Opción no válida", None, {}

        # 2. Obtener progreso del usuario
        progress = await self.get_or_create_user_progress(user_id)

        # 3. Registrar la elección
        user_choice = UserChoice(
            user_id=user_id,
            choice_id=choice_id,
            fragment_id=choice.fragment_id,
            choice_time_seconds=choice_time_seconds,
            made_at=datetime.now(timezone.utc),
            user_level_at_choice=progress.current_narrative_level
        )
        self.session.add(user_choice)

        # 4. Aplicar consecuencias
        consequences_applied = {}
        if choice.consequences:
            # Establecer flags
            flags_set = choice.consequences.get("flags_set", [])
            flags_unset = choice.consequences.get("flags_unset", [])

            for flag in flags_set:
                await self.flags.set_flag(user_id, flag)

            for flag in flags_unset:
                await self.flags.clear_flag(user_id, flag)

            consequences_applied["flags_set"] = flags_set
            consequences_applied["flags_unset"] = flags_unset

            # Actualizar puntos de arquetipo
            archetype_points = choice.consequences.get("archetype_points", {})
            if archetype_points:
                await self.archetype.add_archetype_points(user_id, archetype_points)
                consequences_applied["archetype_points"] = archetype_points

            # Actualizar relaciones con personajes
            relationship_changes = choice.consequences.get("relationship_change", {})
            if relationship_changes:
                for character, change in relationship_changes.items():
                    await self.relationships.update_relationship_score(
                        user_id=user_id,
                        character_name=character.upper(),
                        score_change=change
                    )
                consequences_applied["relationship_changes"] = relationship_changes

        user_choice.consequences_applied = consequences_applied

        # 5. Actualizar progreso
        progress.current_fragment_id = choice.target_fragment_id
        progress.total_choices_made += 1
        progress.last_played_at = datetime.now(timezone.utc)

        # Marcar fragmento actual como completado
        if choice.fragment_id not in progress.fragments_completed:
            progress.fragments_completed.append(choice.fragment_id)

        # 6. Obtener siguiente fragmento
        next_fragment_stmt = select(StoryFragment).where(
            StoryFragment.id == choice.target_fragment_id
        )
        next_fragment_result = await self.session.execute(next_fragment_stmt)
        next_fragment = next_fragment_result.scalar_one_or_none()

        if not next_fragment:
            await self.session.commit()
            return False, "Error: Fragmento destino no encontrado", None, consequences_applied

        # Actualizar nivel narrativo si avanzó
        if next_fragment.narrative_level > progress.max_narrative_level_reached:
            progress.max_narrative_level_reached = next_fragment.narrative_level

        progress.current_narrative_level = next_fragment.narrative_level

        # Marcar nivel como completado si es ending fragment
        if next_fragment.is_ending_fragment:
            if next_fragment.narrative_level not in progress.levels_completed:
                progress.levels_completed.append(next_fragment.narrative_level)

            # Guardar timestamp de completitud
            if next_fragment.narrative_level == 1:
                progress.completed_level_1_at = datetime.now(timezone.utc)
            elif next_fragment.narrative_level == 3:
                progress.completed_level_3_at = datetime.now(timezone.utc)
            elif next_fragment.narrative_level == 6:
                progress.completed_level_6_at = datetime.now(timezone.utc)

        # Commit de toda la transacción
        await self.session.commit()

        logger.info(
            f"User {user_id} advanced to fragment {next_fragment.fragment_id} "
            f"(Level {next_fragment.narrative_level})"
        )

        message = f"✨ {next_fragment.title}"
        if consequences_applied.get("flags_set"):
            message += f"\n🎯 Nueva información descubierta"

        return True, message, next_fragment, consequences_applied

    async def can_access_fragment(
        self,
        user_id: int,
        fragment: StoryFragment,
        user_flags: List[str]
    ) -> Tuple[bool, str]:
        """
        Verifica si un usuario puede acceder a un fragmento.

        Args:
            user_id: ID del usuario
            fragment: StoryFragment a verificar
            user_flags: Lista de flags activos del usuario

        Returns:
            Tuple (can_access, reason)
            - can_access: True si puede acceder
            - reason: Mensaje explicativo si no puede acceder
        """
        # 1. Verificar nivel VIP
        if fragment.narrative_level >= 4:
            from bot.services.subscription import SubscriptionService
            subscription_service = SubscriptionService(self.session, self.bot)
            is_vip = await subscription_service.is_vip_active(user_id)

            if not is_vip:
                return False, f"🔒 Este contenido requiere suscripción VIP (Nivel {fragment.narrative_level})"

        # 2. Verificar condiciones de desbloqueo
        if fragment.unlock_conditions:
            conditions = fragment.unlock_conditions

            # Verificar elecciones requeridas
            required_choices = conditions.get("required_choices", [])
            if required_choices:
                # Verificar si el usuario ha tomado estas elecciones
                user_choices_stmt = select(UserChoice.choice_id).where(
                    and_(
                        UserChoice.user_id == user_id,
                        UserChoice.choice_id.in_(required_choices)
                    )
                )
                result = await self.session.execute(user_choices_stmt)
                choices_made = [row[0] for row in result.all()]

                if not all(choice in choices_made for choice in required_choices):
                    return False, "🔒 Debes tomar ciertas decisiones previas para desbloquear esto"

            # Verificar flags requeridos
            required_flags = conditions.get("required_flags", [])
            if required_flags:
                for flag in required_flags:
                    if not await self.flags.has_flag(user_id, flag):
                        return False, f"🔒 Necesitas descubrir algo más primero"

        return True, ""


# ==============================================================================
# STORY ENGINE - Motor coordinador narrativo
# ==============================================================================

class StoryEngine:
    """
    Motor principal de la historia.

    Coordina todos los servicios narrativos para proporcionar
    una experiencia de historia coherente y personalizada.
    """

    def __init__(self, session: AsyncSession, bot: Bot):
        self.session = session
        self.bot = bot

        # Inicializar sub-servicios
        self.narrative = NarrativeService(session, bot)
        self.flags = self.narrative.flags
        self.archetype = self.narrative.archetype
        self.relationships = self.narrative.relationships

    async def get_current_story_state(
        self,
        user_id: int
    ) -> Dict:
        """
        Obtiene el estado completo de la historia del usuario.

        Args:
            user_id: ID del usuario

        Returns:
            Dict con estado completo de la historia
        """
        # 1. Obtener progreso del usuario
        progress = await self.narrative.get_or_create_user_progress(user_id)

        # 2. Obtener fragmento actual
        current_fragment = None
        if progress.current_fragment_id:
            stmt = select(StoryFragment).where(
                StoryFragment.id == progress.current_fragment_id
            )
            result = await self.session.execute(stmt)
            current_fragment = result.scalar_one_or_none()

        # Si no hay fragmento actual, iniciar desde el principio
        if not current_fragment:
            current_fragment = await self.narrative.get_starting_fragment(
                narrative_level=1
            )
            if not current_fragment:
                return {
                    "error": "No hay fragmentos disponibles"
                }

            progress.current_fragment_id = current_fragment.id
            await self.session.commit()

        # 3. Obtener flags del usuario
        user_flags = await self.flags.get_all_user_flags(user_id)
        flag_keys = [f.flag_key for f in user_flags]

        # 4. Verificar acceso al fragmento
        can_access, unlock_message = await self.narrative.can_access_fragment(
            user_id=user_id,
            fragment=current_fragment,
            user_flags=flag_keys
        )

        if not can_access:
            return {
                "current_fragment": current_fragment,
                "can_continue": False,
                "unlock_message": unlock_message,
                "user_progress": progress
            }

        # 5. Obtener opciones disponibles
        available_choices = await self.narrative.get_fragment_choices(
            fragment_id=current_fragment.id,
            user_id=user_id,
            user_flags=flag_keys
        )

        # 6. Obtener perfil de arquetipo
        archetype_profile = await self.archetype.get_or_create_archetype_profile(user_id)

        # 7. Obtener relaciones con personajes
        lucien_rel = await self.relationships.get_relationship(user_id, "LUCIEN")
        diana_rel = await self.relationships.get_relationship(user_id, "DIANA")

        return {
            "current_fragment": current_fragment,
            "available_choices": available_choices,
            "user_progress": progress,
            "user_flags": flag_keys,
            "archetype": archetype_profile,
            "relationships": {
                "LUCIEN": lucien_rel,
                "DIANA": diana_rel
            },
            "can_continue": True,
            "unlock_message": ""
        }

    async def make_choice(
        self,
        user_id: int,
        choice_id: str,
        choice_time_seconds: int
    ) -> Dict:
        """
        Procesa una elección del usuario.

        Args:
            user_id: ID del usuario
            choice_id: ID de la elección
            choice_time_seconds: Tiempo que tomó en elegir

        Returns:
            Dict con resultado de la elección
        """
        # 1. Registrar tiempo de elección para arquetipo
        await self.archetype.record_choice_timing(user_id, choice_time_seconds)

        # 2. Avanzar historia
        success, message, next_fragment, consequences = await self.narrative.advance_to_next_fragment(
            user_id=user_id,
            choice_id=choice_id,
            choice_time_seconds=choice_time_seconds
        )

        if not success:
            return {
                "success": False,
                "message": message
            }

        # 3. Obtener siguiente estado
        next_state = await self.get_current_story_state(user_id)

        return {
            "success": True,
            "message": message,
            "next_fragment": next_fragment,
            "consequences": consequences,
            "next_state": next_state
        }
