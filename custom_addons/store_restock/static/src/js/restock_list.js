/** @odoo-module **/

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListRenderer } from "@web/views/list/list_renderer";

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
