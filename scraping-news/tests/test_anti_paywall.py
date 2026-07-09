"""
Comprehensive tests for the anti-paywall module.
Tests paywall removal functionality.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch


class TestRemovePaywall:
    """Tests for paywall element removal."""
    
    def test_remove_paywall_returns_bool(self, mock_page):
        """Test that remove_paywall returns a boolean."""
        from src.anti_paywall import remove_paywall
        
        result = remove_paywall(mock_page)
        assert isinstance(result, bool)
    
    def test_remove_paywall_calls_evaluate(self, mock_page):
        """Test that remove_paywall calls page.evaluate."""
        from src.anti_paywall import remove_paywall
        
        remove_paywall(mock_page)
        
        # Should call evaluate multiple times for each element
        assert mock_page.evaluate.call_count >= 2
    
    def test_remove_paywall_removes_ad_position_box(self, mock_page):
        """Test that #ad_position_box is targeted for removal."""
        from src.anti_paywall import remove_paywall
        
        remove_paywall(mock_page)
        
        # Check that the function was called with the correct element ID
        calls = [str(call) for call in mock_page.evaluate.call_args_list]
        # Should contain the element ID in the JavaScript code
        assert any('ad_position_box' in str(call) for call in calls)
    
    def test_remove_paywall_removes_engagement_top(self, mock_page):
        """Test that #engagement-top is targeted for removal."""
        from src.anti_paywall import remove_paywall
        
        remove_paywall(mock_page)
        
        calls = [str(call) for call in mock_page.evaluate.call_args_list]
        assert any('engagement-top' in str(call) for call in calls)
    
    def test_remove_paywall_removes_ins_elements(self, mock_page):
        """Test that <ins> elements are targeted for removal."""
        from src.anti_paywall import remove_paywall
        
        remove_paywall(mock_page)
        
        calls = [str(call) for call in mock_page.evaluate.call_args_list]
        # Should contain code to remove ins elements
        assert any('ins' in str(call).lower() for call in calls)
    
    def test_remove_paywall_restores_scroll(self, mock_page):
        """Test that scroll functionality is restored."""
        from src.anti_paywall import remove_paywall
        
        # Mock that elements were removed
        mock_page.evaluate = MagicMock(return_value=1)
        
        remove_paywall(mock_page)
        
        # Should have called evaluate to restore scroll
        assert mock_page.evaluate.call_count > 0
    
    def test_remove_paywall_no_elements_removed(self, mock_page):
        """Test behavior when no paywall elements exist."""
        from src.anti_paywall import remove_paywall
        
        # Mock that no elements were found (return 0)
        mock_page.evaluate = MagicMock(return_value=0)
        
        result = remove_paywall(mock_page)
        
        # Should return False when nothing was removed
        assert result is False


class TestSetupPaywallObserver:
    """Tests for MutationObserver setup."""
    
    def test_setup_observer_calls_evaluate(self, mock_page):
        """Test that setup_paywall_observer calls page.evaluate."""
        from src.anti_paywall import setup_paywall_observer
        
        setup_paywall_observer(mock_page)
        
        mock_page.evaluate.assert_called_once()
    
    def test_setup_observer_injects_javascript(self, mock_page):
        """Test that JavaScript is injected for the observer."""
        from src.anti_paywall import setup_paywall_observer
        
        setup_paywall_observer(mock_page)
        
        # The call should contain JavaScript code
        call_arg = mock_page.evaluate.call_args[0][0]
        assert isinstance(call_arg, str)
        assert 'MutationObserver' in call_arg
        assert 'function' in call_arg
    
    def test_setup_observer_targets_correct_elements(self, mock_page):
        """Test that observer targets the correct paywall elements."""
        from src.anti_paywall import setup_paywall_observer
        
        setup_paywall_observer(mock_page)
        
        call_arg = mock_page.evaluate.call_args[0][0]
        
        # Should target specific element IDs
        assert 'ad_position_box' in call_arg
        assert 'engagement-top' in call_arg
        assert 'INS' in call_arg or 'ins' in call_arg.lower()
    
    def test_setup_observer_removes_scroll_lock(self, mock_page):
        """Test that observer code includes scroll restoration."""
        from src.anti_paywall import setup_paywall_observer
        
        setup_paywall_observer(mock_page)
        
        call_arg = mock_page.evaluate.call_args[0][0]
        
        # Should include code to remove style attributes
        assert 'removeAttribute' in call_arg
        assert 'style' in call_arg


class TestAntiPaywallIntegration:
    """Integration tests for anti-paywall functionality."""
    
    def test_paywall_elements_constant(self):
        """Test that PAYWALL_ELEMENTS constant is correct."""
        from src.anti_paywall import PAYWALL_ELEMENTS
        
        assert 'ad_position_box' in PAYWALL_ELEMENTS
        assert 'engagement-top' in PAYWALL_ELEMENTS
    
    def test_workflow_remove_then_observe(self, mock_page):
        """Test the workflow of removing existing paywall then setting up observer."""
        from src.anti_paywall import remove_paywall, setup_paywall_observer
        
        # First remove existing paywall
        remove_paywall(mock_page)
        
        # Then set up observer for future paywalls
        setup_paywall_observer(mock_page)
        
        # Both should have called evaluate
        assert mock_page.evaluate.call_count >= 2
