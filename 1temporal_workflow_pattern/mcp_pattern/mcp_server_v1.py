# -------------------------------
# fastmcp_customer_onboarding_server.py
# -------------------------------

import sqlite3
from datetime import datetime
from fastmcp import FastMCP

# -------------------------------
# Initialize MCP Server
# -------------------------------
mcp = FastMCP("Enterprise Customer Onboarding MCP")

# -------------------------------
# Setup SQLite database
# -------------------------------
conn = sqlite3.connect("enterprise_onboarding.db", check_same_thread=False)
cursor = conn.cursor()

# Create customers table
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    email TEXT,
    verified INTEGER DEFAULT 0,
    account_manager TEXT,
    erp_initialized INTEGER DEFAULT 0,
    created_at TEXT
)
""")
conn.commit()
print("✅ Database initialized")

# -------------------------------
# Helper: Fetch full customer record
# -------------------------------
def fetch_customer(customer_id: str):
    cursor.execute("""
        SELECT customer_id, email, verified, account_manager, erp_initialized, created_at
        FROM customers WHERE customer_id=?
    """, (customer_id,))
    row = cursor.fetchone()
    if not row:
        return None
    return {
        "customer_id": row[0],
        "email": row[1],
        "verified": bool(row[2]),
        "account_manager": row[3],
        "erp_initialized": bool(row[4]),
        "created_at": row[5],
    }

# -------------------------------
# Create Customer
# -------------------------------
@mcp.tool()
def create_customer(customer_id: str, email: str):
    print(f"[MCP] create_customer called for {customer_id}")
    cursor.execute("""
        INSERT OR REPLACE INTO customers 
        (customer_id, email, created_at)
        VALUES (?, ?, ?)
    """, (customer_id, email, datetime.utcnow().isoformat()))
    conn.commit()
    return {
        "status": "SUCCESS",
        "operation": "create_customer",
        "customer": fetch_customer(customer_id)
    }

# -------------------------------
# Verify Identity
# -------------------------------
@mcp.tool()
def verify_identity(customer_id: str):
    print(f"[MCP] verify_identity called for {customer_id}")
    cursor.execute("UPDATE customers SET verified=1 WHERE customer_id=?", (customer_id,))
    conn.commit()
    return {
        "status": "SUCCESS",
        "operation": "verify_identity",
        "customer": fetch_customer(customer_id)
    }

# -------------------------------
# Assign Account Manager
# -------------------------------
@mcp.tool()
def assign_account_manager(customer_id: str, manager_name: str):
    print(f"[MCP] assign_account_manager called for {customer_id}")
    cursor.execute("UPDATE customers SET account_manager=? WHERE customer_id=?", (manager_name, customer_id))
    conn.commit()
    return {
        "status": "SUCCESS",
        "operation": "assign_account_manager",
        "customer": fetch_customer(customer_id)
    }

# -------------------------------
# Initialize ERP Account
# -------------------------------
@mcp.tool()
def initialize_erp_account(customer_id: str):
    print(f"[MCP] initialize_erp_account called for {customer_id}")
    cursor.execute("UPDATE customers SET erp_initialized=1 WHERE customer_id=?", (customer_id,))
    conn.commit()
    return {
        "status": "SUCCESS",
        "operation": "initialize_erp_account",
        "customer": fetch_customer(customer_id)
    }

# -------------------------------
# Notify Customer
# -------------------------------
@mcp.tool()
def notify_customer(customer_id: str, message: str):
    print(f"[MCP] notify_customer called for {customer_id}")
    print(f"[CRM] Sending message: {message}")
    return {
        "status": "SUCCESS",
        "operation": "notify_customer",
        "customer": fetch_customer(customer_id),
        "message_sent": True
    }

# -------------------------------
# Get Customer
# -------------------------------
@mcp.tool()
def get_customer(customer_id: str):
    print(f"[MCP] get_customer called for {customer_id}")
    return {
        "status": "SUCCESS",
        "operation": "get_customer",
        "customer": fetch_customer(customer_id)
    }

# -------------------------------
# Run MCP Server
# -------------------------------
if __name__ == "__main__":
    print("🚀 Running Enterprise Customer Onboarding MCP on http://0.0.0.0:8080/mcp")
    # Just use default transport (HTTP) without host/port arguments
    mcp.run()