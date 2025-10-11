"""
MLOps: Chart Pattern Recognition Model Training
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision.datasets import ImageFolder
import torchvision.transforms as T
import mlflow
import mlflow.pytorch
from tqdm import tqdm
import os

# --- Configuration ---
DATASET_DIR = "chart_dataset"
MODEL_NAME = "AuraQuant-Chart-Pattern-CNN-v1"
NUM_EPOCHS = 5  # In a real system, this would be 50-100
BATCH_SIZE = 32
LEARNING_RATE = 0.001


# --- 1. Define the CNN Model Architecture ---
class ChartPatternCNN(nn.Module):
    def __init__(self, num_classes):
        super(ChartPatternCNN, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 16 * 16, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x


def train():
    """Main function to run the training pipeline."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # --- 2. Load and Prepare Data ---
    transform = T.Compose([
        T.Grayscale(),
        T.ToTensor(),
        T.Normalize((0.5,), (0.5,))
    ])

    full_dataset = ImageFolder(root=DATASET_DIR, transform=transform)
    num_classes = len(full_dataset.classes)
    class_map = full_dataset.class_to_idx
    print(f"Found classes: {class_map}")

    # Split dataset into training and validation
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)

    # --- 3. Initialize Model, Loss, and Optimizer ---
    model = ChartPatternCNN(num_classes=num_classes).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # --- 4. Start MLflow Experiment ---
    mlflow.set_tracking_uri("http://127.0.0.1:5000")  # Assumes local MLflow server
    mlflow.set_experiment("Chart Pattern Recognition")

    with mlflow.start_run() as run:
        print(f"MLflow Run ID: {run.info.run_id}")
        mlflow.log_params({
            "epochs": NUM_EPOCHS,
            "batch_size": BATCH_SIZE,
            "learning_rate": LEARNING_RATE,
            "model_architecture": "SimpleCNN",
            "dataset_size": len(full_dataset)
        })

        # --- 5. Training Loop ---
        for epoch in range(NUM_EPOCHS):
            model.train()
            running_loss = 0.0
            for inputs, labels in tqdm(train_loader, desc=f"Epoch {epoch + 1}/{NUM_EPOCHS}"):
                inputs, labels = inputs.to(device), labels.to(device)
                optimizer.zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                running_loss += loss.item()

            avg_train_loss = running_loss / len(train_loader)
            mlflow.log_metric("train_loss", avg_train_loss, step=epoch)

            # --- Validation Loop ---
            model.eval()
            correct = 0
            total = 0
            with torch.no_grad():
                for inputs, labels in val_loader:
                    inputs, labels = inputs.to(device), labels.to(device)
                    outputs = model(outputs)
                    _, predicted = torch.max(outputs.data, 1)
                    total += labels.size(0)
                    correct += (predicted == labels).sum().item()

            accuracy = 100 * correct / total
            print(f"Epoch {epoch + 1}: Train Loss: {avg_train_loss:.3f}, Validation Accuracy: {accuracy:.2f}%")
            mlflow.log_metric("val_accuracy", accuracy, step=epoch)

        # --- 6. Log the Trained Model to MLflow ---
        print("Training finished. Logging model to MLflow...")
        mlflow.pytorch.log_model(
            pytorch_model=model,
            artifact_path="model",
            registered_model_name=MODEL_NAME,  # This registers the model
            extra_files=[{"class_map": class_map}]  # Save the class mapping with the model
        )
        print(f"Model '{MODEL_NAME}' was registered in MLflow.")


if __name__ == "__main__":
    if not os.path.exists(DATASET_DIR):
        print("Dataset not found. Please run 'python create_dataset.py' first.")
    else:
        train()