"""seed messaging data

Revision ID: 010
Revises: 009
Create Date: 2025-01-07 17:51:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, Boolean, DateTime, Text
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None

def upgrade():
    # Define table structures for bulk insert
    messaging_actions_table = table('messaging_actions',
        column('amazon_order_id', String),
        column('marketplace_id', String),
        column('action_name', String),
        column('is_available', Boolean),
        column('description', String)
    )
    
    buyer_attributes_table = table('buyer_attributes',
        column('amazon_order_id', String),
        column('locale', String),
        column('country_code', String),
        column('language_code', String)
    )
    
    messages_table = table('messages',
        column('amazon_order_id', String),
        column('message_type', String),
        column('subject', String),
        column('body', Text),
        column('status', String),
        column('sent_at', DateTime)
    )
    
    # Get some existing order IDs for seeding (these match the order IDs from 002_seed_data.py)
    order_ids = [
        "111-1111111-1110000",
        "111-1111111-1110001",
        "111-1111111-1110002",
        "111-1111111-1110003",
        "111-1111111-1110004",
        "111-1111111-1110005",
        "111-1111111-1110006",
        "111-1111111-1110007",
        "111-1111111-1110008",
        "111-1111111-1110009"
    ]
    
    # Messaging actions data - different actions available for different orders
    actions_data = []
    
    # Standard actions available for most orders
    standard_actions = [
        {
            "name": "confirmCustomizationDetails", 
            "description": "Confirm product customization details like size, color, or personalization"
        },
        {
            "name": "confirmDeliveryDetails", 
            "description": "Confirm delivery instructions or address details"
        },
        {
            "name": "confirmOrderDetails", 
            "description": "Confirm order specifications or requirements"
        },
        {
            "name": "legalDisclosure", 
            "description": "Send required legal disclosures or compliance information"
        }
    ]
    
    # Special actions for specific scenarios
    special_actions = [
        {
            "name": "negativeFeedbackRemoval", 
            "description": "Request removal of negative feedback after issue resolution"
        },
        {
            "name": "warranty", 
            "description": "Send warranty information or warranty-related communications"
        },
        {
            "name": "digitalAccessKey", 
            "description": "Send digital access keys for software or digital products"
        },
        {
            "name": "unexpectedProblem", 
            "description": "Notify buyer about unexpected problems with the order"
        },
        {
            "name": "amazonMotors", 
            "description": "Send Amazon Motors specific communications for automotive products"
        },
        {
            "name": "confirmServiceDetails", 
            "description": "Confirm service appointment details or service requirements"
        },
        {
            "name": "invoice", 
            "description": "Send invoice or billing information to the buyer"
        }
    ]
    
    # Create actions for orders
    for i, order_id in enumerate(order_ids):
        marketplace_id = "ATVPDKIKX0DER" if i % 3 == 0 else "A2EUQ1WTGCTBG2" if i % 3 == 1 else "A1AM78C64UM0Y8"
        
        # Add standard actions for all orders
        for action in standard_actions:
            actions_data.append({
                'amazon_order_id': order_id,
                'marketplace_id': marketplace_id,
                'action_name': action["name"],
                'is_available': True,
                'description': action["description"]
            })
        
        # Add some special actions based on order characteristics
        if i % 4 == 0:  # Every 4th order gets negative feedback removal
            actions_data.append({
                'amazon_order_id': order_id,
                'marketplace_id': marketplace_id,
                'action_name': "negativeFeedbackRemoval",
                'is_available': True,
                'description': special_actions[0]["description"]
            })
        
        if i % 3 == 0:  # Every 3rd order gets warranty action
            actions_data.append({
                'amazon_order_id': order_id,
                'marketplace_id': marketplace_id,
                'action_name': "warranty",
                'is_available': True,
                'description': special_actions[1]["description"]
            })
        
        if i % 5 == 0:  # Every 5th order gets digital access key
            actions_data.append({
                'amazon_order_id': order_id,
                'marketplace_id': marketplace_id,
                'action_name': "digitalAccessKey",
                'is_available': True,
                'description': special_actions[2]["description"]
            })
        
        if i % 6 == 0:  # Some orders have unexpected problems
            actions_data.append({
                'amazon_order_id': order_id,
                'marketplace_id': marketplace_id,
                'action_name': "unexpectedProblem",
                'is_available': True,
                'description': special_actions[3]["description"]
            })
        
        if i % 7 == 0:  # Some orders are automotive
            actions_data.append({
                'amazon_order_id': order_id,
                'marketplace_id': marketplace_id,
                'action_name': "amazonMotors",
                'is_available': True,
                'description': special_actions[4]["description"]
            })
    
    # Buyer attributes data
    locales = [
        {"locale": "en-US", "country": "US", "language": "en"},
        {"locale": "en-CA", "country": "CA", "language": "en"},
        {"locale": "fr-CA", "country": "CA", "language": "fr"},
        {"locale": "es-MX", "country": "MX", "language": "es"},
        {"locale": "en-GB", "country": "GB", "language": "en"},
        {"locale": "de-DE", "country": "DE", "language": "de"},
        {"locale": "fr-FR", "country": "FR", "language": "fr"},
        {"locale": "it-IT", "country": "IT", "language": "it"},
        {"locale": "es-ES", "country": "ES", "language": "es"},
        {"locale": "ja-JP", "country": "JP", "language": "ja"}
    ]
    
    buyer_attrs_data = []
    for i, order_id in enumerate(order_ids):
        locale_info = locales[i % len(locales)]
        buyer_attrs_data.append({
            'amazon_order_id': order_id,
            'locale': locale_info["locale"],
            'country_code': locale_info["country"],
            'language_code': locale_info["language"]
        })
    
    # Sample messages data - some orders already have sent messages
    messages_data = [
        {
            'amazon_order_id': order_ids[0],
            'message_type': 'confirmDeliveryDetails',
            'subject': 'Delivery Confirmation Required',
            'body': 'Hello! We need to confirm your delivery details for your recent order. Please verify that the delivery address is correct and let us know of any special delivery instructions.',
            'status': 'sent',
            'sent_at': datetime(2024, 12, 15, 10, 30, 0)
        },
        {
            'amazon_order_id': order_ids[1],
            'message_type': 'confirmCustomizationDetails',
            'subject': 'Product Customization Confirmation',
            'body': 'Thank you for your order! We need to confirm the customization details for your personalized item. Please verify the text, color, and size options you selected.',
            'status': 'delivered',
            'sent_at': datetime(2024, 12, 16, 14, 15, 0)
        },
        {
            'amazon_order_id': order_ids[2],
            'message_type': 'warranty',
            'subject': 'Warranty Information for Your Purchase',
            'body': 'Your recent purchase includes a comprehensive warranty. Please find attached the warranty terms and information on how to register your product for coverage.',
            'status': 'sent',
            'sent_at': datetime(2024, 12, 17, 9, 45, 0)
        },
        {
            'amazon_order_id': order_ids[3],
            'message_type': 'legalDisclosure',
            'subject': 'Important Legal Disclosure',
            'body': 'As required by law, we are providing you with important legal disclosures regarding your purchase. Please review the attached documentation carefully.',
            'status': 'sent',
            'sent_at': datetime(2024, 12, 18, 16, 20, 0)
        },
        {
            'amazon_order_id': order_ids[4],
            'message_type': 'digitalAccessKey',
            'subject': 'Your Digital Access Key',
            'body': 'Thank you for purchasing our digital product! Your access key is: DAK-2024-XYZ123-ABC789. Please follow the included instructions to activate your software.',
            'status': 'delivered',
            'sent_at': datetime(2024, 12, 19, 11, 10, 0)
        },
        {
            'amazon_order_id': order_ids[5],
            'message_type': 'unexpectedProblem',
            'subject': 'Important Update Regarding Your Order',
            'body': 'We encountered an unexpected issue with your order that may cause a slight delay in processing. We are working to resolve this quickly and will update you as soon as possible.',
            'status': 'sent',
            'sent_at': datetime(2024, 12, 20, 13, 30, 0)
        }
    ]
    
    # Insert data
    op.bulk_insert(messaging_actions_table, actions_data)
    op.bulk_insert(buyer_attributes_table, buyer_attrs_data)
    op.bulk_insert(messages_table, messages_data)
    
    print(f"Inserted {len(actions_data)} messaging actions")
    print(f"Inserted {len(buyer_attrs_data)} buyer attributes")
    print(f"Inserted {len(messages_data)} messages")


def downgrade():
    # Delete all messaging data
    op.execute("DELETE FROM messages")
    op.execute("DELETE FROM buyer_attributes")
    op.execute("DELETE FROM messaging_actions")