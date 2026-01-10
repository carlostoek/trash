# DianaBot Narrative Module - Developer Quick Reference

## 🚀 Quick Start

### 1. Database Models (8 Total)

```
StoryFragment         → Narrative content pieces
StoryChoice           → User decisions that branch story
UserNarrativeProgress → Track user's journey through 6 levels
UserChoice            → Record every decision for analysis
NarrativeFlag         → Persistent state for conditional logic
ArchetypeProfile      → Behavioral detection (6 personality types)
CharacterRelationship → Relationship scores with Diana/Lucien
NarrativeUnlock       → Track content unlocks and achievements
```

### 2. Services (5 Total)

```
FlagService                → Flag management (get, set, clear, has)
ArchetypeService           → Personality detection and tracking
CharacterRelationshipService → Relationship score management
NarrativeService           → Core narrative flow (fragments, progression)
StoryEngine                → Coordinator (composes all services)
```

### 3. Key Integration Points

```python
# VIP Check (Levels 4-6)
if fragment.narrative_level >= 4:
    is_vip = await subscription_service.is_vip_active(user_id)

# Gamification Rewards
await gamification.add_besitos(user_id, amount, reason="narrative")
await gamification.unlock_mission(user_id, mission_id)

# Inventory Checks
required_items = fragment.unlock_conditions.get("required_items", [])
user_inventory = await gamification.get_user_inventory(user_id)
```

---

## 📊 Data Model Relationships

```
User (1:1) ←→ UserNarrativeProgress
User (1:N) ←→ UserChoice
User (1:1) ←→ ArchetypeProfile
User (1:N) ←→ CharacterRelationship
User (1:N) ←→ NarrativeFlag

StoryFragment (1:N) ←→ StoryChoice
StoryChoice → StoryFragment (target)
StoryFragment → Mission (unlocks)
StoryFragment → Reward (unlocks)

UserChoice (N:1) ←→ StoryChoice
```

---

## 🎯 Fragment ID Convention

```
L{N}_{TYPE}_{NUMBER}

Examples:
L1_INTRO_001    → Level 1, Introduction, fragment 1
L1_KINKY_015    → Level 1, Los Kinkys, fragment 15
L4_DIVAN_003    → Level 4, El Diván, fragment 3
L6_FINAL_001    → Level 6, Final ending, fragment 1
```

---

## 🎭 Character Voices

### Diana
- **Emotions:** mysterious, vulnerable, intimate, playful
- **Score Effect:** Positive choices increase relationship
- **Content:** Emotional, sensory, psychological
- **Unlocks:** Higher levels reveal deeper vulnerability

### Lucien
- **Emotions:** formal, skeptical, approving, protective
- **Score Effect:** Evaluates user worthiness
- **Content:** Analytical, challenging, evaluative
- **Unlocks:** Higher approval = insider knowledge

---

## 🧠 Archetypes (6 Types)

```python
ARCHETYPES = {
    "EXPLORER": "Le gusta descubrir, explorar todas las opciones",
    "DIRECT": "Toma decisiones rápidas, va al grano",
    "ROMANTIC": "Busca conexiones emocionales",
    "ANALYTICAL": "Piensa mucho, elige lógica",
    "PERSISTENT": "No se rinde, reintenta caminos",
    "PATIENT": "Toma su tiempo, lee todo"
}

# Detection Metrics:
# - Choice time < 10s → Direct
# - Choice time > 30s → Patient
# - Reread fragment → Explorer/Analytical
# - Romantic choices → Romantic
# - Retry failed paths → Persistent
```

---

## 🔐 VIP Gating Logic

```python
# Levels 1-3: Free (acceso libre)
if fragment.narrative_level <= 3:
    return True, ""  # Access granted

# Levels 4-6: VIP (requiere suscripción)
if fragment.narrative_level >= 4:
    is_vip = await subscription_service.is_vip_active(user_id)
    if not is_vip:
        return False, "🔒 Este contenido requiere suscripción VIP"
```

---

## 🎮 Consequence System

### Choice Consequences Structure

```python
consequences = {
    # Narrative State
    "flags_set": ["met_diana", "chose_romantic_path"],
    "flags_unset": ["first_interaction"],

    # Personality Detection
    "archetype_points": {
        "romantic": +2,
        "direct": -1
    },

    # Character Relationships
    "relationship_change": {
        "DIANA": +5,
        "LUCIEN": -2
    },

    # Gamification
    "besitos_reward": 50,
    "items_gained": ["pista_1_mapa"],
    "items_lost": ["intro_map"],
    "mission_unlocked": 15
}
```

---

## 📋 Typical Handler Flow

```python
@narrative_router.message(Command("story"))
async def cmd_start_story(message: Message, story_engine: StoryEngine):
    """Start or continue narrative"""
    # 1. Get current story state
    state = await story_engine.get_current_story_state(message.from_user.id)

    # 2. Check if can continue
    if not state["can_continue"]:
        await message.answer(state["unlock_message"])
        return

    # 3. Format fragment content
    fragment = state["current_fragment"]
    content = await format_fragment_for_user(
        fragment=fragment,
        archetype=state["archetype"].primary_archetype
    )

    # 4. Create choice keyboard
    choices = state["available_choices"]
    keyboard = create_narrative_keyboard(choices)

    # 5. Send message
    await message.answer(content, reply_markup=keyboard)
```

---

## 🎨 Content Personalization

### Archetype-Based Variants

```python
# In StoryFragment model
content_variants = {
    "EXPLORER": "Como alguien que busca cada detalle...",
    "ROMANTIC": "Hay una poesía en tu forma de aproximarte...",
    "DIRECT": "Me gusta tu honestidad sin filtros...",
    "ANALYTICAL": "Tu análisis revela una mente aguda...",
    "PERSISTENT": "Tu persistencia es admirable...",
    "PATIENT": "Tu paciencia es más seductora de lo que imaginas..."
}

# Retrieval logic
variant = fragment.content_variants.get(user_archetype)
content = variant if variant else fragment.content_text
```

### Relationship-Based Variants

```python
# Lucien based on relationship score
if relationship_score >= 60:
    dialogue = "Entre nosotros... Diana encuentra en usted algo especial."
elif relationship_score >= 40:
    dialogue = "Debo admitir... su desempeño ha mejorado."
else:
    dialogue = "Si me permite observar... su respuesta es reveladora."
```

---

## 🔧 Common Tasks

### Create a New Fragment

```python
fragment = StoryFragment(
    fragment_id="L1_INTRO_001",
    narrative_level=1,
    title="Bienvenida a Los Kinkys",
    content_text="Bienvenido...",
    speaker="DIANA",
    speaker_emotion="mysterious",
    is_starting_fragment=True,
    besitos_reward=10,
    active=True,
    sort_order=1
)
session.add(fragment)
await session.commit()
```

### Create a Choice

```python
choice = StoryChoice(
    choice_id="L1_INTRO_A",
    fragment_id=fragment_id,
    choice_text="🚪 Descubrir más",
    target_fragment_id=next_fragment_id,
    consequences={
        "flags_set": ["met_diana"],
        "archetype_points": {"direct": +2},
        "relationship_change": {"DIANA": +2},
        "besitos_reward": 5
    },
    sort_order=1,
    active=True
)
session.add(choice)
await session.commit()
```

### Check User Progress

```python
progress = await narrative_service.get_or_create_user_progress(user_id)

# Get completion percentage
completion_pct = progress.completion_percentage  # 0.0 to 100.0

# Check if completed level 1
if 1 in progress.levels_completed:
    print("User completed level 1")

# Check current level
current_level = progress.current_narrative_level
max_level = progress.max_narrative_level_reached
```

### Set a Flag

```python
await flag_service.set_flag(
    user_id=12345,
    flag_key="met_diana",
    flag_value="true",
    expires_at=None  # Permanent flag
)

# Temporary flag (24 hours)
from datetime import timedelta
expires = datetime.utcnow() + timedelta(hours=24)
await flag_service.set_flag(
    user_id=12345,
    flag_key="temporary_boost",
    flag_value="active",
    expires_at=expires
)
```

### Update Relationship

```python
await relationship_service.update_relationship_score(
    user_id=12345,
    character_name="DIANA",
    score_change=+5  # -100 to +100 range
)
```

---

## 🧪 Testing Snippets

### Test Fragment Access

```python
async def test_vip_access():
    fragment = StoryFragment(narrative_level=4)  # VIP level
    can_access, reason = await narrative_service.can_access_fragment(
        user_id=free_user_id,
        fragment=fragment,
        user_flags=[]
    )
    assert can_access is False
    assert "VIP" in reason
```

### Test Choice Processing

```python
async def test_choice_consequences():
    success, msg, next_frag, consequences = await narrative_service.advance_to_next_fragment(
        user_id=12345,
        choice_id="L1_INTRO_A"
    )
    assert success is True
    assert "flags_set" in consequences
    assert "met_diana" in consequences["flags_set"]
```

### Test Archetype Detection

```python
async def test_archetype_from_timing():
    # Fast choice = Direct
    await archetype_service.record_choice_timing(user_id=12345, choice_time_seconds=5)
    profile = await archetype_service.get_or_create_archetype_profile(12345)
    assert profile.primary_archetype == "DIRECT"

    # Slow choice = Patient
    await archetype_service.record_choice_timing(user_id=67890, choice_time_seconds=45)
    profile = await archetype_service.get_or_create_archetype_profile(67890)
    assert profile.primary_archetype == "PATIENT"
```

---

## 📈 Performance Tips

### 1. Use Eager Loading
```python
# BAD (N+1 query)
fragments = session.query(StoryFragment).all()
for frag in fragments:
    print(frag.choices)  # N+1 query!

# GOOD (eager load)
fragments = session.query(StoryFragment).options(
    selectinload(StoryFragment.choices)
).all()
```

### 2. Index Queries
```python
# GOOD (uses index)
frag = session.query(StoryFragment).filter(
    StoryFragment.fragment_id == "L1_INTRO_001"
).first()

# GOOD (compound index)
progress = session.query(UserNarrativeProgress).filter(
    UserNarrativeProgress.user_id == 12345
).first()
```

### 3. Batch Operations
```python
# GOOD (single transaction)
async with session.begin():
    session.add_all([fragment1, fragment2, fragment3])
    # Auto-commits at end
```

---

## 🐛 Common Issues

### Issue: User can't access VIP content
**Solution:** Check VIP subscription
```python
is_vip = await subscription_service.is_vip_active(user_id)
if not is_vip:
    # User needs VIP subscription
```

### Issue: Choices not showing
**Solution:** Check display_requirements
```python
# Verify user has required flags
has_flag = await flag_service.has_flag(user_id, "required_flag")
# Verify user meets level requirement
if choice.display_requirements.get("min_level", 0) > user_level:
    # Choice hidden
```

### Issue: Wrong archetype detected
**Solution:** Insufficient data points
```python
profile = await archetype_service.get_or_create_archetype_profile(user_id)
if profile.archetype_confidence < 50:
    # Need more choices for accurate detection
```

### Issue: Relationship score not updating
**Solution:** Check score bounds
```python
# Score is bounded to -100/+100
relationship_score = max(-100, min(100, new_score))
```

---

## 📚 Related Files

```
bot/database/models.py           → Add 8 narrative models
bot/services/narrative.py        → Already exists, needs model updates
bot/handlers/user/narrative.py   → User narrative handlers
bot/handlers/admin/narrative.py  → Admin content tools
bot/states/narrative.py          → FSM states
migrations/add_narrative.py      → Database migration
seeds/seed_narrative.py          → Initial content
tests/test_narrative.py          → Test suite
```

---

## 🎓 Learning Resources

### Narrative Design
- Read `docs/concepto.md` for ecosystem overview
- Read `docs/lucien.md` for character voice guidelines
- Read `docs/narrativo.md` for story structure

### Technical Implementation
- Read `docs/NARRATIVE_TECHNICAL_SPEC.md` for complete spec
- Read `docs/Referencia_Rápida.md` for codebase conventions
- Review existing services for patterns

### Testing
- Review `tests/` for existing test patterns
- Check `bot/services/narrative.py` for service tests
- Use pytest + pytest-asyncio

---

## 🚦 Implementation Checklist

### Phase 1: Foundation
- [ ] Add 8 models to `bot/database/models.py`
- [ ] Create migration script
- [ ] Run migration and verify tables
- [ ] Create seed script for initial content

### Phase 2: Services
- [ ] Implement FlagService (if not complete)
- [ ] Implement ArchetypeService (if not complete)
- [ ] Implement CharacterRelationshipService (if not complete)
- [ ] Verify NarrativeService works with new models
- [ ] Test StoryEngine coordination

### Phase 3: Handlers
- [ ] Create `/story` command handler
- [ ] Implement choice callback handler
- [ ] Create narrative keyboard factory
- [ ] Add FSM states for user flow
- [ ] Test complete user journey

### Phase 4: Admin
- [ ] Create fragment wizard
- [ ] Create choice wizard
- [ ] Implement preview function
- [ ] Add admin menu integration
- [ ] Test content creation flow

### Phase 5: Integration
- [ ] Integrate VIP checks
- [ ] Integrate gamification rewards
- [ ] Integrate inventory system
- [ ] Update ServiceContainer
- [ ] Test all integrations

### Phase 6: Testing
- [ ] Write unit tests (80% coverage)
- [ ] Write integration tests
- [ ] Write E2E tests
- [ ] Performance test
- [ ] Fix bugs

### Phase 7: Content
- [ ] Write level 1 fragments (5-10)
- [ ] Write level 1 choices
- [ ] Write level 2 fragments (5-10)
- [ ] Write level 3 fragments (5-10)
- [ ] Write level 4-6 fragments (VIP)

---

## 💡 Best Practices

### 1. Always Use Transactions
```python
async with session.begin():
    # Multiple operations
    session.add(fragment)
    session.add(choice)
    # Auto-commits if no exception
```

### 2. Validate Input Early
```python
if fragment.narrative_level < 1 or fragment.narrative_level > 6:
    raise ValueError("narrative_level must be 1-6")
```

### 3. Log Important Events
```python
logger.info(f"User {user_id} advanced to fragment {next_fragment.fragment_id}")
logger.debug(f"Applied consequences: {consequences}")
```

### 4. Handle Errors Gracefully
```python
try:
    state = await story_engine.get_current_story_state(user_id)
except Exception as e:
    logger.error(f"Error getting story state: {e}")
    await message.answer("❌ Error loading story. Please try again.")
```

### 5. Use Type Hints
```python
async def get_fragment(self, fragment_id: str) -> Optional[StoryFragment]:
    """Clear return type for better IDE support"""
```

---

## 🎯 Success Metrics

### Technical
- [ ] Response time < 300ms
- [ ] Error rate < 0.1%
- [ ] Test coverage > 80%
- [ ] Zero N+1 queries

### User Engagement
- [ ] Level 1 completion > 60%
- [ ] VIP conversion > 15%
- [ ] 24h retention > 40%
- [ ] Avg session > 5min

### Creative
- [ ] Archetype accuracy > 70%
- [ ] Character voice consistency
- [ ] Emotional resonance high
- [ ] Content replay value

---

**Need Help?**
- Check `docs/NARRATIVE_TECHNICAL_SPEC.md` for detailed specs
- Review `docs/NARRATIVE_TRANSLATION_SUMMARY.md` for design rationale
- Ask questions in team chat
- Create GitHub issues for bugs
