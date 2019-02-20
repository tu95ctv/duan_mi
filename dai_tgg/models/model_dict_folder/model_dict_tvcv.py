 # -*- coding: utf-8 -*-
# from odoo.addons.dai_tgg.models.get_or_create_func import get_or_create_object_sosanh
from odoo.addons.dai_tgg.mytools import get_or_create_object_sosanh
def convert_integer(val,needdata):
    try:
        return int(val)
    except:
        return 0
    

def gen_tvcv_model_dict():
    tvcv_dict = {
          u'Thư viện công việc': {
                'inactive_include_search':True,
                'title_rows' : range(1,4), 
                'begin_data_row_offset_with_title_row' :1,
                'sheet_names':lambda self,wb: wb.sheet_names(),
                'model':'tvcv',
                'fields' : [
                        ('name', {'func':None,'xl_title':u'Công việc',
                                   'required':True,
#                                    'key':True 
                                   } ),#'func_de_tranh_empty':lambda r:  len(r) > 2
                        ( 'loai_record',{'func':None,'set_val':u'Công Việc', 'key':False }),
                        ('department_id',{'key':True,'model':'hr.department', 'set_val': lambda self: self.env['hr.department'].search([('name','=ilike',u'Đài HCM')]).id,'required':True,'raise_if_False':True
                                                                  #'fields':[('name',{'key':True,'set_val':'LTK'})]
                                                                  }),
                        ( 'state',{'set_val':'confirmed'}),
                        ( 'cong_viec_cate_id',
                          {
#                               'func':lambda val,needdata,self:get_or_create_object_sosanh(self, 'tvcvcate', {'name':needdata['sheet_name']}, {} ).id ,
                            'key':False,
                            'fields':[('name',{
                                 'key':True,
                                'required':True,
                                'replace_string':[('Quan_ly',u'Quản lý'),('Vanhanh',u'Vận hành'),('Van_thu_hanh_chinh',u'Văn thư hành chính'),('Baocao',u'Báo cáo'),('Khac',u'Khác')],
                                'func': lambda v,n,self:n['sheet_name']})]
                            
                             }),
                        ( 'code',{'func':None,'xl_title':u'Mã CV',
                                  'key':True ,'required':True}),
                        ('do_phuc_tap',{'func':convert_integer,'xl_title':u'Độ phức tạp','key':False}),
                        ('diem',{'func':None,'xl_title':u'Điểm','key':False}),
                        ('don_vi',{'fields':[
                                                ('name',{'key':True, 'required':True, 'xl_title':u'Đơn vị' }),
                                                ],'key' : False, 'required' : False}),
                         ('thoi_gian_hoan_thanh',{'func':convert_integer, 'xl_title':u'Thời gian hoàn thành','key':False}),
                         ('dot_xuat_hay_dinh_ky',{'fields':[
                                                ('name',{'key':True, 'required':True,'col_index':7}),
                                                ],'key' : False,'required' : False}),  
                        ('ghi_chu',{'func':None,'xl_title':u'Ghi chú','key':False}),
#                         ('children_ids',{'key':False,'required':False,
#                                        'fields':[
#                                                 ('name',{'xl_title':u'Các công việc con',  'key':True, 'required':True, 'is_x2m_field':True,'skip_field_if_not_found_column_in_some_sheet':True }),
#                                                 ]
#                                        }),  
                         ('active',{'func':lambda val, needdata: False if val ==u'na' else True,'xl_title':u'active','key':False,'skip_field_if_not_found_column_in_some_sheet':True,}),
                      ]
                },#End stock.inventory.line'   
        
         u'Loại sự cố, sự vụ': {
                'inactive_include_search':True,
                'title_rows' : [0], 
                'begin_data_row_offset_with_title_row' :1,
                'sheet_names':['Loại sự cố sự vụ'],
                'model':'tvcv',
                'fields' : [
                        ('name', {'func':None,'xl_title':u'Loại', 'required':True,'key':True } ),#'func_de_tranh_empty':lambda r:  len(r) > 2
                        ( 'loai_record',{'func':None,'xl_title':u'loai_record', 'key':True,'required_force':True, 'raise_if_False':True}),
                        ( 'is_bc',{'set_val':True}),
                      ]
                },#End stock.inventory.line'   
        }
    return tvcv_dict