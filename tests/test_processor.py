

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


class TestPipelineOptimizer:
    def test_optimize(self):
        """Test pipeline optimization."""
        from main import DocumentProcessor, PipelineOptimizer
        
        processor = DocumentProcessor()
        optimizer = PipelineOptimizer(processor)
        
        # Test that optimizer is created
        assert optimizer.processor is processor
    
    def test_get_recommendations(self):
        """Test getting recommendations."""
        from main import DocumentProcessor, PipelineOptimizer
        
        processor = DocumentProcessor()
        optimizer = PipelineOptimizer(processor)
        
        recommendations = optimizer.get_recommendations()
        assert isinstance(recommendations, list)
