from odoo import api, fields, models
from odoo.exceptions import AccessError


class RestockReceiveWizard(models.TransientModel):
    _name = 'store.restock.receive.wizard'
    _description = 'Kiểm nhận hàng tại siêu thị'

    request_id = fields.Many2one('store.restock.request', string='Phiếu yêu cầu', required=True, readonly=True)
    remaining_quantity = fields.Float(related='request_id.remaining_quantity', string='Còn chờ nhận', readonly=True)
    quantity = fields.Float(string='Thực nhận lần này', digits='Product Unit', required=True)
    note = fields.Text(string='Ghi chú kiểm nhận')
    expected_received = fields.Float(readonly=True, digits='Product Unit')

    @api.model_create_multi
    def create(self, vals_list):
        prepared = []
        for values in vals_list:
            request = self.env['store.restock.request'].browse(values.get('request_id')).exists()
            request.ensure_one()
            request._check_receiver()
            prepared.append({**values, 'expected_received': request.received_quantity})
        return super().create(prepared)

    def write(self, values):
        if set(values) - {'quantity', 'note'}:
            raise AccessError('Không được thay đổi phiếu liên kết của lần nhận hàng.')
        return super().write(values)

    def action_receive(self):
        self.ensure_one()
        self.request_id._receive_stock(self.quantity, self.expected_received, self.note)
        return {'type': 'ir.actions.act_window_close'}
