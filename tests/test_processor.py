

class TestAsyncProcessor:
    def test_async_processing(self):
        """Test async document processing."""
        import asyncio
        from main import DocumentProcessor, AsyncProcessor
        
        processor = DocumentProcessor()
        async_proc = AsyncProcessor(processor)
        
        # Test that async processor is created
        assert async_proc.processor is processor
        assert async_proc.max_concurrent == 5
