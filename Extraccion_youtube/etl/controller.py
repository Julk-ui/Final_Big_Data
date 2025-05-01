"""This module provides the RP To-Do model-controller."""

from pathlib import Path
from typing import Any, Dict, List, NamedTuple

from etl import DB_READ_ERROR, ID_ERROR, extract
from etl.database import DatabaseHandler


class CurrentTodo(NamedTuple):
    todo: Dict[str, Any]
    error: int


class Todoer:
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)

    def add(self, path: str = '') -> CurrentTodo:
        """Add a new text to the database."""
        result = extract.extract_audio(path)
        regex = extract.regex(result)

        todo = {
            "Text": result,
            "Path": path,
            "BigData": regex,
        }

        read = self._db_handler.read_todos()
        if read.error == DB_READ_ERROR:
            return CurrentTodo(todo, read.error)
        read.todo_list.append(todo)
        write = self._db_handler.write_todos(read.todo_list)
        return CurrentTodo(todo, write.error)

    def get_todo_list(self) -> List[Dict[str, Any]]:
        """Return the current to-do list."""
        read = self._db_handler.read_todos()
        return read.todo_list

    def remove_all(self) -> CurrentTodo:
        """Remove all to-dos from the database."""
        write = self._db_handler.write_todos([])
        return CurrentTodo({}, write.error)
