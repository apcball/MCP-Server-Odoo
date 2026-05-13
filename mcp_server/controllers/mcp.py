# -*- coding: utf-8 -*-

import json
from odoo import http
from odoo import fields as odoo_fields
from odoo.http import request
from odoo.exceptions import AccessDenied
from odoo.tools.translate import _


class MCPController(http.Controller):
    """MCP Server Controller - Exposes Odoo models as MCP tools"""

    def _verify_api_key(self):
        """Verify API key from request headers and set allowed company context"""
        api_key = request.httprequest.headers.get('X-API-Key')
        if not api_key:
            raise AccessDenied(_('API Key is required'))

        key_record = request.env['mcp.api.key'].sudo().search([
            ('key', '=', api_key),
            ('active', '=', True)
        ], limit=1)

        if not key_record:
            raise AccessDenied(_('Invalid API Key'))

        # Update usage tracking
        key_record.write({
            'last_used': odoo_fields.Datetime.now(),
            'usage_count': key_record.usage_count + 1
        })

        # Set allowed company context — allow all companies the user has access to
        # so operations on records from any company work correctly
        user = key_record.user_id
        allowed_company = key_record.company_id
        if allowed_company:
            user_companies = user.company_ids.ids if user.company_ids else [allowed_company.id]
            request.update_context(
                allowed_company_ids=user_companies,
            )

        return user

    @http.route('/mcp/tools', type='http', auth='public', methods=['GET'], csrf=False)
    def mcp_tools(self, **kwargs):
        """Return available MCP tools"""
        tools = [
            {
                'name': 'sale_order_search',
                'description': 'Search for sale orders with optional filters',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'domain': {
                            'type': 'array',
                            'description': 'Odoo domain filter',
                            'items': {'type': 'array'}
                        },
                        'fields': {
                            'type': 'array',
                            'description': 'Fields to return',
                            'items': {'type': 'string'}
                        },
                        'limit': {
                            'type': 'integer',
                            'description': 'Maximum number of records'
                        }
                    }
                }
            },
            {
                'name': 'sale_order_read',
                'description': 'Read a specific sale order',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'integer',
                            'description': 'Sale order ID'
                        },
                        'fields': {
                            'type': 'array',
                            'description': 'Fields to return',
                            'items': {'type': 'string'}
                        }
                    },
                    'required': ['id']
                }
            },
            {
                'name': 'sale_order_create',
                'description': 'Create a new sale order',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'values': {
                            'type': 'object',
                            'description': 'Field values for the sale order'
                        }
                    },
                    'required': ['values']
                }
            },
            {
                'name': 'sale_order_write',
                'description': 'Update an existing sale order',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'integer',
                            'description': 'Sale order ID'
                        },
                        'values': {
                            'type': 'object',
                            'description': 'Field values to update'
                        }
                    },
                    'required': ['id', 'values']
                }
            },
            {
                'name': 'sale_order_confirm',
                'description': 'Confirm a sale order to move it from draft to sale state (triggers business logic)',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'integer',
                            'description': 'Sale order ID'
                        }
                    },
                    'required': ['id']
                }
            },
            {
                'name': 'sale_order_create_invoice',
                'description': 'Create invoice from a confirmed sale order',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'integer',
                            'description': 'Sale order ID (must be confirmed)'
                        }
                    },
                    'required': ['id']
                }
            },
            {
                'name': 'invoice_confirm',
                'description': 'Post/confirm an invoice (action_post) to post it to accounting',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'integer',
                            'description': 'Invoice (account.move) ID'
                        }
                    },
                    'required': ['id']
                }
            },
            {
                'name': 'product_search',
                'description': 'Search for products with optional filters',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'domain': {
                            'type': 'array',
                            'description': 'Odoo domain filter',
                            'items': {'type': 'array'}
                        },
                        'fields': {
                            'type': 'array',
                            'description': 'Fields to return',
                            'items': {'type': 'string'}
                        },
                        'limit': {
                            'type': 'integer',
                            'description': 'Maximum number of records'
                        }
                    }
                }
            },
            {
                'name': 'product_read',
                'description': 'Read a specific product',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'integer',
                            'description': 'Product ID'
                        },
                        'fields': {
                            'type': 'array',
                            'description': 'Fields to return',
                            'items': {'type': 'string'}
                        }
                    },
                    'required': ['id']
                }
            },
            {
                'name': 'product_create',
                'description': 'Create a new product',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'values': {
                            'type': 'object',
                            'description': 'Field values for the product'
                        }
                    },
                    'required': ['values']
                }
            },
            {
                'name': 'product_write',
                'description': 'Update an existing product',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'integer',
                            'description': 'Product ID'
                        },
                        'values': {
                            'type': 'object',
                            'description': 'Field values to update'
                        }
                    },
                    'required': ['id', 'values']
                }
            },
            {
                'name': 'partner_search',
                'description': 'Search for partners (contacts/customers) with optional filters',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'domain': {
                            'type': 'array',
                            'description': 'Odoo domain filter e.g. [["name","ilike","John"]]',
                            'items': {'type': 'array'}
                        },
                        'fields': {
                            'type': 'array',
                            'description': 'Fields to return',
                            'items': {'type': 'string'}
                        },
                        'limit': {
                            'type': 'integer',
                            'description': 'Maximum number of records'
                        }
                    }
                }
            },
            {
                'name': 'partner_read',
                'description': 'Read a specific partner by ID',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'integer',
                            'description': 'Partner ID'
                        },
                        'fields': {
                            'type': 'array',
                            'description': 'Fields to return',
                            'items': {'type': 'string'}
                        }
                    },
                    'required': ['id']
                }
            },
            {
                'name': 'partner_create',
                'description': 'Create a new partner (contact/customer)',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'values': {
                            'type': 'object',
                            'description': 'Field values. Must include name. Optional: phone, email, mobile, company_id, is_company, vat, street, city'
                        }
                    },
                    'required': ['values']
                }
            },
            {
                'name': 'company_list',
                'description': 'List all active companies in the system',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'fields': {
                            'type': 'array',
                            'description': 'Fields to return',
                            'items': {'type': 'string'}
                        }
                    }
                }
            },
            {
                'name': 'company_search',
                'description': 'Search for companies with optional filters',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'domain': {
                            'type': 'array',
                            'description': 'Odoo domain filter e.g. [["name","ilike","Company"]]',
                            'items': {'type': 'array'}
                        },
                        'fields': {
                            'type': 'array',
                            'description': 'Fields to return',
                            'items': {'type': 'string'}
                        },
                        'limit': {
                            'type': 'integer',
                            'description': 'Maximum number of records'
                        }
                    }
                }
            },
            {
                'name': 'sale_report',
                'description': 'Generate sales report aggregated by salesperson, team, and time period (week/month)',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'date_from': {
                            'type': 'string',
                            'description': 'Start date ISO format e.g. "2025-01-01"'
                        },
                        'date_to': {
                            'type': 'string',
                            'description': 'End date ISO format e.g. "2025-12-31"'
                        },
                        'group_by': {
                            'type': 'string',
                            'description': 'Comma-separated group keys: "salesperson", "team", "week", "month", "product". Default: "month,salesperson"'
                        },
                        'states': {
                            'type': 'array',
                            'description': 'Sale order states to include. Default: ["sale","done"]',
                            'items': {'type': 'string'}
                        },
                        'limit': {
                            'type': 'integer',
                            'description': 'Max rows (default 500)'
                        }
                    }
                }
            },
            {
                'name': 'accounting_audit',
                'description': 'Audit accounting entries for errors: unbalanced moves, date mismatches between move and move lines, stale draft entries, and suspicious amounts',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'date_from': {
                            'type': 'string',
                            'description': 'Start date filter ISO format e.g. "2025-01-01"'
                        },
                        'date_to': {
                            'type': 'string',
                            'description': 'End date filter ISO format e.g. "2025-12-31"'
                        },
                        'checks': {
                            'type': 'array',
                            'description': 'Which checks to run: "unbalanced", "date_mismatch", "stale_draft", "suspicious_amount". Default: all checks.',
                            'items': {'type': 'string'}
                        },
                        'limit': {
                            'type': 'integer',
                            'description': 'Max issues per check (default 100)'
                        }
                    }
                }
            },
            {
                'name': 'gl_report',
                'description': 'General Ledger report with opening balance, movements, and closing balance per account. Supports grouping by account, partner, journal.',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'date_from': {
                            'type': 'string',
                            'description': 'Start date ISO format e.g. "2025-01-01"'
                        },
                        'date_to': {
                            'type': 'string',
                            'description': 'End date ISO format e.g. "2025-12-31"'
                        },
                        'account_codes': {
                            'type': 'array',
                            'description': 'Filter by account codes e.g. ["1100","1200"]. Default: all accounts.',
                            'items': {'type': 'string'}
                        },
                        'group_by': {
                            'type': 'string',
                            'description': 'Group by: "account", "account_partner", "account_journal". Default: "account"'
                        },
                        'limit': {
                            'type': 'integer',
                            'description': 'Max rows (default 500)'
                        }
                    }
                }
            },
            {
                'name': 'gl_variance',
                'description': 'Compare GL balances between two periods or against expected values. Detects unexpected variances in account balances.',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'period1_from': {
                            'type': 'string',
                            'description': 'Period 1 start date e.g. "2025-01-01"'
                        },
                        'period1_to': {
                            'type': 'string',
                            'description': 'Period 1 end date e.g. "2025-03-31"'
                        },
                        'period2_from': {
                            'type': 'string',
                            'description': 'Period 2 start date e.g. "2025-04-01"'
                        },
                        'period2_to': {
                            'type': 'string',
                            'description': 'Period 2 end date e.g. "2025-06-30"'
                        },
                        'variance_threshold': {
                            'type': 'number',
                            'description': 'Minimum absolute variance to report. Default: 0.01'
                        },
                        'account_codes': {
                            'type': 'array',
                            'description': 'Filter by account codes. Default: all.',
                            'items': {'type': 'string'}
                        }
                    }
                }
            },
            {
                'name': 'account_move_search',
                'description': 'Search and read journal entries (account.move) with line details',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'domain': {
                            'type': 'array',
                            'description': 'Odoo domain filter e.g. [["journal_id.type","=","sale"]]',
                            'items': {'type': 'array'}
                        },
                        'fields': {
                            'type': 'array',
                            'description': 'Fields to return',
                            'items': {'type': 'string'}
                        },
                        'with_lines': {
                            'type': 'boolean',
                            'description': 'Include move lines detail (default false)'
                        },
                        'limit': {
                            'type': 'integer',
                            'description': 'Max records (default 80)'
                        }
                    }
                }
            },
        ]

        return request.make_json_response(tools)

    @http.route('/mcp/call/sale_order_search', type='http', auth='public', methods=['POST'], csrf=False)
    def sale_order_search(self, **kwargs):
        """Search for sale orders"""
        try:
            self._verify_api_key()
            data = json.loads(request.httprequest.data)
            domain = data.get('domain', [])
            field_list = data.get('fields', ['name', 'partner_id', 'state', 'amount_total', 'date_order'])
            limit = data.get('limit', 80)

            orders = request.env['sale.order'].sudo().search(domain, limit=limit)
            result = [order.read(field_list)[0] for order in orders]

            return request.make_json_response({
                'success': True,
                'data': result
            })
        except AccessDenied as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=401)
        except Exception as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=400)

    @http.route('/mcp/call/sale_order_read', type='http', auth='public', methods=['POST'], csrf=False)
    def sale_order_read(self, **kwargs):
        """Read a specific sale order"""
        try:
            self._verify_api_key()
            data = json.loads(request.httprequest.data)
            order_id = data.get('id')
            field_list = data.get('fields', ['name', 'partner_id', 'state', 'amount_total', 'date_order', 'order_line'])

            if not order_id:
                return request.make_json_response({
                    'success': False,
                    'error': 'id is required'
                }, status=400)

            order = request.env['sale.order'].sudo().browse(order_id)
            if not order.exists():
                return request.make_json_response({
                    'success': False,
                    'error': 'Sale order not found'
                }, status=404)

            result = order.read(field_list)[0]

            return request.make_json_response({
                'success': True,
                'data': result
            })
        except AccessDenied as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=401)
        except Exception as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=400)

    @http.route('/mcp/call/sale_order_create', type='http', auth='public', methods=['POST'], csrf=False)
    def sale_order_create(self, **kwargs):
        """Create a new sale order"""
        try:
            self._verify_api_key()
            data = json.loads(request.httprequest.data)
            values = data.get('values')

            if not values:
                return request.make_json_response({
                    'success': False,
                    'error': 'values is required'
                }, status=400)

            order = request.env['sale.order'].sudo().create(values)
            result = order.read(['name', 'partner_id', 'state', 'amount_total', 'date_order'])[0]

            return request.make_json_response({
                'success': True,
                'data': result
            })
        except AccessDenied as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=401)
        except Exception as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=400)

    @http.route('/mcp/call/sale_order_write', type='http', auth='public', methods=['POST'], csrf=False)
    def sale_order_write(self, **kwargs):
        """Update an existing sale order"""
        try:
            self._verify_api_key()
            data = json.loads(request.httprequest.data)
            order_id = data.get('id')
            values = data.get('values')

            if not order_id or not values:
                return request.make_json_response({
                    'success': False,
                    'error': 'id and values are required'
                }, status=400)

            order = request.env['sale.order'].sudo().browse(order_id)
            if not order.exists():
                return request.make_json_response({
                    'success': False,
                    'error': 'Sale order not found'
                }, status=404)

            order.write(values)
            result = order.read(['name', 'partner_id', 'state', 'amount_total', 'date_order'])[0]

            return request.make_json_response({
                'success': True,
                'data': result
            })
        except AccessDenied as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=401)
        except Exception as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=400)

    # ─── Sale Order action endpoints ─────────────────────────────

    @http.route('/mcp/call/sale_order_confirm', type='http', auth='public', methods=['POST'], csrf=False)
    def sale_order_confirm(self, **kwargs):
        """Confirm a sale order (action_confirm)"""
        try:
            self._verify_api_key()
            data = json.loads(request.httprequest.data)
            order_id = data.get('id')

            if not order_id:
                return request.make_json_response({
                    'success': False,
                    'error': 'id is required'
                }, status=400)

            order = request.env['sale.order'].sudo().browse(order_id)
            if not order.exists():
                return request.make_json_response({
                    'success': False,
                    'error': 'Sale order not found'
                }, status=404)

            order.action_confirm()
            result = order.read(['name', 'partner_id', 'state', 'amount_total', 'date_order', 'invoice_status'])[0]

            return request.make_json_response({
                'success': True,
                'data': result
            })
        except AccessDenied as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=401)
        except Exception as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=400)

    @http.route('/mcp/call/sale_order_create_invoice', type='http', auth='public', methods=['POST'], csrf=False)
    def sale_order_create_invoice(self, **kwargs):
        """Create invoice from a confirmed sale order (_create_invoices)"""
        try:
            self._verify_api_key()
            data = json.loads(request.httprequest.data)
            order_id = data.get('id')

            if not order_id:
                return request.make_json_response({
                    'success': False,
                    'error': 'id is required'
                }, status=400)

            order = request.env['sale.order'].sudo().browse(order_id)
            if not order.exists():
                return request.make_json_response({
                    'success': False,
                    'error': 'Sale order not found'
                }, status=404)

            # Force company context and ensure invoice date is set
            order = order.with_company(order.company_id.id)
            invoice = order._create_invoices(
                final=data.get('final', True),
                date=data.get('date') or order.date_order.date(),
            )
            result = invoice.read(['name', 'partner_id', 'move_type', 'state', 'amount_total', 'amount_untaxed', 'invoice_date', 'invoice_date_due', 'invoice_origin'])[0]

            return request.make_json_response({
                'success': True,
                'data': result
            })
        except AccessDenied as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=401)
        except Exception as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=400)

    @http.route('/mcp/call/invoice_confirm', type='http', auth='public', methods=['POST'], csrf=False)
    def invoice_confirm(self, **kwargs):
        """Post/confirm an invoice (action_post)"""
        try:
            self._verify_api_key()
            data = json.loads(request.httprequest.data)
            invoice_id = data.get('id')

            if not invoice_id:
                return request.make_json_response({
                    'success': False,
                    'error': 'id is required'
                }, status=400)

            invoice = request.env['account.move'].sudo().browse(invoice_id)
            if not invoice.exists():
                return request.make_json_response({
                    'success': False,
                    'error': 'Invoice not found'
                }, status=404)

            invoice.action_post()
            result = invoice.read(['name', 'partner_id', 'move_type', 'state', 'amount_total', 'invoice_date', 'invoice_origin'])[0]

            return request.make_json_response({
                'success': True,
                'data': result
            })
        except AccessDenied as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=401)
        except Exception as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=400)

    @http.route('/mcp/call/product_search', type='http', auth='public', methods=['POST'], csrf=False)
    def product_search(self, **kwargs):
        """Search for products"""
        try:
            self._verify_api_key()
            data = json.loads(request.httprequest.data)
            domain = data.get('domain', [])
            field_list = data.get('fields', ['name', 'default_code', 'list_price', 'qty_available', 'type'])
            limit = data.get('limit', 80)

            products = request.env['product.product'].sudo().search(domain, limit=limit)
            result = [product.read(field_list)[0] for product in products]

            return request.make_json_response({
                'success': True,
                'data': result
            })
        except AccessDenied as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=401)
        except Exception as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=400)

    @http.route('/mcp/call/product_read', type='http', auth='public', methods=['POST'], csrf=False)
    def product_read(self, **kwargs):
        """Read a specific product"""
        try:
            self._verify_api_key()
            data = json.loads(request.httprequest.data)
            product_id = data.get('id')
            field_list = data.get('fields', ['name', 'default_code', 'list_price', 'qty_available', 'type', 'description_sale'])

            if not product_id:
                return request.make_json_response({
                    'success': False,
                    'error': 'id is required'
                }, status=400)

            product = request.env['product.product'].sudo().browse(product_id)
            if not product.exists():
                return request.make_json_response({
                    'success': False,
                    'error': 'Product not found'
                }, status=404)

            result = product.read(field_list)[0]

            return request.make_json_response({
                'success': True,
                'data': result
            })
        except AccessDenied as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=401)
        except Exception as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=400)

    @http.route('/mcp/call/product_create', type='http', auth='public', methods=['POST'], csrf=False)
    def product_create(self, **kwargs):
        """Create a new product"""
        try:
            self._verify_api_key()
            data = json.loads(request.httprequest.data)
            values = data.get('values')

            if not values:
                return request.make_json_response({
                    'success': False,
                    'error': 'values is required'
                }, status=400)

            product = request.env['product.product'].sudo().create(values)
            result = product.read(['name', 'default_code', 'list_price', 'type'])[0]

            return request.make_json_response({
                'success': True,
                'data': result
            })
        except AccessDenied as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=401)
        except Exception as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=400)

    # ─── Partner endpoints ──────────────────────────────────────

    @http.route('/mcp/call/partner_search', type='http', auth='public', methods=['POST'], csrf=False)
    def partner_search(self, **kwargs):
        """Search for partners (contacts/customers)"""
        try:
            self._verify_api_key()
            data = json.loads(request.httprequest.data)
            domain = data.get('domain', [])
            field_list = data.get('fields', ['name', 'email', 'phone', 'mobile', 'company_id', 'is_company', 'parent_id', 'vat'])
            limit = data.get('limit', 80)

            partners = request.env['res.partner'].sudo().search(domain, limit=limit)
            result = [partner.read(field_list)[0] for partner in partners]

            return request.make_json_response({
                'success': True,
                'data': result
            })
        except AccessDenied as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=401)
        except Exception as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=400)

    @http.route('/mcp/call/partner_read', type='http', auth='public', methods=['POST'], csrf=False)
    def partner_read(self, **kwargs):
        """Read a specific partner by ID"""
        try:
            self._verify_api_key()
            data = json.loads(request.httprequest.data)
            partner_id = data.get('id')
            field_list = data.get('fields', ['name', 'email', 'phone', 'mobile', 'company_id', 'is_company', 'parent_id', 'vat', 'street', 'city', 'zip', 'country_id', 'state_id'])

            if not partner_id:
                return request.make_json_response({
                    'success': False,
                    'error': 'id is required'
                }, status=400)

            partner = request.env['res.partner'].sudo().browse(partner_id)
            if not partner.exists():
                return request.make_json_response({
                    'success': False,
                    'error': 'Partner not found'
                }, status=404)

            result = partner.read(field_list)[0]

            return request.make_json_response({
                'success': True,
                'data': result
            })
        except AccessDenied as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=401)
        except Exception as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=400)

    @http.route('/mcp/call/partner_create', type='http', auth='public', methods=['POST'], csrf=False)
    def partner_create(self, **kwargs):
        """Create a new partner"""
        try:
            self._verify_api_key()
            data = json.loads(request.httprequest.data)
            values = data.get('values')

            if not values or not values.get('name'):
                return request.make_json_response({
                    'success': False,
                    'error': 'values with name is required'
                }, status=400)

            partner = request.env['res.partner'].sudo().create(values)
            result = partner.read(['name', 'email', 'phone', 'mobile', 'company_id', 'is_company', 'vat'])[0]

            return request.make_json_response({
                'success': True,
                'data': result
            })
        except AccessDenied as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=401)
        except Exception as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=400)

    # ─── Sales Report endpoint ──────────────────────────────────

    @http.route('/mcp/call/sale_report', type='http', auth='public', methods=['POST'], csrf=False)
    def sale_report(self, **kwargs):
        """Generate sales report aggregated by salesperson, team, and/or time period.

        Request body:
            date_from (str): ISO date e.g. '2025-01-01' (optional)
            date_to (str): ISO date e.g. '2025-12-31' (optional)
            group_by (str): Comma-separated group keys: 'salesperson', 'team', 'week', 'month', 'product'
                            default: 'month,salesperson'
            states (list): Sale order states to include, default: ['sale','done']
            limit (int): Max rows per group, default 500
        """
        try:
            self._verify_api_key()
            data = json.loads(request.httprequest.data)

            date_from = data.get('date_from')
            date_to = data.get('date_to')
            group_by_raw = data.get('group_by', 'month,salesperson')
            states = data.get('states', ['sale', 'done'])
            limit = data.get('limit', 500)

            # Build domain
            domain = [('state', 'in', states)]
            if date_from:
                domain.append(('date_order', '>=', date_from))
            if date_to:
                domain.append(('date_order', '<=', date_to + ' 23:59:59'))

            orders = request.env['sale.order'].sudo().search(domain, limit=limit)

            if not orders:
                return request.make_json_response({
                    'success': True,
                    'data': [],
                    'summary': {'order_count': 0, 'total_amount': 0.0},
                })

            # Build lookup caches
            user_ids = list(set(orders.mapped('user_id.id')))
            team_ids = list(set(orders.mapped('team_id.id')))
            users = {u.id: u.name for u in request.env['res.users'].sudo().browse(user_ids)}
            teams = {t.id: t.name for t in request.env['crm.team'].sudo().browse(team_ids)}

            # Parse group_by keys
            group_keys = [g.strip() for g in group_by_raw.split(',')]

            # Accumulate data per order line for product grouping
            all_rows = []
            total_amount = 0.0
            total_orders = 0

            for order in orders:
                total_amount += order.amount_untaxed
                total_orders += 1

                base_row = {
                    'order_name': order.name,
                    'date': str(order.date_order)[:10],
                    'partner': order.partner_id.name,
                    'salesperson': users.get(order.user_id.id, ''),
                    'team': teams.get(order.team_id.id, ''),
                    'amount_untaxed': order.amount_untaxed,
                    'amount_total': order.amount_total,
                    'state': order.state,
                    'company_id': order.company_id.id,
                    'company_name': order.company_id.name,
                }

                # Add time period fields
                date_order = order.date_order
                base_row['month'] = date_order.strftime('%Y-%m') if date_order else ''
                base_row['week'] = date_order.strftime('%Y-W%W') if date_order else ''

                # If product group is needed, split by line
                if 'product' in group_keys:
                    for line in order.order_line:
                        row = dict(base_row)
                        row['product'] = line.product_id.name or ''
                        row['product_uom_qty'] = line.product_uom_qty
                        row['price_subtotal'] = line.price_subtotal
                        all_rows.append(row)
                else:
                    all_rows.append(base_row)

            # Aggregate
            if group_keys:
                result = self._aggregate_rows(all_rows, group_keys)
            else:
                result = all_rows

            return request.make_json_response({
                'success': True,
                'data': result,
                'summary': {
                    'order_count': total_orders,
                    'total_amount_untaxed': total_amount,
                    'total_amount_total': sum(r.get('amount_total', 0) for r in result) if not group_keys else sum(r.get('amount_total', 0) for r in result),
                    'group_by': group_keys,
                    'date_from': date_from,
                    'date_to': date_to,
                    'states': states,
                },
            })
        except AccessDenied as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=401)
        except Exception as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=400)

    def _aggregate_rows(self, rows, group_keys):
        """Aggregate rows by the specified group keys, summing numeric fields."""
        from collections import OrderedDict

        numeric_fields = ['amount_untaxed', 'amount_total', 'price_subtotal', 'product_uom_qty']

        buckets = OrderedDict()
        for row in rows:
            key_parts = []
            for gk in group_keys:
                key_parts.append(str(row.get(gk, '')))
            key = ' | '.join(key_parts)

            if key not in buckets:
                bucket = {gk: row.get(gk, '') for gk in group_keys}
                for nf in numeric_fields:
                    bucket[nf] = 0.0
                bucket['order_count'] = 0
                buckets[key] = bucket

            bucket = buckets[key]
            bucket['order_count'] += 1
            for nf in numeric_fields:
                bucket[nf] += row.get(nf, 0.0)

        # Round
        for bucket in buckets.values():
            for nf in numeric_fields:
                bucket[nf] = round(bucket[nf], 2)

        return list(buckets.values())

    # ─── Accounting Audit endpoints ─────────────────────────────

    @http.route('/mcp/call/accounting_audit', type='http', auth='public', methods=['POST'], csrf=False)
    def accounting_audit(self, **kwargs):
        """Run accounting audit checks on posted and draft journal entries.

        Checks:
        - unbalanced: moves where sum(debit) != sum(credit)
        - date_mismatch: move lines with date different from parent move
        - stale_draft: draft entries older than N days
        - suspicious_amount: single-line moves or unusually large amounts
        """
        try:
            self._verify_api_key()
            data = json.loads(request.httprequest.data)

            date_from = data.get('date_from')
            date_to = data.get('date_to')
            checks = data.get('checks', ['unbalanced', 'date_mismatch', 'stale_draft', 'suspicious_amount'])
            limit = data.get('limit', 100)

            Move = request.env['account.move'].sudo()
            MoveLine = request.env['account.move.line'].sudo()
            results = {}

            base_domain = []
            if date_from:
                base_domain.append(('date', '>=', date_from))
            if date_to:
                base_domain.append(('date', '<=', date_to))

            # 1) Unbalanced moves — debit != credit at move level
            if 'unbalanced' in checks:
                domain = list(base_domain) + [('state', '=', 'posted')]
                moves = Move.search(domain, limit=limit)
                issues = []
                for move in moves:
                    debit = sum(move.line_ids.mapped('debit'))
                    credit = sum(move.line_ids.mapped('credit'))
                    diff = round(debit - credit, 2)
                    if diff != 0.0:
                        issues.append({
                            'move_id': move.id,
                            'move_name': move.name,
                            'date': str(move.date),
                            'journal': move.journal_id.name,
                            'partner': move.partner_id.name or '',
                            'total_debit': round(debit, 2),
                            'total_credit': round(credit, 2),
                            'difference': diff,
                            'line_count': len(move.line_ids),
                        })
                results['unbalanced'] = {
                    'issue_count': len(issues),
                    'issues': issues,
                }

            # 2) Date mismatch — move line date differs from parent move date
            if 'date_mismatch' in checks:
                domain = list(base_domain) + [('state', '=', 'posted'), ('date_mismatch', '=', False)]
                # No native date_mismatch field — compare manually
                domain_lines = list(base_domain) + [('parent_state', '=', 'posted')]
                lines = MoveLine.search(domain_lines, limit=limit * 5)
                issues = []
                seen_move_ids = set()
                for line in lines:
                    if line.move_id.id in seen_move_ids:
                        continue
                    if line.date != line.move_id.date:
                        seen_move_ids.add(line.move_id.id)
                        issues.append({
                            'move_id': line.move_id.id,
                            'move_name': line.move_id.name,
                            'move_date': str(line.move_id.date),
                            'line_date': str(line.date),
                            'journal': line.move_id.journal_id.name,
                            'account': line.account_id.code + ' ' + line.account_id.name,
                        })
                        if len(issues) >= limit:
                            break
                results['date_mismatch'] = {
                    'issue_count': len(issues),
                    'issues': issues,
                }

            # 3) Stale draft — draft entries older than 30 days
            if 'stale_draft' in checks:
                today = odoo_fields.Date.today()
                stale_date = odoo_fields.Date.subtract(today, days=30)
                domain = [('state', '=', 'draft'), ('date', '<=', stale_date)]
                if date_from:
                    domain.append(('date', '>=', date_from))
                if date_to:
                    domain.append(('date', '<=', date_to))
                moves = Move.search(domain, limit=limit, order='date asc')
                issues = []
                for move in moves:
                    days_old = (today - move.date).days
                    issues.append({
                        'move_id': move.id,
                        'move_name': move.name or '/',
                        'date': str(move.date),
                        'journal': move.journal_id.name,
                        'partner': move.partner_id.name or '',
                        'amount': round(sum(move.line_ids.mapped('debit')), 2),
                        'days_old': days_old,
                    })
                results['stale_draft'] = {
                    'issue_count': len(issues),
                    'issues': issues,
                }

            # 4) Suspicious amount — single-line posted moves or amounts > threshold
            if 'suspicious_amount' in checks:
                domain = list(base_domain) + [('state', '=', 'posted')]
                moves = Move.search(domain, limit=limit * 3)
                issues = []
                for move in moves:
                    lines = move.line_ids.filtered(lambda l: l.account_id.reconcile or l.debit or l.credit)
                    if len(lines) <= 1:
                        issues.append({
                            'move_id': move.id,
                            'move_name': move.name,
                            'date': str(move.date),
                            'journal': move.journal_id.name,
                            'reason': 'single_effective_line',
                            'amount': round(sum(lines.mapped('debit') + lines.mapped('credit')), 2),
                        })
                        continue
                    # Check for unusually large amounts (top 5% by absolute debit)
                    max_debit = max(lines.mapped('debit'))
                    avg_debit = sum(lines.mapped('debit')) / max(len(lines), 1)
                    if avg_debit > 0 and max_debit / avg_debit > 100:
                        issues.append({
                            'move_id': move.id,
                            'move_name': move.name,
                            'date': str(move.date),
                            'journal': move.journal_id.name,
                            'reason': 'large_amount_ratio',
                            'max_line': round(max_debit, 2),
                            'avg_line': round(avg_debit, 2),
                            'ratio': round(max_debit / avg_debit, 2),
                        })
                    if len(issues) >= limit:
                        break
                results['suspicious_amount'] = {
                    'issue_count': len(issues),
                    'issues': issues[:limit],
                }

            total_issues = sum(r.get('issue_count', 0) for r in results.values())

            return request.make_json_response({
                'success': True,
                'data': results,
                'summary': {
                    'total_issues': total_issues,
                    'checks_run': checks,
                    'date_from': date_from,
                    'date_to': date_to,
                },
            })
        except AccessDenied as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=401)
        except Exception as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=400)

    @http.route('/mcp/call/gl_report', type='http', auth='public', methods=['POST'], csrf=False)
    def gl_report(self, **kwargs):
        """General Ledger report with opening balance, movements, and closing balance."""
        try:
            self._verify_api_key()
            data = json.loads(request.httprequest.data)

            date_from = data.get('date_from')
            date_to = data.get('date_to')
            account_codes = data.get('account_codes')
            group_by = data.get('group_by', 'account')
            limit = data.get('limit', 500)

            if not date_from or not date_to:
                return request.make_json_response({
                    'success': False,
                    'error': 'date_from and date_to are required',
                }, status=400)

            Account = request.env['account.account'].sudo()
            MoveLine = request.env['account.move.line'].sudo()

            # Build account domain
            account_domain = [('company_id', '=', request.env.company.id)]
            if account_codes:
                account_domain.append(('code', 'in', account_codes))
            accounts = Account.search(account_domain, order='code')

            result = []
            for account in accounts:
                # Opening balance: sum of all lines before date_from
                opening_domain = [
                    ('account_id', '=', account.id),
                    ('date', '<', date_from),
                    ('parent_state', '=', 'posted'),
                ]
                opening_lines = MoveLine.search(opening_domain)
                opening_debit = round(sum(opening_lines.mapped('debit')), 2)
                opening_credit = round(sum(opening_lines.mapped('credit')), 2)
                opening_balance = round(opening_debit - opening_credit, 2)

                # Period movements
                period_domain = [
                    ('account_id', '=', account.id),
                    ('date', '>=', date_from),
                    ('date', '<=', date_to),
                    ('parent_state', '=', 'posted'),
                ]
                period_lines = MoveLine.search(period_domain)
                period_debit = round(sum(period_lines.mapped('debit')), 2)
                period_credit = round(sum(period_lines.mapped('credit')), 2)
                period_balance = round(period_debit - period_credit, 2)
                closing_balance = round(opening_balance + period_balance, 2)

                if group_by == 'account':
                    if opening_balance != 0 or period_debit != 0 or period_credit != 0:
                        result.append({
                            'account_code': account.code,
                            'account_name': account.name,
                            'account_type': account.account_type,
                            'opening_balance': opening_balance,
                            'period_debit': period_debit,
                            'period_credit': period_credit,
                            'period_balance': period_balance,
                            'closing_balance': closing_balance,
                            'line_count': len(period_lines),
                        })

                elif group_by == 'account_partner':
                    for partner_id in set(period_lines.mapped('partner_id').ids + opening_lines.mapped('partner_id').ids):
                        partner = request.env['res.partner'].sudo().browse(partner_id)
                        p_opening = sum(l.debit - l.credit for l in opening_lines if l.partner_id.id == partner_id)
                        p_period_lines = period_lines.filtered(lambda l: l.partner_id.id == partner_id)
                        p_debit = round(sum(p_period_lines.mapped('debit')), 2)
                        p_credit = round(sum(p_period_lines.mapped('credit')), 2)
                        p_balance = round(p_debit - p_credit, 2)
                        p_closing = round(p_opening + p_balance, 2)
                        if p_opening != 0 or p_debit != 0 or p_credit != 0:
                            result.append({
                                'account_code': account.code,
                                'account_name': account.name,
                                'partner': partner.name,
                                'opening_balance': round(p_opening, 2),
                                'period_debit': p_debit,
                                'period_credit': p_credit,
                                'period_balance': p_balance,
                                'closing_balance': p_closing,
                                'line_count': len(p_period_lines),
                            })

                elif group_by == 'account_journal':
                    for journal in set(period_lines.mapped('journal_id')):
                        j_period = period_lines.filtered(lambda l: l.journal_id.id == journal.id)
                        j_opening = sum(l.debit - l.credit for l in opening_lines if l.journal_id.id == journal.id)
                        j_debit = round(sum(j_period.mapped('debit')), 2)
                        j_credit = round(sum(j_period.mapped('credit')), 2)
                        j_balance = round(j_debit - j_credit, 2)
                        j_closing = round(j_opening + j_balance, 2)
                        if j_opening != 0 or j_debit != 0 or j_credit != 0:
                            result.append({
                                'account_code': account.code,
                                'account_name': account.name,
                                'journal': journal.name,
                                'opening_balance': round(j_opening, 2),
                                'period_debit': j_debit,
                                'period_credit': j_credit,
                                'period_balance': j_balance,
                                'closing_balance': j_closing,
                                'line_count': len(j_period),
                            })

                if len(result) >= limit:
                    break

            return request.make_json_response({
                'success': True,
                'data': result,
                'summary': {
                    'date_from': date_from,
                    'date_to': date_to,
                    'group_by': group_by,
                    'account_count': len(accounts),
                    'row_count': len(result),
                },
            })
        except AccessDenied as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=401)
        except Exception as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=400)

    @http.route('/mcp/call/gl_variance', type='http', auth='public', methods=['POST'], csrf=False)
    def gl_variance(self, **kwargs):
        """Compare GL balances between two periods to detect unexpected variances."""
        try:
            self._verify_api_key()
            data = json.loads(request.httprequest.data)

            p1_from = data.get('period1_from')
            p1_to = data.get('period1_to')
            p2_from = data.get('period2_from')
            p2_to = data.get('period2_to')
            threshold = data.get('variance_threshold', 0.01)
            account_codes = data.get('account_codes')

            if not all([p1_from, p1_to, p2_from, p2_to]):
                return request.make_json_response({
                    'success': False,
                    'error': 'period1_from, period1_to, period2_from, period2_to are required',
                }, status=400)

            Account = request.env['account.account'].sudo()
            MoveLine = request.env['account.move.line'].sudo()

            account_domain = [('company_id', '=', request.env.company.id)]
            if account_codes:
                account_domain.append(('code', 'in', account_codes))
            accounts = Account.search(account_domain, order='code')

            def _period_balance(acc_id, d_from, d_to):
                domain = [
                    ('account_id', '=', acc_id),
                    ('date', '>=', d_from),
                    ('date', '<=', d_to),
                    ('parent_state', '=', 'posted'),
                ]
                lines = MoveLine.search(domain)
                debit = round(sum(lines.mapped('debit')), 2)
                credit = round(sum(lines.mapped('credit')), 2)
                return round(debit - credit, 2)

            result = []
            for account in accounts:
                bal1 = _period_balance(account.id, p1_from, p1_to)
                bal2 = _period_balance(account.id, p2_from, p2_to)
                variance = round(bal2 - bal1, 2)
                pct_change = round((variance / bal1) * 100, 2) if bal1 != 0 else 0.0

                if abs(variance) >= threshold:
                    result.append({
                        'account_code': account.code,
                        'account_name': account.name,
                        'account_type': account.account_type,
                        'period1_balance': bal1,
                        'period2_balance': bal2,
                        'variance': variance,
                        'variance_pct': pct_change,
                    })

            return request.make_json_response({
                'success': True,
                'data': result,
                'summary': {
                    'period1': {'from': p1_from, 'to': p1_to},
                    'period2': {'from': p2_from, 'to': p2_to},
                    'variance_threshold': threshold,
                    'accounts_checked': len(accounts),
                    'accounts_with_variance': len(result),
                    'total_variance': round(sum(r['variance'] for r in result), 2),
                },
            })
        except AccessDenied as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=401)
        except Exception as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=400)

    @http.route('/mcp/call/account_move_search', type='http', auth='public', methods=['POST'], csrf=False)
    def account_move_search(self, **kwargs):
        """Search journal entries with optional line details."""
        try:
            self._verify_api_key()
            data = json.loads(request.httprequest.data)
            domain = data.get('domain', [])
            field_list = data.get('fields', ['name', 'date', 'journal_id', 'partner_id', 'state', 'move_type', 'amount_total'])
            with_lines = data.get('with_lines', False)
            limit = data.get('limit', 80)

            moves = request.env['account.move'].sudo().search(domain, limit=limit)
            result = []
            line_fields = ['account_id', 'partner_id', 'name', 'debit', 'credit', 'date', 'date_maturity', 'reconciled']

            for move in moves:
                move_data = move.read(field_list)[0]
                if with_lines:
                    move_data['lines'] = [line.read(line_fields)[0] for line in move.line_ids]
                result.append(move_data)

            return request.make_json_response({
                'success': True,
                'data': result,
            })
        except AccessDenied as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=401)
        except Exception as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=400)

    # ─── Purchase Order endpoints ──────────────────────────────

    @http.route('/mcp/call/purchase_order_search', type='http', auth='public', methods=['POST'], csrf=False)
    def purchase_order_search(self, **kwargs):
        """Search for purchase orders with optional filters"""
        try:
            self._verify_api_key()
            data = json.loads(request.httprequest.data)
            domain = data.get('domain', [])
            field_list = data.get('fields', ['name', 'partner_id', 'date_order', 'date_planned', 'amount_total', 'amount_untaxed', 'state', 'invoice_status', 'currency_id', 'company_id', 'user_id', 'origin'])
            limit = data.get('limit', 80)

            orders = request.env['purchase.order'].sudo().search(domain, limit=limit)
            result = [order.read(field_list)[0] for order in orders]

            return request.make_json_response({
                'success': True,
                'data': result
            })
        except AccessDenied as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=401)
        except Exception as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=400)

    @http.route('/mcp/call/purchase_order_read', type='http', auth='public', methods=['POST'], csrf=False)
    def purchase_order_read(self, **kwargs):
        """Read a specific purchase order by ID"""
        try:
            self._verify_api_key()
            data = json.loads(request.httprequest.data)
            order_id = data.get('id')
            field_list = data.get('fields', ['name', 'partner_id', 'date_order', 'date_planned', 'amount_total', 'amount_untaxed', 'state', 'invoice_status', 'currency_id', 'company_id', 'user_id', 'origin', 'order_line', 'picking_count', 'invoice_count'])

            if not order_id:
                return request.make_json_response({
                    'success': False,
                    'error': 'id is required'
                }, status=400)

            order = request.env['purchase.order'].sudo().browse(order_id)
            if not order.exists():
                return request.make_json_response({
                    'success': False,
                    'error': 'Purchase order not found'
                }, status=404)

            result = order.read(field_list)[0]

            return request.make_json_response({
                'success': True,
                'data': result
            })
        except AccessDenied as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=401)
        except Exception as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=400)

    # ─── Company endpoints ──────────────────────────────────────

    @http.route('/mcp/call/company_list', type='http', auth='public', methods=['POST'], csrf=False)
    def company_list(self, **kwargs):
        """List all active companies"""
        try:
            self._verify_api_key()
            data = json.loads(request.httprequest.data)
            field_list = data.get('fields', ['name', 'currency_id', 'partner_id', 'vat', 'email', 'phone'])

            companies = request.env['res.company'].sudo().search([('active', '=', True)])
            result = [company.read(field_list)[0] for company in companies]

            return request.make_json_response({
                'success': True,
                'data': result
            })
        except AccessDenied as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=401)
        except Exception as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=400)

    @http.route('/mcp/call/company_search', type='http', auth='public', methods=['POST'], csrf=False)
    def company_search(self, **kwargs):
        """Search for companies with optional filters"""
        try:
            self._verify_api_key()
            data = json.loads(request.httprequest.data)
            domain = data.get('domain', [])
            field_list = data.get('fields', ['name', 'currency_id', 'partner_id', 'vat', 'email', 'phone'])
            limit = data.get('limit', 80)

            companies = request.env['res.company'].sudo().search(domain, limit=limit)
            result = [company.read(field_list)[0] for company in companies]

            return request.make_json_response({
                'success': True,
                'data': result
            })
        except AccessDenied as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=401)
        except Exception as e:
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=400)
