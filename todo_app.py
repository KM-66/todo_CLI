#!/usr/bin/env python3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class TodoApp:
    def __init__(self, data_file: str = "todos.json"):
        self.data_file = data_file
        self.todos: List[Dict] = []
        self.load_todos()

    def load_todos(self) -> None:
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as file:
                    self.todos = json.load(file)
            except (json.JSONDecodeError, IOError):
                self.todos = []
        else:
            self.todos = []

    def save_todos(self) -> None:
        try:
            with open(self.data_file, 'w', encoding='utf-8') as file:
                json.dump(self.todos, file, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"エラー: データの保存に失敗しました - {e}")

    def add_todo(self, task: str) -> None:
        todo = {
            "id": len(self.todos) + 1,
            "task": task,
            "completed": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.todos.append(todo)
        self.save_todos()
        print(f"タスクを追加しました: {task}")

    def list_todos(self) -> None:
        if not self.todos:
            print("タスクがありません。")
            return
        
        print("\n=== Todo リスト ===")
        for todo in self.todos:
            status = "✓" if todo["completed"] else "○"
            print(f"{todo['id']:2d}. [{status}] {todo['task']}")
            print(f"    作成日: {todo['created_at']}")

    def complete_todo(self, todo_id: int) -> None:
        todo = self.find_todo_by_id(todo_id)
        if todo:
            if todo["completed"]:
                print("このタスクはすでに完了しています。")
            else:
                todo["completed"] = True
                todo["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_todos()
                print(f"タスクを完了しました: {todo['task']}")
        else:
            print("指定されたIDのタスクが見つかりません。")

    def delete_todo(self, todo_id: int) -> None:
        todo = self.find_todo_by_id(todo_id)
        if todo:
            self.todos.remove(todo)
            self.save_todos()
            print(f"タスクを削除しました: {todo['task']}")
        else:
            print("指定されたIDのタスクが見つかりません。")

    def find_todo_by_id(self, todo_id: int) -> Optional[Dict]:
        for todo in self.todos:
            if todo["id"] == todo_id:
                return todo
        return None

    def show_menu(self) -> None:
        print("\n=== CUI Todo アプリ ===")
        print("1. タスク一覧表示")
        print("2. タスク追加")
        print("3. タスク完了")
        print("4. タスク削除")
        print("5. 終了")
        print("=" * 20)

    def get_user_input(self, prompt: str) -> str:
        try:
            return input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nアプリケーションを終了します。")
            exit(0)

    def get_integer_input(self, prompt: str) -> Optional[int]:
        try:
            return int(self.get_user_input(prompt))
        except ValueError:
            print("無効な入力です。数字を入力してください。")
            return None

    def run(self) -> None:
        print("CUI Todo アプリへようこそ！")
        
        while True:
            self.show_menu()
            choice = self.get_user_input("選択してください (1-5): ")
            
            if choice == "1":
                self.list_todos()
            
            elif choice == "2":
                task = self.get_user_input("新しいタスクを入力してください: ")
                if task:
                    self.add_todo(task)
                else:
                    print("タスク名が空です。")
            
            elif choice == "3":
                self.list_todos()
                if self.todos:
                    todo_id = self.get_integer_input("完了するタスクのIDを入力してください: ")
                    if todo_id is not None:
                        self.complete_todo(todo_id)
            
            elif choice == "4":
                self.list_todos()
                if self.todos:
                    todo_id = self.get_integer_input("削除するタスクのIDを入力してください: ")
                    if todo_id is not None:
                        self.delete_todo(todo_id)
            
            elif choice == "5":
                print("アプリケーションを終了します。お疲れさまでした！")
                break
            
            else:
                print("無効な選択です。1-5の数字を入力してください。")
            
            input("\nEnterキーを押して続行...")

def main():
    app = TodoApp()
    app.run()

if __name__ == "__main__":
    main()