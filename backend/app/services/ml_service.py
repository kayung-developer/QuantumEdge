"""
AuraQuant - Machine Learning Model Management Service
"""
import mlflow
from typing import List, Optional

from app.core.config import settings
from app.schemas.ai import ModelInfo


class MLModelService:
    """
    A service to interact with the MLflow Model Registry.
    """

    def __init__(self):
        if settings.MLFLOW_TRACKING_URI:
            mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
            self.client = mlflow.tracking.MlflowClient()
            print(f"MLflow service connected to: {settings.MLFLOW_TRACKING_URI}")
        else:
            self.client = None
            print("MLflow tracking URI not configured. ML Model Service will be disabled.")

    def list_registered_models(self) -> List[ModelInfo]:
        """
        Lists all models registered in the MLflow Model Registry.
        """
        if not self.client:
            return []

        models = self.client.list_registered_models()
        model_infos = []
        for m in models:
            latest_version = m.latest_versions[0] if m.latest_versions else None
            if latest_version:
                model_infos.append(ModelInfo(
                    name=latest_version.name,
                    version=latest_version.version,
                    stage=latest_version.current_stage,
                    description=latest_version.description,
                    creation_timestamp=latest_version.creation_timestamp,
                    last_updated_timestamp=latest_version.last_updated_timestamp,
                    run_id=latest_version.run_id,
                ))
        return model_infos

    def get_production_model(self, model_name: str) -> Optional[Any]:
        """
        Fetches and loads the 'Production' stage model from MLflow.

        This is a placeholder for the actual model loading logic.
        """
        if not self.client:
            return None

        try:
            # Example of loading a scikit-learn model from MLflow
            # model_uri = f"models:/{model_name}/Production"
            # loaded_model = mlflow.sklearn.load_model(model_uri)
            # return loaded_model
            print(f"Simulating fetch of production model '{model_name}'.")
            return {"name": model_name, "version": "3", "status": "Simulated Production Model"}

        except Exception as e:
            print(f"Failed to load production model '{model_name}': {e}")
            return None


# Create a single instance
ml_service = MLModelService()