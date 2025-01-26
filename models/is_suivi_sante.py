from odoo import models, fields, api # type: ignore

#TODO : 
# - Ajouter quantité d'alcool
# - Ajouter les calories depenses, abosdbées et l'écart
# - Ajouter jour de la semaine
# - Ajouter une valeur pour indiquer ma forme avec une note entre 1 et 5
# - Faire une requette pour avoir une valeur par ligne et par jour pour avoir pluseurs valeurs sur un même graphique
# - Mettre les objetifs dans la fiche de la société pour pouvoir les modifier
# - Calculer une note personnelle en fonction des différentes valeurs


class is_suivi_sante(models.Model):
    _name = 'is.suivi.sante'
    _description = "Suivi santé"
    _order = "name desc"
    _sql_constraints = [('name_uniq','UNIQUE(name)', 'Cette date existe déjà')] 

    name           = fields.Date(string="Date", required=True, index=True)
    poids          = fields.Float(string="Poids"        , digits=(12, 1))
    poids_objectif = fields.Float(string="Poids ojectif", digits=(12, 1), default=80)
    poids_ecart    = fields.Float(string="Poids écart"  , digits=(12, 1), store=True, compute='_compute_poids_ecart')

    fc_r           = fields.Integer(string="FC-R", help="Fréquence cardiaque au repos")
    fc_r_objectif  = fields.Integer(string="FC-R ojectif", default=70)
    fc_r_ecart     = fields.Integer(string="FC-R écart"  , store=True, compute='_compute_fc_r_ecart')

    fc_s           = fields.Integer(string="FC-S"       , help="Fréquence cardiaque pendant le sommeil")
    fc_s_objectif  = fields.Integer(string="FC-S ojectif"       , default=65)
    fc_s_ecart     = fields.Integer(string="FC-S écart", store=True, compute='_compute_fc_s_ecart')
    fc_s_dessus    = fields.Integer(string="FC-S dessus", help="%s Fréquence cardiaque pendant le sommeil au dessus de la fréquence cardiaque au repose")

    sommeil_profond = fields.Float(string="Sommeil profond")
    ronflement      = fields.Float(string="Ronflement")

    vfc             = fields.Integer(string="VFC", help="Variabilité de la FC en ms")
    vfc_objectif    = fields.Integer(string="VFC ojectif", default=35)
    vfc_ecart       = fields.Integer(string="VFC écart"  , store=True, compute='_compute_vfc_ecart')

    commentaire    = fields.Text(string="Commentaire")


    @api.depends('poids','poids_objectif')
    def _compute_poids_ecart(self):
        for obj in self:
            obj.poids_ecart=obj.poids - obj.poids_objectif

    @api.depends('fc_r','fc_r_objectif')
    def _compute_fc_r_ecart(self):
        for obj in self:
            obj.fc_r_ecart=obj.fc_r - obj.fc_r_objectif

    @api.depends('fc_s','fc_s_objectif')
    def _compute_fc_s_ecart(self):
        for obj in self:
            obj.fc_s_ecart=obj.fc_s - obj.fc_s_objectif

    @api.depends('vfc','vfc_objectif')
    def _compute_vfc_ecart(self):
        for obj in self:
            obj.vfc_ecart = obj.vfc_objectif - obj.vfc

