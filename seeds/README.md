# Seeds - DianaBot Database Seeding Scripts

This directory contains seed scripts for populating the DianaBot database with initial narrative content, gamification data, and other required data.

## Available Seed Scripts

### `seed_narrative_content.py`
Seeds narrative fragments and choices for all story levels.

**Current Coverage:**
- ✅ Level 1: "Los Kinkys" (Free Channel) - Complete
- ⏳ Level 2-3: Free Channel Deepening - Pending
- ⏳ Level 4-6: VIP Channel Content - Pending

## Level 1 Narrative Structure

The Level 1 narrative "Los Kinkys" consists of 5 fragments with branching paths:

### Fragments

1. **L1_INTRO_001** - Bienvenida de Diana
   - Speaker: DIANA
   - Emotion: mysterious
   - Starting: Yes
   - Content: Diana's welcoming message introducing users to Los Kinkys

2. **L1_INTRO_002** - Lucien y el Primer Desafío
   - Speaker: LUCIEN
   - Emotion: formal
   - Content: Lucien introduces himself and presents the first challenge

3. **L1_RESPONSE_QUICK** - Respuesta para Usuario que Reacciona Inmediatamente
   - Speaker: LUCIEN → DIANA
   - Emotion: approving
   - Reward: 15 besitos + Mochila del Viajero
   - Content: Response for users who react quickly

4. **L1_RESPONSE_PATIENT** - Respuesta para Usuario que Toma Tiempo
   - Speaker: LUCIEN → DIANA
   - Emotion: appreciative
   - Reward: 15 besitos + Mochila del Viajero
   - Content: Response for users who take their time

5. **L1_FIRST_CLUE** - La Primera Pista
   - Speaker: LUCIEN → DIANA
   - Emotion: mysterious
   - Ending: Yes
   - Reward: 20 besitos + 50 XP
   - Content: The first clue is revealed, ending Level 1

### Choices

1. **L1_INTRO_A** - "🚪 Descubrir más"
   - From: L1_INTRO_001 → To: L1_INTRO_002
   - Consequences:
     - Sets flag: "impulsive_choice", "met_lucien"
     - Archetype points: direct +2, explorer +1
     - Relationship change: DIANA +2

2. **L1_INTRO_B** - "✨ Entendido"
   - From: L1_INTRO_002 → To: L1_RESPONSE_QUICK (default)
   - Consequences:
     - Sets flag: "accepted_lucien_challenge"
     - Reward: 10 besitos

## Usage

### Seed Level 1 Content

```bash
python -m seeds.seed_narrative_content
```

### Expected Output

```
🌱 Starting Level 1 narrative content seed...

✅ Database initialized

📜 Seeding Level 1 fragments...
✅ Created fragment: L1_INTRO_001
✅ Created fragment: L1_INTRO_002
✅ Created fragment: L1_RESPONSE_QUICK
✅ Created fragment: L1_RESPONSE_PATIENT
✅ Created fragment: L1_FIRST_CLUE
✅ Level 1 fragments seeded: 5 created, 0 updated

🔗 Seeding Level 1 choices...
✅ Created choice: L1_INTRO_A
✅ Created choice: L1_INTRO_B
✅ Level 1 choices seeded: 2 created, 0 updated

🔍 Verifying seeded content...
============================================================
LEVEL 1 NARRATIVE CONTENT VERIFICATION
============================================================

📜 Fragments found: 5
  • L1_INTRO_001: Bienvenida de Diana [STARTING]
  • L1_INTRO_002: Lucien y el Primer Desafío
  • L1_RESPONSE_QUICK: Respuesta para Usuario que Reacciona Inmediatamente
  • L1_RESPONSE_PATIENT: Respuesta para Usuario que Toma Tiempo
  • L1_FIRST_CLUE: La Primera Pista [ENDING]

🔗 Choices found: 2
  • L1_INTRO_A: 🚪 Descubrir más
  • L1_INTRO_B: ✨ Entendido

✅ Starting fragments (1):
  • L1_INTRO_001

✅ Ending fragments (1):
  • L1_FIRST_CLUE

🎉 Level 1 narrative content seeded successfully!

Next steps:
  1. Test the narrative flow with /start command
  2. Verify fragment transitions work correctly
  3. Check that rewards and consequences are applied
```

## Implementation Details

### Fragment ID Convention

All fragment IDs follow this pattern: `L{N}_{TYPE}_{NUMBER}`

- **L{N}**: Level number (1-6)
- **{TYPE}**: Fragment type (INTRO, RESPONSE, CLUE, DIVAN, etc.)
- **{NUMBER}**: Sequential number

Examples:
- `L1_INTRO_001`: Level 1, Introduction, fragment 1
- `L4_DIVAN_015`: Level 4, Diván, fragment 15
- `L6_FINAL_001`: Level 6, Final, fragment 1

### Choice Consequences

Choices can have multiple consequences:

```python
{
    "flags_set": ["met_lucien", "chose_romantic_path"],
    "flags_unset": ["first_interaction"],
    "archetype_points": {
        "romantic": +2,
        "direct": -1
    },
    "relationship_change": {
        "DIANA": +5,
        "LUCIEN": -2
    },
    "besitos_reward": 50,
    "items_gained": ["pista_1_mapa"],
    "items_lost": ["intro_map"],
    "mission_unlocked": 15
}
```

### Narrative Levels

- **Levels 1-3**: Free Channel (Los Kinkys)
  - Accessible to all users
  - Introduction to the narrative universe
  - Initial character development

- **Levels 4-6**: VIP Channel (El Diván)
  - Requires active VIP subscription
  - Deep emotional exploration
  - Intimate character revelations
  - Multiple endings based on choices

## Creative Source Material

The narrative content is based on:

- **`docs/narrativo.md`**: Complete narrative script for all levels
- **`docs/lucien.md`**: Lucien character bible and personality
- **`docs/concepto.md`**: Overall system concept and integration

## Testing

After seeding, test the narrative flow:

1. **Start the narrative**: Use `/start` command or trigger the starting fragment
2. **Make choices**: Verify that buttons appear and work correctly
3. **Check consequences**: Ensure flags, archetype points, and relationships update
4. **Verify rewards**: Confirm besitos and experience points are awarded
5. **Test transitions**: Ensure fragment transitions work smoothly

## Troubleshooting

### Fragment Not Found

If a fragment is missing from the database:

```bash
# Re-run the seed script
python -m seeds.seed_narrative_content
```

### Choice Links Broken

If choices don't navigate to correct fragments:

1. Verify both fragments exist in the database
2. Check that `target_fragment_id` is correctly set
3. Re-run the seed script to update choice references

### Consequences Not Applied

If rewards/consequences don't apply:

1. Check the narrative service implementation
2. Verify consequence JSON structure is valid
3. Review logs for error messages during choice processing

## Future Enhancements

Planned seed scripts:

- **`seed_gamification_data.py`**: Gamification configuration, missions, items
- **`seed_user_progress.py`**: Reset or initialize user progress for testing
- **`seed_all.py`**: Master script that runs all seed scripts in order

## Contributing

When adding new narrative content:

1. Update the creative source files in `docs/`
2. Add fragments to the appropriate level in the seed script
3. Follow the ID convention (`L{N}_{TYPE}_{NUMBER}`)
4. Include all choices with proper consequences
5. Test the narrative flow before committing
6. Update this README with new fragments and choices

## Notes

- All fragments are stored in the `story_fragments` table
- All choices are stored in the `story_choices` table
- Fragment IDs are unique across all levels
- The seed script is idempotent (can be run multiple times safely)
- Existing fragments are updated, not recreated
