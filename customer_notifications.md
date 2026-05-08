# HelloKhata ERP — Notification Requirements
## হ্যালো খাতা — নোটিফিকেশন প্রয়োজনীয়তা

**Version:** 1.0  
**Date:** May 2026  
**Purpose:** Define all events, triggers, and channels where notifications are needed across all modules

---

## Table of Contents

1. [Notification Channels](#1-notification-channels)
2. [Authentication & User](#2-authentication--user)
3. [Sales Module](#3-sales-module)
4. [Purchase Module](#4-purchase-module)
5. [Inventory & Stock](#5-inventory--stock)
6. [Batch & Expiry](#6-batch--expiry)
7. [Payments & Collections](#7-payments--collections)
8. [Credit Control](#8-credit-control)
9. [Quotations](#9-quotations)
10. [Returns Management](#10-returns-management)
11. [Expenses](#11-expenses)
12. [Accounts & Cash](#12-accounts--cash)
13. [Subscription & Billing](#13-subscription--billing)
14. [Staff & Role Management](#14-staff--role-management)
15. [System & Audit](#15-system--audit)
16. [Support Tickets](#16-support-tickets)
17. [AI & Voice](#17-ai--voice)
18. [Notification Delivery Rules](#18-notification-delivery-rules)
19. [Plan-Based Access](#19-plan-based-access)
20. [Notification Data Model](#20-notification-data-model)

---

## 1. Notification Channels

| Channel | Status | Use Case |
|---------|--------|----------|
| **In-App (Push)** | ✅ Required | All real-time alerts inside the mobile/web app |
| **SMS** | ✅ Required | OTP, payment reminders, overdue alerts to customers |
| **WhatsApp** | ✅ Required | Invoice sharing, payment reminders, due alerts |
| **Email** | 🔜 Planned | Reports, subscription receipts, password reset |
| **Push Notification (FCM)** | ✅ Required | Background alerts, low stock, expiry, credit overdue |

---

## 2. Authentication & User

### 2.1 OTP Verification
| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| OTP Sent | `POST /api/auth/send-otp` | User (phone owner) | SMS | 🔴 Critical |
| OTP Verified / Login Success | Successful OTP match | User | In-App | 🟡 Medium |
| Login from New Device | JWT issued on unknown device | User | SMS + In-App | 🔴 Critical |
| Password Changed | `PATCH /api/user/password` | User | SMS + In-App | 🔴 Critical |
| Password Reset | `POST /api/v1/auth/reset-password` | User | SMS | 🔴 Critical |
| Session Expired | JWT refresh fails | User | In-App | 🟡 Medium |

### 2.2 Profile Updates
| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| Profile Updated | `PATCH /api/user` | User | In-App | 🟢 Low |
| Phone Number Changed | Phone field updated | User | SMS (old & new) | 🔴 Critical |

---

## 3. Sales Module

### 3.1 Sale Created
| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| Sale Completed (Cash) | `POST /api/sales` with paid=full | Business Owner / Staff | In-App | 🟡 Medium |
| Sale on Credit Created | Sale with due amount > 0 | Business Owner | In-App | 🟠 High |
| Invoice Generated | Sale confirmed | Customer (optional) | WhatsApp / SMS | 🟡 Medium |
| Credit Limit Exceeded During Sale | `POST /api/credit/check-limit` breached | Business Owner | In-App | 🔴 Critical |
| Stock Near Zero After Sale | Stock falls to min threshold | Business Owner / Manager | In-App + Push | 🟠 High |

### 3.2 Sales Return
| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| Return Initiated | `POST /api/sales/returns` | Business Owner | In-App | 🟡 Medium |
| Refund Processed (Cash/bKash) | Return with refund_method=cash/bKash | Customer | SMS / WhatsApp | 🟡 Medium |
| Credit Note Issued | Return with refund_method=credit_note | Customer | WhatsApp / SMS | 🟡 Medium |

### 3.3 Quotation (Sales Flow)
| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| Quotation Sent to Customer | Status → sent | Customer | WhatsApp / SMS | 🟡 Medium |
| Quotation Accepted | Status → accepted | Business Owner / Staff | In-App | 🟡 Medium |
| Quotation Rejected | Status → rejected | Business Owner | In-App | 🟡 Medium |
| Quotation Expiring Soon | Validity date within 1–2 days | Business Owner | In-App + Push | 🟠 High |
| Quotation Converted to Sale | Status → converted | Business Owner | In-App | 🟢 Low |

---

## 4. Purchase Module

### 4.1 Purchase Entry
| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| Purchase Recorded | `POST /api/purchases` | Business Owner | In-App | 🟢 Low |
| Purchase on Credit | Due amount > 0 | Business Owner | In-App | 🟡 Medium |
| Stock Updated After Purchase | Automatic stock addition | Manager | In-App | 🟢 Low |

### 4.2 Purchase Orders
| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| PO Created | `POST /api/purchase-orders` | Business Owner | In-App | 🟢 Low |
| PO Approved | Status → approved | Purchaser / Manager | In-App | 🟡 Medium |
| PO Partially Received | Status → partial | Business Owner | In-App | 🟡 Medium |
| PO Fully Received | Status → received | Business Owner | In-App | 🟡 Medium |
| Expected Delivery Date Passed | PO delivery date < today, status != received | Business Owner | In-App + Push | 🟠 High |

### 4.3 Purchase Returns
| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| Return to Supplier Created | `POST /api/purchases/returns` | Business Owner | In-App | 🟡 Medium |
| Debit Note Issued to Supplier | Return with debit_note method | Business Owner | In-App | 🟡 Medium |

---

## 5. Inventory & Stock

### 5.1 Low Stock Alerts
| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| Stock Falls Below Minimum | Any sale/adjustment reduces stock ≤ minStock | Business Owner / Manager | In-App + Push | 🔴 Critical |
| Stock Reaches Zero | Stock = 0 after deduction | Business Owner | In-App + Push | 🔴 Critical |
| Dead Stock Detected | Item not sold for X days (configurable) | Business Owner | In-App (Daily Digest) | 🟠 High |

### 5.2 Stock Adjustment
| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| Manual Stock Adjusted | `POST /api/inventory/adjustment` | Business Owner | In-App | 🟡 Medium |
| Stock Reduced (Damage/Loss) | Adjustment reason: damaged, lost, expired | Business Owner | In-App | 🟠 High |

### 5.3 Inter-Branch Stock Transfer
| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| Transfer Initiated | `POST /api/inventory/transfer` | Source Branch Manager | In-App | 🟡 Medium |
| Transfer Received | Stock updated at destination | Destination Branch Manager | In-App | 🟡 Medium |

---

## 6. Batch & Expiry

### 6.1 Expiry Alerts
| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| Batch Expiring — Critical | Days until expiry ≤ 7 | Business Owner | In-App + Push | 🔴 Critical |
| Batch Expiring — Warning | Days until expiry ≤ 30 | Business Owner | In-App | 🟠 High |
| Batch Expired | Expiry date passed, stock > 0 | Business Owner | In-App + Push | 🔴 Critical |
| Batch Depleted | Batch quantity = 0 | Manager | In-App | 🟢 Low |

> **Scheduling:** Run a daily cron job at 8:00 AM to check `GET /api/batches/expiry-alerts` and dispatch notifications accordingly.

---

## 7. Payments & Collections

### 7.1 Customer Payments
| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| Payment Received from Customer | `POST /api/payments` (type=received) | Business Owner | In-App | 🟡 Medium |
| Payment Receipt Sent | Payment confirmed | Customer | WhatsApp / SMS | 🟡 Medium |
| Partial Payment Recorded | Payment < outstanding due | Business Owner | In-App | 🟡 Medium |

### 7.2 Supplier Payments
| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| Payment Made to Supplier | `POST /api/supplier-payments` | Business Owner | In-App | 🟢 Low |
| Supplier Due Reminder | Supplier balance overdue | Business Owner | In-App (Daily) | 🟠 High |

### 7.3 Installment / Payment Plans
| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| Installment Due Today | Installment due_date = today | Business Owner | In-App + Push | 🟠 High |
| Installment Overdue | Installment due_date < today, not paid | Business Owner | In-App + Push | 🔴 Critical |
| Installment Due Reminder — Customer | 1 day before due date | Customer | SMS / WhatsApp | 🟠 High |
| Installment Paid | Installment marked as paid | Business Owner | In-App | 🟢 Low |

---

## 8. Credit Control

### 8.1 Credit Limit Alerts
| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| Credit Limit Approaching (80%) | Party's outstanding ≥ 80% of credit limit | Business Owner | In-App | 🟠 High |
| Credit Limit Exceeded | Party's outstanding > credit limit | Business Owner | In-App + Push | 🔴 Critical |
| Credit Overdue — 30 Days | Party balance overdue > 30 days | Business Owner | In-App | 🟠 High |
| Credit Overdue — 60 Days | Party balance overdue > 60 days | Business Owner | In-App + Push | 🔴 Critical |
| Credit Overdue — 90+ Days | Party balance overdue > 90 days | Business Owner | In-App + Push + SMS | 🔴 Critical |

### 8.2 Customer Payment Reminders
| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| Due Reminder (3 Days Before) | Party due date - 3 days | Customer | SMS / WhatsApp | 🟠 High |
| Due Reminder (Due Date) | Party due date = today | Customer | SMS / WhatsApp | 🔴 Critical |
| Overdue Reminder | Due date passed, balance > 0 | Customer | SMS / WhatsApp | 🔴 Critical |

---

## 9. Quotations

| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| New Quotation Created | `POST /api/quotations` | Business Owner | In-App | 🟢 Low |
| Quotation Sent | Status → sent | Customer | WhatsApp / SMS | 🟡 Medium |
| Quotation Expires in 1 Day | validity_date - 1 = today | Business Owner | In-App + Push | 🟠 High |
| Quotation Expired | validity_date < today, status != converted | Business Owner | In-App | 🟡 Medium |
| Customer Accepts Quotation | Status → accepted | Business Owner | In-App + Push | 🟠 High |
| Quotation Converted to Invoice | Status → converted | Business Owner | In-App | 🟢 Low |

---

## 10. Returns Management

| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| Sale Return Created | `POST /api/sales/returns` | Business Owner | In-App | 🟡 Medium |
| Purchase Return Created | `POST /api/purchases/returns` | Business Owner | In-App | 🟡 Medium |
| Credit Note Created | `POST /api/credit-notes` | Customer | WhatsApp / SMS | 🟡 Medium |
| Debit Note Created | `POST /api/debit-notes` | Business Owner | In-App | 🟡 Medium |
| Credit Note Applied | `POST /api/credit-notes/[id]/apply` | Business Owner | In-App | 🟢 Low |

---

## 11. Expenses

| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| Large Expense Recorded | Expense amount > configurable threshold | Business Owner | In-App | 🟠 High |
| Monthly Expense Budget Exceeded | Total expenses > budget (if set) | Business Owner | In-App + Push | 🔴 Critical |
| Recurring Expense Reminder | Scheduled recurring expense due | Business Owner | In-App | 🟡 Medium |

---

## 12. Accounts & Cash

### 12.1 Account Transfers
| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| Fund Transfer Completed | `POST /api/accounts/transfers` | Business Owner | In-App | 🟢 Low |
| Low Account Balance | Account balance < configured threshold | Business Owner | In-App + Push | 🟠 High |

### 12.2 Cash Drawer
| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| Cash Drawer Opened | Session opened | Manager | In-App | 🟢 Low |
| Cash Drawer Closed with Difference | Expected ≠ actual closing balance | Business Owner | In-App | 🟠 High |
| Cash Drawer Not Closed (End of Day) | Session still open at EOD | Business Owner | In-App + Push | 🟠 High |

---

## 13. Subscription & Billing

| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| Subscription Payment Successful | Webhook: bKash / Stripe confirmed | Business Owner | In-App + Email | 🟡 Medium |
| Subscription Payment Failed | Webhook: payment failed | Business Owner | In-App + SMS | 🔴 Critical |
| Subscription Expiring in 7 Days | subscription.end_date - 7 = today | Business Owner | In-App + SMS | 🟠 High |
| Subscription Expired | subscription.end_date < today | Business Owner | In-App + SMS | 🔴 Critical |
| Plan Upgraded | Subscription plan changed to higher tier | Business Owner | In-App | 🟢 Low |
| Plan Downgraded | Subscription plan changed to lower tier | Business Owner | In-App | 🟡 Medium |
| Usage Limit Approaching | e.g. AI chats 90% used | Business Owner | In-App | 🟠 High |
| Usage Limit Reached | e.g. items, staff, branches at max | Business Owner | In-App + Push | 🔴 Critical |

---

## 14. Staff & Role Management

| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| New Staff Added | `POST /api/staff` | New Staff Member | SMS (Welcome) | 🟡 Medium |
| Staff Role Changed | Role updated | Staff Member | In-App | 🟡 Medium |
| Staff Account Deactivated | Staff deleted/deactivated | Business Owner | In-App | 🟡 Medium |
| Staff Logged In | JWT issued for staff | Business Owner (audit) | In-App (silent log) | 🟢 Low |
| Approval Request Created | `POST /api/approvals` | Approver (Owner) | In-App + Push | 🟠 High |
| Approval Granted / Rejected | Approval status updated | Requesting Staff | In-App | 🟡 Medium |

---

## 15. System & Audit

| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| Period Lock Applied | `POST /api/period-locks` | All Staff | In-App | 🟡 Medium |
| Period Lock Removed | Lock deleted | All Staff | In-App | 🟡 Medium |
| Data Export Completed | `GET /api/v1/export` | Requester | In-App + Email | 🟢 Low |
| Bulk Import Completed | `POST /api/items/import` | Requester | In-App | 🟡 Medium |
| Bulk Import Failed | Import with errors | Requester | In-App | 🟠 High |
| Business Health Score Dropped | Score drops by > 10 points | Business Owner | In-App + Push | 🟠 High |

---

## 16. Support Tickets

| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| Ticket Created | `POST /api/support` | Business Owner | In-App | 🟢 Low |
| Ticket Status Updated | Status → in_progress / resolved / closed | Business Owner | In-App | 🟡 Medium |
| New Message on Ticket | `POST /api/support/[id]/message` | Both parties | In-App | 🟡 Medium |
| Ticket Resolved | Status → resolved | Business Owner | In-App + Email | 🟡 Medium |

---

## 17. AI & Voice

| Event | Trigger | Recipient | Channel | Priority |
|-------|---------|-----------|---------|----------|
| AI Daily Brief Ready | Generated each morning | Business Owner | In-App + Push | 🟡 Medium |
| Draft Transaction Awaiting Confirmation | Voice command creates draft | User | In-App | 🟠 High |
| Draft Transaction Expired (5 min) | Draft not confirmed in time | User | In-App | 🟡 Medium |
| AI Chat Daily Limit Reached | Usage hits plan limit | User | In-App | 🟠 High |
| Voice Command Processing Failed | `POST /api/voice` returns error | User | In-App | 🟡 Medium |

---

## 18. Notification Delivery Rules

### 18.1 Timing Rules
| Rule | Detail |
|------|--------|
| **Business Hours Only** | Non-critical SMS/WhatsApp sent between 9 AM – 9 PM |
| **Daily Digest** | Dead stock, aging summaries sent at 8:00 AM daily |
| **Instant** | Critical alerts (OTP, credit overdue, stock=0) sent immediately |
| **Batching** | Multiple low-stock items grouped into single notification |

### 18.2 Deduplication Rules
| Rule | Detail |
|------|--------|
| **Cooldown Period** | Same alert not repeated within 24 hours for same item/party |
| **Escalation** | If ignored for 3 days, escalate channel (e.g. in-app → SMS) |
| **Read Tracking** | Mark notifications as read; suppress repeat for read items |

### 18.3 Recipient Rules
| Role | Receives |
|------|----------|
| **Owner** | All notifications |
| **Manager** | Operations: stock, transfers, cash drawer, returns |
| **Sales Staff** | Sale alerts, quotations, credit warnings during sale |
| **Customer** | Payment receipts, due reminders, invoice, credit note |
| **Supplier** | Purchase return confirmations (via WhatsApp/SMS) |

---

## 19. Plan-Based Access

| Notification Type | FREE | STARTER | GROWTH | INTELLIGENCE |
|-------------------|------|---------|--------|--------------|
| In-App Alerts | ✅ | ✅ | ✅ | ✅ |
| Low Stock Alert | ❌ | ✅ | ✅ | ✅ |
| Expiry Alert | ❌ | ✅ | ✅ | ✅ |
| Dead Stock Alert | ❌ | ✅ | ✅ | ✅ |
| Credit Overdue Alert | ❌ | ✅ | ✅ | ✅ |
| SMS Notifications | ❌ | ❌ | ✅ | ✅ |
| WhatsApp Notifications | ❌ | ❌ | ✅ | ✅ |
| Email Notifications | ❌ | ❌ | ✅ | ✅ |
| Customer Due Reminders | ❌ | ❌ | ✅ | ✅ |
| AI Brief Push | ❌ | ❌ | ✅ | ✅ |
| Custom Notification Rules | ❌ | ❌ | ❌ | ✅ |

---

## 20. Notification Data Model

```prisma
model Notification {
  id           String   @id @default(cuid())
  businessId   String
  branchId     String?
  userId       String?          // internal staff recipient
  partyId      String?          // external customer/supplier recipient
  type         NotificationType
  channel      NotificationChannel
  title        String
  titleBn      String?
  body         String
  bodyBn       String?
  referenceId  String?          // sale ID, item ID, party ID, etc.
  referenceType String?         // "sale" | "item" | "party" | "batch" | ...
  status       NotificationStatus @default(PENDING)
  isRead       Boolean          @default(false)
  sentAt       DateTime?
  readAt       DateTime?
  createdAt    DateTime         @default(now())

  business     Business         @relation(fields: [businessId], references: [id])
}

enum NotificationType {
  LOW_STOCK
  ZERO_STOCK
  DEAD_STOCK
  EXPIRY_WARNING
  EXPIRY_CRITICAL
  BATCH_EXPIRED
  CREDIT_LIMIT_WARNING
  CREDIT_LIMIT_EXCEEDED
  OVERDUE_30
  OVERDUE_60
  OVERDUE_90
  PAYMENT_RECEIVED
  PAYMENT_DUE_REMINDER
  INSTALLMENT_DUE
  INSTALLMENT_OVERDUE
  SALE_CREATED
  PURCHASE_ORDER_OVERDUE
  QUOTATION_EXPIRING
  SUBSCRIPTION_EXPIRING
  SUBSCRIPTION_EXPIRED
  PAYMENT_FAILED
  USAGE_LIMIT
  OTP_SENT
  APPROVAL_REQUEST
  STAFF_ADDED
  AI_BRIEF
  DRAFT_AWAITING
  SUPPORT_UPDATE
  GENERAL
}

enum NotificationChannel {
  IN_APP
  SMS
  WHATSAPP
  EMAIL
  PUSH
}

enum NotificationStatus {
  PENDING
  SENT
  DELIVERED
  FAILED
  READ
}
```

---

## API Endpoints Required

```
POST   /api/v1/notifications/send              — Send notification manually
POST   /api/v1/notifications/send-sms          — Send SMS
POST   /api/v1/notifications/send-whatsapp     — Send WhatsApp
GET    /api/v1/notifications/templates         — List templates
GET    /api/v1/notifications                   — List in-app notifications for user
PATCH  /api/v1/notifications/[id]/read         — Mark as read
PATCH  /api/v1/notifications/read-all          — Mark all as read
DELETE /api/v1/notifications/[id]              — Delete notification
GET    /api/v1/notifications/settings          — Get notification preferences
PATCH  /api/v1/notifications/settings          — Update notification preferences
```

---

## Notification Templates (Examples)

### SMS — Payment Due Reminder
```
প্রিয় {customer_name}, আপনার {business_name}-এ ৳{amount} বকেয়া আছে। 
দয়া করে {due_date} এর মধ্যে পরিশোধ করুন। ধন্যবাদ।
```

### WhatsApp — Invoice
```
🧾 *ইনভয়েস #{invoice_no}*
তারিখ: {date}
পরিমাণ: ৳{amount}
পেমেন্ট: {payment_status}

বিস্তারিত দেখতে: {invoice_link}
— {business_name}
```

### Push — Low Stock
```
Title: ⚠️ কম স্টক সতর্কতা
Body: "{item_name}" এর স্টক {current_stock} {unit}-এ নেমে এসেছে। এখনই রিঅর্ডার করুন।
```

### Push — Subscription Expiring
```
Title: 🔔 সাবস্ক্রিপশন শেষ হচ্ছে
Body: আপনার {plan_name} প্ল্যান {days} দিনে শেষ হবে। রিনিউ করুন।
```

---

*End of Notification Requirements Document*

**Total Notification Events:** 70+  
**Channels Covered:** In-App, SMS, WhatsApp, Email, Push  
**Modules Covered:** All 23 modules
