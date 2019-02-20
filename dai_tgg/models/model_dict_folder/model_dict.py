 # -*- coding: utf-8 -*-
 #Copy tu internal ham import _thu_vien
from odoo.exceptions import UserError
import datetime

# from odoo.addons.dai_tgg.models.model_dict_product import gen_product_model_dict
# from odoo.addons.dai_tgg.models.model_dict_user_department import gen_user_department_model_dict
# print ('***',type(product_model_dict))
# class self():
#     pass

# from odoo.addons.dai_tgg.models.model_dict_folder.model_dict_product import gen_product_model_dict
from odoo.addons.dai_tgg.models.model_dict_folder.model_dict_user_department import gen_user_department_model_dict
from odoo.addons.dai_tgg.models.model_dict_folder.model_dict_tvcv import  gen_tvcv_model_dict
import re
from odoo.addons.dai_tgg.mytools import pn_replace
 
all_key_tram = 'all_key_tram'
key_ltk_dc = 'key_ltk_dc'
key_ltk_dc2 = 'key_ltk_dc2'
key_tti_dc = 'key_tti_dc'
key_137 = 'key_137'
write_xl = 'write_xl'
sml = 'sml'
key = 'key',
required = 'required'
# product = 'key_tti_dc_product'


def lot_name_key_ltk_dc_(val,needdata,self):
#     p_id = needdata['vof_dict']['product_id']['val']
#     product_id = self.env['product.product'].browse(p_id)
    product_id = needdata['vof_dict']['product_id']['obj']
    lot_name = needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] or (needdata['vof_dict']['barcode_for_first_read']['val'] and  ('use barcode ' + needdata['vof_dict']['barcode_for_first_read']['val']))
#     if lot_name== UBC:
#         lot_name= lot_name + str(int(needdata['vof_dict']['stt']['val']))
    if  (lot_name ==False and  product_id.tracking=='serial'):
#         raise UserError(u'kkkkk')
        lot_name = 'unknown ' + product_id.name + '  ' + str(int(needdata['vof_dict']['stt']['val']) )
        
    return lot_name



def last_record_function_ltk_vtdc_(n,self=None):
#     if not self.mode_no_create_in_main_instance:
    if n['vof_dict']['product_id']['get_or_create']== False:
        raise UserError(u'Product %s  phải được tạo từ trước'%n['vof_dict']['product_id']['fields']['name']['val'])
    gan_inventory_id_vao_needdata(n,self)
def gan_inventory_id_vao_needdata(n,self):
    if n['vof_dict']['inventory_id']['val'] and  not n.get('inventory_id'):
        n['inventory_id'] = n['vof_dict']['inventory_id']['val']
def last_import_function_(n,self):
    self.inventory_id = n['inventory_id']
def convert_float_location_(v,n):
#     return v
    if isinstance(v, float):
        v= str(int(v))
    if  v != False and isinstance(v, int):
        v = str(v)
    return v
def func_pre_func_location_id_1_ltk_dp_xfp_(v,n,self):
    if  n['sheet_name']== u'XFP, SFP các loại':
        return u'Phòng máy 3'
    else:
        return v
def convert_float_to_ghi_chu_cho_sml_ngay_xuat(val):
    if isinstance(val, float):
        seconds = (val - 25569) * 86400.0
        try:
            val= datetime.datetime.utcfromtimestamp(seconds).strftime('%d/%m/%Y')
        except ValueError:# year is out of range
            pass
    return val 

def convert_float_to_ghi_chu_cho_sml_ngay_xuat_2(val):
    if isinstance(val, float):
        seconds = (val - 25569) * 86400.0
        val= datetime.datetime.utcfromtimestamp(seconds).strftime('%d/%m/%Y')
    return val 



def name_of_uom_id_(v,n):
    v = u'Cái' if n['sheet_name']== u'XFP, SFP các loại' else v
    if isinstance(v,str):
        v = v.capitalize()
    return v
def uom_id_137_(v,n):
    if isinstance(v,str):
        v = v.capitalize()
    else:
        v = u'Cái'
    return v
    

SHEET_CONVERT = {'TTI':{u'CHUYỂN MẠCH':u'Chuyển Mạch (IMS, Di Động)',u'IP':u'IP (VN2, VNP)',u'TRUYỀN DẪN':u'Truyền dẫn',u'GTGT': u'GTGT',u'VÔ TUYẾN' :u'Vô tuyến'}}
SHEET_CONVERT_2_BC = {u'Chuyển Mạch (IMS, Di Động)':u'Chuyển mạch',u'IP (VN2, VNP)':u'IP'}


def categ_id_tti_convert_to_ltk_(v,n,tram=None):
#         raise UserError('kdkfasdlkfjld')
    v =  n['sheet_name']
    tram_dict = SHEET_CONVERT.get(tram)
    if tram_dict:
        categ_theo_ltk =  tram_dict.get(v,v)
        return categ_theo_ltk
#         categ_theo_bc = 
    else:
        return v
    
###them self

def location_from_key_tram(v,n,self):
    key_tram = n['key_tram']
    key_tram_split = key_tram.split('_')
    tram = key_tram_split[1]
    if 'dc'  in key_tram:
        stock_location_name = tram +u' đang chạy'
    else:
        stock_location_name = tram +u' dự phòng'
    
    stock_location_id =  self.env['stock.location'].search([('name','=ilike',stock_location_name)])
    if not stock_location_id:
        raise UserError ( u' Không tồn tại stock_location ')
    return stock_location_id
def look_department_from_key_tram_(v,n,self):
    key_tram = n['key_tram']
    key_tram_split = key_tram.split('_')
    tram = key_tram_split[1]
    stock_location_id =  self.env['hr.department'].search([('name','ilike',tram)])
    return stock_location_id.id
    
def location_goc_(v,n,self):
    return location_from_key_tram(v,n,self).id

def check_location_id_is_same_in_bb_(val,obj,needdata,self):
#     location_id_goc = n['vof_dict']['location_id_goc']['obj']
    if obj:
        if obj != self.location_id:
#             print ('aaaa',obj,self.location_id,obj.name,self.location_id.name)
#             raise UserError(u'xl Trạm Location different with stock picking location')
            raise UserError(u'Kho nguồn ở file excel khác với kho nguồn ở biên bản ')
def check_if_your_depart_of_lc_goc_(val,obj,needdata,self):
    if obj:
        if obj.department_id != self.env.user.department_id:
                raise UserError(u'Kho kiểm kê không thuộc đơn vị của bạn')
def check_if_your_department_in_location_1_2_3_4_5_(v,o,n,self):
#     if not self.user_has_groups('base.group_erp_manager'):
        if v != n['department_id']:
            raise UserError (u'với users role,Muốn tạo  hay get địa điểm điều chuyển con của địa điểm gốc, thì department_id phải giống với user.department_id')
def prepare_func_(n,self):
#     raise UserError(u'kkaka')
    n['department_id'] =  self.env.user.department_id.id
    
def check_location_id_is_same_in_bb_dc_(val,obj,needdata,self):
#     location_id_goc = n['vof_dict']['location_id_goc']['obj']
    if obj:
#         if obj.department_id != self.env.user.department_id:
        if obj != self.location_dest_id:
            raise UserError(u'Kho đích trong excel không bằng  kho đích trong biên bản')
        
    
def location_goc_sml_(v,n,self):
    if v == False:
        return self.location_id.id
    else:
        return v
        
def choose_inventory_id_name(v,n,self):
    stock_location_id = location_from_key_tram(v,n,self)
    return stock_location_id.name + '-' +  ','.join(n['sheet_names'])

def choose_inventory_id_name_for_mode(v,n,self):
#     stock_location_id = location_from_key_tram(v,n,self)
    if not n.get('inventory_id_save') :
        stock_location_id_name = n['vof_dict']['location_id_goc']['obj'].name
        return stock_location_id_name + '-' +  ','.join(n['sheet_names'])
    else:
        return False


# end Copy tu internal ham import _thu_vien

#copy ngoai
def convert_integer(val,needdata):
    try:
        return int(val)
    except:
        return 0
def qty_(val,n):
    if val:
        val = float(int(val))
        val=  1.0 if  (n['vof_dict']['prod_lot_id_excel_readonly']['val'] and val > 1) else val
    return val

# def qty_key_ltk_(val,n,self):
#     
#     if val:
#         val = float(int(val))
#         val=  1.0 if  (n['vof_dict']['prod_lot_id_excel_readonly']['val'] and val > 1) else val
#     return val


def qty_137_(val,n):
    if val !=0:
        val =1
    return val


def stt_(v,n):
#     if v == False:
#         return v
    if isinstance(v, str):
        try:
            v = int(v)
            return v
        except :
            return False
    else:
        return v
    
def tinh_trang_(v,n):
    if v ==None or v ==u'Tốt' or v==u'tot' or v ==False:
        return u'tot'
    else:
        return u'hong'
def ghi_chu_cho_sml_(v,n,self):
    if getattr(self, 'allow_cate_for_ghi_chu',False):
        return n.get('cate',False)#n['cate']#
    else:
        return v
# def name_replace_(v,n,self):
#     v = n['vof_dict']['prod_lot_id']['fields']['pn_id']['fields']['name']['val'] 
#     print ('val****',v)
#     if isinstance(v,str):
#         v = re.sub('[-_ \s]','',v)
#     return v
# def ghi_chu_cho_sml_cate_all_key_tram_(v,n,self):
#     if True:#getattr(self, 'allow_cate_for_ghi_chu',False):
#         return n.get('cate',False)
#     else:
#         return False
    
    
def pn_replace_(v,n,self):
    v = n['vof_dict']['product_id']['fields']['pn']['val'] 
    if isinstance(v,str):
        v = pn_replace(v)
#         v = re.sub('[-_ \s]','',v)
    
    return v
def product_id_(v,n,self):
    if v==False:
        v = n['vof_dict']['product_id']
        v = v.get('val',False)
    return v
def break_condition_func_for_main_instance_(needdata):
    needdata ['cate'] = needdata['vof_dict']['product_id_name_readonly']['val']
def tracking_write_func_(**kargs):
#     searched_object = kargs['searched_object']
#     f_name =  kargs['f_name']
    val =  kargs['val']
    if val =='none':
        return 'continue'
# def location_id_sml_(self):
#     product_id = 
#     return self.location_id.id

    

def prod_lot_id_excel_readonly_for_search_(v,n,self):
    prod_lot_id_excel_readonly_name = n['vof_dict']['prod_lot_id_excel_readonly']['val']
    if prod_lot_id_excel_readonly_name:
        prod_lot_id_excel_readonly_for_search = self.env['stock.production.lot'].search([('name','=',prod_lot_id_excel_readonly_name)])
        return prod_lot_id_excel_readonly_for_search
    else:
        return False
# def product_id_excel_readonly_for_search_(v,n,self):
#     product_id_name_readonly = n['vof_dict']['product_id_name_readonly']['val']
#     if product_id_name_readonly:
#         prod_lot_id_excel_readonly_for_search = self.env['product.product'].search([('name','=',product_id_name_readonly),('pn','=',False)])
#         if len(prod_lot_id_excel_readonly_for_search)==1:
#             return prod_lot_id_excel_readonly_for_search
#     return False
    
# def set_val_instead_loop_fields_(n,self):
#     prod_lot_id_excel_readonly_for_search = n['vof_dict']['prod_lot_id_excel_readonly_for_search']['val']
#     if prod_lot_id_excel_readonly_for_search:
#         product_id = prod_lot_id_excel_readonly_for_search.product_id
#         uom_id = product_id.uom_id.id
#         print ('***uom_id***',uom_id)
#         n['vof_dict']['product_id']['fields']['uom_id']['val'] = uom_id
#         return product_id.id
#     else:
#         return None
# def set_val_instead_loop_fields_prod_lot_id_(n,self):
#     prod_lot_id_excel_readonly_for_search = n['vof_dict']['prod_lot_id_excel_readonly_for_search']['val']
#     if prod_lot_id_excel_readonly_for_search:
# #         product_id = prod_lot_id_excel_readonly_for_search.product_id
# #         uom_id = product_id.uom_id.id
# #         print ('***uom_id***',uom_id)
# #         n['vof_dict']['product_id']['fields']['uom_id']['val'] = uom_id
#         return prod_lot_id_excel_readonly_for_search.id
#     else:
#         return None
def exist_val_before_loop_fields_func_pr_id_(n,self): 
    prod_lot_id_excel_readonly_for_search = n['vof_dict']['prod_lot_id_excel_readonly_for_search']['val']
    if prod_lot_id_excel_readonly_for_search:
        return prod_lot_id_excel_readonly_for_search.product_id
    else:
        return False
def exist_val_before_loop_fields_func_pr_id_2_(n,self):
    product_id_excel_readonly_for_search = n['vof_dict']['product_id_excel_readonly_for_search']['val']
    if product_id_excel_readonly_for_search:
        return product_id_excel_readonly_for_search
    else:
        return False
    
def exist_val_before_loop_fields_func_lot_id_(n,self): 
    prod_lot_id_excel_readonly_for_search = n['vof_dict']['prod_lot_id_excel_readonly_for_search']['val']
    if prod_lot_id_excel_readonly_for_search:
        return prod_lot_id_excel_readonly_for_search
    else:
        return False
    
    
    
def check_excel_obj_is_exist_func_(get_or_create,obj,exist_val):
    if not get_or_create:
        raise UserError(u'lot_id: %s đã có nhưng lại tạo product_id')
    else:
        if exist_val not in obj:
            raise UserError(u'search obj (%s,%s) != exist_val (%s,%s)'%(obj.name,obj.pn, exist_val.name,exist_val.pn))
# def check_exist_val_before_loop_fields_func(n,self,get_or_create):
#     if get_or_create:
#         raise UserError(u'product in excel khách với lot_id.product')
#     else:
#         prod_lot_id_excel_readonly_for_search = n['vof_dict']['prod_lot_id_excel_readonly_for_search']['val']
#         return prod_lot_id_excel_readonly_for_search.product_id.id
    
def product_uom_id_(v,n,self):
    pr_id = n['vof_dict']['product_id']['val']
    uom_id = self.env['product.product'].browse(pr_id ).uom_id.id
    return uom_id
        
def product_id_name_(v,n,self):
    v= n['vof_dict']['product_id_name_readonly']['val']
    v = str(int(v)) if  isinstance(v, float) else v
    return v
def search_func_(model_dict,self,exist_val,setting):
#     exist_val = search_func_para.get('exist_val')
    cho_phep_empty_pn_tuong_duong_voi_pn_duy_nhat = setting['cho_phep_empty_pn_tuong_duong_voi_pn_duy_nhat']
    cho_phep_co_pn_cap_nhat_empty_pn = setting['cho_phep_co_pn_cap_nhat_empty_pn']
#     print ('**model_dict',model_dict)
    name =  model_dict['fields']['name']['val']
    pn_replace = model_dict['fields']['pn_replace']['val']
    if not pn_replace:
#         if exist_val:
#             pr = self.env['product.product'].search([('name','=',name)])
#             return pr
#         else:
        pr = self.env['product.product'].search([('name','=',name),('pn','=',False)])
        if pr:
            return pr
        if cho_phep_empty_pn_tuong_duong_voi_pn_duy_nhat:
            pr = self.env['product.product'].search([('name','=',name)])
            if len(pr)==1 :
                return pr
        return False
    else:
        pr = self.env['product.product'].search([('pn_replace','=',pn_replace)])
        if pr:
            return pr
        if cho_phep_co_pn_cap_nhat_empty_pn:
            pr = self.env['product.product'].search([('name','=',name),('pn','=',False)])
            if pr:
                return pr
        return False
    
        
        
        
#     print ('**model_dict name',)
#     print ('**model_dict name',)
#     if pn_replace:
#     pr = self.env['product.product'].search([('name','=',name),('pn','=',False)])
#     if pr:
#         return pr
#     if not pn_replace:
#         pr = self.env['product.product'].search([('name','=',name)])
#         if len(pr)==1:
#             return pr
        
        
def location_id5_chua_ro_(v,needdata,self):    
    v_all = needdata['vof_dict']['location_id5']['val'] \
                or needdata['vof_dict']['location_id4']['val'] or \
                needdata['vof_dict']['location_id3']['val'] or \
                needdata['vof_dict']['location_id2']['val'] or \
                needdata['vof_dict']['location_id1']['val']
    if  v_all ==False:
        return u'Chưa rõ'
    else:
        return False
def or_7_location_id_(v,needdata):
    return needdata['vof_dict']['location_id6'].get('val') or \
                needdata['vof_dict']['location_id5']['val'] or \
                needdata['vof_dict']['location_id4']['val'] or \
                needdata['vof_dict']['location_id3']['val'] or \
                needdata['vof_dict']['location_id2']['val'] or \
                needdata['vof_dict']['location_id1']['val'] or \
                needdata['vof_dict']['location_id_goc']['val']

def location_id_for_sml_(v,n,self):
    lc_id =  or_7_location_id_(v,n)
    if lc_id == False:
        return self.location_id.id
    else:
        return lc_id
#     product_id = n['vof_dict']['product_id']['val']
#     prod_lot_id = n['vof_dict']['prod_lot_id']['val']
#     quants = self.env['stock.quant'].search([('product_id','=',product_id),('lot_id','=',prod_lot_id),('location_id','child_of',self.location_id.id),('quantity','>',0)])
#     if quants:
#         return quants.location_id.id
#     else:
#         return self.location_id.id
    
def inv_id_(v,n,self,import_from_inventory=None):       
#     raise UserError(self._context.get('import_from_inventory'))
#     raise UserError("self._context.get('not_last_import_function') %s"%self._context.get('not_last_import_function'))
    if  import_from_inventory:
        return self.id
    return n.setdefault('inventory_id_save',v)


    if not n.get('inventory_id_save'):
        n['inventory_id_save'] = v
        return v
    else:
        return n.get('inventory_id_save')
def department_for_sml_and_mode2_(v,n,self):
    return self.env['stock.location'].browse(n['vof_dict']['location_id_goc']['val']).department_id.id
#     return n['vof_dict']['location_id_goc']['obj'].department_id.id

def sheet_for_ltk_(self,wb,mode):
    if mode ==u'1':
        return [u'Truyền dẫn',u'IP (VN2, VNP)',u'GTGT',u'Chuyển Mạch (IMS, Di Động)',u'Vô tuyến',u'XFP, SFP các loại']if not self.sheet_name else [self.sheet_name]
    else:
        sheet_name = getattr(self, 'sheet_name',None)
        if sheet_name ==u'all' or sheet_name ==u'All':
            return wb.sheet_names()
        elif sheet_name:
            return [self.sheet_name]
        else:
            return [wb.sheet_names()[0]]
            
def if_self_sheet_name(sheet_name,wb):
    if sheet_name ==u'all' or sheet_name ==u'All':
        return wb.sheet_names()
    return [sheet_name]

default_import_xl_setting = {'default_cho_phep_exist_val_before_loop_fields_func':True,
             'default_write_when_val_exist':False,
             'default_allow_check_excel_obj_is_exist_func':False,
             'default_cho_phep_empty_pn_tuong_duong_voi_pn_duy_nhat':False,
             'default_cho_phep_co_pn_cap_nhat_empty_pn':False,
             }

# def gen_default_import_xl_setting():  
#     adict = {'default_cho_phep_exist_val_before_loop_fields_func':True,
#              'default_write_when_val_exist':False,
#              'default_allow_check_excel_obj_is_exist_func':False,
#              'default_cho_phep_empty_pn_tuong_duong_voi_pn_duy_nhat':False,
#              'default_cho_phep_co_pn_cap_nhat_empty_pn':False,
#              }
        
    
def gen_model_dict(
                    sml_title_row = False,
                   self=None,
                   mode=u'1',
                   key_tram=u'sklsklskl'):     
    mode =       getattr(self, 'mode',None)     or mode
    
    write_field_categ_id = self.env['ir.config_parameter'].sudo().get_param('tonkho.' + 'write_field_categ_id')
    not_use_default_excel_import_setting = self.env['ir.config_parameter'].sudo().get_param('tonkho.' + 'not_use_default_excel_import_setting')
    
    use_default = not not_use_default_excel_import_setting
    
    default_cho_phep_exist_val_before_loop_fields_func = True
    default_write_when_val_exist = False
    default_allow_check_excel_obj_is_exist_func = False
    default_cho_phep_empty_pn_tuong_duong_voi_pn_duy_nhat = False
    default_cho_phep_co_pn_cap_nhat_empty_pn = False
    
    
#     raise UserError(key_tram)
#     write_field_categ_id = getattr(self,'write_field_categ_id',False)
    admin_to_user = False
    user_to_admin = self.user_has_groups('tonkho.group_write_field_when_import_excel')
#     raise UserError( user_to_admin)
    is_admin = self.user_has_groups('base.group_erp_manager')
    is_user = not self.user_has_groups('base.group_erp_manager')
    is_admin_cal = False
    if is_user:
        if user_to_admin:
            is_admin_cal = True
    if is_admin:
        if admin_to_user:
            is_admin_cal = False
        else:
            is_admin_cal = True
#     raise UserError(u'kakak%s'%is_admin_cal)
#     is_user_cal = not is_admin_cal
    
#     raise UserError(is_admin_cal) 
    if key_tram =='sml':
        is_sml = True
    else:
        is_sml = False
    if mode==u'2' or is_sml:
        sml_or_mode_2 = True
    else:
        sml_or_mode_2 = False
    if key_tram == 'key_ltk_dc':
        mode_no_create_in_main_instance = getattr(self,'mode_no_create_in_main_instance',None)
    else:
        mode_no_create_in_main_instance = None
    import_from_inventory =self._context.get('import_from_inventory') # ở đây thì get context được vào trong fields thì mất
#     raise UserError("self._context.get('not_last_import_function') %s"%self._context.get('not_last_import_function'))
    ALL_MODELS_DICT = {
     u'stock.inventory.line.tong.hop.ltk.dp.tti.dp': { #tong hop
                    'key_allow':True,
                    'largest_map_row_choosing':{sml:True,all_key_tram:False},                      
                    'title_rows':{
#                         'key_ltk':[4,5],
                        'key_ltk':range(0,6),
                        'key_tti':[3,4],
                        key_ltk_dc:[0],
                        key_tti_dc:[0,1],
                        key_ltk_dc2:[7,8],
                        sml:sml_title_row or [0],
                        key_137: range(0,10)
                        
                        },
                    'title_rows_some_sheets':{'key_ltk':{u'XFP, SFP các loại':[2,3]}},
                    'begin_data_row_offset_with_title_row' :{all_key_tram:1,
                                                             key_tti_dc:2},
                    'sheet_names':{
#                         'key_ltk':lambda self: [u'Truyền dẫn',u'IP (VN2, VNP)',u'GTGT',u'Chuyển Mạch (IMS, Di Động)',u'Vô tuyến']if not self.sheet_name else [self.sheet_name],
#                         'key_ltk':lambda self: [u'Truyền dẫn',u'IP (VN2, VNP)',u'GTGT',u'Chuyển Mạch (IMS, Di Động)',u'Vô tuyến']if not self.sheet_name else [self.sheet_name],
#                         'key_ltk':lambda self,wb: [wb.sheet_names()[0]],
                        'key_ltk':sheet_for_ltk_,
                        'key_tti':lambda self,wb: wb.sheet_names() if not self.sheet_name else if_self_sheet_name(self.sheet_name,wb),
                        'key_ltk_dc':lambda self:[u'Tổng hợp'] if not self.sheet_name else [self.sheet_name],
                        key_tti_dc:lambda self:[u'TTI-TS co'],
                        sml:  lambda self,wb: [wb.sheet_names()[0]] if not self.sheet_name else if_self_sheet_name(self.sheet_name,wb),
                        key_137:lambda self,wb: [ i for i in wb.sheet_names() if u'000' not in i],#[wb.sheet_names()[0]]
#                         key_137:lambda self,wb: [wb.sheet_names()[0]]
                        key_ltk_dc2:lambda self,wb: [wb.sheet_names()[0]],
                                   } ,#[self.sheet_name],#,#[self.sheet_name],#[u'Chuyển Mạch (IMS, Di Động)'],#xl_workbook.sheet_names(),#[u'Truyền dẫn'],#[u'IP (VN2, VNP)'],[u'Chuyển Mạch (IMS, Di Động)']
                    'model':{all_key_tram: 'stock.inventory.line',sml:'stock.move.line'},## viet lai ben tao_instance_new
                   
#                     'not_update_field_if_instance_exist_default':False,
                    'bypass_this_field_if_value_equal_False_default':False,
#                     'write_when_val_exist':True,
#                     'allow_check_excel_obj_is_exist_func':True,
                    'setting': {all_key_tram: {
                                               'allow_write_from_False_to_not_false':True,
                                               'write_when_val_exist':default_write_when_val_exist if use_default else getattr(self,'write_when_val_exist',default_write_when_val_exist),
                                               'allow_check_excel_obj_is_exist_func':default_allow_check_excel_obj_is_exist_func if use_default else getattr(self,'allow_check_excel_obj_is_exist_func',default_allow_check_excel_obj_is_exist_func),
                                               'cho_phep_empty_pn_tuong_duong_voi_pn_duy_nhat':default_cho_phep_empty_pn_tuong_duong_voi_pn_duy_nhat if use_default else  getattr(self,'cho_phep_empty_pn_tuong_duong_voi_pn_duy_nhat',default_cho_phep_empty_pn_tuong_duong_voi_pn_duy_nhat),
                                               'cho_phep_co_pn_cap_nhat_empty_pn':default_cho_phep_co_pn_cap_nhat_empty_pn if use_default else  getattr(self,'cho_phep_co_pn_cap_nhat_empty_pn',default_cho_phep_co_pn_cap_nhat_empty_pn),
                                               'cho_phep_exist_val_before_loop_fields_func':default_cho_phep_exist_val_before_loop_fields_func if use_default else getattr(self,'cho_phep_exist_val_before_loop_fields_func',default_cho_phep_exist_val_before_loop_fields_func),
#                                                 'allow_check_excel_obj_is_exist_raise_or_break':'break',

                                               }},
                                                      
                    'setting2': {sml: {'allow_check_excel_obj_is_exist_raise_or_break':'break', 'allow_write':True if  is_admin_cal else False},
                                     all_key_tram:{'allow_check_excel_obj_is_exist_raise_or_break':'raise',
                                     'allow_write': True if is_admin_cal else False}
                                 },
                    'not_get_or_create':{key_ltk_dc: mode_no_create_in_main_instance} ,                                 
                    'prepare_func': {sml: prepare_func_},
                    'last_import_function':{all_key_tram:last_import_function_ if not (self._context.get('not_last_import_function') or mode_no_create_in_main_instance) else None,sml:None},
                    'last_record_function':{all_key_tram:gan_inventory_id_vao_needdata,
                                                    key_ltk_dc:last_record_function_ltk_vtdc_ if not mode_no_create_in_main_instance else None,
                                                    sml:None},
                    'break_condition_func_for_main_instance':{#all_key_tram:None,
                                                              all_key_tram:break_condition_func_for_main_instance_,
                                                              key_137:None,
#                                                               all_key_tram:None,
                                                              },
                    'fields' : [
                        #first
          
                    ('barcode_for_first_read',{'empty_val':[u'NA',u"'",u"`"],
                                               'skip_this_field':{key_ltk_dc:False,
                                                                         'all_key_tram':True},
                                               'func':lambda val,needdata: str(int(val)) if isinstance(val,float) else val,'xl_title':[u'Barcode'],'for_excel_readonly' :True}),
                   
                    ('prod_lot_id_excel_readonly',{'empty_val':{'key_ltk':[u'N/C'],
                                                                        'key_tti':[u'N/C',u'N/a',u'n/a',u'N/A'],
                                                                        'key_ltk_dc':[u'N/C',u'-',u'--',u'NA',u'N/A',u'chưa đọc được SN'],
                                                                        all_key_tram:[u'N/C',u'-',u'--',u'NA',u'N/A',u'chưa đọc được SN',u'N/C',u'N/a',u'n/a',u'N/A'],
                                                                }, 'func':lambda val,needdata: str(int(val)) if isinstance(val,float) else val,
                                                                'xl_title':{all_key_tram:[u'Lot/Serial Number',u'Seri Number',u'Số serial (S/N)',u'Serial Number',u'Serial',u'S/N',u'SERI',u'Số S/N',u'''SERI
S/N'''],
                                                                            key_tti_dc: None,},
                                                                'for_excel_readonly' :True,
                                                                'required':{key_137:True},
                                                                'col_index':{'all_key_tram':None,
                                                                             key_tti_dc:20,
                                                                    }
                                                                }),
                    
                    
                  ('prod_lot_id_excel_readonly_for_search',{'for_excel_readonly' :True,'func':prod_lot_id_excel_readonly_for_search_}   ),
                          
                   
#                    ('stt_readonly',{'for_excel_readonly' :True,
#                                             'func':stt_, 
#                                             'xl_title': {'key_ltk':u'STT new',
#                                                 'key_tti':u'STT',
#                                                 'key_ltk_dc':u'STT',
#                                                  key_tti_dc: [u'Stt',u'Stt '],
#                                                  sml:u'STT',
#                                                  key_137:[u'SỐ']
#                                                  },
#                                              'skip_this_field':{sml:True},
#                                              'skip_field_if_not_found_column_in_some_sheet':True ,
#                       }
#                     ), 
                  
                    ('product_id_name_readonly',{'for_excel_readonly' :True,
                                             'col_index':{all_key_tram:None,
                                                                        key_tti_dc:11,
                                                                  },
                                             'xl_title':{'key_ltk':[u'TÊN VẬT TƯ',u'Module quang',u'Product'],
                                                                    'key_ltk_dc':[u'Loại card'],
                                                                    'key_tti':[u'TÊN VẬT TƯ'],
                                                                    sml:[u'TÊN VẬT TƯ',u'Tên Vật Tư',u'Danh mục hàng hóa',u'Tên – Qui cách hàng hóa'],
                                                                    key_137:[u'TÊN TIẾNG VIỆT',u'TÊN THIẾT BỊ',u'Tên vật tư'],
                                                                    key_ltk_dc2:[u'Tên tài sản'],
                                                                    key_tti_dc:u'''Tên
                                                                    
chi tiết
thiết bị
(card)'''
                                                                 },
                                             'empty_val':{'key_ltk':[u'TỔNG ĐÀI IMS',u'JUNIPER ERX 1400; T1600 ; T4000'],all_key_tram:None}
#                                                      'key':True,
})  ,
                  
                    
#                      ('product_id_excel_readonly_for_search',{'for_excel_readonly' :True,'func':product_id_excel_readonly_for_search_ }   ),
                     ('stt',{
#                         'func':lambda v,n:n['vof_dict']['stt_readonly']['val'],
                        'func':stt_, 
                        'xl_title': {
#                             'key_ltk':[u'STT'] if mode==u'2' else [u'STT new'],
                            'key_ltk':[u'STT'],
                            'key_tti':u'STT',
                            'key_ltk_dc':u'STT',
                             key_tti_dc: [u'Stt',u'Stt '],
                             sml:u'STT',
                             key_137:[u'SỐ'],
                             key_ltk_dc2:u'STT'
                             },
                        'skip_this_field':{key_137:True,all_key_tram:getattr(self,'skip_stt',False)},
                        'skip_field_if_not_found_column_in_some_sheet':True ,
                        'key':{all_key_tram:True},
                        'required_force':{all_key_tram:True},
                        'required_not_create':False
                      }
                 ), # bỏ stt ở đây để dùng trong hàm break, function
                                
                                
                    ('product_id',{'string':u'Tên Vật tư',
                                   'print_write_dict_new':True,
                                   'search_func':search_func_,
                                   'offset_write_xl':{sml:1}, 
                                   'key':'Both',
                                   'required':{all_key_tram:True},
                                   'required_not_create':False,
                                   'func':{all_key_tram:None,
                                             key_137: product_id_,
                                           },
                                   'exist_val_before_loop_fields_func':exist_val_before_loop_fields_func_pr_id_,
                                   'check_excel_obj_is_exist_func':{all_key_tram:check_excel_obj_is_exist_func_},#,sml:None
                                   'fields':[
                                            ('pn',{
                                                'type_allow':[int,float],
                                                'func':lambda val,needdata: str(int(val)) if isinstance(val,float) else val,'empty_val':[u'NA',u'-',u'--'],
                                                'xl_title':[u'Part-Number',u'Part Number',u'Partnumber',u'Mã card (P/N)',u'Mã vật tư',u'''MÃ 
VẬT TƯ''',u'''MÃ 
Article Code'''],
                                                'bypass_this_field_if_value_equal_False':True,
                                                'skip_field_if_not_found_column_in_some_sheet':{sml:True,all_key_tram:None},
#                                                 'get_or_create_para':{all_key_tram:{'not_update_field_if_instance_exist':True}},
                                                'write_field':True,
                                                   }
                                             ),
                                            ('pn_replace',{'type_allow':[int,float],
                                                           'func':pn_replace_, 
#                                                            'get_or_create_para':{'all_key_tram':{'operator_search':'=ilike'}},
#                                                             'key':lambda n: True if n['vof_dict']['product_id']['fields']['pn_replace']['val'] else False ,
#                                                             'key':True,
#                                                             'bypass_this_field_if_value_equal_False':True,
#                                                              'get_or_create_para':{all_key_tram:{'not_update_field_if_instance_exist':True}},
#                                                             'write_field':True,
                                                            'for_excel_readonly':True,
                                                            }
                                             ),
                                            ('name',{
#                                                      'get_or_create_para':{'all_key_tram':{'operator_search':'=ilike'}},
                                                     'func': product_id_name_,
                                                     'key':False,
#                                                     'key':lambda n: False if n['vof_dict']['product_id']['fields']['pn_replace']['val'] else True ,
#                                                      'key':False,
                                                     'required':True,
#                                                      'get_or_create_para':{all_key_tram:{'not_update_field_if_instance_exist':True}},
#                                                       'write_field':False,
                                                     'write_field':True if is_admin_cal else False,
                                                                  }),
                                            ('type',{'set_val':'product'}),

#                                             ('tracking',{'func':{all_key_tram:lambda val,needdata: 'serial' if needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] !=False else 'none',
#                                                                         key_ltk_dc:lambda val,needdata: 'serial' if (needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] or needdata['vof_dict']['barcode_for_first_read']['val']) !=False else 'none',
#                                                                         key_137: lambda v,n:'serial'
#                                                                  }, 
#                                                             'write_func': tracking_write_func_,
#                                                          }),
#                                              
                                          
                                          

                                            ('categ_id',{##cua product_id
                                                            'skip_this_field':{all_key_tram:False},
                                                            'bypass_this_field_if_value_equal_False':True,
#                                                             'write_field':write_field_categ_id if self.user_has_groups('base.group_erp_manager') else False,
                                                             'write_field':{all_key_tram:write_field_categ_id if is_admin_cal else False,
                                                                            sml:False,},

#                                                             'write_field':False,
#                                                             'default': self.env['product.category'].search([('name','=','All')]).id,
                                                            'ready_declare_default':True,
                                                            'key':False,
#                                                             'only_get':{all_key_tram:True if  sml_or_mode_2 else False},
                                                            'only_get':{all_key_tram:True if  not is_admin_cal else False},

#                                                            'required':False,
                                                            'raise_if_diff_only_write':False,
                                                            'raise_if_diff':False,
#                                                             'raise_if_diff':{all_key_tram:not(write_field_categ_id if self.user_has_groups('base.group_erp_manager') else False),

#                                                                                   },
#                                                             'get_or_create_para':{key_ltk_dc2:{'not_update_field_if_instance_exist':True}},
                                                            
#                                                             'get_or_create_para':{all_key_tram:{'not_update_field_if_instance_exist':True}},
                                                            'set_val':{
                                                                    key_137: lambda self: self.categ_id.id,
                                                                    key_ltk_dc2:1,
                                                                    key_ltk_dc: 1,
                                                                    },
                                                'fields':[('name',{
                                                                        'skip_field_if_not_found_column_in_some_sheet':{sml:True,all_key_tram:False},
                                                                        'replace_string':{all_key_tram:[(u'Chuyển Mạch (IMS, Di Động)',u'Chuyển mạch'),(u'IP (VN2, VNP)',u'IP'),(u'XFP, SFP các loại',u'XFP, SFP')]},
                                                                        'func':{ 
                                                                                    all_key_tram:(lambda val,needdata: needdata['sheet_name']) if mode!=u'2' else None,
                                                                                    'key_tti':categ_id_tti_convert_to_ltk_,
#                                                                                     key_ltk_dc: lambda val,needdata: needdata['sheet_name'],
                                                                                    key_tti_dc: None,
                                                                                    sml:None,
                                                                                    key_137:None,
#                                                                                     key_ltk_dc2:lambda v,n:1,
                                                                                },
                                                                        'karg':{'key_tti':{'tram':'TTI'}},
                                                                        'key':True,
#                                                                         'required': {all_key_tram:True,key_137:False}},
                                                                        'required':{all_key_tram:True, 
                                                                                    },
                                                                        'xl_title':{
                                                                                    all_key_tram:None,
                                                                                    key_tti_dc:[u'Phân hệ'],
                                                                                    sml:[u'Nhóm'],
                                                                                    key_137:None,
                                                                                    'key_ltk':[u'Nhóm'] if mode ==u'2' else None
                                                                            },
                                                                            
                                                                        }
                                                            )
                                                          ]
                                                         }
                                             ),
                                             ('toc_do_id',{
                                                        'skip_this_field':{all_key_tram:True,'key_ltk':False},
                                                        'bypass_this_field_if_value_equal_False':True,
                                                        'fields':[
                                                            ('name',{'skip_field_if_not_found_column_in_some_sheet':True,'key':True,'xl_title':[u'Tốc độ']})
                                                            ]
                                                                
                                                 }),
                                            ('brand_id',{'empty_val':[u'NA'],
                                                                'skip_this_field':{key_137:True},
                                                                'bypass_this_field_if_value_equal_False':True,
                                                                'fields':[('name',{'func':lambda v,n: v.upper() if isinstance(v,str) else v,
                                                                                                'skip_field_if_not_found_column_in_some_sheet':{sml:True,all_key_tram:False},
                                                                                                'xl_title':{
                                                                                                                'key_ltk':[u'Hãng sản xuất',u'Hãng / Model'],
                                                                                                                'key_tti':[u'Hãng sản xuất',u'Hãng / Model'],
                                                                                                                key_ltk_dc :[u'Hãng sản xuất'],
                                                                                                                'sml':[u'Hãng sản xuất',u'Hãng / Model'],
                                                                                                                 },
                                                                                                 'key':True,
                                                                                                 'required': True}),
                                                                              ]}),
                                            ('thiet_bi_id',{
                                                'skip_this_field':{key_137:True},
                                                'bypass_this_field_if_value_equal_False':True,
#                                                 'get_or_create_para':{'key_tti':{'not_update_field_if_instance_exist':True},
                                                'write_field':None if is_admin_cal else False,
                                                'fields':[('name',{
                                                                'func':{all_key_tram:lambda v,n: str(int(v)) if isinstance(v,float) else v,
                                                                         key_137: lambda v,n:n['sheet_name'],
                                                                        },
#                                                                     'type_allow':[float],
                                                                   'skip_field_if_not_found_column_in_some_sheet':{sml:True,all_key_tram:None,'key_ltk': True if mode ==u'1' else None},
                                                                               'xl_title':{'key_ltk':u'Thiết bị',
                                                                                           'key_tti':u'Thiết bị',
                                                                                           key_ltk_dc:u'Tên hệ thống thiết bị',
                                                                                           sml:u'Thiết bị',
                                                                                           key_tti_dc:u'''Tên
thiết bị'''
                                                                                           }, 
                                                                               'key':True,'required': True}),
                                                            
                                                            
                                                            ('categ_id',{ 
                                                                                
                                                                                'requried':True,
                                                                                'raise_if_False':True,
                                                                                'write_field':write_field_categ_id if is_admin_cal else False,
                                                                                'raise_if_diff_only_write':False,
#                                                                                 'raise_if_diff':{all_key_tram:not(write_field_categ_id if self.user_has_groups('base.group_erp_manager') else False)},
                                                                                'raise_if_diff':False,
                                                                                'bypass_this_field_if_value_equal_False':True,
                                                                                'print_if_write':True,
                                                                                'key':False,
                                                                                'func': lambda v,n:n['vof_dict']['product_id']['fields']['categ_id']['val']}
                                                             ),
                                                            ('brand_id',{
                                                                         'write_field':None if is_admin_cal else False,
                                                                         'skip_this_field':{key_137:True},
                                                                         'key':False,
                                                                         'bypass_this_field_if_value_equal_False':True,
                                                                         'func': lambda v,n:n['vof_dict']['product_id']['fields']['brand_id']['val']}),                                                               
                                                          ]}), 
                                             
                                            
                                            ('uom_id',  {
                                                        'write_field':None if is_admin_cal else False,
                                                         'ready_declare_default':True,
                                                        'bypass_this_field_if_value_equal_False':True, 'fields': [ #'func':uom_id_,'default':1,
                                                        ('name',{'set_val':{
                                                                            all_key_tram:None,
                                                                            key_ltk_dc:u'Cái',
                                                                            key_ltk_dc2:u'Cái',
                                                                            key_tti_dc:u'Cái'
                                                                            },
                                                                 'func':{all_key_tram:name_of_uom_id_,key_137: uom_id_137_},
#                                                                      'get_or_create_para':{'all_key_tram':{'operator_search':'=ilike'},},
                                                                      'operator_search':'=ilike',
                                                                      'xl_title':{all_key_tram:[u'Đơn vị tính',u'ĐVT',u'Đơn vị'],key_ltk_dc2:None },
                                                                      'key':True,'required':True,
                                                                      'replace_string':{'key_ltk':[('Modunle','module'),('CARD','Card'),('module','Module')],
                                                                                                'key_tti':[('CARD','Card'),('module','Module'),(u'bộ',u'Bộ')]
                                                                                    },
                                                                  'sheet_allow_this_field_not_has_exel_col':{'key_ltk':[u'XFP, SFP các loại']
                                                                                                             }
                                                                  }),
                                                                 ('category_id', {'func': lambda n,v,self:self.env['product.uom.categ'].search(['|',('name','=','Unit'),('name','=',u'Đơn vị')])[0].id
                                                                                            }
                                                                     ),
                                          
                                                                           ]
                                                                }
                                             ),
                                             
                                             
                                             # Vật tư dự phòng LTK
#                                             ('ghi_chu_cho_sml_ngay_nhap',{'func':lambda val,needdata: convert_float_to_ghi_chu_cho_sml_ngay_xuat(val) if not needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] else False,
#                                                                   'xl_title':[u'Ngày nhập',u'Ngày nhận',u'Năm sử dụng'],'skip_field_if_not_found_column_in_some_sheet':True}),
#                                             ('ghi_chu_cho_sml_ngay_xuat',{'func':lambda val,needdata: convert_float_to_ghi_chu_cho_sml_ngay_xuat(val) if not needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] else False,
#                                                                   'xl_title':u'Ngày xuất','skip_field_if_not_found_column_in_some_sheet':True}),
#                                             ('ghi_chu_cho_sml_ban_dau',{'func':lambda val,needdata: val if not needdata['vof_dict']['prod_lot_id_excel_readonly']['val'] else False,
#                                                                 'xl_title':[u'Ghi chú',u'Ghi chú - Mô tả thêm',u'diễn giải'],'skip_field_if_not_found_column_in_some_sheet':True}),
                                           
#                                             ('du_phong_tao',{'skip_this_field':{sml:True},'set_val':lambda self: 'dc' not in self.key_tram }),
#                                             ('dang_chay_tao',{'skip_this_field':{sml:True},'set_val':lambda self: 'dc'  in self.key_tram }),
#                                             ('tram_ltk_tao',{'skip_this_field':{sml:True},'set_val':lambda self: (self.key_tram and 'ltk' in self.key_tram), 'bypass_this_field_if_value_equal_False':True }),
#                                             ('tram_tti_tao',{'skip_this_field':{sml:True},'set_val': lambda self: (self.key_tram and 'tti' in self.key_tram), 'bypass_this_field_if_value_equal_False':True  }),



#                                             ('ghi_chu_cho_sml_cate',{'skip_this_field':{sml:True,all_key_tram:False},'func': {all_key_tram:ghi_chu_cho_sml_cate_all_key_tram_} }),
                                            
                                            ]
                                   }),  
                                
                                
               
               
                 ('product_qty', {
                                     'type_allow':[int],
                                     'skip_this_field_for_mode_no_create':{key_ltk_dc:True},
                                     'required':True,
                                     'transfer_name':{sml:'qty_done'},
                                     'skip_this_field': {
#                                                             'key_ltk':True if getattr(self, 'allow_product_qty_dieu_chinh',None) else False,
#                                                             'sml':True if getattr(self, 'allow_product_qty_dieu_chinh',None) else False,
                                                             all_key_tram:False,
                                         },
                                     'func':{all_key_tram: qty_,
                                                key_137: qty_137_,
#                                              key_ltk_dc2:1,
                                             },
                                     'replace_val':{'key_ltk':{u'XFP, SFP các loại':[(False,1)]}},
                                     'set_val':{'all_key_tram':None,
                                                    'key_ltk_dc':1,
                                                    key_tti_dc:1,
                                                    key_ltk_dc2:1,
                                                },
                                     'xl_title':{'key_ltk':[u'Tồn kho cuối kỳ',u'Số lượng',u'Tồn kho cuối kỳ',u'Quantity',u'Số lượng',u'Số lượng điều chỉnh'],
                                                   'key_tti':[u'Tồn kho cuối kỳ',u'Số lượng',u'Tồn kho cuối kỳ'],
                                                   sml:[u'Số lượng',u'Số lượng',u'S/L',u'Tồn kho cuối kỳ',u'Quantity',u'Số lượng điều chỉnh'],
                                                   key_137:[u'CUỐI',u'TỒN',u'Số lượng',u'SL']
                                                 },
                                     'key':False,
                                     'sheet_allow_this_field_not_has_exel_col':{'key_ltk':[u'XFP, SFP các loại']}}),
                 
                 
#                  ('product_qty_dieu_chinh',{
#                                                     'type_allow':[int],
#                                                     'required_force':True,
#                                                     'xl_title':[u'qty_dieu_chinh',u'Số lượng điều chỉnh'],
#                                                     'transfer_name':{'key_ltk':'product_qty', sml:'qty_done'},
#                                                     'skip_this_field':{
#                                                         'key_ltk':False if ( getattr(self, 'allow_product_qty_dieu_chinh',None) and mode ==u'2' )else True,
#                                                         'sml':False if getattr(self, 'allow_product_qty_dieu_chinh',None) else True,
#                                                         all_key_tram:True}}),
                ('location_id_goc', {
                    'model':'stock.location',
                                     'key':False, 
                                     'for_excel_readonly' :True,
                                     "required":{all_key_tram:True if mode !=u'2' else False,sml:False},
                                     'only_get': sml_or_mode_2,
                                    'valid_field_func':{
#                                                         sml:None if  is_admin_cal else check_location_id_is_same_in_bb_,
                                                        sml:check_location_id_is_same_in_bb_,
#                                                         'key_ltk':check_if_your_depart_of_lc_goc_,
#                                                         
#                                                         all_key_tram:  None if  is_admin_cal else (check_if_your_depart_of_lc_goc_ if sml_or_mode_2 else None)
                                                        all_key_tram:  check_if_your_depart_of_lc_goc_ if (mode==u'2' and not is_admin_cal) else None
                                                        
                                                        },
                                     'func':{
#                                              sml: None,
                                             all_key_tram:None if  sml_or_mode_2  else location_goc_},
                                     
                                     'fields': [('name',{'xl_title':u'Trạm',
                                                         'skip_field_if_not_found_column_in_some_sheet':True,
                                                         'key':True,'required':True})] if sml_or_mode_2 else None ,
                                              
                                    'only_get':True,
#                                     'fields': [('name',{'xl_title':u'Trạm','key':True,'required':True})] if mode==u'2' else None ,
#                                     'fields': {'key_ltk':[('name',{'xl_title':u'Trạm','key':True,'required':True})] if getattr(self, 'mode')==u'2' else None
#                                                } ,
                                     'raise_if_False':True, 
                                     'skip_this_field':{sml:not is_sml}
                                     }),  
                
                ('department_id_for_excel_readonly',{
#                     'skip_this_field':{sml:True},
                     'skip_this_field_for_mode_no_create':{key_ltk_dc:True},
                     'for_excel_readonly':True,
                     'key':False,
                     'raise_if_False':True,
                     'func':{all_key_tram: department_for_sml_and_mode2_ if sml_or_mode_2 else look_department_from_key_tram_,
#                              sml:lambda v,n,self:self.location_id.department_id.id
#                                  sml:,
                                 
                             },
                     
                     
                                                      }),
                ('inventory_id', {
#                                         'write_field':True,
                                        'key':True,
                                        'func': inv_id_,
                                        'karg':{'key_ltk':{'import_from_inventory':import_from_inventory}},
                                        'fields':[
                                        ('name',{
                                                 'func':choose_inventory_id_name if mode !=u'2' else choose_inventory_id_name_for_mode  , 
                                                 'key':True,
                                                 'required': True
                                                 }),
                                        ('location_id',{
                                            'func':lambda val,needdata: needdata['vof_dict']['location_id_goc']['val'],
#                                             'get_or_create_para':{all_key_tram:{'not_update_field_if_instance_exist':True}},
                                            })
                                        ,] if not import_from_inventory  else None,
                                   'skip_this_field':{sml:True}
                    }),
                                
                                
                ('location_id1',{
                                   'skip_this_field':{sml:not is_sml,key_137:True},
                                   'only_get': is_sml,
                                  'skip_this_field_for_mode_no_create':{key_ltk_dc:True},'model':'stock.location', 'for_excel_readonly':True, 'skip_this_field_for_mode_no_create':{key_ltk_dc:True},
                                                       'fields':[
                                                                ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id_goc']['val'],
                                                                                 'key':True,'required':True}),
                                                                ('name',{
                                                                        'func_pre_func':{
                                                                            'key_ltk': func_pre_func_location_id_1_ltk_dp_xfp_ if  mode ==u'1' else None
                                                                            },
                                                                        'func':convert_float_location_,
                                                                        'col_index':{all_key_tram:None,
                                                                                                key_tti_dc:22,
                                                                                          },
                                                                         'xl_title':{
                                                                                     'sml':[u'Phòng',u'Phòng máy'],
                                                                                     'key_ltk':[u'Phòng',u'Phòng máy'],
                                                                                     'key_tti':u'Phòng',
                                                                                      key_ltk_dc:[u'Vị trí lắp đặt'],
                                                                                      key_ltk_dc2:[u'Vị trí lắp đặt'],
                                                                                      key_tti_dc:[u'''Vị trí
đặt'''],
                                                                                     },
                                                                          'key':True,'required': True,
                                                                          'skip_field_if_not_found_column_in_some_sheet':{sml:True,all_key_tram:False},
                                                                          'sheet_allow_this_field_not_has_exel_col':{'key_ltk':[u'XFP, SFP các loại']}}),
                                                                
#                                                                     ('department_id',{'key':False,'model':'hr.department', 'set_val':lambda self: self.department_id.id,'required':True}),
                                                                ('department_id',{'key':True,'model':'hr.department',
                                                                                   'func': lambda v,n:n['vof_dict']['department_id_for_excel_readonly']['val'],
                                                                                   'required':True,
                                                                                   'raise_if_False':True}),
                                                                ('stock_type',{'set_val':'phong_may','key':True}),
                                                                ]
                                                       }), 
                ('location_id2',{'skip_this_field':{sml:not is_sml,key_137:True},
                                 'only_get': is_sml,
                                  'skip_this_field_for_mode_no_create':{key_ltk_dc:True},'model':'stock.location', 'for_excel_readonly':True,
                                                           'fields':[
                                                                    ('location_id',{'required':True,'func':lambda val,needdata: needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val']  , 'key':True}),
                                                                    ('name',{'func':convert_float_location_,
                                                                             'xl_title':{
                                                                                            'sml':[u'Tủ/Kệ',u'Tủ',u'Tủ/cabinet'],
                                                                                            'key_ltk':[u'Tủ/Kệ',u'Tủ',u'Tủ/cabinet'],
                                                                                            'key_tti':[u'Tủ/Kệ',u'Tủ'],
                                                                                             key_ltk_dc:[u'Tên tủ (Cabinet / rack)',u'Tủ'],
                                                                                             key_ltk_dc2:[u'Tên tủ (Cabinet / rack)',u'Tủ'],
                                                                                             key_tti_dc:None,
                                                                                         },
                                                                          'skip_field_if_not_found_column_in_some_sheet':{sml:True,all_key_tram:False},
                                                                              'key':True,'required': True}),
    #                                                                    ('department_id',{'key':False,'model':'hr.department', 'set_val':lambda self: self.department_id.id,'required':True,'raise_if_False':True, }),
                                                                    ('department_id',{'key':True,'model':'hr.department', 'func': lambda v,n:n['vof_dict']['department_id_for_excel_readonly']['val'],'required':True,'raise_if_False':True}),
                                                                    ('stock_type',{'set_val':'tu','key':True}),
                                                                    
                                                                    ]
                                                           }),                                           
                ('location_id3',{'skip_this_field':{sml:not is_sml,key_137:True},
                                 'only_get': is_sml,
                                  'skip_this_field_for_mode_no_create':{key_ltk_dc:True},'model':'stock.location', 'for_excel_readonly':True,
                                                       'fields':[
                                                                ('location_id',{'required':True,
                                                                                'func':lambda val,needdata: needdata['vof_dict']['location_id2']['val'] or needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
                                                                ('name',{'func':convert_float_location_,
                                                                         'xl_title':{
                                                                                        'sml':[u'Ngăn',u'Ngăn/Kệ',u'Shelf/ngăn/kệ'],
                                                                                        'key_ltk':[u'Ngăn',u'Ngăn/Kệ',u'Shelf',u'Shelf/ngăn/kệ'],
                                                                                        'key_tti':[u'Ngăn',u'Ngăn/Kệ'],
                                                                                         key_ltk_dc:[u'Ngăn (shelf)',u'Ngăn'],
                                                                                         key_ltk_dc2:[u'Ngăn (shelf)',u'Ngăn'],
                                                                                         key_tti_dc:None},
                                                                          'skip_field_if_not_found_column_in_some_sheet':{sml:True,all_key_tram:False},
                                                                          'key':True,'required': True}),
                                                              
#                                                                     ('department_id',{'key':False,'model':'hr.department', 'set_val':lambda self: self.department_id.id,'required':True }),
                                                                ('department_id',{'key':True,'model':'hr.department', 'func': lambda v,n:n['vof_dict']['department_id_for_excel_readonly']['val'],'required':True,'raise_if_False':True}),
                                                                ('stock_type',{'set_val':'shelf','key':True}),
                                                                
                                                                ]
                                                       }),         
                ('location_id4',{'skip_this_field':{sml:not is_sml,key_137:True},
                                 'only_get': is_sml,
                                  'skip_this_field_for_mode_no_create':{key_ltk_dc:True},'model':'stock.location', 'for_excel_readonly':True,
                                                       'fields':[
                                                                ('location_id',{'required':True,'func':lambda val,needdata: needdata['vof_dict']['location_id3']['val'] or needdata['vof_dict']['location_id2']['val'] or needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
                                                                ('name',{'func':convert_float_location_,
                                                                         'xl_title':{
                                                                                        'sml':[u'Số thùng',u'STT trong shelf',u'STT trong shelf/số thùng',u'Hộp'],
                                                                                        'key_ltk':[u'Số thùng',u'STT trong shelf',u'STT trong shelf/số thùng',u'Hộp'],
                                                                                        'key_tti':[u'Số thùng'],
                                                                                         key_ltk_dc:[u'Số thứ tự (trong shelf)'],
                                                                                         key_ltk_dc2:[u'Số thứ tự (trong shelf)'],
                                                                                         key_tti_dc:None,
                                                                                        },   
                                                                          'skip_field_if_not_found_column_in_some_sheet':{sml:True,all_key_tram:False},
                                                                  'key':True,'required': True,'skip_field_if_not_found_column_in_some_sheet':True}),
#                                                                     ('department_id',{'key':False,'model':'hr.department', 'set_val':lambda self: self.department_id.id,'required':True}),
                                                                ('department_id',{'key':True,'model':'hr.department', 'func': lambda v,n:n['vof_dict']['department_id_for_excel_readonly']['val'],'required':True,'raise_if_False':True}),
                                                                ('stock_type',{'set_val':'stt_trong_self','key':True}),
                                                                ]
                                                       }),  
              ('location_id5',{'skip_this_field':{sml:not is_sml,key_137:True},
                                'only_get': is_sml,
                                'skip_this_field_for_mode_no_create':{key_ltk_dc:True},'model':'stock.location', 'for_excel_readonly':True,
                                           'fields':[
                                                  ('location_id',{'required':True,
                                                                    'func':lambda val,needdata: needdata['vof_dict']['location_id4']['val'] or needdata['vof_dict']['location_id3']['val'] or needdata['vof_dict']['location_id2']['val'] or needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val'],
                                                                    'key':True}),
                                                    ('name',{
                                                            'func':convert_float_location_,
                                                            'xl_title':{
                                                                        'sml':[u'Slot'],
                                                                        'key_ltk':[u'Slot'] if mode ==u'2' else None ,
                                                                        'key_tti':None,
                                                                        key_ltk_dc:[u'Khe (Slot)'],
                                                                        key_ltk_dc2:[u'Khe (Slot)'],
                                                                        key_tti_dc:None,
                                                                        },        
                                                             
                                                            'key':True,'required': True,
                                                            'skip_field_if_not_found_column_in_some_sheet':True,
#                                                             'func':location_id5_chua_ro_,
                                                            }),
                                                  
                                                    ('stock_type',{'set_val':'slot',
                                                                         'key':True,
#                                                                     'func': lambda v,n,self: 'slot' if n['vof_dict']['location_id5']['fields']['name']['val'] != u'Chưa rõ' else False
                                                                   
                                                                   }),
                                                    ('department_id',{'key':True,'model':'hr.department', 'func': lambda v,n:n['vof_dict']['department_id_for_excel_readonly']['val'],'required':True,'raise_if_False':True}),
                                                    ]
                                           }),     
                                
                                
                ('location_id6',{'skip_this_field':{sml:True,key_137:True},
                                 
                                  'skip_this_field_for_mode_no_create':{key_ltk_dc:True},
                                  'model':'stock.location',
                                  'for_excel_readonly':True,
                                           'fields':[
                                                    ('name',{
#                                                             'func':convert_float_location_,
                                                            'xl_title':{all_key_tram:None,
                                                                        },        
                                                            'key':True,
                                                            'required': True,
                                                            'func':location_id5_chua_ro_,
                                                            }),
                                                    ('location_id',{'required':True,'func':lambda val,needdata: needdata['vof_dict']['location_id5']['val']  or needdata['vof_dict']['location_id4']['val'] or needdata['vof_dict']['location_id3']['val'] or needdata['vof_dict']['location_id2']['val'] or needdata['vof_dict']['location_id1']['val'] or  needdata['vof_dict']['location_id_goc']['val'], 'key':True}),
#                                                     ('stock_type',{#'set_val':'slot',
#                                                                     'func': lambda v,n,self: 'slot' if n['vof_dict']['location_id5']['fields']['name']['val'] != u'Chưa rõ' else False
#                                                                    }),
                                                    ('department_id',{'key':True,'model':'hr.department', 'func': lambda v,n:n['vof_dict']['department_id_for_excel_readonly']['val'],'required':True,'raise_if_False':True}),
                                                    ]
                                           }),   
                                
               
                 ('location_id_goc_dc', {
                     'for_excel_readonly':True, 
                    'model':'stock.location',
                                     'key':False, 
                                     'for_excel_readonly' :True,
#                                      "required":True,
                                     'func':None,
                                     'only_get':True,
                                     'valid_field_func':{sml:check_location_id_is_same_in_bb_dc_},
                                     'fields':[
                                         
                                         ('name',{'xl_title':u'Trạm điều chuyển','key':True,'required':True,
                                                        'skip_field_if_not_found_column_in_some_sheet':True}),
#                                                   ('department_id',{'key':True,'model':'hr.department', 'func': lambda v,n:n['vof_dict']['department_id_for_excel_readonly']['val'],'required':True,'raise_if_False':True}),
                                               ], 
                                            
#                                     'only_get':True,
#                                     'fields': [('name',{'xl_title':u'Trạm','key':True,'required':True})] if mode==u'2' else None ,
#                                     'fields': {'key_ltk':[('name',{'xl_title':u'Trạm','key':True,'required':True})] if getattr(self, 'mode')==u'2' else None
#                                                } ,
#                                      'raise_if_False':True,
                                     'skip_this_field':{sml:False, all_key_tram:False},

#                                       'skip_this_field':{sml:True}
                                     }),  
                
               
                ('location_id1_dc',{'skip_this_field':{sml:False, all_key_tram:True
                                                       
                                                       }, 
                                    'skip_this_field_for_mode_no_create':{key_ltk_dc:True},
                                    'model':'stock.location', 
                                    'for_excel_readonly':True, 
                                                       'fields':[
                                                                ('name',{'func':convert_float_location_,
                                                                              'col_index':{all_key_tram:None,
                                                                                                key_tti_dc:22,
                                                                                          },
                                                                         'xl_title':{
                                                                                      'sml':u'Phòng máy điều chuyển',
                                                                                      'key_ltk':[u'Phòng',u'Phòng máy'],
                                                                                     'key_tti':u'Phòng',
                                                                                      key_ltk_dc:[u'Vị trí lắp đặt'],
                                                                                      key_ltk_dc2:[u'Vị trí lắp đặt'],
                                                                                      key_tti_dc:[u'''Vị trí
đặt'''],
                                                                                     },
                                                                          'key':True,'required': True,
                                                                          'sheet_allow_this_field_not_has_exel_col':{'key_ltk':[u'XFP, SFP các loại']},
                                                                          'skip_field_if_not_found_column_in_some_sheet':True,
                                                                          }),
                                                                ('location_id',{'required':True,
                                                                                'func':lambda val,needdata: needdata['vof_dict']['location_id_goc_dc']['val'],
                                                                                 'key':True}),
                                                                
                                                                ('department_id',{
                                                                                  'valid_field_func':None if is_admin_cal else check_if_your_department_in_location_1_2_3_4_5_ ,
                                                                                  'key':True,
                                                                                  'model':'hr.department', 
                                                                                  'func':lambda v,n,self: n['vof_dict']['location_id_goc_dc']['obj'].department_id.id,
                                                                                  'required':True}),
#                                                                 ('department_id',{'key':True,'model':'hr.department', 'func': lambda v,n:n['vof_dict']['department_id_for_excel_readonly']['val'],'required':True,'raise_if_False':True}),
                                                               
                                                                ('stock_type',{'set_val':'phong_may'}),
                                                                ]
                                                       }), 
                ('location_id2_dc',{'skip_this_field':{sml:False, all_key_tram:True}, 'skip_this_field_for_mode_no_create':{key_ltk_dc:True},'model':'stock.location', 'for_excel_readonly':True,
                                                           'fields':[
                                                                    ('name',{'func':convert_float_location_,
                                                                             'xl_title':{'key_ltk':[u'Tủ/Kệ',u'Tủ'],
                                                                                            'key_tti':[u'Tủ/Kệ',u'Tủ'],
                                                                                             key_ltk_dc:[u'Tên tủ (Cabinet / rack)',u'Tủ'],
                                                                                             key_ltk_dc2:[u'Tên tủ (Cabinet / rack)',u'Tủ'],
                                                                                             key_tti_dc:None,
                                                                                             sml:[u'Tủ điều chuyển']
                                                                                         },
                                                                              'key':True,'required': True,'skip_field_if_not_found_column_in_some_sheet':True,}),
                                                                    ('location_id',{'required':True,'func':lambda val,needdata: needdata['vof_dict']['location_id1_dc']['val'] or  needdata['vof_dict']['location_id_goc_dc']['val']  , 'key':True}),
    #                                                                    ('department_id',{'key':False,'model':'hr.department', 'set_val':lambda self: self.department_id.id,'required':True,'raise_if_False':True, }),
                                                                   
                                                                    ('department_id',{
                                                                                  'valid_field_func':None if is_admin_cal else check_if_your_department_in_location_1_2_3_4_5_,
                                                                                  'key':True,
                                                                                  'model':'hr.department', 
                                                                                  'func':lambda v,n,self: n['vof_dict']['location_id_goc_dc']['obj'].department_id.id,
                                                                                  'required':True}),
                                                                     
                                                                    ('stock_type',{'set_val':'tu'}),
                                                                    
                                                                    ]
                                                           }),                                           
                ('location_id3_dc',{'skip_this_field':{sml:False, all_key_tram:True}, 'skip_this_field_for_mode_no_create':{key_ltk_dc:True},'model':'stock.location', 'for_excel_readonly':True,
                                                       'fields':[
                                                                ('name',{'func':convert_float_location_,
                                                                         'xl_title':{'key_ltk':[u'Ngăn',u'Ngăn/Kệ',u'Shelf'],
                                                                                        'key_tti':[u'Ngăn',u'Ngăn/Kệ'],
                                                                                         key_ltk_dc:[u'Ngăn (shelf)',u'Ngăn'],
                                                                                         key_ltk_dc2:[u'Ngăn (shelf)',u'Ngăn'],
                                                                                         key_tti_dc:None,
                                                                                         sml:[u'Shelf điều chuyển']
                                                                                         },
                                                                          'key':True,'required': True,'skip_field_if_not_found_column_in_some_sheet':True,}),
                                                                ('location_id',{'required':True,
                                                                                'func':lambda val,needdata: needdata['vof_dict']['location_id2_dc']['val'] or needdata['vof_dict']['location_id1_dc']['val'] or  needdata['vof_dict']['location_id_goc_dc']['val'], 'key':True}),
#                                                                     ('department_id',{'key':False,'model':'hr.department', 'set_val':lambda self: self.department_id.id,'required':True }),
                                                                ('department_id',{
                                                                                   'valid_field_func':None if is_admin_cal else check_if_your_department_in_location_1_2_3_4_5_,
                                                                                  'key':True,
                                                                                  'model':'hr.department', 
                                                                                  'func':lambda v,n,self: n['vof_dict']['location_id_goc_dc']['obj'].department_id.id,
                                                                                  'required':True}),
                                                                ('stock_type',{'set_val':'shelf'}),
                                                                
                                                                ]
                                                       }),         
                ('location_id4_dc',{'skip_this_field':{sml:False,all_key_tram:True}, 'skip_this_field_for_mode_no_create':{key_ltk_dc:True},
                                    'model':'stock.location', 'for_excel_readonly':True,'skip_field_if_not_found_column_in_some_sheet':True,
                                                       'fields':[
                                                                ('name',{'func':convert_float_location_,
                                                                         'xl_title':{'key_ltk':[u'Số thùng',u'STT trong shelf'],
                                                                                        'key_tti':[u'Số thùng'],
                                                                                         key_ltk_dc:[u'Số thứ tự (trong shelf)'],
                                                                                         key_ltk_dc2:[u'Số thứ tự (trong shelf)'],
                                                                                         key_tti_dc:None,
                                                                                         sml:[u'STT trong shelf điều chuyển']
                                                                                        },   
                                                                  'key':True,'required': True,'skip_field_if_not_found_column_in_some_sheet':True}),
                                                                ('location_id',{'func':lambda val,needdata: needdata['vof_dict']['location_id3_dc']['val'] or needdata['vof_dict']['location_id2_dc']['val'] or needdata['vof_dict']['location_id1_dc']['val'] or  needdata['vof_dict']['location_id_goc_dc']['val'], 'key':True}),
#                                                                 ('department_id',{'required':True,'key':True,'model':'hr.department', 'func': lambda v,n:n['vof_dict']['department_id_for_excel_readonly']['val'],'required':True,'raise_if_False':True}),
                                                                
                                                                ('department_id',{
                                                                                   'valid_field_func':None if is_admin_cal else check_if_your_department_in_location_1_2_3_4_5_,
                                                                                  'key':True,
                                                                                  'model':'hr.department', 
                                                                                  'func':lambda v,n,self: n['vof_dict']['location_id_goc_dc']['obj'].department_id.id,
                                                                                  'required':True}),         
                                                                ('stock_type',{'set_val':'stt_trong_self'}),
                                                                ]
                                                       }),  
              ('location_id5_dc',{'skip_this_field':{sml:False, all_key_tram:True},
                                   'skip_this_field_for_mode_no_create':{key_ltk_dc:True},
                                   'model':'stock.location', 
                                   'for_excel_readonly':True,
                                           'fields':[
                                                    ('name',{
                                                            'func':convert_float_location_,
                                                            'xl_title':{'key_ltk':[u'Hộp',u'Slot'],
                                                                        'key_tti':[u'Hộp'],
                                                                        key_ltk_dc:[u'Khe (Slot)'],
                                                                        key_ltk_dc2:[u'Khe (Slot)'],
                                                                        key_tti_dc:None,
                                                                        sml:[u'Slot điều chuyển']
                                                                        },        
                                                            'key':True,'required': True,
                                                            'skip_field_if_not_found_column_in_some_sheet':True,
#                                                             'func':location_id5_chua_ro_,
                                                            }),
                                                    ('location_id',{'required':True,
                                                                     'valid_field_func':None if is_admin_cal else check_if_your_department_in_location_1_2_3_4_5_,
                                                                    'func':lambda val,needdata: needdata['vof_dict']['location_id4_dc']['val'] or needdata['vof_dict']['location_id3_dc']['val'] or needdata['vof_dict']['location_id2_dc']['val'] or needdata['vof_dict']['location_id1_dc']['val'] or  needdata['vof_dict']['location_id_goc_dc']['val'], 'key':True}),
                                                    ('stock_type',{'set_val':'slot',
#                                                                     'func': lambda v,n,self: 'slot' if n['vof_dict']['location_id5']['fields']['name']['val'] != u'Chưa rõ' else False
                                                                   
                                                                   }),
#                                                     ('department_id',{'key':True,'model':'hr.department', 'func': lambda v,n:n['vof_dict']['department_id_for_excel_readonly']['val'],'required':True,'raise_if_False':True}),
                                                    ('department_id',{
                                                                                  'key':True,
                                                                                  'model':'hr.department', 
                                                                                  'func':lambda v,n,self: n['vof_dict']['location_id_goc_dc']['obj'].department_id.id,
                                                                                  'required':True}),
                                                    ]
                                           }),     
                                
                                
                                
                                
                ('location_id_dc', {
                    'skip_this_field':{sml:False, 
                                       all_key_tram:True},
                    'for_excel_readonly':True,
                                    
                'func':{
                all_key_tram: lambda v,needdata:  
                needdata['vof_dict']['location_id5_dc']['val'] or
                needdata['vof_dict']['location_id4_dc']['val'] or \
                needdata['vof_dict']['location_id3_dc']['val'] or \
                needdata['vof_dict']['location_id2_dc']['val'] or \
                needdata['vof_dict']['location_id1_dc']['val'] or \
                needdata['vof_dict']['location_id_goc_dc']['val']}
                , 'key':False}),
                                               
                                
                                
                                
               
                ('location_dest_id',{'skip_this_field':{sml:False,all_key_tram:True}, 
                                     'skip_this_field_for_mode_no_create':{key_ltk_dc:True},
#                                      'set_val':{sml:lambda self: self.location_dest_id.id}
                                     'func': lambda v,n,self: n['vof_dict']['location_id_dc']['val'] or  self.location_dest_id.id
                                     }),
                                
                                
                ('picking_id',{'required':True,
                                'key':True, 'set_val':{sml:lambda self:self.id},
                                'skip_this_field':{sml:False,all_key_tram:True}}),
               
                ('product_uom_id',{'skip_this_field':{sml:False,all_key_tram:True}, 
                                   'skip_this_field_for_mode_no_create':{key_ltk_dc:True},
                                   'required_not_create':{sml:False},
#                                         'func':lambda v,n,self:n['vof_dict']['product_id']['fields']['uom_id']['val'] 
                                    'func':product_uom_id_,
                                   }),

                ('tinh_trang',{'skip_this_field':{sml:False,all_key_tram:True}, 'skip_this_field_for_mode_no_create':{key_ltk_dc:True},'set_val': {all_key_tram:u'tot',  sml:None},'xl_title':  {all_key_tram:None,  sml:[u'T/T',u'Tình trạng']},
                                                               'skip_field_if_not_found_column_in_some_sheet':True,
                                                               'func':tinh_trang_}),
                ('ghi_chu',{
                            'xl_title':u'ghi chú',
                            'skip_this_field_for_mode_no_create':{key_ltk_dc:True},
                            'func': {'sml':ghi_chu_cho_sml_,
                                     all_key_tram:convert_float_to_ghi_chu_cho_sml_ngay_xuat,
                                     },
                            'skip_field_if_not_found_column_in_some_sheet':True,
                             }),
#                     ('ghi_chu_cho_sml_cate',{'skip_this_field':{sml:True,all_key_tram:False},'func': {all_key_tram:ghi_chu_cho_sml_cate_all_key_tram_} }),
               
                ('prod_lot_id', {
                                  'print_write_dict_new':True,
                                 'offset_write_xl':{sml:2},
                                 'required_force':{all_key_tram:False,key_137:True},
                                 'transfer_name':{sml:'lot_id'},'key':True,'string':u'Serial number',
                                 'exist_val_before_loop_fields_func':exist_val_before_loop_fields_func_lot_id_,
#                                      'set_val_instead_loop_fields':{sml:set_val_instead_loop_fields_prod_lot_id_},
                                 
                                  'fields':[
                                                ('name',{'type_allow':[int],
                                                         'required':{all_key_tram:True, 
                                                                                         },
                                                         'required_not_create':False,
#                                                          'get_or_create_para':{'all_key_tram':{'operator_search':'=ilike'}},
                                                        'operator_search':'=ilike',
                                                         'func':{all_key_tram:lambda val,needdata: needdata['vof_dict']['prod_lot_id_excel_readonly']['val'],
                                                                    key_ltk_dc:lot_name_key_ltk_dc_,
                                                                 },'key':True
                                                         }),
            #                                     ('pn',{'xl_title':[u'Part Number',u'Partnumber',u'Mã card (P/N)']}),
                                                ('barcode_sn',{'skip_this_field':{key_ltk_dc:False,all_key_tram:True},'func':lambda v,n:n['vof_dict']['barcode_for_first_read']['val'] ,'key':True}),
                                               
 
                                                ('id_ke_toan',{'skip_this_field':{key_ltk_dc2:False,all_key_tram:True}, 'key':False,'xl_title':[u'ID - Không sửa cột này']}),
                                                ('the_tai_san',{'skip_this_field':{key_ltk_dc2:False,all_key_tram:True}, 'key':False,'xl_title':[u'Số thẻ']}),
                                                ('product_id',{'func':lambda v,n:n['vof_dict']['product_id']['val'],
                                                               'key': True,
                                                                'required':False
                                                                 }),
                                                ('tinh_trang',{
                                                               'skip_this_field':{sml:True,all_key_tram:False},
                                                               'set_val': {all_key_tram:u'tot',  sml:None},
                                                               'xl_title':  {all_key_tram:None,  sml:[u'T/T',u'Tình trạng']},
                                                               'skip_field_if_not_found_column_in_some_sheet':True,
                                                               'func': tinh_trang_}),
                                            
                                                ('ngay_su_dung',{
                                                    'skip_this_field':{all_key_tram:True,key_ltk_dc2:False},
                                                    'xl_title':[u'Ngày đưa vào SD'],
#                                                     'skip_field_if_not_found_column_in_some_sheet':True,
                                                    'func':lambda v,n: convert_float_to_ghi_chu_cho_sml_ngay_xuat_2(v)}),
                                               
                                                ('ghi_chu_ban_dau',{'write_field':False,'xl_title':[u'Ghi chú - Mô tả thêm',u'Ghi chú'], 'func':lambda v,n: convert_float_to_ghi_chu_cho_sml_ngay_xuat(v),'skip_field_if_not_found_column_in_some_sheet':True}),
                                                ('ghi_chu_ngay_nhap',{'skip_this_field':{all_key_tram:False,key_137:False},'xl_title':[u'NHẬP',u'Ngày nhập'],'skip_field_if_not_found_column_in_some_sheet':True,'func':lambda v,n: convert_float_to_ghi_chu_cho_sml_ngay_xuat(v),'skip_field_if_not_found_column_in_some_sheet':True}),
                                                ('ghi_chu_ngay_xuat',{'skip_this_field':{all_key_tram:False,key_137:False},'xl_title':[u'XUẤT',u'Ngày xuất'],'skip_field_if_not_found_column_in_some_sheet':True,'func':lambda v,n: convert_float_to_ghi_chu_cho_sml_ngay_xuat(v),'skip_field_if_not_found_column_in_some_sheet':True}),
                                      
                                      ]
                                  }),
            ('location_id', {'skip_this_field':{all_key_tram:False},
                              'skip_this_field_for_mode_no_create':{key_ltk_dc:True},
#                  'karg':{sml:{'is_sml':is_sml}},
                'func':{
                'sml':location_id_for_sml_,
                key_137: lambda v,n:n['vof_dict']['location_id_goc']['val'],
                all_key_tram: or_7_location_id_ if mode !=u'2' else location_id_for_sml_}
                , 'key':False}),
                                                 ]
                    },#End stock.inventory.line'
    }                               
#     ALL_MODELS_DICT.update(gen_product_model_dict())
    ALL_MODELS_DICT.update(gen_user_department_model_dict())
    ALL_MODELS_DICT.update(gen_tvcv_model_dict())
    return ALL_MODELS_DICT
    