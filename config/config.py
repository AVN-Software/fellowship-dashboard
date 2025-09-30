import os
import json
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        # Get the directory where this config.py file is located
        config_dir = os.path.dirname(os.path.abspath(__file__))
        config_file_path = os.path.join(config_dir, 'config.json')
        
        # Load analysis config from JSON
        with open(config_file_path, 'r') as f:
            self.analysis_config = json.load(f)
    
    # Supabase settings from .env
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
    
    @property
    def risk_threshold(self):
        return self.analysis_config['analysis']['risk_threshold']
    
    @property
    def tier_threshold_strict(self):
        return self.analysis_config['analysis']['tier_threshold_strict']
    
    @property
    def tier_threshold_lower(self):
        return self.analysis_config['analysis']['tier_threshold_lower']
    
    tier_colors = {
    'Tier 1': '#FF6B6B',
    'Tier 2': '#4ECDC4',
    'Tier 3': '#45B7D1'
}

domain_colors = {
    'AII': '#FF9999',
    'IA': '#66B2FF',
    'KPC': '#99FF99',
    'LE': '#FFCC99',
    'SE': '#FF99CC'
}
