# Customer Notification Strategy for VoiceERP

This document outlines the key events and touchpoints in the VoiceERP system where customers should receive notifications (via Email, SMS, or Push Notification). Notifications are categorized by module.


## 2. Quotations Module
Notifications related to pricing quotes provided to the customer.

*   **New Quotation Created:** Sent when a sales rep generates a quote for a customer. Includes a link or PDF attachment of the quotation.
*   **Quotation Updated/Revised:** Sent if changes are made to an existing open quotation.
*   **Quotation Expiry Reminder:** (Optional) Sent a few days before a quotation's validity period expires.
*   **Quotation Accepted/Rejected Confirmation:** Sent to acknowledge that the customer's decision has been recorded in the system.

## 3. Payments & Invoicing Module
Financial notifications to ensure timely payments and acknowledge receipts.

*   **Invoice Generated:** Sent when an invoice is finalized. Should include the invoice PDF, total amount due, due date, and payment instructions/links.
*   **Payment Received (Receipt):** Sent immediately after a customer makes a payment. Acts as a digital receipt acknowledging the paid amount and updating the current balance.
*   **Payment Overdue Reminder (Collection Reminder):** Automated reminders sent when an invoice passes its due date (e.g., 1 day overdue, 7 days overdue, 30 days overdue).
*   **Promise-to-Pay Confirmation:** If the collection module handles deferred payments, a confirmation of the agreed-upon payment date.
*   **Credit Note Issued:** Sent when a credit note is applied to the customer's account (e.g., due to overpayment or a returned item).

## 4. Parties / Account Management Module
General account and security notifications.

*   **Account Created (Welcome Email):** Sent when a new customer profile is created in the system. Includes login credentials or account setup instructions if there is a customer portal.
*   **Profile/Information Updated:** Sent if critical contact or billing information is changed to prevent fraud.
*   **Account Statement:** A periodic (e.g., monthly) summary of all transactions, invoices, and the current outstanding balance.

## 5. Items & Batch Management Module
Notifications regarding inventory, product availability, and batch expirations.

*   **Low Stock / Out of Stock Alert (Internal/Supplier):** Notifies relevant staff or suppliers when a batch of a specific item is running low or completely out of stock.
*   **Backorder Notification (Customer):** Sent to a customer if an item they ordered is currently out of stock, including an estimated restock date.
*   **Batch Expiry Warning (Internal):** Notifies staff when a specific product batch is approaching its expiration date (e.g., 30 days before expiry) to prevent unsellable inventory.
*   **Expired Batch Alert (Internal):** Alerts staff that a product batch has expired and must be removed from active inventory.

## Standard Notification Content Structure
Every notification should ideally contain:
1.  **Clear Subject Line/Title:** (e.g., "Invoice #INV-1024 from VoiceERP")
2.  **Personalized Greeting:** (e.g., "Dear [Customer Name],")
3.  **The Core Message:** Clear, concise statement of what happened.
4.  **Call to Action (CTA):** What the customer needs to do (e.g., "Pay Now", "View Order", "Download PDF").
5.  **Support Contact:** How they can reach out if they have questions.

## Notification Channels
Depending on the urgency and system configuration, notifications can be routed through:
*   **Email:** Best for invoices, quotations, statements, and detailed receipts (using the existing `mail` module).
*   **SMS/Text:** Best for urgent updates, short payment reminders, or delivery updates.
*   **In-App/Push (if applicable):** If customers have access to a client portal or mobile app.
