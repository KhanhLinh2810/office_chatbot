import bcrypt

class EncryptionUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash mật khẩu"""
        # Tạo salt và hash
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Kiểm tra mật khẩu"""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )