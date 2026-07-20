import subprocess
import sys

def run_script(script_name):
    
    try:
        subprocess.run([sys.executable, script_name], check=True)
        print(f"\n {script_name} 실행")
        
    except subprocess.CalledProcessError as e:
        print(f"\n'{script_name}' 오류")
        sys.exit(1)

if __name__ == "__main__":
    pipeline_scripts = [
        "dataCollection.py",
        "knowledgeGraph.py",
        "import_to_neo4j.py"
    ]
    
    # 리스트에 담긴 순서대로 실행
    for script in pipeline_scripts:
        run_script(script)
        
    print("\n모든 스크립트 완료")