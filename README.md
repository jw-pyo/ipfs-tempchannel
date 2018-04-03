## IPFS-tempchannel

IPFS-tempchannel is a client system of IPFS used for data exchanges.
When data seller uploads the data on IPFS, IPFS-tempchannel makes data encrypted form, only buyer can download the data

## prerequisites

Before opening the port, you should check whether the port is blocked by firewall or not.
The way to open the port:

    iptables -I INPUT 1 -p tcp --dport [PORT_NUM] -j ACCEPT
    iptables -I OUTPUT 1 -p tcp --dport [PORT_NUM] -j ACCEPT

Manually connect to the peer:

    ipfs swarm connect /ip4/[public_ip]/tcp/[port, default:4001]/ipfs/[peerid]

## running the script

In server(data provider) side:

    . env/bin/activate
    python main.py --server

In client(data buyer) side:

    . env/bin/activate
    python main.py --client

## License

