# MCP Server for Odoo 17

Model Context Protocol (MCP) Server module สำหรับ Odoo 17 ที่เปิดเผย Odoo models เป็น MCP tools เพื่อให้ AI agents เรียกใช้งานได้ผ่าน HTTP API

## ฟีเจอร์

- **Sale Order CRUD** — search, read, create, write
- **Product CRUD** — search, read, create, write
- **API Key Authentication** — ยืนยันตัวตนผ่าน `X-API-Key` header
- **Usage Tracking** — ติดตามการใช้งาน API key (last used, usage count)
- **Odoo UI** — จัดการ API keys ผ่านเมนู Settings > MCP API Keys

## โครงสร้างโมดูล

```
mcp_server/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── mcp.py              # MCP endpoints
├── models/
│   ├── __init__.py
│   └── mcp_api_key.py      # API key model
├── security/
│   ├── __init__.py
│   └── ir.model.access.csv # Access rights
└── views/
    └── mcp_server_views.xml # API key views & menu
```

## การติดตั้ง

1. คัดลอกโฟลเดอร์ `mcp_server` ไปยัง Odoo addons path
2. Update Apps List ใน Odoo
3. Install module **MCP Server for Odoo**
4. ไปที่ **Settings > MCP API Keys** เพื่อสร้าง API key

```bash
./odoo-bin -u mcp_server -d <database_name>
```

## การใช้งาน

### 1. สร้าง API Key

ไปที่ **Settings > MCP API Keys** กด **New** กรอกชื่อและเลือก User แล้วบันทึก — API key จะถูกสร้างอัตโนมัติ

### 2. ดูรายการ Tools ที่ใช้ได้

```bash
curl -X GET https://your-odoo.com/mcp/tools
```

### 3. เรียกใช้งาน Tools

ทุก request ต้องมี header `X-API-Key`:

```bash
curl -X POST https://your-odoo.com/mcp/call/sale_order_search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "domain": [["state", "=", "sale"]],
    "fields": ["name", "partner_id", "amount_total"],
    "limit": 10
  }'
```

## API Endpoints

### Sale Order

| Endpoint | Method | คำอธิบาย |
|----------|--------|----------|
| `/mcp/call/sale_order_search` | POST | ค้นหา sale orders ด้วย domain filter |
| `/mcp/call/sale_order_read` | POST | อ่าน sale order ตาม ID |
| `/mcp/call/sale_order_create` | POST | สร้าง sale order ใหม่ |
| `/mcp/call/sale_order_write` | POST | แก้ไข sale order ที่มีอยู่ |

### Product

| Endpoint | Method | คำอธิบาย |
|----------|--------|----------|
| `/mcp/call/product_search` | POST | ค้นหา products ด้วย domain filter |
| `/mcp/call/product_read` | POST | อ่าน product ตาม ID |
| `/mcp/call/product_create` | POST | สร้าง product ใหม่ |
| `/mcp/call/product_write` | POST | แก้ไข product ที่มีอยู่ |

## Request / Response Examples

### Search Sale Orders

```json
// Request
POST /mcp/call/sale_order_search
{
  "domain": [["state", "=", "sale"]],
  "fields": ["name", "partner_id", "amount_total"],
  "limit": 5
}

// Response
{
  "success": true,
  "data": [
    {"id": 1, "name": "SO0001", "partner_id": [42, "Customer A"], "amount_total": 15000.0},
    {"id": 2, "name": "SO0002", "partner_id": [43, "Customer B"], "amount_total": 8500.0}
  ]
}
```

### Read a Sale Order

```json
// Request
POST /mcp/call/sale_order_read
{
  "id": 1,
  "fields": ["name", "partner_id", "state", "amount_total", "order_line"]
}

// Response
{
  "success": true,
  "data": {
    "id": 1,
    "name": "SO0001",
    "partner_id": [42, "Customer A"],
    "state": "sale",
    "amount_total": 15000.0,
    "order_line": [10, 11]
  }
}
```

### Create a Sale Order

```json
// Request
POST /mcp/call/sale_order_create
{
  "values": {
    "partner_id": 42,
    "order_line": [
      [0, 0, {"product_id": 1, "product_uom_qty": 2, "price_unit": 500.0}]
    ]
  }
}

// Response
{
  "success": true,
  "data": {"id": 5, "name": "SO0005", "partner_id": [42, "Customer A"], "state": "draft", "amount_total": 1000.0}
}
```

### Search Products

```json
// Request
POST /mcp/call/product_search
{
  "domain": [["type", "=", "consu"]],
  "fields": ["name", "default_code", "list_price", "qty_available"],
  "limit": 5
}

// Response
{
  "success": true,
  "data": [
    {"id": 1, "name": "Product A", "default_code": "PA001", "list_price": 500.0, "qty_available": 100.0}
  ]
}
```

### Create a Product

```json
// Request
POST /mcp/call/product_create
{
  "values": {
    "name": "New Product",
    "default_code": "NP001",
    "type": "consu",
    "list_price": 250.0
  }
}

// Response
{
  "success": true,
  "data": {"id": 25, "name": "New Product", "default_code": "NP001", "list_price": 250.0, "type": "consu"}
}
```

### Update a Product

```json
// Request
POST /mcp/call/product_write
{
  "id": 25,
  "values": {
    "list_price": 300.0
  }
}

// Response
{
  "success": true,
  "data": {"id": 25, "name": "New Product", "default_code": "NP001", "list_price": 300.0, "type": "consu"}
}
```

## Error Responses

| HTTP Status | สาเหตุ |
|-------------|--------|
| `401` | API Key หายหรือไม่ถูกต้อง |
| `400` | Parameter ผิดพลาด หรือ validation error |
| `404` | ไม่พบ record ที่ระบุ |

```json
{
  "success": false,
  "error": "Invalid API Key"
}
```

## Dependencies

- `sale_management`
- `product`
- `stock`

## License

LGPL-3
