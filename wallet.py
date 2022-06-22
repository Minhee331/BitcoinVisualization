class Wallet(object):
    def __init__(self, passPhrase, privKey, pubKey, address, blockchain):
        self.__passPhrase = passPhrase
        self.__privKey = privKey
        self.__pubKey = pubKey
        self.__address = address
        self.__coin = 0
        self.__utxo = []
        self.__spendedTx = []
        self.__blockchain = blockchain

    def getAddress(self):
        return self.__address

    def getCoin(self):
        return self.__coin

    def __addUtxo(self, sender, amount):
        self.__utxo.append({
            'sender': sender,
            'receiver': self.__address,
            'amount': amount
        })

    def addCoin(self, sender, amount):
        self.__coin += int(amount)
        self.__addUtxo(sender, int(amount))
        return self.__coin

    def __subUtxo(self, receiver, amount):
        left_amount = amount
        for i in range(len(self.__utxo)):
            #utxo잔액이 남으면 자신에게 보내는 utxo를 저장하고 이전 utxo들은 제거
            if self.__utxo[i]['amount'] > left_amount:
                self.__addUtxo(self.__address, self.__utxo[i]['amount'] - left_amount)
                self.__spendedTx.append(self.__utxo[:i+1])
                # transaction 수정
                self.__blockchain.new_transaction(0, [], self.__address, self.__address, self.__utxo[i]['amount'] - left_amount)
                self.__utxo = self.__utxo[i+1:]
                break
            elif self.__utxo[i]['amount'] == left_amount:
                self.__spendedTx.append(self.__utxo[:i+1])
                self.__utxo = [] if i == len(self.__utxo)-1 else self.__utxo[i+1:]
                break
            else:
                left_amount -= self.__utxo[i]['amount']

    def subCoin(self, receiver, amount):
        if self.__coin >= int(amount):
            self.__coin -= int(amount)
            self.__subUtxo(receiver, int(amount))
            return self.__coin
        return -1

    def getUtxo(self):
        return self.__utxo

    def getSpendedTx(self):
        return self.__spendedTx

    # transaction 추가
    def getPrivKey(self):
        return self.__privKey

#남은 코인은 자기 자신에게 보내고 spended와 unspended Tx관리
# w = Wallet('fsfe', '3325ea8878ba034cdbf41e91bdb296a7941716e9645f1afe4868f34ce411664f', '04730458333ba3e11d803ada6e86ff3890f098013df899deb205a7339bb9d40054af2b544aa163b2123bddef3366d43fe094a589f4ddac25e8e712d1c38b0594b4', '1MeH4MHxi2cSLtA3fGXkm1YdgkSdZQDDvv')
# w.addCoin('1FzBtLxgwekstAtdEsyHxLA9ooaVAEMx1j', 10)
# w.addCoin('1FzBtLxgwekstAtdEsyHxLA9ooaVAEMx1j', 20)
# w.subCoin('1FzBtLxgwekstAtdEsyHxLA9ooaVAEMx1j', 25)
# tx = w.getUtxo()
# print(tx)
# tx2 = w.getSpendedTx()
# print(tx2)