import pytest
from unittest.mock import patch

import uvicorn

def test_uvicorn_run_invocation():
    with patch("uvicorn.run") as mock_run:
        import main
        
        mock_run.assert_called_once_with("app.api:app", host="0.0.0.0", port="8081")