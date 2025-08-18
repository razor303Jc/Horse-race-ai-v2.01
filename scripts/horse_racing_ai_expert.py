#!/usr/bin/env python3
"""
Enhanced AI Context System with Horse Racing Domain Knowledge
Integrates project context with comprehensive horse racing expertise
"""

import json
import subprocess
import psycopg2
import os
from pathlib import Path


class HorseRacingAIExpert:
    def __init__(self):
        self.db_params = {
            "host": "localhost",
            "port": 5435,
            "database": "coding_models_db",
            "user": "jc",
            "password": "password123",
        }

        # Load horse racing domain knowledge
        self.domain_knowledge = self.load_domain_knowledge()

    def load_domain_knowledge(self):
        """Load comprehensive horse racing domain knowledge"""
        knowledge_file = Path(
            "/home/jc/Documents/Horse-race-ai-v2.01/knowledge/"
            "horse_racing_domain_knowledge.md"
        )

        if knowledge_file.exists():
            with open(knowledge_file, "r", encoding="utf-8") as f:
                return f.read()
        else:
            return "Horse racing domain knowledge file not found."

    def get_project_context(self, limit=10):
        """Retrieve recent project files from database"""
        try:
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()

            query = """
            SELECT file_path, file_type, summary, key_functions 
            FROM project_files 
            WHERE file_type IN ('python', 'markdown', 'sql')
            ORDER BY created_at DESC 
            LIMIT %s
            """

            cursor.execute(query, (limit,))
            results = cursor.fetchall()

            context = "## HORSE RACING AI PROJECT CONTEXT:\n\n"
            for file_path, file_type, summary, key_functions in results:
                context += f"**File**: {file_path}\n"
                context += f"**Type**: {file_type}\n"
                context += f"**Summary**: {summary}\n"
                if key_functions:
                    context += f"**Key Functions**: {key_functions}\n"
                context += "\n---\n\n"

            cursor.close()
            conn.close()

            return context

        except Exception as e:
            return f"Error retrieving project context: {str(e)}"

    def create_expert_prompt(self, user_question, context_limit=10):
        """Create comprehensive prompt with domain knowledge and project context"""

        project_context = self.get_project_context(context_limit)

        expert_prompt = f"""# HORSE RACING AI EXPERT SYSTEM

You are an expert AI assistant specializing in horse racing analysis, betting strategies, and AI-powered prediction systems. You have comprehensive knowledge of:

## DOMAIN EXPERTISE:
{self.domain_knowledge}

## PROJECT CONTEXT:
{project_context}

## USER QUESTION:
{user_question}

## RESPONSE GUIDELINES:
1. **Domain Expert**: Use your comprehensive horse racing knowledge
2. **Technical Expert**: Apply AI/ML concepts from the project context  
3. **Practical Advisor**: Provide actionable insights for horse racing analysis
4. **Data-Driven**: Reference specific racing classifications, weight systems, course characteristics
5. **Betting Savvy**: Understand exchange betting, traditional bookmakers, value identification

Draw from both your horse racing domain expertise and the technical capabilities of the Horse Racing AI project to provide expert-level analysis and recommendations.

Please provide a detailed, expert response:"""

        return expert_prompt

    def query_qwen_model(self, prompt):
        """Query Qwen2.5-Coder model with enhanced prompt"""
        try:
            result = subprocess.run(
                ["ollama", "run", "qwen2.5-coder:7b"],
                input=prompt,
                text=True,
                capture_output=True,
                timeout=120,
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error: {result.stderr}"

        except subprocess.TimeoutExpired:
            return "Query timed out after 2 minutes"
        except Exception as e:
            return f"Error querying Qwen model: {str(e)}"

    def query_whiterabbit_model(self, prompt):
        """Query White Rabbit Neo model with enhanced prompt"""
        try:
            result = subprocess.run(
                ["ollama", "run", "jimscard/whiterabbit-neo:13b-q5_K_M"],
                input=prompt,
                text=True,
                capture_output=True,
                timeout=180,
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error: {result.stderr}"

        except subprocess.TimeoutExpired:
            return "Query timed out after 3 minutes"
        except Exception as e:
            return f"Error querying White Rabbit model: {str(e)}"

    def get_expert_analysis(self, question, model="both"):
        """Get expert horse racing analysis from AI models"""

        print(f"\n{'='*80}")
        print("🐎 HORSE RACING AI EXPERT SYSTEM")
        print(f"{'='*80}")
        print(f"📝 Question: {question}")
        print(f"🔄 Loading domain knowledge and project context...")

        # Create expert prompt
        expert_prompt = self.create_expert_prompt(question)

        results = {}

        if model in ["qwen", "both"]:
            print(f"\n🤖 Querying Qwen2.5-Coder (7B) - Technical Analysis...")
            qwen_response = self.query_qwen_model(expert_prompt)
            results["qwen"] = qwen_response

            print(f"\n{'='*60}")
            print("🔧 QWEN2.5-CODER TECHNICAL ANALYSIS:")
            print(f"{'='*60}")
            print(qwen_response)

        if model in ["whiterabbit", "both"]:
            print(f"\n🧠 Querying White Rabbit Neo (13B) - Strategic Analysis...")
            whiterabbit_response = self.query_whiterabbit_model(expert_prompt)
            results["whiterabbit"] = whiterabbit_response

            print(f"\n{'='*60}")
            print("🎯 WHITE RABBIT NEO STRATEGIC ANALYSIS:")
            print(f"{'='*60}")
            print(whiterabbit_response)

        print(f"\n{'='*80}")
        print("✅ EXPERT ANALYSIS COMPLETE")
        print(f"{'='*80}")

        return results


def main():
    """Main interactive interface"""
    expert = HorseRacingAIExpert()

    print(
        """
🐎 HORSE RACING AI EXPERT SYSTEM
================================

Enhanced with comprehensive domain knowledge:
- Race classifications and types
- UK racecourses and characteristics  
- Jockey weight allowances and claims
- Trainer roles and responsibilities
- Betting systems and exchange rules
- Handicapping and rating systems
- Technical terminology and practices

Plus full context from your Horse Racing AI project!

Commands:
- 'quit' or 'exit': Exit the system
- 'models': List available models
- 'qwen <question>': Query only Qwen model
- 'whiterabbit <question>': Query only White Rabbit model
- '<question>': Query both models

Examples:
- "Analyze the impact of weight allowances on handicap races"
- "How should I evaluate horses at Cheltenham vs Newmarket?"
- "What betting strategies work best on exchanges vs traditional bookmakers?"
- "Explain the difference between Group 1 and Class 1 races"
    """
    )

    while True:
        try:
            user_input = input("\n🏇 Enter your horse racing question: ").strip()

            if user_input.lower() in ["quit", "exit"]:
                print("👋 Goodbye! Happy racing!")
                break

            if user_input.lower() == "models":
                print("\nAvailable Models:")
                print("- qwen2.5-coder:7b (Technical Analysis)")
                print("- jimscard/whiterabbit-neo:13b-q5_K_M (Strategic Analysis)")
                continue

            if not user_input:
                print("Please enter a question or 'quit' to exit.")
                continue

            # Parse model-specific queries
            if user_input.lower().startswith("qwen "):
                question = user_input[5:]
                model = "qwen"
            elif user_input.lower().startswith("whiterabbit "):
                question = user_input[12:]
                model = "whiterabbit"
            else:
                question = user_input
                model = "both"

            # Get expert analysis
            results = expert.get_expert_analysis(question, model)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Happy racing!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
