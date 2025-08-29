#!/usr/bin/env python3
"""
AI Model Context Query Tool
Query project data from database and feed to AI models
"""

import psycopg2
import subprocess
import json


def get_project_context(project_name="Horse-race-ai-v2.01"):
    """Get project context from database"""
    try:
        conn = psycopg2.connect(database="coding_models_db", user="jc", port=5435)
        cursor = conn.cursor()

        # Get project info
        cursor.execute(
            "SELECT name, description, language, framework FROM projects WHERE name = %s",
            (project_name,),
        )
        project = cursor.fetchone()

        if not project:
            print(f"❌ Project '{project_name}' not found")
            return None

        # Get file list
        cursor.execute(
            """
            SELECT f.file_path, f.file_name, f.language, f.size_bytes 
            FROM files f 
            JOIN projects p ON f.project_id = p.id 
            WHERE p.name = %s 
            ORDER BY f.file_path
            """,
            (project_name,),
        )
        files = cursor.fetchall()

        context = {
            "project": {
                "name": project[0],
                "description": project[1],
                "language": project[2],
                "framework": project[3],
            },
            "files": [
                {"path": f[0], "name": f[1], "language": f[2], "size": f[3]}
                for f in files
            ],
            "total_files": len(files),
        }

        conn.close()
        return context

    except Exception as e:
        print(f"❌ Database error: {e}")
        return None


def query_ai_model(model_name, prompt, context=None):
    """Query Ollama AI model with context"""
    try:
        # Build full prompt with context
        if context:
            full_prompt = f"""
Project Context:
- Name: {context['project']['name']}
- Description: {context['project']['description']}
- Language: {context['project']['language']}
- Framework: {context['project']['framework']}
- Total Files: {context['total_files']}

Key Files Include:
{chr(10).join([f"- {f['path']} ({f['language']}, {f['size']} bytes)" for f in context['files'][:10]])}
{"..." if len(context['files']) > 10 else ""}

User Question: {prompt}

Please answer considering the Horse Racing AI project context above.
"""
        else:
            full_prompt = prompt

        # Query Ollama
        result = subprocess.run(
            ["ollama", "run", model_name],
            input=full_prompt,
            text=True,
            capture_output=True,
        )

        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"❌ Error: {result.stderr}"

    except Exception as e:
        return f"❌ Exception: {e}"


def main():
    """Main function"""
    print("🔍 Fetching project context from database...")
    context = get_project_context()

    if not context:
        return

    print(f"✅ Loaded context for {context['project']['name']}")
    print(f"   📁 {context['total_files']} files indexed")
    print(f"   🏗️  Framework: {context['project']['framework']}")

    # Test questions
    questions = [
        "What is the main purpose of this Horse Racing AI project?",
        "What are the key Python modules in this project?",
        "How would you improve the ML pipeline architecture?",
    ]

    models = ["qwen2.5-coder:7b", "jimscard/whiterabbit-neo:13b-q5_K_M"]

    for question in questions:
        print(f"\n❓ Question: {question}")

        for model in models:
            print(f"\n🤖 {model}:")
            response = query_ai_model(model, question, context)
            print(response[:500] + "..." if len(response) > 500 else response)
            print("-" * 50)


if __name__ == "__main__":
    main()
