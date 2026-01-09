"""
Contenido narrativo Level 1 - Bienvenida y Primer Contacto.

Este nivel establece:
- Primer encuentro con Lucien (El Guardian del Umbral)
- Atmosfera de Los Kinkys (bar exclusivo)
- Primera evaluacion del usuario
- Primer vistazo de Diana
- Establecimiento del misterio

Tempo emocional: Allegretto (vivaz pero contenido)
Peak moment: Primera mencion de Diana
Breathing room: Despues de la primera decision
"""

# =============================================================================
# CHAPTER 1: BIENVENIDA - EL UMBRAL
# =============================================================================

LEVEL_1_CHAPTERS = [
    {
        "chapter_id": "ch1_bienvenida",
        "title": "El Umbral",
        "subtitle": "Donde todo comienza... y nada es lo que parece",
        "required_level": 1,
        "sequence_order": 1,
        "atmosphere": {
            "visual": "Penumbra ambar, un bar de otra epoca. Madera oscura, espejos antiguos que multiplican sombras. Una barra pulida donde se reflejan copas de cristal.",
            "auditory": "Jazz suave - Kind of Blue de Miles Davis. El tintineo distante de hielo en vasos. Murmullo de conversaciones que no alcanzas a descifrar.",
            "tactile": "El terciopelo gastado de una butaca que ha sostenido mil historias. El frio condensado de un vaso que nadie te sirvio.",
            "olfactory": "Madera ahumada, cuero viejo, un perfume que no reconoces pero que despues recordaras.",
            "emotional": "Anticipacion contenida. La sensacion de estar a punto de cruzar un umbral del que no hay retorno."
        },
        "emotional_tempo": "allegretto",
        "peak_moment": "El momento en que Lucien menciona a Diana por primera vez",
        "breathing_room": False,
        "is_active": True
    }
]

# =============================================================================
# SCENES LEVEL 1
# =============================================================================

LEVEL_1_SCENES = [
    # -------------------------------------------------------------------------
    # ESCENA 1.1: LLEGADA AL BAR
    # -------------------------------------------------------------------------
    {
        "scene_id": "L1_S1_llegada",
        "chapter_id": "ch1_bienvenida",
        "title": "Llegada a Los Kinkys",
        "description": "El usuario entra al bar virtual. Primera impresion atmosferica.",
        "primary_character": "narrator",
        "secondary_character": None,
        "trigger_event": "start_narrative",
        "conditions": {},
        "next_scene_default": "L1_S2_lucien_aparece",
        "branching_rules": {},
        "sequence_order": 1,
        "is_checkpoint": True,
        "is_active": True
    },

    # -------------------------------------------------------------------------
    # ESCENA 1.2: LUCIEN APARECE
    # -------------------------------------------------------------------------
    {
        "scene_id": "L1_S2_lucien_aparece",
        "chapter_id": "ch1_bienvenida",
        "title": "El Guardian del Umbral",
        "description": "Lucien se presenta. Primer contacto con el evaluador.",
        "primary_character": "lucien",
        "secondary_character": None,
        "trigger_event": "scene_complete:L1_S1_llegada",
        "conditions": {},
        "next_scene_default": "L1_S3_primera_prueba",
        "branching_rules": {},
        "sequence_order": 2,
        "is_checkpoint": False,
        "is_active": True
    },

    # -------------------------------------------------------------------------
    # ESCENA 1.3: PRIMERA PRUEBA DE LUCIEN
    # -------------------------------------------------------------------------
    {
        "scene_id": "L1_S3_primera_prueba",
        "chapter_id": "ch1_bienvenida",
        "title": "La Primera Evaluacion",
        "description": "Lucien hace su primera pregunta evaluativa.",
        "primary_character": "lucien",
        "secondary_character": None,
        "trigger_event": "scene_complete:L1_S2_lucien_aparece",
        "conditions": {},
        "next_scene_default": "L1_S4_reaccion_lucien",
        "branching_rules": {
            "conditions": [
                {"if": {"decision": "respuesta_impulsiva"}, "goto": "L1_S4a_lucien_impulsivo"},
                {"if": {"decision": "respuesta_reflexiva"}, "goto": "L1_S4b_lucien_reflexivo"},
                {"if": {"decision": "respuesta_directa"}, "goto": "L1_S4c_lucien_directo"}
            ],
            "default": "L1_S4_reaccion_lucien"
        },
        "sequence_order": 3,
        "is_checkpoint": False,
        "is_active": True
    },

    # -------------------------------------------------------------------------
    # ESCENAS 1.4 (VARIANTES): REACCION DE LUCIEN
    # -------------------------------------------------------------------------
    {
        "scene_id": "L1_S4_reaccion_lucien",
        "chapter_id": "ch1_bienvenida",
        "title": "La Evaluacion (Default)",
        "description": "Reaccion neutra de Lucien",
        "primary_character": "lucien",
        "secondary_character": None,
        "trigger_event": "scene_complete:L1_S3_primera_prueba",
        "conditions": {},
        "next_scene_default": "L1_S5_mencion_diana",
        "branching_rules": {},
        "sequence_order": 4,
        "is_checkpoint": False,
        "is_active": True
    },
    {
        "scene_id": "L1_S4a_lucien_impulsivo",
        "chapter_id": "ch1_bienvenida",
        "title": "La Evaluacion (Impulsivo)",
        "description": "Lucien nota la impulsividad",
        "primary_character": "lucien",
        "secondary_character": None,
        "trigger_event": "branch:impulsivo",
        "conditions": {"pattern": {"has": "impulsive"}},
        "next_scene_default": "L1_S5_mencion_diana",
        "branching_rules": {},
        "sequence_order": 4,
        "is_checkpoint": False,
        "is_active": True
    },
    {
        "scene_id": "L1_S4b_lucien_reflexivo",
        "chapter_id": "ch1_bienvenida",
        "title": "La Evaluacion (Reflexivo)",
        "description": "Lucien aprecia la reflexion",
        "primary_character": "lucien",
        "secondary_character": None,
        "trigger_event": "branch:reflexivo",
        "conditions": {"archetype": {"in": ["introspective", "analytical"]}},
        "next_scene_default": "L1_S5_mencion_diana",
        "branching_rules": {},
        "sequence_order": 4,
        "is_checkpoint": False,
        "is_active": True
    },
    {
        "scene_id": "L1_S4c_lucien_directo",
        "chapter_id": "ch1_bienvenida",
        "title": "La Evaluacion (Directo)",
        "description": "Lucien respeta la franqueza",
        "primary_character": "lucien",
        "secondary_character": None,
        "trigger_event": "branch:directo",
        "conditions": {"archetype": {"in": ["direct"]}},
        "next_scene_default": "L1_S5_mencion_diana",
        "branching_rules": {},
        "sequence_order": 4,
        "is_checkpoint": False,
        "is_active": True
    },

    # -------------------------------------------------------------------------
    # ESCENA 1.5: PRIMERA MENCION DE DIANA (PEAK MOMENT)
    # -------------------------------------------------------------------------
    {
        "scene_id": "L1_S5_mencion_diana",
        "chapter_id": "ch1_bienvenida",
        "title": "El Nombre que Cambia Todo",
        "description": "Lucien menciona a Diana por primera vez. Peak moment del nivel.",
        "primary_character": "lucien",
        "secondary_character": None,
        "trigger_event": "scene_complete:L1_S4",
        "conditions": {},
        "next_scene_default": "L1_S6_vistazo_diana",
        "branching_rules": {},
        "atmosphere_override": {
            "emotional": "Un cambio sutil en el aire. Lucien baja la voz. El jazz parece mas lento."
        },
        "sequence_order": 5,
        "is_checkpoint": True,
        "is_active": True
    },

    # -------------------------------------------------------------------------
    # ESCENA 1.6: PRIMER VISTAZO DE DIANA
    # -------------------------------------------------------------------------
    {
        "scene_id": "L1_S6_vistazo_diana",
        "chapter_id": "ch1_bienvenida",
        "title": "La Silueta en las Sombras",
        "description": "El usuario percibe a Diana por primera vez. No la ve claramente.",
        "primary_character": "narrator",
        "secondary_character": "diana",
        "trigger_event": "scene_complete:L1_S5_mencion_diana",
        "conditions": {},
        "next_scene_default": "L1_S7_decision_continuar",
        "branching_rules": {},
        "atmosphere_override": {
            "visual": "Una silueta al fondo del bar. Cabello oscuro, el reflejo de una copa. Solo un instante.",
            "emotional": "El corazon acelera sin razon. Algo ancestral reconoce algo."
        },
        "sequence_order": 6,
        "is_checkpoint": False,
        "is_active": True
    },

    # -------------------------------------------------------------------------
    # ESCENA 1.7: DECISION DE CONTINUAR
    # -------------------------------------------------------------------------
    {
        "scene_id": "L1_S7_decision_continuar",
        "chapter_id": "ch1_bienvenida",
        "title": "El Primer Umbral",
        "description": "Lucien ofrece la opcion de continuar o retirarse.",
        "primary_character": "lucien",
        "secondary_character": None,
        "trigger_event": "scene_complete:L1_S6_vistazo_diana",
        "conditions": {},
        "next_scene_default": "L1_S8_cierre_nivel",
        "branching_rules": {
            "conditions": [
                {"if": {"decision": "continuar_curiosidad"}, "goto": "L1_S8_cierre_curioso"},
                {"if": {"decision": "continuar_determinado"}, "goto": "L1_S8_cierre_determinado"},
                {"if": {"decision": "retirarse"}, "goto": "L1_S8_cierre_retirada"}
            ],
            "default": "L1_S8_cierre_nivel"
        },
        "sequence_order": 7,
        "is_checkpoint": True,
        "is_active": True
    },

    # -------------------------------------------------------------------------
    # ESCENA 1.8: CIERRE DEL NIVEL (VARIANTES)
    # -------------------------------------------------------------------------
    {
        "scene_id": "L1_S8_cierre_nivel",
        "chapter_id": "ch1_bienvenida",
        "title": "El Primer Paso",
        "description": "Cierre del nivel 1 (default)",
        "primary_character": "lucien",
        "secondary_character": None,
        "trigger_event": "scene_complete:L1_S7_decision_continuar",
        "conditions": {},
        "next_scene_default": None,
        "branching_rules": {},
        "sequence_order": 8,
        "is_checkpoint": True,
        "is_active": True
    },
    {
        "scene_id": "L1_S8_cierre_curioso",
        "chapter_id": "ch1_bienvenida",
        "title": "El Primer Paso (Curioso)",
        "description": "Cierre para usuarios curiosos",
        "primary_character": "lucien",
        "secondary_character": None,
        "trigger_event": "branch:curioso",
        "conditions": {},
        "next_scene_default": None,
        "branching_rules": {},
        "sequence_order": 8,
        "is_checkpoint": True,
        "is_active": True
    },
    {
        "scene_id": "L1_S8_cierre_determinado",
        "chapter_id": "ch1_bienvenida",
        "title": "El Primer Paso (Determinado)",
        "description": "Cierre para usuarios determinados",
        "primary_character": "lucien",
        "secondary_character": None,
        "trigger_event": "branch:determinado",
        "conditions": {},
        "next_scene_default": None,
        "branching_rules": {},
        "sequence_order": 8,
        "is_checkpoint": True,
        "is_active": True
    },
    {
        "scene_id": "L1_S8_cierre_retirada",
        "chapter_id": "ch1_bienvenida",
        "title": "El Umbral Rechazado",
        "description": "El usuario decide no continuar (mantiene opcion de volver)",
        "primary_character": "lucien",
        "secondary_character": None,
        "trigger_event": "branch:retirada",
        "conditions": {},
        "next_scene_default": None,
        "branching_rules": {},
        "sequence_order": 8,
        "is_checkpoint": True,
        "is_active": True
    }
]

# =============================================================================
# DIALOGUES LEVEL 1
# =============================================================================

LEVEL_1_DIALOGUES = [
    # =========================================================================
    # ESCENA 1.1: LLEGADA - NARRADOR
    # =========================================================================
    {
        "dialogue_id": "L1_D1_llegada_1",
        "scene_id": "L1_S1_llegada",
        "character": "narrator",
        "base_text": "La puerta se abre sin que la toques.\n\nAdentro, el tiempo parece haberse detenido en alguna noche de 1947. Un bar de otra epoca, donde las sombras tienen mas historia que la mayoria de las personas.",
        "archetype_variants": {
            "introspective": "La puerta se abre sin que la toques.\n\nTe preguntas cuanto tiempo llevas caminando hacia este momento. El interior revela un bar de otra epoca, donde cada sombra parece guardar una pregunta que aun no has formulado.",
            "analytical": "La puerta se abre sin que la toques. Mecanismo neumatico, probablemente.\n\nAdentro, el diseno sugiere los anos 40. Art Deco con toques de penumbra deliberada. Cada elemento parece calculado para crear una atmosfera especifica.",
            "romantic": "La puerta se abre sin que la toques, como si te esperara.\n\nAdentro, el mundo que conocias deja de existir. Un bar banado en luz ambar, donde cada sombra podria esconder un secreto... o una promesa.",
            "direct": "La puerta se abre sola.\n\nBar antiguo. Poca luz. Humo de otra epoca que ya nadie fuma. Algo te dice que este lugar no aparece en ningun mapa."
        },
        "relationship_variants": {},
        "delivery_style": "dramatic",
        "typing_delay": 2.0,
        "media": None,
        "creates_memory": None,
        "sequence_order": 1,
        "requires_response": False,
        "is_active": True
    },
    {
        "dialogue_id": "L1_D1_llegada_2",
        "scene_id": "L1_S1_llegada",
        "character": "narrator",
        "base_text": "Un vaso de cristal te espera en la barra. El hielo aun no se ha derretido.\n\nAlguien sabia que vendrias.",
        "archetype_variants": {},
        "relationship_variants": {},
        "delivery_style": "normal",
        "typing_delay": 1.5,
        "media": None,
        "creates_memory": None,
        "sequence_order": 2,
        "requires_response": False,
        "is_active": True
    },

    # =========================================================================
    # ESCENA 1.2: LUCIEN APARECE
    # =========================================================================
    {
        "dialogue_id": "L1_D2_lucien_1",
        "scene_id": "L1_S2_lucien_aparece",
        "character": "lucien",
        "base_text": "Permitame presentarme.\n\nSoy Lucien. Podria decirse que... cuido de este lugar.",
        "archetype_variants": {},
        "relationship_variants": {},
        "delivery_style": "normal",
        "typing_delay": 1.0,
        "media": None,
        "creates_memory": None,
        "sequence_order": 1,
        "requires_response": False,
        "is_active": True
    },
    {
        "dialogue_id": "L1_D2_lucien_2",
        "scene_id": "L1_S2_lucien_aparece",
        "character": "lucien",
        "base_text": "Su presencia aqui no es coincidencia. Nadie llega a Los Kinkys por accidente.\n\nLa pregunta es... que lo trajo hasta el umbral.",
        "archetype_variants": {
            "introspective": "Su presencia aqui... intrigante. No todos encuentran esta puerta.\n\nPero encontrarla es solo el principio. La pregunta que importa es otra: que busca realmente?",
            "analytical": "Interesante. Sus pasos lo trajeron aqui con cierta... precision.\n\nPermitame observar: llego solo, sin mapa, sin invitacion explicita. Y sin embargo, aqui esta. Que le dice eso?",
            "romantic": "Hay algo en su mirada... Un anhelo que reconozco.\n\nEste lugar tiene la costumbre de atraer a quienes buscan algo mas profundo que lo obvio. Algo que quiza ni siquiera saben nombrar.",
            "direct": "Bien. Llego.\n\nNo perdere su tiempo con rodeos. Este lugar existe para quienes buscan algo especifico. La pregunta es simple: que quiere?"
        },
        "relationship_variants": {},
        "delivery_style": "normal",
        "typing_delay": 1.5,
        "media": None,
        "creates_memory": {
            "character": "lucien",
            "memory_type": "first_impression",
            "template": "Primera impresion: {archetype_hint}"
        },
        "sequence_order": 2,
        "requires_response": False,
        "is_active": True
    },

    # =========================================================================
    # ESCENA 1.3: PRIMERA PRUEBA
    # =========================================================================
    {
        "dialogue_id": "L1_D3_prueba_1",
        "scene_id": "L1_S3_primera_prueba",
        "character": "lucien",
        "base_text": "Si me permite observar... su respuesta revelara mas sobre su caracter de lo que quizas pretende mostrar.\n\nDigame: cuando enfrenta algo que desea pero no comprende, que hace primero?",
        "archetype_variants": {},
        "relationship_variants": {},
        "delivery_style": "normal",
        "typing_delay": 1.5,
        "media": None,
        "creates_memory": None,
        "sequence_order": 1,
        "requires_response": True,
        "is_active": True
    },

    # =========================================================================
    # OPCIONES DE LA PRIMERA PRUEBA
    # =========================================================================
    # Las opciones se definen en LEVEL_1_OPTIONS mas abajo

    # =========================================================================
    # ESCENA 1.4: REACCIONES DE LUCIEN (VARIANTES)
    # =========================================================================
    {
        "dialogue_id": "L1_D4_default",
        "scene_id": "L1_S4_reaccion_lucien",
        "character": "lucien",
        "base_text": "Su respuesta es... reveladora.\n\nTomese su tiempo. Este lugar no tiene prisa.",
        "archetype_variants": {},
        "relationship_variants": {},
        "delivery_style": "normal",
        "typing_delay": 1.0,
        "media": None,
        "creates_memory": None,
        "sequence_order": 1,
        "requires_response": False,
        "is_active": True
    },
    {
        "dialogue_id": "L1_D4a_impulsivo",
        "scene_id": "L1_S4a_lucien_impulsivo",
        "character": "lucien",
        "base_text": "Rapido. Muy rapido.\n\nLa impulsividad tiene su encanto, supongo. Aunque tambien sus... consecuencias. Aqui, cada decision tiene peso.",
        "archetype_variants": {},
        "relationship_variants": {},
        "delivery_style": "normal",
        "typing_delay": 1.0,
        "media": None,
        "creates_memory": {
            "character": "lucien",
            "memory_type": "behavior",
            "template": "Respondio impulsivamente en la primera prueba"
        },
        "sequence_order": 1,
        "requires_response": False,
        "is_active": True
    },
    {
        "dialogue_id": "L1_D4b_reflexivo",
        "scene_id": "L1_S4b_lucien_reflexivo",
        "character": "lucien",
        "base_text": "Debo admitir... eso fue inesperadamente perspicaz.\n\nQuizas hay mas sustancia en usted de la que inicialmente calcule. El tiempo lo dira.",
        "archetype_variants": {},
        "relationship_variants": {},
        "delivery_style": "normal",
        "typing_delay": 1.0,
        "media": None,
        "creates_memory": {
            "character": "lucien",
            "memory_type": "behavior",
            "template": "Mostro profundidad reflexiva desde el inicio"
        },
        "sequence_order": 1,
        "requires_response": False,
        "is_active": True
    },
    {
        "dialogue_id": "L1_D4c_directo",
        "scene_id": "L1_S4c_lucien_directo",
        "character": "lucien",
        "base_text": "Directo. Sin adornos.\n\nAprecio la honestidad, aunque sea rara en este lugar. Veremos si esa franqueza sobrevive a lo que viene.",
        "archetype_variants": {},
        "relationship_variants": {},
        "delivery_style": "normal",
        "typing_delay": 1.0,
        "media": None,
        "creates_memory": {
            "character": "lucien",
            "memory_type": "behavior",
            "template": "Fue brutalmente honesto desde el primer momento"
        },
        "sequence_order": 1,
        "requires_response": False,
        "is_active": True
    },

    # =========================================================================
    # ESCENA 1.5: MENCION DE DIANA (PEAK MOMENT)
    # =========================================================================
    {
        "dialogue_id": "L1_D5_diana_1",
        "scene_id": "L1_S5_mencion_diana",
        "character": "lucien",
        "base_text": "Hay alguien aqui... alguien a quien quizas le interese conocerlo.",
        "archetype_variants": {},
        "relationship_variants": {},
        "delivery_style": "whisper",
        "typing_delay": 2.0,
        "media": None,
        "creates_memory": None,
        "sequence_order": 1,
        "requires_response": False,
        "is_active": True
    },
    {
        "dialogue_id": "L1_D5_diana_2",
        "scene_id": "L1_S5_mencion_diana",
        "character": "lucien",
        "base_text": "Diana.\n\nEse es su nombre. Y ese nombre... no se comparte a la ligera.",
        "archetype_variants": {
            "introspective": "Diana.\n\nEl nombre resuena de una manera que no puedo explicar. Y sospecho que usted tampoco podria, aunque lo intentara.",
            "analytical": "Diana.\n\nUn nombre que en mitologia representa a la cazadora. Aunque aqui... los roles son mas complejos de lo que parecen.",
            "romantic": "Diana.\n\nHay nombres que cambian algo cuando los escuchas. Este es uno de ellos. Y ahora usted lo sabe.",
            "direct": "Diana.\n\nRecuerde ese nombre. Puede que sea lo mas importante que escuche esta noche."
        },
        "relationship_variants": {},
        "delivery_style": "dramatic",
        "typing_delay": 2.5,
        "media": None,
        "creates_memory": {
            "character": "lucien",
            "memory_type": "milestone",
            "template": "Primera vez que escucho el nombre de Diana"
        },
        "sequence_order": 2,
        "requires_response": False,
        "is_active": True
    },

    # =========================================================================
    # ESCENA 1.6: VISTAZO DE DIANA
    # =========================================================================
    {
        "dialogue_id": "L1_D6_vistazo_1",
        "scene_id": "L1_S6_vistazo_diana",
        "character": "narrator",
        "base_text": "Al fondo del bar, entre las sombras...\n\nUna silueta. Cabello oscuro cayendo sobre un hombro. El reflejo de una copa de vino tinto. Solo un instante.",
        "archetype_variants": {
            "introspective": "Al fondo del bar, tu mirada se desvio sin que lo decidieras.\n\nUna silueta. La curva de un cuello. Un gesto que no puedes descifrar pero que te resulta... familiar. De algun lugar que no recuerdas.",
            "analytical": "Movimiento en tu vision periferica. Al fondo, parcialmente oculta por una columna.\n\nUna figura femenina. Postura relajada pero atenta. Te esta observando tambien? Imposible saberlo con esta luz.",
            "romantic": "El aire cambio.\n\nY entonces la viste. Solo una fraccion de segundo, pero suficiente. Cabello que absorbia la poca luz. Una sonrisa que no estaba dirigida a ti, pero que sentiste como si lo estuviera.",
            "direct": "Alguien al fondo.\n\nMujer. Observando. No se esconde, pero tampoco se muestra. Sabe que la viste. Y no le importa."
        },
        "relationship_variants": {},
        "delivery_style": "dramatic",
        "typing_delay": 2.0,
        "media": None,
        "creates_memory": {
            "character": "diana",
            "memory_type": "first_sight",
            "template": "Primer vistazo del usuario - reaccion: {reaction}"
        },
        "sequence_order": 1,
        "requires_response": False,
        "is_active": True
    },
    {
        "dialogue_id": "L1_D6_vistazo_2",
        "scene_id": "L1_S6_vistazo_diana",
        "character": "narrator",
        "base_text": "Cuando volviste a mirar, ya no estaba.\n\nO quizas nunca estuvo. En Los Kinkys, la linea entre lo real y lo deseado es... difusa.",
        "archetype_variants": {},
        "relationship_variants": {},
        "delivery_style": "normal",
        "typing_delay": 1.5,
        "media": None,
        "creates_memory": None,
        "sequence_order": 2,
        "requires_response": False,
        "is_active": True
    },

    # =========================================================================
    # ESCENA 1.7: DECISION DE CONTINUAR
    # =========================================================================
    {
        "dialogue_id": "L1_D7_decision_1",
        "scene_id": "L1_S7_decision_continuar",
        "character": "lucien",
        "base_text": "Ahora conoce un nombre. Ha vislumbrado una sombra.\n\nLa pregunta es simple: desea saber mas?",
        "archetype_variants": {
            "introspective": "Ha sentido algo esta noche. Algo que no puede nombrar.\n\nPero antes de continuar, debe preguntarse: esta preparado para las respuestas, o prefiere quedarse con las preguntas?",
            "analytical": "Los datos que tiene son insuficientes. Un nombre, una silueta, mis palabras.\n\nPero a veces, la falta de informacion es precisamente el punto. Que decide?",
            "romantic": "Algo cambio en usted cuando la vio. Lo note.\n\nEse momento... puede ser el principio de algo. O puede quedarse en el misterio de una noche. Depende de usted.",
            "direct": "Diana existe. La vio.\n\nPuede irse ahora y olvidar esto. O puede quedarse y ver que pasa. No hay opcion intermedia."
        },
        "relationship_variants": {},
        "delivery_style": "normal",
        "typing_delay": 1.5,
        "media": None,
        "creates_memory": None,
        "sequence_order": 1,
        "requires_response": True,
        "is_active": True
    },

    # =========================================================================
    # ESCENA 1.8: CIERRES (VARIANTES)
    # =========================================================================
    {
        "dialogue_id": "L1_D8_default",
        "scene_id": "L1_S8_cierre_nivel",
        "character": "lucien",
        "base_text": "Bien.\n\nEl primer paso esta dado. Ahora... todo depende de como camine.",
        "archetype_variants": {},
        "relationship_variants": {},
        "delivery_style": "normal",
        "typing_delay": 1.5,
        "media": None,
        "creates_memory": None,
        "sequence_order": 1,
        "requires_response": False,
        "is_active": True
    },
    {
        "dialogue_id": "L1_D8_curioso",
        "scene_id": "L1_S8_cierre_curioso",
        "character": "lucien",
        "base_text": "La curiosidad... es un buen motor.\n\nPero recuerde: en este lugar, las respuestas vienen con sus propias preguntas. Y Diana... Diana tiene muchas de ambas.",
        "archetype_variants": {},
        "relationship_variants": {},
        "delivery_style": "normal",
        "typing_delay": 1.5,
        "media": None,
        "creates_memory": {
            "character": "lucien",
            "memory_type": "motivation",
            "template": "Eligio continuar por curiosidad"
        },
        "sequence_order": 1,
        "requires_response": False,
        "is_active": True
    },
    {
        "dialogue_id": "L1_D8_determinado",
        "scene_id": "L1_S8_cierre_determinado",
        "character": "lucien",
        "base_text": "Determinacion. Interesante.\n\nEspero que esa resolucion no sea solo bravuconeria. Diana sabe distinguir la diferencia. Y yo tambien.",
        "archetype_variants": {},
        "relationship_variants": {},
        "delivery_style": "normal",
        "typing_delay": 1.5,
        "media": None,
        "creates_memory": {
            "character": "lucien",
            "memory_type": "motivation",
            "template": "Mostro determinacion firme para continuar"
        },
        "sequence_order": 1,
        "requires_response": False,
        "is_active": True
    },
    {
        "dialogue_id": "L1_D8_retirada",
        "scene_id": "L1_S8_cierre_retirada",
        "character": "lucien",
        "base_text": "Una decision... prudente, quizas.\n\nLa puerta siempre estara aqui. Si algun dia cambia de opinion, el vaso seguira esperando en la barra. El hielo nunca se derrite en Los Kinkys.",
        "archetype_variants": {},
        "relationship_variants": {},
        "delivery_style": "normal",
        "typing_delay": 1.5,
        "media": None,
        "creates_memory": {
            "character": "lucien",
            "memory_type": "choice",
            "template": "Eligio retirarse en el primer umbral"
        },
        "sequence_order": 1,
        "requires_response": False,
        "is_active": True
    }
]

# =============================================================================
# OPTIONS LEVEL 1
# =============================================================================

LEVEL_1_OPTIONS = [
    # =========================================================================
    # OPCIONES ESCENA 1.3: PRIMERA PRUEBA
    # =========================================================================
    {
        "option_id": "L1_O3_introspectivo",
        "dialogue_id": "L1_D3_prueba_1",
        "text": "Me detengo a observar. Intento entender antes de actuar.",
        "text_variants": {
            "introspective": "Necesito comprender que significa para mi, antes de decidir.",
            "analytical": "Primero recopilo informacion. Despues analizo patrones."
        },
        "associated_archetype": "introspective",
        "is_default": False,
        "visibility_conditions": None,
        "immediate_effects": {
            "archetype_introspective": 15,
            "lucien_respect": 3
        },
        "delayed_effects": {
            "trigger_at_level": 2,
            "effect": {"unlock": "lucien_appreciates_depth"}
        },
        "next_dialogue_id": None,
        "next_scene_id": "L1_S4b_lucien_reflexivo",
        "creates_memory": {
            "character": "lucien",
            "memory_type": "first_choice",
            "content": "eligio reflexionar antes de actuar"
        },
        "display_order": 1,
        "is_active": True
    },
    {
        "option_id": "L1_O3_directo",
        "dialogue_id": "L1_D3_prueba_1",
        "text": "Voy directo. Si quiero algo, lo busco.",
        "text_variants": {
            "direct": "No pierdo tiempo. Quiero, lo tomo."
        },
        "associated_archetype": "direct",
        "is_default": False,
        "visibility_conditions": None,
        "immediate_effects": {
            "archetype_direct": 15,
            "lucien_respect": 2
        },
        "delayed_effects": None,
        "next_dialogue_id": None,
        "next_scene_id": "L1_S4c_lucien_directo",
        "creates_memory": {
            "character": "lucien",
            "memory_type": "first_choice",
            "content": "fue directo y sin rodeos desde el inicio"
        },
        "display_order": 2,
        "is_active": True
    },
    {
        "option_id": "L1_O3_romantico",
        "dialogue_id": "L1_D3_prueba_1",
        "text": "Me dejo llevar. El misterio es parte del encanto.",
        "text_variants": {
            "romantic": "El no saber es hermoso. Me entrego al momento."
        },
        "associated_archetype": "romantic",
        "is_default": False,
        "visibility_conditions": None,
        "immediate_effects": {
            "archetype_romantic": 15,
            "diana_trust": 2
        },
        "delayed_effects": {
            "trigger_at_level": 3,
            "effect": {"unlock": "diana_appreciates_surrender"}
        },
        "next_dialogue_id": None,
        "next_scene_id": "L1_S4_reaccion_lucien",
        "creates_memory": {
            "character": "diana",
            "memory_type": "first_impression",
            "content": "se rindio al misterio sin resistencia"
        },
        "display_order": 3,
        "is_active": True
    },
    {
        "option_id": "L1_O3_analitico",
        "dialogue_id": "L1_D3_prueba_1",
        "text": "Busco el patron. Todo tiene logica si miras suficiente.",
        "text_variants": {
            "analytical": "Descompongo el problema. Hay reglas, solo hay que encontrarlas."
        },
        "associated_archetype": "analytical",
        "is_default": False,
        "visibility_conditions": None,
        "immediate_effects": {
            "archetype_analytical": 15,
            "lucien_respect": 4
        },
        "delayed_effects": None,
        "next_dialogue_id": None,
        "next_scene_id": "L1_S4b_lucien_reflexivo",
        "creates_memory": {
            "character": "lucien",
            "memory_type": "first_choice",
            "content": "busca patrones y reglas en todo"
        },
        "display_order": 4,
        "is_active": True
    },

    # =========================================================================
    # OPCIONES ESCENA 1.7: DECISION DE CONTINUAR
    # =========================================================================
    {
        "option_id": "L1_O7_curiosidad",
        "dialogue_id": "L1_D7_decision_1",
        "text": "Quiero saber mas. Necesito entender.",
        "text_variants": {
            "introspective": "Hay algo aqui que me llama. Necesito explorar que es.",
            "analytical": "Los datos son insuficientes. Requiero mas informacion."
        },
        "associated_archetype": "introspective",
        "is_default": False,
        "visibility_conditions": None,
        "immediate_effects": {
            "archetype_introspective": 5,
            "add_flag": {"type": "choices", "name": "chose_curiosity"}
        },
        "delayed_effects": None,
        "next_dialogue_id": None,
        "next_scene_id": "L1_S8_cierre_curioso",
        "creates_memory": None,
        "display_order": 1,
        "is_active": True
    },
    {
        "option_id": "L1_O7_determinacion",
        "dialogue_id": "L1_D7_decision_1",
        "text": "Estoy listo. Quiero conocer a Diana.",
        "text_variants": {
            "direct": "No vine a dudar. Llévame con ella.",
            "romantic": "Senti algo. Quiero saber si es real."
        },
        "associated_archetype": "direct",
        "is_default": True,
        "visibility_conditions": None,
        "immediate_effects": {
            "archetype_direct": 5,
            "diana_trust": 2,
            "add_flag": {"type": "choices", "name": "chose_determination"}
        },
        "delayed_effects": None,
        "next_dialogue_id": None,
        "next_scene_id": "L1_S8_cierre_determinado",
        "creates_memory": {
            "character": "lucien",
            "memory_type": "milestone",
            "content": "mostro determinacion al pedir conocer a Diana"
        },
        "display_order": 2,
        "is_active": True
    },
    {
        "option_id": "L1_O7_retiro",
        "dialogue_id": "L1_D7_decision_1",
        "text": "Necesito pensarlo. Quizas en otro momento.",
        "text_variants": {},
        "associated_archetype": None,
        "is_default": False,
        "visibility_conditions": None,
        "immediate_effects": {
            "add_flag": {"type": "choices", "name": "chose_retreat"}
        },
        "delayed_effects": {
            "trigger_at_level": 1,
            "effect": {"unlock": "return_option"}
        },
        "next_dialogue_id": None,
        "next_scene_id": "L1_S8_cierre_retirada",
        "creates_memory": {
            "character": "lucien",
            "memory_type": "choice",
            "content": "eligio retirarse en el primer umbral"
        },
        "display_order": 3,
        "is_active": True
    }
]
