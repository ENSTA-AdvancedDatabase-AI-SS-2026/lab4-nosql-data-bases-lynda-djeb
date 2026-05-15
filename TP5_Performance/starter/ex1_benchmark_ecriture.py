"""
TP5 - Exercice 1 : Benchmark d'ecriture
100 000 enregistrements par base
Mesure debit, latence, ressources
"""

import time
import psutil
import threading
import json
from datetime import datetime
from typing import Dict, List
import statistics

# Redis
import redis

# MongoDB
from pymongo import MongoClient

# Cassandra
from cassandra.cluster import Cluster
from cassandra.query import BatchStatement, SimpleStatement

# Neo4j
from neo4j import GraphDatabase


class MetricsCollector:
    """Collecte les metriques CPU/Memoire pendant le benchmark"""
    
    def __init__(self):
        self.running = False
        self.cpu_samples = []
        self.memory_samples = []
        
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._collect)
        self.thread.start()
        
    def _collect(self):
        while self.running:
            self.cpu_samples.append(psutil.cpu_percent(interval=0.1))
            self.memory_samples.append(psutil.virtual_memory().percent)
            time.sleep(0.1)
            
    def stop(self):
        self.running = False
        self.thread.join()
        
    def get_stats(self):
        return {
            'cpu_avg': statistics.mean(self.cpu_samples),
            'cpu_max': max(self.cpu_samples),
            'memory_avg': statistics.mean(self.memory_samples),
            'memory_max': max(self.memory_samples)
        }


class RedisBenchmark:
    """Benchmark pour Redis"""
    
    def __init__(self):
        self.client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.latencies = []
        
    def cleanup(self):
        self.client.flushdb()
        
    def insert_batch(self, data: List[Dict]) -> float:
        """Insertion batch avec pipeline"""
        pipe = self.client.pipeline()
        start = time.perf_counter()
        
        for item in data:
            key = f"user:{item['id']}"
            pipe.hset(key, mapping=item)
            pipe.expire(key, 3600)
            
        pipe.execute()
        end = time.perf_counter()
        return (end - start) * 1000  # ms
        
    def benchmark(self, nb_records: int = 100000):
        print("\n" + "="*50)
        print("BENCHMARK REDIS")
        print("="*50)
        
        self.cleanup()
        metrics = MetricsCollector()
        metrics.start()
        
        batch_size = 1000
        total_time = 0
        self.latencies = []
        
        for i in range(0, nb_records, batch_size):
            batch = []
            for j in range(batch_size):
                idx = i + j
                if idx >= nb_records:
                    break
                batch.append({
                    'id': f"{idx:06d}",
                    'nom': f"User{idx}",
                    'age': 18 + (idx % 50),
                    'ville': ['Alger', 'Oran', 'Constantine', 'Annaba'][idx % 4],
                    'score': idx % 1000
                })
            
            latency = self.insert_batch(batch)
            self.latencies.append(latency)
            total_time += latency
            
        metrics.stop()
        
        # Calcul des stats
        self.latencies.sort()
        p50 = self.latencies[len(self.latencies) // 2]
        p95 = self.latencies[int(len(self.latencies) * 0.95)]
        p99 = self.latencies[int(len(self.latencies) * 0.99)]
        
        total_seconds = total_time / 1000
        throughput = nb_records / total_seconds
        
        results = {
            'database': 'Redis',
            'records': nb_records,
            'total_time_sec': round(total_seconds, 2),
            'throughput_records_sec': round(throughput, 2),
            'latency_ms': {
                'p50': round(p50, 2),
                'p95': round(p95, 2),
                'p99': round(p99, 2),
                'min': round(min(self.latencies), 2),
                'max': round(max(self.latencies), 2)
            },
            'resources': metrics.get_stats()
        }
        
        self._print_results(results)
        return results
        
    def _print_results(self, results):
        print(f"\n--- RESULTATS REDIS ---")
        print(f"Total: {results['records']} enregistrements")
        print(f"Temps: {results['total_time_sec']} secondes")
        print(f"Debit: {results['throughput_records_sec']} rec/s")
        print(f"Latence P50: {results['latency_ms']['p50']} ms")
        print(f"Latence P95: {results['latency_ms']['p95']} ms")
        print(f"Latence P99: {results['latency_ms']['p99']} ms")
        print(f"CPU moyen: {results['resources']['cpu_avg']:.1f}%")
        print(f"Memoire: {results['resources']['memory_avg']:.1f}%")


class MongoDBBenchmark:
    """Benchmark pour MongoDB"""
    
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['benchmark']
        self.collection = self.db['users']
        self.latencies = []
        
    def cleanup(self):
        self.db.drop_collection('users')
        
    def create_indexes(self):
        self.collection.create_index('id')
        self.collection.create_index('ville')
        self.collection.create_index([('age', -1)])
        
    def insert_batch(self, data: List[Dict]) -> float:
        start = time.perf_counter()
        self.collection.insert_many(data)
        end = time.perf_counter()
        return (end - start) * 1000
        
    def benchmark(self, nb_records: int = 100000):
        print("\n" + "="*50)
        print("BENCHMARK MONGODB")
        print("="*50)
        
        self.cleanup()
        self.create_indexes()
        metrics = MetricsCollector()
        metrics.start()
        
        batch_size = 1000
        total_time = 0
        self.latencies = []
        
        for i in range(0, nb_records, batch_size):
            batch = []
            for j in range(batch_size):
                idx = i + j
                if idx >= nb_records:
                    break
                batch.append({
                    'id': f"{idx:06d}",
                    'nom': f"User{idx}",
                    'age': 18 + (idx % 50),
                    'ville': ['Alger', 'Oran', 'Constantine', 'Annaba'][idx % 4],
                    'score': idx % 1000,
                    'timestamp': datetime.now()
                })
            
            latency = self.insert_batch(batch)
            self.latencies.append(latency)
            total_time += latency
            
        metrics.stop()
        
        self.latencies.sort()
        p50 = self.latencies[len(self.latencies) // 2]
        p95 = self.latencies[int(len(self.latencies) * 0.95)]
        p99 = self.latencies[int(len(self.latencies) * 0.99)]
        
        total_seconds = total_time / 1000
        throughput = nb_records / total_seconds
        
        results = {
            'database': 'MongoDB',
            'records': nb_records,
            'total_time_sec': round(total_seconds, 2),
            'throughput_records_sec': round(throughput, 2),
            'latency_ms': {
                'p50': round(p50, 2),
                'p95': round(p95, 2),
                'p99': round(p99, 2),
                'min': round(min(self.latencies), 2),
                'max': round(max(self.latencies), 2)
            },
            'resources': metrics.get_stats()
        }
        
        self._print_results(results)
        return results
        
    def _print_results(self, results):
        print(f"\n--- RESULTATS MONGODB ---")
        print(f"Total: {results['records']} enregistrements")
        print(f"Temps: {results['total_time_sec']} secondes")
        print(f"Debit: {results['throughput_records_sec']} rec/s")
        print(f"Latence P50: {results['latency_ms']['p50']} ms")
        print(f"Latence P95: {results['latency_ms']['p95']} ms")
        print(f"Latence P99: {results['latency_ms']['p99']} ms")
        print(f"CPU moyen: {results['resources']['cpu_avg']:.1f}%")
        print(f"Memoire: {results['resources']['memory_avg']:.1f}%")


class CassandraBenchmark:
    """Benchmark pour Cassandra"""
    
    def __init__(self):
        self.cluster = Cluster(['127.0.0.1'])
        self.session = self.cluster.connect()
        self._init_keyspace()
        self.latencies = []
        
    def _init_keyspace(self):
        self.session.execute("""
            CREATE KEYSPACE IF NOT EXISTS benchmark
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
        """)
        self.session.set_keyspace('benchmark')
        
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id text,
                nom text,
                age int,
                ville text,
                score int,
                PRIMARY KEY (id)
            )
        """)
        
    def cleanup(self):
        self.session.execute("TRUNCATE users")
        
    def insert_batch(self, data: List[Dict]) -> float:
        start = time.perf_counter()
        batch = BatchStatement()
        
        for item in data:
            batch.add(SimpleStatement(
                "INSERT INTO users (id, nom, age, ville, score) VALUES (%s, %s, %s, %s, %s)"
            ), (item['id'], item['nom'], item['age'], item['ville'], item['score']))
            
        self.session.execute(batch)
        end = time.perf_counter()
        return (end - start) * 1000
        
    def benchmark(self, nb_records: int = 100000):
        print("\n" + "="*50)
        print("BENCHMARK CASSANDRA")
        print("="*50)
        
        self.cleanup()
        metrics = MetricsCollector()
        metrics.start()
        
        batch_size = 500
        total_time = 0
        self.latencies = []
        
        for i in range(0, nb_records, batch_size):
            batch = []
            for j in range(batch_size):
                idx = i + j
                if idx >= nb_records:
                    break
                batch.append({
                    'id': f"{idx:06d}",
                    'nom': f"User{idx}",
                    'age': 18 + (idx % 50),
                    'ville': ['Alger', 'Oran', 'Constantine', 'Annaba'][idx % 4],
                    'score': idx % 1000
                })
            
            latency = self.insert_batch(batch)
            self.latencies.append(latency)
            total_time += latency
            
        metrics.stop()
        
        self.latencies.sort()
        p50 = self.latencies[len(self.latencies) // 2]
        p95 = self.latencies[int(len(self.latencies) * 0.95)]
        p99 = self.latencies[int(len(self.latencies) * 0.99)]
        
        total_seconds = total_time / 1000
        throughput = nb_records / total_seconds
        
        results = {
            'database': 'Cassandra',
            'records': nb_records,
            'total_time_sec': round(total_seconds, 2),
            'throughput_records_sec': round(throughput, 2),
            'latency_ms': {
                'p50': round(p50, 2),
                'p95': round(p95, 2),
                'p99': round(p99, 2),
                'min': round(min(self.latencies), 2),
                'max': round(max(self.latencies), 2)
            },
            'resources': metrics.get_stats()
        }
        
        self._print_results(results)
        return results
        
    def _print_results(self, results):
        print(f"\n--- RESULTATS CASSANDRA ---")
        print(f"Total: {results['records']} enregistrements")
        print(f"Temps: {results['total_time_sec']} secondes")
        print(f"Debit: {results['throughput_records_sec']} rec/s")
        print(f"Latence P50: {results['latency_ms']['p50']} ms")
        print(f"Latence P95: {results['latency_ms']['p95']} ms")
        print(f"Latence P99: {results['latency_ms']['p99']} ms")
        print(f"CPU moyen: {results['resources']['cpu_avg']:.1f}%")
        print(f"Memoire: {results['resources']['memory_avg']:.1f}%")


class Neo4jBenchmark:
    """Benchmark pour Neo4j"""
    
    def __init__(self):
        self.driver = GraphDatabase.driver('bolt://localhost:7687', 
                                           auth=('neo4j', 'password123'))
        self.latencies = []
        
    def cleanup(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            
    def insert_batch(self, data: List[Dict]) -> float:
        start = time.perf_counter()
        with self.driver.session() as session:
            for item in data:
                session.run(
                    "CREATE (u:User {id: $id, nom: $nom, age: $age, ville: $ville, score: $score})",
                    item
                )
        end = time.perf_counter()
        return (end - start) * 1000
        
    def benchmark(self, nb_records: int = 100000):
        print("\n" + "="*50)
        print("BENCHMARK NEO4J")
        print("="*50)
        
        self.cleanup()
        metrics = MetricsCollector()
        metrics.start()
        
        batch_size = 500
        total_time = 0
        self.latencies = []
        
        for i in range(0, nb_records, batch_size):
            batch = []
            for j in range(batch_size):
                idx = i + j
                if idx >= nb_records:
                    break
                batch.append({
                    'id': f"{idx:06d}",
                    'nom': f"User{idx}",
                    'age': 18 + (idx % 50),
                    'ville': ['Alger', 'Oran', 'Constantine', 'Annaba'][idx % 4],
                    'score': idx % 1000
                })
            
            latency = self.insert_batch(batch)
            self.latencies.append(latency)
            total_time += latency
            
        metrics.stop()
        
        self.latencies.sort()
        p50 = self.latencies[len(self.latencies) // 2]
        p95 = self.latencies[int(len(self.latencies) * 0.95)]
        p99 = self.latencies[int(len(self.latencies) * 0.99)]
        
        total_seconds = total_time / 1000
        throughput = nb_records / total_seconds
        
        results = {
            'database': 'Neo4j',
            'records': nb_records,
            'total_time_sec': round(total_seconds, 2),
            'throughput_records_sec': round(throughput, 2),
            'latency_ms': {
                'p50': round(p50, 2),
                'p95': round(p95, 2),
                'p99': round(p99, 2),
                'min': round(min(self.latencies), 2),
                'max': round(max(self.latencies), 2)
            },
            'resources': metrics.get_stats()
        }
        
        self._print_results(results)
        return results
        
    def _print_results(self, results):
        print(f"\n--- RESULTATS NEO4J ---")
        print(f"Total: {results['records']} enregistrements")
        print(f"Temps: {results['total_time_sec']} secondes")
        print(f"Debit: {results['throughput_records_sec']} rec/s")
        print(f"Latence P50: {results['latency_ms']['p50']} ms")
        print(f"Latence P95: {results['latency_ms']['p95']} ms")
        print(f"Latence P99: {results['latency_ms']['p99']} ms")
        print(f"CPU moyen: {results['resources']['cpu_avg']:.1f}%")
        print(f"Memoire: {results['resources']['memory_avg']:.1f}%")


def run_all_benchmarks():
    """Execute tous les benchmarks"""
    
    print("\n" + "#"*60)
    print("# BENCHMARK ECRITURE - 100 000 ENREGISTREMENTS")
    print("#"*60)
    
    results = []
    
    # Redis
    redis_bm = RedisBenchmark()
    results.append(redis_bm.benchmark(100000))
    
    # MongoDB
    mongo_bm = MongoDBBenchmark()
    results.append(mongo_bm.benchmark(100000))
    
    # Cassandra
    cassandra_bm = CassandraBenchmark()
    results.append(cassandra_bm.benchmark(100000))
    
    # Neo4j
    neo4j_bm = Neo4jBenchmark()
    results.append(neo4j_bm.benchmark(10000))  # Moins pour Neo4j
    
    # Sauvegarde
    with open('results/write_benchmark.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results


if __name__ == "__main__":
    run_all_benchmarks()
