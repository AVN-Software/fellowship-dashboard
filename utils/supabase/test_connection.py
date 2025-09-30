from src.database.supabase_connection import SupabaseConnection
from config.config import Config


def test_supabase_connection():
    """Test the Supabase connection"""
    try:
        # Load configuration
        config = Config()
        
        # Create connection
        db = SupabaseConnection(config)
        
        # Test basic connection
        if db.test_connection():
            print("✓ Basic connection test passed")
        
        # Test data retrieval
        df = db.get_all_observations()
        if not df.empty:
            print(f"✓ Successfully retrieved {len(df)} observations")
            print(f"✓ Columns: {list(df.columns)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Connection test failed: {e}")
        return False


if __name__ == "__main__":
    test_supabase_connection()
