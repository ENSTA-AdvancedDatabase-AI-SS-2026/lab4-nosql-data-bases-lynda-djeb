"""
TP5 - Exercice 2 : Benchmark lecture
Point lookup, Range query, Complex query
"""

import time
import random
import statistics
from typing import List, Dict
import json

import redis
from pymongo import MongoClient
from cassandra.cluster import Cluster
from neo4j import GraphDatabase


class ReadBenchmark:
    
    def __init__(self):
        self.results = {}
        
    def setup_test_data(self, nb_records: int = 50000):
        """Prepare les donnees de test"""
        pass
        
    def benchmark_point_lookup(self, nb_queries: int = 10000) -> Dict:
        """Recherche par ID/cl primaire"""
        pass
        
    def benchmark_range_query(self, nb_queries: int = 10000) -> Dict:
        """Recherche par plage"""
        pass
        
    def benchmark_complex_query(self, nb_queries: int = 1000) -> Dict:
        """Requete complexe (agregation/traversal)"""
        pass


class RedisReadBenchmark(ReadBenchmark):
    
    def __init__(self):
        super().__init__()
        self.client = redis.Redis(decode_responses=True)
        
    def setup_test_data(self, nb_records: int = 50000):
        for i in range(nb_records):
            key = f"user:{i:06d}"
            self.client.hset(key, mapping={
                'id': f"{i:06d}",
                'nom': f"User{i}",
                'age': 18 + (i % 50),
                'ville': ['Alger', 'Oran', 'Constantine', 'Annaba'][i % 4],
                'score': i % 1000
            })
            
    def benchmark_point_lookup(self, nb_queries: int = 10000) -> Dict:
        ids = [f"{random.randint(0, 49999):06d}" for _ in range(nb_queries)]
        latencies = []
        
        for uid in ids:
            start = time.perf_counter()
            self.client.hgetall(f"user:{uid}")
            latencies.append((time.perf_counter() - start) * 1000)
            
        return self._compute_stats(latencies, "point_lookup")
        
    def benchmark_range_query(self, nb_queries: int = 10000) -> Dict:
        latencies = []
        
        for _ in range(nb_queries):
            min_age = random.randint(20, 40)
            max_age = min_age + random.randint(5, 20)
            
            start = time.perf_counter()
            # Redis n'a pas de range query native, scan tous les users
            keys = self.client.keys("user:*")
            for key in keys:
                age = int(self.client.hget(key, 'age') or 0)
                if min_age <= age <= max_age:
                    pass
            latencies.append((time.perf_counter() - start) * 1000)
            
        return self._compute_stats(latencies, "range_query")
        
    def benchmark_complex_query(self, nb_queries: int = 1000) -> Dict:
        latencies = []
        
        for _ in range(nb_queries):
            start = time.perf_counter()
            # Top users par score (simule avec sort)
            scores = []
            keys = self.client.keys("user:*")
            for key in keys:
                score = int(self.client.hget(key, 'score') or 0)
                scores.append(score)
            scores.sort(reverse=True)
            top10 = scores[:10]
            latencies.append((time.perf_counter() - start) * 1000)
            
        return self._compute_stats(latencies, "complex_query")
        
    def _compute_stats(self, latencies: List[float], query_type: str) -> Dict:
        latencies.sort()
        return {
            'database': 'Redis',
            'query_type': query_type,
            'queries': len(latencies),
            'avg_ms': round(statistics.mean(latencies), 2),
            'p50_ms': round(latencies[len(latencies)//2], 2),
            'p95_ms': round(latencies[int(len(latencies)*0.95)], 2),
            'p99_ms': round(latencies[int(len(latencies)*0.99)], 2)
        }


class MongoDBReadBenchmark(ReadBenchmark):
    
    def __init__(self):
        super().__init__()
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['benchmark']
        self.collection = self.db['users']
        
    def setup_test_data(self, nb_records: int = 50000):
        self.collection.drop()
        data = []
        for i in range(nb_records):
            data.append({
                'id': f"{i:06d}",
                'nom': f"User{i}",
                'age': 18 + (i % 50),
                'ville': ['Alger', 'Oran', 'Constantine', 'Annaba'][i % 4],
                'score': i % 1000
            })
        self.collection.insert_many(data)
        self.collection.create_index('id')
        self.collection.create_index('age')
        self.collection.create_index('ville')
        
    def benchmark_point_lookup(self, nb_queries: int = 10000) -> Dict:
        ids = [f"{random.randint(0, 49999):06d}" for _ in range(nb_queries)]
        latencies = []
        
        for uid in ids:
            start = time.perf_counter()
            self.collection.find_one({'id': uid})
            latencies.append((time.perf_counter() - start) * 1000)
            
        return self._compute_stats(latencies, "point_lookup")
        
    def benchmark_range_query(self, nb_queries: int = 10000) -> Dict:
        latencies = []
        
        for _ in range(nb_queries):
            min_age = random.randint(20, 40)
            max_age = min_age + random.randint(5, 20)
            
            start = time.perf_counter()
            list(self.collection.find({'age': {'$gte': min_age, '$lte': max_age}}).limit(100))
            latencies.append((time.perf_counter() - start) * 1000)
            
        return self._compute_stats(latencies, "range_query")
        
    def benchmark_complex_query(self, nb_queries: int = 1000) -> Dict:
        latencies = []
        
        for _ in range(nb_queries):
            ville = random.choice(['Alger', 'Oran', 'Constantine', 'Annaba'])
            start = time.perf_counter()
            list(self.collection.aggregate([
                {'$match': {'ville': ville}},
                {'$group': {'_id': '$ville', 'avg_age': {'$avg': '$age'}, 'count': {'$sum': 1}}},
                {'$sort': {'avg_age': -1}}
            ]))
            latencies.append((time.perf_counter() - start) * 1000)
            
        return self._compute_stats(latencies, "complex_query")
        
    def _compute_stats(self, latencies: List[float], query_type: str) -> Dict:
        latencies.sort()
        return {
            'database': 'MongoDB',
            'query_type': query_type,
            'queries': len(latencies),
            'avg_ms': round(statistics.mean(latencies), 2),
            'p50_ms': round(latencies[len(latencies)//2], 2),
            'p95_ms': round(latencies[int(len(latencies)*0.95)], 2),
            'p99_ms': round(latencies[int(len(latencies)*0.99)], 2)
        }


class CassandraReadBenchmark(ReadBenchmark):
    
    def __init__(self):
        super().__init__()
        self.cluster = Cluster(['127.0.0.1'])
        self.session = self.cluster.connect()
        self.session.set_keyspace('benchmark')
        
    def setup_test_data(self, nb_records: int = 50000):
        self.session.execute("TRUNCATE users")
        for i in range(0, nb_records, 100):
            batch = []
            for j in range(100):
                idx = i + j
                if idx >= nb_records:
                    break
                batch.append(f"('{idx:06d}', 'User{idx}', {18 + (idx % 50)}, '{['Alger','Oran','Constantine','Annaba'][idx%4]}', {idx%1000})")
            
            if batch:
                self.session.execute(f"INSERT INTO users (id, nom, age, ville, score) VALUES {','.join(batch)}")
                
    def benchmark_point_lookup(self, nb_queries: int = 10000) -> Dict:
        ids = [f"{random.randint(0, 49999):06d}" for _ in range(nb_queries)]
        latencies = []
        
        for uid in ids:
            start = time.perf_counter()
            self.session.execute("SELECT * FROM users WHERE id = %s", (uid,))
            latencies.append((time.perf_counter() - start) * 1000)
            
        return self._compute_stats(latencies, "point_lookup")
        
    def benchmark_range_query(self, nb_queries: int = 10000) -> Dict:
        latencies = []
        
        for _ in range(nb_queries):
            min_age = random.randint(20, 40)
            max_age = min_age + random.randint(5, 20)
            
            start = time.perf_counter()
            # Cassandra require ALLOW FILTERING pour range sur non-clé
            self.session.execute(
                "SELECT * FROM users WHERE age >= %s AND age <= %s ALLOW FILTERING",
                (min_age, max_age)
            )
            latencies.append((time.perf_counter() - start) * 1000)
            
        return self._compute_stats(latencies, "range_query")
        
    def benchmark_complex_query(self, nb_queries: int = 1000) -> Dict:
        latencies = []
        
        for _ in range(nb_queries):
            start = time.perf_counter()
            # Compter par ville
            result = self.session.execute("SELECT ville, COUNT(*) FROM users GROUP BY ville ALLOW FILTERING")
            list(result)
            latencies.append((time.perf_counter() - start) * 1000)
            
        return self._compute_stats(latencies, "complex_query")
        
    def _compute_stats(self, latencies: List[float], query_type: str) -> Dict:
        latencies.sort()
        return {
            'database': 'Cassandra',
            'query_type': query_type,
            'queries': len(latencies),
            'avg_ms': round(statistics.mean(latencies), 2),
            'p50_ms': round(latencies[len(latencies)//2], 2),
            'p95_ms': round(latencies[int(len(latencies)*0.95)], 2),
            'p99_ms': round(latencies[int(len(latencies)*0.99)], 2)
        }


class Neo4jReadBenchmark(ReadBenchmark):
    
    def __init__(self):
        super().__init__()
        self.driver = GraphDatabase.driver('bolt://localhost:7687', 
                                           auth=('neo4j', 'password123'))
        
    def setup_test_data(self, nb_records: int = 50000):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            
            for i in range(0, nb_records, 500):
                query = "UNWIND $users AS user CREATE (u:User {id: user.id, nom: user.nom, age: user.age, ville: user.ville, score: user.score})"
                users = []
                for j in range(500):
                    idx = i + j
                    if idx >= nb_records:
                        break
                    users.append({
                        'id': f"{idx:06d}",
                        'nom': f"User{idx}",
                        'age': 18 + (idx % 50),
                        'ville': ['Alger', 'Oran', 'Constantine', 'Annaba'][idx % 4],
                        'score': idx % 1000
                    })
                session.run(query, users=users)
                
            session.run("CREATE INDEX user_id IF NOT EXISTS FOR (u:User) ON (u.id)")
            session.run("CREATE INDEX user_age IF NOT EXISTS FOR (u:User) ON (u.age)")
            
    def benchmark_point_lookup(self, nb_queries: int = 10000) -> Dict:
        ids = [f"{random.randint(0, 49999):06d}" for _ in range(nb_queries)]
        latencies = []
        
        with self.driver.session() as session:
            for uid in ids:
                start = time.perf_counter()
                session.run("MATCH (u:User {id: $id}) RETURN u", id=uid)
                latencies.append((time.perf_counter() - start) * 1000)
                
        return self._compute_stats(latencies, "point_lookup")
        
    def benchmark_range_query(self, nb_queries: int = 10000) -> Dict:
        latencies = []
        
        with self.driver.session() as session:
            for _ in range(nb_queries):
                min_age = random.randint(20, 40)
                max_age = min_age + random.randint(5, 20)
                
                start = time.perf_counter()
                session.run("MATCH (u:User) WHERE u.age >= $min AND u.age <= $max RETURN u", 
                           min=min_age, max=max_age)
                latencies.append((time.perf_counter() - start) * 1000)
                
        return self._compute_stats(latencies, "range_query")
        
    def benchmark_complex_query(self, nb_queries: int = 1000) -> Dict:
        latencies = []
        
        with self.driver.session() as session:
            for _ in range(nb_queries):
                start = time.perf_counter()
                session.run("""
                    MATCH (u:User)
                    RETURN u.ville, avg(u.age) AS avg_age, count(u) AS count
                    ORDER BY avg_age DESC
                """)
                latencies.append((time.perf_counter() - start) * 1000)
                
        return self._compute_stats(latencies, "complex_query")
        
    def _compute_stats(self, latencies: List[float], query_type: str) -> Dict:
        latencies.sort()
        return {
            'database': 'Neo4j',
            'query_type': query_type,
            'queries': len(latencies),
            'avg_ms': round(statistics.mean(latencies), 2),
            'p50_ms': round(latencies[len(latencies)//2], 2),
            'p95_ms': round(latencies[int(len(latencies)*0.95)], 2),
            'p99_ms': round(latencies[int(len(latencies)*0.99)], 2)
        }


def run_all_read_benchmarks():
    """Execute tous les benchmarks de lecture"""
    
    print("\n" + "#"*60)
    print("# BENCHMARK LECTURE")
    print("#"*60)
    
    results = []
    
    # Setup test data
    print("\nPreparation des donnees de test...")
    
    for bm_class in [RedisReadBenchmark, MongoDBReadBenchmark, CassandraReadBenchmark, Neo4jReadBenchmark]:
        bm = bm_class()
        bm.setup_test_data(50000)
        print(f"  {bm_class.__name__}: OK")
    
    # Run benchmarks
    for bm_class in [RedisReadBenchmark, MongoDBReadBenchmark, CassandraReadBenchmark, Neo4jReadBenchmark]:
        bm = bm_class()
        
        print(f"\n--- {bm_class.__name__} ---")
        
        r1 = bm.benchmark_point_lookup(5000)
        results.append(r1)
        print(f"  Point lookup: {r1['avg_ms']} ms avg")
        
        r2 = bm.benchmark_range_query(1000)
        results.append(r2)
        print(f"  Range query: {r2['avg_ms']} ms avg")
        
        r3 = bm.benchmark_complex_query(500)
        results.append(r3)
        print(f"  Complex query: {r3['avg_ms']} ms avg")
    
    with open('results/read_benchmark.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results


if __name__ == "__main__":
    run_all_read_benchmarks()
