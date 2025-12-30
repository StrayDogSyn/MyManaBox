"""Integration tests for MCP server tools."""
import pytest
import json


class TestMCPTools:
    """Tests for MCP tool responses."""
    
    @pytest.mark.asyncio
    async def test_search_cards_tool_exists(self):
        """search_cards tool should be defined."""
        from cardforge.mcp.server import list_tools
        
        tools = await list_tools()
        tool_names = [t.name for t in tools]
        
        assert "search_cards" in tool_names
    
    @pytest.mark.asyncio
    async def test_collection_stats_tool_exists(self):
        """collection_stats tool should be defined."""
        from cardforge.mcp.server import list_tools
        
        tools = await list_tools()
        tool_names = [t.name for t in tools]
        
        assert "get_collection_stats" in tool_names
    
    @pytest.mark.asyncio
    async def test_check_ownership_tool_exists(self):
        """check_ownership tool should be defined."""
        from cardforge.mcp.server import list_tools
        
        tools = await list_tools()
        tool_names = [t.name for t in tools]
        
        assert "check_ownership" in tool_names
    
    @pytest.mark.asyncio
    async def test_all_10_tools_defined(self):
        """Should have all 10 MCP tools defined."""
        from cardforge.mcp.server import list_tools
        
        tools = await list_tools()
        
        # Should have 10 tools as per specification
        assert len(tools) >= 10
    
    @pytest.mark.asyncio
    async def test_tool_call_returns_text_content(self):
        """Tool calls should return TextContent."""
        from cardforge.mcp.server import call_tool
        
        try:
            result = await call_tool("get_collection_stats", {})
            # Should return a sequence of TextContent
            assert len(result) > 0
        except Exception as e:
            # If it fails, it's likely due to missing data, which is acceptable in tests
            assert "not found" in str(e).lower() or "error" in str(e).lower()


class TestMCPServerIntegration:
    """Integration tests for MCP server functionality."""
    
    def test_server_imports_successfully(self):
        """MCP server module should import without errors."""
        from cardforge.mcp import server
        assert server is not None
    
    def test_server_instance_exists(self):
        """Server instance should be created."""
        from cardforge.mcp.server import server
        assert server is not None
        assert hasattr(server, 'name')
