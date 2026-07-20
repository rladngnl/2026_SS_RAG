import os
import json
from collections import defaultdict
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USERNAME = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "12345678")

KG_DIR = os.path.join('data', 'kg')

def insert_kg_batch(tx, entities, relations):
    if entities:
        node_batch = [{"id": n} for n in entities if isinstance(n, str)]
        if node_batch:
            tx.run("UNWIND $batch AS row MERGE (n:Entity {id: row.id})", batch=node_batch)
            
    grouped_rels = defaultdict(list)
    for rel in relations:
        if isinstance(rel, list) and len(rel) == 3:
            subj, label, obj = rel
            grouped_rels[label].append({"source": subj, "target": obj})
    
    for label, batch in grouped_rels.items():
        rel_label = str(label).replace(' ', '_').upper()
        query = f"""
        UNWIND $batch AS row
        MATCH (s:Entity {{id: row.source}})
        MATCH (t:Entity {{id: row.target}})
        MERGE (s)-[r:`{rel_label}`]->(t)
        """
        tx.run(query, batch=batch)

try:
    print("Neo4j 연결 중")
    
    if not os.path.exists(KG_DIR):
        raise FileNotFoundError(f"'{KG_DIR}' 폴더가 없습니다")

    kg_files = [f for f in os.listdir(KG_DIR) if f.endswith('.json')]

    with GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD)) as driver:
        with driver.session() as session:
            for filename in kg_files:
                filepath = os.path.join(KG_DIR, filename)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                entities = data.get('entities', [])
                relations = data.get('relations', [])
                
                if entities or relations:
                    session.execute_write(insert_kg_batch, entities, relations)
                    print(f"{filename} 노드 {len(entities)}개, 관계 {len(relations)}개")

    print("\n neo4j에 업로드 성공")

except Exception as e:
    print(f"오류 발생: {e}")