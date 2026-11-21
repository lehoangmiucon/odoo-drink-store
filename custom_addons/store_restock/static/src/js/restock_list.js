/** @odoo-module **/

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListRenderer } from "@web/views/list/list_renderer";
import { X2ManyField, x2ManyField } from "@web/views/fields/x2many/x2many_field";

// Only this view has fixed headers; other Odoo lists retain native sorting.
export class RestockListRenderer extends ListRenderer {
    isSortable() {
        return false;
    }
}

registry.category("views").add("store_restock_fixed_list", {
    ...listView,
    Renderer: RestockListRenderer,
});

// Receipt history can be reordered by time, while other headers stay static.
export class RestockReceiptRenderer extends ListRenderer {
    isSortable(column) {
        return column.name === "received_at" && super.isSortable(column);
    }
}

export class RestockReceiptField extends X2ManyField {
    static components = {
        ...X2ManyField.components,
        ListRenderer: RestockReceiptRenderer,
    };
}

registry.category("fields").add("store_restock_receipts", {
    ...x2ManyField,
    component: RestockReceiptField,
});
