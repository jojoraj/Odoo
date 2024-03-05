from odoo import api, fields, models, _, registry, SUPERUSER_ID
import base64
import io
import csv
import xlrd
from odoo.addons.smile_impex.models.import_template import XLSDictReader
from datetime import datetime

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def open_import_leads_wizard(self):
        action = self.env.ref('smile_impex.action_imports').read()[0]
        action['res_id'] = self.env.ref('igy_import_crm.import_crm_lead_leads_template').id
        action['target'] = 'new'
        return action

    def open_import_opportunities_wizard(self):
        action = self.env.ref('smile_impex.action_imports').read()[0]
        action['res_id'] = self.env.ref('igy_import_crm.import_crm_lead_opportunities_template').id
        action['target'] = 'new'
        return action

    def open_import_tender_wizard(self):
        action = self.env.ref('smile_impex.action_imports').read()[0]
        action['res_id'] = self.env.ref('igy_import_crm.import_crm_lead_tender_template').id
        action['target'] = 'new'
        return action

    # Import file
    def check_file_type(self, template):
        reader = False
        if template and 'csv' in template.file_name:
            csv_file = base64.decodebytes(template.file).decode('utf-8-sig')
            csv_data = io.StringIO(csv_file)
            reader = csv.DictReader(csv_data, delimiter=';')

        elif template and 'xlsx' in template.file_name:
            excel_file = base64.decodebytes(template.file)
            reader = XLSDictReader(excel_file, 0)
        return reader

    # def import_crm_lead(self, *args, **kwargs):
    #     logger = self._context['logger']
    #     model_import_obj = self.env['ir.model.import.template']
    #     try:
    #         template = model_import_obj.browse(kwargs.get('template_id'))
    #         if not template:
    #             logger.error(_('There is nothing to import.'))
    #             return
    #         reader = self.check_file_type(template)
    #         if not reader:
    #             logger.error(_('There is nothing to import, Dict errors.'))
    #         import_current = template.import_ids[0]
    #         current_ligne = 1
    #         for row in reader :
    #             name = row.get('nom_entreprise')
    #             partner_id = False
    #             if name :
    #                 entreprise = self.env['res.partner'].search([('name', '=', name),('company_type','=','company')],limit=1)
    #                 if entreprise :
    #                     entreprise.website = row.get("site_web")
    #                     entreprise.phone = row.get("tel_entreprise")
    #                     entreprise.email = row.get("addresse_mail")
    #                     entreprise.snov = row.get("domaine_snov")
    #                     entreprise.ca = row.get("ca")
    #                     entreprise.personne = row.get("nb_personne")
    #                     entreprise.domaine = row.get('domaine_activite')
    #                     pays = self.env['res.country'].search([('name', '=',row.get('pays'))],limit=1)
    #                     if pays :
    #                         entreprise.country_id = pays.id
    #                     nom = row.get('nom')
    #                     if nom :
    #                         child = self.env['res.partner'].search([('name', '=', nom),('parent_id','=',entreprise.id)],limit=1)
    #                         if child :
    #                             child.name = nom
    #                             child.company_type = 'person'
    #                             child.website= row.get("lien_linkedin")
    #                             child.function= row.get("titre_entreprise")
    #                             child.client_title = row.get("titre",False)
    #                         else :
    #                             child = {}
    #                             child["name"] = nom
    #                             child["parent_id"] = entreprise.id
    #                             child["company_type"] = 'person'
    #                             child["website"] = row.get("lien_linkedin")
    #                             child["function"]= row.get("titre_entreprise")
    #                             child["client_title"] = row.get("titre",False)
    #                             try:
    #                                 self.env['res.partner'].sudo().create(child)
    #
    #                             except Exception as e:
    #                                 logger.error(repr(e))
    #                                 self._cr.rollback()
    #                     partner_id = entreprise
    #                 else :
    #                     societe = {}
    #                     societe["name"] = name
    #                     societe["website"] = row.get("site_web")
    #                     societe["company_type"] = 'company'
    #                     societe["phone"] = row.get("tel_entreprise")
    #                     societe["email"] = row.get("addresse_mail")
    #                     societe["snov"] = row.get("domaine_snov")
    #                     societe["ca"] = row.get("ca")
    #                     societe["personne"] = row.get("nb_personne")
    #                     societe["domaine"] = row.get('domaine_activite')
    #                     pays = self.env['res.country'].search([('name', '=',row.get('pays'))],limit=1)
    #                     if pays :
    #                         societe["country_id"] = pays.id
    #                     try:
    #                         res = self.env['res.partner'].sudo().create(societe)
    #                         partner_id = res
    #                         nom = row.get('nom')
    #                         if nom :
    #                             child = self.env['res.partner'].search([('name', '=', nom),('parent_id','=',res.id)],limit=1)
    #                             if child :
    #                                 child.name = nom
    #                                 child.company_type = 'person'
    #                                 child.website= row.get("lien_linkedin")
    #                                 child.function= row.get("titre_entreprise")
    #                             else :
    #                                 child = {}
    #                                 child["name"] = nom
    #                                 child["parent_id"] = partner_id
    #                                 child["company_type"] = 'person'
    #                                 child["website"] = row.get("lien_linkedin")
    #                                 child["function"]= row.get("titre_entreprise")
    #                                 try:
    #                                     self.env['res.partner'].sudo().create(child)
    #                                 except Exception as e:
    #                                     logger.error(repr(e))
    #                                     self._cr.rollback()
    #                     except Exception as e:
    #                             logger.error(repr(e))
    #                             self._cr.rollback()
    #             lead = {}
    #             lead["name"] = name
    #             lead["user_id"] = self.env.user.id
    #             lead["type"] = 'opportunity'
    #             lead["color"] = 8
    #             lead["stage_id"] = self.env.ref("igy_custom_crm.igy_qualification_marketting").id
    #             if lead.partner_id:
    #                 if lead.partner_id.country_id != self.env.ref('base.mg'):
    #                     if current_ligne <= 500:
    #                         lead['tag_ids'] = [(4, self.env.ref('igy_custom_crm.sdra_data').id)]
    #                     else:
    #                         lead['tag_ids'] = [(4, self.env.ref('igy_custom_crm.sdrb_data').id)]
    #                 else:
    #                     lead['tag_ids'] = [(4, self.env.ref('igy_custom_crm.sdr_local_data').id)]
    #
    #             try:
    #                 self.env['crm.lead'].sudo().create(lead)
    #             except Exception as e:
    #                 logger.error(repr(e))
    #                 self._cr.rollback()
    #             current_ligne += 1
    #     except Exception as e:
    #         logger.error(repr(e))
    #         self._cr.rollback()

    def import_crm_lead_tender(self, *args, **kwargs):
        with registry(self._cr.dbname).cursor() as new_cr:
            self = self.with_env(self.env(cr=new_cr))
            logger = self._context['logger']
            model_import_obj = self.env['ir.model.import.template']
            try:
                template = model_import_obj.browse(kwargs.get('template_id'))
                if not template:
                    logger.error(_('There is nothing to import.'))
                    self.send_notif_channel_bot_import("IMPORT ERREUR", "PAS DE FICHIER A IMPORTER")
                    return

                reader = self.check_file_type(template)
                if not reader:
                    logger.error(_('There is nothing to import, Dict errors.'))
                    self.send_notif_channel_bot_import("IMPORT ERREUR", "PAS DE FICHIER A IMPORTER")
                    return

                logger = logger or self._context['logger']
                index = 1
                errors = []
                lines = []
                all_reader_rows = []

                for line in self.check_file_type(template):
                    all_reader_rows.append(line)
                total_lines = len(all_reader_rows)

                for row in reader:
                    lead_obj = {
                        # 'source_id': self.manage_origin(row.get('Source', False)),
                        'name': row.get('Source', False) if row.get('Source') else False,
                        'ao_week': row.get('Semaine',False) if row.get('Semaine') else False,
                        'description': row.get('Description', False) if row.get('Description') else False,
                        'ao_link': row.get('Lien') if row.get('Lien') else False,
                        'ao_type': row.get('Type') if row.get('Type') else False,
                        'is_tender': True,
                        'stage_two_id': self.manage_stage_two_ids(row.get('Etape')) if row.get('Etape') else False,
                        'partner_id': self.manage_partner_id(
                            name=row.get('Source', False),
                            snov=False,
                            website=row.get('Lien', False),
                            phone=False,
                            mobile=False,
                            email=False,
                            domaine=False,
                            activity_info=False,
                            activity_ids=False,
                            ca=False,
                            cc=False,
                            activity=False,
                            address_type=False,
                            personne=False,
                            last_address=False,
                            update_address=False,
                            country_name=False,
                            child_name=False,
                            child_firstname=False,
                            child_website=False,
                            child_function=False,
                            child_title=False
                        ).id
                    }
                    country = row.get('Pays')
                    if country:
                        country_id = self.env['res.country'].search(
                            [('name', 'ilike', country)],
                            limit=1
                        )
                        if len(country_id.mapped('id')) > 0:
                            lead_obj['country_id'] = country_id.id

                    lead_res = self.env['crm.lead'].search(
                        [('name', '=', lead_obj["name"]),
                         ('ao_week', '=', lead_obj['ao_week']),
                         ('ao_type', '=', lead_obj['ao_type']),
                         ('description', '=', lead_obj["description"])],
                        limit=1
                    )
                    if lead_res:
                        try:
                            self.env['crm.lead'].sudo().write(lead_obj)
                        except ValueError as e:
                            self.send_notif_channel_bot_import(
                                "IMPORT ERREUR",
                                "Erreur d'écriture"
                            )
                            logger.error(repr(e))
                            errors.append((row, repr(e)))
                            self._cr.rollback()
                    else:
                        try:
                            self.env['crm.lead'].sudo().create(lead_obj)
                        except ValueError as e:
                            logger.error(repr(e))
                            errors.append((row, repr(e)))
                            self.send_notif_channel_bot_import(
                                "IMPORT ERREUR",
                                "Erreur d'écriture"
                            )
                            self._cr.rollback()

                    try:
                        logger.info(_('Import in progress ... %s lines treated.' % index))
                        lines.append(index)
                        if total_lines != 0:
                            percent_done = round((index * 100) / total_lines, -1)
                            logger.info(_('... %s percent done.' % percent_done))
                            template.write({
                                'import_progress': int(percent_done),
                                'line_treated': _("%s ligne(s) traitée(s) sur %s." % (index, total_lines)),
                            })

                        self._cr.commit()
                        index += 1
                    except ValueError as e:
                        logger.error(repr(e))
                        errors.append((row, repr(e)))
                        self._cr.rollback()

                logger.info(_('Import finished successfully.'))
                self.send_notif_channel_bot_import("IMPORTATION TERMINEE", "Importation terminée avec succès")

            except Exception as e:
                self.send_notif_channel_bot_import("IMPORT ERREUR", "Veuillez vérifier le fichier à importer.")
                logger.error(repr(e))
                errors.append((row, repr(e)))
                self._cr.rollback()

    def import_crm_lead(self, *args, **kwargs):
        with registry(self._cr.dbname).cursor() as new_cr:
            self = self.with_env(self.env(cr=new_cr))
            logger = self._context['logger']
            model_import_obj = self.env['ir.model.import.template']
            try:
                template = model_import_obj.browse(kwargs.get('template_id'))
                if not template:
                    logger.error(_('There is nothing to import.'))
                    self.send_notif_channel_bot_import("IMPORT ERREUR", "PAS DE FICHIER A IMPORTER")
                    return

                reader = self.check_file_type(template)
                if not reader:
                    logger.error(_('There is nothing to import, Dict errors.'))
                    self.send_notif_channel_bot_import("IMPORT ERREUR", "PAS DE FICHIER A IMPORTER")
                    return

                logger = logger or self._context['logger']
                index = 1
                sdr_index = 1
                errors = []
                lines = []
                all_reader_rows = []

                for line in self.check_file_type(template):
                    all_reader_rows.append(line)
                total_lines = len(all_reader_rows)
                for row in reader:
                    try:
                        lead_obj = {
                            'name': row.get('nom_opportunite', False),
                            'user_id': self.env.user.id,
                            'description': row.get('notes_internes', False) if row.get('notes_internes') else False,
                            'color': 8,
                            'stage_id': self.manage_stage_one_ids(row.get('etape_sdr')),
                            'stage_two_id': self.manage_stage_two_ids(row.get('etape_bdr')),
                            'is_bdr': self._context.get('import_bdr'),
                            'tag_ids': self.manage_tag_ids(row.get('etiquettes')),
                            'partner_id': self.manage_partner_id(
                                name=row.get('nom_entreprise', False),
                                snov=row.get('domaine_snov', False),
                                website=row.get('site_web', False),
                                phone=row.get('tel_entreprise', False),
                                mobile=row.get('numero', False),
                                email=row.get('adresse_mail', False),
                                domaine=row.get('domaine_activite', False),
                                activity_info=row.get('liste_activite_info', False),
                                activity_ids=row.get('liste_activite_info', False),
                                ca=row.get('ca_societe', False),
                                cc=row.get('code_communal', False),
                                activity=row.get('activites', False),
                                address_type=row.get('type_adresse', False),
                                personne=row.get('nb_personne', False),
                                last_address=row.get('ancienne_adresse', False),
                                update_address=row.get('maj_adresse', False),
                                country_name=row.get('pays', False),
                                child_name=row.get('nom', False),
                                child_firstname=row.get('prenom'),
                                child_website=row.get('lien_linkedin', False),
                                child_function=row.get('poste', False),
                                child_title=row.get('titre', False)
                            ).id,
                            'verif_nom': True if row.get('verif_nom', False) else False,
                            'created_date': self.manage_date(row.get('cree_le')),
                            'contact_linkedin': self.manage_date(row.get('contacte_linkedin_com')),
                            'contact_mail': self.manage_date(row.get('contacte_mailing_com')),
                            'contact_phone': self.manage_date(row.get('contacte_phoning_com')),
                            'source_id': self.manage_origin(row.get('origine', False)),
                            'medium_id': self.manage_medium(row.get('moyen', False)),
                            'contact': self.manage_igy_contact(row.get('contacte_par_ingenosya', False))
                        }
                        if self._context.get('import_sdr'):
                            lead_obj['type'] = 'lead'
                        if self._context.get('import_bdr'):
                            lead_obj['type'] = 'opportunity'
                        country = row.get('pays')
                        if country:
                            country_id = self.env['res.country'].search(
                                [('name', 'ilike', country)],
                                limit=1
                            )
                            if len(country_id.mapped('id')) > 0:
                                if country_id.id != self.env.ref('base.mg').id:
                                    sdr_index += 1
                                    if sdr_index <= 500:
                                        lead_obj['sdr_user'] = 'sdra'
                                    else:
                                        lead_obj['sdr_user'] = 'sdrb'
                                else:
                                    lead_obj['sdr_type'] = False

                        lead_res = self.env['crm.lead'].search(
                            [('name', '=', lead_obj["name"]),
                             # ('stage_id', '=', lead_obj["stage_id"])
                             ],
                            limit=1
                        )
                        if lead_res:
                            try:
                                lead_obj['stage_id'] = lead_res.stage_id.id
                                self.env['crm.lead'].sudo().write(lead_obj)
                            except ValueError as e:
                                self.send_notif_channel_bot_import(
                                    "IMPORT ERREUR",
                                    "Erreur d'écriture"
                                )
                                logger.error(repr(e))
                                errors.append((row, repr(e)))
                                self._cr.rollback()
                        else:
                            try:
                                self.env['crm.lead'].sudo().create(lead_obj)
                            except ValueError as e:
                                logger.error(repr(e))
                                errors.append((row, repr(e)))
                                self.send_notif_channel_bot_import(
                                    "IMPORT ERREUR",
                                    "Erreur d'écriture"
                                )
                                self._cr.rollback()

                        try:
                            logger.info(_('Import in progress ... %s lines treated.' % index))
                            lines.append(index)
                            if total_lines != 0:
                                percent_done = round((index * 100) / total_lines, -1)
                                logger.info(_('... %s percent done.' % percent_done))
                                template.write({
                                    'import_progress': int(percent_done),
                                    'line_treated': _("%s ligne(s) traitée(s) sur %s." % (index, total_lines)),
                                })

                            index += 1
                        except ValueError as e:
                            logger.error(repr(e))
                            errors.append((row, repr(e)))
                            self._cr.rollback()

                        self._cr.commit()

                    except Exception as e:
                        self.send_notif_channel_bot_import("IMPORT ERREUR", "Veuillez vérifier le fichier à importer.")
                        logger.error(repr(e))
                        errors.append((row, repr(e)))
                        self._cr.rollback()

                logger.info(_('Import finished successfully.'))
                self.send_notif_channel_bot_import("IMPORTATION TERMINEE", "Importation terminée avec succès")

            except Exception as e:
                logger.error(repr(e))
                self._cr.rollback()
                self.send_notif_channel_bot_import("IMPORT ERREUR", "Veuillez vérifier votre fichier excel")


    def manage_partner_id(self, name, address_type, website,  activity, activity_ids, activity_info, snov, phone, mobile, email, ca, cc, personne, domaine, country_name,
                          child_name, child_firstname, child_website, child_function, child_title, last_address, update_address):
        """
        this function is used for creating partner only
        """
        if name:
            partner_id = self.env['res.partner'].search(
                [('name', '=', name),
                 ('company_type', '=', 'company')],
                 limit=1
            )
            country_res = self.env['res.country'].sudo().search([('name', 'ilike', country_name)], limit=1)
            partner_obj = {
                'name': name if name else False,
                'type': 'contact',
                'company_type': 'company',
                'website': website if website else False,
                'phone': phone if phone else False,
                'mobile': mobile if mobile else False,
                'updated_address': update_address if update_address else False,
                'last_address': last_address if last_address else False,
                'snov': snov if snov else False,
                'email': email if email else False,
                'ca': ca if ca else False,
                'cc': cc if cc else False,
                'activity': str(int(activity)) if activity else False,
                'domaine': domaine if domaine else False,
                'activity_info': activity_info if activity_info else False,
                'personne': personne if personne else False,
                'country_id': country_res.id if country_res else False,
                'address_type': address_type if address_type else False,
                'res_activity_ids': self.manage_activity_ids(activity_ids) if activity_ids else False
            }
            if child_name:
                partner_obj['child_ids'] = [(5, 0, 0)] + [(0, 0, {
                    'name': child_name,
                    'firstname': child_firstname if child_firstname else False,
                    'company_type': 'person',
                    'email': email if email else False,
                    'phone': phone if phone else False,
                    'mobile': mobile if mobile else False,
                    'linkedin_link': child_website if child_website else False,
                    'function': child_function if child_function else False,
                    'client_title': child_title
                })]
            else:
                partner_obj['child_ids'] = False
            if partner_id:
                partner_id.sudo().write(partner_obj)
                return partner_id
            else:
                partner_created = self.env['res.partner'].create(partner_obj)
                return partner_created

    def manage_stage_two_ids(self, stage):
        try:
            stage_number = int(stage)
        except:
            stage_number = False
        if stage_number:
            if self._context.get('import_bdr') or self._context.get('import_tender'):
                if stage_number == 1:
                    return self.env.ref('igy_custom_crm.bdr_crm_qualif').id
                if stage_number == 2:
                    return self.env.ref('igy_custom_crm.bdr_crm_proposition').id
                if stage_number == 3:
                    return self.env.ref('igy_custom_crm.bdr_crm_offer_sent').id
                if stage_number == 4:
                    return self.env.ref('igy_custom_crm.bdr_crm_won').id
                if stage_number == 5:
                    return self.env.ref('igy_custom_crm.bdr_crm_lost').id
            else:
                return self.env.ref('igy_custom_crm.bdr_crm_qualif').id
        else:
            return self.env.ref('igy_custom_crm.bdr_crm_qualif').id

    def manage_stage_one_ids(self, stage):
        try:
            stage_number = int(stage)
        except:
            stage_number = False
        if stage_number:
            if self._context.get('import_sdr'):
                if stage_number == 1:
                    return self.env.ref('igy_custom_crm.igy_qualification_marketting').id
                elif stage_number == 2:
                    return self.env.ref('igy_custom_crm.igy_first_send').id
                elif stage_number == 3:
                    return self.env.ref('igy_custom_crm.igy_second_send').id
                elif stage_number == 4:
                    return self.env.ref('igy_custom_crm.igy_third_send').id
                elif stage_number == 5:
                    return self.env.ref('igy_custom_crm.igy_crm_won').id
                elif stage_number == 6:
                    return self.env.ref('igy_custom_crm.igy_crm_unqalified').id
                elif stage_number == 7:
                    return self.env.ref('igy_custom_crm.igy_crm_fail').id
                elif stage_number == 8:
                    return self.env.ref('igy_custom_crm.igy_fourth_send').id
                else:
                    return self.env.ref('igy_custom_crm.igy_qualification_marketting').id
            else:
                return self.env.ref('igy_custom_crm.igy_qualification_marketting').id
        else:
            return self.env.ref('igy_custom_crm.igy_qualification_marketting').id

    # def manage_child(self, name, parent_id, email, website, function, client_title):
    #     """
    #     this function update or create child partner in parent partner
    #     """
    #     child_res = self.env['res.partner'].sudo().search(
    #         [('company_type','=','person'),
    #          ('client_title','=',client_title),
    #          ('name','=',name),
    #          ('parent_id','=',parent_id)],
    #         limit = 1
    #     )
    #     child_object = {
    #         'name' : name if name else False,
    #         'company_type' : 'person',
    #         'email': email,
    #         'linkedin_link' : website,
    #         'function' : function,
    #         'client_title' : client_title,
    #         'parent_id' : parent_id
    #     }
    #     if child_res:
    #         child_res.write(child_object)
    #         return child_res
    #     else:
    #         child_created = self.env['res.partner'].sudo().create(child_object)
    #         return child_created

    def manage_origin(self, origin):
        if origin:
            origin_id = self.env['utm.source'].sudo().search(
                [('name','ilike',origin)],
                limit=1
            )
            if origin_id:
                return origin_id.id
            else:
                return self.env.ref('igy_custom_crm.utm_source_on_demand').id
        else:
            return self.env.ref('igy_custom_crm.utm_source_on_demand').id

    def manage_medium(self, medium):
        if medium:
            medium_id = self.env['utm.medium'].sudo().search(
                [('name','ilike',medium)],
                limit=1
            )
            if medium_id:
                return medium_id.id
            else:
                return self.env.ref('igy_custom_crm.utm_medium_on_demand').id
        else:
            return self.env.ref('igy_custom_crm.utm_medium_on_demand').id

    def manage_igy_contact(self, igy_contact):
        if igy_contact:
            return str(igy_contact).strip().lower()
        else:
            return 'non'

    def manage_date(self, date):
        if date:
            datetime_date = datetime(*xlrd.xldate_as_tuple(date, 0))
            return datetime_date

    def manage_tag_ids(self,tags):
        if tags:
            Tags = self.env['crm.lead.tag'].sudo().search([('name','like',tags)],limit=1)
            return [(4,Tags.id)] if Tags else False

    def send_notif_channel_bot_import(self, subject, body):
        odoo_bot = self.env['res.users'].browse(SUPERUSER_ID)
        channel_odoo_bot_users = '%s, %s' % (odoo_bot.name, self.env.user.name)
        channel_obj = self.env['mail.channel']
        channel_id = channel_obj.search([('name', 'like', channel_odoo_bot_users)])
        if not channel_id:
            channel_id = channel_obj.create({
                'name': channel_odoo_bot_users,
                'email_send': False,
                'channel_type': 'chat',
                'public': 'private',
                'channel_partner_ids': [(4, odoo_bot.partner_id.id), (4, self.env.user.partner_id.id)]
            })
        channel_id.message_post(
            subject=subject,
            body=body,
            message_type='comment',
            subtype='mail.mt_comment',
        )

    def manage_activity_ids(self, activity):
        if activity:
            activity_tab = []
            ActivityObjTab = []
            activity_split = activity.split(",")
            for activity_num in activity_split:
                activity_num = activity_num.strip()
                activity_tab.append(activity_num)
            if len(activity_tab) > 0:
                for activity_number in activity_tab:
                    try:
                        activity_number = int(activity_number)
                        Activity = self.env['res.partner.activity'].sudo().search([('color','=',activity_number)], limit=1)
                        if Activity:
                            ActivityObjTab.append(Activity.id)
                    except ValueError as ve:
                        # Handle the exception
                        print('Please enter an integer')
                        print(ve)
            if len(ActivityObjTab) > 0:
                return [(6, 0, ActivityObjTab)]
            else:
                return False
