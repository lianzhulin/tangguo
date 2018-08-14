#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
"""
@author: zhulin.lian@gmail.com

@python examples for browser API
@see more in https://github.com/elastos/Elastos.ELA/blob/master/docs/jsonrpc_apis.md

"""

import requests
from pprint import pprint

'''
get blockchain status, response:
{'info': {'blocks': 168785, #the height of the lastest block
          'connections': 1,
          'difficulty': 0,
          'errors': '',
          'network': '主网',
          'protocolversion': 1,
          'proxy': '',
          'relayfee': 1e-05,
          'testnet': False,
          'timeoffset': 0,
          'version': 1}}
'''
#https://blockchain.elastos.org/api/v1/newblock/
pprint(requests.get(url='https://blockchain.elastos.org/api/v1/status/').json())

'''
get block hash by block height id
{'blockHash': 'aba057e264ec5a5ed3117997abd21d5a87ff90fa12ec9b585dd870d65955fe40'} #base58
'''
pprint(requests.get(url='https://blockchain.elastos.org/api/v1/block-index/{block_height}'.format(block_height=168780)).json())

'''
get block information by block_hash value
{'_id': 'a1325146eed27989480bd173c13ba50997dc97953f8a9182888c51880cade79b',
 'bits': 490024803,
 'confirmations': 5008,
 'difficulty': '0',
 'hash': 'a1325146eed27989480bd173c13ba50997dc97953f8a9182888c51880cade79b',
 'height': 163781,
 'isMainChain': True,
 'merkleroot': '0c777a67d0104adb8dc552d1bc1f9dfe564db24ee492ca5dd7b2b465235bc937',
 'nonce': 0,
 'poolInfo': {'poolName': 'ELA', 'url': ''},
 'previousblockhash': '6003e7f36d3bcac4774d94873ee699f7bab60ac1d702391533aa55efff5f8ee5',
 'size': 0,
 'time': 1533632837,
 'tx': ['191feeff29f39422998c9341971b1c2d2ca186572f01e0a5c186d3e6c027ac93', #Array of Transactions
        'f6081caed1ca4397c1e858899fc5ef85359d5a8c228a4bc3bf84050b49aac59c',
        '80723dd2c43d824b39828f8014a33dfa0c102471d49a76bea0bd14f2742f7ef2',
        '625744ce2ed38e6f3c8d28b56c5668101045e9355f2ffa5cee37993ab9e018bc',
        '6c3748460d4c833d59aef4e120b89cb383e2df5147ac792b72a6657cad7e62d3',
        'fe0fc580b16d285dcaa69dc82d8dc9df3e1836cc426d09401f25e09041a084c2',
        '328b84a5b6998caa0a1901992bd8513f603a39f164744067ba720a9e9ba974a2'],
 'txlength': 7,
 'version': 0}
'''
pprint(requests.get(url='https://blockchain.elastos.org/api/v1/block/{block_hash}'.format(block_hash='a1325146eed27989480bd173c13ba50997dc97953f8a9182888c51880cade79b')).json())

'''
get the information of a single transaction
{'_id': 'bdfdc436c3d66ba64db553766907ec7f970fdb46c05983bb6d0c51d323336e5d',
 'blockhash': '6003e7f36d3bcac4774d94873ee699f7bab60ac1d702391533aa55efff5f8ee5',
 'blockheight': 163780,
 'blocktime': 1533632765,
 'confirmations': 5012,
 'fees': 0.005,
 'isCoinBase': False,
 'locktime': 0,
 'size': 367,
 'time': 1533632765,
 'txid': 'bdfdc436c3d66ba64db553766907ec7f970fdb46c05983bb6d0c51d323336e5d', #current tx id, other name is transaction hash
 'valueOut': 67931.1080045,
 'version': 0,
 'vin': [{'addr': 'EUW5fxD3mQgYXUdiDHrBpPK1WUB4goWTpw',
          'n': 1,
          'txid': '7f4b3aa605014f4bc7dad7b6bb81482be69879b238beea7daf73e7ae426978e7', #pre tx id
          'value': 67931.11300453,
          'valueSat': 6793111300453}],
 'vout': [{'n': 0,
           'scriptPubKey': {'addresses': ['EPUHxpvfx46h4XNvYgukJM8sFZDcipd6yA'],
                            'type': 'pubkeyhash'},
           'value': 300.195,
           'valueSat': '30019500000'},
          {'n': 1,
           'scriptPubKey': {'addresses': ['EcTiVbpG4nZ3shdoZjGwoJM8mmr1Nvhk7P'],
                            'type': 'pubkeyhash'},
           'value': 11.14266,
           'valueSat': 1114266000},
          {'n': 2,
           'scriptPubKey': {'addresses': ['EdBxEDSt2Q3D19V66k4QrhV2beggH4vbme'],
                            'type': 'pubkeyhash'},
           'value': 67619.7703445,
           'valueSat': '6761977034453'}]}

'''
pprint(requests.get(url='https://blockchain.elastos.org/api/v1/tx/{transaction_hash}'.format(transaction_hash='733f785f8b7f46cfa0eee2e4bd4312efc93dee25e9ff84842ce04bbf67326cd5')).json())

'''
get the summary of single address

{'addrStr': '8KNrJAyF4M67HT5tma7ZE4Rx9N9YzaUbtM',
 'balance': 15733517.7659,
 'balanceSat': 1573351776590000,
 'totalReceived': 33917034.5318,
 'totalReceivedSat': 3391703453180000,
 'totalSent': 18183516.7659,
 'totalSentSat': 1818351676590000,
 'txApperances': 7,
 'unconfirmedBalance': 0,
 'unconfirmedBalanceSat': 0,
 'unconfirmedTxApperances': 0}

'''
pprint(requests.get(url='https://blockchain.elastos.org/api/v1/addr/{Elastos_address}'.format(Elastos_address='8KNrJAyF4M67HT5tma7ZE4Rx9N9YzaUbtM')).json())

'''
get the utxos of ad single address
'''
