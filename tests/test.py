'''
Test script
*WARNING* Don't run this on a production bitcoin server! *WARNING*
Only on the test network.
'''
import argparse
import os
import sys
sys.path.append('../src')

import bitcoinrpc
# from bitcoinrpc.exceptions import BitcoinException, InsufficientFunds

from decimal import Decimal

parser = argparse.ArgumentParser()
parser.add_argument('--config', help="Specify configuration file")
parser.add_argument('--nolocal', help="Don't use connect_to_local",
                    action='store_true')
parser.add_argument('--noremote', help="Don't use connect_to_remote",
                    action='store_true')
parser.add_argument('--envbox',
                    help="Use testnet box configured through env vars",
                    action='store_true')
args = parser.parse_args()

if __name__ == "__main__":
    connections = []
    if args.envbox:
        host = os.environ['HOST']
        passwd = os.environ['PASS']
        user1 = os.environ['USER1']
        user2 = os.environ['USER2']
        port1 = int(os.environ['PORT1'])
        port2 = int(os.environ['PORT2'])
        conn1 = bitcoinrpc.connect_to_remote(user=user1, password=passwd,
                                        host=host, port=port1, use_https=False)
        connections.append(conn1)
        # TODO connect to second box to send coins back and forth
    else:
        if args.config:
            from bitcoinrpc.config import read_config_file
            cfg = read_config_file(args.config)
        else:
            from bitcoinrpc.config import read_default_config
            cfg = read_default_config(None)
        port = int(cfg.get('rpcport', '18332' if cfg.get('testnet') else '8332'))
        rpcuser = cfg.get('rpcuser', '')

        if not args.nolocal:
            local_conn = bitcoinrpc.connect_to_local()  # will use read_default_config
            connections.append(local_conn)
        if not args.noremote:
            remote_conn = bitcoinrpc.connect_to_remote(
                    user=rpcuser, password=cfg['rpcpassword'], host='localhost',
                    port=port, use_https=False)
            connections.append(remote_conn)

    for conn in connections:
        assert(conn.getinfo().testnet) # don't test on prodnet

        assert(type(conn.getblockcount()) is int)
        assert(type(conn.getconnectioncount()) is int)
        assert(type(conn.getdifficulty()) is Decimal)
        assert(type(conn.getgenerate()) is bool)
        conn.setgenerate(True)
        conn.setgenerate(True, 2)
        conn.setgenerate(False)
        assert(type(conn.gethashespersec()) is int)
        account = "testaccount"
        account2 = "testaccount2"
        bitcoinaddress = conn.getnewaddress(account)
        conn.setaccount(bitcoinaddress, account)
        address = conn.getaccountaddress(account)
        address2 = conn.getaccountaddress(account2)
        assert(conn.getaccount(address) == account)
        addresses = conn.getaddressesbyaccount(account)
        assert(address in addresses)
        #conn.sendtoaddress(bitcoinaddress, amount, comment=None, comment_to=None)
        conn.getreceivedbyaddress(bitcoinaddress)
        conn.getreceivedbyaccount(account)
        conn.listreceivedbyaddress()
        conn.listreceivedbyaccount()
        #conn.backupwallet(destination)
        x = conn.validateaddress(address)
        assert(x.isvalid == True)
        x = conn.validateaddress("invalid")
        assert(x.isvalid == False)

        for accid in conn.listaccounts(as_dict=True).iterkeys():
          tx = conn.listtransactions(accid)
          if len(tx) > 0:
            txid = tx[0].txid
            txdata = conn.gettransaction(txid)
            assert(txdata.txid == tx[0].txid)

        assert(type(conn.listunspent()) is list)  # needs better testing

    info = conn.getinfo()
    print "Blocks: %i" % info.blocks
    print "Connections: %i" % info.connections
    print "Difficulty: %f" % info.difficulty

    m_info = conn.getmininginfo()
    print ("Pooled Transactions: {pooledtx}\n"
           "Testnet: {testnet}\n"
           "Hash Rate: {hashes} H/s".format(pooledtx=m_info.pooledtx,
                                            testnet=m_info.testnet,
                                            hashes=m_info.hashespersec))
