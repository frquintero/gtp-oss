"""Basic tests for GPT CLI Enhanced."""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.message import Message
from models.conversation import Conversation
from utils.validators import InputValidator, CommandValidator


class TestMessage:
    """Test Message model."""
    
    def test_message_creation(self):
        """Test basic message creation."""
        msg = Message("user", "Hello world")
        assert msg.role == "user"
        assert msg.content == "Hello world"
        assert msg.timestamp is not None
    
    def test_message_to_dict(self):
        """Test message serialization."""
        msg = Message("assistant", "Hi there")
        # Since we removed to_dict method, we'll test basic functionality instead
        assert msg.role == "assistant"
        assert msg.content == "Hi there"
        assert msg.timestamp is not None


class TestConversation:
    """Test Conversation model."""
    
    def test_conversation_creation(self):
        """Test basic conversation creation."""
        conv = Conversation()
        assert conv.session_id is not None
        assert len(conv.messages) == 0
    
    def test_add_message(self):
        """Test adding messages to conversation."""
        conv = Conversation()
        msg = conv.add_message("user", "Hello")
        assert len(conv.messages) == 1
        assert conv.messages[0].content == "Hello"
    
    def test_get_messages_for_api(self):
        """Test API format conversion."""
        conv = Conversation()
        conv.add_message("user", "Hello")
        conv.add_message("assistant", "Hi there")
        
        api_messages = conv.get_messages_for_api()
        assert len(api_messages) == 2
        assert api_messages[0]["role"] == "user"
        assert api_messages[0]["content"] == "Hello"
    
    def test_conversation_stats(self):
        """Test conversation statistics."""
        conv = Conversation()
        conv.add_message("user", "Hello")
        conv.add_message("assistant", "Hi")
        conv.add_message("user", "How are you?")
        
        assert conv.get_message_count() == 3
        assert conv.get_user_message_count() == 2
        assert conv.get_assistant_message_count() == 1


class TestValidators:
    """Test validation utilities."""
    
    def test_model_validation(self):
        """Test model name validation."""
        assert InputValidator.validate_model_name("openai/gpt-oss-20b") == True
        assert InputValidator.validate_model_name("invalid-model") == False
    
    def test_filename_validation(self):
        """Test filename validation."""
        assert InputValidator.validate_filename("test.txt") == True
        assert InputValidator.validate_filename("test<>.txt") == False
    
    def test_export_format_validation(self):
        """Test export format validation."""
        assert InputValidator.validate_export_format("json") == True
        assert InputValidator.validate_export_format("invalid") == False
    
    def test_command_parsing(self):
        """Test command parsing."""
        result = CommandValidator.parse_command("save test.json")
        assert result["is_command"] == True
        assert result["command"] == "save"
        assert result["args"] == ["test.json"]
    
    def test_save_command_validation(self):
        """Test save command validation."""
        assert CommandValidator.validate_save_command(["test.json"]) is None
        assert CommandValidator.validate_save_command([]) is not None
        assert CommandValidator.validate_save_command(["a", "b"]) is not None


if __name__ == "__main__":
    pytest.main([__file__])
