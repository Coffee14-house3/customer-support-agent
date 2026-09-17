"""
Script to create the raw customer support dataset with realistic variations,
intentional noise, duplicates, and class imbalance for audit testing.
"""
import os
import csv
import random

RAW_DATA_PATH = "data/raw/customer_support_tickets.csv"

# 10 realistic support intents and representative knowledge definitions
INTENT_SPECS = [
    {
        "intent": "order_tracking",
        "category": "Orders & Shipping",
        "policy": "Orders can be tracked via the tracking link sent in the confirmation email or under Account > Order History. Standard domestic shipping takes 3-5 business days.",
        "resolution": "Advise customer to check their confirmation email for the courier tracking number, or log into Account > Orders to view real-time transit status.",
        "queries": [
            "Where is my order right now?",
            "Can I track my shipment package #88219?",
            "How do I check the delivery status of my recent purchase?",
            "My package hasn't arrived yet, where is it?",
            "Can you give me the tracking link for order 49201?",
            "Check status of package order #10492",
            "Where is order #99214 currently located?",
            "Is there a tracking number for my order?",
            "Track my parcel please",
            "How long until my order reaches my address?",
            "When will my order be delivered?",
            "I need an update on my package shipping status",
            "Status of shipment #33910?",
            "Has order #55129 been dispatched yet?",
            "I want to know where my items are right now",
            "Delivery timeline for my pending order?",
            "Courier status for order #77123",
            "Where is my order? Ordered 3 days ago.",
            "Can you check shipping progress for order #66102?",
            "When should I expect my delivery to arrive?"
        ]
    },
    {
        "intent": "refund_request",
        "category": "Billing & Refunds",
        "policy": "Refunds are processed within 5-7 business days back to the original payment method after an item is returned or order cancelled. Expedited processing is not available.",
        "resolution": "Verify the order status, initiate the refund request in the billing system, and inform the customer it takes 5-7 business days to reflect on their bank statement.",
        "queries": [
            "I want a full refund for my order",
            "How do I get my money back for a returned product?",
            "When will my refund appear in my bank account?",
            "Can I get a refund for order #44910?",
            "I was double charged, refund me immediately",
            "How long do refunds take to process?",
            "Refund status for my returned shoes order #12894",
            "I was charged twice on my card, please issue a refund",
            "Can I get my money back?",
            "Refund policy details and turnaround time",
            "Why haven't I received my refund yet?",
            "Cancel my order and give me a refund",
            "I demand a refund for defective item",
            "How does the refund process work?",
            "Has my refund for order #90212 been issued?",
            "Where is the refund money you promised?",
            "Need a refund for cancelled subscription",
            "Please return the money to my credit card",
            "Refund turnaround time question",
            "Will I get a refund to my original card?"
        ]
    },
    {
        "intent": "return_exchange",
        "category": "Returns & Replacements",
        "policy": "Items can be returned or exchanged within 30 days of delivery in original packaging. Return shipping is free with our prepaid printable label.",
        "resolution": "Generate a prepaid return shipping label, guide customer to attach it to the original package, and bring it to any authorized postal drop-off location within 30 days.",
        "queries": [
            "How do I return an item I bought?",
            "Can I exchange this shirt for a larger size?",
            "What is your return window policy?",
            "I received the wrong item and need to exchange it",
            "Where do I download the return shipping label?",
            "How many days do I have to return my purchase?",
            "Can I return an opened box product?",
            "Process an exchange for order #88412",
            "Need to return damaged goods",
            "Is return shipping free or do I pay for it?",
            "How do I send back an unwanted product?",
            "Exchange process for different color sweater",
            "Do you provide a printable return label?",
            "I want to return my order for store credit",
            "Can I drop off my return at a physical store?",
            "Return guidelines for electronics",
            "How to exchange damaged merchandise?",
            "My product arrived broken, how do I return it?",
            "What is the return address for packages?",
            "Can I exchange without the receipt?"
        ]
    },
    {
        "intent": "password_reset",
        "category": "Account Security",
        "policy": "Passwords can be reset using the 'Forgot Password' link on the sign-in screen. A reset link valid for 1 hour will be emailed to the registered address.",
        "resolution": "Direct customer to click 'Forgot Password' on the login screen, enter their registered email, and use the security link within 60 minutes to create a new password.",
        "queries": [
            "How do I reset my password?",
            "I forgot my password and cannot log in",
            "Password reset link is not arriving in my inbox",
            "Can you reset my login password for me?",
            "I'm locked out of my account due to wrong password",
            "Where is the forgot password button?",
            "Need to change my account password",
            "How long is the password reset link valid?",
            "Can't remember my password to sign in",
            "Reset password instructions please",
            "How to update my login credentials?",
            "Password reset token expired, what now?",
            "My password doesn't work anymore",
            "Can I reset password via SMS instead of email?",
            "Steps to recover account password",
            "Help me log in, password forgotten",
            "Change my security password",
            "Forgot password link not working",
            "Reset credentials for user john@example.com",
            "Trouble accessing my profile due to password"
        ]
    },
    {
        "intent": "account_access",
        "category": "Account Management",
        "policy": "Accounts locked due to multiple failed logins unlock automatically after 30 minutes, or can be unlocked via two-factor authentication (2FA) verification.",
        "resolution": "Verify customer identity via 2FA security code, check account lock flags, and reset session tokens if necessary.",
        "queries": [
            "My account is locked out, how do I unlock it?",
            "I am having trouble logging into my profile",
            "Two-factor authentication code is not being sent to my phone",
            "Can't access my account dashboard",
            "Why is my account disabled?",
            "How to update my registered email address?",
            "I lost access to my authenticator app for 2FA",
            "Cannot log in from a new computer",
            "My account says suspended when I sign in",
            "How do I change my primary phone number?",
            "Account verification code not received",
            "Trouble with 2FA sign in",
            "Help unlocking my registered user account",
            "Login page keeps giving an error message",
            "How do I delete or deactivate my account?",
            "Update my profile personal information",
            "Multiple sign-in failures locked my profile",
            "Account recovery without 2FA device",
            "Can someone assist with locked portal access?",
            "Change the name on my customer profile"
        ]
    },
    {
        "intent": "billing_inquiry",
        "category": "Billing & Payments",
        "policy": "Accepted payment methods include Visa, MasterCard, American Express, PayPal, and Apple Pay. Invoices are accessible anytime under Account > Billing.",
        "resolution": "Guide the customer to Account > Billing to download PDF tax receipts and review itemized invoice breakdowns.",
        "queries": [
            "Why was I charged an extra fee on my invoice?",
            "Where can I find and download my monthly invoice receipt?",
            "What payment methods do you accept on your platform?",
            "I see an unknown charge from your company on my credit card statement",
            "Can I update my credit card details for upcoming bills?",
            "Why is there a sales tax charge on my order?",
            "How do I download a PDF receipt for tax expenses?",
            "Do you accept PayPal or Apple Pay?",
            "Explain this mystery charge on invoice #9921",
            "Can I split payment between two cards?",
            "How do I update billing address on file?",
            "Why was my card declined during checkout?",
            "Payment method update instructions",
            "Download invoice for last month's purchase",
            "Where do I enter a promo discount code?",
            "Tax exemption certificate submission",
            "Why did the price increase on my monthly bill?",
            "Can I pay via wire transfer or check?",
            "View past billing statements",
            "Dispute an extra charge on my bill"
        ]
    },
    {
        "intent": "subscription_cancellation",
        "category": "Subscriptions",
        "policy": "Subscriptions can be cancelled anytime under Account > Subscriptions. Benefits remain active until the end of the current paid billing cycle with no cancellation penalties.",
        "resolution": "Instruct customer to navigate to Account > Subscriptions > Manage Subscription > Cancel Subscription, confirming access continues until cycle ends.",
        "queries": [
            "How do I cancel my monthly subscription?",
            "I want to stop my auto-renewing membership",
            "Can I cancel my premium plan immediately?",
            "Stop recurring charges on my account",
            "If I cancel now, do I keep access until the end of the month?",
            "How to terminate my annual subscription?",
            "Cancel subscription for account #4410",
            "I do not want to renew next month",
            "Steps to turn off auto-renewal",
            "Will I be penalized for cancelling early?",
            "Cancel my Pro plan before next billing date",
            "How do I downgrade to the free tier?",
            "Stop charging my credit card every month",
            "Unsubscribe from the paid service",
            "Where is the cancel subscription button?",
            "Can I pause my subscription instead of cancelling?",
            "Does cancelling give me a prorated refund?",
            "I want to end my premium membership",
            "Turn off recurring billing please",
            "Opt out of subscription renewal"
        ]
    },
    {
        "intent": "shipping_delay",
        "category": "Orders & Shipping",
        "policy": "Express shipping takes 1-2 business days. If shipping is delayed beyond 5 business days, customers receive a $10 shipping credit or free expedited reshipment.",
        "resolution": "Check carrier delay status, apply $10 shipping delay courtesy credit, and offer free expedited reshipment if package is deemed lost in transit.",
        "queries": [
            "My package is severely delayed, what compensation do I get?",
            "Why is my delivery taking so long to arrive?",
            "Order was promised by yesterday but hasn't shipped",
            "Do you compensate for late express delivery?",
            "Package stuck in transit for over a week",
            "Late delivery inquiry for order #77123",
            "Why has courier tracking not updated in 4 days?",
            "Can I get a refund on shipping fees because of delay?",
            "My order is 6 days late, what is going on?",
            "Will my delayed order still be delivered today?",
            "Carrier says delivery exception / weather delay",
            "How do I claim the $10 late shipping credit?",
            "Is my package lost or just delayed?",
            "Overnight shipping didn't arrive overnight",
            "Delivery date keeps getting pushed back"
        ]
    },
    {
        "intent": "technical_support",
        "category": "Technical Issues",
        "policy": "Clear browser cache and cookies, disable ad-blockers, or try an incognito window if experiencing web portal errors. We support Chrome, Safari, Firefox, and Edge.",
        "resolution": "Provide standard troubleshooting steps: hard refresh (Ctrl+F5), clear cookies/cache, try alternate browser, or check service status dashboard.",
        "queries": [
            "The website checkout page is freezing when I click pay",
            "I am getting error code 500 when saving my settings",
            "Mobile app crashes every time I tap the cart icon",
            "How do I clear cache and cookies to fix website glitches?",
            "The website is not loading properly on Safari",
            "Button is unclickable on the payment form",
            "Getting continuous network error on the portal",
            "Is your service experiencing an outage right now?",
            "Browser error during file upload",
            "App keeps crashing on Android 14",
            "Troubleshoot error 403 forbidden on dashboard",
            "Blank screen appears after signing in",
            "Why is the checkout page spinning endlessly?",
            "Features not displaying correctly in Firefox"
        ]
    },
    {
        "intent": "product_inquiry",
        "category": "Products & Specifications",
        "policy": "All hardware devices include a 1-year limited warranty against manufacturer defects. Product user manuals and compatibility matrices are available in the Help Center.",
        "resolution": "Consult the official product specifications, confirm compatibility requirements, and refer customer to user manual documentation.",
        "queries": [
            "Does this product come with a manufacturer warranty?",
            "Is the wireless model compatible with Mac and Windows?",
            "Where can I find the user manual and setup guide?",
            "What materials is this item made of?",
            "What is the battery life of the wireless headphones?",
            "Does the product include a charging cable in the box?",
            "Is this item waterproof or water resistant?",
            "Dimensions and weight specifications for the desk stand?",
            "Warranty coverage details for refurbished devices",
            "Will this gadget work with 220V European power outlets?",
            "How do I register my product warranty?",
            "What accessories are included in the packaging?"
        ]
    }
]

# Intentionally noisy / ambiguous records
NOISY_RECORDS = [
    {
        "ticket_id": "TICK-NOISE-001",
        "customer_query": "help",
        "intent": "account_access",
        "category": "Account Management",
        "policy_reference": "Ambiguous one-word request",
        "resolution_steps": "Request clarification from user on specific account or order issue.",
        "sentiment": "neutral",
        "urgency": "low"
    },
    {
        "ticket_id": "TICK-NOISE-002",
        "customer_query": "it does not work",
        "intent": "technical_support",
        "category": "Technical Issues",
        "policy_reference": "Ambiguous complaint without context",
        "resolution_steps": "Ask which feature or device is not working and collect error details.",
        "sentiment": "negative",
        "urgency": "medium"
    },
    {
        "ticket_id": "TICK-NOISE-003",
        "customer_query": "Cancel",
        "intent": "subscription_cancellation",
        "category": "Subscriptions",
        "policy_reference": "Ambiguous: could mean cancel order or cancel subscription",
        "resolution_steps": "Clarify if customer wishes to cancel an active order or an ongoing subscription.",
        "sentiment": "neutral",
        "urgency": "medium"
    },
    {
        "ticket_id": "TICK-NOISE-004",
        "customer_query": "", # Missing / empty query for data pipeline testing
        "intent": "order_tracking",
        "category": "Orders & Shipping",
        "policy_reference": "Corrupted record with missing query",
        "resolution_steps": "Discard or flag for review.",
        "sentiment": "neutral",
        "urgency": "low"
    },
    {
        "ticket_id": "TICK-NOISE-005",
        "customer_query": "   ", # Whitespace only
        "intent": "billing_inquiry",
        "category": "Billing & Payments",
        "policy_reference": "Whitespace query",
        "resolution_steps": "Discard.",
        "sentiment": "neutral",
        "urgency": "low"
    },
    {
        "ticket_id": "TICK-NOISE-006",
        "customer_query": "Can I change something?",
        "intent": "return_exchange",
        "category": "Returns & Replacements",
        "policy_reference": "Vague question lacking subject",
        "resolution_steps": "Ask customer whether they want to modify an order, address, or exchange an item.",
        "sentiment": "neutral",
        "urgency": "low"
    },
    {
        "ticket_id": "TICK-NOISE-007",
        "customer_query": "Where is my order right now?", # Exact duplicate of an order_tracking query
        "intent": "order_tracking",
        "category": "Orders & Shipping",
        "policy_reference": "Orders can be tracked via the tracking link sent in the confirmation email.",
        "resolution_steps": "Advise customer to check tracking link.",
        "sentiment": "neutral",
        "urgency": "medium"
    },
    {
        "ticket_id": "TICK-NOISE-008",
        "customer_query": "where is my order right now???", # Near duplicate with punctuation
        "intent": "order_tracking",
        "category": "Orders & Shipping",
        "policy_reference": "Orders can be tracked via the tracking link sent in the confirmation email.",
        "resolution_steps": "Advise customer to check tracking link.",
        "sentiment": "negative",
        "urgency": "high"
    }
]

def generate_dataset():
    os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)
    rows = []
    ticket_counter = 1000

    sentiments = ["positive", "neutral", "negative"]
    urgencies = ["low", "medium", "high"]

    for spec in INTENT_SPECS:
        intent = spec["intent"]
        category = spec["category"]
        policy = spec["policy"]
        resolution = spec["resolution"]

        for q in spec["queries"]:
            ticket_counter += 1
            rows.append({
                "ticket_id": f"TICK-{ticket_counter}",
                "customer_query": q,
                "intent": intent,
                "category": category,
                "policy_reference": policy,
                "resolution_steps": resolution,
                "sentiment": random.choice(sentiments),
                "urgency": random.choice(urgencies)
            })

    # Add noisy and duplicate records
    rows.extend(NOISY_RECORDS)

    fieldnames = [
        "ticket_id",
        "customer_query",
        "intent",
        "category",
        "policy_reference",
        "resolution_steps",
        "sentiment",
        "urgency"
    ]

    with open(RAW_DATA_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} raw customer support tickets at {RAW_DATA_PATH}")

if __name__ == "__main__":
    generate_dataset()
