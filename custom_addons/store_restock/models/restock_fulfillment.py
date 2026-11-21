import math

from odoo import api, fields, models, Command
from odoo.exceptions import AccessError, UserError, ValidationError


class RestockRoute(models.Model):
    _name = 'store.restock.route'
    _description = 'Tuyến bổ sung hàng'
    _check_company_auto = True

    name = fields.Char(string='Tuyến bổ sung', required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    source_id = fields.Many2one('stock.location', string='Kho tổng', required=True, check_company=True)
    transit_id = fields.Many2one('stock.location', string='Hàng đang đi', required=True, check_company=True)
    destination_id = fields.Many2one('stock.location', string='Kho siêu thị', required=True, check_company=True)
    picking_type_id = fields.Many2one('stock.picking.type', string='Loại chuyển nội bộ', required=True, check_company=True)

    def _validate_route(self):
        for route in self.sudo():
            locations = [route.source_id, route.transit_id, route.destination_id]
            if any(not loc.active or loc.company_id != route.company_id for loc in locations):
                raise ValidationError('Ba vị trí phải hoạt động và thuộc đúng công ty của tuyến.')
            if [loc.usage for loc in locations] != ['internal', 'transit', 'internal']:
                raise ValidationError('Tuyến phải đi từ kho nội bộ qua vị trí trung chuyển tới kho nội bộ.')
            if len({loc.id for loc in locations}) != 3:
                raise ValidationError('Kho tổng, trung chuyển và siêu thị phải là ba vị trí khác nhau.')
            if route.source_id.parent_path.startswith(route.destination_id.parent_path) or route.destination_id.parent_path.startswith(route.source_id.parent_path):
                raise ValidationError('Kho tổng và kho siêu thị không được chứa nhau.')
            if (not route.picking_type_id.active or route.picking_type_id.code != 'internal'
                    or route.picking_type_id.company_id != route.company_id
                    or route.picking_type_id.create_backorder == 'never'):
                raise ValidationError('Chọn loại chuyển nội bộ cùng công ty, có hỗ trợ đơn giao còn lại.')

    @api.constrains('source_id', 'transit_id', 'destination_id', 'company_id', 'picking_type_id')
    def _check_route(self):
        self._validate_route()


class RestockReceipt(models.Model):
    _name = 'store.restock.receipt'
    _description = 'Lần nhận hàng bổ sung'
    _order = 'id desc'

    request_id = fields.Many2one('store.restock.request', required=True, ondelete='restrict')
    company_id = fields.Many2one(related='request_id.company_id', store=True)
    quantity = fields.Float(string='Thực nhận', digits='Product Unit', required=True)
    received_by = fields.Many2one('res.users', string='Người nhận', required=True)
    received_at = fields.Datetime(string='Thời gian nhận', required=True)
    picking_ref = fields.Char(string='Phiếu nhập', required=True)
    note = fields.Text(string='Ghi chú kiểm nhận')


class RestockFulfillment(models.Model):
    _inherit = 'store.restock.request'

    route_id = fields.Many2one('store.restock.route', string='Tuyến bổ sung', ondelete='restrict')
    source_id = fields.Many2one('stock.location', readonly=True, copy=False)
    transit_id = fields.Many2one('stock.location', readonly=True, copy=False)
    destination_id = fields.Many2one('stock.location', readonly=True, copy=False)
    transfer_type_id = fields.Many2one('stock.picking.type', readonly=True, copy=False)
    outbound_id = fields.Many2one('stock.picking', readonly=True, copy=False, ondelete='restrict')
    inbound_id = fields.Many2one('stock.picking', readonly=True, copy=False, ondelete='restrict')
    outbound_ref = fields.Char(string='Phiếu xuất kho tổng', readonly=True, copy=False)
    inbound_ref = fields.Char(string='Phiếu nhập đang chờ', readonly=True, copy=False)
    source_name = fields.Char(string='Kho tổng', readonly=True, copy=False)
    destination_name = fields.Char(string='Kho siêu thị', readonly=True, copy=False)
    shipped_at = fields.Datetime(string='Thời gian gửi hàng', readonly=True, copy=False)
    shipped_by = fields.Many2one('res.users', string='Người gửi hàng', readonly=True, copy=False)
    received_quantity = fields.Float(string='Đã nhận', digits='Product Unit', readonly=True, copy=False)
    remaining_quantity = fields.Float(string='Còn chờ nhận', compute='_compute_remaining', digits='Product Unit')
    receipt_ids = fields.One2many('store.restock.receipt', 'request_id', string='Lịch sử nhận hàng', readonly=True)
    central_stock = fields.Float(string='Tồn kho tổng hiện tại', compute='_compute_stock', compute_sudo=True, digits='Product Unit')
    supermarket_stock = fields.Float(string='Tồn siêu thị hiện tại', compute='_compute_stock', compute_sudo=True, digits='Product Unit')

    @api.model
    def default_get(self, field_names):
        values = super().default_get(field_names)
        if 'route_id' in field_names and not values.get('route_id'):
            values['route_id'] = self.env['store.restock.route'].search([
                ('company_id', '=', self.env.company.id)], limit=1).id
        return values

    @api.depends('state', 'received_quantity', 'route_id', 'product_id')
    def _compute_stock(self):
        for request in self:
            for field, location in [('central_stock', request.source_id or request.route_id.source_id),
                                    ('supermarket_stock', request.destination_id or request.route_id.destination_id)]:
                request[field] = sum(self.env['stock.quant'].search([
                    ('company_id', '=', request.company_id.id), ('product_id', '=', request.product_id.id),
                    ('location_id', '=', location.id)]).mapped('quantity')) if location and request.product_id else 0

    @api.depends('quantity', 'received_quantity', 'state')
    def _compute_remaining(self):
        for request in self:
            request.remaining_quantity = max(0, request.quantity - request.received_quantity) if request.state in ('shipped', 'received') else 0

    @api.constrains('route_id', 'company_id')
    def _check_route_company(self):
        for request in self:
            if request.route_id and request.route_id.company_id != request.company_id:
                raise ValidationError('Tuyến bổ sung phải cùng công ty với phiếu.')

    def _stock_env(self):
        # Elevation is confined to stock operations after ownership/role checks.
        return self.env['stock.picking'].sudo().with_context({}, allowed_company_ids=[self.company_id.id])

    def _create_transfer(self, source, destination, quantity):
        self.ensure_one()
        return self._stock_env().create({
            'origin': self.name,
            'company_id': self.company_id.id,
            'picking_type_id': self.transfer_type_id.id,
            'location_id': source.id,
            'location_dest_id': destination.id,
            'move_ids': [Command.create({
                'company_id': self.company_id.id,
                'product_id': self.product_id.id,
                'uom_id': self.product_id.uom_id.id,
                'product_uom_qty': quantity,
                'location_id': source.id,
                'location_dest_id': destination.id,
            })],
        })

    def _prepare_outbound(self):
        self.ensure_one()
        if self.outbound_id:
            return
        if not self.product_id.is_storable or self.product_id.tracking:
            raise UserError('Luồng này cần hàng hóa có theo dõi tồn kho, không quản lý lô/serial. Hãy kiểm tra sản phẩm.')
        if not math.isfinite(self.quantity) or self.product_uom_id.compare(self.quantity, 0) <= 0:
            raise ValidationError('Số lượng yêu cầu phải là số hữu hạn lớn hơn 0.')
        route = self.route_id or self.env['store.restock.route'].search([('company_id', '=', self.company_id.id)], limit=1)
        if not route or not route.active or route.company_id != self.company_id:
            raise UserError('Chưa có tuyến bổ sung hợp lệ. Nhờ quản trị viên cấu hình Kho tổng → Siêu thị.')
        route._validate_route()
        route = route.sudo()
        self._write_workflow({
            'route_id': route.id, 'source_id': route.source_id.id, 'transit_id': route.transit_id.id,
            'destination_id': route.destination_id.id, 'transfer_type_id': route.picking_type_id.id,
            'source_name': route.source_id.display_name, 'destination_name': route.destination_id.display_name,
        })
        picking = self._create_transfer(self.source_id, self.transit_id, self.quantity)
        self._write_workflow({'outbound_id': picking.id, 'outbound_ref': picking.name})

    def action_approve(self):
        with self.env.cr.savepoint():
            result = super().action_approve()
            for request in self:
                request._prepare_outbound()
            return result

    def action_dispatch(self):
        self.ensure_one()
        if not self.env.user.has_group('store_restock.group_restock_manager'):
            raise AccessError('Chỉ quản lý kho tổng được gửi hàng.')
        with self.env.cr.savepoint():
            self._lock_records()
            if self.state != 'approved':
                raise UserError('Chỉ gửi hàng cho phiếu đã duyệt và chưa gửi.')
            self._prepare_outbound()
            picking = self._stock_env().browse(self.outbound_id.id)
            if picking.state in ('done', 'cancel'):
                raise UserError('Phiếu xuất đã xử lý ngoài luồng. Nhờ quản trị viên kiểm tra.')
            picking.action_confirm()
            picking.action_assign()
            move = picking.move_ids
            if len(move) != 1 or move.product_id != self.product_id or move.state != 'assigned' or self.product_uom_id.compare(move.quantity, self.quantity) != 0:
                raise UserError('Kho tổng chưa đủ hàng khả dụng để gửi toàn bộ yêu cầu. Bổ sung tồn kho rồi thử lại.')
            move.picked = True
            picking.with_context(skip_backorder=True).button_validate()
            if picking.state != 'done':
                raise UserError('Phiếu xuất chưa hoàn tất; chưa ghi nhận gửi hàng.')
            incoming = self._create_transfer(self.transit_id, self.destination_id, self.quantity)
            incoming.action_confirm()
            self._write_workflow({
                'state': 'shipped', 'shipped_at': fields.Datetime.now(), 'shipped_by': self.env.uid,
                'inbound_id': incoming.id, 'inbound_ref': incoming.name,
            })
        return True

    def _check_receiver(self):
        self._require_employee()
        self.check_access('write')
        if self.requester_id != self.env.user:
            raise AccessError('Chỉ nhân viên tạo yêu cầu được xác nhận thực nhận.')
        if self.state != 'shipped':
            raise UserError('Chỉ nhận hàng khi phiếu đang vận chuyển và còn hàng chờ nhận.')

    def action_open_receive_wizard(self):
        self.ensure_one()
        self._check_receiver()
        wizard = self.env['store.restock.receive.wizard'].create({
            'request_id': self.id, 'quantity': self.remaining_quantity})
        return {'type': 'ir.actions.act_window', 'name': 'Siêu thị nhận hàng',
                'res_model': 'store.restock.receive.wizard', 'view_mode': 'form', 'target': 'new',
                'res_id': wizard.id}

    def _receive_stock(self, quantity, expected_received, note):
        self.ensure_one()
        with self.env.cr.savepoint():
            self._lock_records()
            self._check_receiver()
            uom = self.product_uom_id
            if uom.compare(expected_received, self.received_quantity) != 0:
                raise UserError('Phiếu đã được nhận ở phiên khác. Đóng hộp thoại, tải lại và kiểm đếm phần còn lại.')
            if not math.isfinite(quantity) or uom.compare(quantity, 0) <= 0 or uom.compare(quantity, self.remaining_quantity) > 0:
                raise ValidationError('Thực nhận phải lớn hơn 0 và không vượt số lượng còn chờ nhận.')
            if quantity > self.remaining_quantity + 1e-6 or not math.isclose(quantity, uom.round(quantity), rel_tol=0, abs_tol=1e-6):
                raise ValidationError('Thực nhận phải đúng bước đơn vị sản phẩm và không vượt phần còn lại.')
            incoming = self._stock_env().browse(self.inbound_id.id)
            if incoming.state in ('done', 'cancel') or len(incoming.move_ids) != 1:
                raise UserError('Phiếu nhập đã thay đổi ngoài luồng. Nhờ quản trị viên kiểm tra.')
            incoming.action_assign()
            move = incoming.move_ids
            if move.product_id != self.product_id or move.location_id != self.transit_id or move.location_dest_id != self.destination_id:
                raise UserError('Thông tin phiếu nhập không khớp với yêu cầu.')
            if move.state != 'assigned' or uom.compare(move.quantity, self.remaining_quantity) < 0:
                raise UserError('Chưa đủ hàng tại vị trí trung chuyển để nhận. Nhờ quản lý kiểm tra.')
            move.write({'quantity': quantity, 'picked': True})
            incoming.with_context(skip_backorder=True).button_validate()
            if incoming.state != 'done':
                raise UserError('Phiếu nhập chưa hoàn tất; tồn chưa được xác nhận.')
            total = self.received_quantity + quantity
            complete = uom.compare(total, self.quantity) == 0
            pending = incoming.backorder_ids.filtered(lambda p: p.state not in ('done', 'cancel'))
            if not complete and len(pending) != 1:
                raise UserError('Không tạo được phiếu chờ nhận phần còn lại.')
            self.env['store.restock.receipt'].sudo().create({
                'request_id': self.id, 'quantity': quantity, 'received_by': self.env.uid,
                'received_at': fields.Datetime.now(), 'picking_ref': incoming.name, 'note': note,
            })
            self._write_workflow({'received_quantity': total, 'state': 'received' if complete else 'shipped',
                'inbound_id': False if complete else pending.id, 'inbound_ref': False if complete else pending.name})
        return True
