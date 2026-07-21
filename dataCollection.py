import pandas as pd
import wikipediaapi
import time
import os
import json

INPUT_FILE = 'entity_ids.del'
OUTPUT_FILE = 'wikipedia_rag_data.jsonl'
USER_AGENT = 'MyRAGBot/1.0 (rladngnl@gmail.com)'
LANG = 'en'

wiki = wikipediaapi.Wikipedia(
    user_agent=USER_AGENT,
    language=LANG
)

try:
    df = pd.read_csv(INPUT_FILE, sep='\t', header=None, names=['id', 'entity'])
    print(f"{len(df)}개의 엔티티를 읽어왔습니다.")
except FileNotFoundError:
    print(f"'{INPUT_FILE}' 파일을 찾을 수 없습니다")
    exit()


def fetch_wiki_data(entity_name):
    try:
        page = wiki.page(entity_name)
        if not page.exists():
            return None
        
        data = {
            "entity": entity_name,
            "summary": page.summary,
            "sections": [
                {"section_title": s.title, "text": s.text} 
                for s in page.sections if s.text.strip()
            ]
        }
        return data
    except Exception as e:
        print(f"에러 ({entity_name}): {e}")
        return None
    
test_limit = 1000  # 1000개 수집 시 1000으로 변경
target_entities = df['entity'].head(test_limit)

print(f"\n{len(target_entities)}개 엔티티에 대한 데이터 수집을 시작")

with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
    for idx, entity in enumerate(target_entities):
        print(f"[{idx+1}/{len(target_entities)}] '{entity}' 가져오는 중...", end="")
        
        wiki_data = fetch_wiki_data(entity)
        
        if wiki_data:
            # 수집 성공 시 JSON 파일에 한 줄로 쓰기
            f.write(json.dumps(wiki_data, ensure_ascii=False) + '\n')
            print(" -> [성공!]")
        else:
            print(" -> [실패: 문서 없음 또는 에러]")
            
        time.sleep(0.5)
