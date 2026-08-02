

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


class TestStreamingResponse:
    def test_stream_answer(self):
        """Test streaming answer generation."""
        from main import QASystem, StreamingResponse
        
        qa = QASystem()
        streaming = StreamingResponse(qa)
        assert streaming.qa is qa
    
    def test_stream_with_sources(self):
        """Test streaming with sources."""
        from main import QASystem, StreamingResponse
        
        qa = QASystem()
        streaming = StreamingResponse(qa)
        assert streaming.qa is qa


class TestRAGEnhancer:
    def test_enhance_query(self):
        """Test query enhancement."""
        from main import QASystem, RAGEnhancer
        
        qa = QASystem()
        enhancer = RAGEnhancer(qa)
        
        enhanced = enhancer.enhance_query("What is AI?", "Context: AI is...")
        assert "Context" in enhanced
        assert "What is AI?" in enhanced
    
    def test_generate_with_sources(self):
        """Test generation with sources."""
        from main import QASystem, RAGEnhancer
        
        qa = QASystem()
        enhancer = RAGEnhancer(qa)
        
        # Add some documents
        qa.add_documents(["AI is artificial intelligence.", "Machine learning is a subset of AI."])
        
        output = enhancer.generate_with_sources("What is AI?")
        assert 'answer' in output
        assert 'sources' in output
    
    def test_evaluate_rag(self):
        """Test RAG evaluation."""
        from main import QASystem, RAGEnhancer
        
        qa = QASystem()
        enhancer = RAGEnhancer(qa)
        
        test_questions = [
            {"question": "What is AI?"},
            {"question": "What is ML?"}
        ]
        
        results = enhancer.evaluate_rag(test_questions)
        assert results['total_questions'] == 2
