"""Test the HTTP API for LLM Task integration."""

from homeassistant.components.llm_task import LLMTaskType
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import HomeAssistant

from .conftest import TEST_ENTITY_ID

from tests.typing import WebSocketGenerator


async def test_ws_run_task(
    hass: HomeAssistant,
    hass_ws_client: WebSocketGenerator,
    init_components: None,
) -> None:
    """Test running a task via the WebSocket API."""
    entity = hass.states.get(TEST_ENTITY_ID)
    assert entity is not None
    assert entity.state == STATE_UNKNOWN

    client = await hass_ws_client(hass)

    await client.send_json_auto_id(
        {
            "type": "llm_task/run_task",
            "task_name": "Test Task",
            "entity_id": TEST_ENTITY_ID,
            "task_type": LLMTaskType.SUMMARY.value,
            "prompt": "Test prompt",
        }
    )

    msg = await client.receive_json()

    assert msg["success"]
    assert msg["result"]["result"] == "Mock result"

    entity = hass.states.get(TEST_ENTITY_ID)
    assert entity.state != STATE_UNKNOWN


async def test_ws_preferences(
    hass: HomeAssistant,
    hass_ws_client: WebSocketGenerator,
    init_components: None,
) -> None:
    """Test preferences via the WebSocket API."""
    client = await hass_ws_client(hass)

    # Get initial preferences
    await client.send_json_auto_id({"type": "llm_task/preferences/get"})
    msg = await client.receive_json()
    assert msg["success"]
    assert msg["result"] == {
        "summary_entity_id": None,
        "generate_entity_id": None,
    }

    # Set preferences
    await client.send_json_auto_id(
        {
            "type": "llm_task/preferences/set",
            "summary_entity_id": "llm_task.summary_1",
            "generate_entity_id": "llm_task.generate_1",
        }
    )
    msg = await client.receive_json()
    assert msg["success"]
    assert msg["result"] == {
        "summary_entity_id": "llm_task.summary_1",
        "generate_entity_id": "llm_task.generate_1",
    }

    # Get updated preferences
    await client.send_json_auto_id({"type": "llm_task/preferences/get"})
    msg = await client.receive_json()
    assert msg["success"]
    assert msg["result"] == {
        "summary_entity_id": "llm_task.summary_1",
        "generate_entity_id": "llm_task.generate_1",
    }

    # Set only one preference
    await client.send_json_auto_id(
        {
            "type": "llm_task/preferences/set",
            "summary_entity_id": "llm_task.summary_2",
        }
    )
    msg = await client.receive_json()
    assert msg["success"]
    assert msg["result"] == {
        "summary_entity_id": "llm_task.summary_2",
        "generate_entity_id": "llm_task.generate_1",
    }

    # Get updated preferences
    await client.send_json_auto_id({"type": "llm_task/preferences/get"})
    msg = await client.receive_json()
    assert msg["success"]
    assert msg["result"] == {
        "summary_entity_id": "llm_task.summary_2",
        "generate_entity_id": "llm_task.generate_1",
    }

    # Clear a preference
    await client.send_json_auto_id(
        {
            "type": "llm_task/preferences/set",
            "generate_entity_id": None,
        }
    )
    msg = await client.receive_json()
    assert msg["success"]
    assert msg["result"] == {
        "summary_entity_id": "llm_task.summary_2",
        "generate_entity_id": None,
    }

    # Get updated preferences
    await client.send_json_auto_id({"type": "llm_task/preferences/get"})
    msg = await client.receive_json()
    assert msg["success"]
    assert msg["result"] == {
        "summary_entity_id": "llm_task.summary_2",
        "generate_entity_id": None,
    }
