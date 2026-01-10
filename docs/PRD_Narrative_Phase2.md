# DianaBot Narrative System - Product Requirements Document (PRD)
## Phase 2: Completing the Narrative Journey

**Document Version:** 1.0
**Date:** January 10, 2026
**Status:** Strategic Planning
**Prepared by:** Narrative Games Expert Analysis

---

## Executive Summary

### Current State Assessment

**What's Working (Strengths):**
- ✅ **Level 1 Complete:** 5 fragments, 2 choices, fully functional narrative system
- ✅ **Technical Foundation:** 8 database models, StoryEngine service, all handlers operational
- ✅ **Character Foundation:** Diana and Lucien established with distinct voices
- ✅ **Test Coverage:** 39/39 tests passing (100%)
- ✅ **System Integration:** Narrative system connects with gamification (besitos, XP, relationships)

**Critical Gaps Identified:**
- ❌ **Missing 83% of Narrative:** Levels 2-6 completely absent from database
- ❌ **Incomplete Character Arcs:** Diana's evolution from mysterious muse to vulnerable intimate not delivered
- ❌ **Lucien's Growth:** Gatekeeper evolution from cold evaluator to trusted confidant missing
- ❌ **No Archetype Personalization:** 6 user archetypes defined but not implemented in content
- ❌ **No Consequence System:** Choices don't create meaningful delayed payoff
- ❌ **No Multiple Endings:** Level 6 promises archetype-based endings but none exist
- ❌ **Missing Emotional Progression:** Free→VIP transition lacks compelling justification

**Business Impact:**
- Users experience 5-minute taste but no journey completion
- VIP subscription has weak value proposition (no premium content to access)
- Character investment dissipates without continuation
- Technical excellence underutilized (full system built, minimal content)

### The Vision vs Reality Gap

**Promised Experience (from docs/narrativo.md):**
```
Level 1: Welcome & Curiosity ✅ DELIVERED
Level 2: Observation & Deep Interest ❌ MISSING
Level 3: Mutual Discovery & Intimacy Preview ❌ MISSING
Level 4: Intellectual Comprehension (VIP starts) ❌ MISSING
Level 5: Emotional Vulnerability (VIP deepens) ❌ MISSING
Level 6: Complete Synthesis & Multiple Endings ❌ MISSING
```

**Emotional Promise:** "Diana se revela gradualmente, pasando de musa enigmática a compañera vulnerable"

**Current Delivery:** Diana stays enigmatic, never reaches vulnerability. Users left at first base.

---

## Section 1: Narrative Content Requirements for Levels 2-3 (Free Content)

### Level 2: "Observación y Prueba" - Deepening the Mystery

**Objective:** Transform Diana from distant figure to intriguing presence worth pursuing

**Narrative Arc:**
- Diana acknowledges user's return (creates sense of being noticed)
- Lucien presents observation challenge (tests attention to detail)
- User demonstrates genuine interest beyond surface curiosity
- Diana rewards observation with personal vulnerability (first crack in armor)

**Required Fragments (L2_*):**

1. **L2_RETURN_001** - "El Regreso Observado de Diana"
   - Speaker: DIANA
   - Emotion: intrigued_amused
   - Starting: Yes (continuation from L1)
   - Content: Diana notices user returned, comments on their persistence
   - Variations:
     - If returned < 24h: "Viniste de inmediato. Hay una urgencia en ti..."
     - If returned > 3 days: "Tomaste tiempo para procesar. Esa paciencia..."
   - Reward: 10 besitos

2. **L2_CHALLENGE_002** - "Lucien Presenta el Desafío de Observación"
   - Speaker: LUCIEN
   - Emotion: testing
   - Content: Lucien explains 3-day observation mission in channel
   - Mission: Find hidden clues in channel posts (subtle visual/text details)
   - Technical: Integration with channel post tracking system
   - Reward: 15 besitos

3. **L2_SUCCESS_003** - "Reconocimiento de la Observación Profunda"
   - Speaker: DIANA
   - Emotion: genuine_surprise
   - Unlock Condition: User found 3+ hidden clues
   - Content: Diana expresses genuine surprise at user's attention to detail
   - Reward: "Pista 2 del mapa" + 20 besitos + "Fragmento de Memoria" (image)

4. **L2_PARTIAL_004** - "Reconocimiento de Observación Parcial"
   - Speaker: DIANA
   - Emotion: encouraging
   - Unlock Condition: User found 1-2 clues
   - Content: Diana acknowledges effort, encourages deeper observation
   - Reward: 10 besitos + hint for better observation

5. **L2_MEMORY_FRAGMENT_005** - "El Fragmento de Memoria"
   - Speaker: NARRATOR
   - Media: IMAGE (Diana's personal memory - reveal something about her past)
   - Content: Visual storytelling showing Diana's vulnerability
   - Ending: Yes
   - Reward: 25 besitos + 50 XP + unlock L3

**Key Emotional Beats:**
- **Curiosity → Fascination:** User moves from "who is she?" to "I need to know more"
- **Distance → Recognition:** Diana shifts from distant to "I see you"
- **Passive → Active:** User proves genuine interest through observation challenge

**Choices (L2_*):**
- L2_RETURN_A: "🔍 Explorar más profundo" → L2_CHALLENGE_002
  - Consequences: flags_set ["deep_interest"], archetype: explorer+2, patient+1
- L2_CHALLENGE_A: "👁️ Aceptar el desafío" → L2_SUCCESS_003 (conditional)
  - Consequences: flags_set ["observation_accepted"], unlocks mission
- L2_SUCCESS_A: "💎 Las encontré todas" → L2_MEMORY_FRAGMENT_005
  - Consequences: relationship: DIANA+5, LUCIEN+3, items_gained ["pista_2_mapa", "fragmento_memoria"]

**Technical Requirements:**
- Channel post tracking system (hidden clue detection)
- Time-based return detection (hours since L1 completion)
- Image storage for "Fragmento de Memoria"
- Mission unlock system for observation challenge

---

### Level 3: "Prueba Final" - The VIP Hook

**Objective:** Create irresistible desire to continue to VIP by delivering maximum free content value

**Narrative Arc:**
- Diana reveals she wants to know user (reciprocity)
- User completes "Perfil de Deseo" (deep psychological questions)
- Diana acknowledges mutual vulnerability
- Invitation to VIP with personalized discount based on understanding

**Required Fragments (L3_*):**

1. **L3_REVEAL_001** - "Diana Revela la Prueba Final"
   - Speaker: DIANA
   - Emotion: intense_curiosity
   - Starting: Yes
   - Content: "Hemos llegado al final de lo que puedo mostrarte... en este lado del muro"
   - Hook: "Ahora yo quiero descubrir quién eres tú"
   - Reward: 15 besitos

2. **L3_PROFILE_INTRO_002** - "El Perfil de Deseo"
   - Speaker: DIANA
   - Emotion: vulnerable_curious
   - Content: Introduction to deep psychological questions
   - Mission: Complete 7-question profile about desires, motivations, authenticity
   - Questions examples:
     - "¿Qué buscas realmente detrás de la curiosidad?"
     - "Describe un momento donde sentiste conexión verdadera"
     - "¿Qué estás dispuesto a arriesgar para entenderme?"
   - Technical: Multi-step FSM with question storage

3. **L3_PROFILE_RESPONSE_ROMANTIC** - "Respuesta para Perfil Romántico"
   - Speaker: DIANA
   - Emotion: moved_touched
   - Unlock Condition: Archetype = ROMANTIC OR profile indicates emotional focus
   - Content: "Hay una poesía en cómo describes lo que buscas..."
   - Reward: "Pista 3 del mapa" + 25 besitos + 75 XP

4. **L3_PROFILE_RESPONSE_DIRECT** - "Respuesta para Perfil Directo"
   - Speaker: DIANA
   - Emotion: respecting_admiring
   - Unlock Condition: Archetype = DIRECT OR profile indicates honesty/bluntness
   - Content: "Me fascina tu honestidad sin filtros..."
   - Reward: "Pista 3 del mapa" + 25 besitos + 75 XP

5. **L3_PROFILE_RESPONSE_INTROSPECTIVE** - "Respuesta para Perfil Introspectivo"
   - Speaker: DIANA
   - Emotion: deep_connection
   - Unlock Condition: Archetype = ANALYTICAL OR profile indicates self-awareness
   - Content: "Hay una profundidad en tus respuestas que me recuerda a mí misma..."
   - Reward: "Pista 3 del mapa" + 25 besitos + 75 XP

6. **L3_INVITATION_006** - "La Invitación al Diván"
   - Speaker: DIANA → LUCIEN
   - Emotion: longing_hopeful
   - Ending: Yes (Level 3 complete)
   - Content:
     - Diana: "Sabes algo curioso? Pensé que mantener la distancia sería más fácil contigo..."
     - "Pero hay algo en cómo me miras que hace que quiera mostrar más"
     - Lucien: Appears with personalized VIP invitation
   - Reward: 30 besitos + 100 XP + VIP_INVITATION (custom discount based on profile)

**Key Emotional Beats:**
- **One-Way Mystery → Two-Way Discovery:** Diana shifts from being studied to studying user
- **Distance → Closeness:** Maximum free intimacy before VIP paywall
- **Curiosity → Investment:** User emotionally invested before seeing price tag

**Choices (L3_*):**
- L3_REVEAL_A: "💭 Quiero conocerte mejor" → L3_PROFILE_INTRO_002
  - Consequences: flags_set ["reciprocal_interest"], relationship: DIANA+3
- L3_PROFILE_A: [Submit Profile] → [Archetype-based response]
  - Consequences: archetype_points based on responses, flags_set ["completed_profile"]
- L3_RESPONSE_A: "🚀 Continuar al Diván" → L3_INVITATION_006
  - Consequences: relationship: DIANA+5, LUCIEN+2, unlocks VIP invitation

**Technical Requirements:**
- Multi-step FSM for 7-question profile
- Archetype detection algorithm based on profile answers
- Custom VIP invitation generation (discount based on profile depth)
- Profile storage for Level 4 callbacks

**VIP Conversion Hook:**
The personalized invitation should say:
> "Diana ha seleccionado especialmente para ti: [X]% de descuento en acceso VIP.
> Tu perfil indica [archetype] - nivel de compatibilidad: [Y]%.
> Diana espera tu respuesta en el Diván."

---

## Section 2: Narrative Content Requirements for Levels 4-6 (VIP Content)

### Level 4: "El Diván - Intimidad I" - Intellectual Comprehension

**Objective:** Deliver immediate VIP value through intellectual depth, not just withheld content

**Narrative Arc:**
- Diana welcomes user to VIP space (closer but still guarded)
- Lucien presents "comprehension evaluation" (not trivia, but soul questions)
- User demonstrates understanding of Diana's psychology
- Diana shows unprecedented vulnerability (not physical, emotional)

**Required Fragments (L4_*):**

1. **L4_WELCOME_001** - "Bienvenida Íntima de Diana"
   - Speaker: DIANA
   - Emotion: warm_enigmatic
   - Starting: Yes (requires VIP subscription)
   - Content: "Oh... finalmente decidiste cruzar completamente. Bienvenido al Diván"
   - Key line: "Aquí estoy más cerca, sí. Pero recuerda... la verdadera intimidad no se trata de proximidad física"
   - Media: IMAGE (Diana in elegant space, closer but still mysterious)
   - Reward: 25 besitos + 100 XP

2. **L4_CHALLENGE_002** - "Lucien Presenta el Desafío Profundo"
   - Speaker: LUCIEN
   - Emotion: respectful_testing
   - Content: "Aquí, ella evalúa tu comprensión. No se trata de conocer datos sobre ella"
   - Mission: 7 comprehension questions (not factual, but psychological)
   - Questions:
     - "¿Por qué Diana construye muros si busca conexión?"
     - "¿Qué contradicción en Diana te intriga más?"
     - "¿Cuándo crees que Diana es más auténtica?"
   - Technical: Quiz system with psychological scoring
   - Reward: 20 besitos

3. **L4_HIGH_COMPREHENSION_003** - "Alta Comprensión (7+ correctas)"
   - Speaker: DIANA
   - Emotion: genuine_vulnerability
   - Unlock Condition: 7+ correct comprehension answers
   - Content: "Vaya... realmente me ves, ¿verdad? Respondiste con comprensión que va más allá de las palabras"
   - Key moment: Diana allows moment of authentic vulnerability
   - Reward: "Visión del Diván" + "Pista Complementaria" + 40 besitos

4. **L4_MEDIUM_COMPREHENSION_004** - "Comprensión Media (4-6 correctas)"
   - Speaker: DIANA
   - Emotion: honest_appreciating
   - Unlock Condition: 4-6 correct comprehension answers
   - Content: "Comprendes algunas capas, pero otras permanecen opacas"
   - Key moment: Diana appreciates honesty about limitations
   - Reward: "Visión Parcial" + "Pista Incompleta" + 25 besitos

5. **L4_SYNTHESIS_005** - "La Síntesis de Mundos"
   - Speaker: DIANA
   - Emotion: proud_touched
   - Unlock Condition: Completed L2 + L3 + L4 (collected all clues)
   - Content: User has united pieces from Free and VIP worlds
   - Key line: "Este mapa no señala un lugar físico. Señala un estado de comprensión"
   - Reward: "Los Archivos de Diana" unlock + 50 besitos + 150 XP
   - Ending: Yes

**Key Emotional Beats:**
- **Distance → Nearness:** Physical proximity in VIP space
- **Surface → Depth:** Intellectual comprehension replaces superficial curiosity
- **Mystery → Understanding:** User sees Diana's psychology, not just persona

**Premium Differentiators:**
- Diana speaks more openly (longer, deeper monologues)
- Content references specific user choices from Levels 1-3 (memory system)
- Higher emotional intensity (vulnerability glimpses)
- "Los Archivos de Diana" - exclusive content unlocked only here

**Technical Requirements:**
- VIP subscription validation before accessing L4_*
- Comprehension quiz system (psychological scoring, not factual)
- Cross-level memory system (references L1-L3 choices)
- "Archivos de Diana" content delivery system

---

### Level 5: "El Diván - Intimidad II" - Emotional Vulnerability

**Objective:** Transform intellectual understanding into emotional intimacy

**Narrative Arc:**
- Diana acknowledges user's growth from Level 1
- Lucien explains new phase: emotional comprehension vs intellectual
- "Diálogos de Intimidad" - Diana shares fears/contradictions
- User responds with empathy (not solving, just understanding)
- Diana rewards emotional maturity with "Archivo Personal"

**Required Fragments (L5_*):**

1. **L5_EVOLUTION_001** - "Diana Reconoce la Evolución"
   - Speaker: DIANA
   - Emotion: warm_proud
   - Starting: Yes
   - Content: "Mira cómo has crecido desde Los Kinkys hasta aquí"
   - Callbacks: References specific L1-L3 choices user made
   - Key line: "Cuando te conocí, eras curiosidad pura. Ahora... ahora eres comprensión"
   - Reward: 30 besitos

2. **L5_CHALLENGE_002** - "Los Diálogos de Vulnerabilidad"
   - Speaker: LUCIEN
   - Emotion: serious_warning
   - Content: "Diana está a punto de mostrarte partes de sí misma que nunca ha compartido"
   - Warning: "Solo si demuestras que puedes sostener esa intimidad sin intentar poseerla"
   - Mission: "Diálogos de Intimidad" - multi-stage emotional conversation
   - Reward: 25 besitos

3. **L5_DIALOGUE_1_003** - "Primera Confesión: La Contradicción"
   - Speaker: DIANA
   - Emotion: raw_honest
   - Content: "¿Sabes cuál es mi mayor contradicción? Construyo muros para mantener a todos a distancia... pero secretamente anhelo que alguien sea lo suficientemente persistente para encontrar la puerta"
   - Challenge: User must respond with empathy, not solutions
   - Response options:
     - A: "Puedes confiar en mí completamente" → Diana se distancia (posesive)
     - B: "Entiendo esa contradicción, es hermosa y humana" → Diana se acerca (empatic)
     - C: "No necesitas muros conmigo" → Diana se cierra (solution-oriented)
   - Reward: 20 besitos

4. **L5_DIALOGUE_2_004** - "Segunda Confesión: El Miedo"
   - Speaker: DIANA
   - Emotion: vulnerable_afraid
   - Content: Diana shares deeper fear about being seen completely
   - Challenge: User must demonstrate understanding without invasion
   - Response evaluation based on archetype and emotional intelligence
   - Reward: 25 besitos

5. **L5_RECOGNITION_005** - "El Reconocimiento de la Verdadera Intimidad"
   - Speaker: DIANA
   - Emotion: relieved_touched
   - Unlock Condition: All dialogue responses showed empathy
   - Content: "Comprendes algo que pocos logran captar: que la verdadera intimidad no es eliminar la distancia"
   - Key line: "Gracias por entender que puedo ser vulnerable sin ser conquistable"
   - Reward: "Archivo Personal de Diana" (memories, thoughts, reflections) + 50 besitos + 200 XP
   - Ending: Yes

**Key Emotional Beats:**
- **Intellectual → Emotional:** User moves from understanding mind to understanding heart
- **Distanced → Closest:** Maximum emotional intimacy (still not physical/romantic)
- **Understanding → Acceptance:** User accepts Diana's contradictions without fixing

**Premium Differentiators:**
- Diana's most vulnerable content yet
- User choices have immediate emotional consequences (Diana pulls closer/pushes away)
- "Archivo Personal" - deeply personal content never shared elsewhere
- First time Diana explicitly says "thank you for understanding me"

**Technical Requirements:**
- Response evaluation system (empathy vs possession vs solution detection)
- Relationship score impacts (positive/negative based on responses)
- "Archivo Personal" content delivery (exclusive Level 5+ content)
- Archetype-based dialogue variations

---

### Level 6: "La Culminación Suprema" - Multiple Endings

**Objective:** Deliver archetype-based endings that honor user's entire journey

**Narrative Arc:**
- Diana reveals final secret (she was evaluating herself too)
- Lucien shifts from gatekeeper to collaborator
- User receives ending based on archetype + relationship scores
- Multiple endings: Romantic Deep, Intellectual Partner, Guardian of Secrets, etc.

**Required Fragments (L6_*):**

1. **L6_FINAL_REVELATION_001** - "Diana Revela el Secreto Final"
   - Speaker: DIANA
   - Emotion: intense_serene
   - Starting: Yes
   - Content: "Todo este tiempo... no solo te he estado evaluando para ver si eres digno de conocerme. También me he estado evaluando a mí misma para ver si soy digna de ser conocida por ti"
   - Key revelation: Diana's vulnerability is about her own worthiness
   - Reward: 40 besitos

2. **L6_SYNTHESIS_002** - "La Síntesis Completa"
   - Speaker: LUCIEN → DIANA
   - Emotion: respectful_collaborative
   - Content: Lucien acknowledges transformation from gatekeeper to witness
   - Key line: "Ha presenciado algo extraordinario. Diana se ha permitido ser vulnerable de maneras que van más allá de la seducción. Ha presenciado... humanidad auténtica"
   - Reward: 30 besitos

3. **L6_ENDING_ROMANTIC_DEEP** - "Final: Conexión Romántica Profunda"
   - Speaker: DIANA
   - Emotion: love_vulnerability
   - Unlock Condition: Archetype = ROMANTIC + DIANA relationship >= 80
   - Content: Diana admits romantic feelings + openness to real connection
   - Key line: "Nunca pensé que permitir que alguien me conociera podría hacerme sentir más yo misma, no menos"
   - Ending: Yes (Romantic Ending)
   - Reward: "Círculo Íntimo de Diana" (ongoing interactions) + 100 besitos + 500 XP

4. **L6_ENDING_INTELLECTUAL_PARTNER** - "Final: Compañero Intelectual"
   - Speaker: DIANA
   - Emotion: deep_respect_trust
   - Unlock Condition: Archetype = ANALYTICAL + comprehension score high
   - Content: Diana values mental connection above all
   - Key line: "Me comprendes de manera que pocos logran. Esa comprensión es más valiosa que la pasión efímera"
   - Ending: Yes (Intellectual Ending)
   - Reward: "Círculo Intelectual de Diana" + 100 besitos + 500 XP

5. **L6_ENDING_EXPLORER_TOGETHER** - "Final: Exploradores Juntos"
   - Speaker: DIANA
   - Emotion: adventurous_connection
   - Unlock Condition: Archetype = EXPLORER + completed all secrets
   - Content: Diana and user as co-explorers of mystery
   - Key line: "Tú y yo, descubriendo juntos lo que significa ser vistos completamente"
   - Ending: Yes (Explorer Ending)
   - Reward: "Círculo de Exploradores" + 100 besitos + 500 XP

6. **L6_ENDING_PERSISTENT_GUARDIAN** - "Final: Guardián de Secretos"
   - Speaker: DIANA
   - Emotion: profound_gratitude
   - Unlock Condition: Archetype = PERSISTENT + relationship with LUCIEN >= 60
   - Content: User becomes guardian, trusted by both Diana and Lucien
   - Key line: "Lucien y yo estamos de acuerdo: eres digno de lo que hemos construido"
   - Ending: Yes (Guardian Ending)
   - Reward: "Guardián de Secretos" title + 100 besitos + 500 XP

7. **L6_ENDING_DIRECT_AUTHENTIC** - "Final: Autenticidad Directa"
   - Speaker: DIANA
   - Emotion: authentic_free
   - Unlock Condition: Archetype = DIRECT + high honesty in profile
   - Content: No games, just authentic connection
   - Key line: "Contigo no necesito los misterios. Puedo ser simplemente... yo"
   - Ending: Yes (Authentic Ending)
   - Reward: "Conexión Auténtica" + 100 besitos + 500 XP

8. **L6_ENDING_PATIENT_ETERNAL** - "Final: Conexión Eterna"
   - Speaker: DIANA
   - Emotion: timeless_connection
   - Unlock Condition: Archetype = PATIENT + took time through all levels
   - Content: Slow-burn connection that transcends time
   - Key line: "Los que saben esperar... al final reciben todo"
   - Ending: Yes (Eternal Ending)
   - Reward: "Conexión Eterna" + 100 besitos + 500 XP

**Key Emotional Beats:**
- **Mystery Complete:** User finally understands Diana completely
- **Reciprocity Acknowledged:** Diana explicitly admits she was evaluating herself too
- **Personalized Payoff:** Ending matches user's archetype + journey
-**Open Door:** All endings include ongoing interaction ("Círculo Íntimo" etc.)

**Premium Differentiators:**
- 6 unique endings based on archetype + relationship scores
- Each ending feels personal and earned
- Diana's most vulnerable content (final revelation)
- Ongoing interaction system post-ending (not just "the end")
- Lucien's character arc complete (gatekeeper → collaborator)
- Sense of complete narrative journey (not cut off)

**Technical Requirements:**
- Complex ending determination algorithm (archetype + relationships + completion)
- "Círculo Íntimo" post-ending interaction system
- Archive of all endings for replayability
- Ending celebration (besitos, XP, special title)

---

## Section 3: Technical Requirements

### New Models/Enhancements Needed

**1. Channel Post Tracking System (Level 2)**
```python
class ChannelPostInteraction(Base):
    """Track user interactions with channel posts for observation challenges"""
    post_id = Column(BigInteger)  # Telegram message ID
    user_id = Column(BigInteger)
    interaction_type = Column(String)  # "reaction", "view", "forward"
    detected_hidden_clue = Column(Boolean, default=False)
    interaction_time = Column(DateTime)
```

**2. User Profile System (Level 3)**
```python
class UserDesireProfile(Base):
    """Store user responses to desire profile questions"""
    user_id = Column(BigInteger, unique=True)
    question_1_response = Column(Text)
    question_2_response = Column(Text)
    # ... 7 questions total
    profile_archetype = Column(String)  # Detected from responses
    profile_depth_score = Column(Integer)  # 0-100 depth
    completed_at = Column(DateTime)
```

**3. Comprehension Quiz System (Level 4)**
```python
class ComprehensionQuiz(Base):
    """Comprehension quiz responses (not factual trivia)"""
    user_id = Column(BigInteger)
    quiz_id = Column(String)
    question_responses = Column(JSON)  # {question_id: response}
    comprehension_score = Column(Integer)  # 0-7 correct
    psychological_insights = Column(JSON)  # Analysis of responses
```

**4. Intimacy Dialogue System (Level 5)**
```python
class IntimacyDialogue(Base):
    """Track intimacy dialogue responses"""
    user_id = Column(BigInteger)
    dialogue_id = Column(String)
    user_response = Column(Text)
    empathy_score = Column(Integer)  # AI-evaluated empathy
    diana_reaction = Column(String)  # "approaches", "distances", "closes"
    relationship_change = Column(Integer)  # Impact on Diana score
```

**5. Ending Archive System (Level 6)**
```python
class EndingArchive(Base):
    """Track which endings user has achieved"""
    user_id = Column(BigInteger)
    ending_type = Column(String)  # "ROMANTIC_DEEP", "INTELLECTUAL_PARTNER", etc.
    achieved_at = Column(DateTime)
    ending_data = Column(JSON)  # Snapshot of archetype, relationships, choices
```

### Service Methods Needed

**NarrativeService Enhancements:**
```python
# Level 2: Channel observation
async def track_channel_post_interaction(user_id, post_id, interaction_type)
async def check_observation_challenge_completion(user_id) -> bool
async def get_hidden_clues_found(user_id) -> List[Clue]

# Level 3: Profile system
async def create_desire_profile(user_id) -> UserDesireProfile
async def submit_profile_answer(user_id, question_num, answer)
async def analyze_profile_archetype(profile) -> str
async def generate_vip_invitation(user_id, profile) -> str

# Level 4: Comprehension
async def create_comprehension_quiz(user_id) -> ComprehensionQuiz
async def submit_comprehension_response(user_id, question_id, response)
async def evaluate_comprehension_depth(responses) -> int

# Level 5: Intimacy dialogues
async def create_intimacy_dialogue(user_id, dialogue_id)
async def process_empathy_response(user_id, response) -> empathy_score
async def update_diana_relationship_based_on_empathy(user_id, score)

# Level 6: Endings
async def determine_ending(user_id) -> str
async def unlock_ending(user_id, ending_type) -> EndingArchive
async def get_ending_celebration_content(ending_type) -> Content
```

### Handler Enhancements

**New Handlers Needed:**
1. **Channel Observation Handler** (Level 2)
   - Track reactions to channel posts
   - Detect hidden clues
   - Notify when challenge complete

2. **Profile Question Handler** (Level 3)
   - FSM for 7-question profile
   - Store responses
   - Generate archetype detection

3. **Comprehension Quiz Handler** (Level 4)
   - Present comprehension questions
   - Evaluate psychological depth
   - Unlock appropriate response variant

4. **Intimacy Dialogue Handler** (Level 5)
   - Present vulnerability dialogues
   - Process empathy responses
   - Update relationship scores

5. **Ending Handler** (Level 6)
   - Determine ending based on journey
   - Present personalized ending
   - Unlock post-ending content

### Database Considerations

**New Tables:**
- channel_post_interactions (Level 2 tracking)
- user_desire_profiles (Level 3 profiles)
- comprehension_quizzes (Level 4 evaluation)
- intimacy_dialogues (Level 5 responses)
- ending_archives (Level 6 endings)

**Indexes Needed:**
- idx_channel_interaction_user_post (user_id, post_id)
- idx_profile_user (user_id)
- idx_quiz_user (user_id, quiz_id)
- idx_dialogue_user (user_id, dialogue_id)
- idx_ending_user_type (user_id, ending_type)

**Data Migration:**
- Add new columns to existing tables if needed
- Ensure backward compatibility with Level 1 data

---

## Section 4: Success Metrics

### Completion Rate Targets

**Free Content (Levels 1-3):**
- Level 1 → Level 2: Target 70% retention
  - Metric: Users who complete L1_FIRST_CLUE and start L2_RETURN_001
  - Current: N/A (Level 2 doesn't exist)
- Level 2 → Level 3: Target 50% retention
  - Metric: Users who complete observation challenge and start profile
- Level 3 → VIP: Target 15-20% conversion
  - Metric: Users who click VIP invitation after L3_INVITATION

**VIP Content (Levels 4-6):**
- Level 4 → Level 5: Target 80% retention
  - Metric: VIP users who complete L4 and start L5
  - Rationale: Already paid, high motivation to continue
- Level 5 → Level 6: Target 90% retention
  - Metric: VIP users who reach final ending
  - Rationale: Maximum investment by this point

### VIP Conversion Targets

**Conversion Funnel:**
```
Total Users (100%)
  ↓ Start Level 1 (80% of users)
  ↓ Complete Level 1 (60% of users who start)
  ↓ Complete Level 2 (40% of Level 1 completers)
  ↓ Complete Level 3 (70% of Level 2 completers)
  ↓ Click VIP Invitation (30% of Level 3 completers)
  ↓ Purchase VIP (50% of invitation clickers)
  = Overall Conversion: 2-3% of total users → VIP
```

**Targets:**
- Month 1 (after L2-L3 launch): 1% conversion
- Month 3: 2% conversion
- Month 6: 3% conversion (optimized based on data)

**Justification:**
- Narrative-driven conversion (not forced)
- Emotional investment creates willingness to pay
- Personalized VIP invitation increases conversion
- Free content delivers value before asking for money

### Emotional Engagement Indicators

**Qualitative Metrics (via user feedback):**
- "I felt like Diana was really talking to ME" (personalization score)
- "I HAD to know what happened next" (curiosity hook score)
- "The ending felt like MY ending" (archetype matching score)
- "I didn't expect to care this much" (emotional impact score)

**Quantitative Metrics:**
- **Re-read Rate:** % of users who replay levels
  - Target: 20% replay at least one level
  - Indicates: Content worth experiencing again
- **Choice Time:** Average time to make choices
  - Target: 30+ seconds for important choices
  - Indicates: Thoughtful engagement (not clicking through)
- **Completion Speed:** Time to complete levels
  - Target: Multi-day engagement (not binge in 1 hour)
  - Indicates: Sustained interest, anticipation
- **Relationship Score Impact:** Diana/Lucien relationship changes
  - Target: 80% of users reach at least "Close Friend" (40+)
  - Indicates: Character investment

### Branching Diversity Metrics

**Archetype Distribution:**
- Target: All 6 archetypes represented in user base
- Target: No single archetype > 30% of users
- Indicates: Choices are genuinely branching, not funneling

**Ending Distribution:**
- Target: All 6 endings achieved by some users
- Target: Most popular ending < 40% (avoiding "one true ending")
- Indicates: Genuine personalization, not illusion of choice

**Choice Distribution:**
- Target: No choice has > 80% selection rate
- Target: At least 3 choices per level have 20-40% selection
- Indicates: Meaningful decisions, not obvious "right" answers

---

## Section 5: Estimated Effort

### Content Creation Time

**Level 2 Content:**
- Fragments: 5 fragments × 200-300 words each = 1,000-1,500 words
- Choices: 3 choices with consequence logic
- Dialogue: Diana (3 variations), Lucien (2 dialogues)
- Images: 1 "Fragmento de Memoria" image
- **Estimated Time:** 20-25 hours (writing + refinement + technical integration)

**Level 3 Content:**
- Fragments: 6 fragments × 300-400 words each = 1,800-2,400 words
- Choices: 3 choices + archetype-based response variants
- Profile: 7 deep psychological questions + response analysis logic
- Dialogue: Diana (4 variations based on archetype)
- Images: None needed (text-heavy psychological content)
- **Estimated Time:** 30-35 hours (writing + refinement + profile system)

**Level 4 Content:**
- Fragments: 5 fragments × 400-500 words each = 2,000-2,500 words
- Choices: 3 choices + comprehension quiz (7 questions)
- Quiz: 7 psychological comprehension questions + scoring system
- Dialogue: Diana (2 variations: high/medium comprehension)
- Images: 1 VIP welcome image
- **Estimated Time:** 35-40 hours (writing + quiz system + VIP validation)

**Level 5 Content:**
- Fragments: 5 fragments × 500-600 words each = 2,500-3,000 words
- Choices: 2 intimacy dialogues + empathy response evaluation
- Dialogue: Diana (vulnerability monologues - highest emotional intensity)
- Images: None needed (emotional connection through text)
- **Estimated Time:** 40-45 hours (writing + empathy system + emotional calibration)

**Level 6 Content:**
- Fragments: 8 endings × 600-800 words each = 4,800-6,400 words
- Choices: Ending determination logic + celebration content
- Dialogue: Diana (6 unique endings) + Lucien (synthesis)
- Images: Optional (ending celebration images if budget allows)
- **Estimated Time:** 50-60 hours (writing + 6 endings + determination algorithm)

**Total Content Creation:** 175-205 hours

### Technical Implementation Time

**Database & Models:**
- New tables: 5 models (interactions, profiles, quizzes, dialogues, endings)
- Migrations: Add indexes, constraints
- Testing: Unit tests for new models
- **Estimated Time:** 15-20 hours

**Service Methods:**
- NarrativeService enhancements: 20+ new methods
- Archetype detection algorithm
- Ending determination algorithm
- Empathy evaluation system
- **Estimated Time:** 30-35 hours

**Handler Development:**
- Channel observation handler
- Profile FSM handler
- Comprehension quiz handler
- Intimacy dialogue handler
- Ending handler
- **Estimated Time:** 25-30 hours

**Integration Testing:**
- End-to-end flow tests (L1 → L6)
- Choice consequence verification
- VIP validation testing
- Cross-level memory testing
- **Estimated Time:** 20-25 hours

**Total Technical Implementation:** 90-110 hours

### Testing Requirements

**Unit Tests:**
- Model tests: 5 new models × 5 tests each = 25 tests
- Service tests: 20 methods × 3 tests each = 60 tests
- Handler tests: 5 handlers × 5 tests each = 25 tests
- **Total:** 110 unit tests

**Integration Tests:**
- Level flow tests: 6 levels × 3 paths each = 18 tests
- Cross-level memory tests: 5 tests
- Archetype detection tests: 6 archetypes × 2 = 12 tests
- Ending determination tests: 6 endings × 2 = 12 tests
- **Total:** 47 integration tests

**E2E Tests:**
- Complete user journeys: 6 archetype journeys × 1 = 6 tests
- VIP conversion flow: 3 tests
- Error recovery: 5 tests
- **Total:** 14 E2E tests

**Total Testing:** 171 tests
**Estimated Time:** 40-50 hours (writing + execution + debugging)

### Total Effort Summary

| Component | Time (hours) |
|-----------|--------------|
| Content Creation (L2-L6) | 175-205 |
| Technical Implementation | 90-110 |
| Testing | 40-50 |
| **Total** | **305-365 hours** |

**Timeline (assuming 1 person, part-time ~20 hours/week):**
- **Optimistic:** 15 weeks (~3.5 months)
- **Realistic:** 18 weeks (~4.5 months)
- **Conservative:** 22 weeks (~5.5 months)

**Team Acceleration (if multiple people):**
- 2 people (content + technical): 10-12 weeks
- 3 people (content + backend + frontend): 8-10 weeks

### Risk Assessment

**High Risk Items:**
1. **Content Quality Consistency**
   - Risk: Diana's voice may drift across 5 levels
   - Mitigation: Create voice guidelines document, review all content together
   - Probability: Medium | Impact: High

2. **Archetype Detection Accuracy**
   - Risk: Algorithm misclassifies users, breaks immersion
   - Mitigation: Extensive testing, fallback to manual selection
   - Probability: Medium | Impact: Medium

3. **VIP Conversion Rate**
   - Risk: Users complete free content but don't convert to VIP
   - Mitigation: A/B test pricing, optimize L3 invitation, add mid-level teasers
   - Probability: Low | Impact: High

4. **Technical Complexity (Cross-Level Memory)**
   - Risk: References to L1 choices in L4-6 break if user revisits L1
   - Mitigation: Immutable choice history, snapshot system
   - Probability: Low | Impact: Medium

**Medium Risk Items:**
1. **Ending Determination Logic**
   - Risk: Users feel funneled into "wrong" ending
   - Mitigation: Transparent ending criteria, offer ending re-selection
   - Probability: Medium | Impact: Medium

2. **Empathy Response Evaluation**
   - Risk: AI evaluation feels arbitrary or unfair
   - Mitigation: Human-reviewed response patterns, clear feedback
   - Probability: Medium | Impact: Medium

3. **Channel Observation Challenge (Level 2)**
   - Risk: Users can't find hidden clues, abandon narrative
   - Mitigation: Hint system, progressive difficulty, alternative paths
   - Probability: Medium | Impact: Medium

**Low Risk Items:**
1. **Database Performance**
   - Risk: Query slowdown with complex relationships
   - Mitigation: Proper indexing, query optimization, caching
   - Probability: Low | Impact: Low

2. **Handler Conflicts**
   - Risk: New handlers conflict with existing /story command
   - Mitigation: Clear handler separation, comprehensive testing
   - Probability: Low | Impact: Low

---

## Section 6: Recommendation

### Strategic Decision: Complete Free Content First (Levels 2-3)

**Recommended Path: Option A - Levels 2-3 First (Free Content Expansion)**

**Justification:**

**1. Build User Base Before Monetization**
- Current state: 5-minute taste with no journey completion = low retention
- With Levels 2-3: 30-45 minute complete free journey = higher investment
- Free content acts as marketing for VIP (users experience value before paying)
- Viral potential: Users share "complete this story, it's amazing" vs "it's unfinished"

**2. Prove Content Quality Before Premium Ask**
- Users won't pay for VIP if they don't trust quality
- Levels 2-3 demonstrate: story consistency, character development, emotional payoff
- Free journey creates confidence: "If L1-L3 are this good, L4-L6 must be incredible"
- Current state: No proof of quality beyond initial hook

**3. Optimize Conversion Funnel**
- Level 3's "Perfil de Deseo" creates emotional investment right before price reveal
- Personalized VIP invitation based on profile increases conversion
- Natural upsell: "I just poured my heart into this profile, Diana wants to know me, now I pay?"
- Current state: No emotional hook before VIP ask

**4. Reduce Technical Risk**
- Levels 2-3 less technically complex (no VIP validation, no ending system)
- Can test archetype detection, cross-level memory in simpler context first
- Learn from user behavior patterns before implementing complex L4-L6 systems
- Current state: Blind leap into complex VIP systems

**5. Faster Time to Market**
- Levels 2-3: 8-10 weeks (content + technical)
- Levels 4-6: 20-25 weeks (content + technical)
- Strategy: Ship L2-L3, gather data, iterate L4-L6 based on real usage
- Current state: All-or-nothing approach delays any content delivery

**6. Emotional Narrative Structure**
- L1: Hook (✅ done)
- L2-L3: Deepening + Investment (❌ missing)
- L4-L6: Payoff (❌ missing)
- Complete arc: Hook → Investment → Payoff
- Current state: Hook → [NOTHING] → Payoff (broken emotional arc)

**Economic Rationale:**

**Current State (Level 1 only):**
- User journey: 5 minutes
- Emotional investment: Low (curiosity only)
- VIP conversion: < 1% (no reason to pay)
- Viral sharing: Low ("it's just a bot demo")

**With Levels 2-3 Complete:**
- User journey: 30-45 minutes
- Emotional investment: High (completed profile, Diana knows them)
- VIP conversion: 2-3% (personalized invitation + proven quality)
- Viral sharing: High ("finish this free story, you'll be hooked")

**Revenue Projection (Conservative):**
- 10,000 users start L1
- 7,000 (70%) complete L1
- 2,800 (40% of completers) complete L2
- 1,960 (70% of L2 completers) complete L3
- 39 (2% of L3 completers) convert to VIP at $10/month
- **Monthly recurring revenue: $390** (from single cohort)
- **6-month cumulative (6 cohorts): $2,340/month**

**With All Levels 1-6 Complete:**
- Same 10,000 users start
- Higher completion rates (full journey available)
- VIP conversion: 3-4% (full story, proven quality, endings visible)
- 78 users (4% of L3 completers) × $10 = $780/month
- **6-month cumulative: $4,680/month**

**Conclusion:** Completing Levels 2-3 first builds foundation for higher long-term revenue.

### Implementation Roadmap (Option A)

**Phase 1: Foundation (Weeks 1-2)**
- Create voice guidelines document (Diana/Lucien consistency)
- Design Level 2 observation challenge mechanics
- Implement channel post tracking system
- Create UserDesireProfile model
- Unit tests for new models

**Phase 2: Level 2 Content (Weeks 3-6)**
- Write 5 Level 2 fragments
- Create 3 Level 2 choices
- Design hidden clues in channel posts
- Implement observation challenge handler
- Test Level 2 flow end-to-end
- **Deliverable:** Level 2 fully functional

**Phase 3: Level 3 Content (Weeks 7-10)**
- Write 6 Level 3 fragments
- Create 7-question profile system
- Implement archetype detection algorithm
- Create profile FSM handler
- Design personalized VIP invitations
- Test Level 3 flow end-to-end
- **Deliverable:** Level 3 fully functional + VIP conversion funnel

**Phase 4: Integration & Optimization (Weeks 11-12)**
- Test complete L1-L3 flow
- Optimize archetype detection accuracy
- A/B test VIP invitation language
- Fix bugs, refine content based on testing
- **Deliverable:** Production-ready L1-L3 narrative

**Phase 5: Launch & Monitoring (Week 13+)**
- Deploy Levels 2-3 to production
- Monitor metrics: completion rates, conversion, archetype distribution
- Gather user feedback
- **Deliverable:** Live data to inform L4-L6 development

**Success Criteria for Phase 5:**
- L1 → L2 retention: > 60%
- L2 → L3 retention: > 40%
- L3 → VIP conversion: > 1.5%
- User feedback: "I want more" sentiment > 80%

**If Success Criteria Met:** Proceed to Levels 4-6 development
**If Not:** Iterate on L2-L3 based on data before building VIP content

### Alternative Path Considerations

**Option B: Levels 4-6 First (VIP Premium Content)**
- ✅ Immediate monetization potential
- ❌ Weak free content = low user base to convert
- ❌ No emotional investment built before paywall
- ❌ Higher risk (building premium without proven demand)
- **Verdict:** Not recommended (build demand before supply)

**Option C: All Levels 2-6 Simultaneously**
- ✅ Complete narrative vision delivered at once
- ✅ Maximum user journey from day one
- ❌ 22-week delay before ANY new content
- ❌ Can't iterate based on real user data
- ❌ All-or-nothing risk (if content misses mark, entire effort wasted)
- **Verdict:** Not recommended (iterate quickly, don't boil ocean)

---

## Conclusion

**Current State:** Technically excellent foundation, emotionally incomplete narrative

**Critical Gap:** 83% of narrative content missing (Levels 2-6)

**Recommended Action:** Complete Levels 2-3 (Free Content) first

**Timeline:** 12-13 weeks to production-ready L1-L3

**Expected Outcome:**
- 30-45 minute complete free narrative journey
- 2-3% VIP conversion rate (personalized invitations)
- Proven content quality to justify VIP premium
- Data-driven insights for L4-L6 development

**Long-Term Vision:**
After Levels 2-3 proven successful, complete Levels 4-6 (20-25 weeks) to deliver full 6-level narrative arc with archetype-based endings, creating a sustainable narrative-gamification product with recurring revenue potential.

**The question isn't whether to complete the narrative—the technical foundation and creative vision demand it. The question is whether to build the audience first (Option A) or build the premium content first (Option B). The data and user psychology strongly suggest: build audience, then monetize.**

---

**Next Steps:**
1. Review this PRD with creative team
2. Confirm Level 2-3 creative direction
3. Allocate resources (content writer + developer)
4. Begin Phase 1: Foundation (voice guidelines, technical design)
5. Ship Level 2 by Week 6, Level 3 by Week 10
6. Measure, learn, iterate, then build Levels 4-6

**The narrative journey awaits. Let's complete it.**
