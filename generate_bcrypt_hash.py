from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
password = 'adminpassword'  # Remplace par ton mot de passe souhaité
hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
print(f"Mot de passe haché : {hashed_password}")
