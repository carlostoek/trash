# DianaBot UX Improvement PRD
## Product Requirements Document for Enhanced Emotional Connection

**Version:** 1.0
**Date:** 2026-01-10
**Status:** Draft for Review
**Prepared by:** Experience Design Analysis

---

## EXECUTIVE SUMMARY

### Current UX Assessment

DianaBot has a solid technical foundation with sophisticated narrative mechanics, but the **user experience lacks critical emotional touchpoints** that create genuine attachment and word-of-mouth sharing. The system successfully tracks archetype, relationships, and progress, but fails to surface this information in ways that make users feel seen, understood, and emotionally invested.

**Critical Finding:** The current implementation focuses on **mechanics over feeling**, delivering functional narrative progression without the emotional resonance that transforms users from readers into invested participants.

### User Experience Gaps Identified

1. **Invisible Progress:** Users complete fragments with no visual indication of advancement or remaining content
2. **Flat Choice Feedback:** Choices happen without emotional consequence or narrative weight
3. **Static Relationships:** Character relationships exist in database but don't evolve visibly
4. **No Suspense Building:** Pacing is uniform, missing curiosity and anticipation beats
5. **Zero Shareability:** No screenshot-worthy moments or viral mechanics
6. **Transaction Over Intimacy:** Interactions feel like consuming content, not building relationship

### Strategic Recommendation

**Recommended Approach: D) Balanced Approach with Emotional Priority**

Implement improvements in three waves:
1. **Wave 1 (Quick Wins - 2 weeks):** Visual polish, progress indicators, enhanced feedback
2. **Wave 2 (Emotional Depth - 4 weeks):** Relationship evolution, suspense mechanics, surprise moments
3. **Wave 3 (Social Features - 2 weeks):** Shareability, viral mechanics, community building

**Priority Matrix:**
- **High Impact / Low Effort:** Progress visualization, enhanced choice feedback
- **High Impact / High Effort:** Character relationship evolution, emotional beat enhancements
- **Medium Impact / Low Effort:** Shareability features
- **Medium Impact / High Effort:** Social features (defer to Wave 3)

---

## SECTION 1: PROGRESS VISUALIZATION

### Current State

**What Users Experience:**
- Run `/story` → See fragment → Make choice → See next fragment
- No indication of level completion
- No sense of "how much more"
- No milestone celebrations
- Status screen exists but requires manual checking via separate callback

**Emotional Impact:**
- Feels like endless content consumption
- No satisfaction of completion
- No anticipation of upcoming levels
- Reduced motivation to continue

### Target Experience

**Emotional Goals:**
- **Satisfaction:** "I'm making progress, I can see it"
- **Anticipation:** "I'm getting closer to something meaningful"
- **Pride:** "I've accomplished something worth celebrating"
- **Curiosity:** "I wonder what's coming next"

### Technical Requirements

#### 1.1 Embedded Progress Indicators

**Feature:** Visual progress bar within narrative messages

**Implementation:**
```python
# New function in narrative_formatters.py
def format_progress_indicator(
    current_fragment: StoryFragment,
    user_progress: UserNarrativeProgress
) -> str:
    """
    Creates visual progress indicator embedded in narrative.

    Format:
    📖 Nivel 1 de 6
    ▓▓▓▓▓░░░░░ 50% (3/6 fragmentos)

    Returns empty string if no meaningful progress to show.
    """
    level = current_fragment.narrative_level
    fragments_completed = len(user_progress.fragments_completed)

    # Count total fragments in level
    total_in_level = _count_fragments_in_level(level)

    if total_in_level <= 1:
        return ""  # Don't show for single-fragment levels

    percentage = int((fragments_completed / total_in_level) * 100)
    filled = '▓' * (percentage // 10)
    empty = '░' * (10 - len(filled))

    return (
        f"📖 Nivel {level} de 6\n"
        f"{filled}{empty} {percentage}% "
        f"({fragments_completed}/{total_in_level} fragmentos)\n\n"
    )
```

**Integration:**
```python
# In format_narrative_message(), add before header:
progress_indicator = format_progress_indicator(fragment, user_progress)
if progress_indicator:
    message = f"{progress_indicator}{title}{header}\n\n{content}"
```

#### 1.2 Level Completion Celebrations

**Feature:** Special message when completing a level

**Implementation:**
```python
# New function in narrative_formatters.py
def format_level_completion(
    level_completed: int,
    next_level_unlocked: bool
) -> str:
    """
    Creates celebratory message for level completion.

    Emotional beat: Achievement + Anticipation

    Example output:
    ✨ ¡Nivel Completado! ✨

    Has completado el Nivel 1: La Primera Revelación
    🎯 5 fragmentos explorados
    💕 Tu conexión con Diana ha comenzado

    [Next level preview hint]
    """
    if next_level_unlocked:
        preview = _get_level_preview_hint(level_completed + 1)
        return (
            f"✨ ¡Nivel Completado! ✨\n\n"
            f"Has completado el Nivel {level_completed}\n"
            f"{preview}\n\n"
            f"🌟 Tu viaje continúa..."
        )
    else:
        # VIP required message
        return (
            f"✨ ¡Nivel Completado! ✨\n\n"
            f"Has completado el Nivel {level_completed}\n\n"
            f"🔒 Los niveles 4-6 requieren suscripción VIP\n"
            f"para continuar tu viaje íntimo con Diana."
        )
```

**Trigger:** When user reaches fragment with `is_ending_fragment=True`

#### 1.3 "How Much More" Indicator

**Feature:** Subtle hint of remaining depth

**Implementation:**
```python
def format_depth_hint(
    current_level: int,
    user_archetype: ArchetypeProfile
) -> str:
    """
    Provides subtle hint of remaining content depth.

    Personalized by archetype:
    - Explorer: "Hay X caminos por descubrir..."
    - Romantic: "Tu conexión con Diana puede profundizar..."
    - Analytical: "X fragmentos restantes en este nivel..."
    """
    archetype = user_archetype.primary_archetype.lower()

    if archetype == "explorer":
        remaining = _count_unexplored_paths(current_level)
        return f"_🔍 Quedan {remaining} caminos por descubrir..._"
    elif archetype == "romantic":
        return f"_💕 Tu conexión con Diana puede profundizar más..._"
    elif archetype == "analytical":
        remaining = _count_remaining_fragments(current_level)
        return f"_🧠 {remaining} fragmentos restantes en este nivel_"
    else:
        # Generic hint
        return f"_📖 Tu historia continúa..._"
```

**Placement:** After narrative content, before choices

### Success Metrics

- **Session Length:** +30% time spent per session
- **Return Rate:** +40% users return within 24 hours
- **Completion Rate:** +25% users complete Level 1
- **Milestone Screenshots:** +20% users screenshot completion messages

---

## SECTION 2: ENHANCED CHOICE FEEDBACK

### Current State

**What Users Experience:**
- Click choice → Immediate transition to next fragment
- Small "Consequences" message appears (archetype points, relationship changes)
- Feedback feels like game mechanics, not narrative consequence
- No emotional weight to decisions
- No curiosity about alternative paths

**Emotional Impact:**
- Choices feel like clicking buttons, not making decisions
- No reflection on meaning of choice
- No investment in consequences
- Reduced replay value

### Target Experience

**Emotional Goals:**
- **Weight:** "My choice mattered and had impact"
- **Curiosity:** "I wonder what would have happened if..."
- **Recognition:** "Diana/Lucien noticed something about me from this choice"
- **Authenticity:** "I'm being真实的, not optimizing"

### Technical Requirements

#### 2.1 Immediate Narrative Feedback

**Feature:** Character reacts to choice before next fragment

**Implementation:**
```python
# New function in narrative_formatters.py
def format_choice_reaction(
    choice: StoryChoice,
    character_speaker: str,
    relationship_score: int
) -> str:
    """
    Creates immediate character reaction to user's choice.

    Emotional beat: Recognition of intention behind choice

    Example outputs:
    🌸 Diana: "Tu respuesta me dice mucho sobre ti..."
    🎩 Lucien: "Interesante. No muchos toman ese camino."
    """
    # Extract choice metadata
    choice_type = _classify_choice_type(choice)  # "romantic", "direct", "explorer", "analytical"

    # Get character-specific reaction
    if character_speaker == "DIANA":
        reaction = _get_diana_reaction(choice_type, relationship_score)
    elif character_speaker == "LUCIEN":
        reaction = _get_lucien_reaction(choice_type, relationship_score)
    else:
        return ""

    # Format with character emoji
    emoji = CHARACTER_EMOJIS.get(character_speaker, "")
    return f"{emoji} {reaction}"
```

**Reaction Database (JSON):**
```json
{
  "diana_reactions": {
    "romantic": [
      "Siento la sinceridad en tu respuesta...",
      "Hay una calidez en tu elección que me atrae...",
      "No muchos se atreven a ser tan vulnerables..."
    ],
    "direct": [
      "Tu franquez es refrescante...",
      "Aprecio que no rodees el asunto...",
      "Decidido. Me gusta eso..."
    ],
    "explorer": [
      "Siempre buscas más, ¿verdad?...",
      "Tu curiosidad es... intrigante...",
      "Veo que prefieres descubrir por ti mismo..."
    ],
    "analytical": [
      "Piensas mucho antes de actuar...",
      "Tu mente es tan fascinante como tu corazón...",
      "Interesante perspectiva. No la había considerado..."
    ]
  }
}
```

**Timing:** Display for 3 seconds before showing next fragment

#### 2.2 Consequence Visualization

**Feature:** Visual, narrative description of consequences

**Current Implementation (Improvement Needed):**
```python
# Current format_consequences_message() shows:
# ✨ Consecuencias:
# 🎯 Nueva información descubierta
# 💕 +2 puntos Romántico
# ❤️ Mejoró relación con Diana

# Problem: Feels like game mechanics, not narrative impact
```

**Enhanced Implementation:**
```python
def format_consequences_message_narrative(
    consequences: Dict[str, Any],
    relationship_status: CharacterRelationship
) -> str:
    """
    Creates narrative description of consequences.

    Emotional beat: Meaningful impact on relationship/character

    Example output:
    ✨ _Diana sonríe ligeramente al responder..._

    Tu elección ha deepenedizado la conexión entre ustedes.
    Algo en tu respuesta la ha hecho sentir comprendida.

    [Emoji indicators for game mechanics]
    💕 +2 puntos Romántico
    """
    parts = []

    # 1. Narrative consequence (primary)
    if consequences.get("relationship_changes", {}).get("DIANA", 0) > 0:
        parts.append("_Diana sonríe ligeramente al responder..._")
        parts.append("\nTu elección ha deepenedizado la conexión entre ustedes.")
        parts.append("Algo en tu respuesta la ha hecho sentir comprendida.\n")

    elif consequences.get("relationship_changes", {}).get("LUCIEN", 0) > 0:
        parts.append("_Lucien asiente con aprobación..._")
        parts.append("\nHas ganado su respeto. No es fácil lograrlo.\n")

    # 2. Game mechanics (secondary, visually distinct)
    if parts:
        parts.append("✨ <b>Consecuencias:</b>\n")

    # ... existing archetype points logic ...

    return "\n".join(parts) if parts else ""
```

#### 2.3 "What If" Preview

**Feature:** Hint at alternative paths without revealing content

**Implementation:**
```python
def format_alternative_path_hint(
    choice_made: StoryChoice,
    available_choices: List[StoryChoice]
) -> str:
    """
    Creates subtle hint about alternative paths.

    Emotional beat: Curiosity without regret

    Example output:
    _Otros viajeros han tomado caminos diferentes..._
    _En otra línea temporal, podrías haber descubierto..._

    Placement: After consequences, before next fragment
    """
    other_choices = [c for c in available_choices if c.choice_id != choice_made.choice_id]

    if not other_choices:
        return ""

    # Select random alternative choice
    other = random.choice(other_choices)

    # Get archetype-based hint
    archetype_hint = _get_archetype_alternative_hint(other)

    return f"_🔮 {archetype_hint}_"

def _get_archetype_alternative_hint(choice: StoryChoice) -> str:
    """Returns subtle hint based on choice archetype"""
    choice_type = _classify_choice_type(choice)

    hints = {
        "romantic": "Algunos han encontrado un camino más pasional aquí...",
        "direct": "Otros prefieren la acción inmediata...",
        "explorer": "Queda mucho por descubrir en el camino no tomado...",
        "analytical": "Una mente analítica podría haber visto esto diferente...",
    }

    return hints.get(choice_type, "Otros caminos quedan sin explorar...")
```

**Constraint:** Only show after user has made 3+ choices (avoid overwhelming new users)

### Success Metrics

- **Choice Deliberation Time:** +50% average time before selecting choice
- **Reread Rate:** +30% users re-read fragments before choosing
- **Replay Intent:** +40% users express desire to explore alternative paths
- **Emotional Engagement:** +60% users report choices feeling meaningful

---

## SECTION 3: CHARACTER RELATIONSHIP EVOLUTION

### Current State

**What Users Experience:**
- Relationship scores exist in database
- Status screen shows: "DIANA: Friendly (20)"
- No visible evolution during narrative
- No character recognition of relationship depth
- Static character voice regardless of relationship status

**Emotional Impact:**
- Relationships feel like game stats, not genuine connections
- No sense of progression toward intimacy
- Characters don't feel emotionally responsive
- Reduced attachment to Diana/Lucien

### Target Experience

**Emotional Goals:**
- **Recognition:** "Diana/Lucien knows how close we've become"
- **Pride:** "I've earned this level of intimacy"
- **Protectiveness:** "I care about this character"
- **Anticipation:** "I want to see how our relationship evolves"

### Technical Requirements

#### 3.1 Dynamic Character Voice

**Feature:** Character dialogue changes based on relationship score

**Implementation:**
```python
# Enhancement to format_narrative_message()
def format_narrative_message(
    fragment: StoryFragment,
    archetype: Optional[ArchetypeProfile] = None,
    relationship: Optional[CharacterRelationship] = None  # NEW PARAMETER
) -> str:
    """
    Formatea mensaje narrativo basado en fragmento, arquetipo y relación.

    NUEVO: Character voice adapts based on relationship score.
    """
    # Get content with archetype variant
    content = fragment.content_text or ""
    if archetype and fragment.content_variants:
        content = _get_archetype_variant(content, archetype, fragment.content_variants)

    # NEW: Apply relationship-based voice transformation
    if relationship and fragment.speaker in ["DIANA", "LUCIEN"]:
        content = _apply_relationship_voice(content, relationship)

    # ... rest of existing formatting ...
```

**Voice Transformation Database:**
```python
RELATIONSHIP_VOICE_TRANSFORMS = {
    "DIANA": {
        "neutral": {  # 0-19 score
            "distance_formality": 0.8,  # High formality
            "vulnerability_level": 0.1,  # Low vulnerability
            "personal_pronouns": 0.2,  # Few "tú", "nosotros"
        },
        "friendly": {  # 20-39 score
            "distance_formality": 0.5,
            "vulnerability_level": 0.3,
            "personal_pronouns": 0.5,
            "prefix_additions": ["¿Sabes?", "Te diré que..."]
        },
        "close_friend": {  # 40-59 score
            "distance_formality": 0.3,
            "vulnerability_level": 0.5,
            "personal_pronouns": 0.7,
            "prefix_additions": ["No se lo diré a muchos, pero...", "Confío en que..."]
        },
        "romantic": {  # 60-79 score
            "distance_formality": 0.1,
            "vulnerability_level": 0.7,
            "personal_pronouns": 0.9,
            "prefix_additions": ["Hay algo en ti...", "Nunca había compartido esto..."],
            "intimacy_markers": ["_susurra_", "_se acerca un poco más_"]
        },
        "deep_intimacy": {  # 80+ score
            "distance_formality": 0.0,
            "vulnerability_level": 0.9,
            "personal_pronouns": 1.0,
            "prefix_additions": ["Solo tú...", "Es que contigo es diferente..."],
            "intimacy_markers": ["_susurra muy cerca_", "_su voz tierna_"],
            "exclusive_content": True  # Unique content for deep intimacy
        }
    }
}
```

#### 3.2 Relationship Milestone Notifications

**Feature:** Celebrate when relationship status changes

**Implementation:**
```python
def format_relationship_milestone(
    character: str,
    old_status: str,
    new_status: str,
    relationship: CharacterRelationship
) -> str:
    """
    Creates celebratory message for relationship milestones.

    Emotional beat: Recognition of earned intimacy

    Example output (reaching "Romantic Interest"):
    💕 **Algo está cambiando...**

    Diana te mira de una forma diferente ahora.
    Hay una tensión entre ustedes que antes no existía.

    Tu sinceridad y vulnerabilidad han abierto un camino
    que solo unos pocos han recorrido con ella.

    _¿Hasta dónde estás dispuesto/a a llegar?_
    """
    if new_status == "Close Friend":
        return _format_close_friend_milestone(character, relationship)
    elif new_status == "Romantic Interest":
        return _format_romantic_milestone(character, relationship)
    elif new_status == "Deep Intimacy":
        return _format_deep_intimacy_milestone(character, relationship)
    return ""

def _format_romantic_milestone(character: str, relationship: CharacterRelationship) -> str:
    """Milestone: Reaching Romantic Interest (60+ score)"""
    character_emoji = CHARACTER_EMOJIS.get(character, "")

    if character == "DIANA":
        return (
            f"💕 **Algo está cambiando...**\n\n"
            f"{character_emoji} Diana te mira de una forma diferente ahora.\n"
            f"Hay una tensión entre ustedes que antes no existía.\n\n"
            f"Tu sinceridad y vulnerabilidad han abierto un camino\n"
            f"que solo unos pocos han recorrido con ella.\n\n"
            f"_¿Hasta dónde estás dispuesto/a a llegar?_"
        )
    elif character == "LUCIEN":
        return (
            f"🎩 **Respeto Mutuo**\n\n"
            f"{character_emoji} Lucien te ha ganado.\n\n"
            f"No es fácil impresionarlo, pero lo has logrado.\n"
            f"Su frialdad se ha transformado en respeto genuino,\n"
            f"y eso es algo que no concede ligeramente.\n\n"
            f"_Has demostrado que mereces estar aquí._"
        )
```

**Trigger:** When `relationship_score` crosses threshold (40, 60, 80)

#### 3.3 Character Memory System

**Feature:** Characters reference past interactions

**Implementation:**
```python
# New service: bot/services/character_memory.py
class CharacterMemoryService:
    """
    Tracks and retrieves meaningful interactions for character references.

    Enables characters to "remember" past choices and behaviors.
    """

    async def record_meaningful_interaction(
        self,
        user_id: int,
        character: str,
        interaction_type: str,
        context: Dict
    ) -> None:
        """
        Records an interaction worth remembering.

        Types:
        - "first_vulnerable_choice"
        - "consistent_behavior_pattern"
        - "emotional_intelligence_moment"
        - "surprising_depth"
        """
        # Store in JSON field or separate table
        pass

    async def get_relevant_memory(
        self,
        user_id: int,
        character: str,
        current_context: str
    ) -> Optional[str]:
        """
        Returns character-appropriate reference to past interaction.

        Example output:
        "Recuerdo cuando elegiste X en nuestra primera interacción...
         Esa misma autenticidad está aquí otra vez."
        """
        pass
```

**Integration in narrative:**
```python
# In format_narrative_message(), add character memory:
memory = await character_memory.get_relevant_memory(user_id, fragment.speaker)
if memory:
    content = f"{content}\n\n{i记忆}"
```

### Success Metrics

- **Emotional Attachment:** +70% users report feeling "connected" to characters
- **Relationship Progression:** +50% users reach "Close Friend" status
- **Return Rate:** +60% users return to see relationship evolution
- **Character Mentions:** +40% users mention Diana/Lucien in feedback

---

## SECTION 4: EMOTIONAL BEAT ENHANCEMENTS

### Current State

**What Users Experience:**
- Uniform pacing (fragment → choice → fragment → choice)
- No suspense building
- No surprise moments
- No variation in emotional intensity
- No anticipation beats

**Emotional Impact:**
- Narrative feels mechanical, not organic
- No emotional peaks and valleys
- Reduced immersion
- Boring, predictable rhythm

### Target Experience

**Emotional Goals:**
- **Suspense:** "I need to know what happens next"
- **Surprise:** "I didn't expect that!"
- **Anticipation:** "Something important is coming"
- **Relief:** "That was worth waiting for"

### Technical Requirements

#### 4.1 Suspense Building Mechanics

**Feature:** Delay and anticipation before important reveals

**Implementation:**
```python
# New function in narrative_formatters.py
def format_suspense_beat(
    next_fragment: StoryFragment,
    relationship_score: int
) -> Optional[str]:
    """
    Creates suspense beat before important fragments.

    Emotional beat: Build anticipation for impactful moments

    Example output:
    ···
    Algo está a punto de cambiar...
    ···

    Placement: Between fragments, auto-dismiss after 3 seconds
    """
    # Determine if next fragment is "important"
    if not next_fragment.is_ending_fragment and not next_fragment.besitos_reward > 50:
        return None  # Only build suspense for important moments

    # Select suspense message based on context
    if next_fragment.narrative_level >= 4:
        return (
            "···\n"
            "_Puedes sentirlo... algo está a punto de cambiar._\n"
            "···"
        )
    elif relationship_score >= 60:
        return (
            "···\n"
            "_Diana toma aire antes de continuar..._\n"
            "···"
        )
    else:
        return (
            "···\n"
            "_Un momento importante se aproxima..._\n"
            "···"
        )
```

**Timing:** Display as separate message, auto-delete after 3 seconds, then send actual fragment

#### 4.2 Surprise Moments

**Feature:** Unexpected emotional peaks

**Implementation:**
```python
# In StoryFragment model, add new field:
# surprise_moment = Column(Boolean, default=False)  # Is this a surprise reveal?

# In narrative.py handler:
async def _send_fragment_to_user(
    message: Message,
    fragment: StoryFragment,
    choices: list[StoryChoice],
    archetype: Optional[ArchetypeProfile] = None,
    is_reread: bool = False
) -> None:
    """
    Enhanced with surprise moment detection.
    """
    # Check if this is a surprise moment
    if fragment.surprise_moment and not is_reread:
        # Add visual indicator
        surprise_indicator = "✨ **REVELACIÓN** ✨\n\n"
        formatted_message = f"{surprise_indicator}{formatted_message}"

        # Optional: Add special animation/emoji burst
        await message.answer("✨", disable_notification=True)
        await asyncio.sleep(0.5)

    # ... rest of existing sending logic ...
```

**Surprise Moment Criteria:**
- First time Diana shows vulnerability
- First time Lucien approves
- Major plot twist
- Character revelation
- Unlock of hidden content

#### 4.3 Pacing Variation

**Feature:** Deliberate variation in rhythm

**Implementation:**
```python
# In StoryFragment model, add new field:
# pacing_intensity = Column(String(20), default="normal")  # "slow", "normal", "fast", "urgent"

# In handler:
async def _send_fragment_to_user(...):
    """
    Enhanced with pacing-based delays.
    """
    # Calculate delay based on pacing
    delay_map = {
        "slow": 2.0,  # 2 seconds before showing choices
        "normal": 0.5,
        "fast": 0.0,
        "urgent": 0.0
    }

    delay = delay_map.get(fragment.pacing_intensity, 0.5)

    # Send fragment without choices first
    await message.answer(formatted_message, parse_mode="HTML")

    # Wait based on pacing, then send choices
    if delay > 0:
        await asyncio.sleep(delay)

    # Send choices as separate message
    keyboard = create_narrative_keyboard(choices, fragment)
    await message.answer(
        "¿Qué haces?",
        reply_markup=keyboard
    )
```

**Pacing Guidelines:**
- **Slow:** Emotional moments, vulnerability, important revelations
- **Normal:** Standard narrative progression
- **Fast:** Action sequences, urgency
- **Urgent:** Critical decisions, time-sensitive choices

### Success Metrics

- **Session Engagement:** +40% increase in session length
- **Message Retention:** +50% users save/star important messages
- **Anticipation:** +60% users return quickly after suspense beats
- **Surprise Sharing:** +30% users screenshot/share surprise moments

---

## SECTION 5: SHAREABILITY & SOCIAL FEATURES

### Current State

**What Users Experience:**
- Zero shareability features
- No screenshot-worthy moments designed
- No viral mechanics
- No social proof or community feeling

**Emotional Impact:**
- No word-of-mouth promotion
- Reduced viral growth
- Isolated experience
- Missing emotional validation through sharing

### Target Experience

**Emotional Goals:**
- **Pride:** "I want people to know I experienced this"
- **Belonging:** "I'm part of something special"
- **Validation:** "Look at this beautiful/meaningful thing I found"
- **Curiosity:** "I want others to experience this too"

### Technical Requirements

#### 5.1 Archetype Share Cards

**Feature:** Generate shareable image showing user's archetype

**Implementation:**
```python
# New handler: bot/handlers/user/share.py
@share_router.callback_query("narrative:share:archetype")
async def callback_share_archetype(callback: CallbackQuery, session: AsyncSession):
    """
    Generates and sends shareable archetype card.

    Creates beautiful image with:
    - User's archetype (Explorer, Romantic, etc.)
    - Visual representation of secondary archetype
    - Confidence percentage
    - Meaningful description
    - Call-to-action: "Start your journey"

    Output: Image file + caption with deep link
    """
    user_id = callback.from_user.id

    # Get archetype data
    engine = StoryEngine(session, callback.bot)
    story_state = await engine.get_current_story_state(user_id)
    archetype = story_state["archetype"]

    # Generate image (using PIL or external service)
    image_path = await _generate_archetype_card_image(archetype)

    # Create shareable caption
    caption = (
        f"Mi arquetipo: {archetype.primary_archetype}\n"
        f"Descubre el tuyo en DianaBot\n"
        f"https://t.me/botusername?start=share_{user_id}"
    )

    # Send image
    with open(image_path, 'rb') as photo:
        await callback.message.answer_photo(
            photo,
            caption=caption
        )

    await callback.answer("✅ Tarjeta generada")
```

**Image Template:**
- Elegant, mysterious design
- Archetype name prominently displayed
- Visual representation (icons, colors)
- Secondary archetype subtly shown
- Confidence indicator
- Bot branding (subtle)

#### 5.2 Quote Generator

**Feature:** Extract and format beautiful quotes from narrative

**Implementation:**
```python
# New handler
@share_router.callback_query("narrative:share:quote")
async def callback_share_quote(callback: CallbackQuery, session: AsyncSession):
    """
    Generates shareable quote card.

    Selects meaningful quote from recent fragments.
    Formats with character name and atmosphere.
    Adds deep link for sharing.

    Example output:
    ·························
    "Algunas puertas solo se
     abren desde dentro."

        — Diana
    ·························
    """
    user_id = callback.from_user.id

    # Get recent meaningful quotes
    engine = StoryEngine(session, callback.bot)
    quotes = await engine.get_recent_meaningful_quotes(user_id, limit=5)

    # Select random quote (avoid repetition)
    quote = random.choice(quotes)

    # Format quote card
    quote_card = _format_quote_card(quote)

    # Send as message
    await callback.message.answer(
        quote_card,
        parse_mode="HTML"
    )

    await callback.answer("✅ Cita generada")
```

**Quote Selection Criteria:**
- Emotional resonance
- Character voice consistency
- Memorable phrasing
- Non-spoiler (no major plot points)
- Shareable length (1-3 sentences)

#### 5.3 Relationship Milestone Sharing

**Feature:** Share relationship achievements

**Implementation:**
```python
@share_router.callback_query("narrative:share:milestone")
async def callback_share_milestone(callback: CallbackQuery, session: AsyncSession):
    """
    Generates shareable milestone card.

    Example output:
    ✨ He alcanzado un nivel de
     conexión profunda con Diana.

     Circle Intimo — DianaBot

     ¿Tu turno?
    """
    # Get current relationship status
    # Generate milestone card
    # Include deep link
    pass
```

**Constraint:** Only allow sharing positive milestones (no "Diana hates me" cards)

#### 5.4 Referral System with Emotional Hook

**Feature:** Invite others with personalized message

**Implementation:**
```python
@share_router.callback_query("narrative:invite")
async def callback_invite_friend(callback: CallbackQuery, session: AsyncSession):
    """
    Generates personalized invitation link.

    User can select message style:
    - "Mysterious invitation"
    - "Direct recommendation"
    - "Emotional appeal"
    - "Challenge invitation"

    Each style reflects user's archetype.
    """
    # Get user's archetype
    # Generate invitation options
    # Create deep link with referral code
    pass
```

**Reward:** Small relationship boost for both users when referred friend completes Level 1

### Success Metrics

- **Shares Per User:** +0.5 shares per active user (baseline: 0)
- **Referral Rate:** +15% new users from referrals
- **Viral Coefficient:** 0.3 (each user brings 0.3 new users)
- **Social Media Mentions:** +50% mentions in social platforms

---

## SECTION 6: SUCCESS METRICS

### Emotional Engagement Indicators

**Primary Metrics:**
- **Emotional Investment Score:** Percentage of users reaching "Romantic Interest" (60+) relationship status
  - Target: 40% of users who complete Level 1
  - Current: Unknown (needs baseline measurement)

- **Authenticity Score:** Average time spent on choices (longer = more thoughtful)
  - Target: 45+ seconds per choice
  - Current: ~15 seconds (estimated)

- **Attachment Score:** Percentage of users who return within 24 hours
  - Target: 60%
  - Current: Unknown (needs baseline measurement)

**Secondary Metrics:**
- **Completion Rate:** Percentage of users completing each level
  - Level 1: Target 70%
  - Level 2: Target 50%
  - Level 3: Target 40%

- **Session Depth:** Average fragments per session
  - Target: 8+ fragments per session
  - Current: ~3 fragments (estimated)

- **Reread Rate:** Percentage of fragments re-read
  - Target: 25%
  - Current: ~5% (estimated)

### Behavioral Indicators

**Leading Indicators (predict future engagement):**
- Quick return (< 1 hour) after suspense beat
- Screenshot/key screenshot behavior
- Message forwarding to friends
- Repeated visits to same level

- Lagging Indicators (reflect past engagement):
- VIP conversion rate
- Referral generation
- Community participation
- Long-term retention (30+ days)

### Technical Performance Metrics

**System Performance:**
- Message delivery latency: < 2 seconds
- Image generation time: < 5 seconds
- Database query time: < 500ms

**Error Rates:**
- Message send failure rate: < 1%
- Image generation failure rate: < 2%
- User-reported bugs: < 5% of users

---

## SECTION 7: ESTIMATED EFFORT

### Wave 1: Quick Wins (2 weeks)

**Progress Visualization (5 days)**
- Embedded progress indicators: 2 days
- Level completion celebrations: 1 day
- "How much more" indicators: 1 day
- Testing and refinement: 1 day

**Enhanced Choice Feedback (5 days)**
- Immediate narrative feedback: 2 days
- Consequence visualization: 2 days
- "What if" previews: 1 day

**Technical Complexity:** Low-Medium
**Risk:** Low (non-breaking changes)
**Dependencies:** None

### Wave 2: Emotional Depth (4 weeks)

**Character Relationship Evolution (10 days)**
- Dynamic character voice system: 4 days
- Relationship milestone notifications: 2 days
- Character memory service: 4 days

**Emotional Beat Enhancements (10 days)**
- Suspense building mechanics: 3 days
- Surprise moments: 2 days
- Pacing variation: 3 days
- Testing and refinement: 2 days

**Narrative Content Creation (8 days)**
- Write character voice variations: 3 days
- Write milestone messages: 2 days
- Write suspense beats: 2 days
- Review and polish: 1 day

**Technical Complexity:** Medium-High
**Risk:** Medium (requires careful emotional calibration)
**Dependencies:** Wave 1 completion

### Wave 3: Social Features (2 weeks)

**Shareability Features (6 days)**
- Archetype share cards: 2 days
- Quote generator: 2 days
- Milestone sharing: 1 day
- Testing: 1 day

**Referral System (4 days)**
- Invitation system: 2 days
- Reward mechanics: 1 day
- Deep link integration: 1 day

**Technical Complexity:** Medium
**Risk:** Low-Medium
**Dependencies:** Wave 2 completion

### Total Effort Summary

- **Development Time:** 8 weeks (2 months)
- **Testing Time:** 2 weeks (parallel with development)
- **Content Creation:** 2 weeks (integrated with development)
- **Total Timeline:** 10 weeks from start to full deployment

### Resource Requirements

**Development:**
- 1 Full-stack developer (backend + Telegram bot)
- 1 Content writer (narrative variations, reactions, milestones)
- 1 UI/UX designer (shareable cards, visual polish)

**Infrastructure:**
- Image generation service (PIL, Pillow, or external API)
- Additional database storage for character memories
- Potential CDN for shareable images

**Testing:**
- User testing group (10-15 users) for emotional calibration
- A/B testing for timing and pacing
- Analytics implementation for success metrics

---

## SECTION 8: PHASED ROLLOUT PLAN

### Phase 1: Internal Testing (Week 1-2)

**Goals:**
- Verify technical implementation
- Test emotional resonance
- Identify pacing issues

**Activities:**
- Deploy Wave 1 features to test environment
- Internal team testing (5 people)
- Collect qualitative feedback
- Iterate on timing and messaging

**Success Criteria:**
- No critical bugs
- Positive qualitative feedback on emotional impact
- Clear improvement over baseline experience

### Phase 2: Beta Testing (Week 3-4)

**Goals:**
- Validate emotional resonance with real users
- Test technical performance at scale
- Gather metrics for baseline comparison

**Activities:**
- Invite 20-30 beta users
- Deploy Wave 1 features
- Collect quantitative metrics (session length, return rate)
- Collect qualitative feedback (surveys, interviews)

**Success Criteria:**
- +30% session length increase
- +40% return rate increase
- Positive emotional feedback (>70% report feeling "more engaged")

### Phase 3: Wave 1 Rollout (Week 5-6)

**Goals:**
- Deploy progress visualization and enhanced feedback to all users
- Monitor performance and user feedback
- Prepare for Wave 2 development

**Activities:**
- Full rollout of Wave 1
- Monitor analytics dashboard
- Address any critical issues
- Begin Wave 2 content creation

**Success Criteria:**
- No increase in error rates
- Positive user feedback (>60% report improvements)
- Stable performance under load

### Phase 4: Wave 2 Development & Testing (Week 7-10)

**Goals:**
- Develop and test emotional depth features
- Calibrate character voice evolution
- Validate relationship milestones

**Activities:**
- Internal testing of Wave 2 features
- Beta testing with select group
- Emotional calibration iterations
- Performance testing

**Success Criteria:**
- Character voice feels natural (not forced)
- Relationship milestones feel earned (not rushed)
- Positive emotional impact (>80% report feeling "more connected")

### Phase 5: Wave 2 Rollout (Week 11-12)

**Goals:**
- Deploy emotional depth features to all users
- Monitor advanced metrics
- Begin Wave 3 development

**Activities:**
- Full rollout of Wave 2
- Monitor relationship progression metrics
- Collect feedback on character evolution
- Begin social feature development

**Success Criteria:**
- +50% users reach "Close Friend" status
- +40% increase in session depth
- Positive emotional feedback (>75% report feeling "emotionally invested")

### Phase 6: Wave 3 Rollout (Week 13-14)

**Goals:**
- Deploy shareability and social features
- Measure viral impact
- Complete full UX transformation

**Activities:**
- Full rollout of Wave 3
- Monitor sharing metrics
- Track referral growth
- Final analytics review

**Success Criteria:**
- +0.5 shares per user
- +15% referral rate
- Viral coefficient > 0.3
- Overall positive user feedback (>80% satisfied with experience)

---

## SECTION 9: RISK MITIGATION

### Technical Risks

**Risk 1: Message Delivery Latency**
- **Impact:** Poor user experience, lost emotional beat
- **Probability:** Medium
- **Mitigation:**
  - Implement message queuing system
  - Add retry logic for failed sends
  - Monitor latency in real-time
  - Set up alerts for threshold breaches

**Risk 2: Image Generation Failures**
- **Impact:** Shareability features break
- **Probability:** Low-Medium
- **Mitigation:**
  - Implement fallback to text-only sharing
  - Use reliable image generation service
  - Add error handling and retry logic
  - Monitor failure rates

### Emotional Risks

**Risk 3: Forced Emotional Manipulation**
- **Impact:** Users feel manipulated, disengage
- **Probability:** Medium (if not carefully calibrated)
- **Mitigation:**
  - User testing for emotional resonance
  - Avoid over-dramatization
  - Keep character voice authentic
  - Don't break character for mechanics

**Risk 4: Pacing Issues**
- **Impact:** Users bored or overwhelmed
- **Probability:** Medium
- **Mitigation:**
  - A/B test timing variations
  - Monitor session drop-off points
  - Allow user control (skip button)
  - Calibrate based on user behavior

### Content Risks

**Risk 5: Inconsistent Character Voice**
- **Impact:** Breaks immersion, reduces attachment
- **Probability:** Medium (with multiple writers)
- **Mitigation:**
  - Create detailed character voice guidelines
  - Single writer for each character
  - Regular voice consistency reviews
  - User feedback on character authenticity

### Business Risks

**Risk 6: Low Adoption of New Features**
- **Impact:** Development effort wasted
- **Probability:** Low (given strong baseline engagement)
- **Mitigation:**
  - Phased rollout with continuous feedback
  - Feature discovery (don't hide new features)
  - User education (subtle in-character hints)
  - Monitor adoption metrics

---

## SECTION 10: CONCLUSION & RECOMMENDATIONS

### Summary of UX Improvements

DianaBot has exceptional technical foundation and sophisticated narrative mechanics, but currently **prioritizes functionality over emotional connection**. The proposed UX improvements will transform the experience from "reading a story" to "building a relationship with Diana."

### Critical Success Factors

1. **Emotional Calibration is Key**
   - Every feature must serve emotional connection
   - Test emotional resonance, not just functionality
   - Avoid game mechanics that break immersion

2. **Character Consistency is Paramount**
   - Never break character for UI mechanics
   - Keep Diana's voice authentic and mysterious
   - Maintain Lucien's evolving but consistent personality

3. **Pacing Creates Emotional Impact**
   - Suspense and anticipation are as important as content
   - Variation in emotional intensity keeps users engaged
   - Not every moment should be "epic" — contrast matters

4. **Recognition Creates Attachment**
   - Users return when they feel seen and understood
   - Personalization must be genuine, not algorithmic
   - Character memory creates sense of ongoing relationship

### Recommended Implementation Order

**Priority 1 (Do First):**
- Progress visualization (improves session completion)
- Enhanced choice feedback (creates immediate emotional impact)
- Relationship milestone notifications (recognizes user investment)

**Priority 2 (Do Second):**
- Dynamic character voice (creates sense of evolution)
- Suspense and surprise mechanics (builds anticipation)
- Character memory system (deepens connection)

**Priority 3 (Do Last):**
- Shareability features (leverages existing emotional investment)
- Social mechanics (amplifies success through virality)
- Advanced analytics (optimizes based on data)

### Long-Term Vision

The ultimate goal is to create an experience where users:

1. **Feel genuinely understood** by Diana and Lucien
2. **Experience emotional growth** through the narrative journey
3. **Develop authentic attachment** to fictional characters
4. **Want to share** their experience with others (carefully, without spoiling)
5. **Return regularly** to continue the relationship

These improvements will position DianaBot as not just a narrative bot, but as an **emotional experience** that users remember, value, and advocate for.

### Final Recommendation

**Proceed with Balanced Approach (Option D)**

Implement all three waves, but prioritize Wave 1 (Visual Polish) first for quick wins, then Wave 2 (Emotional Depth) for deep impact, and finally Wave 3 (Social Features) to amplify success through virality.

**Timeline:** 10 weeks total, with measurable improvements visible after Week 2 (Wave 1 rollout).

**Expected ROI:**
- +50% increase in session length
- +60% increase in return rate
- +40% increase in completion rate
- +15% increase in referral rate
- +30% increase in VIP conversion

**Emotional ROI (Harder to measure but more valuable):**
- Users who feel "seen" and "understood"
- Word-of-mouth advocacy from genuine emotional impact
- Community formation around shared experience
- Long-term brand loyalty and attachment

---

**Document Status:** Ready for Review
**Next Steps:**
1. Stakeholder review and approval
2. Resource allocation and team assignment
3. Detailed technical specifications for each feature
4. Content creation timeline and guidelines
5. Analytics and measurement framework setup

**Contact:** For questions or clarifications about this PRD, consult the Experience Design team.

---

*This PRD was created with emotional connection as the primary success metric. Every recommended feature serves the goal of making users feel understood, valued, and emotionally invested in their relationship with Diana and Lucien.*
