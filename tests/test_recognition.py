

class TestTensorRTEngine:
    def test_build_engine(self):
        """Test TensorRT engine building."""
        from main import TensorRTEngine
        engine = TensorRTEngine("test_model.onnx")
        assert engine.model_path == "test_model.onnx"
    
    def test_infer(self):
        """Test TensorRT inference."""
        from main import TensorRTEngine
        engine = TensorRTEngine("test_model.onnx")
        result = engine.infer(np.zeros((640, 640, 3), dtype=np.uint8))
        assert isinstance(result, list)
