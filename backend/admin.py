from werkzeug.security import generate_password_hash

password = "student123"

hashed = generate_password_hash(password)

print(hashed)