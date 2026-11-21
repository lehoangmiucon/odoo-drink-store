"""Run through `odoo-bin shell -d <demo-db>`; creates demo data once.

Does not reset quantities on subsequent runs. No user credentials are changed.
"""

def fixture(model, key, values):
    record = env.ref('store_restock.' + key, raise_if_not_found=False)
    if record:
        return record, False
    record = env[model].create(values)
    env['ir.model.data'].create({'module': 'store_restock', 'name': key,
        'model': model, 'res_id': record.id, 'noupdate': True})
    return record, True


company = env.company
source, _ = fixture('stock.location', 'demo_central', {
    'name': 'Kho tổng DEMO', 'usage': 'internal', 'company_id': company.id})
transit, _ = fixture('stock.location', 'demo_transit', {
    'name': 'Hàng đang đi DEMO', 'usage': 'transit', 'company_id': company.id})
store, _ = fixture('stock.location', 'demo_supermarket', {
    'name': 'Siêu thị DEMO', 'usage': 'internal', 'company_id': company.id})
operation, _ = fixture('stock.picking.type', 'demo_internal_type', {
    'name': 'Chuyển hàng siêu thị DEMO', 'code': 'internal', 'sequence_code': 'BSH-DEMO',
    'company_id': company.id, 'create_backorder': 'always',
    'default_location_src_id': source.id, 'default_location_dest_id': store.id})
route, _ = fixture('store.restock.route', 'demo_route', {
    'name': 'Kho tổng → Siêu thị DEMO', 'company_id': company.id,
    'source_id': source.id, 'transit_id': transit.id, 'destination_id': store.id,
    'picking_type_id': operation.id})
product, created = fixture('product.product', 'demo_water', {
    'name': 'Nước suối 500 ml (chai)', 'default_code': 'BSH-500', 'is_storable': True,
    'categ_id': env.ref('store_restock.category_restock_water').id})
if created:
    quant = env['stock.quant'].with_context(inventory_mode=True).create({
        'product_id': product.id, 'location_id': source.id, 'inventory_quantity': 100})
    quant.action_apply_inventory()
    print('Đã nhập số dư đầu kỳ DEMO bằng điều chỉnh tồn kho: kho tổng 100, siêu thị 0.')
else:
    print('Dữ liệu DEMO đã có; giữ nguyên số tồn hiện tại.')

cola, cola_created = fixture('product.product', 'demo_cola', {
    'name': 'Coca-Cola lon 330 ml (lon)',
    'default_code': 'BSH-COLA330', 'is_storable': True,
    'categ_id': env.ref('store_restock.category_restock_soft_drinks').id})
if cola_created:
    quant = env['stock.quant'].with_context(inventory_mode=True).create({
        'product_id': cola.id, 'location_id': source.id, 'inventory_quantity': 50})
    quant.action_apply_inventory()
    print('Đã nhập số dư đầu kỳ Coca-Cola DEMO: kho tổng 50 lon, siêu thị 0.')
else:
    print('Coca-Cola DEMO đã có; giữ nguyên số tồn hiện tại.')
env.cr.commit()
print('DEMO_READY', route.name, product.display_name)
print('DEMO_READY', route.name, cola.display_name)
