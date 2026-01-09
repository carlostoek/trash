"""
Contenido narrativo Level 2 - Profundizacion y Misiones de Observacion.

Este nivel desarrolla:
- Lucien comienza a evaluar mas profundamente
- Primeras misiones/pruebas narrativas
- Diana aparece mas, pero sigue siendo enigmatica
- El usuario empieza a revelar su arquetipo dominante
- Sistema de memoria: Diana/Lucien recuerdan decisiones

Tempo emocional: Andante (caminando, desarrollando)
Peak moment: Primera interaccion directa con Diana
Breathing room: Si (momentos de reflexion)
"""

# =============================================================================
# CHAPTER 2: PROFUNDIZACION - LAS PRUEBAS
# =============================================================================

LEVEL_2_CHAPTERS = [
    {
        "chapter_id": "ch2_profundizacion",
        "title": "Las Pruebas",
        "subtitle": "Lucien observa. Diana espera. Tu decides.",
        "required_level": 2,
        "sequence_order": 2,
        "atmosphere": {
            "visual": "El mismo bar, pero ahora notas detalles: fotos antiguas en las paredes, nombres grabados en la barra, una escalera que sube hacia la oscuridad.",
            "auditory": "La musica cambio. Chet Baker cantando sobre amor perdido. El silencio entre canciones pesa mas.",
            "tactile": "El terciopelo de la butaca ahora se siente familiar. El vaso se llena solo cuando no miras.",
            "olfactory": "Hay un nuevo aroma. Gardenia. Viene de alguna parte del bar.",
            "emotional": "Familiaridad tentativa. Como estar en un sueno que empiezas a reconocer."
        },
        "emotional_tempo": "andante",
        "peak_moment": "Diana habla directamente al usuario por primera vez",
        "breathing_room": True,
        "is_active": True
    }
]

# =============================================================================
# SCENES LEVEL 2
# =============================================================================

LEVEL_2_SCENES = [
    # -------------------------------------------------------------------------
    # ESCENA 2.1: REGRESO A LOS KINKYS
    # -------------------------------------------------------------------------
    {
        "scene_id": "L2_S1_regreso",
        "chapter_id": "ch2_profundizacion",
        "title": "El Regreso",
        "description": "El usuario regresa a Los Kinkys. Lucien recuerda.",
        "primary_character": "lucien",
        "secondary_character": None,
        "trigger_event": "start_level_2",
        "conditions": {"level": {">=": 2}},
        "next_scene_default": "L2_S2_memoria_lucien",
        "branching_rules": {},
        "sequence_order": 1,
        "is_checkpoint": True,
        "is_active": True
    },

    # -------------------------------------------------------------------------
    # ESCENA 2.2: LUCIEN RECUERDA (MEMORIA DINAMICA)
    # -------------------------------------------------------------------------
    {
        "scene_id": "L2_S2_memoria_lucien",
        "chapter_id": "ch2_profundizacion",
        "title": "El Guardian Recuerda",
        "description": "Lucien hace referencia a la decision del Level 1.",
        "primary_character": "lucien",
        "secondary_character": None,
        "trigger_event": "scene_complete:L2_S1_regreso",
        "conditions": {},
        "next_scene_default": "L2_S3_mision_observacion",
        "branching_rules": {
            "conditions": [
                {"if": {"flags": {"has": "chose_curiosity"}}, "goto": "L2_S2a_recuerda_curioso"},
                {"if": {"flags": {"has": "chose_determination"}}, "goto": "L2_S2b_recuerda_determinado"},
                {"if": {"flags": {"has": "chose_retreat"}}, "goto": "L2_S2c_recuerda_retirada"}
            ],
            "default": "L2_S2_memoria_lucien"
        },
        "sequence_order": 2,
        "is_checkpoint": False,
        "is_active": True
    },
    {
        "scene_id": "L2_S2a_recuerda_curioso",
        "chapter_id": "ch2_profundizacion",
        "title": "El Guardian Recuerda (Curioso)",
        "description": "Lucien recuerda que eligio curiosidad",
        "primary_character": "lucien",
        "secondary_character": None,
        "trigger_event": "branch:curioso",
        "conditions": {"flags": {"has": "chose_curiosity"}},
        "next_scene_default": "L2_S3_mision_observacion",
        "branching_rules": {},
        "sequence_order": 2,
        "is_checkpoint": False,
        "is_active": True
    },
    {
        "scene_id": "L2_S2b_recuerda_determinado",
        "chapter_id": "ch2_profundizacion",
        "title": "El Guardian Recuerda (Determinado)",
        "description": "Lucien recuerda la determinacion",
        "primary_character": "lucien",
        "secondary_character": None,
        "trigger_event": "branch:determinado",
        "conditions": {"flags": {"has": "chose_determination"}},
        "next_scene_default": "L2_S3_mision_observacion",
        "branching_rules": {},
        "sequence_order": 2,
        "is_checkpoint": False,
        "is_active": True
    },
    {
        "scene_id": "L2_S2c_recuerda_retirada",
        "chapter_id": "ch2_profundizacion",
        "title": "El Guardian Recuerda (Regreso)",
        "description": "Lucien nota que regresaste despues de retirarte",
        "primary_character": "lucien",
        "secondary_character": None,
        "trigger_event": "branch:regreso_retirada",
        "conditions": {"flags": {"has": "chose_retreat"}},
        "next_scene_default": "L2_S3_mision_observacion",
        "branching_rules": {},
        "sequence_order": 2,
        "is_checkpoint": False,
        "is_active": True
    },

    # -------------------------------------------------------------------------
    # ESCENA 2.3: PRIMERA MISION DE OBSERVACION
    # -------------------------------------------------------------------------
    {
        "scene_id": "L2_S3_mision_observacion",
        "chapter_id": "ch2_profundizacion",
        "title": "La Primera Mision",
        "description": "Lucien propone una tarea: observar y reportar.",
        "primary_character": "lucien",
        "secondary_character": None,
        "trigger_event": "scene_complete:L2_S2",
        "conditions": {},
        "next_scene_default": "L2_S4_resultado_mision",
        "branching_rules": {},
        "sequence_order": 3,
        "is_checkpoint": True,
        "is_active": True
    },

    # -------------------------------------------------------------------------
    # ESCENA 2.4: RESULTADO DE LA MISION
    # -------------------------------------------------------------------------
    {
        "scene_id": "L2_S4_resultado_mision",
        "chapter_id": "ch2_profundizacion",
        "title": "El Reporte",
        "description": "Usuario reporta lo que observo (decision multiple)",
        "primary_character": "lucien",
        "secondary_character": None,
        "trigger_event": "mission_complete:observacion_1",
        "conditions": {},
        "next_scene_default": "L2_S5_evaluacion_lucien",
        "branching_rules": {
            "conditions": [
                {"if": {"decision": "reporte_detallado"}, "goto": "L2_S5a_analitico"},
                {"if": {"decision": "reporte_emocional"}, "goto": "L2_S5b_romantico"},
                {"if": {"decision": "reporte_esencial"}, "goto": "L2_S5c_directo"}
            ],
            "default": "L2_S5_evaluacion_lucien"
        },
        "sequence_order": 4,
        "is_checkpoint": False,
        "is_active": True
    },

    # -------------------------------------------------------------------------
    # ESCENA 2.5: EVALUACION DE LUCIEN (VARIANTES)
    # -------------------------------------------------------------------------
    {
        "scene_id": "L2_S5_evaluacion_lucien",
        "chapter_id": "ch2_profundizacion",
        "title": "La Evaluacion",
        "description": "Lucien evalua el reporte (default)",
        "primary_character": "lucien",
        "secondary_character": None,
        "trigger_event": "scene_complete:L2_S4",
        "conditions": {},
        "next_scene_default": "L2_S6_diana_aparece",
        "branching_rules": {},
        "sequence_order": 5,
        "is_checkpoint": False,
        "is_active": True
    },
    {
        "scene_id": "L2_S5a_analitico",
        "chapter_id": "ch2_profundizacion",
        "title": "La Evaluacion (Analitico)",
        "description": "Lucien aprecia el analisis detallado",
        "primary_character": "lucien",
        "secondary_character": None,
        "trigger_event": "branch:analitico",
        "conditions": {},
        "next_scene_default": "L2_S6_diana_aparece",
        "branching_rules": {},
        "sequence_order": 5,
        "is_checkpoint": False,
        "is_active": True
    },
    {
        "scene_id": "L2_S5b_romantico",
        "chapter_id": "ch2_profundizacion",
        "title": "La Evaluacion (Romantico)",
        "description": "Lucien nota la sensibilidad",
        "primary_character": "lucien",
        "secondary_character": None,
        "trigger_event": "branch:romantico",
        "conditions": {},
        "next_scene_default": "L2_S6_diana_aparece",
        "branching_rules": {},
        "sequence_order": 5,
        "is_checkpoint": False,
        "is_active": True
    },
    {
        "scene_id": "L2_S5c_directo",
        "chapter_id": "ch2_profundizacion",
        "title": "La Evaluacion (Directo)",
        "description": "Lucien aprecia la eficiencia",
        "primary_character": "lucien",
        "secondary_character": None,
        "trigger_event": "branch:directo",
        "conditions": {},
        "next_scene_default": "L2_S6_diana_aparece",
        "branching_rules": {},
        "sequence_order": 5,
        "is_checkpoint": False,
        "is_active": True
    },

    # -------------------------------------------------------------------------
    # ESCENA 2.6: DIANA APARECE (PEAK MOMENT)
    # -------------------------------------------------------------------------
    {
        "scene_id": "L2_S6_diana_aparece",
        "chapter_id": "ch2_profundizacion",
        "title": "El Momento",
        "description": "Diana aparece y habla por primera vez. Peak moment del nivel.",
        "primary_character": "diana",
        "secondary_character": "lucien",
        "trigger_event": "scene_complete:L2_S5",
        "conditions": {},
        "next_scene_default": "L2_S7_primera_conversacion",
        "branching_rules": {},
        "atmosphere_override": {
            "visual": "La luz cambia. El ambar se vuelve mas calido. Diana emerge de las sombras.",
            "olfactory": "Gardenia. Ahora sabes de donde viene.",
            "emotional": "El corazon se detiene. O al menos eso parece."
        },
        "sequence_order": 6,
        "is_checkpoint": True,
        "is_active": True
    },

    # -------------------------------------------------------------------------
    # ESCENA 2.7: PRIMERA CONVERSACION CON DIANA
    # -------------------------------------------------------------------------
    {
        "scene_id": "L2_S7_primera_conversacion",
        "chapter_id": "ch2_profundizacion",
        "title": "Primeras Palabras",
        "description": "Diana hace una pregunta al usuario. Decision crucial.",
        "primary_character": "diana",
        "secondary_character": None,
        "trigger_event": "scene_complete:L2_S6_diana_aparece",
        "conditions": {},
        "next_scene_default": "L2_S8_reaccion_diana",
        "branching_rules": {
            "conditions": [
                {"if": {"decision": "respuesta_profunda"}, "goto": "L2_S8a_diana_intrigada"},
                {"if": {"decision": "respuesta_directa"}, "goto": "L2_S8b_diana_respeta"},
                {"if": {"decision": "respuesta_romantica"}, "goto": "L2_S8c_diana_sonrie"}
            ],
            "default": "L2_S8_reaccion_diana"
        },
        "sequence_order": 7,
        "is_checkpoint": True,
        "is_active": True
    },

    # -------------------------------------------------------------------------
    # ESCENA 2.8: REACCION DE DIANA (VARIANTES)
    # -------------------------------------------------------------------------
    {
        "scene_id": "L2_S8_reaccion_diana",
        "chapter_id": "ch2_profundizacion",
        "title": "La Reaccion (Default)",
        "description": "Diana responde neutralmente",
        "primary_character": "diana",
        "secondary_character": None,
        "trigger_event": "scene_complete:L2_S7",
        "conditions": {},
        "next_scene_default": "L2_S9_cierre_nivel",
        "branching_rules": {},
        "sequence_order": 8,
        "is_checkpoint": False,
        "is_active": True
    },
    {
        "scene_id": "L2_S8a_diana_intrigada",
        "chapter_id": "ch2_profundizacion",
        "title": "Diana Intrigada",
        "description": "La respuesta profunda intriga a Diana",
        "primary_character": "diana",
        "secondary_character": None,
        "trigger_event": "branch:profundo",
        "conditions": {},
        "next_scene_default": "L2_S9_cierre_nivel",
        "branching_rules": {},
        "sequence_order": 8,
        "is_checkpoint": False,
        "is_active": True
    },
    {
        "scene_id": "L2_S8b_diana_respeta",
        "chapter_id": "ch2_profundizacion",
        "title": "Diana Respeta",
        "description": "La honestidad directa gana respeto",
        "primary_character": "diana",
        "secondary_character": None,
        "trigger_event": "branch:directo",
        "conditions": {},
        "next_scene_default": "L2_S9_cierre_nivel",
        "branching_rules": {},
        "sequence_order": 8,
        "is_checkpoint": False,
        "is_active": True
    },
    {
        "scene_id": "L2_S8c_diana_sonrie",
        "chapter_id": "ch2_profundizacion",
        "title": "Diana Sonrie",
        "description": "La respuesta romantica hace sonreir a Diana",
        "primary_character": "diana",
        "secondary_character": None,
        "trigger_event": "branch:romantico",
        "conditions": {},
        "next_scene_default": "L2_S9_cierre_nivel",
        "branching_rules": {},
        "sequence_order": 8,
        "is_checkpoint": False,
        "is_active": True
    },

    # -------------------------------------------------------------------------
    # ESCENA 2.9: CIERRE DEL NIVEL 2
    # -------------------------------------------------------------------------
    {
        "scene_id": "L2_S9_cierre_nivel",
        "chapter_id": "ch2_profundizacion",
        "title": "El Segundo Umbral",
        "description": "Cierre del nivel 2, preparacion para nivel 3",
        "primary_character": "diana",
        "secondary_character": "lucien",
        "trigger_event": "scene_complete:L2_S8",
        "conditions": {},
        "next_scene_default": None,
        "branching_rules": {},
        "sequence_order": 9,
        "is_checkpoint": True,
        "is_active": True
    }
]

# =============================================================================
# DIALOGUES LEVEL 2
# =============================================================================

LEVEL_2_DIALOGUES = [
    # =========================================================================
    # ESCENA 2.1: REGRESO
    # =========================================================================
    {
        "dialogue_id": "L2_D1_regreso_1",
        "scene_id": "L2_S1_regreso",
        "character": "narrator",
        "base_text": "La puerta se abre antes de que la toques. Otra vez.\n\nPero esta vez, algo es diferente. El bar te reconoce.",
        "archetype_variants": {
            "introspective": "La puerta se abre antes de que la toques.\n\nPero esta vez, en lugar de sorpresa, sientes algo parecido a volver a casa. Una casa que apenas conoces, pero que parece conocerte.",
            "analytical": "La puerta se abre. Mismo mecanismo. Misma precision.\n\nPero tu percepcion ha cambiado. Notas detalles que antes pasaste por alto. Fotos. Nombres. Una escalera.",
            "romantic": "La puerta se abre, y con ella, una anticipacion que no sabias que guardabas.\n\nHay un aroma nuevo. Gardenia. Y una esperanza que no quieres nombrar.",
            "direct": "La puerta. El bar. Todo igual.\n\nPero tu no eres el mismo. Y ellos lo saben."
        },
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
        "dialogue_id": "L2_D1_regreso_2",
        "scene_id": "L2_S1_regreso",
        "character": "lucien",
        "base_text": "Volvio.\n\nNo muchos lo hacen. Y menos con esa... determinacion en la mirada.",
        "archetype_variants": {},
        "relationship_variants": {},
        "delivery_style": "normal",
        "typing_delay": 1.0,
        "media": None,
        "creates_memory": None,
        "sequence_order": 2,
        "requires_response": False,
        "is_active": True
    },

    # =========================================================================
    # ESCENA 2.2: MEMORIA DE LUCIEN (VARIANTES)
    # =========================================================================
    {
        "dialogue_id": "L2_D2_memoria_curioso",
        "scene_id": "L2_S2a_recuerda_curioso",
        "character": "lucien",
        "base_text": "Recuerdo su ultima visita. Eligio la curiosidad sobre la certeza.\n\nUna decision interesante. Diana tambien lo noto.",
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
        "dialogue_id": "L2_D2_memoria_determinado",
        "scene_id": "L2_S2b_recuerda_determinado",
        "character": "lucien",
        "base_text": "Recuerdo su determinacion. Pidio conocer a Diana sin titubear.\n\nEso... no pasa desapercibido aqui.",
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
        "dialogue_id": "L2_D2_memoria_retirada",
        "scene_id": "L2_S2c_recuerda_retirada",
        "character": "lucien",
        "base_text": "Ah... el que se fue.\n\nPero aqui esta. De vuelta. Interesante. A veces la retirada es solo una pausa para tomar impulso.",
        "archetype_variants": {},
        "relationship_variants": {},
        "delivery_style": "normal",
        "typing_delay": 1.5,
        "media": None,
        "creates_memory": {
            "character": "lucien",
            "memory_type": "return",
            "template": "Regreso despues de retirarse inicialmente"
        },
        "sequence_order": 1,
        "requires_response": False,
        "is_active": True
    },

    # =========================================================================
    # ESCENA 2.3: MISION DE OBSERVACION
    # =========================================================================
    {
        "dialogue_id": "L2_D3_mision_1",
        "scene_id": "L2_S3_mision_observacion",
        "character": "lucien",
        "base_text": "Antes de que pueda presentarlo formalmente a Diana... hay algo que debe hacer.\n\nUna pequena prueba. Nada complicado.",
        "archetype_variants": {
            "introspective": "Diana no se muestra a cualquiera. Y yo necesito saber si usted... ve.\n\nNo me refiero a ver con los ojos. Me refiero a percibir. A notar lo que otros pasan por alto.",
            "analytical": "Necesito datos sobre usted. No los que puedo obtener observandolo directamente.\n\nNecesito ver como procesa informacion. Como filtra lo relevante de lo accesorio.",
            "romantic": "Diana me pregunto algo sobre usted. Y no supe responderle.\n\nAsí que le propongo algo: una pequeña mision. Algo que me ayude a responder su pregunta.",
            "direct": "Voy a ser claro: Diana quiere saber mas. Yo tambien.\n\nAsí que hara algo por nosotros. Observara. Y despues, me contara lo que vio."
        },
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
        "dialogue_id": "L2_D3_mision_2",
        "scene_id": "L2_S3_mision_observacion",
        "character": "lucien",
        "base_text": "Durante las proximas horas, preste atencion a lo que le rodea. A las conversaciones que escucha. A los gestos que nota.\n\nDespues, vuelva y cuenteme lo que observo.",
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
    # ESCENA 2.4: RESULTADO DE LA MISION
    # =========================================================================
    {
        "dialogue_id": "L2_D4_resultado_1",
        "scene_id": "L2_S4_resultado_mision",
        "character": "lucien",
        "base_text": "Ha vuelto. Bien.\n\nCuenteme: que observo?",
        "archetype_variants": {},
        "relationship_variants": {},
        "delivery_style": "normal",
        "typing_delay": 1.0,
        "media": None,
        "creates_memory": None,
        "sequence_order": 1,
        "requires_response": True,
        "is_active": True
    },

    # =========================================================================
    # ESCENA 2.5: EVALUACIONES DE LUCIEN (VARIANTES)
    # =========================================================================
    {
        "dialogue_id": "L2_D5_default",
        "scene_id": "L2_S5_evaluacion_lucien",
        "character": "lucien",
        "base_text": "Interesante perspectiva.\n\nLe contare algo: Diana estaba observando mientras usted observaba. Y lo que vio... le gusto.",
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
        "dialogue_id": "L2_D5_analitico",
        "scene_id": "L2_S5a_analitico",
        "character": "lucien",
        "base_text": "Preciso. Detallado. Casi... quirurgico.\n\nNo muchos ven los patrones que usted noto. Diana apreciara eso. Ella tambien tiene ojo para los detalles.",
        "archetype_variants": {},
        "relationship_variants": {},
        "delivery_style": "normal",
        "typing_delay": 1.5,
        "media": None,
        "creates_memory": {
            "character": "lucien",
            "memory_type": "evaluation",
            "template": "Demostro capacidad analitica excepcional en la mision"
        },
        "sequence_order": 1,
        "requires_response": False,
        "is_active": True
    },
    {
        "dialogue_id": "L2_D5_romantico",
        "scene_id": "L2_S5b_romantico",
        "character": "lucien",
        "base_text": "Usted no solo observo. Sintio.\n\nEso es... inesperado. Y Diana, entre nosotros, valora la sensibilidad mas de lo que admite.",
        "archetype_variants": {},
        "relationship_variants": {},
        "delivery_style": "normal",
        "typing_delay": 1.5,
        "media": None,
        "creates_memory": {
            "character": "lucien",
            "memory_type": "evaluation",
            "template": "Mostro profunda sensibilidad emocional en la mision"
        },
        "sequence_order": 1,
        "requires_response": False,
        "is_active": True
    },
    {
        "dialogue_id": "L2_D5_directo",
        "scene_id": "L2_S5c_directo",
        "character": "lucien",
        "base_text": "Al punto. Sin adornos. Eficiente.\n\nHay virtud en eso. Diana prefiere la claridad a la florura. Y usted... tiene claridad.",
        "archetype_variants": {},
        "relationship_variants": {},
        "delivery_style": "normal",
        "typing_delay": 1.5,
        "media": None,
        "creates_memory": {
            "character": "lucien",
            "memory_type": "evaluation",
            "template": "Fue directo y eficiente en su reporte"
        },
        "sequence_order": 1,
        "requires_response": False,
        "is_active": True
    },

    # =========================================================================
    # ESCENA 2.6: DIANA APARECE (PEAK MOMENT)
    # =========================================================================
    {
        "dialogue_id": "L2_D6_diana_1",
        "scene_id": "L2_S6_diana_aparece",
        "character": "narrator",
        "base_text": "La luz cambia.\n\nNo es un truco de iluminacion. Es como si el aire mismo se volviera mas denso. Mas presente.",
        "archetype_variants": {},
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
        "dialogue_id": "L2_D6_diana_2",
        "scene_id": "L2_S6_diana_aparece",
        "character": "diana",
        "base_text": "Así que tu eres el curioso que ha estado visitando mi bar.",
        "archetype_variants": {
            "introspective": "Así que tu eres el que piensa demasiado y decide poco.\n\n...Me identifico.",
            "analytical": "El observador. El que busca patrones en el caos.\n\nDime, has encontrado alguno?",
            "romantic": "El romantico. Puedo verlo en como me miras.\n\nNo te preocupes. No es algo malo.",
            "direct": "Directo. Me gusta eso.\n\nLucien dijo que no perdias el tiempo. Veo que tenia razon."
        },
        "relationship_variants": {},
        "delivery_style": "dramatic",
        "typing_delay": 2.5,
        "media": None,
        "creates_memory": {
            "character": "diana",
            "memory_type": "first_contact",
            "template": "Primera vez que hablo directamente con el usuario"
        },
        "sequence_order": 2,
        "requires_response": False,
        "is_active": True
    },

    # =========================================================================
    # ESCENA 2.7: PRIMERA CONVERSACION CON DIANA
    # =========================================================================
    {
        "dialogue_id": "L2_D7_pregunta_1",
        "scene_id": "L2_S7_primera_conversacion",
        "character": "diana",
        "base_text": "Antes de que sigamos... necesito saber algo.\n\nQue buscas aqui? Y no me digas 'a ti'. Eso ya lo se.",
        "archetype_variants": {
            "introspective": "Hay una pregunta que llevas dentro. La siento.\n\nNo me refiero a lo que quieres de mi. Me refiero a lo que buscas en ti.",
            "analytical": "Has analizado este lugar. Me has analizado a mi, probablemente.\n\nPero la verdadera pregunta es: que esperas encontrar cuando termines de analizar?",
            "romantic": "Tus ojos dicen mucho. Pero quiero escucharlo de tus labios.\n\nQue es lo que realmente anhelas?",
            "direct": "Sin rodeos: que quieres?\n\nY no me refiero a esta noche. Me refiero a por que estas aqui, en este lugar que no existe."
        },
        "relationship_variants": {},
        "delivery_style": "teasing",
        "typing_delay": 2.0,
        "media": None,
        "creates_memory": None,
        "sequence_order": 1,
        "requires_response": True,
        "is_active": True
    },

    # =========================================================================
    # ESCENA 2.8: REACCIONES DE DIANA (VARIANTES)
    # =========================================================================
    {
        "dialogue_id": "L2_D8_default",
        "scene_id": "L2_S8_reaccion_diana",
        "character": "diana",
        "base_text": "Hmm.\n\nEso es... suficiente. Por ahora.",
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
        "dialogue_id": "L2_D8_intrigada",
        "scene_id": "L2_S8a_diana_intrigada",
        "character": "diana",
        "base_text": "Interesante.\n\nMuy pocos responden con tanta... profundidad. Me haces querer saber mas de ti.",
        "archetype_variants": {},
        "relationship_variants": {},
        "delivery_style": "whisper",
        "typing_delay": 2.0,
        "media": None,
        "creates_memory": {
            "character": "diana",
            "memory_type": "impression",
            "template": "Su respuesta profunda desperto mi curiosidad genuina"
        },
        "sequence_order": 1,
        "requires_response": False,
        "is_active": True
    },
    {
        "dialogue_id": "L2_D8_respeta",
        "scene_id": "L2_S8b_diana_respeta",
        "character": "diana",
        "base_text": "Directo. Sin filtro.\n\nEso es refrescante en un lugar donde todos usan mascaras. Incluyéndome.",
        "archetype_variants": {},
        "relationship_variants": {},
        "delivery_style": "normal",
        "typing_delay": 1.5,
        "media": None,
        "creates_memory": {
            "character": "diana",
            "memory_type": "impression",
            "template": "Respeto su honestidad brutal - es rara aqui"
        },
        "sequence_order": 1,
        "requires_response": False,
        "is_active": True
    },
    {
        "dialogue_id": "L2_D8_sonrie",
        "scene_id": "L2_S8c_diana_sonrie",
        "character": "diana",
        "base_text": "Romantico.\n\nNo lo digo como critica. Hay belleza en ver el mundo así. Solo... ten cuidado con lo que deseas.",
        "archetype_variants": {},
        "relationship_variants": {},
        "delivery_style": "teasing",
        "typing_delay": 2.0,
        "media": None,
        "creates_memory": {
            "character": "diana",
            "memory_type": "impression",
            "template": "Me hizo sonreir con su romanticismo - debo tener cuidado"
        },
        "sequence_order": 1,
        "requires_response": False,
        "is_active": True
    },

    # =========================================================================
    # ESCENA 2.9: CIERRE
    # =========================================================================
    {
        "dialogue_id": "L2_D9_cierre_1",
        "scene_id": "L2_S9_cierre_nivel",
        "character": "diana",
        "base_text": "Por ahora, eso es todo lo que puedo darte.\n\nPero si sigues viniendo... quien sabe que mas podria mostrarte.",
        "archetype_variants": {},
        "relationship_variants": {},
        "delivery_style": "teasing",
        "typing_delay": 2.0,
        "media": None,
        "creates_memory": None,
        "sequence_order": 1,
        "requires_response": False,
        "is_active": True
    },
    {
        "dialogue_id": "L2_D9_cierre_2",
        "scene_id": "L2_S9_cierre_nivel",
        "character": "lucien",
        "base_text": "Eso... fue mas de lo que usualmente ofrece.\n\nNo lo desperdicie.",
        "archetype_variants": {},
        "relationship_variants": {},
        "delivery_style": "normal",
        "typing_delay": 1.5,
        "media": None,
        "creates_memory": {
            "character": "lucien",
            "memory_type": "milestone",
            "template": "Diana mostro interes inusual en este usuario"
        },
        "sequence_order": 2,
        "requires_response": False,
        "is_active": True
    }
]

# =============================================================================
# OPTIONS LEVEL 2
# =============================================================================

LEVEL_2_OPTIONS = [
    # =========================================================================
    # OPCIONES ESCENA 2.4: REPORTE DE MISION
    # =========================================================================
    {
        "option_id": "L2_O4_detallado",
        "dialogue_id": "L2_D4_resultado_1",
        "text": "Note patrones: la forma en que las personas evitan el contacto visual, como sostienen sus bebidas, los silencios entre palabras...",
        "text_variants": {
            "analytical": "Observe 7 interacciones distintas. El 70% mostro senales de incomodidad. Hay un patron de evasion que se repite."
        },
        "associated_archetype": "analytical",
        "is_default": False,
        "visibility_conditions": None,
        "immediate_effects": {
            "archetype_analytical": 15,
            "lucien_respect": 5
        },
        "delayed_effects": {
            "trigger_at_level": 3,
            "effect": {"unlock": "lucien_shares_analysis"}
        },
        "next_dialogue_id": None,
        "next_scene_id": "L2_S5a_analitico",
        "creates_memory": {
            "character": "lucien",
            "memory_type": "skill",
            "content": "tiene ojo clinico para los detalles"
        },
        "display_order": 1,
        "is_active": True
    },
    {
        "option_id": "L2_O4_emocional",
        "dialogue_id": "L2_D4_resultado_1",
        "text": "Senti algo... una melancolia colectiva. Como si todos estuvieran buscando algo que perdieron.",
        "text_variants": {
            "romantic": "Habia una tristeza hermosa en el aire. Como si todos guardaran un secreto que anhelaban compartir.",
            "introspective": "Me pregunte que buscaban. Y despues me pregunte que busco yo."
        },
        "associated_archetype": "romantic",
        "is_default": False,
        "visibility_conditions": None,
        "immediate_effects": {
            "archetype_romantic": 15,
            "diana_trust": 5
        },
        "delayed_effects": {
            "trigger_at_level": 3,
            "effect": {"unlock": "diana_shares_feeling"}
        },
        "next_dialogue_id": None,
        "next_scene_id": "L2_S5b_romantico",
        "creates_memory": {
            "character": "diana",
            "memory_type": "resonance",
            "content": "siente lo que otros no ven"
        },
        "display_order": 2,
        "is_active": True
    },
    {
        "option_id": "L2_O4_esencial",
        "dialogue_id": "L2_D4_resultado_1",
        "text": "La gente habla mucho y dice poco. Todos actuan. Nadie es real.",
        "text_variants": {
            "direct": "Mucho ruido. Poca sustancia. Mascaras por todos lados."
        },
        "associated_archetype": "direct",
        "is_default": True,
        "visibility_conditions": None,
        "immediate_effects": {
            "archetype_direct": 15,
            "lucien_respect": 3,
            "diana_trust": 3
        },
        "delayed_effects": None,
        "next_dialogue_id": None,
        "next_scene_id": "L2_S5c_directo",
        "creates_memory": {
            "character": "lucien",
            "memory_type": "observation",
            "content": "corta a traves de la superficialidad sin piedad"
        },
        "display_order": 3,
        "is_active": True
    },

    # =========================================================================
    # OPCIONES ESCENA 2.7: RESPUESTA A DIANA
    # =========================================================================
    {
        "option_id": "L2_O7_profunda",
        "dialogue_id": "L2_D7_pregunta_1",
        "text": "Busco entender. A mi mismo, a los demas. Hay algo aqui que me hace sentir mas cerca de una verdad que no puedo nombrar.",
        "text_variants": {
            "introspective": "No lo se con certeza. Pero hay preguntas en mi que este lugar parece capaz de responder."
        },
        "associated_archetype": "introspective",
        "is_default": False,
        "visibility_conditions": None,
        "immediate_effects": {
            "archetype_introspective": 15,
            "diana_trust": 8,
            "intimacy_level": 5
        },
        "delayed_effects": {
            "trigger_at_level": 3,
            "effect": {"unlock": "diana_opens_up"}
        },
        "next_dialogue_id": None,
        "next_scene_id": "L2_S8a_diana_intrigada",
        "creates_memory": {
            "character": "diana",
            "memory_type": "connection",
            "content": "busca verdad, no solo placer - eso es raro"
        },
        "display_order": 1,
        "is_active": True
    },
    {
        "option_id": "L2_O7_directa",
        "dialogue_id": "L2_D7_pregunta_1",
        "text": "Quiero algo real. En un mundo de mentiras, este lugar parece... autentico. Incluso si es un espejismo.",
        "text_variants": {
            "direct": "Algo verdadero. Sin juegos, sin actuacion. Aunque sea solo por un momento."
        },
        "associated_archetype": "direct",
        "is_default": True,
        "visibility_conditions": None,
        "immediate_effects": {
            "archetype_direct": 15,
            "diana_trust": 6,
            "lucien_respect": 3
        },
        "delayed_effects": None,
        "next_dialogue_id": None,
        "next_scene_id": "L2_S8b_diana_respeta",
        "creates_memory": {
            "character": "diana",
            "memory_type": "respect",
            "content": "no me miente - eso vale mas de lo que sabe"
        },
        "display_order": 2,
        "is_active": True
    },
    {
        "option_id": "L2_O7_romantica",
        "dialogue_id": "L2_D7_pregunta_1",
        "text": "Busco conexion. Algo que me haga sentir vivo. Y cuando te vi... senti que podria encontrarlo aqui.",
        "text_variants": {
            "romantic": "Te busco a ti. O lo que representas. La posibilidad de algo que trascienda lo ordinario."
        },
        "associated_archetype": "romantic",
        "is_default": False,
        "visibility_conditions": None,
        "immediate_effects": {
            "archetype_romantic": 15,
            "diana_trust": 5,
            "intimacy_level": 8
        },
        "delayed_effects": {
            "trigger_at_level": 4,
            "effect": {"unlock": "diana_vulnerability_moment"}
        },
        "next_dialogue_id": None,
        "next_scene_id": "L2_S8c_diana_sonrie",
        "creates_memory": {
            "character": "diana",
            "memory_type": "attraction",
            "content": "me busca - pero sabe que soy mas que un deseo?"
        },
        "display_order": 3,
        "is_active": True
    }
]
