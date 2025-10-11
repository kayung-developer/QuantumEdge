"""
AuraQuant - Computer Vision (CV) Service for Chart Analysis
"""
import numpy as np
import cv2
import torch
import torchvision.transforms as T
import mlflow
import mlflow.pytorch
import logging
from typing import List

from app.schemas.market_data import KlineData
from app.schemas.ai import ChartPatternDetection, ChartPatternType
from app.core.config import settings


class ChartCVService:
    def __init__(self):
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.class_map = {}
        self.transform = T.Compose([
            T.ToTensor(),
            T.Normalize((0.5,), (0.5,))
        ])
        self.img_size = (128, 128)

    def load_production_model(self):
        """
        Loads the model version marked as 'Production' from the MLflow Model Registry.
        This is called once at application startup.
        """
        if not settings.MLFLOW_TRACKING_URI:
            logger.warning("MLFLOW_TRACKING_URI not set. CV Service will be disabled.")
            return

        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
        model_name = "AuraQuant-Chart-Pattern-CNN-v1"
        model_uri = f"models:/{model_name}/Production"

        try:
            logger.info(f"Loading production model from MLflow URI: {model_uri}")
            self.model = mlflow.pytorch.load_model(model_uri, map_location=self.device)
            self.model.eval()

            # Here you would load the class_map saved with the model
            # For this example, we'll hardcode it based on our training script
            self.class_map = {0: "double_top", 1: "head_and_shoulders", 2: "no_pattern", 3: "rising_wedge"}

            logger.info(f"Successfully loaded model '{model_name}' to device '{self.device}'.")
        except Exception as e:
            logger.error(f"Failed to load production model from MLflow. CV Service will be inactive. Error: {e}")
            self.model = None


    def _klines_to_image(self, klines: List[KlineData], width: int = 224, height: int = 224) -> np.ndarray:
        """
        Converts a list of kline data into a normalized grayscale image.
        This is a crucial preprocessing step for a CV model.
        """
        if not klines:
            return np.zeros((height, width), dtype=np.uint8)

        prices = [k.close for k in klines]
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        if price_range == 0:
            price_range = 1  # Avoid division by zero

        # Normalize prices to fit within the image height
        normalized_prices = [int(((p - min_price) / price_range) * (height - 1)) for p in prices]

        # Create a blank image (black background)
        image = np.zeros((height, width), dtype=np.uint8)

        # Draw the price line on the image
        num_points = len(normalized_prices)
        for i in range(num_points - 1):
            x1 = int((i / num_points) * width)
            y1 = height - 1 - normalized_prices[i]
            x2 = int(((i + 1) / num_points) * width)
            y2 = height - 1 - normalized_prices[i + 1]
            cv2.line(image, (x1, y1), (x2, y2), (255, 255, 255), 1)  # White line

        return image

    def detect_patterns(self, klines: List[KlineData]) -> List[ChartPatternDetection]:
        """
        Detects chart patterns from kline data using a CV model.

        THIS IS A SIMULATED IMPLEMENTATION. A real implementation would:
        1. Convert klines to an image.
        2. Preprocess the image (resize, normalize, convert to tensor).
        3. Pass the tensor through the loaded PyTorch model.
        4. Interpret the model's output (softmax probabilities) to determine the pattern.
        5. Return the detected pattern with its confidence score.
        """

        def detect_patterns(self, klines: List[KlineData]) -> List[ChartPatternDetection]:
            """
            Detects chart patterns using the loaded production CV model.
            """
            if not self.model or not klines or len(klines) < 50:
                return []

            # 1. Preprocess data into the format the model expects
            image = self._klines_to_image(klines)
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)  # Add batch dimension

            # 2. Perform inference
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)[0]
                confidence, predicted_idx = torch.max(probabilities, 0)

            predicted_class_name = self.class_map.get(predicted_idx.item(), "unknown")
            confidence_score = confidence.item()

            # 3. Post-process the prediction
            # Don't report low-confidence predictions or "no_pattern"
            if confidence_score < 0.75 or predicted_class_name == "no_pattern":
                return []

            # Map the class name to our ChartPatternType Enum
            pattern_type_map = {
                "head_and_shoulders": ChartPatternType.HEAD_AND_SHOULDERS,
                "double_top": ChartPatternType.DOUBLE_TOP,
                "rising_wedge": ChartPatternType.RISING_WEDGE,
            }
            pattern_type = pattern_type_map.get(predicted_class_name, ChartPatternType.UNKNOWN)

            # In a real system, you'd have a mapping of patterns to recommended actions
            action = "Potential bearish reversal detected."  # Example action

            detection = ChartPatternDetection(
                pattern_type=pattern_type,
                confidence_score=confidence_score,
                start_timestamp=klines[0].time,
                end_timestamp=klines[-1].time,
                recommended_action=action
            )
            return [detection]


# Create a single instance of the service
cv_service = ChartCVService()