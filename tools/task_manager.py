#!/usr/bin/env python3
"""
🎯 AI Racing Task Manager - Simple Interface
===========================================

Simple command-line interface for managing AI Racing improvement tasks.
"""

import json
from pathlib import Path
from datetime import datetime
import argparse


class TaskManager:
    """Simple task management interface."""

    def __init__(self):
        self.todo_file = Path("ai_racing_todo.json")
        self.load_todos()

    def load_todos(self):
        """Load todos from file."""
        if self.todo_file.exists():
            with open(self.todo_file, "r", encoding="utf-8") as f:
                self.todos = json.load(f)
        else:
            print("❌ TODO file not found. Run ai_racing_todo_manager.py first.")
            exit(1)

    def save_todos(self):
        """Save todos to file."""
        self.todos["project_info"]["last_updated"] = datetime.now().isoformat()
        with open(self.todo_file, "w", encoding="utf-8") as f:
            json.dump(self.todos, f, indent=2, ensure_ascii=False)

    def list_immediate_tasks(self):
        """List immediate opportunity tasks."""
        print("⚡ IMMEDIATE OPPORTUNITIES - QUICK WINS")
        print("=" * 50)

        immediate = self.todos.get("immediate_opportunities", {})
        for i, (key, task) in enumerate(immediate.items(), 1):
            status = task["status"]
            hours = task["estimated_hours"]
            impact = task["expected_impact"]

            print(f"\n{i}. {task['title']}")
            print(f"   {status} | {hours}h | {impact}")
            print(f"   Key: {key}")

    def start_task(self, task_key):
        """Mark a task as started."""
        task = self.find_task(task_key)
        if task:
            task["status"] = "🔄 IN PROGRESS"
            task["started_date"] = datetime.now().isoformat()
            self.save_todos()
            print(f"✅ Started task: {task['title']}")
        else:
            print(f"❌ Task not found: {task_key}")

    def complete_task(self, task_key):
        """Mark a task as completed."""
        task = self.find_task(task_key)
        if task:
            task["status"] = "✅ COMPLETED"
            task["completed_date"] = datetime.now().isoformat()
            self.save_todos()
            print(f"🎉 Completed task: {task['title']}")
        else:
            print(f"❌ Task not found: {task_key}")

    def find_task(self, task_key):
        """Find task by key in any section."""
        sections = [
            "immediate_opportunities",
            "high_priority",
            "medium_priority",
            "advanced_features",
        ]

        for section in sections:
            if task_key in self.todos.get(section, {}):
                return self.todos[section][task_key]

        return None

    def show_progress(self):
        """Show overall progress."""
        print("📊 PROJECT PROGRESS")
        print("=" * 30)

        sections = [
            ("⚡ Immediate", "immediate_opportunities"),
            ("🔥 High Priority", "high_priority"),
            ("⚡ Medium Priority", "medium_priority"),
            ("🚀 Advanced", "advanced_features"),
        ]

        total_tasks = 0
        completed_tasks = 0
        in_progress_tasks = 0

        for section_name, section_key in sections:
            section = self.todos.get(section_key, {})
            section_total = len(section)
            section_completed = sum(
                1 for task in section.values() if "✅" in task["status"]
            )
            section_progress = sum(
                1 for task in section.values() if "🔄" in task["status"]
            )

            total_tasks += section_total
            completed_tasks += section_completed
            in_progress_tasks += section_progress

            if section_total > 0:
                percent = (section_completed / section_total) * 100
                print(
                    f"{section_name}: {section_completed}/{section_total} ({percent:.0f}%)"
                )

        print(f"\n📊 OVERALL: {completed_tasks}/{total_tasks} completed")
        print(f"🔄 IN PROGRESS: {in_progress_tasks} tasks")

        if total_tasks > 0:
            overall_percent = (completed_tasks / total_tasks) * 100
            print(f"🎯 COMPLETION: {overall_percent:.1f}%")


def main():
    """Main interface."""
    parser = argparse.ArgumentParser(description="AI Racing Task Manager")
    parser.add_argument(
        "action",
        choices=["list", "start", "complete", "progress"],
        help="Action to perform",
    )
    parser.add_argument("--task", help="Task key for start/complete actions")

    args = parser.parse_args()

    manager = TaskManager()

    if args.action == "list":
        manager.list_immediate_tasks()
    elif args.action == "start":
        if args.task:
            manager.start_task(args.task)
        else:
            print("❌ Please specify --task for start action")
    elif args.action == "complete":
        if args.task:
            manager.complete_task(args.task)
        else:
            print("❌ Please specify --task for complete action")
    elif args.action == "progress":
        manager.show_progress()


if __name__ == "__main__":
    main()
