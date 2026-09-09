from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

# Read existing bcrypt hashes; write Argon2 hashes for new accounts and upgrades.
pwd_context = PasswordHash((Argon2Hasher(), BcryptHasher()))
hash = pwd_context.hash
verify = pwd_context.verify
DUMMY_HASH = hash("dummy-password-for-timing-only")
