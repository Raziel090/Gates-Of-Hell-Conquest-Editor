"""Centralized constants for the campaign editor and inventory management system."""

# File and directory names
CAMPAIGN_DIR = "campaign"
CAMPAIGN_FILE = "campaign.scn"
STATUS_FILE = "status"
DATA_DIR_NAME = "data"

# File extensions
DEF_EXTENSION = ".def"
INC_EXTENSION = ".inc"
EXT_EXTENSION = ".ext"
BAK_EXTENSION = ".bak"
JSON_EXTENSION = ".json"
TXT_EXTENSION = ".txt"
PRESETS_EXTENSION = ".presets"
FSM_EXTENSION = ".fsm"
BACKUP_PATTERN = "*.bak"

# Archive and game data paths
SET_DIR = "set"
SET_STUFF_PATH = "set/stuff"
SET_BREED_PATH = "set/breed"
SET_BREED_MP_PATH = "set/breed/mp"
SET_DYNAMIC_CAMPAIGN_PATH = "set/dynamic_campaign"
SET_MULTIPLAYER_PATH = "set/multiplayer"
SET_MULTIPLAYER_UNITS_PATH = "set/multiplayer/units"
SET_MULTIPLAYER_CONQUEST_PATH = "set/multiplayer/units/conquest"
ENTITY_PATH = "entity"
ENTITY_VEHICLE_PATH = "entity/-vehicle"
PROPERTIES_PATH = "properties"

# Cache files
CAMPAIGN_MANAGER_CACHE = "campaign_manager_cache.json"

# Data files
ITEM_SIZES_FILE = "item_sizes.json"
ITEM_PATTERN_SIZES_FILE = "item_pattern_sizes.json"
RESUPPLY_FILENAME = "resupply.inc"

# File operations
READ_MODE = "r"
WRITE_MODE = "w"

# Campaign data patterns and markers
CAMPAIGN_SQUADS_MARKER = "{CampaignSquads"
DECEASED_MEMBER_ID = "0xffffffff"
INVENTORY_PREFIX = "{Inventory "
ENTITY_MARKER = "{Entity"
HUMAN_MARKER = "{Human"
ITEM_MARKER = "{item"
TAB_CLOSE = "\t}\n"

# Game data keywords
FILLING_KEYWORD = "filling"
FILLED_KEYWORD = "filled"
HUMAN_KEYWORD = "human"
WEAPONRY_KEYWORD = "Weaponry"
WEAPON_KEYWORD = "weapon"
MASS_KEYWORD = "mass"
CELL_KEYWORD = "cell"
CLEAR_KEYWORD = "clear"
BOX_KEYWORD = "box"

# Common separators and characters
DOT_SEPARATOR = "."
SPACE_SEPARATOR = " "
NEWLINE = "\n"
TAB = "\t"
QUOTE_CHAR = '"'
EMPTY_STRING = ""

# Default values
DEFAULT_AMOUNT = 1
DEFAULT_PROPERTY_NAME = "human"
EMPTY_CELL_VALUE = 0
OCCUPIED_CELL_VALUE = 1
INVALID_AMOUNT = -1

# Excluded patterns and files
EXCLUDED_PATTERNS = ["{noView}", "hand thrower"]
EXCLUDED_FILES_EXTENSIONS = [
    PRESETS_EXTENSION,
    FSM_EXTENSION,
    INC_EXTENSION,
    TXT_EXTENSION,
]

# Item properties
X_SIZE_KEY = "x"
Y_SIZE_KEY = "y"

# GUI Constants
THEME_NAME = "equilux"
WINDOW_TITLE = "Inventory Manager"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Style Constants
RED_LABEL_STYLE = "Red.TLabel"
GREEN_LABEL_STYLE = "Green.TLabel"
MP_LABEL_STYLE = "MP.TLabel"
AP_LABEL_STYLE = "AP.TLabel"
TFRAME_STYLE = "TFrame"

# Color Constants
RED_COLOR = "red"
GREEN_COLOR = "green"

# Style Properties
FOREGROUND_PROPERTY = "foreground"
BACKGROUND_PROPERTY = "background"

# Widget States
READONLY_STATE = "readonly"

# Pack Options
PACK_FILL_BOTH = "both"
PACK_EXPAND_TRUE = True

# Numeric Constants
CENTER_DIVISOR = 2
COMBOBOX_WIDTH = 30

# UI Text Constants
INVENTORY_MANAGER_TITLE = "Inventory Manager"
CONTROLS_FRAME_TITLE = "Controls"
SELECTION_FRAME_TITLE = "Selection"
CONSOLE_OUTPUT_TITLE = "Console Output"
ACTIONS_FRAME_TITLE = "Actions"

# Button Text
RESUPPLY_UNIT_BUTTON = "Resupply Unit"
RESUPPLY_SQUAD_BUTTON = "Resupply Squad"
RESUPPLY_ALL_BUTTON = "Resupply All"
ADD_MISSING_MEMBERS_BUTTON = "Add Missing Squad Members"

# Label Text
SELECT_SQUAD_LABEL = "Select Squad:"
SELECT_SQUAD_MEMBER_LABEL = "Select Squad Member:"
UNIT_TYPE_LABEL = "Unit Type:"
UNIT_NAME_LABEL = "Unit Name:"
UNIT_INVENTORY_DETAILS_LABEL = "Unit Inventory Details:"
UNKNOWN_LABEL = "Unknown"
CACHE_LABEL_TEXT = "Select saved campaign:"
CURRENT_UNIT_LABEL_TEXT = "Current Unit:"
UNIT_NAME_LABEL_TEXT = "Unit Name:"
UNIT_INVENTORY_LABEL_TEXT = "Unit Inventory:"
UNKNOWN_UNIT_TEXT = "Unknown"

# Resource Display
MP_ICON_TEXT = "MP"
AP_ICON_TEXT = "AP"

# Cache Keys
GAME_INSTALL_DIR_KEY = "game_install_dir"
CAMPAIGN_FILE_PATH_KEY = "campaign_file_path"
DATA_DIR_PATH_KEY = "data_dir_path"

# Regex Patterns
SQUAD_INFO_PATTERN = r"\{(.*?)\}"
SUPPLIES_PATTERN = r'\{\s*Extender\s+"supply_zone"[\s\n]+\{enabled\}[\s\n]+\{current\s+(\d+)\}[\s\n]+\}'
RESOURCES_PATTERN = r'\{\s*Extender\s+"resources"[\s\n]+\{current\s+(\d+)\}[\s\n]+\}'
FUEL_PATTERN = r"\{\s*FuelBag\s*\{\s*Remain\s+([\d.]+)\s*\}\s*\}"
CAMPAIGN_SQUADS_PATTERN = r"(\t\{CampaignSquads\n)"
SAVE_SQUADS_PATTERN = r"(\t\{CampaignSquads\n)(.*?)(\n\t\})"
USER_PLAYER_PATTERN = r'(\t\{Tags "_user" "player")'
MP_STATUS_PATTERN = r"\{mp\s+\d+\.?\d*\}"
AP_STATUS_PATTERN = r"\{ap\s+\d+\.?\d*\}"

# Item and inventory patterns
QUOTE_ITEM_PATTERN = r'\{item(?:\s+"[^"]+")+'
QUOTED_STRING_PATTERN = r'"([^"]+)"'
AMOUNT_PATTERN = r'"[^"]+"\s+(?:"[^"]+"\s+)*?(\d+)\s*\{cell'
CELL_PATTERN = r"\{cell\s+\d{1,2}\s+\d{1,2}\}"
CELL_VALUES_PATTERN = r"\d{1,2}"
FILL_AMOUNT_PATTERN = r"(\d+)(\s*{cell)"

# Replacement templates
MP_VALUE_REPLACEMENT = "{{mp {}}}"
AP_VALUE_REPLACEMENT = "{{ap {}}}"
SECTION_REPLACEMENT = "\t{}\n\\1"

# Error message templates
INVENTORY_MATRIX_ERROR = "Inventory matrix is not created yet!"
ITEM_FIT_ERROR_TEMPLATE = "Item '{}' with size {} doesn't fit in inventory of {}."
ADD_ITEM_ERROR_TEMPLATE = "Could not add item: {}"

# String format templates
ENTITY_INVENTORY_STR_TEMPLATE = "EntityInventory(\n  squad={}\n  entity={}\n  entries=\n{}\n  supplies={}\n  fuel={}\n)"
ITEM_ENTRY_PREFIX = "\t\t\t{item "
ITEM_NAME_QUOTE_TEMPLATE = '"{}" '
AMOUNT_FORMAT = "{} "
CELL_FORMAT = "{{cell {} {}}}\n"
AMOUNT_REPLACEMENT_TEMPLATE = " {} {{"

# Inventory file format
INVENTORY_HEADER_TEMPLATE = "{{Inventory {}\n"
BOX_OPEN = "\t\t{box\n"
BOX_CLEAR = "\t\t\t{clear}\n"
BOX_CLOSE = "\t\t}\n"
INVENTORY_CLOSE = "\t}"

# Logging messages
EXTRACTED_MESSAGE = "Extracted '{}' into: {}"
ALREADY_EXISTS_MESSAGE = "'{}' already exists at: {}"
OVERWRITING_MESSAGE = "Campaign files already exist at: {}, overwriting..."
BACKUP_EXISTS_MESSAGE = "Campaign backup already exists at: {}, overwriting..."
STATUS_BACKUP_EXISTS_MESSAGE = (
    "Campaign Status backup already exists at: {}, overwriting..."
)
BACKUP_CREATED_MESSAGE = "Campaign backup created at: {}"
STATUS_BACKUP_CREATED_MESSAGE = "Campaign Status backup created at: {}"
CAMPAIGNS_SAVED_MESSAGE = "Campaigns saved to: {}"
STATUS_SAVED_MESSAGE = "Campaign status info saved to: {}"
SQUADS_SAVED_MESSAGE = "Squads entries saved to campaign file: {}"
UNITS_SAVED_MESSAGE = "New unit entries saved to campaign file: {}"
ARCHIVE_CREATED_MESSAGE = "Archive created at: {} ({} files)"
ADDED_TO_ARCHIVE_MESSAGE = "Added to archive: {}"
ERROR_SAVING_MESSAGE = "Error saving campaign file: {}"
ERROR_CREATING_ARCHIVE_MESSAGE = "Error creating archive: {}"

# Special strings and keywords
ANIMATION_KEYWORD = "animation"
CURLY_BRACES = "{}"
NEWLINE_JOIN = "\n"
EMPTY_JOIN = ""
TAB_TAB_FORMAT = "\t\t{}"
TAB_FORMAT = "\t{}"

# Archive formats
CAMPAIGN_SQUADS_FORMAT = "\t{{CampaignSquads\n{}\n\t}}"
