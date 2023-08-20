import pytest
from unittest import mock
from main import main
import uvicorn
@pytest.mark.parametrize("host, port", [("0.0.0.0", 8081)])

def test_main(mocker, host, port):
    mocker.patch("uvicorn.run")
    
    main()
    
    uvicorn.run.assert_called_once_with("app.api:app", host=host, port=port, reload=True)
    