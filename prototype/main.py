from chain.block import Block
from chain.chain import Blockchain
from ai_modules.simple_nn import train_model

# Simula um nó de aprendizado + grava na blockchain
if __name__ == "__main__":
    print("Treinando modelo local...")
    weights = train_model()

    print("Inicializando blockchain...")
    blockchain = Blockchain()

    print("Criando bloco com pesos...")
    new_block = Block(data=weights)
    blockchain.add_block(new_block)

    print("Blockchain atual:")
    for b in blockchain.chain:
        print(b)
