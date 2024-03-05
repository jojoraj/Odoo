from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)

datas = [
{'external_id': '__export__.employee_admin', 'project': [150], 'skype_id': False, 'matricule': False} ,
{'external_id': '__export__.hr_employee_407', 'project': [102], 'skype_id': 'live:.cid.fa37f6eacad3bdf5', 'matricule': 'IGY084'} ,
{'external_id': '__export__.hr_employee_412_ef625778', 'project': [], 'skype_id': 'live:.cid.c4eac160b1decf26', 'matricule': 'IGY165'} ,
{'external_id': '__export__.hr_employee_6', 'project': [], 'skype_id': 'mravelon', 'matricule': 'IGY002'} ,
{'external_id': '__export__.hr_employee_424_7fa5ecbb', 'project': [], 'skype_id': False, 'matricule': 'IGY176'} ,
{'external_id': '__export__.hr_employee_393', 'project': [106], 'skype_id': 'Chris ANDRIAMANANA (The Rev)', 'matricule': 'IGY065'} ,
{'external_id': '__export__.hr_employee_218', 'project': [], 'skype_id': 'area-fyh', 'matricule': 'IGY012'} ,
{'external_id': '__export__.hr_employee_427_7c29d83e', 'project': [], 'skype_id': 'live:.cid.624600a6944085ab', 'matricule': 'IGY179'} ,
{'external_id': '__export__.hr_employee_394_64c870f4', 'project': [178, 175], 'skype_id': 'fredo.andrianaivo2', 'matricule': 'IGY150'} ,
{'external_id': '__export__.hr_employee_439', 'project': [91, 131], 'skype_id': 'live:.cid.a251dd23b42d1a57', 'matricule': 'IGY075'} ,
{'external_id': '__export__.hr_employee_416_ac8203a2', 'project': [107], 'skype_id': 'live:.cid.2bd27285a127ca41', 'matricule': 'IGY169'} ,
{'external_id': '__export__.hr_employee_426', 'project': [64], 'skype_id': 'live:miorandrianarisoa', 'matricule': 'IGY055'} ,
{'external_id': '__export__.hr_employee_418_5fad52c4', 'project': [107], 'skype_id': 'live:.cid.9d336f792be3d71d', 'matricule': 'IGY170'} ,
{'external_id': '__export__.hr_employee_426_21c84f8e', 'project': [], 'skype_id': False, 'matricule': 'IGY178'} ,
{'external_id': '__export__.hr_employee_367_8216c19c', 'project': [150], 'skype_id': 'live:.cid.f2af5d8205fcf519', 'matricule': 'IGY124'} ,
{'external_id': '__export__.hr_employee_454', 'project': [91, 126, 128, 31, 57, 72], 'skype_id': 'live:aromax.cris', 'matricule': 'IGY072'} ,
{'external_id': '__export__.hr_employee_347_8d72faa4', 'project': [56], 'skype_id': 'live:.cid.9bc3067004411ce8', 'matricule': 'IGY107'} ,
{'external_id': '__export__.hr_employee_318_498f15f0', 'project': [116], 'skype_id': 'l.andriamalala', 'matricule': 'IGY076'} ,
{'external_id': '__export__.hr_employee_387_e620b1bd', 'project': [150], 'skype_id': 'Patromeo12', 'matricule': 'IGY144'} ,
{'external_id': '__export__.hr_employee_329_588d032a', 'project': [131, 20, 104], 'skype_id': 'live:.cid.1bc63168ad492e75', 'matricule': 'IGY101'} ,
{'external_id': '__export__.hr_employee_392_d20c41b3', 'project': [107], 'skype_id': 'live:Patricia BETKOU ORTOLLI', 'matricule': 'IGY148'} ,
{'external_id': '__export__.hr_employee_384_fea9cfe3', 'project': [19], 'skype_id': 'live:.cid.1543e00cb45ce1c3', 'matricule': 'IGY142'} ,
{'external_id': '__export__.hr_employee_15', 'project': [], 'skype_id': False, 'matricule': False} ,
{'external_id': '__export__.hr_employee_418', 'project': [18, 127], 'skype_id': 'live:.cid.2cb0cbad53754bb1', 'matricule': 'IGY073'} ,
{'external_id': '__export__.hr_employee_414_9b1726e7', 'project': [108], 'skype_id': False, 'matricule': 'IGY166'} ,
{'external_id': '__export__.hr_employee_215', 'project': [23], 'skype_id': 'live:a7025b21816d3244', 'matricule': 'IGY027'} ,
{'external_id': '__export__.hr_employee_407_30cd90b6', 'project': [186], 'skype_id': 'live:.cid.caabae592c9ef5e1', 'matricule': 'IGY152'} ,
{'external_id': '__export__.hr_employee_327_08832ac1', 'project': [64], 'skype_id': 'live:hobisoua', 'matricule': 'IGY082'} ,
{'external_id': '__export__.hr_employee_385_f56741fd', 'project': [23], 'skype_id': 'live:harifidyilay', 'matricule': 'IGY141'} ,
{'external_id': '__export__.hr_employee_270', 'project': [31], 'skype_id': 'live:mmjjonah', 'matricule': 'IGY029'} ,
{'external_id': '__export__.hr_employee_395', 'project': [67], 'skype_id': 'live:mmjjonah', 'matricule': 'IGY067'} ,
{'external_id': '__export__.hr_employee_327', 'project': [25], 'skype_id': 'live:tsiavaherimamy', 'matricule': 'IGY037'} ,
{'external_id': '__export__.hr_employee_317', 'project': [106], 'skype_id': 'michaelrazfyxavier', 'matricule': 'IGY035'} ,
{'external_id': '__export__.hr_employee_423_1167a61a', 'project': [], 'skype_id': False, 'matricule': 'IGY175'} ,
{'external_id': '__export__.hr_employee_448', 'project': [], 'skype_id': 'njules5', 'matricule': 'IGY071'} ,
{'external_id': '__export__.hr_employee_358', 'project': [128, 77, 81], 'skype_id': 'live:thierryniaina.xa', 'matricule': 'IGY043'} ,
{'external_id': '__export__.hr_employee_444', 'project': [91, 67, 19, 57], 'skype_id': 'live:b19f740dda81dde3', 'matricule': 'IGY069'} ,
{'external_id': '__export__.hr_employee_383', 'project': [23], 'skype_id': 'live:andyrabearimanana', 'matricule': 'IGY058'} ,
{'external_id': '__export__.hr_employee_351_3e34c10d', 'project': [76], 'skype_id': 'live:etech-eddy', 'matricule': 'IGY110'} ,
{'external_id': '__export__.hr_employee_411_919ec883', 'project': [], 'skype_id': False, 'matricule': 'IGY152'} ,
{'external_id': '__export__.hr_employee_397_b2869cbd', 'project': [], 'skype_id': 'live:.cid.fb7e34e206c36d50', 'matricule': 'IGY158'} ,
{'external_id': '__export__.hr_employee_440', 'project': [20, 76, 104], 'skype_id': 'live:.cid.974dcbd5c37ce828', 'matricule': 'IGY088'} ,
{'external_id': '__export__.hr_employee_195', 'project': [116], 'skype_id': 'marienorosoa', 'matricule': 'IGY004'} ,
{'external_id': '__export__.hr_employee_7', 'project': [161], 'skype_id': 'live:.cid.203a381e66866eea', 'matricule': 'IGY003'} ,
{'external_id': '__export__.hr_employee_419_f21f88dd', 'project': [], 'skype_id': 'Mii Rindra RAHOLIARISOA', 'matricule': 'IGY171'} ,
{'external_id': '__export__.hr_employee_35', 'project': [69, 44], 'skype_id': 'narisandy', 'matricule': 'IGY015'} ,
{'external_id': '__export__.hr_employee_399_f4e8d588', 'project': [106], 'skype_id': 'live:.cid.66f477bd402db39f', 'matricule': 'IGY122'} ,
{'external_id': '__export__.hr_employee_354_945129ad', 'project': [], 'skype_id': False, 'matricule': 'IGY001'} ,
{'external_id': '__export__.hr_employee_383_9dd856c1', 'project': [20], 'skype_id': 'live:.cid.9447d44c57a295ab', 'matricule': 'IGY140'} ,
{'external_id': '__export__.hr_employee_285', 'project': [107], 'skype_id': 'live:187c7f67c4067c2f', 'matricule': 'IGY042'} ,
{'external_id': '__export__.hr_employee_413_a71ab79d', 'project': [], 'skype_id': 'Santatra Floyd', 'matricule': 'IGY164'} ,
{'external_id': '__export__.hr_employee_33', 'project': [102], 'skype_id': 'liva.admin', 'matricule': 'IGY005'} ,
{'external_id': '__export__.hr_employee_445', 'project': [66], 'skype_id': 'live:.cid.d85cff4d6597f1a1', 'matricule': 'IGY091'} ,
{'external_id': '__export__.hr_employee_307', 'project': [], 'skype_id': 'ellen.rakotoharivahoaka', 'matricule': 'IGY025'} ,
{'external_id': '__export__.hr_employee_321_41c1fdb2', 'project': [116], 'skype_id': 'live:c16b714e3e84f756', 'matricule': 'IGY078'} ,
{'external_id': '__export__.hr_employee_324_db6bf596', 'project': [81, 76, 148], 'skype_id': 'live:.cid.9dc6ceca06b80c3f', 'matricule': 'IGY098'} ,
{'external_id': '__export__.hr_employee_3', 'project': [47], 'skype_id': 'hasinandrina', 'matricule': 'IGY020'} ,
{'external_id': '__export__.hr_employee_319_168f55ab', 'project': [150, 126], 'skype_id': 'live:fahbruceroland', 'matricule': 'IGY097'} ,
{'external_id': '__export__.hr_employee_322_2ba60edf', 'project': [107], 'skype_id': 'live:.cid.faf33906c1c4c758', 'matricule': 'IGY079'} ,
{'external_id': '__export__.hr_employee_428_82839651', 'project': [], 'skype_id': 'Andry Fitahiana Natanaela Rakotonindrina', 'matricule': 'IGY180'} ,
{'external_id': '__export__.hr_employee_10', 'project': [31], 'skype_id': 'ralaivao.tina', 'matricule': 'IGY017'} ,
{'external_id': '__export__.hr_employee_400_c24bc0bd', 'project': [189], 'skype_id': 'live:toavinar', 'matricule': 'IGY 152'} ,
{'external_id': '__export__.hr_employee_268', 'project': [54, 16, 62], 'skype_id': 'andriamanaja.ramalanjaona', 'matricule': 'IGY034'} ,
{'external_id': '__export__.hr_employee_422_b21b74c1', 'project': [], 'skype_id': 'riantsoa sandratra', 'matricule': 'IGY174'} ,
{'external_id': '__export__.hr_employee_244', 'project': [23], 'skype_id': 'hajasram', 'matricule': 'IGY024'} ,
{'external_id': '__export__.hr_employee_430_e26fa258', 'project': [], 'skype_id': 'Fitahiana Ramarolahy', 'matricule': 'IGY182'} ,
{'external_id': '__export__.hr_employee_410_132e90e9', 'project': [], 'skype_id': 'live:haribenja', 'matricule': 'IGY161'} ,
{'external_id': '__export__.hr_employee_306', 'project': [23], 'skype_id': 'live:88cb750b07044b03', 'matricule': 'IGY056'} ,
{'external_id': '__export__.hr_employee_393_cc178e3b', 'project': [130], 'skype_id': 'iramarosata@ingenosya.mg', 'matricule': 'IGY149'} ,
{'external_id': '__export__.hr_employee_421_6c3d828e', 'project': [66, 184], 'skype_id': False, 'matricule': 'IGY173'} ,
{'external_id': '__export__.hr_employee_326_cf255ec5', 'project': [64], 'skype_id': 'live:dd97b8cccecc0949', 'matricule': 'IGY081'} ,
{'external_id': '__export__.hr_employee_342_ee595171', 'project': [130], 'skype_id': 'live:.cid.b70df2c156097249', 'matricule': 'IGY103'} ,
{'external_id': '__export__.hr_employee_73', 'project': [61], 'skype_id': 'ntsouh_rmh', 'matricule': 'IGY008'} ,
{'external_id': '__export__.hr_employee_216', 'project': [57], 'skype_id': 'live:45d160f423dbaf76', 'matricule': 'IGY028'} ,
{'external_id': '__export__.hr_employee_22', 'project': [77, 100], 'skype_id': 'live:setralink', 'matricule': 'IGY031'} ,
{'external_id': '__export__.hr_employee_432', 'project': [56, 7, 175, 91], 'skype_id': 'live:.cid.b67e5bb7e8708dfe', 'matricule': 'IGY087'} ,
{'external_id': '__export__.hr_employee_356_2541ad20', 'project': [76], 'skype_id': 'live:rihagatiana0', 'matricule': 'IGY114'} ,
{'external_id': '__export__.hr_employee_355_c6382dc2', 'project': [64], 'skype_id': 'live:.cid.c4983e0099d41998', 'matricule': 'IGY112'} ,
{'external_id': '__export__.hr_employee_43', 'project': [102], 'skype_id': 'gody.ranaivo', 'matricule': 'IGY022'} ,
{'external_id': '__export__.hr_employee_12', 'project': [47], 'skype_id': 'hoppy_o', 'matricule': 'IGY 013'} ,
{'external_id': '__export__.hr_employee_324', 'project': [45], 'skype_id': 'live:lovanirinamurelle', 'matricule': 'IGY036'} ,
{'external_id': '__export__.hr_employee_372_3c245da6', 'project': [168], 'skype_id': 'live:.cid.53d15bff7a72f43c', 'matricule': 'IGY129'} ,
{'external_id': '__export__.hr_employee_417_418a5fa5', 'project': [107], 'skype_id': 'live:.cid.b6197a0e881986e1', 'matricule': 'IGY168'} ,
{'external_id': '__export__.hr_employee_377', 'project': [46, 72], 'skype_id': 'njato.ferdi', 'matricule': 'IGY045'} ,
{'external_id': '__export__.hr_employee_331', 'project': [91, 103], 'skype_id': 'live:fe8eafc8d00714e7', 'matricule': 'IGY050'} ,
{'external_id': '__export__.hr_employee_420_2bedead5', 'project': [100], 'skype_id': 'live:jerrys_h.randriamire', 'matricule': 'IGY172'} ,
{'external_id': '__export__.hr_employee_339', 'project': [61, 79, 103, 32, 189], 'skype_id': 'live:ceomatkeomat', 'matricule': 'IGY052'} ,
{'external_id': '__export__.hr_employee_375_123b0dff', 'project': [104], 'skype_id': 'live:.cid.5770fedae0a5b8c9', 'matricule': 'IGY132'} ,
{'external_id': '__export__.hr_employee_316', 'project': [], 'skype_id': 'randrianirinaboniface', 'matricule': 'IGY033'} ,
{'external_id': '__export__.hr_employee_365_70941663', 'project': [150], 'skype_id': 'live:.cid.2dd6fd71152cd598', 'matricule': 'IGY123'} ,
{'external_id': '__export__.hr_employee_259', 'project': [47], 'skype_id': 't.randrianarisoa', 'matricule': 'IGY023'} ,
{'external_id': '__export__.hr_employee_363', 'project': [106], 'skype_id': 'sitraka_randria', 'matricule': 'IGY054'} ,
{'external_id': '__export__.hr_employee_429_262233e4', 'project': [], 'skype_id': 'Andriamalala Sitraka Rasatarivony', 'matricule': 'IGY181'} ,
{'external_id': '__export__.hr_employee_401_6edd8cec', 'project': [189], 'skype_id': 'rnh-nz', 'matricule': 'IGY153'} ,
{'external_id': '__export__.hr_employee_345_bb7965e1', 'project': [72], 'skype_id': 'live:.cid.64891f68dcaf8f6b', 'matricule': 'IGY105'} ,
{'external_id': '__export__.hr_employee_434', 'project': [116], 'skype_id': False, 'matricule': 'IGY060'} ,
{'external_id': '__export__.hr_employee_409_8cabedf7', 'project': [59], 'skype_id': 'darolla1', 'matricule': 'IGY162'} ,
{'external_id': '__export__.hr_employee_5', 'project': [], 'skype_id': 'ainnarh', 'matricule': 'IGY021'} ,
{'external_id': '__export__.hr_employee_359_6afe57be', 'project': [], 'skype_id': 'live:.cid.e40f41b9df87ff3b', 'matricule': 'IGY116'} ,
{'external_id': '__export__.hr_employee_355', 'project': [63, 72], 'skype_id': 'live:tokyratefinanahary97', 'matricule': 'IGY049'} ,
{'external_id': '__export__.hr_employee_425_6cf6ae1f', 'project': [], 'skype_id': False, 'matricule': 'IGY177'} ,
{'external_id': '__export__.hr_employee_410', 'project': [173, 128, 54, 15, 149, 184, 41, 121, 174], 'skype_id': 'toky.nirina23', 'matricule': 'IGY051'} ,
{'external_id': '__export__.hr_employee_85', 'project': [91, 103], 'skype_id': 'informadev', 'matricule': 'IGY011'} ,
{'external_id': '__export__.hr_employee_381', 'project': [], 'skype_id': 'lalaina.ratsiharovala', 'matricule': 'IGY048'} ,
{'external_id': '__export__.hr_employee_387', 'project': [], 'skype_id': 'live:d1e85179d3675a04', 'matricule': 'IGY063'} ,
{'external_id': '__export__.hr_employee_389_49315456', 'project': [104], 'skype_id': 'live:.cid.81c928eb928fd2ea', 'matricule': 'IGY146'} ,
{'external_id': '__export__.hr_employee_370', 'project': [153, 72], 'skype_id': 'live:e040e7f3822b4fe8', 'matricule': 'IGY044'} ,
{'external_id': '__export__.hr_employee_358_a998ac71', 'project': [150], 'skype_id': 'live:.cid.142d215077a93ad9', 'matricule': 'IGY115'} ,
{'external_id': '__export__.hr_employee_396_6d6ff664', 'project': [106], 'skype_id': 'live:f6592bc569c64b18', 'matricule': 'IGY157'} ,
{'external_id': '__export__.hr_employee_390_8a802f35', 'project': [], 'skype_id': 'live:.cid.febd4aa8c1502d14', 'matricule': 'IGY145'} ,
{'external_id': '__export__.hr_employee_395_08f0ec67', 'project': [], 'skype_id': 'aime.jean7', 'matricule': 'IGY151'} ,
{'external_id': '__export__.hr_employee_359', 'project': [150, 25, 144, 69, 131], 'skype_id': 'live:8b732a319f711043', 'matricule': 'IGY057'} ,
{'external_id': '__export__.hr_employee_28', 'project': [], 'skype_id': 'crazafimamonjy', 'matricule': 'IGY019'} ,
{'external_id': '__export__.hr_employee_381_2e4232f5', 'project': [175], 'skype_id': 'live:.cid.2eeafe843822e899', 'matricule': 'IGY138'} ,
{'external_id': '__export__.hr_employee_429', 'project': [116], 'skype_id': 'jerison.razafimandimby2', 'matricule': 'IGY059'} ,
{'external_id': '__export__.hr_employee_361_2bbaca75', 'project': [76], 'skype_id': 'live:.cid.a0697bc2b220d1c4', 'matricule': 'IGY117'} ,
{'external_id': '__export__.hr_employee_11', 'project': [], 'skype_id': 'yelandy', 'matricule': 'IGY016'} ,
{'external_id': '__export__.hr_employee_370_491754b3', 'project': [126, 128], 'skype_id': 'live:vazonzandriny', 'matricule': 'IGY127'} ,
{'external_id': '__export__.hr_employee_69', 'project': [], 'skype_id': 'ando.razanajatovo', 'matricule': 'IGY006'} ,
{'external_id': '__export__.hr_employee_156', 'project': [66, 54, 15, 184], 'skype_id': 'live:robelnicl', 'matricule': 'IGY007'} ,
{'external_id': '__export__.hr_employee_240', 'project': [189], 'skype_id': 'live:1b99b18dedc6188c', 'matricule': 'IGY030'} ,
{'external_id': '__export__.hr_employee_357_e3107b5f', 'project': [156], 'skype_id': 'live:.cid.62b73733b8e5003e', 'matricule': 'IGY113'} ,
{'external_id': '__export__.hr_employee_320_825923b2', 'project': [23], 'skype_id': 'nicolasrazanatsimba', 'matricule': 'IGY077'} ,
{'external_id': '__export__.hr_employee_394', 'project': [7, 138, 46], 'skype_id': 'live:f3acfed14dc3a41b', 'matricule': 'IGY066'} ,
{'external_id': '__export__.hr_employee_31', 'project': [22], 'skype_id': 'ale_ingeno', 'matricule': 'IGY009'} ,
{'external_id': '__export__.hr_employee_308', 'project': [], 'skype_id': False, 'matricule': 'IGY026'} ,
]


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def import_igy_employee_data(self):
        for data in datas:
            try:
                employee = self.env.ref(data['external_id'])
                employee.skype_id = data['skype_id']
                employee.matricule = data['matricule']
                for project_id in data['project']:
                    employee.project_ids = [(4, project_id)]
            except:
                _logger.warning(data['external_id']+' not found')

    @api.model
    def export_project(self):
        employee_json = {}
        employee_list = []
        employees = self.env['hr.employee'].search([('active', '=', True)])
        for employee in employees:
            external_id = self.env['ir.model.data'].search([('res_id', '=', employee.id), ('model', '=', 'hr.employee')], limit=1)
            employee_json['external_id'] = '__export__.'+external_id.name
            projects = employee.project_ids.mapped('id')
            employee_json['project'] = projects
            employee_json['skype_id'] = employee.skype_id
            employee_json['matricule'] = employee.matricule
            print(employee_json,',')
            employee_list.append(employee_json)

        with open('/home/brice/employee.txt', 'w+') as f:
            for employee in employee_list:
                # print(employee)
                f.write(str(employee)+',\n')