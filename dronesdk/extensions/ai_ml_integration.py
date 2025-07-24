from typing import Any, Dict, Optional, Tuple
import numpy as np
import tensorflow as tf
import torch

class AIMLIntegration:
    """Supports machine learning models for advanced features."""
    
    def __init__(self):
        self.models = {}
        self.tensorflow_available = False
        self.pytorch_available = False
        
        try:
            self.tensorflow_available = True
            self.tf = tf
        except ImportError:
            pass
            
        try:
            self.pytorch_available = True
            self.torch = torch
        except ImportError:
            pass
    
    def load_tensorflow_model(self, model_path: str, model_name: str) -> bool:
        """Load a TensorFlow model."""
        if not self.tensorflow_available:
            print("TensorFlow not available")
            return False
            
        try:
            model = self.tf.keras.models.load_model(model_path)
            self.models[model_name] = {
                'model': model,
                'framework': 'tensorflow',
                'input_shape': model.input_shape
            }
            print(f"Loaded TensorFlow model: {model_name}")
            return True
        except Exception as e:
            print(f"Failed to load TensorFlow model {model_name}: {e}")
            return False
    
    def load_pytorch_model(self, model_path: str, model_name: str, model_class=None) -> bool:
        """Load a PyTorch model."""
        if not self.pytorch_available:
            print("PyTorch not available")
            return False
            
        try:
            if model_class:
                model = model_class()
                model.load_state_dict(self.torch.load(model_path))
            else:
                model = self.torch.load(model_path)
            
            model.eval()
            self.models[model_name] = {
                'model': model,
                'framework': 'pytorch'
            }
            print(f"Loaded PyTorch model: {model_name}")
            return True
        except Exception as e:
            print(f"Failed to load PyTorch model {model_name}: {e}")
            return False
    
    def predict(self, model_name: str, input_data: np.ndarray) -> Optional[np.ndarray]:
        """Run inference with a loaded model."""
        if model_name not in self.models:
            print(f"Model {model_name} not found")
            return None
            
        model_info = self.models[model_name]
        model = model_info['model']
        framework = model_info['framework']
        
        try:
            if framework == 'tensorflow':
                prediction = model.predict(input_data)
                return prediction
            elif framework == 'pytorch':
                with self.torch.no_grad():
                    if isinstance(input_data, np.ndarray):
                        input_tensor = self.torch.from_numpy(input_data).float()
                    else:
                        input_tensor = input_data
                    prediction = model(input_tensor)
                    return prediction.numpy()
        except Exception as e:
            print(f"Prediction error for model {model_name}: {e}")
            
        return None
    
    def detect_objects_ml(self, image: np.ndarray, model_name: str = "object_detection") -> list:
        """Detect objects in image using ML model."""
        if model_name not in self.models:
            print(f"Object detection model {model_name} not loaded")
            return []
            
        preprocessed_image = self._preprocess_image_for_detection(image)
        predictions = self.predict(model_name, preprocessed_image)
        
        if predictions is not None:
            return self._postprocess_detections(predictions)
        
        return []
    
    def classify_terrain(self, image: np.ndarray, model_name: str = "terrain_classifier") -> Dict[str, float]:
        """Classify terrain type from aerial image."""
        if model_name not in self.models:
            print(f"Terrain classification model {model_name} not loaded")
            return {}
            
        preprocessed_image = self._preprocess_image_for_classification(image)
        predictions = self.predict(model_name, preprocessed_image)
        
        if predictions is not None:
            terrain_classes = ["grass", "concrete", "water", "trees", "buildings", "roads"]
            results = {}
            for i, class_name in enumerate(terrain_classes):
                if i < len(predictions[0]):
                    results[class_name] = float(predictions[0][i])
            return results
            
        return {}
    
    def estimate_obstacle_distance(self, image: np.ndarray, model_name: str = "depth_estimation") -> Optional[np.ndarray]:
        """Estimate depth/distance to obstacles from monocular image."""
        if model_name not in self.models:
            print(f"Depth estimation model {model_name} not loaded")
            return None
            
        preprocessed_image = self._preprocess_image_for_depth(image)
        depth_map = self.predict(model_name, preprocessed_image)
        
        return depth_map
    
    def _preprocess_image_for_detection(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for object detection."""
        resized = cv2.resize(image, (416, 416))
        normalized = resized.astype(np.float32) / 255.0
        return np.expand_dims(normalized, axis=0)
    
    def _preprocess_image_for_classification(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for terrain classification."""
        resized = cv2.resize(image, (224, 224))
        normalized = (resized.astype(np.float32) - 127.5) / 127.5
        return np.expand_dims(normalized, axis=0)
    
    def _preprocess_image_for_depth(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for depth estimation."""
        resized = cv2.resize(image, (640, 480))
        normalized = resized.astype(np.float32) / 255.0
        return np.expand_dims(normalized, axis=0)
    
    def _postprocess_detections(self, predictions: np.ndarray) -> list:
        """Postprocess object detection predictions."""
        detections = []
        confidence_threshold = 0.5
        
        for i in range(predictions.shape[1]):
            confidence = predictions[0, i, 4]
            if confidence > confidence_threshold:
                x, y, w, h = predictions[0, i, :4]
                class_scores = predictions[0, i, 5:]
                class_id = np.argmax(class_scores)
                
                detections.append({
                    'bbox': (x, y, w, h),
                    'confidence': confidence,
                    'class_id': class_id,
                    'class_score': class_scores[class_id]
                })
        
        return detections