import json
from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "12345678"

INPUT_FILE = 'final_kg.json'

def insert_graph_data(tx, graph_data):
    
    nodes = graph_data.get('entities', graph_data.get('nodes', []))
    for node in nodes:
        if isinstance(node, str):
            tx.run("MERGE (n:Entity {id: $id})", id=node)
        elif isinstance(node, dict):
            tx.run("MERGE (n:Entity {id: $id}) SET n.type = $type", 
                   id=node.get('id', 'Unknown'), type=node.get('type', 'Unknown'))
            
    print(f"{len(nodes)}개의 노드(Node) 완료")

    edges = graph_data.get('edges', graph_data.get('relations', []))
    for edge in edges:
        if isinstance(edge, dict):
            source = edge.get('source', edge.get('head'))
            target = edge.get('target', edge.get('tail'))
            label = edge.get('label', edge.get('relation', 'RELATED_TO'))
            
            if source and target:
                rel_label = str(label).replace(' ', '_').upper()
                query = f"""
                MATCH (s:Entity {{id: $source}})
                MATCH (t:Entity {{id: $target}})
                MERGE (s)-[r:`{rel_label}`]->(t)
                """
                tx.run(query, source=source, target=target)
                
    print(f"{len(edges)}개의 관계(Edge) 완료.")

try:
    print("JSON 파일 로드")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        kg_data = json.load(f)
    
    if isinstance(kg_data, str):
        kg_data = json.loads(kg_data)

    print("Neo4j 데이터베이스에 연결 중")
    with GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD)) as driver:
        with driver.session() as session:
            session.execute_write(insert_graph_data, kg_data)
            
    print("Neo4j 업로드 성공")

except FileNotFoundError:
    print(f"'{INPUT_FILE}' 파일을 찾을 수 없습니다.")
except Exception as e:
    print(f"업로드 중 오류 발생: {e}")