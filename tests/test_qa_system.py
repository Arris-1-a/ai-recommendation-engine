

class TestContextManager:
    def test_add_turn(self):
        """Test adding conversation turns."""
        from main import ContextManager
        cm = ContextManager(max_turns=3)
        
        cm.add_turn("conv1", "Hello", "Hi there!")
        cm.add_turn("conv1", "How are you?", "I'm good!")
        
        context = cm.get_context("conv1")
        assert "Hello" in context
        assert "How are you?" in context
    
    def test_context_limit(self):
        """Test context limit."""
        from main import ContextManager
        cm = ContextManager(max_turns=2)
        
        for i in range(5):
            cm.add_turn("conv1", f"Q{i}", f"A{i}")
        
        context = cm.get_context("conv1")
        # Should only have last 2 turns
        assert "Q0" not in context
        assert "Q3" in context or "Q4" in context
    
    def test_clear(self):
        """Test clearing context."""
        from main import ContextManager
        cm = ContextManager()
        
        cm.add_turn("conv1", "Q1", "A1")
        assert cm.clear("conv1")
        assert cm.get_context("conv1") == ""
