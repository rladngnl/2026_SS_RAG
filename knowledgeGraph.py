import json
import os
from kg_gen import KGGen
from dotenv import load_dotenv

load_dotenv()

API_CONFIGS = {
    "gemini": {
        "model_name": "gemini/gemini-2.5-flash",
        "env_key": "GEMINI_API_KEY"
    },
    "openai": {
        "model_name": "gpt-4o-mini",
        "env_key": "OPENAI_API_KEY"
    }
}

ACTIVE_API = "openai"

config = API_CONFIGS[ACTIVE_API]
api_key = os.getenv(config["env_key"])

if not api_key:
    raise ValueError(f" '{config['env_key']}' .env 파일을 확인해주세요.")

os.environ[config["env_key"]] = api_key
kg = KGGen(model=config["model_name"])

INPUT_FILE = 'wikipedia_rag_data.jsonl'
individual_graphs = []

try:
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        # 개수 설정
        for i, line in enumerate(f):
            if i >= 3: 
                break
                
            data = json.loads(line)
            entity_name = data['entity']
            text_to_process = f"Entity: {data['title']}\nSummary: {data['summary']}"
            
            print(f"[{entity_name}] 그래프 추출 중...")
            
            graph = kg.generate(
                input_data=text_to_process, 
                cluster=False
            )
            individual_graphs.append(graph)

    final_knowledge_graph = kg.aggregate(individual_graphs)
    
    with open('final_kg.json', 'w', encoding='utf-8') as out_f:
        if hasattr(final_knowledge_graph, 'model_dump'):
            graph_data = final_knowledge_graph.model_dump()
        elif hasattr(final_knowledge_graph, 'dict'):
            graph_data = final_knowledge_graph.dict()
        else:
            graph_data = final_knowledge_graph
            
        json.dump(graph_data, out_f, ensure_ascii=False, indent=2, default=list)
        
    print("final_kg.json 저장")
    
except FileNotFoundError:
    print(f"'{INPUT_FILE}' 파일이 존재하지 않습니다. 경로를 확인해주세요.")
except Exception as e:
    print(f"실행 중 오류가 발생했습니다: {e}")