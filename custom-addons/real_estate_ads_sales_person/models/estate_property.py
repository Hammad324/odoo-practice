from odoo import models, fields, api
from odoo.exceptions import ValidationError

from odoo.odoo.tools import file_open_temporary_directory


class EstateProperty(models.Model):
    _inherit = 'estate.property'

    sales_id = fields.Many2one("res.users", required=True)

    # now we will rewrite the model_create_multi method
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            sales_person_property_ids = self.env[self._name].search_count([("sales_id", "=", vals.get("sales_id"))])
            if sales_person_property_ids >= 2:
                raise ValidationError("A user cannot have more than 2 properties.")
        return super(EstateProperty, self).create(vals_list)
    # we should not be assigning more than one property to the user.