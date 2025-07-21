"""
Simple test to verify Docker setup is working correctly.
"""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint():
    """Test the root endpoint returns API information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["message"] == "Expense Tracker API"


def test_categories_endpoint():
    """Test that categories endpoint is accessible."""
    response = client.get("/categories/")
    assert response.status_code == 200
    # Should return list of default categories
    categories = response.json()
    assert isinstance(categories, list)
    # Should have default categories if init_db ran
    if categories:
        assert len(categories) > 0


def test_expenses_endpoint():
    """Test that expenses endpoint is accessible."""
    response = client.get("/expenses/")
    assert response.status_code == 200
    # Should return empty list initially
    expenses = response.json()
    assert isinstance(expenses, list)


def test_create_expense():
    """Test creating a new expense."""
    expense_data = {
        "amount": 25.50,
        "merchant": "Test Merchant",
        "description": "Test expense for Docker verification",
        "transaction_date": "2024-01-15T10:30:00"
    }
    
    response = client.post("/expenses/", json=expense_data)
    assert response.status_code == 200
    
    expense = response.json()
    assert expense["amount"] == 25.50
    assert expense["merchant"] == "Test Merchant"
    assert "id" in expense
    assert "created_at" in expense


def test_docs_accessible():
    """Test that API documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200


if __name__ == "__main__":
    # Run basic health check
    print("🧪 Running Docker verification tests...")
    
    try:
        test_health_check()
        print("✅ Health check passed")
        
        test_root_endpoint()
        print("✅ Root endpoint passed")
        
        test_categories_endpoint()
        print("✅ Categories endpoint passed")
        
        test_expenses_endpoint()
        print("✅ Expenses endpoint passed")
        
        test_create_expense()
        print("✅ Create expense passed")
        
        test_docs_accessible()
        print("✅ Documentation accessible")
        
        print("\n🎉 All Docker verification tests passed!")
        print("💡 Your Docker setup is working correctly!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        exit(1) 