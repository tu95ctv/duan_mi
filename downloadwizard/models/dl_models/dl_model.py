# -*- coding: utf-8 -*-
from openerp.http import request
import datetime
from odoo.tools.misc import xlwt
from odoo.exceptions import UserError
from collections import  OrderedDict


def generate_easyxf (font='Times New Roman', 
                     bold = False,
                     underline=False,
                     height=12, 
                     align_wrap = False,
                     vert = False,
                     horiz = False,
                     borders = False,
                     pattern = False,
                     italic= False
                     ):
    fonts = []
    fonts.append('name %s'%font)
    if underline:
        fonts.append('underline on')
    if bold:
        fonts.append('bold on')
        
    if italic:
        fonts.append('italic on')
        
    fonts.append('height %s'%(height*20))
    sums = []
    font = 'font: ' + ','.join(fonts)
    sums.append(font)
    
    aligns = []
    if vert:
        aligns.append('vert %s'%vert)
    if horiz:
        aligns.append('horiz %s'%horiz)
    if align_wrap:
        aligns.append('wrap on')
        
    if aligns:
        align = 'align:  ' + ','.join(aligns)
#         font = font + '; ' + align
        sums.append(align)
    
  
    if borders:
        borders = 'borders: ' + borders
        sums.append(borders) 
    
    if pattern:
        pattern = 'pattern: ' + pattern
        sums.append(pattern)
        
    sums = ';'.join(sums)   
    
    return sums



def stt_(v,needdata): 
    v = needdata['a_instance_dict']['stt_not_model']['val']  +1   
    return v  

def get_width(num_characters,font_height=12):
    return int((1+num_characters) * 256*font_height/12)

# font_height = request.env['ir.config_parameter'].sudo().get_param('tonkho.' + 'font_height')
# if not font_height:
#     HEIGHT = 12
# else:
#     HEIGHT = font_height
# normal_style = xlwt.easyxf("font:  name Times New Roman, height 240")
HEIGHT = 12
# Border:
header_bold_style = xlwt.easyxf(generate_easyxf(height=HEIGHT,bold=True,vert = 'center',horiz='center',borders='left thin, right thin, top thin, bottom thin',pattern = 'pattern solid, fore_colour gray25'))
header_bold_style_no_gray =xlwt.easyxf(generate_easyxf(bold=True,vert = 'center',horiz='center',borders='left thin, right thin, top thin, bottom thin'))
center_vert_border_style = xlwt.easyxf(generate_easyxf(height=HEIGHT,borders='left thin, right thin, top thin, bottom thin',vert = 'center'))
wrap_center_vert_border_style = xlwt.easyxf(generate_easyxf(height=HEIGHT,vert = 'center',borders='left thin, right thin, top thin, bottom thin',align_wrap=True))
center_border_style = xlwt.easyxf(generate_easyxf(height=HEIGHT,borders='left thin, right thin, top thin, bottom thin',vert = 'center',horiz = 'center'))

# normal
normal_style = xlwt.easyxf(generate_easyxf(height=HEIGHT))  # sửa chiều cao
wrap_normal_style = xlwt.easyxf(generate_easyxf(height=HEIGHT,align_wrap=True))  
center_style = xlwt.easyxf(generate_easyxf(height=HEIGHT,vert = 'center',horiz='center'))
vert_center_style = xlwt.easyxf(generate_easyxf(vert = 'center'))#ông bà

#bold
bold_italic_style = xlwt.easyxf(generate_easyxf(bold=True,height=HEIGHT,italic=True))
bold_center_style = xlwt.easyxf(generate_easyxf(height=HEIGHT, vert = 'center',horiz = 'center',bold=True))
# bold_style = xlwt.easyxf("font: bold on, name Times New Roman, height 240;")
bold_style = xlwt.easyxf(generate_easyxf(height=HEIGHT,bold=True))

bold_center_18_style = xlwt.easyxf(generate_easyxf(bold=True,height=18, vert = 'center',horiz = 'center'))




def add_1_row(worksheet,r ,FIELDNAME_FIELDATTR, row_index, 
            offset_column=0,
            needdata=None,
            save_ndata=False,
            dl_model_para=None,
            center_vert_border_style=center_vert_border_style,
#             font_height= 12
            ):
    if save_ndata:
        a_instance_dict =  needdata.get('a_instance_dict', {})
    else:
        a_instance_dict = {}
    writen_column_number = 0
    col_index = 0
    col_index += offset_column
    for  f_name,FIELDATTR in FIELDNAME_FIELDATTR.items():
        skip_field = FIELDATTR.get('skip_field')
        if callable(skip_field):
            skip_field = skip_field(dl_model_para)
        if skip_field:
            continue
        is_not_model_field = FIELDATTR.get('is_not_model_field')
        split = FIELDATTR.get('split')
        write_to_excel = FIELDATTR.get('write_to_excel',True)
        transfer_fname = FIELDATTR.get('transfer_fname')
        f_name_real =transfer_fname or  f_name
        if is_not_model_field:
            val = False
        else:
            val = getattr(r, f_name_real)
        one_field_val = a_instance_dict.setdefault(f_name,{})
        one_field_val['val_before_func'] = val
        func = FIELDATTR.get('func',None)
        kargs = FIELDATTR.get('kargs',{})
        if func:
            val = func(val,needdata, **kargs)
        else:
            if hasattr(val, 'name'):
                val = val.name
        if val == False:
            val = u''
        one_field_val['val']=val 
        max_len_field_val =  FIELDATTR.setdefault('max_len_field_val',0)
        val_len = len(val) if isinstance(val, str) else 0
        if val_len > max_len_field_val:
            FIELDATTR['max_len_field_val'] = val_len
        if  write_to_excel:
            style = FIELDATTR.get('style',center_vert_border_style)
            worksheet.write(row_index, col_index, val, style)
            writen_column_number +=1
            col_index +=1
        else:
            pass
        if split:
            a_instance_dict,writen_column_number_children = add_1_row(worksheet,r ,split, row_index, offset_column=col_index  ,needdata=needdata)
            offset_column += writen_column_number_children -1 +  (1 if write_to_excel else 0)
            writen_column_number += writen_column_number_children
            one_field_val['split'] = a_instance_dict
            col_index +=writen_column_number_children
    return a_instance_dict, writen_column_number


def add_title(worksheet,FIELDNAME_FIELDATTR,model_fields,ROW_TITLE=0, offset_column=0,
               is_set_width = True,
               no_gray = False,
#               is_auto_width = True,
#                for_len_adj = False
                dl_model_para=None,
                font_height = 12,
                max_header_char_number=0
               ):
    
    header_bold_style = xlwt.easyxf(generate_easyxf(height=font_height,bold=True,vert = 'center',horiz='center',borders='left thin, right thin, top thin, bottom thin',pattern = 'pattern solid, fore_colour gray25'))
    header_bold_style_no_gray =xlwt.easyxf(generate_easyxf(height=font_height,bold=True,vert = 'center',horiz='center',borders='left thin, right thin, top thin, bottom thin'))
    writen_column_number = 0
    column_index = offset_column
    for f_name, FIELDATTR in  FIELDNAME_FIELDATTR.items():
        is_not_model_field = FIELDATTR.get('is_not_model_field')
        skip_field = FIELDATTR.get('skip_field')
        if callable(skip_field):
            skip_field = skip_field(dl_model_para)
        if skip_field:
            continue
        split = FIELDATTR.get('split')
        write_to_excel = FIELDATTR.get('write_to_excel',True)
        if is_not_model_field:
            header_string =FIELDATTR.get('string') or  f_name
        else:
            header_string =FIELDATTR.get('string')
            if not header_string:
                field = model_fields[f_name]
                header_string = field.string
            else:
                if callable(header_string):
                    header_string = header_string(dl_model_para)
        if write_to_excel:
            if no_gray:
                title_style = header_bold_style_no_gray
            else:
                title_style = header_bold_style
                
            worksheet.write(ROW_TITLE, column_index, header_string, title_style)
            writen_column_number += 1
            
            if is_set_width:
                char_number =FIELDATTR.get('width')
                if not char_number:
                    char_number = FIELDATTR.get('max_len_field_val',0)
                    if max_header_char_number and char_number > max_header_char_number:
                        char_number = max_header_char_number
#                     width  = get_width(char_number) #or width
                    
#                     header_string_width = get_width(len(header_string) + 2,font_height)
                    
                    header_char_number = len(header_string)
                    if header_char_number > char_number:
                        char_number = header_char_number
                worksheet.col(column_index).width = get_width(char_number + 4,font_height)
            column_index +=1
        else:
            pass
        if split:
            writen_column_number_child = add_title(worksheet,split, model_fields,ROW_TITLE=ROW_TITLE, offset_column=column_index,no_gray=no_gray)
            print ("writen_column_number_child",writen_column_number_child)
            column_index +=writen_column_number_child
            writen_column_number += writen_column_number_child
    return writen_column_number


def download_model(dl_obj,
                    Export_Para=None,
                    workbook=None,
                    append_domain=None,
                    sheet_name=None,
                    worksheet = None,
                    ROW_TITLE = 0,
                    return_more_thing_for_bcn = False,
                    write_before_title = None,
                    kargs_write_before_title = None,
                    no_gray = False,
                    is_set_width = True,
                    dl_model_para = None,
                    OFFSET_COLUMN = 0,
                    write_title_even_not_recs = True,
                    write_title_even_not_recs_for_title = True,
                    font_height = 12
                    ):
    font_height = dl_obj.font_height# or font_height or 12
#     global dl_obj_global
#     dl_obj_global = dl_obj
    exported_model= Export_Para['exported_model']
    max_header_char_number = Export_Para.get('max_header_char_number')
    FIELDNAME_FIELDATTR= Export_Para['FIELDNAME_FIELDATTR']
    FIELDNAME_FIELDATTR = recursive_OrderedDict(FIELDNAME_FIELDATTR)
#     print ('**FIELDNAME_FIELDATTR***',FIELDNAME_FIELDATTR)
    gen_domain= Export_Para.get('gen_domain')
    
    # đưa wb,ws_name  ;  đưa ws ; ko đưa chi cả
    if not worksheet:
        if workbook==None:
            workbook = xlwt.Workbook()
        if sheet_name ==None:
            sheet_name =  u'Sheet 1'
        worksheet = workbook.add_sheet(sheet_name)# cell_overwrite_ok=True

        
        
    needdata = {'a_instance_dict':{'stt_not_model':{'val':0}}}
    needdata['dl_obj'] = dl_obj
    model_fields = request.env[exported_model]._fields
    
#     add_title(worksheet, FIELDNAME_FIELDATTR, model_fields, ROW_TITLE=ROW_TITLE, offset_column=OFFSET_COLUMN)
    if gen_domain:
        domain = gen_domain(dl_obj)
    else:
        domain = []
    if append_domain:
        domain.extend(append_domain)  
    order = Export_Para.get('search_para',{'order': 'id asc'})
    recs = request.env[exported_model].search(domain,**order)
   
    
    n_row_title = 0
    if (recs or write_title_even_not_recs) and write_before_title:
        ROW_TITLE +=1
        n_row_title+= 1
        write_before_title (kargs_write_before_title)
    
    center_vert_border_style = xlwt.easyxf(generate_easyxf(height=font_height,borders='left thin, right thin, top thin, bottom thin',vert = 'center'))

    row_index = ROW_TITLE 
    if  recs:
        for r in recs:#request.env['cvi'].search([]):
            row_index +=  1
            add_1_row(worksheet,r, 
                      FIELDNAME_FIELDATTR, 
                       row_index,
                       offset_column=OFFSET_COLUMN,
                       needdata=needdata,
                       save_ndata=True,
                       dl_model_para=dl_model_para,
                       center_vert_border_style = center_vert_border_style)
        n_row_recs = row_index - (ROW_TITLE + 1) + 1
    else:
        n_row_recs = 0       
    if  recs or write_title_even_not_recs_for_title:
        add_title(worksheet, FIELDNAME_FIELDATTR, model_fields, ROW_TITLE=ROW_TITLE, 
                  offset_column=OFFSET_COLUMN,no_gray=no_gray,is_set_width=is_set_width,
                  dl_model_para=dl_model_para,
                  font_height = font_height,max_header_char_number=max_header_char_number)
        n_row_title += 1
    if return_more_thing_for_bcn:
        return n_row_recs + n_row_title
    return workbook
def recursive_OrderedDict (FIELDNAME_FIELDATTR):
    if isinstance(FIELDNAME_FIELDATTR,list):
        obj_loop= FIELDNAME_FIELDATTR
    else:
        obj_loop= FIELDNAME_FIELDATTR.items()
    for fname,attr in obj_loop:
        split = attr.get('split')
        if split:
            attr['split'] = recursive_OrderedDict(split)
    if isinstance(FIELDNAME_FIELDATTR,list):
        return OrderedDict(FIELDNAME_FIELDATTR)
    else:
        return FIELDNAME_FIELDATTR
def write_all_row(fixups,dl_obj,set_cols_width,wb=None,ws_name=None,font_height=12):
    normal_style = xlwt.easyxf(generate_easyxf(height=font_height))
    needdata = {}
    if not ws_name:
        ws_name = u'First'
    if not wb:
        wb = xlwt.Workbook()
    ws = wb.add_sheet(ws_name)#cell_overwrite_ok=True
#     ws.header_str = 0
#     ws.footer_str = 0
#     
#     ws.__header_str = 'adfdfdf'
#     ws.__footer_str = 'adfdfdf'
#     worksheet.PageSetup.CenterHeader = ''
#     worksheet.PageSetup.CenterFooter = ''
    if set_cols_width:
        for col,width in enumerate(set_cols_width):
            ws.col(col).width =  width
    fixups = OrderedDict(fixups)
    instance_dict = {}
    needdata['instance_dict'] = instance_dict
    for f_name,field_attr in fixups.items():
        a_field_dict = {}
        xrange = field_attr.get('range')
        offset = field_attr.get('offset',1)
        if callable(offset):
            offset_kargs = field_attr.get('offset_kargs',{})
            offset = offset(needdata,**offset_kargs)
        style = field_attr.get('style',normal_style)
        if xrange[0]=='auto':
            row = needdata['cr'] + offset
            xrange[0] = row
            if xrange[1] == 'auto':
                xrange[1] = row
        else:
            row = xrange[0]
        val = field_attr.get('val')
        val_func = field_attr.get('val_func')
        if val_func:
            val_kargs =  field_attr.get('val_kargs',{})
            val = val_func(ws,f_name,fixups,needdata,row,dl_obj,**val_kargs)
        func = field_attr.get('func')
        instance_dict[f_name]=a_field_dict
        a_field_dict['begin_row'] = row
        if func:
            kargs = field_attr.get('kargs',{})
            nrow = func(ws,f_name,fixups,needdata,row,dl_obj, **kargs)
            if nrow:
                cr_new = row + nrow  
                needdata['cr'] = cr_new
            a_field_dict['end_row'] = needdata['cr']
        else:
            a_field_dict['val'] = val
            if val != None:
                if len(xrange) ==2:
                    ws.write(xrange[0], xrange[1], val, style)
                elif len(xrange)==4:
                    ws.write_merge(xrange[0], xrange[1],xrange[2], xrange[3], val, style)
                needdata['cr'] = xrange[0]
        height =  field_attr.get('height',400)
        if height != None:
            ws.row(row).height_mismatch = True
            ws.row(row).height = height
    return wb




