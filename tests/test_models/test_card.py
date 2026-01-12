import pytest
from cardforge.models import Card

class TestCard:
    def test_card_initialization(self):
        """Test basic card initialization."""
        card = Card(name="Lightning Bolt", set_code="m21")
        assert card.name == "Lightning Bolt"
        assert card.set_code == "m21"
        assert str(card) == "Lightning Bolt (m21)"

    def test_card_prices(self):
        """Test card price handling."""
        card = Card(
            name="Sol Ring", 
            set_code="cmr",
            prices={"usd": "1.50", "usd_foil": "3.00"}
        )
        assert card.prices["usd"] == "1.50"
        assert card.prices["usd_foil"] == "3.00"

    def test_card_equality(self):
        """Test card equality based on ID or name/set."""
        card1 = Card(id="1", name="Card A", set_code="set1")
        card2 = Card(id="1", name="Card A", set_code="set1")
        card3 = Card(id="2", name="Card B", set_code="set1")
        
        assert card1 == card2
        assert card1 != card3
