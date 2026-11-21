from odoo import Command
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestRestockFulfillment(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.Request = cls.env['store.restock.request']
        base = cls.env.ref('base.group_user')
        employee = cls.env.ref('store_restock.group_restock_employee')
        manager = cls.env.ref('store_restock.group_restock_manager')
        cls.env.ref('base.user_admin').group_ids = [Command.link(manager.id)]
        def user(login, groups):
            return cls.env['res.users'].create({'name': login, 'login': login,
                'company_id': cls.company.id, 'company_ids': [Command.set(cls.company.ids)],
                'group_ids': [Command.set([base.id] + [g.id for g in groups])]})
        cls.employee = user('restock-test-employee', [employee])
        cls.other = user('restock-test-other', [employee])
        cls.manager = user('restock-test-manager', [manager])
        cls.both = user('restock-test-both', [employee, manager])
        Location = cls.env['stock.location']
        cls.source = Location.create({'name': 'Test central', 'usage': 'internal', 'company_id': cls.company.id})
        cls.transit = Location.create({'name': 'Test transit', 'usage': 'transit', 'company_id': cls.company.id})
        cls.destination = Location.create({'name': 'Test supermarket', 'usage': 'internal', 'company_id': cls.company.id})
        cls.picking_type = cls.env['stock.picking.type'].create({'name': 'Test restock', 'code': 'internal',
            'sequence_code': 'TESTREST', 'company_id': cls.company.id, 'create_backorder': 'always'})
        cls.route = cls.env['store.restock.route'].create({'name': 'Test route', 'company_id': cls.company.id,
            'source_id': cls.source.id, 'transit_id': cls.transit.id, 'destination_id': cls.destination.id,
            'picking_type_id': cls.picking_type.id})
        cls.product = cls.env['product.product'].create({'name': 'Test restock water', 'is_storable': True})
        cls.env['stock.quant']._update_available_quantity(cls.product, cls.source, 100)

    def request(self, user=None, **values):
        return self.Request.with_user(user or self.employee).create({
            'product_id': self.product.id, 'quantity': 20, 'reason': 'Restock shift',
            'route_id': self.route.id, **values})

    def approved(self):
        request = self.request()
        request.action_submit()
        request.with_user(self.manager).action_approve()
        return request

    def shipped(self):
        request = self.approved()
        request.with_user(self.manager).action_dispatch()
        return request

    def qty(self, location):
        return sum(self.env['stock.quant'].search([
            ('product_id', '=', self.product.id), ('location_id', '=', location.id)]).mapped('quantity'))

    def receive(self, request, qty):
        wizard = self.env['store.restock.receive.wizard'].with_user(self.employee).create({
            'request_id': request.id, 'quantity': qty, 'note': 'Counted'})
        wizard.action_receive()
        return wizard

    def test_full_flow_stock_and_audit(self):
        request = self.approved()
        self.assertEqual(self.qty(self.source), 100)
        self.assertEqual(self.qty(self.destination), 0)
        self.assertEqual(request.outbound_id.sudo().state, 'draft')
        request.with_user(self.manager).action_dispatch()
        self.assertEqual([self.qty(loc) for loc in (self.source, self.transit, self.destination)], [80, 20, 0])
        self.assertTrue(request.shipped_at)
        self.assertEqual(request.shipped_by, self.manager)
        self.receive(request, 20)
        self.assertEqual(request.state, 'received')
        self.assertEqual([self.qty(loc) for loc in (self.source, self.transit, self.destination)], [80, 0, 20])
        self.assertEqual(request.receipt_ids.received_by, self.employee)
        self.assertEqual(request.receipt_ids.quantity, 20)
        self.assertEqual(request.remaining_quantity, 0)
        details = request.read(['route_id', 'source_name', 'outbound_ref', 'receipt_ids', 'central_stock', 'supermarket_stock'])[0]
        self.assertEqual(details['central_stock'], 80)
        self.assertEqual(details['supermarket_stock'], 20)

    def test_partial_receipt_backorder_and_replay(self):
        request = self.shipped()
        stale_action = request.action_open_receive_wizard()
        stale = self.env['store.restock.receive.wizard'].with_user(self.employee).browse(stale_action['res_id'])
        wizard = self.receive(request, 8)
        self.assertEqual(request.state, 'shipped')
        self.assertEqual(request.remaining_quantity, 12)
        self.assertEqual(self.qty(self.destination), 8)
        with self.assertRaises(UserError):
            wizard.action_receive()
        stale.write({'quantity': 8})
        with self.assertRaises(UserError):
            stale.action_receive()
        self.assertEqual(self.qty(self.destination), 8)
        self.receive(request, 12)
        self.assertEqual(request.state, 'received')
        self.assertEqual(len(request.receipt_ids), 2)
        self.assertEqual(self.qty(self.destination), 20)

    def test_invalid_receipts_no_stock_change(self):
        request = self.shipped()
        for qty in (0, -1, 21, 20.4, float('nan'), float('inf')):
            with self.assertRaises(ValidationError):
                request._receive_stock(qty, 0, '')
        self.assertEqual(self.qty(self.destination), 0)
        self.assertEqual(request.state, 'shipped')

    def test_permissions_and_immutable_wizard(self):
        request = self.shipped()
        with self.assertRaises(AccessError):
            request.with_user(self.other).action_open_receive_wizard()
        with self.assertRaises(AccessError):
            request.with_user(self.manager).action_open_receive_wizard()
        with self.assertRaises(AccessError):
            request.write({'received_quantity': 20})
        wizard = self.env['store.restock.receive.wizard'].with_user(self.employee).create({
            'request_id': request.id, 'quantity': 20})
        with self.assertRaises(AccessError):
            wizard.write({'expected_received': 5})
        with self.assertRaises(AccessError):
            request.action_dispatch()

    def test_stock_shortage_and_duplicate_dispatch(self):
        request = self.request(quantity=101)
        request.action_submit()
        request.with_user(self.manager).action_approve()
        with self.assertRaises(UserError):
            request.with_user(self.manager).action_dispatch()
        self.assertEqual(request.state, 'approved')
        self.assertEqual(self.qty(self.source), 100)
        self.assertEqual(self.qty(self.destination), 0)
        second = self.shipped()
        with self.assertRaises(UserError):
            second.with_user(self.manager).action_dispatch()
        self.assertEqual(self.qty(self.source), 80)
        with self.assertRaises(UserError):
            second.with_user(self.env.ref('base.user_admin')).unlink()

    def test_privacy_review_and_validation(self):
        request = self.request()
        with self.assertRaises(AccessError):
            request.with_user(self.manager).read(['name'])
        with self.assertRaises(AccessError):
            request.with_user(self.other).read(['name'])
        for values in ({'quantity': 0}, {'quantity': -1}, {'reason': ' '}, {'product_id': False}):
            bad = self.request(**values)
            with self.assertRaises(ValidationError):
                bad.action_submit()
        request.action_submit()
        with self.assertRaises(AccessError):
            request.write({'quantity': 5})
        with self.assertRaises(ValidationError):
            request.with_user(self.manager)._reject(' ')
        request.with_user(self.manager)._reject('Enough stock')
        self.assertFalse(request.outbound_id)
        self.assertEqual(self.qty(self.source), 100)
        own = self.request(user=self.both)
        own.action_submit()
        with self.assertRaises(AccessError):
            own.action_approve()

    def test_product_and_route_checks_atomic_approval(self):
        product = self.env['product.product'].create({'name': 'Not tracked'})
        request = self.request(product_id=product.id)
        request.action_submit()
        with self.assertRaises(UserError):
            request.with_user(self.manager).action_approve()
        self.assertEqual(request.state, 'submitted')
        self.assertFalse(request.outbound_id)
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.route.write({'transit_id': self.source.id})

    def test_delete_and_withdrawal(self):
        draft = self.request(); draft.unlink()
        submitted = self.request(); submitted.action_submit(); submitted.unlink()
        withdrawn = self.request(); withdrawn.action_submit(); withdrawn.action_cancel()
        with self.assertRaises(UserError):
            withdrawn.with_user(self.manager).action_approve()
        self.assertEqual(withdrawn.state, 'cancelled')
        self.assertEqual(self.qty(self.destination), 0)

    def test_employee_catalog_readonly_even_with_product_grant(self):
        self.employee.group_ids = [Command.link(self.env.ref('product.group_product_manager').id)]
        self.assertTrue(self.product.with_user(self.employee).read(['name']))
        template = self.product.product_tmpl_id
        for model in ('product.template', 'product.product'):
            with self.assertRaises(AccessError):
                self.env[model].with_user(self.employee).create({'name': 'Forbidden product'})
        for record in (self.product, template):
            with self.assertRaises(AccessError):
                record.with_user(self.employee).write({'name': 'Forbidden rename'})
            with self.assertRaises(AccessError):
                record.with_user(self.employee).unlink()
        action = self.env.ref('store_restock.action_restock_products_menu').with_user(self.employee).run()
        self.assertEqual(action['id'], self.env.ref('store_restock.action_restock_products_readonly').id)
        admin = self.env.ref('base.user_admin')
        product = self.env['product.product'].with_user(admin).create({'name': 'Admin catalog test'})
        product.write({'name': 'Admin catalog updated'})
        product.unlink()
        request = self.request()
        request.action_submit()
        self.assertEqual(request.state, 'submitted')
