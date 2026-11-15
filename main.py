# 터미널에서 동작하는 할 일 관리 프로그램
# 할 일 하나는 {"title": 제목, "done": 완료 여부} 모양의 딕셔너리로 기억한다.
# 목록은 todos.json 파일에 저장하고, 프로그램을 시작할 때 다시 불러온다.

import json  # 파이썬 데이터를 JSON 글자로 바꾸거나 되돌리는 기본 도구
from pathlib import Path  # 파일 경로를 다루는 기본 도구

from rich.console import Console  # 색깔과 표를 터미널에 그려 주는 도구 (rich 패키지)
from rich.table import Table  # 표를 만드는 도구 (rich 패키지)
from rich.text import Text  # 글자를 꾸밈 없이 그대로 보여 줄 때 쓰는 도구

# 표를 화면에 출력할 때 쓸 콘솔 (print 대신 console.print 를 쓴다)
console = Console()

# 저장 파일 위치: 어느 폴더에서 실행하든 main.py와 같은 폴더의 todos.json을 쓴다.
# __file__ 은 지금 이 파일(main.py)의 경로이고, .parent 는 그 파일이 있는 폴더다.
TODO_FILE = Path(__file__).parent / "todos.json"


def load_todos():
    """todos.json에서 할 일 목록을 불러온다. 파일이 없으면 빈 목록을 돌려준다."""
    if not TODO_FILE.exists():
        return []

    try:
        # encoding="utf-8" 은 한글이 깨지지 않게 해 준다.
        with open(TODO_FILE, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # 파일 내용이 망가져서 읽을 수 없을 때는 빈 목록으로 시작한다.
        print("todos.json 내용을 읽을 수 없어서 빈 목록으로 시작합니다.")
        return []


def save_todos(todos):
    """할 일 목록을 todos.json에 저장한다."""
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        # ensure_ascii=False: 한글을 그대로 저장 (안 하면 우 같은 글자로 바뀜)
        # indent=2: 사람이 읽기 좋게 줄을 바꾸고 들여쓰기
        json.dump(todos, f, ensure_ascii=False, indent=2)


def show_menu():
    """메뉴를 화면에 보여 준다."""
    print()
    print("===== 할 일 관리 =====")
    print("1. 목록 보기  2. 추가  3. 완료  4. 삭제  5. 종료")


def show_todos(todos):
    """할 일 목록을 번호, 상태, 할 일 세 칸짜리 표로 보여 준다."""
    if not todos:
        print("할 일이 없습니다.")
        return

    # 표를 만들고 칸(열) 제목을 정한다.
    table = Table(title="할 일 목록")
    table.add_column("번호", justify="right")  # 번호는 오른쪽 정렬
    table.add_column("상태", justify="center")  # 상태는 가운데 정렬
    table.add_column("할 일")

    # enumerate(..., start=1)은 1부터 번호를 붙여 준다.
    for number, todo in enumerate(todos, start=1):
        # 완료했으면 초록색 "완료", 아니면 그냥 "미완료"로 표시한다.
        if todo["done"]:
            status = Text("완료", style="green")
        else:
            status = Text("미완료")

        # 제목은 Text()로 감싸서 넣는다.
        # rich는 [red] 같은 글자를 색깔 명령으로 알아듣기 때문에,
        # 제목에 대괄호가 들어 있어도 쓴 그대로 보이게 하려는 것이다.
        table.add_row(str(number), status, Text(todo["title"]))

    console.print(table)


def add_todo(todos):
    """새 할 일을 입력받아 목록에 추가한다."""
    # strip()은 앞뒤 공백을 없애 준다.
    title = input("할 일 제목: ").strip()
    if title == "":
        print("제목이 비어 있어서 추가하지 않았습니다.")
        return

    # 새 할 일은 아직 완료하지 않았으므로 done은 False다.
    todos.append({"title": title, "done": False})
    save_todos(todos)  # 바뀐 목록을 바로 파일에 저장
    print(f"'{title}'을(를) 추가했습니다.")


def ask_number(todos):
    """목록을 보여 주고 번호를 입력받아 리스트 위치(인덱스)를 돌려준다.

    잘못 입력하면 None을 돌려준다. (완료, 삭제에서 함께 사용)
    """
    if not todos:
        print("할 일이 없습니다.")
        return None

    show_todos(todos)
    text = input("번호를 입력하세요: ").strip()

    # 숫자가 아닌 글자를 int()로 바꾸면 ValueError가 나므로 미리 잡아 준다.
    try:
        number = int(text)
    except ValueError:
        print("숫자를 입력해 주세요.")
        return None

    # 목록에 없는 번호인지 확인한다.
    if number < 1 or number > len(todos):
        print("목록에 없는 번호입니다.")
        return None

    # 사용자가 보는 번호는 1부터, 리스트 인덱스는 0부터 시작하므로 1을 뺀다.
    return number - 1


def complete_todo(todos):
    """고른 할 일을 완료 상태로 바꾼다."""
    index = ask_number(todos)
    if index is None:
        return

    todos[index]["done"] = True
    save_todos(todos)  # 바뀐 목록을 바로 파일에 저장
    print(f"'{todos[index]['title']}'을(를) 완료했습니다.")


def delete_todo(todos):
    """고른 할 일을 목록에서 지운다."""
    index = ask_number(todos)
    if index is None:
        return

    # pop()은 그 위치의 항목을 꺼내면서 목록에서 지운다.
    removed = todos.pop(index)
    save_todos(todos)  # 바뀐 목록을 바로 파일에 저장
    print(f"'{removed['title']}'을(를) 삭제했습니다.")


def main():
    # 저장해 둔 할 일 목록을 불러온다. (파일이 없으면 빈 리스트)
    todos = load_todos()

    # 5번(종료)을 고를 때까지 계속 반복한다.
    while True:
        show_menu()
        choice = input("메뉴를 고르세요: ").strip()

        if choice == "1":
            show_todos(todos)
        elif choice == "2":
            add_todo(todos)
        elif choice == "3":
            complete_todo(todos)
        elif choice == "4":
            delete_todo(todos)
        elif choice == "5":
            print("프로그램을 종료합니다. 안녕히 가세요!")
            break  # while 반복을 빠져나간다.
        else:
            print("잘못된 선택입니다. 1~5 중에서 골라 주세요.")


# 이 파일을 직접 실행했을 때만 main()을 부른다.
if __name__ == "__main__":
    main()
