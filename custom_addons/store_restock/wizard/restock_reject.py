from odoo import fields, models
from odoo.exceptions import AccessError


class RestockRejectWizard(models.TransientModel):
    _name = 'store.restock.reject.wizard'
    _description = 'Lý do từ chối yêu cầu bổ sung hàng'

    request_id = fields.Many2one(
        'store.restock.request', string='Phiếu yêu cầu', required=True, readonly=True,
    )
    rejection_reason = fields.Text(string='Lý do từ chối', required=True)

    def action_confirm_reject(self):
        self.ensure_one()
        self.check_access('read')
        if not self.env.user.has_group('store_restock.group_restock_manager'):
            raise AccessError('Chỉ quản lý được từ chối phiếu.')
        self.request_id._reject(self.rejection_reason)
        return {'type': 'ir.actions.act_window_close'}
