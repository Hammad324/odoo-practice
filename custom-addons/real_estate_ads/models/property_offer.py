from odoo import fields, models, api
from datetime import timedelta
from odoo.exceptions import ValidationError

# Abstract, Transient and Regualr models.
# class AbstractOffer(models.AbstractModel):
#     _name = 'abstract.model.offer'
#     _description = 'Abstract Offers'
#
#     partner_email = fields.Char(string="Partner Email")
#     phone = fields.Char(string="Phone")

# class TransientOffer(models.TransientModel):
    # transient is a wizard model, meaning its data is not meant to be stored permanently in the databases
    # _name = 'transient.model.offer'
    # _description = 'Transient Offers'
    # _transient_max_count = 0 # this is used to determine the number of transient records in the db.
    # _transient_max_hours = 0
    # You can set a certain time for which the record
    # exist or when left to zero the system decides the time

    # @api.autovacuum
    # def transient_vacuum(self): # we can unlink old records with this method.

    # partner_email = fields.Char(string="Partner Email")
    # phone = fields.Char(string="Phone")

class PropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offers'

    @api.depends("partner_id", "property_id")
    def _compute_name(self):
        for rec in self:
            if rec.property_id and rec.property_id:
                rec.name = f"{rec.partner_id.name} - {rec.property_id.name}"
            else:
                rec.name = False

    name = fields.Char('Property Name', compute="_compute_name")
    price = fields.Float(string='Price')
    status = fields.Selection([
        ('accepted', 'Accepted'), ('refused', 'Refused')],
        string="Status")
    partner_id = fields.Many2one('res.partner', string='Customer') # change customer to partner
    partner_email = fields.Char(string='Customer Email Address', related='partner_id.email')
    property_id = fields.Many2one('estate.property', string='Property')
    validity = fields.Integer(string='Validity')
    deadline = fields.Date(string='Deadline', compute='_compute_deadline', inverse="_inverse_deadline")

    # this decorator is a model based decorator, it does not depend on a single record,
    # for example we want to print something when a change happens in the model this is where
    # we will use this decorator paired with a function.
    # @api.model
    # def _creation_date_default(self):
    #     return fields.Date.today()

    # _sql_constraints = [
    #     ('check_validity', "check(validity > 0)", "Deadlines cannot be before creation dates.")
    # ] # Enforced even outside Odoo, at the database level (strong data integrity), to inflict them we will have to reinstall the module.

    creation_date = fields.Date(string='Creation Date')

    @api.depends('validity', 'creation_date') # for depends we use fields that are available.
    # @api.depends_context('uid') # we use valid keys that are in the context dictionary. (Recompute when environment context key changes)
    def _compute_deadline(self):
        # print(self.env.context)
        # print(self._context)
        for rec in self:
            if rec.creation_date and rec.validity:
                rec.deadline = rec.creation_date + timedelta(days=rec.validity)
            else:
                rec.deadline = False

    def _inverse_deadline(self): # inverse is triggered when you save a record.
        for rec in self:
            if rec.deadline and rec.creation_date:
                rec.validity = (rec.deadline - rec.creation_date).days
            else:
                rec.validity = False
# the onchange only works in the form view. So decide if you want to use onchange or depend decorators.

    def extend_offer_deadline(self):
        activ_ids = self._context.get('active_ids', [])
        # print(activ_ids)
        if activ_ids:
            offer_ids = self.env['estate.property.offer'].browse('activ_ids')
            for offer in offer_ids:
                offer.validity = 10
                # or offer.write({'validity':10}) // better way

    def _extend_offer_deadline(self):
        offer_ids = self.env['estate.property.offer'].search([])
        for offer in offer_ids:
            offer.validity += 1

    def action_accept_offer(self):
        if self.property_id:
            self._validate_accepted_offer()
            self.property_id.write({
                'selling_price': self.price,
                'state': 'accepted'
            })
        self.status = 'accepted'

    def _validate_accepted_offer(self): # checks if the offer has been accepted before.
        offer_ids = self.env['estate.property.offer'].search([
            ('property_id', '=', self.property_id.id),
            ('status', '=', 'accepted'),
        ])
        if offer_ids:
            raise ValidationError("You have an accepted offer already")

    def action_decline_offer(self):
        self.status = 'refused'
        if all(self.property_id.offer_ids.mapped('status')):
            self.property_id.write({
                'selling_price': 0,
                'state': 'received'
            })

# this cron job runs every day and with this function it will clear all the offers whose status is refused.
#     @api.autovaccum
#     def _clearn_offers(self):
#         self.search([('status', '=', 'refused')]).unlink()

# @api.model_create_multi
# def create(self, vals):
#     for rec in vals:
#         if not rec.get('creation_date'):
#             rec["creation_date"] = fields.Date.today()
#     return super(PropertyOffer, self).create(vals)

# this decorator puts in a creation date if none is in the record.
# super() = access the parent class’s method.
# (PropertyOffer, self) = tell it which class’s parent to look up and which instance to operate on.
# .create(vals) = call the original create() with your modified data.

#api.depends_context decorator can be used alone or with @api.depends as well.

    @api.constrains('validity') # sets a constraint that a certain value cannot go above or below a certain threshold.
    def _check_validity(self):
        for rec in self:
            if rec.deadline <= rec.creation_date:
                raise ValidationError("Deadlines cannot be before creation dates.")

    # ORM Methods #
    def write(self, vals):
        print(vals) # the values which have been changed.
        # res_partner_ids = self.env['res.partner'].search([(
        #     'is_company', "=", True
        # )]) # fetches partners that are in a company
        # res_partner_ids = self.env['res.partner'].search_count([
        #     ('is_company', "=", True)
        # ])  # search_count returns the number of records that matches the domain. // 8
        # res_partner_ids = self.env['res.partner'].browse([10, 14]) # fetches the following partners
        # res_partner_ids = self.env['res.partner'].browse(14) # fetches the single partners // Azure Interior
        res_partner_ids = self.env['res.partner'].search([
            ('is_company', "=", True),
        ]).filtered(lambda x: x.phone == '(870)-931-0505') # res.partner(14,)
        print(res_partner_ids)
        # print(res_partner_ids.name)
        return super(PropertyOffer, self).write(vals)

    # {'price': 23}
    # res.partner(14, 10, 11, 15, 12, 13, 9, 1)

# .unlink()
# .mapped()
# .filtered()
# with lambda we only get one record set.

