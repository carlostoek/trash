# mybot/handlers/admin_storyboard.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import json
import sqlite3
from typing import List, Dict, Any, Optional

router = Router()

class StoryboardStates(StatesGroup):
    adding_scene = State()
    editing_scene = State()
    adding_dialogue = State()
    editing_dialogue = State()
    adding_character = State()
    editing_character = State()

class StoryboardManager:
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Inicializa las tablas del storyboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de escenas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS storyboard_scenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                channel TEXT NOT NULL,
                order_num INTEGER DEFAULT 0,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de diálogos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS storyboard_dialogues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scene_id INTEGER,
                character_name TEXT NOT NULL,
                message TEXT NOT NULL,
                triggers TEXT, -- JSON array
                conditions TEXT, -- JSON object
                actions TEXT, -- JSON object
                order_num INTEGER DEFAULT 0,
                active BOOLEAN DEFAULT 1,
                FOREIGN KEY (scene_id) REFERENCES storyboard_scenes (id)
            )
        ''')
        
        # Tabla de personajes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS storyboard_characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                role TEXT,
                color TEXT DEFAULT '#666666',
                description TEXT,
                active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Insertar personajes por defecto
        cursor.execute('''
            INSERT OR IGNORE INTO storyboard_characters (name, role, color, description)
            VALUES 
            ('Diana', 'Creadora', '#ff6b9d', 'La creadora del universo, directa y apasionada'),
            ('Lucien', 'Guía', '#4ecdc4', 'El guía misterioso, seductor y sabio')
        ''')
        
        conn.commit()
        conn.close()
    
    # CRUD Escenas
    def get_scenes(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.*, COUNT(d.id) as dialogue_count
            FROM storyboard_scenes s
            LEFT JOIN storyboard_dialogues d ON s.id = d.scene_id
            GROUP BY s.id
            ORDER BY s.order_num
        ''')
        
        scenes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return scenes
    
    def create_scene(self, name: str, channel: str) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Obtener el próximo número de orden
        cursor.execute('SELECT MAX(order_num) FROM storyboard_scenes')
        max_order = cursor.fetchone()[0] or 0
        
        cursor.execute('''
            INSERT INTO storyboard_scenes (name, channel, order_num)
            VALUES (?, ?, ?)
        ''', (name, channel, max_order + 1))
        
        scene_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return scene_id
    
    def update_scene(self, scene_id: int, name: str, channel: str, active: bool = True):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE storyboard_scenes 
            SET name = ?, channel = ?, active = ?
            WHERE id = ?
        ''', (name, channel, active, scene_id))
        
        conn.commit()
        conn.close()
    
    def delete_scene(self, scene_id: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Eliminar diálogos asociados
        cursor.execute('DELETE FROM storyboard_dialogues WHERE scene_id = ?', (scene_id,))
        # Eliminar escena
        cursor.execute('DELETE FROM storyboard_scenes WHERE id = ?', (scene_id,))
        
        conn.commit()
        conn.close()
    
    # CRUD Diálogos
    def get_dialogues(self, scene_id: int) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM storyboard_dialogues 
            WHERE scene_id = ? 
            ORDER BY order_num
        ''', (scene_id,))
        
        dialogues = []
        for row in cursor.fetchall():
            dialogue = dict(row)
            # Parsear JSON
            dialogue['triggers'] = json.loads(dialogue['triggers']) if dialogue['triggers'] else []
            dialogue['conditions'] = json.loads(dialogue['conditions']) if dialogue['conditions'] else {}
            dialogue['actions'] = json.loads(dialogue['actions']) if dialogue['actions'] else {}
            dialogues.append(dialogue)
        
        conn.close()
        return dialogues
    
    def create_dialogue(self, scene_id: int, character: str, message: str, 
                       triggers: List[str] = None, conditions: Dict = None, 
                       actions: Dict = None) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Obtener el próximo número de orden para esta escena
        cursor.execute('SELECT MAX(order_num) FROM storyboard_dialogues WHERE scene_id = ?', (scene_id,))
        max_order = cursor.fetchone()[0] or 0
        
        cursor.execute('''
            INSERT INTO storyboard_dialogues 
            (scene_id, character_name, message, triggers, conditions, actions, order_num)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            scene_id, character, message,
            json.dumps(triggers or []),
            json.dumps(conditions or {}),
            json.dumps(actions or {}),
            max_order + 1
        ))
        
        dialogue_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return dialogue_id
    
    def update_dialogue(self, dialogue_id: int, character: str, message: str,
                       triggers: List[str] = None, conditions: Dict = None,
                       actions: Dict = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE storyboard_dialogues 
            SET character_name = ?, message = ?, triggers = ?, conditions = ?, actions = ?
            WHERE id = ?
        ''', (
            character, message,
            json.dumps(triggers or []),
            json.dumps(conditions or {}),
            json.dumps(actions or {}),
            dialogue_id
        ))
        
        conn.commit()
        conn.close()
    
    def delete_dialogue(self, dialogue_id: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM storyboard_dialogues WHERE id = ?', (dialogue_id,))
        conn.commit()
        conn.close()
    
    # CRUD Personajes
    def get_characters(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM storyboard_characters WHERE active = 1')
        characters = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return characters
    
    def create_character(self, name: str, role: str, color: str = '#666666', description: str = '') -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO storyboard_characters (name, role, color, description)
            VALUES (?, ?, ?, ?)
        ''', (name, role, color, description))
        
        char_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return char_id
    
    # Funciones de búsqueda y ejecución
    def find_dialogue_by_trigger(self, trigger: str, user_id: int) -> Optional[Dict]:
        """Busca un diálogo por trigger y verifica condiciones"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT d.*, s.channel, s.name as scene_name
            FROM storyboard_dialogues d
            JOIN storyboard_scenes s ON d.scene_id = s.id
            WHERE d.active = 1 AND s.active = 1
        ''')
        
        for row in cursor.fetchall():
            dialogue = dict(row)
            triggers = json.loads(dialogue['triggers']) if dialogue['triggers'] else []
            
            if trigger in triggers:
                conditions = json.loads(dialogue['conditions']) if dialogue['conditions'] else {}
                if self._check_conditions(conditions, user_id):
                    dialogue['triggers'] = triggers
                    dialogue['conditions'] = conditions
                    dialogue['actions'] = json.loads(dialogue['actions']) if dialogue['actions'] else {}
                    conn.close()
                    return dialogue
        
        conn.close()
        return None
    
    def _check_conditions(self, conditions: Dict, user_id: int) -> bool:
        """Verifica condiciones del usuario"""
        if not conditions:
            return True
        
        # Aquí integrarías con tu sistema existente de usuarios
        # Por ejemplo:
        # user_data = get_user_data(user_id)
        # 
        # if "points" in conditions:
        #     condition = conditions["points"]
        #     if isinstance(condition, str) and condition.startswith(">="):
        #         required_points = int(condition[2:])
        #         if user_data.get("points", 0) < required_points:
        #             return False
        
        return True
    
    def execute_dialogue_actions(self, actions: Dict, user_id: int) -> Dict:
        """Ejecuta acciones de un diálogo"""
        results = {}
        
        if "points" in actions:
            # Integrar con tu sistema de puntos
            # update_user_points(user_id, actions["points"])
            results["points_added"] = actions["points"]
        
        if "lorepiece" in actions:
            # Integrar con tu sistema de lorepieces
            results["lorepiece_added"] = actions["lorepiece"]
        
        if "mission" in actions:
            # Integrar con tu sistema de misiones
            results["mission_assigned"] = actions["mission"]
        
        return results

# Instancia global del manager
storyboard_manager = StoryboardManager()

# Handlers del bot
@router.message(Command("storyboard"))
async def storyboard_main_menu(message: Message):
    """Menú principal del storyboard (solo admins)"""
    # Verificar si es admin
    if not await is_admin(message.from_user.id):
        await message.answer("❌ No tienes permisos para acceder al storyboard.")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Ver Escenas", callback_data="sb_scenes")],
        [InlineKeyboardButton(text="👥 Gestionar Personajes", callback_data="sb_characters")],
        [InlineKeyboardButton(text="🔄 Exportar Config", callback_data="sb_export")],
        [InlineKeyboardButton(text="📊 Estadísticas", callback_data="sb_stats")],
        [InlineKeyboardButton(text="❌ Cerrar", callback_data="sb_close")]
    ])
    
    await message.answer(
        "🎭 <b>Panel de Storyboard</b>\n\n"
        "Gestiona la narrativa completa de tu bot:\n"
        "• Escenas y diálogos\n"
        "• Personajes\n"
        "• Condiciones y acciones\n"
        "• Exportación de configuración",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(F.data == "sb_scenes")
async def show_scenes(callback: CallbackQuery):
    """Muestra lista de escenas"""
    scenes = storyboard_manager.get_scenes()
    
    if not scenes:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Crear Primera Escena", callback_data="sb_add_scene")],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="sb_main")]
        ])
        
        await callback.message.edit_text(
            "📚 <b>Escenas del Storyboard</b>\n\n"
            "No hay escenas configuradas aún.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return
    
    text = "📚 <b>Escenas del Storyboard</b>\n\n"
    keyboard_buttons = []
    
    for scene in scenes:
        status_emoji = "✅" if scene['active'] else "❌"
        text += f"{status_emoji} <b>{scene['name']}</b>\n"
        text += f"   📺 Canal: {scene['channel']}\n"
        text += f"   💬 Diálogos: {scene['dialogue_count']}\n\n"
        
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"📝 {scene['name'][:20]}{'...' if len(scene['name']) > 20 else ''}", 
                callback_data=f"sb_scene_{scene['id']}"
            )
        ])
    
    keyboard_buttons.extend([
        [InlineKeyboardButton(text="➕ Nueva Escena", callback_data="sb_add_scene")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="sb_main")]
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data.startswith("sb_scene_"))
async def show_scene_details(callback: CallbackQuery):
    """Muestra detalles de una escena específica"""
    scene_id = int(callback.data.split("_")[2])
    
    # Obtener datos de la escena
    scenes = storyboard_manager.get_scenes()
    scene = next((s for s in scenes if s['id'] == scene_id), None)
    
    if not scene:
        await callback.answer("❌ Escena no encontrada")
        return
    
    dialogues = storyboard_manager.get_dialogues(scene_id)
    
    text = f"📝 <b>Escena: {scene['name']}</b>\n\n"
    text += f"📺 <b>Canal:</b> {scene['channel']}\n"
    text += f"📊 <b>Estado:</b> {'Activa' if scene['active'] else 'Inactiva'}\n"
    text += f"💬 <b>Diálogos:</b> {len(dialogues)}\n\n"
    
    if dialogues:
        text += "<b>Diálogos:</b>\n"
        for i, dialogue in enumerate(dialogues[:3], 1):  # Mostrar solo los primeros 3
            text += f"{i}. <b>{dialogue['character_name']}:</b> "
            text += f"{dialogue['message'][:50]}{'...' if len(dialogue['message']) > 50 else ''}\n"
        
        if len(dialogues) > 3:
            text += f"... y {len(dialogues) - 3} más\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Ver Todos los Diálogos", callback_data=f"sb_dialogues_{scene_id}")],
        [InlineKeyboardButton(text="➕ Nuevo Diálogo", callback_data=f"sb_add_dialogue_{scene_id}")],
        [InlineKeyboardButton(text="✏️ Editar Escena", callback_data=f"sb_edit_scene_{scene_id}")],
        [InlineKeyboardButton(text="🗑️ Eliminar Escena", callback_data=f"sb_delete_scene_{scene_id}")],
        [InlineKeyboardButton(text="🔙 Volver a Escenas", callback_data="sb_scenes")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data == "sb_add_scene")
async def add_scene_start(callback: CallbackQuery, state: FSMContext):
    """Inicia el proceso de agregar una nueva escena"""
    await state.set_state(StoryboardStates.adding_scene)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancelar", callback_data="sb_scenes")]
    ])
    
    await callback.message.edit_text(
        "➕ <b>Nueva Escena</b>\n\n"
        "Envía el nombre de la nueva escena:\n"
        "Ejemplo: <i>Bienvenida - Los Kinkys</i>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.message(StoryboardStates.adding_scene)
async def add_scene_name(message: Message, state: FSMContext):
    """Procesa el nombre de la nueva escena"""
    scene_name = message.text.strip()
    
    if len(scene_name) < 3:
        await message.answer("❌ El nombre debe tener al menos 3 caracteres.")
        return
    
    await state.update_data(scene_name=scene_name)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📺 Los Kinkys", callback_data="sb_channel_kinkys")],
        [InlineKeyboardButton(text="💎 El Diván", callback_data="sb_channel_divan")],
        [InlineKeyboardButton(text="❌ Cancelar", callback_data="sb_scenes")]
    ])
    
    await message.answer(
        f"✅ Nombre: <b>{scene_name}</b>\n\n"
        "Ahora selecciona el canal:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("sb_channel_"))
async def add_scene_channel(callback: CallbackQuery, state: FSMContext):
    """Procesa la selección del canal"""
    channel = "Los Kinkys" if callback.data.endswith("kinkys") else "El Diván"
    
    data = await state.get_data()
    scene_name = data['scene_name']
    
    # Crear la escena
    scene_id = storyboard_manager.create_scene(scene_name, channel)
    
    await state.clear()
    
    await callback.message.edit_text(
        f"✅ <b>Escena creada exitosamente</b>\n\n"
        f"📝 <b>Nombre:</b> {scene_name}\n"
        f"📺 <b>Canal:</b> {channel}\n"
        f"🆔 <b>ID:</b> {scene_id}",
        parse_mode="HTML"
    )
    
    # Mostrar menú de la nueva escena después de 2 segundos
    await asyncio.sleep(2)
    await show_scene_details(callback)

# Función auxiliar para verificar admin
async def is_admin(user_id: int) -> bool:
    """Verifica si el usuario es administrador"""
    # Integrar con tu sistema de administradores existente
    # Por ejemplo, verificar en base de datos o lista de admins
    return True  # Placeholder - implementar según tu lógica

# Función para integrar con el sistema de narrativa existente
async def trigger_narrative(user_id: int, trigger: str, bot):
    """Función para disparar narrativa desde otros handlers"""
    dialogue = storyboard_manager.find_dialogue_by_trigger(trigger, user_id)
    
    if dialogue:
        # Enviar mensaje
        await bot.send_message(user_id, dialogue['message'], parse_mode="HTML")
        
        # Ejecutar acciones
        results = storyboard_manager.execute_dialogue_actions(dialogue['actions'], user_id)
        
        return results
    
    return None

# Ejemplo de uso en otros handlers
"""
# En mybot/handlers/welcome.py
from .admin_storyboard import trigger_narrative

@router.message(Command("start"))
async def welcome_handler(message: Message):
    user_id = message.from_user.id
    
    # Disparar narrativa de bienvenida
    result = await trigger_narrative(user_id, "welcome", message.bot)
    
    if not result:
        # Mensaje por defecto si no hay narrativa configurada
        await message.answer("¡Bienvenido!")
"""
