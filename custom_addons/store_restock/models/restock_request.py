from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError


class RestockRequest(models.Model):
    _name = 'store.restock.request'
    _description = 'Phiếu yêu cầu bổ sung hàng'
    _order = 'id desc'

    name = fields.Char(string='Mã phiếu', default='Mới', readonly=True, copy=False, required=True)
    requester_id = fields.Many2one(
        'res.users', string='Người yêu cầu', default=lambda self: self.env.user,
        required=True, readonly=True, copy=False,
    )
    request_date = fields.Date(
        string='Ngày yêu cầu', default=fields.Date.context_today,
        required=True, readonly=True, copy=False,
    )
    company_id = fields.Many2one(
        'res.company', string='Công ty', default=lambda self: self.env.company,
        required=True, readonly=True, copy=False,
    )
    product_id = fields.Many2one(
        'product.product', string='Sản phẩm', ondelete='restrict', check_company=True,
    )
    quantity = fields.Float(string='Số lượng', default=1, digits='Product Unit')
    product_uom_id = fields.Many2one(
        related='product_id.uom_id', string='Đơn vị tính', readonly=True,
    )
    reason = fields.Text(string='Lý do yêu cầu')
    state = fields.Selection(
        [('draft', 'Nháp'), ('submitted', 'Chờ duyệt'),
         ('approved', 'Đã duyệt'), ('rejected', 'Từ chối')],
        string='Trạng thái', default='draft', required=True, readonly=True, copy=False,
    )
    reviewer_id = fields.Many2one('res.users', string='Người xử lý', readonly=True, copy=False)
    reviewed_at = fields.Datetime(string='Thời gian xử lý', readonly=True, copy=False)
    rejection_reason = fields.Text(string='Lý do từ chối', readonly=True, copy=False)

    def _require_employee(self):
        if not self.env.user.has_group('store_restock.group_restock_employee'):
            raise AccessError('Bạn cần quyền Nhân viên kho để tạo hoặc gửi phiếu.')

    def _lock_records(self):
        self.check_access('write')
        self.flush_recordset()
        self.env.cr.execute(
            'SELECT id FROM store_restock_request WHERE id = ANY(%s) ORDER BY id FOR UPDATE',
            [self.ids],
        )
        self.invalidate_recordset()
        self.check_access('write')

    def _check_own_drafts(self):
        self._require_employee()
        for request in self:
            if request.requester_id != self.env.user or request.state != 'draft':
                raise AccessError('Chỉ được sửa hoặc gửi phiếu nháp do mình tạo.')

    @api.model_create_multi
    def create(self, vals_list):
        self._require_employee()
        allowed_fields = {'product_id', 'quantity', 'reason'}
        server_defaults = {
            'name': 'Mới',
            'requester_id': self.env.uid,
            'request_date': fields.Date.context_today(self),
            'company_id': self.env.company.id,
            'state': 'draft',
            'reviewer_id': False,
            'reviewed_at': False,
            'rejection_reason': False,
        }
        prepared = []
        for vals in vals_list:
            if set(vals) - allowed_fields - server_defaults.keys():
                raise AccessError('Trường dữ liệu không được phép khi tạo phiếu.')
            provided_defaults = {key: value for key, value in vals.items() if key in server_defaults}
            if 'request_date' in provided_defaults:
                provided_defaults['request_date'] = fields.Date.to_date(provided_defaults['request_date'])
            if any(value != server_defaults[key] for key, value in provided_defaults.items()):
                raise AccessError('Mã phiếu, người tạo, trạng thái và thông tin xử lý do hệ thống quản lý.')
            prepared.append({
                **vals,
                'name': self.env['ir.sequence'].next_by_code('store.restock.request') or '/',
                'requester_id': self.env.uid,
                'request_date': fields.Date.context_today(self),
                'company_id': self.env.company.id,
                'state': 'draft',
                'reviewer_id': False,
                'reviewed_at': False,
                'rejection_reason': False,
            })
        return super().create(prepared)

    def write(self, vals):
        if set(vals) - {'product_id', 'quantity', 'reason'}:
            raise AccessError('Hãy dùng các nút xử lý để chuyển trạng thái phiếu.')
        self._lock_records()
        self._check_own_drafts()
        return super().write(vals)

    def unlink(self):
        raise AccessError('Phiếu được giữ lại để theo dõi lịch sử và không được xóa.')

    def copy(self, default=None):
        self.ensure_one()
        raise UserError('Hãy tạo phiếu mới bằng nút Tạo.')

    def action_submit(self):
        self._lock_records()
        self._check_own_drafts()
        for request in self:
            if not request.product_id:
                raise ValidationError('Hãy chọn sản phẩm trước khi gửi duyệt.')
            if request.product_uom_id.compare(request.quantity, 0) <= 0:
                raise ValidationError('Số lượng phải lớn hơn 0 theo độ làm tròn của đơn vị tính.')
            if not (request.reason or '').strip():
                raise ValidationError('Hãy nhập lý do yêu cầu trước khi gửi duyệt.')
        return super().write({'state': 'submitted'})

    def _check_review(self):
        if not self.env.user.has_group('store_restock.group_restock_manager'):
            raise AccessError('Chỉ quản lý được duyệt hoặc từ chối phiếu.')
        for request in self:
            if request.requester_id == self.env.user:
                raise AccessError('Bạn không được xử lý phiếu do chính mình tạo.')
            if request.state != 'submitted':
                raise UserError('Chỉ được xử lý phiếu đang Chờ duyệt.')

    def action_approve(self):
        self._lock_records()
        self._check_review()
        return super().write({
            'state': 'approved',
            'reviewer_id': self.env.uid,
            'reviewed_at': fields.Datetime.now(),
            'rejection_reason': False,
        })

    def action_open_reject_wizard(self):
        self.ensure_one()
        self.check_access('write')
        self._check_review()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Từ chối yêu cầu bổ sung hàng',
            'res_model': 'store.restock.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_request_id': self.id},
        }

    def _reject(self, reason):
        self._lock_records()
        self._check_review()
        if not (reason or '').strip():
            raise ValidationError('Hãy nhập lý do từ chối.')
        return super().write({
            'state': 'rejected',
            'reviewer_id': self.env.uid,
            'reviewed_at': fields.Datetime.now(),
            'rejection_reason': reason.strip(),
        })
