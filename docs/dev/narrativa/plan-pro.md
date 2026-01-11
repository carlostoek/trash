# DianaBot - Plan de Desarrollo Narrativo
## Roadmap Integrado: 12 Semanas hacia una Experiencia Completa

**Versión:** 1.0
**Fecha:** 10 de Enero, 2026
**Estado:** Aprobado para Desarrollo
**Propietario:** Creative Director

---

## 📋 TABLA DE CONTENIDOS

1. [Visión Ejecutiva](#visión-ejecutiva)
2. [Estado Actual del Sistema](#estado-actual-del-sistema)
3. [Roadmap de 12 Semanas](#roadmap-de-12-semanas)
   - Fase 1: Contenido Narrativo (Semana 1-4)
   - Fase 2: Experiencia + Recompensas (Semana 5-8)
   - Fase 3: VIP + Social (Semana 9-12)
4. [Métricas de Éxito](#métricas-de-éxito)
5. [Estructura de Equipo](#estructura-de-equipo)
6. [Glosario de Términos](#glosario-de-términos)

---

## 🎬 VISIÓN EJECUTIVA

### Propósito del Proyecto

Transformar DianaBot de un bot funcional con Level 1 de contenido en una **experiencia narrativa completa** que:

1. **Cree conexión emocional** entre usuarios y personajes (Diana, Lucien)
2. **Genere engagement sostenido** a través de arcos narrativos significativos
3. **Convierta usuarios Free en suscriptores VIP** mediante contenido premium diferenciado
4. **Construya comunidad** alrededor de experiencias compartidas virales

### Estrategia de Desarrollo

**ENFOQUE HÍBRIDO ESTRATÉGICO:**
- **Fase 1 (Contenido):** Completar arco narrativo Free primero → crear base de usuarios
- **Fase 2 (Experiencia):** Mejorar UX + integrar gamificación → maximizar retención
- **Fase 3 (Monetización):** Desplegar contenido VIP + features sociales → escalar

**JUSTIFICACIÓN:**
- Sin contenido, no hay nada que mejorar
- Con contenido Free leal, podemos optimizar experiencia antes de vender VIP
- Con base de usuarios, podemos justificar inversión en contenido premium

---

## 📊 ESTADO ACTUAL DEL SISTEMA

### ✅ COMPLETADO

| Componente | Estado | Detalles |
|------------|--------|----------|
| **Base de Datos** | ✅ 100% | 8 modelos narrativos implementados |
| **Servicios** | ✅ 100% | StoryEngine + 5 subservicios funcionales |
| **Handlers Usuario** | ✅ 100% | `/story`, choices, status, reread |
| **Level 1 Content** | ✅ 100% | 5 fragments, 2 choices, Diana+Lucien |
| **Tests** | ✅ 100% | 39/39 passing |
| **Gamification** | ✅ 100% | Besitos, niveles, misiones, recompensas |

### ❌ FALTANTE

| Componente | Estado | Impacto |
|------------|--------|---------|
| **Levels 2-3 Content** | ❌ 0% | 83% de historia ausente |
| **Levels 4-6 Content** | ❌ 0% | Propuesta VIP es débil |
| **Integración Narrativa→Gamificación** | ⚠️ 10% | Sin recompensas por progreso |
| **Integración Gamificación→Narrativa** | ❌ 0% | No se pueden gastar besitos en contenido |
| **UX Visual** | ⚠️ 30% | Progreso invisible, feedback plano |
| **Detección de Arquetipos** | ⚠️ 20% | Sistema existe pero contenido no lo usa |

---

## 🗓️ ROADMAP DE 12 SEMANAS

---

## FASE 1: CONTENIDO NARRATIVO (Semana 1-4)
**Objetivo:** Completar Levels 2-3 (Free) → Crear base de usuarios leales → Preparar para VIP

**Liderazgo:** Narrative Games Expert
**KPIs:** Level 2 completado, Level 3 completado, 2% conversión VIP

### 📅 SEMANA 1-2: LEVEL 2 - "OBSERVACIÓN Y PRUEBA"

**Narrativa:** Diana pasa de misteriosa a intrínsecamente interesada

#### Fragmentos Level 2:

| ID | Speaker | Emoción | Contenido | Rewards |
|----|--------|---------|----------|---------|
| **L2_RETURN_001** | DIANA | intrigued_amused | Nota que el usuario regresó, comenta persistencia | 10 besitos |
| **L2_CHALLENGE_002** | LUCIEN | testing | Presenta misión de observación 3 días en canal | 15 besitos |
| **L2_SUCCESS_003** | DIANA | genuine_surprise | Reconoce observación profunda (3+ pistas) | 20 besitos + Pista 2 |
| **L2_PARTIAL_004** | DIANA | encouraging | Reconoce esfuerzo parcial (1-2 pistas) | 10 besitos |
| **L2_TIMEOUT_005** | LUCIEN | disappointed | Usuario no completó observación | 5 besitos |

#### Sistema de Observación:
- **Requerimiento técnico:** Tracking de interacciones en canal
- **Implementación:** Contar posts leídos, reacciones, tiempo en canal
- **Pistas ocultas:** Detalles sutiles en contenido del canal

#### Técnicos Necesarios:
```python
# Nuevo servicio para tracking de canal
class ChannelInteractionService:
    async def track_post_view(user_id, post_id)
    async def track_channel_time_spent(user_id, minutes)
    async def get_observation_score(user_id) -> int
```

#### Choices Level 2:
- **L2_ACCEPT_A**: "Acepto el desafío" → Inicia observación
- **L2_POSTPONE**: "Necesito tiempo" → Pausa, puede retomprar

---

### 📅 SEMANA 3-4: LEVEL 3 - "PRUEBA FINAL"

**Narrativa:** Diana quiere conocer al usuario → Perfil de Deseo → Invitación VIP personalizada

#### Fragmentos Level 3:

| ID | Speaker | Emoción | Contenido | Rewards |
|----|--------|---------|----------|---------|
| **L3_CONTINUE_001** | LUCIEN | approving | Continuación desde Level 2 completado | 10 besitos |
| **L3_PROFILE_002** | DIANA | curious_intimate | Pregunta 1 de Perfil de Deseo | 5 besitos |
| **L3_PROFILE_003** | DIANA | curious_intimate | Pregunta 2 de Perfil de Deseo | 5 besitos |
| **L3_PROFILE_004** | DIANA | curious_intimate | Pregunta 3 de Perfil de Deseo | 5 besitos |
| **L3_PROFILE_005** | DIANA | curious_intimate | Pregunta 4 de Perfil de Deseo | 5 besitos |
| **L3_PROFILE_006** | DIANA | curious_intimate | Pregunta 5 de Perfil de Deseo | 5 besitos |
| **L3_ARCHETYPE_007** | SYSTEM | analytical | Arquetipo detectado basado en respuestas | Badge |
| **L3_SYNTHESIS_008** | DIANA | vulnerable | Síntesis personalizada del perfil | 25 besitos |
| **L3_INVITATION_009** | DIANA | hopeful_inviting | Invitación VIP personalizada | Link VIP |

#### Perfil de Deseo (7 preguntas psicológicas):
1. "¿Qué buscas en una conexión?" (Explorer/Intimate)
2. "¿Prefieres lo inesperado o lo familiar?" (Novelty/Comfort)
3. "¿Qué tan rápido te abres?" (Direct/Patient)
4. "¿Mente o corazón?" (Analytical/Romantic)
5. "¿Luchas o te dejas llevar?" (Persistent/Yield)
6. "¿Secretos o transparencia?" (Private/Open)
7. "¿Pasión o plenitud?" (Intensity/Peace)

#### Técnicos Necesarios:
```python
# Nuevo modelo para perfiles de deseo
class DesireProfile(Base):
    user_id = Column(BigInteger, primary_key=True)
    question_1_answer = Column(String)  # Explorer/Intimate
    question_2_answer = Column(String)  # Novelty/Comfort
    # ... 7 preguntas
    archetype_prediction = Column(String)  # Generated
    created_at = Column(DateTime)
```

#### Choices Level 3:
- **L3_COMPLETE_A**: "Responder pregunta 1" → Inicia perfil
- **L3_SKIP:** "Omitir por ahora" → Pausa, puede retomprar

#### Invitación VIP Personalizada:
```python
# Generación de mensaje personalizado según arquetipo
if archetype == "ROMANTIC":
    vip_message = "🌸 Tu sensibilidad romántica... hay mundos donde solo tú puedes entrar."
elif archetype == "INTELLECTUAL":
    vip_message = "🌸 Tu mente analítica... hay capas de conocimiento que solo tú descubrirás."
# etc.
```

---

### 📊 MÉTRICAS FASE 1 - TARGET

| Métrica | Actual | Target | Medición |
|---------|--------|--------|----------|
| **Nivel 2 completado** | 0% | 60% | Usuarios que finalizan Level 2 |
| **Nivel 3 completado** | 0% | 40% | Usuarios que finalizan Level 3 |
| **L1→L2 retención** | 100% | 70% | Usuarios que continúan después de Level 1 |
| **L2→L3 retención** | N/A | 50% | Usuarios que continúan después de Level 2 |
| **Tiempo en Level 1** | ~5 min | ~15 min | Engagement por sesión |
| **Conversión VIP** | 0% | 2-3% | Usuarios que se suscriben después de Level 3 |

---

## FASE 2: EXPERIENCIA + RECOMPENSAS (Semana 5-8)
**Objetivo:** Maximizar retención mediante UX mejorada + integración gamificación

**Liderazgo:** Experience Designer + Python Pro
**KPIs:** Session length +50%, Return rate +60%, Completion +40%

### 📅 SEMANA 5: VISUAL POLISH

#### Objetivos UX:

1. **Indicadores de Progreso**
   - Barra de progreso incrustada en mensajes narrativos
   - Contador de fragmentos: "3/6" o "50%"
   - Indicador visual de nivel actual

2. **Feedback de Decisiones Mejorado**
   - Carácter reacciona inmediatamente a tu elección
   - Consecuencias narrativas visibles
   - "Qué pasaría si..." preview (opcional)

3. **Celebraciones de Milestones**
   - Nivel completado → celebración visual
   - Arquetipo detectado → badge desbloqueado
   - Relación milestone → personaje celebra contigo

#### Implementación Técnica:

```python
# narrative_formatters.py - Nueva función
def format_progress_indicator(
    current_fragment: StoryFragment,
    user_progress: UserNarrativeProgress
) -> str:
    """Crea indicador visual de progreso incrustado."""
    level = current_fragment.narrative_level

    # Contar fragmentos en este nivel
    total_in_level = _count_fragments_in_level(level)

    # Fragmentos completados por usuario en este nivel
    completed = _count_completed_in_level(user_progress, level)

    # Porcentaje
    percentage = int((completed / total_in_level) * 100)

    # Barra visual
    filled = "▓" * completed
    empty = "░" * (total_in_level - completed)

    return f"\n\n📖 Nivel {level} de 6\n{filled}{empty} {percentage}% ({completed}/{total_in_level} fragmentos)"
```

#### Experiencia Objetivo:
```
ANTES:
🌸 <i>(mysterious)</i>

Bienvenida de Diana...
[Contenido]
[🚪 Descubrir más] [Mi progreso]

DESPUÉS:
📖 Nivel 1 de 6
▓▓▓░░░░░ 50% (3/6 fragmentos)

🌸 <i>(mysterious)</i>

Bienvenida de Diana...
[Contenido]
[🚪 Descubrir más] [Mi progreso]
```

---

### 📅 SEMANA 6: RECOMPENSAS NARRATIVAS

#### Objetivos:

1. **Besitos por Completar Fragmentos**
   - Cada fragmento tiene `besitos_reward` (ya en modelo)
   - Al completar fragmento → otorgar besitos
   - Bonus por primer completion del fragmento

2. **XP por Hitos Narrativos**
   - Nivel completado → XP grande
   - Arquetipo detectado → XP mediano
   - Relationship milestone → XP pequeño

3. **Badges de Arquetipo**
   - "Explorer Iniciado" → 10 primeras decisiones
   - "Romántico Emergente" → 5 decisiones románticas
   - "Analítico Confirmado" → 3 decisiones analíticas

#### Implementación Técnica:

```python
# NarrativeService - Nuevo método
async def complete_fragment(
    self,
    user_id: int,
    fragment_id: int,
    choice_time_seconds: int = 0
) -> Tuple[bool, str, Dict]:
    """
    Completa un fragmento y otorga recompensas.

    Rewards:
    - Besitos del fragmento
    - XP del fragmento
    - Bonus primer completion
    - Badge de hito
    """
    # 1. Obtener fragmento
    fragment = await self.get_fragment_by_id(fragment_id)

    # 2. Otorgar besitos
    if fragment.besitos_reward > 0:
        await self.besitos_service.add_besitos(
            user_id,
            fragment.besitos_reward,
            source="narrative_completion",
            description=f"Fragment {fragment.fragment_id}"
        )

    # 3. Otorgar XP
    if fragment.experience_reward > 0:
        await self.gamification_service.add_xp(
            user_id,
            fragment.experience_reward
        )

    # 4. Verificar badges
    await self.check_and_award_badges(user_id, fragment_id)

    # 5. Primer completion bonus
    if await self._is_first_completion(user_id, fragment_id):
        await self.besitos_service.add_besitos(
            user_id,
            bonus=50,  # 50 besitos bonus
            source="first_completion",
            description="Primera vez que completas este fragmento"
        )

    return True, "Fragmento completado", rewards_dict
```

#### Experiencia Objetivo:
```
✨ Has completado "El Regreso Observado"

🪙 25 besitos ganados
⭐ 50 XP obtenidos
🏅 Badge: "Observador Iniciado" desbloqueado

Tu relación con Diana ha mejorado (+5)
```

---

### 📅 SEMANA 7: PROFUNDIZACIÓN EMOCIONAL

#### Objetivos:

1. **Voz Dinámica de Diana**
   - Relación < 20: Formal, distante
   - Relación 20-39: Amigable, pronombres personales
   - Relación 40-59: Vulnerable, confía en usuario
   - Relación 60+: Íntima, exclusivo

2. **Notificaciones de Milestones**
   - "Diana te está empezando a confiar en ti..."
   - "¡Has alcanzado el estatus de Amigo Cercano!"
   - "Diana te considera una persona de confianza..."

3. **Mecánicas de Suspenso**
   - "···" (pausa dramática)
   - "_Sientes que algo está a punto de cambiar..._"
   - Revelaciones inesperadas

#### Implementación Técnica:

```python
# narrative_formatters.py - Voz dinámica
def format_narrative_message(
    fragment: StoryFragment,
    user_progress: UserNarrativeProgress,
    relationship_score: Optional[int] = None
) -> str:
    """Formatea mensaje con voz dinámica según relación."""

    # Obtener relación con Diana
    diana_rel = await get_relationship(user_id, "DIANA")
    score = diana_rel.relationship_score if diana_rel else 0

    # Determinar tono basado en score
    if score < 20:
        # Formal, distante
        pronoun = "usted"
        tone = "formal"
    elif score < 40:
        # Amigable
        pronoun = "tú" (primera vez)
        tone = "friendly"
    elif score < 60:
        # Vulnerable, confía
        pronoun = "tú"
        tone = "intimate"
    else:
        # Íntima, exclusivo
        pronoun = "tú"
        tone = "exclusive"

    # Aplicar variante de contenido según tono
    if fragment.content_variants and tone in fragment.content_variants:
        content = fragment.content_variants[tone]
    else:
        content = fragment.content_text

    # Formatear con tono apropiado
    # ...
```

#### Experiencia Objetivo:
```
LEVEL 1 (Relationship: 0):
🌸 **Diana:** "Bienvenido a Los Kinkys. Tú has cruzado una línea..."

LEVEL 2 (Relationship: 15):
🌸 **Diana:** "Te veo de nuevo. Hay persistencia en ti..."

LEVEL 3 (Relationship: 35):
🌸 **Diana:** "Me gustaría conocerte mejor..."

LEVEL 4+ (Relationship: 60):
🌸 **Diana:** "Entre tú y yo... hay algo que necesito decirte..."
```

---

### 📅 SEMANA 8: SUSPENSO Y SORPRESAS

#### Objetivos:

1. **Mecánica de Suspenso**
   - Pausas dramáticas entre fragmentos clave
   - "Cargando..." para builds emocionales
   - Tiempos de espera variables

2. **Momentos de Sorpresa**
   - Revelaciones inesperadas sobre Diana
   - Giros argumentales
   - Consecuencias retardadas de elecciones pasadas

3. **Flashbacks y Recuerdos**
   - "¿Recuerdas tu primera elección?..."
   - Sistema recuerda decisiones y las menciona

#### Implementación Técnica:

```python
# NarrativeService - Sistema de delayed consequences
async def check_delayed_consequences(
    self,
    user_id: int
) -> List[str]:
    """Verifica si hay consecuencias retardadas que activar."""

    # Buscar elecciones pasadas que tenían efectos retardados
    past_choices = await self.session.execute(
        select(UserChoice).where(
            UserChoice.user_id == user_id,
            UserChoice.delayed_consequence.isnot(None)
        )
    )

    consequences_to_trigger = []

    for choice in past_choices.scalars():
        delayed = choice.delayed_consequence
        # Verificar si es tiempo de activar
        if self._should_trigger(delayed):
            consequences_to_trigger.append(delayed)

    return consequences_to_trigger
```

---

### 📊 MÉTRICAS FASE 2 - TARGET

| Métrica | Actual | Target | Medición |
|---------|--------|--------|----------|
| **Session length** | ~5 min | ~12 min | Tiempo promedio por sesión |
| **Return rate (24h)** | N/A | +60% | Usuarios que regresan en 24h |
| **Level completion** | ~30% | +40% | Usuarios que completan niveles |
| **Besitos/user/day** | +10 | +50 | Economía activa |
| **VIP conversion** | 2% | 3% | Usuarios que se suscriben |

---

## FASE 3: VIP + SOCIAL (Semana 9-12)
**Objetivo:** Desplegar contenido premium + features sociales → Escalar crecimiento

**Liderazgo:** Narrative Games Expert + Experience Designer
**KPIs:** VIP conversion 5%, Viral coefficient 0.3, Revenue $2,000/month

### 📅 SEMANA 9-10: LEVEL 4 - "INTIMIDAD I" (VIP)

**Narrativa:** Nivel premium donde Diana comienza su revelación auténtica

#### Fragmentos Level 4:

| ID | Speaker | Emoción | Contenido | Requirements |
|----|--------|---------|----------|--------------|
| **L4_CONTINUE_001** | DIANA | reserved | Bienvenida VIP, reconocimiento | VIP activo |
| **L4_QUIZ_002** | DIANA | curious_intellectual | Pregunta de comprensión intelectual | VIP activo |
| **L4_RESPONSE_ROMANTIC_003** | DIANA | vulnerable | Respuesta a arquetipo romántico | Romantic + VIP |
| **L4_RESPONSE_INTELLECTUAL_004** | DIANA | appreciative | Respuesta a arquetipo intelectual | Intellectual + VIP |
| **L4_SECRET_005** | DIANA | mysterious_secret | Primer secreto profundo revelado | Relationship 40+ |
| **L4_SYNTHESIS_006** | DIANA | emotionally_opened | Síntesis personalizada | Cualquier VIP |

#### Sistema de Comprensión:
- Quiz de comprensión sobre la historia
- Respuestas correctas → desbloquean contenido más profundo
- Respuestas incorrectas → Diana corrige y explica

#### Experiencia VIP:
```
🔒 CONTENIDO VIP - NIVEL 4

🌸 **Diana (Intelectual):**
"Tu mente analítica... hay dimensiones de mi mundo que requieren
la misma precisión que tú aplicas a todo.

Permítemos ver si podemos resonar a un nivel más profundo..."

[Quiz de comprensión del mundo de Los Kinkys]

✨ Has desbloqueado: "Fragmento de Intimidad I"
```

---

### 📅 SEMANA 11: LEVEL 5 - "INTIMIDAD II" (VIP)

**Narrativa:** Vulnerabilidad emocional profunda de Diana

#### Fragmentos Level 5:

| ID | Speaker | Emoción | Contenido | Requirements |
|----|--------|---------|----------|--------------|
| **L5_INTRO_001** | DIANA | vulnerable | Continuación VIP | VIP activo |
| **L5_DIALOGUE_002** | DIANA | emotionally_raw | Diálogo vulnerable profundo | Relationship 50+ |
| **L5_DIALOGUE_003** | LUCIEN | protective_guardian | Lucien advierte sobre vulnerabilidad | Relationship 30+ |
| **L5_REVELATION_004** | DIANA | utterly_vulnerable | Revelación mayor de Diana | Relationship 60+ |
| **L5_SYNTHESIS_005** | DIANA | transformed | Síntesis transformadora | Cualquier VIP |

#### Sistema de Diálogos:
- Conversaciones multi-turno con Diana
- Lucien interviene si relación es muy cercana
- Consecuencias según respuestas del usuario

---

### 📅 SEMANA 12: LEVEL 6 - "CULMINACIÓN" + FEATURES SOCIALES

#### Nivel 6: Múltiples Endings por Arquetipo

| Arquetipo | Ending ID | Título | Descripción |
|----------|-----------|-------|-------------|
| **ROMANTIC** | L6_ENDING_ROMANTIC | "Unión Eterna" | Romance profundo con Diana |
| **INTELLECTUAL** | L6_ENDING_INTELLECTUAL | "Sociedad Secreta" | Diana como mentora intelectual |
| **EXPLORER** | L6_ENDING_EXPLORER | "Infinito Descubrimiento" | Diana como compañera de aventura |
| **GUARDIAN** | L6_ENDING_GUARDIAN | "Protector Elegido" | Diana encomienda confianza |
| **AUTHENTIC** | L6_ENDING_AUTHENTIC | "Yo Misma" | Diana ayuda a encontrarse a sí mismo |
| **ETERNAL** | L6_ENDING_ETERNAL | "Ciclos Infinitos" | Continuación más allá del final |

#### Features Sociales:

1. **Tarjetas de Arquetipo Shareables**
   ```python
   # Generar tarjeta de arquetipo
   def generate_archetype_card(user_id: int) -> Image:
       archetype = get_user_archetype(user_id)

       card = f"""
       ╔═════════════════════════════╗
       ║  TU ARQUETIPO              ║
       ║                            ║
       ║  🎭 {archetype.title}        ║
       ║                            ║
       ║  "{archetype.tagline}"      ║
       ║                            ║
       ║  @DianaBot                  ║
       ╚═════════════════════════════╝
       """

       return generate_image(card)
   ```

2. **Generador de Citas de Diana/Lucien**
   ```python
   async def generate_diana_quote(user_id: int) -> str:
       """Genera cita personalizada de Diana según relación."""
       relationship = await get_relationship(user_id, "DIANA")
       archetype = get_user_archetype(user_id)

       # Seleccionar cita según contexto
       quote = select_personalized_quote(relationship, archetype)

       return f"🌸 **Diana:**\n\n{quote}\n\n📖 @DianaBot"
   ```

3. **Sistema de Referidos**
   ```python
   # Código de referido
   referral_code = generate_referral_code(user_id)

   # Cuando referido se hace VIP:
   - Referido gana 1 mes gratis
   - Usuario que refiere gana 500 besitos
   ```

---

### 📊 MÉTRICAS FASE 3 - TARGET

| Métrica | Actual | Target | Medición |
|---------|--------|--------|----------|
| **VIP Conversion** | 2% | 5% | Conversión después de Level 6 |
| **MRR Proyectada** | $0 | $2,000 | Ingresos recurrentes mensuales |
| **Referral Rate** | 0% | 15% | Usuarios que refieren nuevos usuarios |
| **Viral Coefficient** | 0 | 0.3 | Cada usuario trae 0.3 usuarios en promedio |
| **Completion Rate** | 30% | 70% | Usuarios que completan Level 6 |

---

## 📈 MÉTRICAS DE ÉXITO

### Métricas de Engagimiento

| Fase | Métrica | Target | Herramienta de Medición |
|------|---------|--------|------------------------|
| **Actual** | DAU | 10,000 | Bot stat /users |
| **Actual** | MAU | 1,000 | Bot stat unique users |
| **Fase 1** | L1→L2 Retention | 70% | UserNarrativeProgress timestamps |
| **Fase 1** | L2→L3 Retention | 50% | UserNarrativeProgress timestamps |
| **Fase 2** | Session Length | +50% | Time between first/last story view |
| **Fase 2** | Return Rate (24h) | +60% | Users with activity < 24h ago |
| **Fase 3** | VIP Conversion | 5% | VIPSubscriber / total users |

### Métricas Técnicas

| Métrica | Target | Medición |
|---------|--------|----------|
| **Test Coverage** | 85%+ | pytest coverage |
| **Response Time** | <300ms | Performance monitoring |
| **Uptime** | 99.9% | Server monitoring |
| | | |

### Métricas de Negocio

| Métrica | Target | Medición |
|---------|--------|----------|
| **MRR Month 1** | $500 | VIP subscriptions × $10 |
| **MRR Month 3** | $2,000 | Compounding growth |
| **MRR Month 6** | $5,000 | Scaling optimization |
| **CAC Payback** | <6 meses | Marketing spend vs LTV |

---

## 👥 ESTRUCTURA DE EQUIPO

### Roles y Responsabilidades

| Rol | Responsabilidad | Horas Estimadas |
|-----|----------------|-------------------|
| **Narrative Designer** | Crear contenidoLevels 2-6 | 120h |
| **Python Developer** | Implementar servicios técnicos | 80h |
| **UX/UI Designer** | Diseñar experiencia visual | 40h |
| **QA Engineer** | Testing y validación | 30h |
| **Creative Director** | Orquestrar y aprobar entregables | 20h |
| **TOTAL** | | **290 horas (~7 semanas @ 40h/week)** |

### Workflow de Creación de Contenido

```
1. Narrative Designer
   └─ Escribe fragmento (contenido, speaker, emoción)
   └─ Define opciones y consecuencias

2. Experience Designer
   └─ Revisa para impacto emocional
   └─ Sugiere mejoras de pacing

3. Creative Director
   └─ Aprueba versión final
   └─ Da luz verde para implementación

4. Python Developer
   └─ Crea seed script con fragmento
   └─ Implementa lógica técnica (si aplica)

5. QA Engineer
   └─ Prueba flujo completo
   └─ Reporta bugs

6. Deployment
   └─ Ejecuta seed en producción
   └─ Monitorea métricas
```

---

## 📚 GLOSARIO DE TÉRMINOS

### Términos Narrativos

- **Fragmento:** Unidad de contenido narrativo (texto + speaker + emoción)
- **Choice:** Opción de decisión que lleva a otro fragmento
- **Speaker:** Personaje que habla (DIANA, LUCIEN, NARRATOR)
- **Emotion:** Estado emocional del speaker (mysterious, formal, vulnerable)
- **Arquetipo:** Personalidad del usuario detectada por su comportamiento
- **Relationship Score:** Puntuación de relación con personaje (-100 a +100)

### Términos Técnicos

- **StoryEngine:** Coordinador de todos los servicios narrativos
- **NarrativeService:** Servicio core de gestión de fragmentos y progreso
- **FlagService:** Gestión de estados persistentes en la historia
- **ArchetypeService:** Detección de personalidad de usuario
- **CharacterRelationshipService:** Gestión de relaciones con personajes

### Términos de Gamificación

- **Besitos:** Moneda virtual del sistema
- **XP:** Puntos de experiencia para subir de nivel
- **Mission:** Quest/objetivo que otorga recompensas
- **Streak:** Racha de días consecutivos de actividad
- **Badges:** Logros desbloqueables por hitos específicos

### Términos UX

- **Session Length:** Tiempo que un usuario pasa en el bot por sesión
- **Return Rate:** Porcentaje de usuarios que regresan después de 24h
- **Completion Rate:** Porcentaje de usuarios que completan niveles
- **Viral Coefficient:** K factor (cada usuario trae K nuevos usuarios)

---

## 📝 NOTAS DE IMPLEMENTACIÓN

### Convenciones de Código

1. **Nombres de Fragmentos:** `L{N}_{TYPE}_{NUMBER}`
   - Ejemplo: `L2_RETURN_001` (Level 2, Return, primer fragmento)

2. **Nombres de Choices:** `L{N}_{TYPE}_{LETTER}`
   - Ejemplo: `L2_ACCEPT_A`, `L3_SKIP`

3. **Emociones de Speaker:** formato `snake_case`
   - Ejemplo: `genuine_surprise`, `mysterious`, `vulnerable`

4. **Ids de Arquetipos:**
   - EXPLORER, DIRECT, ROMANTIC, ANALYTICAL, PERSISTENT, PATIENT

### Sistema de Control de Versiones

- **Branch principal:** `main` para producción
- **Branch desarrollo:** `dev-narrative` para features narrativas
- **Tags:** `v2.0.0-level2`, `v2.1.0-level3`, etc.

### Proceso de Testing

1. **Unit Tests:** Cada servicio/función tiene tests
2. **Integration Tests:** Prueban flujos completos
3. **E2E Tests:** Prueban experiencia de usuario completa
4. **Content Validation:** Narrative designer aprueba contenido antes de seed

---

## 🎯 PRÓXIMOS PASOS INMEDIATOS

### Para Comenzar Fase 1:

1. ✅ **Este documento está aprobado** (plan-pro.md creado)
2. **Revisar y aprobar:** Aprobación del director
3. **Crear estructura de equipos:** Asignar roles
4. **Comenzar Semana 1:** Level 2 - "Observación y Prueba"

### Dependencias Técnicas

1. **Sistema de tracking de canal** (para Level 2)
2. **Modelo DesireProfile** (para Level 3)
3. **Sistema de quizzes de comprensión** (para Level 4)

---

## 📞 CONTACTO

**Creative Director:** @Claude
**Document Location:** `/docs/dev/narrativa/plan-pro.md`
**Status:** APROBADO PARA DESARROLLO

**Last Updated:** 10 de Enero, 2026

---

*"La diferencia entre una historia funcional y una experiencia memorable no está en qué sucede, sino en cómo se siente. Nuestro trabajo es transformar mecánicas funcionales en momentos emocionales que los usuarios recordarán."*

— Creative Director
