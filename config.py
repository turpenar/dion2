import pathlib as pathlib
import pandas as pd

DATA_DIR = pathlib.Path(__file__).parent / "Resources"
DATA_FORMAT = "json"

ROOM_FILE = str(DATA_DIR / f"tiles.{DATA_FORMAT}")
ITEM_FILE = str(DATA_DIR / f"items.{DATA_FORMAT}")
ENEMY_FILE = str(DATA_DIR / f"enemies.{DATA_FORMAT}")
NPC_FILE = str(DATA_DIR / f"npcs.{DATA_FORMAT}")
QUEST_FILE = str(DATA_DIR / f"quests.{DATA_FORMAT}")
OBJECT_FILE = str(DATA_DIR / f"objects.{DATA_FORMAT}")
PLAYER_FILE = str(DATA_DIR / f"players.{DATA_FORMAT}")

TEXT_WRAPPER_WIDTH = 100

PROFESSION_STATS_GROWTH_FILE = pd.read_csv(DATA_DIR / "Profession_Stats_Growth.csv" )
PROFESSION_STATS_GROWTH_FILE.set_index('Profession', inplace=True)

PROFESSION_SKILLPOINT_BONUS_FILE = pd.read_csv(DATA_DIR / "Profession_SkillPoint_Bonus.csv")
PROFESSION_SKILLPOINT_BONUS_FILE.set_index('Profession', inplace=True)

RACE_STATS_FILE = pd.read_csv(DATA_DIR / "Race_Stats.csv")
RACE_STATS_FILE.set_index('Race', inplace=True)

verbs_path = DATA_DIR / 'verbs.txt'
with verbs_path.open(mode='r') as file:
    verbs = file.readlines()
verbs = [x.strip() for x in verbs]

prepositions_path = DATA_DIR / 'prepositions.txt'
with prepositions_path.open(mode='r') as file:
    prepositions = file.readlines()
prepositions = [x.strip() for x in prepositions]

# importing all articles
articles_path = DATA_DIR / 'articles.txt'
with articles_path.open(mode='r') as file:
    articles = file.readlines()
articles = [x.strip() for x in articles]

# importing all determiners
determiners_path = DATA_DIR / 'determiners.txt'
with determiners_path.open(mode='r') as file:
    determiners = file.readlines()
determiners = [x.strip() for x in determiners]

# importing all nouns
nouns_path = DATA_DIR / 'nouns.txt'
with nouns_path.open(mode='r') as file:
    nouns = file.readlines()
nouns = [x.strip() for x in nouns]

available_stat_points = 528
base_training_points = 25
profession_choices = ['None', 'Clairvoyant', 'Enchanter', 'Illusionist', 'Paladin', 'Ranger', 'Rogue', 'Inyanga', 'Warrior']
gender_choices = ['None', 'Female', 'Male']

