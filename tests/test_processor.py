

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


class TestParallelProcessor:
    def test_parallel_processing(self):
        """Test parallel document processing."""
        from main import DocumentProcessor, ParallelProcessor
        
        processor = DocumentProcessor()
        parallel = ParallelProcessor(processor, num_workers=2)
        
        assert parallel.processor is processor
        assert parallel.num_workers == 2
