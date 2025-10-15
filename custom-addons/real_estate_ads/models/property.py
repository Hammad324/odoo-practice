from odoo import fields, models, api, _

class Property(models.Model):
    _name = 'estate.property'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'website.published.mixin', 'website.seo.metadata'] #'mail.alias.mixin', 'utm.mixin'
    _description = 'Estate Property'

    name = fields.Char(string="Name", required=True)
    state = fields.Selection([
        ('new', 'New'),
        ('received', 'Offer Received'),
        ('accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('cancelled', 'Cancelled')
    ], string="Status", default='new')
    tag_id = fields.Many2many('estate.property.tag', string="Property Tag")
    type_id = fields.Many2one('estate.property.type', string="Property Type")
    description = fields.Text(string="Description")
    post_code = fields.Char(string="Postcode")
    date_availability = fields.Date(string="Date Available")
    expected_price = fields.Float(string="Expected Price", tracking=True)
    best_offer = fields.Float(string="Best Offer")
    selling_price = fields.Float(string="Selling Price")
    bedrooms = fields.Integer(string="Bedrooms")
    living_area = fields.Integer(string="Living Area")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage", default=False)
    garden = fields.Boolean(string="Garden", default=False)
    garden_area = fields.Integer(string="Garden Area")
    garden_orientation = fields.Selection([
        ('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')
    ], string="Garden Orientation", default='north')
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    sales_id = fields.Many2one('res.users', string="Salesman")
    buyer_id = fields.Many2one('res.partner', string="Buyer", domain=[("is_company", "=", True)])
    # domain is basically the WHERE clause in sql
    phone = fields.Char(string="Phone", related="buyer_id.phone")

# I will implement the onchange here.

    @api.onchange('living_area', 'garden_area')
    def _onchange_total_area(self):
        self.total_area = self.living_area + self.garden_area

    total_area = fields.Integer(string="Total Area")
    # in this case we do not have to point it to a field, it will automatically detect the change.
    # THIS ONLY WORKS IN FORM VIEW.

    # @api.depends('living_area', 'garden_area')
    # def _compute_total_area(self):
    #     for rec in self:
    #         rec.total_area = self.living_area + self.garden_area

    # total_area = fields.Integer(string="Total Area", compute=_compute_total_area)

    def accept_offer(self):
        self.state = 'sold'

    def reject_offer(self):
        self.state = 'cancelled'

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for rec in self:
            rec.offer_count = len(rec.offer_ids)

    offer_count = fields.Integer(string="Offer Count", compute="_compute_offer_count")

    def action_property_view_offers(self):
        return {
            'type': 'ir.actions.act_window',
            'name': f"{self.name} - Offers",
            'res_model': 'estate.property.offer',
            'domain': [('property_id', '=', self.id)],
            'view_mode': 'tree'
        }
        # we can either link a button to an action like this one or have a smart button. see line 42-44 of property_view.xml

    def action_url_action(self):
        return {
            'type': 'ir.actions.act_url',
            'url': 'https://odoo.com',
            'target': 'new' # => opens on a new window, similarly if used with self opens the page in the same page.
        }

    def _compute_website_url(self):
        for rec in self:
            rec.website_url = "/properties/%s" % rec.id

    #Testing Client Actions
    # def action_client_action(self):
    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'display_notification',
    #         'params': {
    #             'title': _('Testing client action'),
    #             'type': 'success',
    #             'sticky': False
    #         }
    #     }

    def _get_report_base_filename(self):
        self.ensure_one()
        return 'Estate Property - %s' % self.name

    def action_send_email(self):
        mail_template = self.env.ref('real_estate_ads.offer_mail_template')
        mail_template.send_mail(self.id, force_send=True)

    def _get_emails(self):
        return ','.join(self.offer_ids.mapped('partner_email'))

class PropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'

    name = fields.Char(string="Name", required=True)

class PropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Estate Property Tag'

    name = fields.Char(string="Name", required=True)
    color = fields.Integer(string="Color")
