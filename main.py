from blockchain import Blockchain
from wallet import Wallet
import bitcoin.main as btc
import tkinter
from tkinter import messagebox
import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4
# transaction 추가
from Crypto.Hash import MD5, RIPEMD, SHA, SHA256

wallets = []
blockchain = Blockchain()
node_identifier = str(uuid4()).replace('-', '')

#트랜잭션 검증
def verifyTransaction(sender, receiver, amount):
    #주소가 올바른지
    senderWallet = None
    receiverWallet = None
    for i in range(len(wallets)):
        if sender == wallets[i].getAddress():
            senderWallet = wallets[i]
        if receiver == wallets[i].getAddress():
            receiverWallet = wallets[i]
    if sender != '0' and (senderWallet == None or receiverWallet == None):
        print("송수신자의 지갑주소가 올바르지 않습니다.")
        messagebox.showerror("지갑주소 오류", f"송수신자의 지갑주소가 올바르지 않습니다.\senderWallet: {senderWallet}\receiverWallet: {receiverWallet}")
        return False, senderWallet, receiverWallet
    #돈이 있는지
    if sender != '0' and senderWallet.getCoin() < int(amount):
        print("sender의 코인이 부족합니다.")
        messagebox.showerror("코인 부족", f"송신자의 코인이 부족합니다.\n가지고 있는 코인: {senderWallet.getCoin()}\r보내려는 코인: {amount}")
        return False, senderWallet, receiverWallet
    #서명이 올바른지
    return True, senderWallet, receiverWallet

def mine(miner):
    if blockchain.getChainLength() == 0:
        block = blockchain.new_block(previous_hash=1, proof=100)
        verify, senderWallet, receiverWallet = verifyTransaction('0', miner, 100)
        receiverWallet.addCoin('0', 100)
        return block

    last_block = blockchain.last_block
    last_proof = last_block['nonce']
    proof = blockchain.proof_of_work(last_proof)

    blockchain.new_transaction(
        input_count= 0,
        previous_output= [],
        sender="0",
        receiver=miner,
        amount=1,
    )

    verify, senderWallet, receiverWallet = verifyTransaction('0', miner, 100)
    receiverWallet.addCoin('0', 100)
    
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    print(json.dumps(blockchain.chain, indent=4))
    return block

def new_transaction(sender:str, receiver:str, amount:int):

    verify, senderWallet, receiverWallet = verifyTransaction(sender, receiver, amount)
    if not verify:
        print("트랜잭션 추가 중단")
        return False

    # transaction 추가
    input_count = len(senderWallet.getUtxo())
    previous_output = []
    for i in senderWallet.getUtxo():
        ori_msg = (i['sender'] + i['receiver'] + str(i['amount']))
        msg = ori_msg.encode()
        h1 = SHA256.new()
        h1.update(msg)                       # 1st SHA256
        h2 = SHA256.new()
        h2.update((h1.hexdigest()).encode()) # 2nd SHA256
        hv = h2.hexdigest()
        previous_output.append(hv)

    senderWallet.subCoin(receiver, amount)
    receiverWallet.addCoin(sender, amount)

    tx = blockchain.new_transaction(input_count, previous_output, sender, receiver, amount)
    messagebox.showinfo("알림", f"tx가 정상적으로 만들어졌습니다.\nSender: {sender}\nReceiver: {receiver}\nAmount: {amount}")

    return tx

def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return response

def makeWallet(passphrase):
    privKey = btc.sha256(passphrase)
    dPrivKey = btc.decode_privkey(privKey, 'hex')
    if passphrase=='':
        messagebox.showerror("에러", "Passphrase를 적으신 후 다시 시도해 주세요.")
        return None, None, None
    elif dPrivKey < btc.N:  # secp256k1 의 N 보다 작으면 OK
        # 개인키로 공개키를 생성한다.
        pubKey = btc.privkey_to_pubkey(privKey)
        
        # 공개키로 지갑 주소를 생성한다. (mainnet 용)
        address = btc.pubkey_to_address(pubKey, 0)
        # 결과 확인
        print("\n\nPassphrase :", passphrase)
        print("\n개인키 :", privKey)
        print("개인키 --> 공개키 :", pubKey)
        print("\n공개키 --> 지갑주소 :", address)
        
        messagebox.showinfo("알림", f"지갑이 정상적으로 만들어졌습니다.\n문구: {passphrase}\n개인키: {privKey}\n공개키: {pubKey}\n지갑주소: {address}")

        wallets.append(Wallet(passphrase, privKey, pubKey, address, blockchain))
        return privKey, pubKey, address
    else:
        print("요청하신 Passphrase로 개인키를 만들었으나, 유효하지 않습니다.")
        print("다른 Passphrase로 다시 시도해 주세요.")
        messagebox.showerror("에러", "요청하신 Passphrase로 개인키를 만들었으나, 유효하지 않습니다.\n다른 Passphrase로 다시 시도해 주세요.")
        return None, None, None

if __name__=="__main__":
    window = tkinter.Tk()
    window.title("Blockchain Assignment")
    window.geometry("1250x800+100+100")
    window.resizable(False, False)

    # 4분할
    Frame0 = tkinter.Frame(window, relief="solid", bd=1)
    Frame0.pack(side="top", fill="both")
    Frame1 = tkinter.Frame(window, relief="solid", bd=1)
    Frame1.pack(side="left", fill="both")
    Frame2 = tkinter.Frame(window, relief="solid", bd=1)
    Frame2.pack(side="left", fill="both")
    Frame3 = tkinter.Frame(window, relief="solid", bd=1)
    Frame3.pack(side="left", fill="both")
    Frame4 = tkinter.Frame(window, relief="solid", bd=1)
    Frame4.pack(side="left", fill="both")

    ####### 잔액 확인 | 0번째 frame ############
    balance_lb = tkinter.Label(Frame0, text="지갑 주소:")
    balance_lb.pack(side="left", fill="both")
    balance_en = tkinter.Entry(Frame0, width=20)
    balance_en.pack(side="left", fill="both")
    balance_btn = tkinter.Button(Frame0,text="잔액확인", overrelief="solid", width=12, repeatdelay=1000)
    balance_btn.pack(side="left", fill="both")
    def get_balance():
        wallet = balance_en.get()
        flag = 0
        for i in range(len(wallets)):
            if wallet == wallets[i].getAddress():
                flag = 1
                messagebox.showinfo("알림", f"잔액확인\n지갑주소: {wallet}\n잔액: {wallets[i].getCoin()}")
        if flag == 0:
            messagebox.showinfo("에러", f"올바른 지갑 주소를 입력해주세요")
        balance_en.delete(0, tkinter.END)
    balance_btn.configure(command=get_balance)

    
    ######## 지갑 생성 | 첫번째 frame(wallet)########
    make_wallet_lb = tkinter.Label(Frame1, text="Wallet", font=('Arial', 20), height=2)
    make_wallet_lb.pack(side="top", fill="both")
    make_wallet_frame = tkinter.Frame(Frame1, relief="solid")
    make_wallet_frame.pack(side="top", fill="both")
    make_wallet_lb = tkinter.Label(make_wallet_frame, text="지갑 생성 문구:")
    make_wallet_lb.grid(row=0, column=0)
    make_wallet_en = tkinter.Entry(make_wallet_frame, width=20)
    make_wallet_en.grid(row=0, column=1)
    make_wallet_btn = tkinter.Button(make_wallet_frame,text="지갑 생성", overrelief="solid", width=12, repeatdelay=1000)
    make_wallet_btn.grid(row=0, column=2)
    make_wallet_frame2 = tkinter.Frame(Frame1, relief="solid")
    scrollbar1=tkinter.Scrollbar(make_wallet_frame2)
    scrollbar1.pack(side="right", fill="y")
    listbox1 = tkinter.Listbox(make_wallet_frame2, yscrollcommand = scrollbar1.set, width=40, height=40)
    listbox1.pack(side="left")
    scrollbar1["command"]=listbox1.yview
    make_wallet_frame2.pack()
    def getPhase_wallet():
        privKey, pubKey, address = makeWallet(make_wallet_en.get())
        if address:
            listbox1.insert(tkinter.END, address)
            make_wallet_en.delete(0, tkinter.END)
    make_wallet_btn.configure(command=getPhase_wallet)

    ######## tx 생성 | 두번째 frame(tx)########
    transaction_lb = tkinter.Label(Frame2, text="Transaction", font=('Arial', 20), height=2)
    transaction_lb.pack(side="top", fill="both")
    transaction_frame = tkinter.Frame(Frame2, relief="solid")
    transaction_frame.pack(side="top", fill="both")
    tx_sender_lb = tkinter.Label(transaction_frame, text="Sender:", width=12)
    tx_sender_lb.grid(row=0, column=0)
    tx_sender_en = tkinter.Entry(transaction_frame, width=30)
    tx_sender_en.grid(row=0, column=1)
    tx_receiver_lb = tkinter.Label(transaction_frame, text="Receiver:", width=12)
    tx_receiver_lb.grid(row=1, column=0)
    tx_receiver_en = tkinter.Entry(transaction_frame, width=30)
    tx_receiver_en.grid(row=1, column=1)
    tx_amount_lb = tkinter.Label(transaction_frame, text="Amount:", width=12)
    tx_amount_lb.grid(row=2, column=0)
    tx_amount_en = tkinter.Entry(transaction_frame, width=30)
    tx_amount_en.grid(row=2, column=1)
    make_tx_btn = tkinter.Button(transaction_frame,text="Tx 생성", overrelief="solid", width=20, repeatdelay=1000)
    make_tx_btn.grid(row=3, column=1)
    transaction_frame2 = tkinter.Frame(Frame2, relief="solid")
    scrollbar2=tkinter.Scrollbar(transaction_frame2)
    scrollbar2.pack(side="right", fill="y")
    listbox2 = tkinter.Text(transaction_frame2, yscrollcommand = scrollbar2.set, width=50, height=45)
    listbox2.pack(side="left")
    scrollbar2["command"]=listbox2.yview
    transaction_frame2.pack()
    def getPhase_tx():
        tx = new_transaction(tx_sender_en.get(), tx_receiver_en.get(), tx_amount_en.get())
        if tx:
            listbox2.configure(state='normal')
            listbox2.insert(tkinter.END, json.dumps(tx, indent=4)+'\n\n')
            tx_sender_en.delete(0, tkinter.END)
            tx_receiver_en.delete(0, tkinter.END)
            tx_amount_en.delete(0, tkinter.END)
            listbox2.configure(state='disabled')
    make_tx_btn.configure(command=getPhase_tx)

    ######## 마이닝 | 세번째 frame(mining)########
    mining_lb = tkinter.Label(Frame3, text="Mining", font=('Arial', 20), height=2)
    mining_lb.pack(side="top", fill="both")
    mining_frame = tkinter.Frame(Frame3, relief="solid")
    mining_frame.pack(side="top", fill="both")
    mining_lb1 = tkinter.Label(mining_frame, text="마이너의 지갑주소: ")
    mining_lb1.grid(row=0, column=0)
    mining_en = tkinter.Entry(mining_frame, width=20)
    mining_en.grid(row=0, column=1)
    mining_btn = tkinter.Button(mining_frame,text="마이닝", overrelief="solid", width=12, repeatdelay=1000)
    mining_btn.grid(row=0, column=2)
    mining_frame2 = tkinter.Frame(Frame3, relief="solid")
    scrollbar3=tkinter.Scrollbar(mining_frame2)
    scrollbar3.pack(side="right", fill="y")
    listbox3 = tkinter.Text(mining_frame2, yscrollcommand = scrollbar3.set, width=50, height=50)
    listbox3.pack(side="left")
    scrollbar3["command"]=listbox3.yview
    mining_frame2.pack()
    def getPhase_mining():
        m = mine(mining_en.get())
        if m:
            #tx에 제거
            listbox2.configure(state='normal')
            listbox2.delete("1.0", "end")
            listbox2.configure(state='disable')
            #block에 추가
            listbox3.configure(state='normal')
            listbox3.insert(tkinter.END, json.dumps(m, indent=4)+'\n\n')
            mining_en.delete(0, tkinter.END)
            listbox3.configure(state='disabled')
    mining_btn.configure(command=getPhase_mining)

    window.mainloop()