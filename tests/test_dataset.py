"""Test dataset loading and prompt building for MBPP+ dataset."""

import pytest


@pytest.fixture
def tasks():
    from helpers.data import load_mbpp_plus

    return load_mbpp_plus()


def test_load_mbpp_plus(tasks):
    assert len(tasks) > 0, "No tasks loaded from MBPP+ dataset."
    for task in tasks:
        assert "task_id" in task, "Task missing 'task_id'."
        assert "prompt" in task, "Task missing 'prompt'."
        assert "code" in task, "Task missing 'code'."
        assert "test_list" in task, "Task missing 'test_list'."


def test_build_chat_messages(tasks):
    from helpers.prompts import build_chat_messages

    for task in tasks:
        messages = build_chat_messages(task)
        assert isinstance(messages, list), "Chat messages should be a list."
        assert len(messages) == 2, (
            "There should be exactly two messages (system and user)."
        )
        assert messages[0]["role"] == "system", (
            "First message should be a system message."
        )
        assert messages[1]["role"] == "user", "Second message should be a user message."
        assert task["prompt"] in messages[1]["content"], (
            "User message should contain the task prompt."
        )
