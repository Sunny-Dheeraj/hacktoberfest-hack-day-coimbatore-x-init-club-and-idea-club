"""Unit tests for PythonAnalyzer AST extraction."""

import pytest
import json
from app.analyzers.python_analyzer import PythonAnalyzer


def test_pytorch_training_script_ast():
    analyzer = PythonAnalyzer()
    code = """import torch
from torch import nn
from torch.utils.data import DataLoader

class Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(10, 2)

    def forward(self, x):
        return self.fc(x)

def train(model, loader, optimizer):
    for x, y in loader:
        loss = model(x).sum()
        loss.backward()
        optimizer.step()
"""
    result = analyzer.analyze("train.py", code, repository="vision-model")

    assert result.error is None
    assert result.language == "python"

    signal_names = [s.name for s in result.signals]
    assert "torch" in signal_names
    assert "torch.nn" in signal_names
    assert "DataLoader" in signal_names
    assert "torch.nn.Module" in signal_names
    assert "loss.backward" in signal_names
    assert "optimizer.step" in signal_names
    assert "model_training_loop" in signal_names

    # Verify line numbers are captured
    class_sig = next(s for s in result.signals if s.name == "torch.nn.Module")
    assert class_sig.line_start == 5
    assert class_sig.line_end >= 5
    assert class_sig.technology == "PyTorch"


def test_fastapi_route_detection():
    analyzer = PythonAnalyzer()
    code = """from fastapi import FastAPI, APIRouter, Depends

app = FastAPI()
router = APIRouter()

@app.get("/items")
async def read_items():
    return [{"name": "item1"}]

@router.post("/items")
def create_item():
    return {"status": "created"}
"""
    result = analyzer.analyze("main.py", code, repository="api-backend")

    assert result.error is None
    signal_names = [s.name for s in result.signals]
    assert "FastAPI" in signal_names
    assert "fastapi_route_decorator" in signal_names

    fastapi_signals = [s for s in result.signals if s.technology == "FastAPI"]
    assert len(fastapi_signals) >= 3


def test_scikit_learn_and_pandas():
    analyzer = PythonAnalyzer()
    code = """import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

df = pd.read_csv("dataset.csv")
model = LogisticRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
"""
    result = analyzer.analyze("pipeline.py", code, repository="data-pipeline")

    assert result.error is None
    signal_names = [s.name for s in result.signals]
    assert "pandas" in signal_names
    assert "pd.read_csv" in signal_names
    assert "sklearn.model_selection.train_test_split" in signal_names
    assert "model.fit" in signal_names
    assert "model.predict" in signal_names


def test_malformed_python_does_not_crash():
    analyzer = PythonAnalyzer()
    malformed_code = """def broken_function(:
    return 42
    import invalid syntax +++
"""
    result = analyzer.analyze("bad.py", malformed_code, repository="broken-repo")

    # Should gracefully catch SyntaxError and report error message
    assert result.error is not None
    assert "SyntaxError" in result.error
    assert isinstance(result.signals, list)


def test_jupyter_notebook_analysis():
    analyzer = PythonAnalyzer()
    nb_content = json.dumps({
        "cells": [
            {
                "cell_type": "markdown",
                "source": ["# Analysis Notebook"]
            },
            {
                "cell_type": "code",
                "source": [
                    "import numpy as np\n",
                    "import pandas as pd\n",
                    "arr = np.array([1, 2, 3])\n"
                ]
            }
        ]
    })

    result = analyzer.analyze("notebook.ipynb", nb_content, repository="ml-lab")
    assert result.error is None
    signal_names = [s.name for s in result.signals]
    assert "numpy" in signal_names
    assert "pandas" in signal_names
