# DianaBot Narrative Module - Architecture Diagrams

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         DIANABOT ECOSYSTEM                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  NARRATIVE   │  │ GAMIFICATION │  │   CHANNELS   │          │
│  │   MODULE     │  │   MODULE     │  │   MODULE     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                 │                 │                    │
│         └─────────────────┴─────────────────┘                    │
│                           │                                       │
│                   ┌───────▼───────┐                              │
│                   │  CORE SYSTEM  │                              │
│                   │   (User DB)   │                              │
│                   └───────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Narrative Module Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      NARRATIVE MODULE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    STORY ENGINE                          │    │
│  │  (Coordinator - Composes all services)                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                     │
│         ┌─────────────────┼─────────────────┐                 │
│         │                 │                 │                 │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐          │
│  │  NARRATIVE   │  │   ARCHETYPE │  │   CHARACTER │          │
│  │   SERVICE    │  │   SERVICE   │  │  RELATION   │          │
│  │              │  │             │  │   SERVICE   │          │
│  │ - Fragments  │  │ - Detect    │  │ - Scores    │          │
│  │ - Progress   │  │ - Track     │  │ - Milestones│          │
│  │ - Choices    │  │ - Personalize│  │ - History  │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                 │
│         └─────────────────┼─────────────────┘                 │
│                           │                                     │
│                   ┌───────▼───────┐                            │
│                   │  FLAG SERVICE │                            │
│                   │ - Set/Get     │                            │
│                   │ - Has/Clear   │                            │
│                   │ - Expire      │                            │
│                   └───────┬───────┘                            │
│                           │                                     │
└───────────────────────────┼─────────────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │  DATABASE (8   │
                    │    TABLES)     │
                    └────────────────┘
```

---

## Data Model Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                      DATA MODEL RELATIONS                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│   ┌─────────┐                                                    │
│   │  USER   │                                                    │
│   └────┬────┘                                                    │
│        │                                                         │
│        ├──(1:1)──→ USER_NARRATIVE_PROGRESS                       │
│        │            ├─ current_fragment_id                       │
│        │            ├─ current_level (1-6)                       │
│        │            ├─ levels_completed                          │
│        │            └─ fragments_completed                       │
│        │                                                          │
│        ├──(1:N)──→ USER_CHOICE                                   │
│        │            ├─ choice_id                                 │
│        │            ├─ choice_time_seconds                       │
│        │            └─ consequences_applied                      │
│        │                                                          │
│        ├──(1:1)──→ ARCHETYPE_PROFILE                             │
│        │            ├─ primary_archetype (6 types)               │
│        │            ├─ archetype_points (JSON)                   │
│        │            └─ archetype_confidence (0-100)              │
│        │                                                          │
│        ├──(1:N)──→ CHARACTER_RELATIONSHIP                        │
│        │            ├─ character_name (LUCIEN/DIANA)             │
│        │            ├─ relationship_score (-100 to +100)         │
│        │            └─ relationship_status                       │
│        │                                                          │
│        └──(1:N)──→ NARRATIVE_FLAG                                │
│                     ├─ flag_key                                  │
│                     ├─ flag_value                                │
│                     └─ expires_at                                │
│                                                                   │
│   ┌──────────────┐        ┌──────────────┐                      │
│   │STORY_FRAGMENT│◄───────┤STORY_CHOICE  │                      │
│   ├─ fragment_id│  (1:N)  ├─ choice_id   │                      │
│   ├─ level(1-6) │        ├─ target_fragment_id                 │
│   ├─ speaker    │        ├─ consequences (JSON)                 │
│   ├─ content    │        └─ display_requirements (JSON)         │
│   ├─ variants   │                                                    │
│   └─ rewards    │                                                    │
│   └──────┬───────┘                                                    │
│          │                                                            │
│          ├──(unlocks)──→ MISSION                                      │
│          └──(unlocks)──→ REWARD                                      │
│                                                                   │
│   ┌──────────────┐                                                    │
│   │NARRATIVE_    │                                                    │
│   │UNLOCK        │                                                    │
│   ├─ unlock_type │                                                    │
│   ├─ unlock_id   │                                                    │
│   └─ unlock_method│                                                   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## User Journey Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER NARRATIVE JOURNEY                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  START                                                            │
│   │                                                               │
│   ├─ /story command                                              │
│   │                                                               │
│   ▼                                                               │
│  ┌─────────────────┐                                             │
│  │ StoryEngine.    │                                             │
│  │ get_current_    │                                             │
│  │ story_state()   │                                             │
│  └────────┬────────┘                                             │
│           │                                                       │
│           ├─→ Get user progress                                  │
│           ├─→ Get current fragment                               │
│           ├─→ Check VIP access (levels 4-6)                      │
│           ├─→ Get available choices                              │
│           ├─→ Load user flags                                    │
│           ├─→ Load archetype profile                             │
│           └─→ Load relationships                                 │
│           │                                                       │
│           ▼                                                       │
│  ┌─────────────────┐                                             │
│  │ Display Fragment│                                             │
│  │ + Choices       │                                             │
│  └────────┬────────┘                                             │
│           │                                                       │
│           ├─→ Personalize content by archetype                   │
│           ├─→ Adapt dialogue by relationship score               │
│           └─→ Filter choices by requirements                     │
│           │                                                       │
│           ▼                                                       │
│  ┌─────────────────┐                                             │
│  │ User Makes      │                                             │
│  │ Choice          │                                             │
│  └────────┬────────┘                                             │
│           │                                                       │
│           ├─→ Record choice time (archetype detection)           │
│           │                                                       │
│           ▼                                                       │
│  ┌─────────────────┐                                             │
│  │ Process Choice  │                                             │
│  │ Consequences    │                                             │
│  └────────┬────────┘                                             │
│           │                                                       │
│           ├─→ Set/unset flags                                    │
│           ├─→ Add archetype points                               │
│           ├─→ Update relationships                               │
│           ├─→ Grant besitos (gamification)                       │
│           ├─→ Unlock missions (gamification)                     │
│           ├─→ Update progress                                    │
│           └─→ Move to next fragment                              │
│           │                                                       │
│           ▼                                                       │
│  ┌─────────────────┐                                             │
│  │ Display Next    │                                             │
│  │ Fragment        │                                             │
│  └────────┬────────┘                                             │
│           │                                                       │
│           └─→ Repeat until ending fragment                       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## VIP Access Control Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    VIP ACCESS CONTROL                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  User Requests Fragment                                          │
│   │                                                               │
│   ▼                                                               │
│  ┌─────────────────────────────────────┐                         │
│  │ Check fragment.narrative_level      │                         │
│  └────────┬────────────────────────────┘                         │
│           │                                                         │
│           ├─→ Level 1-3? ──→ ALLOW (Free content)                │
│           │                                                         │
│           └─→ Level 4-6?                                          │
│                      │                                            │
│                      ▼                                            │
│           ┌─────────────────────────────────────┐                 │
│           │ Check subscription_service          │                 │
│           │ .is_vip_active(user_id)             │                 │
│           └────────┬────────────────────────────┘                 │
│                    │                                               │
│                    ├─→ True?  ──→ ALLOW (VIP content)            │
│                    │                                               │
│                    └─→ False? ──→ DENY                           │
│                                        │                          │
│                                        ▼                          │
│                              Return error message:                │
│                              "🔒 Este contenido requiere          │
│                               suscripción VIP"                    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Archetype Detection Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                 ARCHETYPE DETECTION SYSTEM                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  User Makes Choice                                               │
│   │                                                               │
│   ▼                                                               │
│  ┌─────────────────────────────────────┐                         │
│  │ Measure choice_time_seconds         │                         │
│  └────────┬────────────────────────────┘                         │
│           │                                                         │
│           ├─→ < 10s  ──→ Add +1 DIRECT point                     │
│           ├─→ > 30s  ──→ Add +1 PATIENT point                    │
│           └─→ 10-30s → No timing points                          │
│                                                                   │
│  User Rereads Fragment                                           │
│   │                                                               │
│   ▼                                                               │
│  ┌─────────────────────────────────────┐                         │
│  │ Record reread                       │                         │
│  └────────┬────────────────────────────┘                         │
│           │                                                         │
│           └─→ Add +1 EXPLORER point                               │
│              Add +1 ANALYTICAL point                              │
│                                                                   │
│  User Selects Choice                                             │
│   │                                                               │
│   ▼                                                               │
│  ┌─────────────────────────────────────┐                         │
│  │ Apply choice.consequences           │                         │
│  │ .archetype_points                   │                         │
│  └────────┬────────────────────────────┘                         │
│           │                                                         │
│           └─→ Add points from choice (e.g., +2 ROMANTIC)         │
│                                                                   │
│  Calculate Archetype                                             │
│   │                                                               │
│   ▼                                                               │
│  ┌─────────────────────────────────────┐                         │
│  │ Find archetype with MAX points      │                         │
│  │ Calculate confidence from spread    │                         │
│  │ Identify secondary archetype        │                         │
│  └────────┬────────────────────────────┘                         │
│           │                                                         │
│           ▼                                                       │
│  ┌─────────────────────────────────────┐                         │
│  │ Store in ArchetypeProfile           │                         │
│  │ - primary_archetype                 │                         │
│  │ - secondary_archetype               │                         │
│  │ - archetype_confidence (0-100)      │                         │
│  └─────────────────────────────────────┘                         │
│                                                                   │
│  Personalize Future Content                                      │
│   │                                                               │
│   ▼                                                               │
│  ┌─────────────────────────────────────┐                         │
│  │ Use fragment.content_variants       │                         │
│  │ [primary_archetype]                 │                         │
│  └─────────────────────────────────────┘                         │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Relationship Evolution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              CHARACTER RELATIONSHIP EVOLUTION                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Score Range: -100 ──────────────── 0 ───────────────── +100     │
│                │                     │                      │       │
│           Hostile                 Neutral           Deep Intimacy │
│                                                                   │
│  User Makes Choice About Character                               │
│   │                                                               │
│   ▼                                                               │
│  ┌─────────────────────────────────────┐                         │
│  │ Get choice.consequences             │                         │
│  │ .relationship_change[character]     │                         │
│  └────────┬────────────────────────────┘                         │
│           │                                                         │
│           │ Example: {"DIANA": +5, "LUCIEN": -2}                 │
│           │                                                         │
│           ▼                                                       │
│  ┌─────────────────────────────────────┐                         │
│  │ Update character.score              │                         │
│  │ Bound to -100/+100 range            │                         │
│  └────────┬────────────────────────────┘                         │
│           │                                                         │
│           ▼                                                       │
│  ┌─────────────────────────────────────┐                         │
│  │ Check milestones                    │                         │
│  │ - score >= 40? → Close Friend       │                         │
│  │ - score >= 60? → Romantic Interest  │                         │
│  │ - score >= 80? → Deep Intimacy      │                         │
│  └────────┬────────────────────────────┘                         │
│           │                                                         │
│           ▼                                                       │
│  ┌─────────────────────────────────────┐                         │
│  │ Update relationship_status property │                         │
│  │ Store milestone timestamps          │                         │
│  └────────┬────────────────────────────┘                         │
│           │                                                         │
│           ▼                                                       │
│  Affect Future Content                                          │
│   │                                                               │
│   ├─→ Unlock dialogue variants                                   │
│   ├─→ Enable special choices                                     │
│   ├─→ Modify character voice                                     │
│   └─→ Affect narrative endings                                   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Content Unlock Conditions

```
┌─────────────────────────────────────────────────────────────────┐
│              CONTENT UNLOCK CHECKING SYSTEM                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  User Attempts to Access Fragment                                │
│   │                                                               │
│   ▼                                                               │
│  ┌─────────────────────────────────────┐                         │
│  │ Check fragment.unlock_conditions    │                         │
│  └────────┬────────────────────────────┘                         │
│           │                                                         │
│           ├─→ None? ──────────────────→ ALLOW                    │
│           │                                                         │
│           └─→ Has conditions?                                     │
│                      │                                            │
│                      ▼                                            │
│           ┌─────────────────────────────────────┐                 │
│           │ Check required_choices              │                 │
│           │ (Did user take specific actions?)   │                 │
│           └────────┬────────────────────────────┘                 │
│                    │                                               │
│                    ├─→ Missing? ──→ DENY                         │
│                    │                                               │
│                    └─→ Has all? ──→ Continue                     │
│                                        │                          │
│                                        ▼                          │
│           ┌─────────────────────────────────────┐                 │
│           │ Check required_flags                │                 │
│           │ (Does user have specific flags?)    │                 │
│           └────────┬────────────────────────────┘                 │
│                    │                                               │
│                    ├─→ Missing? ──→ DENY                         │
│                    │                                               │
│                    └─→ Has all? ──→ Continue                     │
│                                        │                          │
│                                        ▼                          │
│           ┌─────────────────────────────────────┐                 │
│           │ Check min_relationship_score        │                 │
│           │ (Is relationship high enough?)      │                 │
│           └────────┬────────────────────────────┘                 │
│                    │                                               │
│                    ├─→ Too low? ──→ DENY                         │
│                    │                                               │
│                    └─→ High enough? ──→ Continue                  │
│                                            │                      │
│                                            ▼                      │
│           ┌─────────────────────────────────────┐                 │
│           │ Check required_items                │                 │
│           │ (Does user have specific items?)    │                 │
│           └────────┬────────────────────────────┘                 │
│                    │                                               │
│                    ├─→ Missing? ──→ DENY                         │
│                    │                                               │
│                    └─→ Has all? ──→ ALLOW                        │
│                                                                   │
│  Example:                                                         │
│  {                                                                │
│    "required_choices": ["L1_INTRO_A", "L2_CHOICE_B"],            │
│    "required_flags": ["met_diana", "completed_level_1"],         │
│    "min_relationship_score": {"LUCIEN": 20, "DIANA": 10},        │
│    "required_items": ["mochila_viajero", "pista_1_mapa"],        │
│    "besitos_cost": 100                                           │
│  }                                                                │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Service Integration Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                   SERVICE INTEGRATION MATRIX                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐                                                │
│  │  NARRATIVE   │                                                │
│  │   SERVICE    │                                                │
│  └──────┬───────┘                                                │
│         │                                                         │
│         ├──→ SubscriptionService (VIP check)                     │
│         │   └─→ is_vip_active(user_id)                           │
│         │                                                          │
│         ├──→ GamificationService (besitos)                        │
│         │   ├─→ add_besitos(user_id, amount, reason)             │
│         │   ├─→ unlock_mission(user_id, mission_id)              │
│         │   └─→ get_user_inventory(user_id)                      │
│         │                                                          │
│         ├──→ UserService (user data)                              │
│         │   └─→ get_user(user_id)                                 │
│         │                                                          │
│         ├──→ BroadcastService (content distribution)             │
│         │   └─→ send_narrative_fragment(channel_id, fragment)    │
│         │                                                          │
│         └──→ ConfigService (configuration)                        │
│             └─→ get_config()                                     │
│                                                                   │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │   FLAGS      │────→│  ARCHETYPE   │────→│  CHARACTER   │    │
│  │  SERVICE     │     │   SERVICE    │     │   RELATION   │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│         │                     │                     │           │
│         └─────────────────────┴─────────────────────┘           │
│                           │                                     │
│                           ▼                                     │
│                   ┌───────────────┐                             │
│                   │  STORY ENGINE │                             │
│                   │  (COORDINATOR) │                             │
│                   └───────────────┘                             │
│                           │                                     │
└───────────────────────────┼─────────────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │    DATABASE     │
                    │  (SQLAlchemy)  │
                    └────────────────┘
```

---

## Database Schema (Simplified)

```sql
-- Core Tables
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    role VARCHAR(20) NOT NULL,  -- FREE, VIP, ADMIN
    -- ... other fields
);

-- Narrative Tables
CREATE TABLE story_fragments (
    id INTEGER PRIMARY KEY,
    fragment_id VARCHAR(50) UNIQUE NOT NULL,
    narrative_level INTEGER NOT NULL,  -- 1-6
    speaker VARCHAR(50),  -- DIANA, LUCIEN, NARRATOR
    content_text TEXT,
    unlock_conditions JSON,  -- Complex requirements
    content_variants JSON,  -- Archetype variants
    besitos_reward INTEGER DEFAULT 0,
    unlocks_mission_id INTEGER,
    INDEX idx_fragment_level_active (narrative_level, active)
);

CREATE TABLE story_choices (
    id INTEGER PRIMARY KEY,
    choice_id VARCHAR(50) UNIQUE NOT NULL,
    fragment_id INTEGER REFERENCES story_fragments(id),
    target_fragment_id INTEGER NOT NULL,
    consequences JSON,  -- Effects of choice
    display_requirements JSON,  -- When to show
    INDEX idx_choice_fragment (fragment_id, sort_order)
);

CREATE TABLE user_narrative_progress (
    id INTEGER PRIMARY KEY,
    user_id BIGINT UNIQUE REFERENCES users(user_id),
    current_fragment_id INTEGER,
    current_narrative_level INTEGER DEFAULT 1,
    max_narrative_level_reached INTEGER DEFAULT 1,
    levels_completed JSON,  -- [1, 2, 3]
    fragments_completed JSON,
    INDEX idx_progress_level (current_narrative_level)
);

CREATE TABLE user_choices (
    id INTEGER PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    choice_id VARCHAR(50) NOT NULL,
    choice_time_seconds INTEGER NOT NULL,
    consequences_applied JSON,
    INDEX idx_user_choice_date (user_id, made_at)
);

CREATE TABLE narrative_flags (
    id INTEGER PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    flag_key VARCHAR(100) NOT NULL,
    flag_value VARCHAR(500),
    expires_at DATETIME,
    UNIQUE (user_id, flag_key),
    INDEX idx_flag_user_key (user_id, flag_key)
);

CREATE TABLE archetype_profiles (
    id INTEGER PRIMARY KEY,
    user_id BIGINT UNIQUE REFERENCES users(user_id),
    primary_archetype VARCHAR(20) NOT NULL,
    archetype_points JSON,  -- {"explorer": 10, "romantic": 5}
    archetype_confidence INTEGER DEFAULT 0,
    average_choice_time_seconds INTEGER DEFAULT 0
);

CREATE TABLE character_relationships (
    id INTEGER PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    character_name VARCHAR(50) NOT NULL,
    relationship_score INTEGER DEFAULT 0,  -- -100 to +100
    became_close_friend_at DATETIME,
    became_romantic_at DATETIME,
    UNIQUE (user_id, character_name)
);

CREATE TABLE narrative_unlocks (
    id INTEGER PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    unlock_type VARCHAR(50) NOT NULL,
    unlock_id VARCHAR(100) NOT NULL,
    unlock_method VARCHAR(50) NOT NULL,
    UNIQUE (user_id, unlock_type, unlock_id)
);
```

---

## Handler Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     HANDLER REQUEST FLOW                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  USER SENDS: /story                                              │
│   │                                                               │
│   ▼                                                               │
│  ┌─────────────────────────────────────┐                         │
│  │ DatabaseMiddleware                  │                         │
│  │ - Create AsyncSession               │                         │
│  │ - Inject into data["session"]       │                         │
│  └────────┬────────────────────────────┘                         │
│           │                                                         │
│           ▼                                                       │
│  ┌─────────────────────────────────────┐                         │
│  │ cmd_start_story(message, state)     │                         │
│  │ - Get user_id from message          │                         │
│  │ - Get StoryEngine from container    │                         │
│  └────────┬────────────────────────────┘                         │
│           │                                                         │
│           ▼                                                       │
│  ┌─────────────────────────────────────┐                         │
│  │ StoryEngine.get_current_story_state │                         │
│  │ - Load user progress                │                         │
│  │ - Get current fragment              │                         │
│  │ - Check VIP access                  │                         │
│  │ - Get available choices             │                         │
│  │ - Load archetype & relationships    │                         │
│  └────────┬────────────────────────────┘                         │
│           │                                                         │
│           ▼                                                       │
│  ┌─────────────────────────────────────┐                         │
│  │ Format Response                     │                         │
│  │ - Personalize by archetype          │                         │
│  │ - Adapt to relationship level       │                         │
│  │ - Create inline keyboard            │                         │
│  └────────┬────────────────────────────┘                         │
│           │                                                         │
│           ▼                                                       │
│  ┌─────────────────────────────────────┐                         │
│  │ Send Message to User                │                         │
│  │ - Store message_id in FSM state     │                         │
│  │ - Record timestamp (choice timing)  │                         │
│  └─────────────────────────────────────┘                         │
│                                                                   │
│  USER CLICKS CHOICE                                               │
│   │                                                               │
│   ▼                                                               │
│  ┌─────────────────────────────────────┐                         │
│  │ callback_narrative_choice(callback)  │                        │
│  │ - Extract choice_id from data        │                        │
│  │ - Calculate choice_time_seconds      │                        │
│  └────────┬────────────────────────────┘                         │
│           │                                                         │
│           ▼                                                       │
│  ┌─────────────────────────────────────┐                         │
│  │ StoryEngine.make_choice()            │                         │
│  │ - Record choice timing (archetype)   │                         │
│  │ - Apply consequences                 │                         │
│  │ - Update progress                    │                         │
│  │ - Get next fragment                  │                         │
│  └────────┬────────────────────────────┘                         │
│           │                                                         │
│           ▼                                                       │
│  ┌─────────────────────────────────────┐                         │
│  │ Edit Previous Message               │                         │
│  │ - Update content                     │                         │
│  │ - Update keyboard                    │                         │
│  └─────────────────────────────────────┘                         │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Admin Content Creation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                ADMIN: CREATE FRAGMENT WIZARD                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Admin: /admin → Narrative → Create Fragment                     │
│   │                                                               │
│   ▼                                                               │
│  ┌─────────────────────────────────────┐                         │
│  │ STEP 1: Fragment ID                 │                         │
│  │ Prompt: "Enter fragment ID"         │                         │
│  │ Example: L1_INTRO_001               │                         │
│  │ Validation: Unique, follows format  │                         │
│  └────────┬────────────────────────────┘                         │
│           │                                                         │
│           ▼                                                       │
│  ┌─────────────────────────────────────┐                         │
│  │ STEP 2: Narrative Level             │                         │
│  │ Prompt: "Enter level (1-6)"         │                         │
│  │ Validation: 1-6, 4-6 requires VIP   │                         │
│  └────────┬────────────────────────────┘                         │
│           │                                                         │
│           ▼                                                       │
│  ┌─────────────────────────────────────┐                         │
│  │ STEP 3: Title                       │                         │
│  │ Prompt: "Enter fragment title"      │                         │
│  │ Example: "Bienvenida a Los Kinkys"  │                         │
│  └────────┬────────────────────────────┘                         │
│           │                                                         │
│           ▼                                                       │
│  ┌─────────────────────────────────────��                         │
│  │ STEP 4: Content                     │                         │
│  │ Prompt: "Enter narrative content"   │                         │
│  │ Support: Multi-line text            │                         │
│  └────────┬────────────────────────────┘                         │
│           │                                                         │
│           ▼                                                       │
│  ┌─────────────────────────────────────┐                         │
│  │ STEP 5: Speaker (Optional)          │                         │
│  │ Prompt: "Choose speaker"            │                         │
│  │ Options: [DIANA] [LUCIEN] [NONE]    │                         │
│  └────────┬────────────────────────────┘                         │
│           │                                                         │
│           ▼                                                       │
│  ┌─────────────────────────────────────┐                         │
│  │ STEP 6: Media (Optional)            │                         │
│  │ Prompt: "Send image/video"          │                         │
│  │ Support: Forward from channel       │                         │
│  └────────┬────────────────────────────┘                         │
│           │                                                         │
│           ▼                                                       │
│  ┌─────────────────────────────────────┐                         │
│  │ STEP 7: Unlock Conditions (Optional)│                        │
│  │ Prompt: "Add unlock conditions?"    │                         │
│  │ Options: [Yes] [No] [Skip]          │                         │
│  │ If Yes: JSON editor                 │                         │
│  └────────┬────────────────────────────┘                         │
│           │                                                         │
│           ▼                                                       │
│  ┌─────────────────────────────────────┐                         │
│  │ STEP 8: Rewards (Optional)          │                         │
│  │ Prompt: "Add besitos reward?"       │                         │
│  │ Options: [0] [10] [25] [50] [100]   │                         │
│  │ Prompt: "Unlock mission?"           │                         │
│  │ Options: [Select Mission] [Skip]    │                         │
│  └────────┬────────────────────────────┘                         │
│           │                                                         │
│           ▼                                                       │
│  ┌─────────────────────────────────────┐                         │
│  │ STEP 9: Confirmation                │                         │
│  │ Display: Summary of all fields      │                         │
│  │ Options: [✓ Confirm] [✗ Edit] [✗ Cancel]                     │
│  └────────┬────────────────────────────┘                         │
│           │                                                         │
│           ▼                                                       │
│  ┌─────────────────────────────────────┐                         │
│  │ Save Fragment                       │                         │
│  │ - Create StoryFragment record       │                         │
│  │ - Commit to database                │                         │
│  │ - Clear FSM state                   │                         │
│  │ - Show success message              │                         │
│  └─────────────────────────────────────┘                         │
│                                                                   │
│  NEXT: Add Choices to Fragment (separate wizard)                  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    ERROR HANDLING STRATEGY                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  TRY                                                              │
│   │                                                               │
│   ├─→ Get story state                                            │
│   │   ├─→ Success → Continue                                    │
│   │   └─→ Error → Log error, send user message                  │
│   │                                                               │
│   ├─→ Process choice                                             │
│   │   ├─→ Success → Update progress                              │
│   │   ├─→ Invalid choice → Send error, keep fragment            │
│   │   ├─→ Missing requirements → Send hint                       │
│   │   └─→ Database error → Log, rollback, inform user           │
│   │                                                               │
│   ├─→ Apply consequences                                         │
│   │   ├─→ Success → Update all services                         │
│   │   ├─→ Partial failure → Log warning, continue               │
│   │   └─→ Critical failure → Rollback, inform admin             │
│   │                                                               │
│   └─→ Send message                                               │
│       ├─→ Success → Update/edit message                         │
│       ├─→ User blocked bot → Log, silently fail                 │
│       └─→ Network error → Retry once, then fail                 │
│                                                                   │
│  LOGGING LEVELS                                                   │
│   - DEBUG: Normal operations, state changes                      │
│   - INFO: User progress, choices made                            │
│   - WARNING: Partial failures, retries needed                    │
│   - ERROR: Failures requiring attention                          │
│   - CRITICAL: System not functional                              │
│                                                                   │
│  USER MESSAGES                                                    │
│   - Success: ✨ Continue story                                    │
│   - Validation: ❌ Invalid choice                                │
│   - Requirements: 🔒 Requirements not met                        │
│   - Error: ⚠️ Error loading story                                │
│   - Critical: 🚧 Technical difficulties                          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Performance Optimization Strategies

```
┌─────────────────────────────────────────────────────────────────┐
│                 PERFORMANCE OPTIMIZATION                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  DATABASE QUERIES                                                 │
│   ├─→ Use indexed columns (fragment_id, user_id, level)         │
│   ├─→ Eager load relationships (selectinload)                    │
│   ├─→ Batch operations where possible                            │
│   └─→ Avoid N+1 queries (use joinload)                           │
│                                                                   │
│  CACHING                                                          │
│   ├─→ Cache starting fragments (rarely change)                   │
│   ├─→ Cache user progress (5-minute TTL)                         │
│   ├─→ Cache archetype profiles (1-hour TTL)                      │
│   └─→ Invalidate cache on updates                                │
│                                                                   │
│  JSON PROCESSING                                                  │
│   ├─→ Validate JSON structure early                              │
│   ├─→ Use JSON schema for validation                             │
│   ├─→ Minimize JSON size (abbreviate keys)                       │
│   └─→ Consider separate tables for complex data                  │
│                                                                   │
│  ASYNC OPERATIONS                                                 │
│   ├─→ All DB operations async                                    │
│   ├─→ Parallel independent queries                              │
│   ├─→ Background tasks for heavy operations                     │
│   └─→ Non-blocking I/O throughout                                │
│                                                                   │
│  RESPONSE TIME TARGETS                                            │
│   ├─→ Fragment retrieval: < 100ms                                │
│   ├─→ Choice processing: < 200ms                                 │
│   ├─→ State calculation: < 300ms                                 │
│   └─→ Complete interaction: < 500ms                              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

**End of Architecture Diagrams**

For complete technical specifications, see:
- `docs/NARRATIVE_TECHNICAL_SPEC.md` - Detailed implementation guide
- `docs/NARRATIVE_TRANSLATION_SUMMARY.md` - Design rationale
- `docs/NARRATIVE_QUICK_REFERENCE.md` - Developer quick start
