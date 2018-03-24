from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto import Random
import ast, os, random, struct

class AES_cipher():
    def __init__(self, passcode):
        self.passcode = passcode
        self.iv = bytes(16*'\x00'.encode())
        #self.key = hashlib.sha256(key.encode()).digest()
    def encrypt_file(self, in_filename, out_filename=None, chunksize=64*1024):
        passcode = self.passcode
        if out_filename is None:
            out_filename = in_filename + '.enc'

        #iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
        iv = self.iv
        encryptor = AES.new(passcode, AES.MODE_CBC, iv)
        filesize = os.path.getsize(in_filename)

        with open(in_filename, 'rb') as infile:
            with open(out_filename, 'wb') as outfile:
                outfile.write(struct.pack('<Q', filesize))
                outfile.write(iv)

                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        chunk += bytes((16 - len(chunk) % 16)*' '.encode())

                    outfile.write(encryptor.encrypt(chunk))

    def decrypt_file(self,in_filename, out_filename=None, chunksize=24*1024):
        """
        Decrypts a file using AES (CBC mode) with the
            given key. Parameters are similar to encrypt_file,
            with one difference: out_filename, if not supplied
            will be in_filename without its last extension
            (i.e. if in_filename is 'aaa.zip.enc' then
            out_filename will be 'aaa.zip')
        """
        passcode = self.passcode
        if out_filename is None:
            out_filename = os.path.splitext(in_filename)[0] + ".dec"

        with open(in_filename, 'rb') as infile:
            origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
            iv = infile.read(16)
            decryptor = AES.new(passcode, AES.MODE_CBC, iv)

            with open(out_filename, 'wb') as outfile:
                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    outfile.write(decryptor.decrypt(chunk))

                outfile.truncate(origsize)

class RSA_cipher(): # public key algorithm
    def __init__(self, username=None):
        self.username = username
        self.key = None
    def init(self):
        if self.username is None:
            self.username = "Alice"
        self.random_generator = Random.new().read
        self.key = RSA.generate(1024, self.random_generator)
        self.pubkey = self.key.publickey()
        with open("key/{}.priv".format(self.username), "wb") as privkey:
            privkey.write(self.key.exportKey(format='PEM'))
        with open("key/{}.pub".format(self.username), "wb") as pubkey:
            pubkey.write(self.pubkey.exportKey(format='PEM'))
            
        #self.prikey = self.key.privatekey()
    def importKey(self, keypath=None): # pubkey_path or priv_path
        if keypath.endswith(".pub"):
            pubkey_text = open(keypath, "rb")
            self.pubkey = RSA.importKey(pubkey_text.read())
            pubkey_text.close()
        if keypath.endswith(".priv"):
            prikey_text = open(keypath, "rb")
            self.key = RSA.importKey(prikey_text.read())
            self.pubkey = self.key.publickey()
            prikey_text.close()
    def importKeyAsString(self, pub_text=None):
        self.pubkey = RSA.importKey(pub_text)
    def encrypt_with_public(self, msg):
        encrypted = self.pubkey.encrypt(msg.encode('utf-8'), 32)
        self.encrypted = encrypted[0]
        return encrypted[0]
    def encrypt_with_private(self, msg):
        raise NotImplementedError
    def decrypt_with_public(self, msg):
        raise NotImplementedError
    def decrypt_with_private(self, msg=None):
        if msg is None:
            msg = str(self.encrypted)
        #print(ast.literal_eval(str(msg)))
        decrypted = self.key.decrypt(ast.literal_eval(str(msg)))
        #decrypted = self.key.decrypt(bytes(msg))
        return decrypted
    def restore_key(self, priv_path):
        pass
    def printParams(self):
        attr = [attr for attr in vars(self).items() if not attr[0].startswith('__')]
        print(attr) 
        return attr





if __name__ == '__main__':
    rsa = RSA_cipher()
    rsa.init()
    print(type(rsa.pubkey))
