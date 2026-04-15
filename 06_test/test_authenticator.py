#
import pytest
from authenticator import Authenticator

class TestAuthenticator:
    @pytest.fixture
    def auth(self):
        return Authenticator()

    @pytest.mark.parametrize("u,p", [
        ("user1", "pass123"),
        ("user2", "securepass"),
        ("admin", "admin@2024"),
        ("test_user", "testpass99"),
        ("john_doe", "john#2024"),
    ])
    def test_register_new(self, auth, u, p):
        auth.register(u, p)
        assert u in auth.users
        assert auth.users[u] == p

    def test_register_dup(self, auth):
        auth.register("dupuser", "1234")
        with pytest.raises(ValueError, match="ユーザーは既に存在します"):
            auth.register("dupuser", "qwer456")

    def test_login_success(self, auth):
        auth.register("passok", "p123")
        result = auth.login("passok", "p123")
        assert result == "ログイン成功"

    def test_login_passwrong(self, auth):
        auth.register("existuser", "p123")
        with pytest.raises(ValueError, match="ユーザー名またはパスワードが正しくありません"):
            auth.login("existuser", "mismatch")

    def test_login_nouser(self, auth):
        with pytest.raises(ValueError, match="ユーザー名またはパスワードが正しくありません"):
            auth.login("nonexistent", "p123")

