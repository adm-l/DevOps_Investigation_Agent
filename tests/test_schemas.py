import pytest
from pydantic import ValidationError
from app.schemas import InvestigationRequest

def test_valid_request():
    assert InvestigationRequest(service="payment-service",incident="HTTP 500 errors").service=="payment-service"

def test_service_name_rejects_spaces():
    with pytest.raises(ValidationError):
        InvestigationRequest(service="payment service",incident="HTTP 500 errors")
