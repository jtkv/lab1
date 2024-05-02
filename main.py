import datetime
import hashlib
import json
import random
from flask import Flask, jsonify, request
import psycopg2
from faker import Faker

fake = Faker()

NAMES = [fake.name() for _ in range(50)]
POKEMONS = [
    "Pikachu",
    "Charizard",
    "Bulbasaur",
    "Squirtle",
    "Jigglypuff",
    "Snorlax",
    "Eevee",
    "Mewtwo",
    "Gengar",
    "Meowth",
    "Psyduck",
    "Charmander",
    "Mew",
    "Vaporeon",
    "Flareon",
    "Jolteon",
    "Blastoise",
    "Dragonite",
    "Gyarados",
    "Lapras",
    "Butterfree",
    "Snorlax",
    "Machamp",
    "Arcanine",
    "Raichu",
    "Alakazam",
    "Magikarp",
    "Golem",
    "Ditto",
    "Zapdos",
    "Articuno",
    "Moltres",
    "Gloom",
    "Clefairy",
    "Clefable",
    "Chansey",
    "Kingler",
    "Nidoking",
    "Nidoqueen",
    "Persian",
    "Golduck",
    "Poliwrath",
    "Tentacruel",
    "Victreebel",
    "Rapidash",
    "Slowbro",
    "Magneton",
    "Farfetch'd",
    "Dodrio",
    "Seaking"
]

INSERT_SQL = """
    INSERT INTO firstLab (index, previous_hash, proof, animal_type, pet_name, timestamp)
    VALUES (%(index)s, %(previous_hash)s, %(proof)s, %(animal_type)s, %(pet_name)s, %(timestamp)s)
"""

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS firstLab (
    index INTEGER PRIMARY KEY,
    previous_hash TEXT,
    proof INTEGER,
    animal_type TEXT,
    pet_name TEXT,
    timestamp TIMESTAMP
);
"""

SELECT_ALL_SQL = """
    SELECT * FROM firstLab
"""

class Blockchain:
    def __init__(self):
        self.chain = []
        cursor.execute(CREATE_TABLE_SQL)
        cursor.execute(SELECT_ALL_SQL)
        rows = cursor.fetchall()
        if not len(rows):
            self.new_block(proof=1, previous_hash='0')
        else:
            for row in rows:
                block = {
                    "index": row[0],
                    "previous_hash": row[1],
                    "proof": row[2],
                    "animal_type": row[3],
                    "pet_name": row[4],
                    "timestamp": str(row[5]),
                }
                self.chain.append(block)

    def new_block(self, proof, previous_hash, animal_type="Charizard", pet_name="Ash"):
        block = {
            "index": len(self.chain) + 1,
            "previous_hash": previous_hash,
            "proof": proof,
            "animal_type": animal_type,
            "pet_name": pet_name,
            "timestamp": str(datetime.datetime.now()),
        }
        
        self.chain.append(block)
        cursor.execute(INSERT_SQL, block)
        return block

    
    @staticmethod
    def hash(block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    @property
    def last_block(self):
        return self.chain[-1]
    
    
    @staticmethod
    def valid_proof(last_proof, proof):
        hash_operation = hashlib.sha256(str(proof**2 - last_proof**2).encode()).hexdigest()
        return hash_operation[:5] == "00000"
    
    def PoW(self, last_proof):
        proof = 1
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof
        
    def chain_valid(self, chain):
        last_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block["previous_hash"] != self.hash(last_block):
                return False
            if not self.valid_proof(last_block["proof"], block["proof"]):
                return False
            last_block = block
            block_index += 1
        return True

conn = psycopg2.connect(dbname="postgres", user="postgres", password="admin", host="localhost", port=2222)
cursor = conn.cursor()
conn.autocommit = True
app = Flask(__name__)
blockchain = Blockchain()



@app.route('/mine', methods=['GET'])
def mine_block():
    animal_type = request.args.get("animal_type") or random.choice(POKEMONS)
    pet_name = request.args.get("pet_name") or random.choice(NAMES)
    previous_block = blockchain.last_block
    previous_proof = previous_block['proof']
    proof = blockchain.PoW(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.new_block(proof, previous_hash, animal_type=animal_type, pet_name=pet_name)
    
    response = {
        'message': 'A block is MINED',
        'index': block['index'],
        'previous_hash': block['previous_hash'],
        'proof': block['proof'],
        "animal_type": block["animal_type"],
        "pet_name": block["pet_name"],
        'timestamp': block['timestamp'],
    }
    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def display_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200


# Проверка валидности блокчейна
@app.route('/valid', methods=['GET'])
def valid():
    valid = blockchain.chain_valid(blockchain.chain)
    if valid:
        response = {'message': 'The Blockchain is valid.'}
    else:
        response = {'message': 'The Blockchain is not valid.'}
    return jsonify(response), 200


@app.route('/', methods=["GET"])
def start():
    return "Работает штатно!", 200


app.run(host='0.0.0.0', port=1431)
