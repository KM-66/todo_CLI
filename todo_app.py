#!/usr/bin/env python3
import json # データを.json　のファイルで管理できる
import os # ファイルが存在するかチェックするモジュール
from datetime import datetime # 現在の日付を取得するモジュール
from typing import List, Dict, Optional # 今の型がどういう物なのかを提示するモジュール
import tkinter as tk
import tkinter.font as font
import threading


# 変数の設定
WORK_MIN = 25
BREAK_MIN = 5

root = None
status_label = None
timer_label = None
start_stop_button = None

is_work_time = True
remaining_time = WORK_MIN * 60
timer_running = False
timer_id = None

class TodoApp:
    def __init__(self, data_file: str = "todos.json"): # data_file todosの初期設定およびload_todos関数の起動
        self.data_file = data_file
        self.todos: List[Dict] = []
        self.load_todos()

    def load_todos(self) -> None: # todos.json　のファイルに何か書き込みがあった場合、　todos に読み込む　エラー、空の場合の例外処理
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as file:
                    self.todos = json.load(file)
            except (json.JSONDecodeError, IOError):
                self.todos = []
        else:
            self.todos = []

    def save_todos(self) -> None: # todos.jsonファイルへの書き込み処理及び例外処理
        try:
            with open(self.data_file, 'w', encoding='utf-8') as file:
                json.dump(self.todos, file, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"エラー: データの保存に失敗しました - {e}")

    def add_todo(self, task: str) -> None: # inputされたtaskをもとにtodoディクショナリを作成、todosのリストに追加、save_todos
        todo = {
            "id": len(self.todos) + 1,
            "task": task,
            "completed": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.todos.append(todo)
        self.save_todos()
        print(f"タスクを追加しました: {task}")

    def list_todos(self) -> None: # self.todos内のデータをprint 無いときはその旨をprint
        if not self.todos:
            print("タスクがありません。")
            return
        
        print("\n=== Todo リスト ===")
        for todo in self.todos:
            status = "✓" if todo["completed"] else "○"
            print(f"{todo['id']:2d}. [{status}] {todo['task']}")
            print(f"    作成日: {todo['created_at']}")

    def complete_todo(self, todo_id: int) -> None:# inputされたidを完了させsave_todos、及び例外処理
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

    def delete_todo(self, todo_id: int) -> None: # inputされたidをもとにfind_todo_by_id起動、存在したらremove後save_todos
        todo = self.find_todo_by_id(todo_id)
        if todo:
            self.todos.remove(todo)
            self.save_todos()
            print(f"タスクを削除しました: {todo['task']}")
        else:
            print("指定されたIDのタスクが見つかりません。")

    def find_todo_by_id(self, todo_id: int) -> Optional[Dict]: # inputされたidが存在するかどうか判断する
        for todo in self.todos:
            if todo["id"] == todo_id:
                return todo
        return None

    def show_menu(self) -> None: # メニュー表示
        print("\n=== CUI Todo アプリ ===")
        print("1. タスク一覧表示")
        print("2. タスク追加")
        print("3. タスク完了")
        print("4. タスク削除")
        print("5. ポモドーロタイマー作成")
        print("6. 終了")
        print("=" * 20)

    def get_user_input(self, prompt: str) -> str: # inputの処理及び例外処理（str　タスクを入力する際）
        try:
            return input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nアプリケーションを終了します。")
            exit(0)

    def get_integer_input(self, prompt: str) -> Optional[int]: # inputの処理及び例外処理（int）
        try:
            return int(self.get_user_input(prompt))
        except ValueError:
            print("無効な入力です。数字を入力してください。")
            return None
        
    def update_display(self):
    # 残り時間を画面に表示する
        global is_work_time, remaining_time, root, status_label, timer_label

        # ステータスの更新
        if is_work_time:
            status_text = f"作業中 ({WORK_MIN}分)"
            if root: root.config(bg="#d9534f")
        else:
            status_text = f"休憩中 ({BREAK_MIN}分)"
            if root: root.config(bg="#5cb85c")

        if status_label: status_label.config(text=status_text)

        # 時間の表示形式をMM:SSに変換
        minutes, seconds = divmod(remaining_time, 60)
        time_string = f"{minutes:02d}:{seconds:02d}"
        if timer_label: timer_label.config(text=time_string)

    def countdown(self):
        """カウントダウン処理を行う"""
        global remaining_time, is_work_time, timer_id

        if remaining_time > 0:
            self.update_display()
            remaining_time -= 1
            # 1000ミリ秒（1秒）後にもう一度この関数を呼び出す
            if root: timer_id = root.after(1000, self.countdown)
        else:
            # 時間が0になったら、作業と休憩を切り替える
            is_work_time = not is_work_time
            if is_work_time:
                remaining_time = WORK_MIN * 60
            else:
                remaining_time = BREAK_MIN * 60
            self.countdown() # 次のタイマーを即座に開始

    def stop_timer(self):
        """タイマーを一時停止する"""
        global timer_running, timer_id, root
        if timer_id and root:
            root.after_cancel(timer_id)
            timer_running = False

    def start_timer(self):
        """タイマーを開始または再開する"""
        global timer_running, start_stop_button
        if not timer_running:
            timer_running = True
            self.countdown()
            if start_stop_button: start_stop_button.config(text="停止")

    def toggle_timer(self):
        """タイマーの開始と停止を切り替える"""
        global timer_running, start_stop_button
        if timer_running:
            self.stop_timer()
            if start_stop_button: start_stop_button.config(text="再開")
        else:
            self.start_timer()

    def close_window(self):
        """ウィンドウを閉じて、関連するグローバル変数をすべてリセットする"""
        global root, timer_id, timer_running, status_label, timer_label, start_stop_button

        if root:
            # 実行中のタイマー (after) をキャンセル
            if timer_id:
                root.after_cancel(timer_id)
            
            # ウィンドウを破棄
            root.destroy()

        # すべてのグローバル変数を初期状態に戻す
        root = None
        timer_id = None
        timer_running = False
        status_label = None
        timer_label = None
        start_stop_button = None

    def run_pomodoro_timer(self):
        """タイマーウィンドウを作成し、実行するメイン関数"""
        global root, status_label, timer_label, start_stop_button, is_work_time, remaining_time

        # 既にウィンドウが存在する場合は何もしない
        if root and root.winfo_exists():
            return

        # グローバル変数の初期化
        is_work_time = True
        remaining_time = WORK_MIN * 60
        
        root = tk.Tk()
        root.title("ポモドーロタイマー")
        root.geometry("350x180")
        root.attributes("-topmost", True)

        # フォントの設定
        timer_font = font.Font(family='Helvetica', size=48, weight='bold')
        status_font = font.Font(family='Helvetica', size=16)

        # ウィジェットの作成
        status_label = tk.Label(root, text="", font=status_font)
        status_label.pack(pady=5)

        timer_label = tk.Label(root, text="", font=timer_font)
        timer_label.pack(pady=10)

        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)

        start_stop_button = tk.Button(button_frame, text="停止", width=8, command=self.toggle_timer)
        start_stop_button.pack(side=tk.LEFT, padx=10)

        quit_button = tk.Button(button_frame, text="終了", width=8, command=self.close_window)
        quit_button.pack(side=tk.LEFT, padx=10)

        # ウィンドウが閉じられたときの処理
        root.protocol("WM_DELETE_WINDOW",self.close_window)

        # タイマーを開始
        self.start_timer()
        root.mainloop()

    def start_my_timer(self):
        # タイマーがGUIをブロックしないように別スレッドで実行
        timer_thread = threading.Thread(target=self.run_pomodoro_timer)
        timer_thread.daemon = True # メインアプリ終了時にタイマースレッドも終了
        timer_thread.start()
        print("タイマーウィンドウを起動しました。")

    def run(self) -> None: # 主要な機能の起動、全体の流れ show_menu起動後inputされた数字ごとにやることを分ける
        print("CUI Todo アプリへようこそ！")
        
        while True:
            self.show_menu()
            choice = self.get_user_input("選択してください (1-6): ")
            
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
            
            elif choice == '5':
                print('タイマーを作成します。')
                self.start_my_timer()

            elif choice == "6":
                print("アプリケーションを終了します。お疲れさまでした！")
                break
            
            else:
                print("無効な選択です。1-6の数字を入力してください。")
            
            input("\nEnterキーを押して続行...")

def main(): # app.runの起動
    app = TodoApp()
    app.run()
    input("何かキーを押すとメインプログラムが終了します...")
if __name__ == "__main__": # mainの例外処理　詳しくはわからない
    main()