"""Protocol-level regression tests for the migrated MCP servers."""

import importlib.util
import sys
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

from mcp.client import Client
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

import server


# Resolve the secondary server explicitly because prompts is intentionally not a package.
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_legacy_server() -> ModuleType:
    """Load the legacy-output server as an isolated module for protocol testing."""
    path = PROJECT_ROOT / "prompts" / "server.py"
    spec = importlib.util.spec_from_file_location("legacy_oblique_server", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load legacy server from {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MCPServerTests(unittest.IsolatedAsyncioTestCase):
    """Verify tool discovery and output behavior through the v2 client contract."""

    async def test_main_server_exposes_tool_and_preserves_all_output_modes(self) -> None:
        """The active server should expose one tool with all three established formats."""
        expected_fragments = {
            "0": "<thinking>\n*Consulting the rubber duck*—Reverse",
            "1": "<thinking>\nReverse",
            "2": "<thinking>\n*Consulting the rubber duck*",
        }

        # Use the in-process v2 client so discovery and invocation cross the SDK boundary.
        async with Client(server.mcp) as client:
            tools = await client.list_tools()
            self.assertEqual([tool.name for tool in tools.tools], ["ObliqueStrategies"])

            for mode, expected_fragment in expected_fragments.items():
                # Fix randomness so each assertion proves mode policy rather than lucky output.
                with (
                    self.subTest(mode=mode),
                    patch.object(server, "OUTPUT_MODE", mode),
                    patch.object(
                        server.random,
                        "choice",
                        side_effect=["Consulting the rubber duck", "Reverse"],
                    ),
                ):
                    result = await client.call_tool("ObliqueStrategies", {})
                    self.assertFalse(result.is_error)
                    self.assertIn(expected_fragment, result.content[0].text)

    async def test_secondary_server_uses_v2_and_preserves_result_envelope(self) -> None:
        """The secondary server should remain callable with its structured result envelope."""
        legacy_server = load_legacy_server()

        # Fix randomness before crossing MCP so the result-envelope assertion is deterministic.
        with patch.object(
            legacy_server.random,
            "choice",
            side_effect=["Consulting the rubber duck", "Reverse"],
        ):
            # Invoke through MCP to prove migrated registration and structured output together.
            async with Client(legacy_server.mcp) as client:
                tools = await client.list_tools()
                self.assertEqual([tool.name for tool in tools.tools], ["ObliqueStrategies"])

                result = await client.call_tool("ObliqueStrategies", {})
                self.assertFalse(result.is_error)
                self.assertEqual(
                    result.structured_content,
                    {"result": "Now Consulting the rubber duck\n<thinking>\nReverse"},
                )

    async def test_secondary_stdio_advertises_tools_only_with_compatibility_handlers(self) -> None:
        """The legacy initialization should hide the empty compatibility capabilities."""
        parameters = StdioServerParameters(
            command=sys.executable,
            args=[str(PROJECT_ROOT / "prompts" / "server.py")],
            cwd=PROJECT_ROOT,
        )

        # Exercise the no-argument entrypoint and inspect its real initialization response.
        async with stdio_client(parameters) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                initialization = await session.initialize()
                self.assertIsNotNone(initialization.capabilities.tools)
                self.assertIsNone(initialization.capabilities.prompts)
                self.assertIsNone(initialization.capabilities.resources)

                prompts = await session.list_prompts()
                resources = await session.list_resources()
                self.assertEqual(prompts.prompts, [])
                self.assertEqual(resources.resources, [])

    async def test_stdio_entrypoint_serves_the_tool_in_card_only_mode(self) -> None:
        """The documented process command should complete a real stdio tool call."""
        parameters = StdioServerParameters(
            command=sys.executable,
            args=[str(PROJECT_ROOT / "server.py"), "1"],
            cwd=PROJECT_ROOT,
        )

        # Spawn the documented entrypoint so transport setup is tested outside this process.
        async with Client(stdio_client(parameters)) as client:
            tools = await client.list_tools()
            self.assertEqual([tool.name for tool in tools.tools], ["ObliqueStrategies"])

            result = await client.call_tool("ObliqueStrategies", {})
            self.assertFalse(result.is_error)
            self.assertIn("<thinking>\n", result.content[0].text)
            self.assertNotRegex(result.content[0].text, r"<thinking>\n\*[^*]+\*")


if __name__ == "__main__":
    unittest.main()
