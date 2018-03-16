import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES

from PIL import Image
import numpy as np
import os, random, struct

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS).encode()
unpad = lambda s: s[:-ord(s[len(s)-1:])]

class AESCipher(object):
    """
    https://github.com/dlitz/pycrypto
    """

    def __init__(self, key):
        self.key = key
        self.iv = bytes(16*'\x00'.encode())
        #self.key = hashlib.sha256(key.encode()).digest()
    def encrypt_file(self, in_filename, out_filename=None, chunksize=64*1024):
        """ 
        out_filename:
        If None, '<in_filename>.enc' will be used.
        chunksize:
        Sets the size of the chunk which the function
        uses to read and encrypt the file. Larger chunk
        sizes can be faster for some files and machines.
        chunksize must be divisible by 16.
        """
        key = self.key
        if out_filename is None:
            out_filename = in_filename + '.enc'

        #iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
        iv = self.iv
        encryptor = AES.new(key, AES.MODE_CBC, iv)
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
        key = self.key
        if out_filename is None:
            out_filename = os.path.splitext(in_filename)[0] + ".dec"

        with open(in_filename, 'rb') as infile:
            origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
            iv = infile.read(16)
            decryptor = AES.new(key, AES.MODE_CBC, iv)

            with open(out_filename, 'wb') as outfile:
                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    outfile.write(decryptor.decrypt(chunk))

                outfile.truncate(origsize) 
    def encrypt(self, variable):
        variable = variable.encode()
        raw = pad(variable)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        enc.cipher.encrypt(raw)
        return base64.b64encode(enc).decode('utf-8')

if __name__ == '__main__':
    #ipfs = ipfsapi.connect('127.0.0.1', 5001)
    
    key = ['12345678901234567890123456789012', 
           '09876543210987654321098765432109'] #key1, key2
    message_path = "test.txt"
    a = AESCipher(key[0])
    a.encrypt_file(message_path) 
    #a.decrypt_file(message_path+".enc") 
    
    res = ipfs.add(message_path+".enc")
    ipfs_hash1 = res['Hash']
    b = AESCipher(key[1])
    ipfs_enc1 = b.encrypt(ipfs_hash1)
    os.system("touch " + ipfs_enc1 + " " + ipfs_enc1)
    res = ipfs.add(ipfs_enc1)
    ipfs_hash2 = res['Hash']


    """
    img = "1.cat.jpeg"
    enc = AESCipher(key).encrypt_image(img)
    dec = AESCipher(key).decrypt_image(enc)
    
    with open("dec_test.jpg", "w") as f:
        f.write(dec)
    """
