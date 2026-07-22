## Knowledge Graph 기반 RAG 파이프라인
위키백과 데이터를 수집하여 지식 그래프(Knowledge Graph)를 구축하고, 
이를 Neo4j 그래프 데이터베이스에 적재하여 RAG(Retrieval-Augmented Generation) 시스템의 기반을 마련하는 파이프라인입니다.

dataColleciotn.py : 위키백과 API를 호출하여 wikipedia_rag_data.jsonl 파일 생성

knowledgeGraph.py: LLM을 이용해 텍스트에서 지식 그래프 추출 및 개별 JSON 저장

import_to_neo4j.py: 추출된 JSON 데이터를 읽어 UNWIND 쿼리를 통해 Neo4j에 일괄 적재


