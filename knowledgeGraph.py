import json
import os
from kg_gen import KGGen
from dotenv import load_dotenv

load_dotenv()

kg = KGGen(
    model="gpt-4o-mini", 
    temperature=0.0,
    api_key=os.getenv("OPENAI_API_KEY")
)

INPUT_FILE = 'wikipedia_rag_data.jsonl'
OUTPUT_DIR = os.path.join('data', 'kg')

os.makedirs(OUTPUT_DIR, exist_ok=True)

try:
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 1000:  # 개수 설정
                break
                
            data = json.loads(line)
            entity_name = data.get('entity', f'Unknown_{i}')

            output_path = os.path.join(OUTPUT_DIR, f"{entity_name.replace('/', '_')}.json")
            if os.path.exists(output_path):
                print(f" [{entity_name}] 이미 존재하여 건너뜁니다.")
                continue
            
            text = f"Entity: {entity_name}\nSummary: {data.get('summary', '')}"
            print(f" [{entity_name}] 지식 그래프 추출 중", end="")
            
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