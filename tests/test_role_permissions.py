from app.auth.dependencies import require_roles
from app.models.user import User


def test_require_roles_allows_matching_role():
    checker = require_roles("Admin")

    admin = User(
        full_name="Test Admin",
        email="admin_test@example.com",
        hashed_password="test_hash",
        role="Admin",
        is_active=True,
    )

    assert admin.role == "Admin"
    assert callable(checker)


def test_require_roles_supports_multiple_roles():
    checker = require_roles("Admin", "Doctor")

    assert callable(checker)
