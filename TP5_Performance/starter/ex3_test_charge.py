"""
TP5 - Exercice 3 : Test de charge concurrente
50 clients simultanes
"""

import threading
import time
import random
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
import json

import redis
from pymongo import MongoClient
from cassandra.cluster import Cluster
from neo4j import GraphDatabase


class ConcurrentLoadTest:
    
    def __init__(self, db_name: str, nb_clients: int = 50, duration_sec: int = 60):
        self.db_name = db_name
        self.nb_clients = nb_clients
        self.duration_sec = duration_sec
        self.latencies = []
        self.errors = 0
        self.operations = 0
        self.running = True
        
    def worker(self, client_id: int):
        """Simule un client effectuant operations"""
        pass
        
    def run(self) -> Dict:
        self.running = True
        self.latencies = []
        self.errors = 0
        self.operations = 0
        
        with ThreadPoolExecutor(max_workers=self.nb_clients) as executor:
            futures = [executor.submit(self.worker, i) for i in range(self.nb_clients)]
            
            time.sleep(self.duration_sec)
            self.running = False
            
            for f in as_completed(futures):
                f.result()
                
        latencies = [l for l in self.latencies if l > 0]
        if latencies:
            latencies.sort()
            return {
                'database': self.db_name,
                'clients': self.nb_clients,
                'duration_sec': self.duration_sec,
                'total_operations': self.operations,
                'errors': self.errors,
                'throughput_ops_sec': round(self.operations / self.duration_sec, 2),
                'latency_ms': {
                    'avg': round(statistics.mean(latencies), 2),
                    'p50': round(latencies[len(latencies)//2], 2),
                    'p95': round(latencies[int(len(latencies)*0.95)], 2),
                    'p99': round(latencies[int(len(latencies)*0.99)], 2)
                }
            }
        return None


class RedisLoadTest(ConcurrentLoadTest):
    
    def __init__(self, nb_clients: int = 50, duration_sec: int = 60):
        super().__init__('Redis', nb_clients, duration_sec)
        
    def worker(self, client_id: int):
        client = redis.Redis(decode_responses=True)
        
        while self.running:
            op_type = random.choice(['read', 'write'])
            key = f"test:{random.randint(1, 10000)}"
            
            start = time.perf_counter()
            try:
                if op_type == 'read':
                    client.get(key)
                else:
                    client.set(key, f"value_{client_id}_{time.time()}")
                    client.expire(key, 60)
                    
                self.latencies.append((time.perf_counter() - start) * 1000)
                self.operations += 1
            except Exception as e:
                self.errors += 1
                
            time.sleep(random.uniform(0, 0.1))


class MongoDBLoadTest(ConcurrentLoadTest):
    
    def __init__(self, nb_clients: int = 50, duration_sec: int = 60):
        super().__init__('MongoDB', nb_clients, duration_sec)
        
    def worker(self, client_id: int):
        client = MongoClient('localhost', 27017)
        db = client['benchmark']
        collection = db['load_test']
        
        while self.running:
            op_type = random.choice(['read', 'write'])
            doc_id = random.randint(1, 10000)
            
            start = time.perf_counter()
            try:
                if op_type == 'read':
                    collection.find_one({'_id': doc_id})
                else:
                    collection.update_one(
                        {'_id': doc_id},
                        {'$set': {'value': f"val_{client_id}_{time.time()}", 'timestamp': time.time()}},
                        upsert=True
                    )
                    
                self.latencies.append((time.perf_counter() - start) * 1000)
                self.operations += 1
            except Exception as e:
                self.errors += 1
                
            time.sleep(random.uniform(0, 0.1))


class CassandraLoadTest(ConcurrentLoadTest):
    
    def __init__(self, nb_clients: int = 50, duration_sec: int = 60):
        super().__init__('Cassandra', nb_clients, duration_sec)
        
    def worker(self, client_id: int):
        cluster = Cluster(['127.0.0.1'])
        session = cluster.connect()
        session.set_keyspace('benchmark')
        
        while self.running:
            op_type = random.choice(['read', 'write'])
            doc_id = random.randint(1, 10000)
            
            start = time.perf_counter()
            try:
                if op_type == 'read':
                    session.execute("SELECT * FROM load_test WHERE id = %s", (doc_id,))
                else:
                    session.execute(
                        "INSERT INTO load_test (id, value, timestamp) VALUES (%s, %s, %s)",
                        (doc_id, f"val_{client_id}_{time.time()}", time.time())
                    )
                    
                self.latencies.append((time.perf_counter() - start) * 1000)
                self.operations += 1
            except Exception as e:
                self.errors += 1
                
            time.sleep(random.uniform(0, 0.1))
            
        cluster.shutdown()


class Neo4jLoadTest(ConcurrentLoadTest):
    
    def __init__(self, nb_clients: int = 50, duration_sec: int = 60):
        super().__init__('Neo4j', nb_clients, duration_sec)
        
    def worker(self, client_id: int):
        driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password123'))
        
        while self.running:
            op_type = random.choice(['read', 'write'])
            node_id = random.randint(1, 10000)
            
            start = time.perf_counter()
            try:
                with driver.session() as session:
                    if op_type == 'read':
                        session.run("MATCH (n:LoadTest {id: $id}) RETURN n", id=node_id)
                    else:
                        session.run(
                            "MERGE (n:LoadTest {id: $id}) SET n.value = $value, n.timestamp = $timestamp",
                            id=node_id, value=f"val_{client_id}_{time.time()}", timestamp=time.time()
                        )
                    
                self.latencies.append((time.perf_counter() - start) * 1000)
                self.operations += 1
            except Exception as e:
                self.errors += 1
                
            time.sleep(random.uniform(0, 0.1))
            
        driver.close()


def prepare_test_data():
    """Prepare les donnees avant test"""
    
    # Redis
    r = redis.Redis()
    for i in range(1, 10001):
        r.set(f"test:{i}", f"initial_value_{i}")
        
    # MongoDB
    mongo = MongoClient()
    db = mongo['benchmark']
    collection = db['load_test']
    for i in range(1, 10001):
        collection.insert_one({'_id': i, 'value': f"initial_{i}", 'timestamp': time.time()})
    collection.create_index('_id')
    
    # Cassandra
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()
    session.set_keyspace('benchmark')
    session.execute("""
        CREATE TABLE IF NOT EXISTS load_test (
            id int PRIMARY KEY,
            value text,
            timestamp double
        )
    """)
    for i in range(1, 10001):
        session.execute("INSERT INTO load_test (id, value, timestamp) VALUES (%s, %s, %s)", 
                       (i, f"initial_{i}", time.time()))
    cluster.shutdown()
    
    # Neo4j
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password123'))
    with driver.session() as session:
        session.run("CREATE CONSTRAINT load_test_id IF NOT EXISTS FOR (n:LoadTest) REQUIRE n.id IS UNIQUE")
        for i in range(1, 10001):
            session.run("MERGE (n:LoadTest {id: $id}) SET n.value = $value, n.timestamp = $timestamp",
                       id=i, value=f"initial_{i}", timestamp=time.time())
    driver.close()


def run_all_load_tests():
    """Execute tous les tests de charge"""
    
    print("\n" + "#"*60)
    print("# TEST DE CHARGE CONCURRENTE - 50 CLIENTS")
    print("#"*60)
    
    prepare_test_data()
    
    results = []
    
    tests = [
        (RedisLoadTest, "Redis"),
        (MongoDBLoadTest, "MongoDB"),
        (CassandraLoadTest, "Cassandra"),
        (Neo4jLoadTest, "Neo4j")
    ]
    
    for test_class, name in tests:
        print(f"\n--- Test: {name} ---")
        test = test_class(nb_clients=50, duration_sec=30)
        result = test.run()
        if result:
            results.append(result)
            print(f"  Operations: {result['total_operations']}")
            print(f"  Debit: {result['throughput_ops_sec']} ops/sec")
            print(f"  Latence moyenne: {result['latency_ms']['avg']} ms")
            print(f"  P99: {result['latency_ms']['p99']} ms")
            print(f"  Erreurs: {result['errors']}")
    
    with open('results/load_test.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results


if __name__ == "__main__":
    run_all_load_tests()
