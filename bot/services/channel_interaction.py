"""
Channel Interaction Service - Sistema de Observación (Level 2).

Este servicio maneja el tracking de interacciones de usuarios en canales
para el sistema de observación de Level 2.

Funcionalidades:
- Registro de visualizaciones de posts
- Tracking de tiempo dedicado en el canal
- Registro de reacciones y comentarios
- Sistema de pistas (clues)
- Cálculo de score de observación
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Tuple

from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import ChannelInteraction, User


logger = logging.getLogger(__name__)


class ChannelInteractionService:
    """
    Servicio para tracking de interacciones en canales.

    El sistema de observación (Level 2) utiliza este servicio para:
    1. Rastrear qué posts ve el usuario
    2. Medir tiempo dedicado a cada post
    3. Detectar pistas descubiertas en el contenido
    4. Calcular score de observación total

    Scoring:
    - View: +1 punto
    - Time > 30s: +2 puntos adicionales
    - Reacción: +2 puntos
    - Pista descubierta: +5 puntos

    Thresholds:
    - 3+ pistas: Success (L2_SUCCESS_003)
    - 1-2 pistas: Partial (L2_PARTIAL_004)
    - 0 pistas o timeout: Failed (L2_TIMEOUT_005)
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializar el servicio.

        Args:
            session: Sesión de base de datos async
        """
        self.session = session

    async def track_post_view(
        self,
        user_id: int,
        post_id: int,
        channel_id: int,
        time_spent_seconds: int = 0,
        fragment_id_ref: Optional[str] = None
    ) -> Tuple[bool, str, ChannelInteraction]:
        """
        Registrar que un usuario vio un post.

        Args:
            user_id: ID del usuario
            post_id: ID del mensaje en Telegram
            channel_id: ID del canal
            time_spent_seconds: Tiempo dedicado al post (segundos)
            fragment_id_ref: Referencia a fragmento narrativo (opcional)

        Returns:
            Tuple (success, message, interaction)
        """
        try:
            # Verificar si ya existe interacción previa con este post
            existing = await self.session.execute(
                select(ChannelInteraction).where(
                    and_(
                        ChannelInteraction.user_id == user_id,
                        ChannelInteraction.post_id == post_id,
                        ChannelInteraction.channel_id == channel_id
                    )
                )
            )
            existing_interaction = existing.scalars().first()

            if existing_interaction:
                # Actualizar tiempo si es mayor
                if time_spent_seconds > existing_interaction.time_spent_seconds:
                    existing_interaction.time_spent_seconds = time_spent_seconds

                    # Recalcular score
                    base_score = 1  # View
                    if time_spent_seconds > 30:
                        base_score += 2  # Time bonus
                    existing_interaction.observation_score = base_score

                    await self.session.commit()
                    logger.info(f"Updated view time for user {user_id}, post {post_id}: {time_spent_seconds}s")

                return True, "View time updated", existing_interaction

            # Calcular score inicial
            score = 1  # View base
            if time_spent_seconds > 30:
                score += 2  # Time bonus

            # Crear nueva interacción
            interaction = ChannelInteraction(
                user_id=user_id,
                post_id=post_id,
                channel_id=channel_id,
                interaction_type="view",
                interaction_timestamp=datetime.now(timezone.utc),
                time_spent_seconds=time_spent_seconds,
                observation_score=score,
                fragment_id_ref=fragment_id_ref
            )

            self.session.add(interaction)
            await self.session.commit()

            logger.info(f"Tracked view for user {user_id}, post {post_id}, score: {score}")

            return True, "View tracked successfully", interaction

        except Exception as e:
            logger.error(f"Error tracking post view: {e}")
            await self.session.rollback()
            return False, f"Error: {str(e)}", None

    async def track_reaction(
        self,
        user_id: int,
        post_id: int,
        channel_id: int,
        fragment_id_ref: Optional[str] = None
    ) -> Tuple[bool, str, ChannelInteraction]:
        """
        Registrar que un usuario reaccionó a un post.

        Args:
            user_id: ID del usuario
            post_id: ID del mensaje en Telegram
            channel_id: ID del canal
            fragment_id_ref: Referencia a fragmento narrativo (opcional)

        Returns:
            Tuple (success, message, interaction)
        """
        try:
            # Verificar si existe interacción previa
            existing = await self.session.execute(
                select(ChannelInteraction).where(
                    and_(
                        ChannelInteraction.user_id == user_id,
                        ChannelInteraction.post_id == post_id,
                        ChannelInteraction.interaction_type == "view"
                    )
                )
            )
            existing_interaction = existing.scalars().first()

            if existing_interaction:
                # Actualizar a reacción
                existing_interaction.interaction_type = "reaction"
                existing_interaction.observation_score += 2  # Reaction bonus
                await self.session.commit()

                logger.info(f"Updated to reaction for user {user_id}, post {post_id}")

                return True, "Reaction tracked (updated)", existing_interaction

            # Crear nueva interacción de reacción
            interaction = ChannelInteraction(
                user_id=user_id,
                post_id=post_id,
                channel_id=channel_id,
                interaction_type="reaction",
                interaction_timestamp=datetime.now(timezone.utc),
                time_spent_seconds=0,
                observation_score=3,  # Base view (1) + reaction bonus (2)
                fragment_id_ref=fragment_id_ref
            )

            self.session.add(interaction)
            await self.session.commit()

            logger.info(f"Tracked reaction for user {user_id}, post {post_id}")

            return True, "Reaction tracked successfully", interaction

        except Exception as e:
            logger.error(f"Error tracking reaction: {e}")
            await self.session.rollback()
            return False, f"Error: {str(e)}", None

    async def add_clue_discovered(
        self,
        user_id: int,
        post_id: int,
        clue_id: str
    ) -> Tuple[bool, str]:
        """
        Registrar que un usuario descubrió una pista.

        Args:
            user_id: ID del usuario
            post_id: ID del mensaje donde se descubrió la pista
            clue_id: ID de la pista descubierta

        Returns:
            Tuple (success, message)
        """
        try:
            # Buscar interacción asociada
            result = await self.session.execute(
                select(ChannelInteraction).where(
                    and_(
                        ChannelInteraction.user_id == user_id,
                        ChannelInteraction.post_id == post_id
                    )
                )
            )
            interaction = result.scalars().first()

            if not interaction:
                return False, "No interaction found for this post"

            # Verificar si la pista ya fue descubierta
            if interaction.clues_discovered is None:
                interaction.clues_discovered = []

            if clue_id in interaction.clues_discovered:
                return True, "Clue already discovered"

            # Agregar pista
            interaction.clues_discovered.append(clue_id)
            interaction.observation_score += 5  # Clue bonus

            await self.session.commit()
            await self.session.refresh(interaction)

            logger.info(f"Clue '{clue_id}' discovered by user {user_id} in post {post_id}")

            return True, "Clue added successfully"

        except Exception as e:
            logger.error(f"Error adding clue: {e}")
            await self.session.rollback()
            return False, f"Error: {str(e)}"

    async def get_observation_score(self, user_id: int, channel_id: Optional[int] = None) -> int:
        """
        Obtener score de observación total de un usuario.

        Args:
            user_id: ID del usuario
            channel_id: ID del canal (opcional, si None busca en todos)

        Returns:
            Score total de observación
        """
        try:
            query = select(func.sum(ChannelInteraction.observation_score)).where(
                ChannelInteraction.user_id == user_id
            )

            if channel_id:
                query = query.where(ChannelInteraction.channel_id == channel_id)

            result = await self.session.execute(query)
            total_score = result.scalar() or 0

            return total_score

        except Exception as e:
            logger.error(f"Error getting observation score: {e}")
            return 0

    async def get_clues_discovered_count(self, user_id: int, channel_id: Optional[int] = None) -> int:
        """
        Obtener cantidad de pistas descubiertas por un usuario.

        Args:
            user_id: ID del usuario
            channel_id: ID del canal (opcional)

        Returns:
            Cantidad de pistas únicas descubiertas
        """
        try:
            query = select(ChannelInteraction).where(
                ChannelInteraction.user_id == user_id
            )

            if channel_id:
                query = query.where(ChannelInteraction.channel_id == channel_id)

            result = await self.session.execute(query)
            interactions = result.scalars().all()

            # Recopilar todas las pistas únicas
            all_clues = set()
            for interaction in interactions:
                if interaction.clues_discovered:
                    all_clues.update(interaction.clues_discovered)

            return len(all_clues)

        except Exception as e:
            logger.error(f"Error getting clues count: {e}")
            return 0

    async def get_observation_period(
        self,
        user_id: int,
        channel_id: Optional[int] = None
    ) -> Tuple[Optional[datetime], Optional[datetime]]:
        """
        Obtener período de observación de un usuario.

        Args:
            user_id: ID del usuario
            channel_id: ID del canal (opcional)

        Returns:
            Tuple (first_interaction, last_interaction)
        """
        try:
            query = select(ChannelInteraction).where(
                ChannelInteraction.user_id == user_id
            ).order_by(ChannelInteraction.interaction_timestamp)

            if channel_id:
                query = query.where(ChannelInteraction.channel_id == channel_id)

            result = await self.session.execute(query)
            interactions = result.scalars().all()

            if not interactions:
                return None, None

            first = interactions[0].interaction_timestamp
            last = interactions[-1].interaction_timestamp

            return first, last

        except Exception as e:
            logger.error(f"Error getting observation period: {e}")
            return None, None

    async def get_observation_status(
        self,
        user_id: int,
        channel_id: Optional[int] = None
    ) -> Dict:
        """
        Obtener estado completo de observación de un usuario.

        Args:
            user_id: ID del usuario
            channel_id: ID del canal (opcional)

        Returns:
            Dict con:
                - total_score: int
                - clues_count: int
                - posts_viewed: int
                - total_time_seconds: int
                - first_seen: datetime or None
                - last_seen: datetime or None
                - status: "success", "partial", "pending", "timeout"
        """
        try:
            # Obtener estadísticas
            query = select(ChannelInteraction).where(
                ChannelInteraction.user_id == user_id
            )

            if channel_id:
                query = query.where(ChannelInteraction.channel_id == channel_id)

            result = await self.session.execute(query)
            interactions = result.scalars().all()

            if not interactions:
                return {
                    "total_score": 0,
                    "clues_count": 0,
                    "posts_viewed": 0,
                    "total_time_seconds": 0,
                    "first_seen": None,
                    "last_seen": None,
                    "status": "pending"
                }

            # Calcular estadísticas
            total_score = sum(i.observation_score for i in interactions)
            posts_viewed = len(interactions)
            total_time = sum(i.time_spent_seconds for i in interactions)

            # Pistas únicas
            all_clues = set()
            for i in interactions:
                if i.clues_discovered:
                    all_clues.update(i.clues_discovered)

            clues_count = len(all_clues)
            first_seen = interactions[0].interaction_timestamp
            last_seen = interactions[-1].interaction_timestamp

            # Determinar estado
            if clues_count >= 3:
                status = "success"
            elif clues_count >= 1:
                status = "partial"
            else:
                # Verificar si pasó tiempo (3 días desde primera interacción)
                if first_seen:
                    # Normalizar first_seen a timezone-aware si es naive
                    if first_seen.tzinfo is None:
                        first_seen = first_seen.replace(tzinfo=timezone.utc)

                    timeout_threshold = first_seen + timedelta(days=3)
                    if datetime.now(timezone.utc) > timeout_threshold:
                        status = "timeout"
                    else:
                        status = "pending"
                else:
                    status = "pending"

            return {
                "total_score": total_score,
                "clues_count": clues_count,
                "posts_viewed": posts_viewed,
                "total_time_seconds": total_time,
                "first_seen": first_seen,
                "last_seen": last_seen,
                "status": status
            }

        except Exception as e:
            logger.error(f"Error getting observation status: {e}")
            return {
                "total_score": 0,
                "clues_count": 0,
                "posts_viewed": 0,
                "total_time_seconds": 0,
                "first_seen": None,
                "last_seen": None,
                "status": "error"
            }

    async def get_top_observers(
        self,
        channel_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Tuple[int, int, str]]:
        """
        Obtener top observadores (para leaderboard).

        Args:
            channel_id: ID del canal (opcional)
            limit: Cantidad máxima de resultados

        Returns:
            List de tuples (user_id, score, username)
        """
        try:
            query = select(
                ChannelInteraction.user_id,
                func.sum(ChannelInteraction.observation_score).label("score")
            ).group_by(ChannelInteraction.user_id)

            if channel_id:
                query = query.where(ChannelInteraction.channel_id == channel_id)

            query = query.order_by(desc("score")).limit(limit)

            result = await self.session.execute(query)
            rows = result.all()

            # Obtener usernames
            top_observers = []
            for user_id, score in rows:
                user_result = await self.session.execute(
                    select(User).where(User.user_id == user_id)
                )
                user = user_result.scalars().first()
                username = user.username if user else f"user_{user_id}"

                top_observers.append((user_id, score, username))

            return top_observers

        except Exception as e:
            logger.error(f"Error getting top observers: {e}")
            return []

    async def cleanup_old_interactions(self, days_old: int = 30) -> int:
        """
        Limpiar interacciones antiguas (para mantenimiento).

        Args:
            days_old: Días de antigüedad para eliminar

        Returns:
            Cantidad de registros eliminados
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)

            result = await self.session.execute(
                select(ChannelInteraction).where(
                    ChannelInteraction.interaction_timestamp < cutoff_date
                )
            )
            old_interactions = result.scalars().all()

            count = len(old_interactions)

            for interaction in old_interactions:
                await self.session.delete(interaction)

            await self.session.commit()

            logger.info(f"Cleaned up {count} old interactions (>{days_old} days)")

            return count

        except Exception as e:
            logger.error(f"Error cleaning up old interactions: {e}")
            await self.session.rollback()
            return 0
