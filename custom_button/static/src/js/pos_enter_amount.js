/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";

patch(PosStore.prototype, {
    async openAmountPopup() {
        const order = this.get_order();
        const selected_orderline = order?.get_selected_orderline();

        if (!selected_orderline) {
            this.notification.add("Please select a product first!", { type: "warning" });
            return;
        }

        const selected_product = selected_orderline.get_product();
        const price_per_unit = selected_product.lst_price;

        if (!price_per_unit || price_per_unit <= 0) {
            this.notification.add("Invalid price for this product!", { type: "danger" });
            return;
        }

        const { confirmed, payload } = await this.popup.add(NumberPopup, {
            title: "Enter Amount (₹)",
            startingValue: "",
            confirmButtonLabel: "Confirm",
            isValid: (value) => !isNaN(value) && parseFloat(value) > 0,
            getPayload: (value) => value,
        });

        if (confirmed && payload) {
            const entered_amount = parseFloat(payload);
            const new_quantity = entered_amount / price_per_unit;

            selected_orderline.set_quantity(new_quantity);
            selected_orderline.set_unit_price(price_per_unit);

            order.trigger("change", { orderline: selected_orderline });
            console.log(`Updated Order Line: Qty = ${new_quantity}, Price = ${price_per_unit}`);
        }
    },
});
