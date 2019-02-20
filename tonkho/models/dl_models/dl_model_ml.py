# -*- coding: utf-8 -*-
#######################ML################################
import xlwt
from openerp.http import request
# from odoo.addons.tonkho.models.dl_models.dl_model import add_title
from odoo.addons.downloadwizard.models.dl_models.dl_model import  add_title
from collections import  OrderedDict
from odoo.addons.downloadwizard.models.dl_models.dl_model import generate_easyxf, wrap_center_vert_border_style,\
center_border_style


# wrap_center_vert_border_style = xlwt.easyxf("font:  name Times New Roman, height 240 ;align: wrap on , vert centre; borders: left thin,right thin, top thin, bottom thin")
wrap_center_vert_border_style = xlwt.easyxf(generate_easyxf(height=12,vert = 'center',borders='left thin, right thin, top thin, bottom thin',align_wrap=True))
def add_1_row_new_ml(worksheet, move ,FIELDNAME_FIELDATTR, row_index, offset_column=0, 
                            needdata=None,save_ndata=False,ml=False,
                            ml_index=False,rowspan=False,
                            font_height=12,wrap_center_vert_border_style=wrap_center_vert_border_style):
    
    
    if save_ndata:
        a_instance_dict =  needdata.get('a_instance_dict', {})
    else:
        a_instance_dict = {}
    writen_column_number = 0
    col_index = 0
    col_index += offset_column
    for f_name,FIELDATTR in FIELDNAME_FIELDATTR.items():
#         f_name,FIELDATTR =  field_from_my_FIELDNAME_FIELDATTR
        is_not_model_field = FIELDATTR.get('is_not_model_field')
        skip_field = FIELDATTR.get('skip_field')
        one_field_val = a_instance_dict.setdefault(f_name,{})
        if skip_field:
            continue
        if '.' in f_name:
            f_names = f_name.split('.')
            f_name = f_names[-1]
            r = ml
            is_same = FIELDATTR.get('is_same', False)
            if is_same == False:
                if not is_not_model_field:
                    is_same = len(set(move.move_line_ids.mapped(f_name))) <=1
        else:
            r = move
            is_same = FIELDATTR.get('is_same', True)
        if callable(is_same):
            kargs_for_is_same = FIELDATTR.get('kargs_for_is_same',{})
            is_same = is_same(move,ml,**kargs_for_is_same)
        is_same = is_same if rowspan > 1 else False       
        write_to_excel = FIELDATTR.get('write_to_excel',True)
        
        
        if is_not_model_field:
            val = False
        else:
#             real_f_name = f_name
            real_f_name = FIELDATTR.get('transfer_field') or f_name
            val = getattr(r, real_f_name)
        
        one_field_val['val_before_func'] = val
        func = FIELDATTR.get('func',None)
        
        kargs = FIELDATTR.get('kargs',{})
        if FIELDATTR.get('is_use_kargs_co_san',None):
            kargs_co_san = {'is_same':is_same,'ml_index':ml_index}
            kargs.update(kargs_co_san)
        if func:
            val = func(val,needdata,move,ml, **kargs)
        if val == False:
            val = u''
            
        one_field_val['val']=val 
        
        if write_to_excel:
            style = FIELDATTR.get('style',wrap_center_vert_border_style)
            if is_same:
                if ml_index==0:
                    worksheet.write_merge(row_index, row_index +rowspan-1, col_index,col_index,val,style)
            else:
                worksheet.write(row_index, col_index, val, style)
            writen_column_number +=1
            col_index +=1
        else:
            pass

    return a_instance_dict, writen_column_number


 
# normal_not_bold_style = xlwt.easyxf("font: bold on, name Times New Roman, height 240 ;align:  vert centre, horiz center;")


def download_model_new_ml(dl_obj, Export_Para=None,workbook=None,
                          append_domain=None,sheet_name=None,worksheet=None,
                          row_index=15,
                          font_height=12):
    exported_model= Export_Para['exported_model']
    FIELDNAME_FIELDATTR= Export_Para['FIELDNAME_FIELDATTR']
    FIELDNAME_FIELDATTR = OrderedDict(FIELDNAME_FIELDATTR)
    gen_domain= Export_Para.get('gen_domain')
    if worksheet ==None:
        if workbook==None:
            workbook = xlwt.Workbook()
        sheet_name =  u'Sheet 1' if sheet_name ==None else sheet_name
        worksheet = workbook.add_sheet(sheet_name,cell_overwrite_ok=True)
        worksheet.header_str = 'not thing'
        worksheet.footer_str = 'not thing'
#         worksheet.PageSetup.CenterHeader = ''
#         worksheet.PageSetup.CenterFooter = ''
    needdata = {'a_instance_dict':{'move_line_ids.stt_not_model':{'val':0}}}
    needdata['dl_obj'] = dl_obj
    if gen_domain:
        domain = gen_domain(dl_obj)
    else:
        domain = []
    if append_domain:
        domain.extend(append_domain)  
    order = Export_Para.get('search_para',{})
    print ('order',order)
    all_objs = request.env[exported_model].search(domain,**order)
#     all_objs = all_objs.sorted(key=lambda r: r.move_line_ids[0].stt)
    model_fields = request.env[exported_model]._fields
    
    
#     skip_tinh_trang_field = set(dl_obj.move_line_ids.mapped('tinh_trang')) ==set(['tot']) and   dl_obj.is_ghom_tot
#     FIELDNAME_FIELDATTR['move_line_ids.tinh_trang']['skip_field'] = skip_tinh_trang_field
    
    add_title(worksheet, FIELDNAME_FIELDATTR, 
              model_fields, ROW_TITLE=row_index,
               offset_column=0,
               is_set_width = False,
               font_height=font_height
#                is_auto_width = False
               )
    nrow = 0
    row_index +=1
    wrap_center_vert_border_style = xlwt.easyxf(generate_easyxf(height=font_height,vert = 'center',borders='left thin, right thin, top thin, bottom thin',align_wrap=True))
    for move in all_objs:#request.env['cvi'].search([]):
        rowspan = len(move.move_line_ids)
        for ml_index, ml in enumerate(move.move_line_ids):
            nrow +=1
            add_1_row_new_ml(worksheet, move , FIELDNAME_FIELDATTR, 
                             row_index, offset_column=0,
                             needdata=needdata,
                             save_ndata=True, ml=ml, ml_index=ml_index,rowspan=rowspan,
                             font_height=font_height,
                             wrap_center_vert_border_style = wrap_center_vert_border_style

                             )
            row_index +=1
    return nrow



def stt_ml_(v,needdata,m,ml,is_same,ml_index): 
    v = needdata['a_instance_dict']['move_line_ids.stt_not_model']['val']
    if is_same and ml_index:
        return v
    else:
        return v +1   

def ghi_chu_(val,n,move,ml, all_tot = False, IS_SET_TT_COL=False,empty = False):
    if empty:
        return False
    tinh_trang = ml.tinh_trang
    
    if not val:
        ghi_chu =  move.ghi_chu
    else:
        ghi_chu =  val
    if not (IS_SET_TT_COL or  all_tot):# ghop tinh trang vao #not IS_SET_TT_COL and  not all_tot, not (IS_SET_TT_COL or all_tot)
        
        tinh_trang_show = TINH_TRANG[tinh_trang]
        if ghi_chu:
            ghi_chu =  u'%s, %s'%(tinh_trang_show,ghi_chu) #aha
        else:
            ghi_chu = u'%s'%tinh_trang_show
    return ghi_chu

def is_same_ghi_chu_(m,ml, all_tot = False, IS_SET_TT_COL=False):
    is_same_tt = len(set(m.move_line_ids.mapped('tinh_trang'))) <=1
    is_same_gc = len(set(m.move_line_ids.mapped('ghi_chu'))) <=1
    if (IS_SET_TT_COL or  all_tot):
        return is_same_gc
    else:
        is_same_gc = is_same_gc and is_same_tt
        return is_same_gc
    

def is_same_(m,ml):
    if m.product_id.tracking == 'none':
        is_same = False
    else:
        is_same = True
    return is_same

def quantity_done_(v,n,m,l):
    if m.product_id.tracking == 'none':
        qty = l.qty_done
    else:
        qty = v
    return qty
TINH_TRANG = {'tot':u'Tốt','hong':u'Hỏng'}
def tinh_trang_(v,n,m,l):
    return TINH_TRANG[v]
def gen_domain_sml(dl_obj):
    domain = []
    domain.append(('picking_id','=',dl_obj.id))
    return domain
def download_ml_for_bb(dl_obj,workbook=None,
                       append_domain=None,
                       sheet_name=None,
                       worksheet=None,
                       row_index=0,
                       IS_SET_TT_COL=False,
                       all_tot_and_ghom_all_tot=False,
                       font_height=12):
    center_border_style = xlwt.easyxf(generate_easyxf(height=font_height,borders='left thin, right thin, top thin, bottom thin',vert = 'center',horiz = 'center'))
    FIELDNAME_FIELDATTR_ML = [
         ('move_line_ids.stt_not_model',{'is_not_model_field':True,'string':u'STT', 'func':stt_ml_,'is_same':True,
                                         'is_use_kargs_co_san':True,'style':center_border_style }),#'is_same':False 
         ('product_id',{'func':lambda v,n,m,ml: v.name,'string':u'Tên vật tư' }),
         ('product_id_pn',{'transfer_field':'product_id','func':lambda v,n,m,ml: v.pn,'string':u'Mã vật tư'}),
         ('quantity_done',{'is_same':is_same_,'func':quantity_done_,'string':u'S/L','style':center_border_style}),
         ('product_uom',{'func':lambda v,n,m,ml: v.name,'string':u'ĐVT'}),
         ('move_line_ids.lot_id',{'func':lambda v,n,m,ml: v.name,'string':u'Serial Number'}),
         ('move_line_ids.tinh_trang',{'string':u'T/T','func':tinh_trang_, 'skip_field':not IS_SET_TT_COL or  all_tot_and_ghom_all_tot    }),
         ('move_line_ids.ghi_chu',{'string':u'Ghi chú',
                                   'is_same':is_same_ghi_chu_,
                                   'kargs_for_is_same':{'all_tot':all_tot_and_ghom_all_tot, 'IS_SET_TT_COL':IS_SET_TT_COL},
                                   'func':ghi_chu_,
                                   'kargs':{'empty':dl_obj.empty_ghi_chu_in_bb,
                                            'all_tot':all_tot_and_ghom_all_tot,
                                             'IS_SET_TT_COL':IS_SET_TT_COL},
                                             }),
        ]
    Export_Para_ml = {
        'exported_model':'stock.move',
        'FIELDNAME_FIELDATTR':FIELDNAME_FIELDATTR_ML,
        'gen_domain':gen_domain_sml,
        'search_para':{'order': 'id asc'},#desc
        }
    
    return download_model_new_ml(dl_obj, Export_Para=Export_Para_ml, append_domain=append_domain,
                                 workbook=workbook,
                                 sheet_name=sheet_name,
                                 worksheet=worksheet,
                                 row_index=row_index,
                                 font_height = font_height) + 1