import json
import os
from kg_gen import KGGen
from dotenv import load_dotenv

load_dotenv()

# 1. 모델별 설정값 정의
API_CONFIGS = {
    "openai": {
        "model_name": "gpt-4o-mini",
        "env_key": "OPENAI_API_KEY",
        "folder_name": "openai"
    },
    "gemini": {
        "model_name": "gemini/gemini-2.5-flash",
        "env_key": "GEMINI_API_KEY",
        "folder_name": "gemini"
    },
    "deepseek": {
        "model_name": "deepseek/deepseek-chat",
        "env_key": "DEEPSEEK_API_KEY",
        "folder_name": "deepseek"
    }
}

ACTIVE_API = "openai" #사용할 모델(folder_name) 입력하면 됨.

config = API_CONFIGS[ACTIVE_API]
api_key = os.getenv(config["env_key"])

if not api_key:
    raise ValueError(f"'{config['env_key']}' 환경변수를 찾을 수 없습니다. .env 파일을 확인해 주세요.")

kg = KGGen(
    model=config["model_name"], 
    temperature=0.0,
    api_key=api_key
)

INPUT_FILE = 'wikipedia_rag_data.jsonl'

OUTPUT_DIR = os.path.join('data', 'kg', config["folder_name"])
os.makedirs(OUTPUT_DIR, exist_ok=True)

try:
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 10:  # 개수 설정
                break
                
            data = json.loads(line)
            entity_name = data.get('entity', f'Unknown_{i}')

            output_path = os.path.join(OUTPUT_DIR, f"{entity_name.replace('/', '_')}.json")
            if os.path.exists(output_path):
                print(f"[{entity_name}] 이미 존재하여 건너뜁니다.")
                continue
            
            text = f"Entity: {entity_name}\nSummary: {data.get('summary', '')}"
            print(f"[{entity_name}] 지식 그래프 추출 중 ({ACTIVE_API})", end="")
            
            try:
                graph = kg.generate(input_data=text, context=entity_name)
                
                result = {
                    "entities": list(graph.entities),
                    "edges": list(graph.edges),
                    "relations": [list(r) for r in graph.relations]
                }
                
                with open(output_path, 'w', encoding='utf-8') as out:
                    json.dump(result, out, ensure_ascii=False, indent=2)
                    
                print(" -> 성공")
                
            except Exception as e:
                print(f" -> 실패: {e}")

except FileNotFoundError:
    print(f"'{INPUT_FILE}' 파일이 없습니다.")
except Exception as e:
    print(f"전체 실행 중 오류 발생: {e}")