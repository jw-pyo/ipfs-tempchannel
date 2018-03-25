#project import
from cipher import AES_cipher, RSA_cipher

#library import
import ipfsapi
from os import listdir
import os, base64
import socket, sys
IP = "localhost"
PORT = 50401

# order : client 0 -> server 0 -> client 1 -> ...

class Server(object):
    def __init__(self, data_path):
        self.aes_passphrase = None
        self.buyer_pub = None
        self.ipfs_hash1 = None
        self.ipfs_addr = None
        self.data_path = data_path
    def run(self):
        ipfs = None
        try:
            ipfs = ipfsapi.connect("127.0.0.1", 5001)
        except:
            raise ConnectionError("cannot connect to ipfs\n")
        recv_buffer = []
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()
        port = PORT
        server_socket.bind(("", port))
        server_socket.listen(5)
        print("Server waiting for client on port {}".format(port))
        while True:
            client_socket, client_addr = server_socket.accept()
            print("I got a connection from {}".format(client_addr))
            i = 0
            while True:
                #TODO: input data ipfs_hash2
                #TODO: can I send public key via TCP?
                data = ["channel name: ",
                        "channel: {}, send the public key".format(self.aes_passphrase),
                        "ipfs_hash: {}".format(self.ipfs_addr)]
                #waiting...
                client_socket.send(data[i].encode()) 
                recv_buffer = client_socket.recv(512).decode()
                print("client [{}]:".format(client_addr), recv_buffer)
                if i == 0:
                    # encrypt data with AES and get ipfs_address for encrypted data
                    self.aes_passphrase = recv_buffer
                    aes = AES_cipher(self.aes_passphrase)
                    aes.encrypt_file(self.data_path, out_filename=self.data_path+".enc")
                    question = input("ipfs add?(y/n)")
                    if question == 'y':
                        self.ipfs_hash1 = ipfs.add(self.data_path+".enc")["Hash"]
                    else:
                        client_socket.close()
                        break;
                elif i == 1:
                    self.buyer_pub = recv_buffer
                    buyer = RSA_cipher("Bob")
                    buyer.importKeyAsString(self.buyer_pub)
                    ipfs_enc1 = buyer.encrypt_with_public(self.ipfs_hash1)
                    with open("data/ipfs_enc1", "w") as f:
                        f.write(str(ipfs_enc1))
                    print("ipfs_enc1: " + str(ipfs_enc1))
                    ipfs_hash2 = ipfs.add("data/ipfs_enc1")
                    self.ipfs_addr = ipfs_hash2['Hash']
                else:
                    dummy = input("dummy")
                    client_socket.send("dummy".encode())

                i += 1
            break;
        server_socket.close()
        print("SOCKET closed... END") 

class Client(object):
    def __init__(self):
        self.aes = None
        self.buyer = RSA_cipher("Bob")
        self.buyer_pub_path = None
        data = []
        i = 0
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((IP, PORT))
        while True:
            data = client_socket.recv(512).decode()
            if(data == 'q' or data=='Q'):
                client_socket.close()
                break;
            else:
                print("Server) ",data)
                if i == 0:
                    # set the passcode
                    send_buffer = input("")
                    self.aes = AES_cipher(send_buffer)
                    client_socket.send(self.aes.passcode.encode())
                elif i == 1:
                    # send the public key
                    send_buffer = input("path to public key: ")
                    with open(send_buffer, "r") as f:
                        send_buffer = f.read()
                    self.buyer_pub_path = send_buffer
                    client_socket.send(send_buffer.encode())
                elif i == 2:
                    # get the data
                    download_path = input("path to download: ")
                    self.buyer_pri_path = input("path to priv key: ")
                    data = data.split(": ")[1]
                    ipfs = None
                    try:
                        ipfs = ipfsapi.connect("127.0.0.1", 5001)
                        ipfs.get(data)
                        os.rename(data, "data/ipfs_enc1")
                    except:
                        raise ConnectionError("ipfs connection error")
                    ipfs_enc1 = None
                    with open("data/ipfs_enc1", "r") as f:
                        ipfs_enc1 = eval(f.read())
                    os.remove("data/ipfs_enc1")
                    self.buyer.importKey(self.buyer_pri_path)
                    ipfs_hash1 = self.buyer.decrypt_with_private(ipfs_enc1)
                    ipfs_hash1 = ipfs_hash1.decode("utf-8")
                    ipfs.get(ipfs_hash1)
                    os.rename(ipfs_hash1, download_path)

                    # decrypt aes
                    self.aes.decrypt_file(download_path,download_path+".dec")
                    print("Download completed.\n")

                else:
                    send_buffer = "dummy"
                    client_socket.send(send_buffer.encode())
            i += 1

        print("socket closed... END.")

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
    aes.encrypt_file(data, out_filename=data+".enc") #create test.txt.enc
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
    try:
        if(sys.argv[1] == "--server"):
            s = Server(data_path="/Users/pyo/ipfs-tempchannel/data/3.video.mp4")
            s.run()
        elif(sys.argv[1] == "--client"):
            c = Client()
        elif(sys.argv[1] == "--generatekey"):
            keygen = RSA_cipher(sys.argv[2])
            keygen.init()
    except ConnectionError:
        raise ConnectionError("Err")
    #seller_ = seller()
    #buyer(seller_)

    

