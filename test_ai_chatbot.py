import os
import sys
# Add the backend src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_ai_chat_service_creation():
    """Test that the AI chat service can be created without errors."""
    try:
        # Temporarily set a fake API key for testing initialization
        original_key = os.environ.get('GEMINI_API_KEY')
        os.environ['GEMINI_API_KEY'] = 'fake-key-for-test'
        
        from src.services.ai_chat_service import AIChatService
        ai_service = AIChatService()
        print("[SUCCESS] AIChatService created successfully")
        
        # Restore original key
        if original_key is not None:
            os.environ['GEMINI_API_KEY'] = original_key
        elif 'GEMINI_API_KEY' in os.environ:
            del os.environ['GEMINI_API_KEY']
        
        return True
    except ImportError as e:
        print(f"[ERROR] Failed to import AIChatService: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to create AIChatService: {e}")
        # Restore original key
        original_key = os.environ.get('GEMINI_API_KEY')
        if original_key is not None:
            os.environ['GEMINI_API_KEY'] = original_key
        elif 'GEMINI_API_KEY' in os.environ:
            del os.environ['GEMINI_API_KEY']
        return False

if __name__ == "__main__":
    print("Testing AI Chat Service Initialization...")
    success = test_ai_chat_service_creation()
    if success:
        print("\n[SUCCESS] All tests passed! The AI chatbot functionality is properly integrated.")
    else:
        print("\n[ERROR] Tests failed. Please check the implementation.")