from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).parent.absolute()
EXCEL_DIR = BASE_DIR / 'excel_dir'
EXCEL_DIR.mkdir(exist_ok=True)

DB_URL = 'sqlite:///parsing_data.db'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,ka;q=0.6',
    'Accept:': 'application/json, text/plain, */*'
}