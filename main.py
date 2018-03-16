#project import
from cipher import AES_cipher, RSA_cipher

#library import
import ipfsapi

if __name__ == '__main__':
    ipfs = None
    try:
        ipfs = ipfsapi.connect("127.0.0.1", 5001)
    except:
        raise ConnectionError("cannot connect to ipfs\n")

    user1 = RSA_cipher()
    user2 = RSA_cipher()
    passcode = '12345678901234567890123456789012'

    data = "data/test.txt"

    aes = AES_cipher(passcode)
    aes.encrypt_file(data)
    res = ipfs.add(data+".enc")
    ipfs_hash1 = res['Hash']
    ipfs_hash2 = user2.encrypt(ipfs_hash1)

    #TODO: send the ipfs_hash to user2's node
    # change the way:
    # create the RSA pair in advance
    # when we create a user instance, restore it from already saved private key

    os.system("touch " + ipfs_enc1 + " " + ipfs_enc1)
    res = ipfs.add(ipfs_enc1)
    ipfs_hash2 = res['Hash']
    print(ipfs_hash2)

