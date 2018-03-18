#project import
from cipher import AES_cipher, RSA_cipher

#library import
import ipfsapi
from os import listdir
import os, base64

def seller():
    """
    this func is executed by seller
    """
    ipfs = None
    try:
        ipfs = ipfsapi.connect("127.0.0.1", 5001)
    except:
        raise ConnectionError("cannot connect to ipfs\n")

    user1 = RSA_cipher("Alice")
    user1.importKey()
    user2 = RSA_cipher("Bob")
    user2.importKey()
    passcode = '12345678901234567890123456789012'

    data = "data/test.txt"

    aes = AES_cipher(passcode)
    aes.encrypt_file(data) #create test.txt.enc
    res = ipfs.add(data+".enc")
    ipfs_hash1 = res['Hash'] # ipfs_hash1 is the real address of encrypted data
    print("ipfs_hash1: " + ipfs_hash1)
    ipfs_enc1 = user2.encrypt_with_public(ipfs_hash1)
    with open("data/ipfs_enc1", "w") as f:
        f.write(str(ipfs_enc1))
    print("ipfs_enc1: " + str(ipfs_enc1))
    ipfs_hash2 = ipfs.add("data/ipfs_enc1")
    ipfs_hash2 = ipfs_hash2['Hash']
    print("ipfs_hash2: " + ipfs_hash2+ "\n")
    user2.printParams()
    return ipfs_hash2

def buyer(ipfs_hash2):
    """
    this func is executed by buyer
    """
    ipfs = None
    try:
        ipfs = ipfsapi.connect("127.0.0.1", 5001)
    except:
        raise ConnectionError("cannot connect to ipfs\n")

    user1 = RSA_cipher("Alice")
    user1.importKey()
    user2 = RSA_cipher("Bob")
    user2.importKey()
    passcode = '12345678901234567890123456789012'
    data = "data/test.txt"
    aes = AES_cipher(passcode)
    
    ipfs_enc1 = ipfs.get(ipfs_hash2)
    with open(ipfs_hash2, "r") as f:
        ipfs_enc1 = eval(f.read())
    print("ipfs_enc1: " + str(ipfs_enc1))
    ipfs_hash1 = user2.decrypt_with_private(ipfs_enc1)
    print("ipfs_hash1: "+ ipfs_hash1.decode("utf-8"))
    enc_jpg = ipfs.get(ipfs_hash1)
    os.system("rm {}".format(ipfs_hash2))
    
    hashfiles = [f for f in listdir(os.getcwd()) if f.startswith("Qm")][0]
    aes.decrypt_file(hashfiles, "data/output/result.txt") 
    

def test2(command):
    """
    check if the diff between before aes encryption and after exists
    """
    passcode = '12345678901234567890123456789012'
    data = "data/test.txt"
    aes = AES_cipher(passcode)
    if command == "encrypt":
        aes.encrypt_file(data) #create test.txt.enc
    else:
        aes.decrypt_file(data+".enc")


if __name__ == '__main__':
    seller_ = seller()
    buyer(seller_)
    #test2("decrypt")

    
    #TODO: send the ipfs_hash to user2's node
    # change the way:
    # create the RSA pair in advance
    # when we create a user instance, restore it from already saved private key

    #os.system("touch " + ipfs_enc1 + " " + ipfs_enc1)
    #res = ipfs.add(ipfs_enc1)
    #ipfs_hash2 = res['Hash']
    #print(ipfs_hash2)

