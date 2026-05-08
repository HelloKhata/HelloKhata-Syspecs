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
| **WhatsApp** | ⚙️ Optional | Invoice sharing, payment reminders, due alerts — user must connect WhatsApp Business API |
| **Email** | 🔜 Planned | Reports, subscription receipts, password reset |
| **Push Notification (FCM)** | ✅ Required | Background alerts, low stock, expiry, credit overdue |

---

## 📋 Quick Reference — Where SMS & Email Are Required

> At-a-glance overview. All other events use In-App / Push only.

### 📱 SMS — Required Events

| # | Event | Recipient | Trigger |
|---|-------|-----------|---------|
| 1 | OTP Sent | User | Login / Register |
| 2 | Login from New Device | User | Unknown device detected |
| 3 | Password Changed | User | `PATCH /api/user/password` |
| 4 | Password Reset | User | `POST /api/v1/auth/reset-password` |
| 5 | Phone Number Changed | User (old & new number) | Phone field updated |
| 6 | Invoice Sent to Customer | Customer | Sale confirmed |
| 7 | Refund Processed | Customer | Return with cash/bKash refund |
| 8 | Credit Note Issued | Customer | Return with credit_note method |
| 9 | Quotation Sent | Customer | Status → sent |
| 10 | Payment Receipt Sent | Customer | Payment confirmed |
| 11 | Installment Due Reminder | Customer | 1 day before due date |
| 12 | Due Reminder — 3 Days Before | Customer | Party due date - 3 days |
| 13 | Due Reminder — Due Today | Customer | Party due date = today |
| 14 | Overdue Reminder | Customer | Due date passed, balance > 0 |
| 15 | Credit Note Created | Customer | `POST /api/credit-notes` |
| 16 | New Staff Welcome | New Staff Member | `POST /api/staff` |
| 17 | Subscription Payment Failed | Business Owner | Webhook: payment failed |
| 18 | Subscription Expiring (7 days) | Business Owner | subscription.end_date - 7 = today |
| 19 | Subscription Expired | Business Owner | subscription.end_date < today |
| 20 | Credit Overdue — 90+ Days | Business Owner | Balance overdue > 90 days |

---

### 📧 Email — Required Events

> Email is **planned** (🔜). Implement after SMS. Use for receipts and reports.

| # | Event | Recipient | Trigger |
|---|-------|-----------|---------|
| 1 | Subscription Payment Successful | Business Owner | Webhook: bKash / Stripe confirmed |
| 2 | Subscription Payment Failed | Business Owner | Webhook: payment failed |
| 3 | Subscription Expiring (7 days) | Business Owner | subscription.end_date - 7 = today |
| 4 | Subscription Expired | Business Owner | subscription.end_date < today |
| 5 | Support Ticket Resolved | Business Owner | Status → resolved |
| 6 | Data Export Completed | Requester | `GET /api/v1/export` |
| 7 | Password Reset Link | User | `POST /api/v1/auth/reset-password` |

---

## 2. Authentication & User

### 2.1 OTP Verification
| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| OTP Sent | `POST /api/auth/send-otp` | User (phone owner) | SMS | 🔴 Critical | 🍞 Toast only |
| OTP Verified / Login Success | Successful OTP match | User | In-App | 🟡 Medium | 🍞 Toast only |
| Login from New Device | JWT issued on unknown device | User | SMS + In-App | 🔴 Critical | 🔔 In-App + Push |
| Password Changed | `PATCH /api/user/password` | User | SMS + In-App | 🔴 Critical | 🍞+🔔 Both |
| Password Reset | `POST /api/v1/auth/reset-password` | User | SMS | 🔴 Critical | 🍞 Toast only |
| Session Expired | JWT refresh fails | User | In-App | 🟡 Medium | 🍞 Toast only |

### 2.2 Profile Updates
| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| Profile Updated | `PATCH /api/user` | User | In-App | 🟢 Low | 🍞 Toast only |
| Phone Number Changed | Phone field updated | User | SMS (old & new) | 🔴 Critical | 🔔 In-App |

---

## 3. Sales Module

### 3.1 Sale Created
| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| Sale Completed (Cash) | `POST /api/sales` with paid=full | Business Owner / Staff | In-App | 🟡 Medium | 🍞 Toast only |
| Sale on Credit Created | Sale with due amount > 0 | Business Owner | In-App | 🟠 High | 🍞+🔔 Both |
| Invoice Generated | Sale confirmed | Customer (optional) | SMS (+ WhatsApp optional) | 🟡 Medium | 🍞 Toast only |
| Credit Limit Exceeded During Sale | `POST /api/credit/check-limit` breached | Business Owner | In-App | 🔴 Critical | 🍞+🔔 Both |
| Stock Near Zero After Sale | Stock falls to min threshold | Business Owner / Manager | In-App + Push | 🟠 High | 🔔 In-App + Push |

### 3.2 Sales Return
| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| Return Initiated | `POST /api/sales/returns` | Business Owner | In-App | 🟡 Medium | 🍞 Toast only |
| Refund Processed (Cash/bKash) | Return with refund_method=cash/bKash | Customer | SMS (+ WhatsApp optional) | 🟡 Medium | 🍞 Toast only |
| Credit Note Issued | Return with refund_method=credit_note | Customer | SMS (+ WhatsApp optional) | 🟡 Medium | 🍞+🔔 Both |

### 3.3 Quotation (Sales Flow)
| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| Quotation Sent to Customer | Status → sent | Customer | SMS (+ WhatsApp optional) | 🟡 Medium | 🍞 Toast only |
| Quotation Accepted | Status → accepted | Business Owner / Staff | In-App + Push | 🟡 Medium | 🔔 In-App + Push |
| Quotation Rejected | Status → rejected | Business Owner | In-App | 🟡 Medium | 🔔 In-App |
| Quotation Expiring Soon | Validity date within 1–2 days | Business Owner | In-App + Push | 🟠 High | 🔔 In-App + Push |
| Quotation Converted to Sale | Status → converted | Business Owner | In-App | 🟢 Low | 🍞 Toast only |

---

## 4. Purchase Module

### 4.1 Purchase Entry
| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| Purchase Recorded | `POST /api/purchases` | Business Owner | In-App | 🟢 Low | 🍞 Toast only |
| Purchase on Credit | Due amount > 0 | Business Owner | In-App | 🟡 Medium | 🍞+🔔 Both |
| Stock Updated After Purchase | Automatic stock addition | Manager | In-App | 🟢 Low | 🍞 Toast only |

### 4.2 Purchase Orders
| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| PO Created | `POST /api/purchase-orders` | Business Owner | In-App | 🟢 Low | 🍞 Toast only |
| PO Approved | Status → approved | Purchaser / Manager | In-App | 🟡 Medium | 🔔 In-App + Push |
| PO Partially Received | Status → partial | Business Owner | In-App | 🟡 Medium | 🔔 In-App |
| PO Fully Received | Status → received | Business Owner | In-App | 🟡 Medium | 🍞+🔔 Both |
| Expected Delivery Date Passed | PO delivery date < today, status != received | Business Owner | In-App + Push | 🟠 High | 🔔 In-App + Push |

### 4.3 Purchase Returns
| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| Return to Supplier Created | `POST /api/purchases/returns` | Business Owner | In-App | 🟡 Medium | 🍞 Toast only |
| Debit Note Issued to Supplier | Return with debit_note method | Business Owner | In-App | 🟡 Medium | 🍞+🔔 Both |

---

## 5. Inventory & Stock

### 5.1 Low Stock Alerts
| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| Stock Falls Below Minimum | Any sale/adjustment reduces stock ≤ minStock | Business Owner / Manager | In-App + Push | 🔴 Critical | 🔔 In-App + Push |
| Stock Reaches Zero | Stock = 0 after deduction | Business Owner | In-App + Push | 🔴 Critical | 🔔 In-App + Push |
| Dead Stock Detected | Item not sold for X days (configurable) | Business Owner | In-App (Daily Digest) | 🟠 High | 🔔 In-App |

### 5.2 Stock Adjustment
| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| Manual Stock Adjusted | `POST /api/inventory/adjustment` | Business Owner | In-App | 🟡 Medium | 🍞 Toast only |
| Stock Reduced (Damage/Loss) | Adjustment reason: damaged, lost, expired | Business Owner | In-App | 🟠 High | 🍞+🔔 Both |

### 5.3 Inter-Branch Stock Transfer
| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| Transfer Initiated | `POST /api/inventory/transfer` | Source Branch Manager | In-App | 🟡 Medium | 🍞 Toast only |
| Transfer Received | Stock updated at destination | Destination Branch Manager | In-App + Push | 🟡 Medium | 🔔 In-App + Push |

---

## 6. Batch & Expiry

### 6.1 Expiry Alerts
| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| Batch Expiring — Critical | Days until expiry ≤ 7 | Business Owner | In-App + Push | 🔴 Critical | 🔔 In-App + Push |
| Batch Expiring — Warning | Days until expiry ≤ 30 | Business Owner | In-App | 🟠 High | 🔔 In-App |
| Batch Expired | Expiry date passed, stock > 0 | Business Owner | In-App + Push | 🔴 Critical | 🔔 In-App + Push |
| Batch Depleted | Batch quantity = 0 | Manager | In-App | 🟢 Low | 🔔 In-App |

> **Scheduling:** Run a daily cron job at 8:00 AM to check `GET /api/batches/expiry-alerts` and dispatch notifications accordingly.

---

## 7. Payments & Collections

### 7.1 Customer Payments
| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| Payment Received from Customer | `POST /api/payments` (type=received) | Business Owner | In-App | 🟡 Medium | 🍞 Toast only |
| Payment Receipt Sent | Payment confirmed | Customer | SMS (+ WhatsApp optional) | 🟡 Medium | 🍞 Toast only |
| Partial Payment Recorded | Payment < outstanding due | Business Owner | In-App | 🟡 Medium | 🍞+🔔 Both |

### 7.2 Supplier Payments
| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| Payment Made to Supplier | `POST /api/supplier-payments` | Business Owner | In-App | 🟢 Low | 🍞 Toast only |
| Supplier Due Reminder | Supplier balance overdue | Business Owner | In-App (Daily) | 🟠 High | 🔔 In-App |

### 7.3 Installment / Payment Plans
| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| Installment Due Today | Installment due_date = today | Business Owner | In-App + Push | 🟠 High | 🔔 In-App + Push |
| Installment Overdue | Installment due_date < today, not paid | Business Owner | In-App + Push | 🔴 Critical | 🔔 In-App + Push |
| Installment Due Reminder — Customer | 1 day before due date | Customer | SMS (+ WhatsApp optional) | 🟠 High | SMS (+ WhatsApp optional) |
| Installment Paid | Installment marked as paid | Business Owner | In-App | 🟢 Low | 🍞 Toast only |

---

## 8. Credit Control

### 8.1 Credit Limit Alerts
| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| Credit Limit Approaching (80%) | Party's outstanding ≥ 80% of credit limit | Business Owner | In-App | 🟠 High | 🍞+🔔 Both |
| Credit Limit Exceeded | Party's outstanding > credit limit | Business Owner | In-App + Push | 🔴 Critical | 🍞+🔔 Both |
| Credit Overdue — 30 Days | Party balance overdue > 30 days | Business Owner | In-App | 🟠 High | 🔔 In-App |
| Credit Overdue — 60 Days | Party balance overdue > 60 days | Business Owner | In-App + Push | 🔴 Critical | 🔔 In-App + Push |
| Credit Overdue — 90+ Days | Party balance overdue > 90 days | Business Owner | In-App + Push + SMS | 🔴 Critical | 🔔 In-App + Push |

### 8.2 Customer Payment Reminders
| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| Due Reminder (3 Days Before) | Party due date - 3 days | Customer | SMS (+ WhatsApp optional) | 🟠 High | SMS (+ WhatsApp optional) |
| Due Reminder (Due Date) | Party due date = today | Customer | SMS (+ WhatsApp optional) | 🔴 Critical | SMS (+ WhatsApp optional) |
| Overdue Reminder | Due date passed, balance > 0 | Customer | SMS (+ WhatsApp optional) | 🔴 Critical | SMS (+ WhatsApp optional) |

---

## 9. Quotations

| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| New Quotation Created | `POST /api/quotations` | Business Owner | In-App | 🟢 Low | 🍞 Toast only |
| Quotation Sent | Status → sent | Customer | SMS (+ WhatsApp optional) | 🟡 Medium | 🍞 Toast only |
| Quotation Expires in 1 Day | validity_date - 1 = today | Business Owner | In-App + Push | 🟠 High | 🔔 In-App + Push |
| Quotation Expired | validity_date < today, status != converted | Business Owner | In-App | 🟡 Medium | 🔔 In-App |
| Customer Accepts Quotation | Status → accepted | Business Owner | In-App + Push | 🟠 High | 🔔 In-App + Push |
| Quotation Converted to Invoice | Status → converted | Business Owner | In-App | 🟢 Low | 🍞 Toast only |

---

## 10. Returns Management

| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| Sale Return Created | `POST /api/sales/returns` | Business Owner | In-App | 🟡 Medium | 🍞 Toast only |
| Purchase Return Created | `POST /api/purchases/returns` | Business Owner | In-App | 🟡 Medium | 🍞 Toast only |
| Credit Note Created | `POST /api/credit-notes` | Customer | SMS (+ WhatsApp optional) | 🟡 Medium | 🍞+🔔 Both |
| Debit Note Created | `POST /api/debit-notes` | Business Owner | In-App | 🟡 Medium | 🍞+🔔 Both |
| Credit Note Applied | `POST /api/credit-notes/[id]/apply` | Business Owner | In-App | 🟢 Low | 🍞 Toast only |

---

## 11. Expenses

| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| Large Expense Recorded | Expense amount > configurable threshold | Business Owner | In-App | 🟠 High | 🍞+🔔 Both |
| Monthly Expense Budget Exceeded | Total expenses > budget (if set) | Business Owner | In-App + Push | 🔴 Critical | 🔔 In-App + Push |
| Recurring Expense Reminder | Scheduled recurring expense due | Business Owner | In-App | 🟡 Medium | 🔔 In-App |

---

## 12. Accounts & Cash

### 12.1 Account Transfers
| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| Fund Transfer Completed | `POST /api/accounts/transfers` | Business Owner | In-App | 🟢 Low | 🍞 Toast only |
| Low Account Balance | Account balance < configured threshold | Business Owner | In-App + Push | 🟠 High | 🔔 In-App + Push |

### 12.2 Cash Drawer
| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| Cash Drawer Opened | Session opened | Manager | In-App | 🟢 Low | 🍞 Toast only |
| Cash Drawer Closed with Difference | Expected ≠ actual closing balance | Business Owner | In-App | 🟠 High | 🔔 In-App |
| Cash Drawer Not Closed (End of Day) | Session still open at EOD | Business Owner | In-App + Push | 🟠 High | 🔔 In-App + Push |

---

## 13. Subscription & Billing

| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| Subscription Payment Successful | Webhook: bKash / Stripe confirmed | Business Owner | In-App + Email | 🟡 Medium | 🔔 In-App |
| Subscription Payment Failed | Webhook: payment failed | Business Owner | In-App + SMS | 🔴 Critical | 🔔 In-App + Push |
| Subscription Expiring in 7 Days | subscription.end_date - 7 = today | Business Owner | In-App + SMS | 🟠 High | 🔔 In-App + Push |
| Subscription Expired | subscription.end_date < today | Business Owner | In-App + SMS | 🔴 Critical | 🔔 In-App + Push |
| Plan Upgraded | Subscription plan changed to higher tier | Business Owner | In-App | 🟢 Low | 🍞+🔔 Both |
| Plan Downgraded | Subscription plan changed to lower tier | Business Owner | In-App | 🟡 Medium | 🔔 In-App |
| Usage Limit Approaching | e.g. AI chats 90% used | Business Owner | In-App | 🟠 High | 🍞+🔔 Both |
| Usage Limit Reached | e.g. items, staff, branches at max | Business Owner | In-App + Push | 🔴 Critical | 🍞+🔔 Both |

---

## 14. Staff & Role Management

| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| New Staff Added | `POST /api/staff` | New Staff Member | SMS (Welcome) | 🟡 Medium | 🍞+🔔 Both |
| Staff Role Changed | Role updated | Staff Member | In-App | 🟡 Medium | 🍞+🔔 Both |
| Staff Account Deactivated | Staff deleted/deactivated | Business Owner | In-App | 🟡 Medium | 🔔 In-App |
| Staff Logged In | JWT issued for staff | Business Owner (audit) | In-App | 🟢 Low | 🔔 In-App (silent log) |
| Approval Request Created | `POST /api/approvals` | Approver (Owner) | In-App + Push | 🟠 High | 🔔 In-App + Push |
| Approval Granted / Rejected | Approval status updated | Requesting Staff | In-App | 🟡 Medium | 🍞+🔔 Both |

---

## 15. System & Audit

| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| Period Lock Applied | `POST /api/period-locks` | All Staff | In-App | 🟡 Medium | 🍞+🔔 Both |
| Period Lock Removed | Lock deleted | All Staff | In-App | 🟡 Medium | 🍞+🔔 Both |
| Data Export Completed | `GET /api/v1/export` | Requester | In-App | 🟢 Low | 🍞 Toast only |
| Bulk Import Completed | `POST /api/items/import` | Requester | In-App | 🟡 Medium | 🍞+🔔 Both |
| Bulk Import Failed | Import with errors | Requester | In-App | 🟠 High | 🔔 In-App |
| Business Health Score Dropped | Score drops by > 10 points | Business Owner | In-App + Push | 🟠 High | 🔔 In-App + Push |

---

## 16. Support Tickets

| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| Ticket Created | `POST /api/support` | Business Owner | In-App | 🟢 Low | 🍞 Toast only |
| Ticket Status Updated | Status → in_progress / resolved / closed | Business Owner | In-App | 🟡 Medium | 🔔 In-App |
| New Message on Ticket | `POST /api/support/[id]/message` | Both parties | In-App + Push | 🟡 Medium | 🔔 In-App + Push |
| Ticket Resolved | Status → resolved | Business Owner | In-App | 🟡 Medium | 🍞+🔔 Both |

---

## 17. AI & Voice

| Event | Trigger | Recipient | Channel | Priority | Delivery |
|-------|---------|-----------|---------|----------|----------|
| AI Daily Brief Ready | Generated each morning | Business Owner | In-App + Push | 🟡 Medium | 🔔 In-App + Push |
| Draft Transaction Awaiting Confirmation | Voice command creates draft | User | In-App | 🟠 High | 🍞+🔔 Both |
| Draft Transaction Expired (5 min) | Draft not confirmed in time | User | In-App | 🟡 Medium | 🍞 Toast only |
| AI Chat Daily Limit Reached | Usage hits plan limit | User | In-App | 🟠 High | 🍞+🔔 Both |
| Voice Command Processing Failed | `POST /api/voice` returns error | User | In-App | 🟡 Medium | 🍞 Toast only |

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
