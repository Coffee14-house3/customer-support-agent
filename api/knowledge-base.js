// server/embeddedData.ts
var KNOWLEDGE_BASE_DATA = [
  {
    "kb_id": "KB-PASSWORD_RESET",
    "intent": "password_reset",
    "category": "Account Security",
    "title": "Password Reset",
    "policy_summary": "Passwords can be reset using the 'Forgot Password' link on the sign-in screen. A reset link valid for 1 hour will be emailed to the registered address.",
    "resolution_procedure": "Direct customer to click 'Forgot Password' on the login screen, enter their registered email, and use the security link within 60 minutes to create a new password.",
    "example_queries": [
      "I forgot my password and cannot log in",
      "Change my security password",
      "How long is the password reset link valid?",
      "Reset credentials for user john@example.com",
      "Can I reset password via SMS instead of email?"
    ]
  },
  {
    "kb_id": "KB-ACCOUNT_ACCESS",
    "intent": "account_access",
    "category": "Account Management",
    "title": "Account Access",
    "policy_summary": "Accounts locked due to multiple failed logins unlock automatically after 30 minutes, or can be unlocked via two-factor authentication (2FA) verification.",
    "resolution_procedure": "Verify customer identity via 2FA security code, check account lock flags, and reset session tokens if necessary.",
    "example_queries": [
      "Two-factor authentication code is not being sent to my phone",
      "Can someone assist with locked portal access?",
      "Account recovery without 2FA device",
      "Can't access my account dashboard",
      "Help unlocking my registered user account"
    ]
  },
  {
    "kb_id": "KB-BILLING_INQUIRY",
    "intent": "billing_inquiry",
    "category": "Billing & Payments",
    "title": "Billing Inquiry",
    "policy_summary": "Accepted payment methods include Visa, MasterCard, American Express, PayPal, and Apple Pay. Invoices are accessible anytime under Account > Billing.",
    "resolution_procedure": "Guide the customer to Account > Billing to download PDF tax receipts and review itemized invoice breakdowns.",
    "example_queries": [
      "Explain this mystery charge on invoice #9921",
      "I see an unknown charge from your company on my credit card statement",
      "How do I update billing address on file?",
      "What payment methods do you accept on your platform?",
      "How do I download a PDF receipt for tax expenses?"
    ]
  },
  {
    "kb_id": "KB-RETURN_EXCHANGE",
    "intent": "return_exchange",
    "category": "Returns & Replacements",
    "title": "Return Exchange",
    "policy_summary": "Items can be returned or exchanged within 30 days of delivery in original packaging. Return shipping is free with our prepaid printable label.",
    "resolution_procedure": "Generate a prepaid return shipping label, guide customer to attach it to the original package, and bring it to any authorized postal drop-off location within 30 days.",
    "example_queries": [
      "My product arrived broken, how do I return it?",
      "Can I exchange without the receipt?",
      "What is the return address for packages?",
      "Can I change something?",
      "How do I return an item I bought?"
    ]
  },
  {
    "kb_id": "KB-ORDER_TRACKING",
    "intent": "order_tracking",
    "category": "Orders & Shipping",
    "title": "Order Tracking",
    "policy_summary": "Orders can be tracked via the tracking link sent in the confirmation email or under Account > Order History. Standard domestic shipping takes 3-5 business days.",
    "resolution_procedure": "Advise customer to check their confirmation email for the courier tracking number, or log into Account > Orders to view real-time transit status.",
    "example_queries": [
      "Can I track my shipment package #88219?",
      "I need an update on my package shipping status",
      "When will my order be delivered?",
      "When should I expect my delivery to arrive?",
      "Is there a tracking number for my order?"
    ]
  },
  {
    "kb_id": "KB-REFUND_REQUEST",
    "intent": "refund_request",
    "category": "Billing & Refunds",
    "title": "Refund Request",
    "policy_summary": "Refunds are processed within 5-7 business days back to the original payment method after an item is returned or order cancelled. Expedited processing is not available.",
    "resolution_procedure": "Verify the order status, initiate the refund request in the billing system, and inform the customer it takes 5-7 business days to reflect on their bank statement.",
    "example_queries": [
      "I demand a refund for defective item",
      "How long do refunds take to process?",
      "Can I get my money back?",
      "I want a full refund for my order",
      "How do I get my money back for a returned product?"
    ]
  },
  {
    "kb_id": "KB-SHIPPING_DELAY",
    "intent": "shipping_delay",
    "category": "Orders & Shipping",
    "title": "Shipping Delay",
    "policy_summary": "Express shipping takes 1-2 business days. If shipping is delayed beyond 5 business days, customers receive a $10 shipping credit or free expedited reshipment.",
    "resolution_procedure": "Check carrier delay status, apply $10 shipping delay courtesy credit, and offer free expedited reshipment if package is deemed lost in transit.",
    "example_queries": [
      "Delivery date keeps getting pushed back",
      "Do you compensate for late express delivery?",
      "Overnight shipping didn't arrive overnight",
      "Why is my delivery taking so long to arrive?",
      "My package is severely delayed, what compensation do I get?"
    ]
  },
  {
    "kb_id": "KB-PRODUCT_INQUIRY",
    "intent": "product_inquiry",
    "category": "Products & Specifications",
    "title": "Product Inquiry",
    "policy_summary": "All hardware devices include a 1-year limited warranty against manufacturer defects. Product user manuals and compatibility matrices are available in the Help Center.",
    "resolution_procedure": "Consult the official product specifications, confirm compatibility requirements, and refer customer to user manual documentation.",
    "example_queries": [
      "Is the wireless model compatible with Mac and Windows?",
      "How do I register my product warranty?",
      "Will this gadget work with 220V European power outlets?",
      "Dimensions and weight specifications for the desk stand?",
      "Does the product include a charging cable in the box?"
    ]
  },
  {
    "kb_id": "KB-TECHNICAL_SUPPORT",
    "intent": "technical_support",
    "category": "Technical Issues",
    "title": "Technical Support",
    "policy_summary": "Clear browser cache and cookies, disable ad-blockers, or try an incognito window if experiencing web portal errors. We support Chrome, Safari, Firefox, and Edge.",
    "resolution_procedure": "Provide standard troubleshooting steps: hard refresh (Ctrl+F5), clear cookies/cache, try alternate browser, or check service status dashboard.",
    "example_queries": [
      "The website is not loading properly on Safari",
      "it does not work",
      "Browser error during file upload",
      "Why is the checkout page spinning endlessly?",
      "Mobile app crashes every time I tap the cart icon"
    ]
  },
  {
    "kb_id": "KB-SUBSCRIPTION_CANCELLATION",
    "intent": "subscription_cancellation",
    "category": "Subscriptions",
    "title": "Subscription Cancellation",
    "policy_summary": "Subscriptions can be cancelled anytime under Account > Subscriptions. Benefits remain active until the end of the current paid billing cycle with no cancellation penalties.",
    "resolution_procedure": "Instruct customer to navigate to Account > Subscriptions > Manage Subscription > Cancel Subscription, confirming access continues until cycle ends.",
    "example_queries": [
      "Does cancelling give me a prorated refund?",
      "Opt out of subscription renewal",
      "Turn off recurring billing please",
      "I do not want to renew next month",
      "Can I pause my subscription instead of cancelling?"
    ]
  }
];

// api/knowledge-base.ts
function handler(req, res) {
  res.setHeader("Content-Type", "application/json");
  return res.status(200).json(KNOWLEDGE_BASE_DATA);
}
export {
  handler as default
};
