from microchannel import AESCipher
import ipfsapi

if __name__ == '__main__':
    ipfs = ipfsapi.connect('127.0.0.1', 5001)    
    key = ['12345678901234567890123456789012', 
           '09876543210987654321098765432109'] #key1, key2
    message_path = "test.txt"

    a = AESCipher(key[0])
    a.encrypt_file(message_path) 
    
    res = ipfs.add(message_path+".enc")
    ipfs_hash1 = res['Hash']
    
    b = AESCipher(key[1])
    ipfs_enc1 = b.encrypt(ipfs_hash1)
    os.system("touch " + ipfs_enc1 + " " + ipfs_enc1)
    res = ipfs.add(ipfs_enc1)
    ipfs_hash2 = res['Hash']
    print(ipfs_hash2)

