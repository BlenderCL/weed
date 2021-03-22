# -*- coding: utf-8 -*-
"""
    pygments.lexers._scilab_builtins
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Builtin list for the ScilabLexer.

    :copyright: Copyright 2006-2013 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

# These lists are generated automatically.
# Run the following in a Scilab script:
#
# varType=["functions", "commands", "macros", "variables" ];
# fd = mopen('list.txt','wt');
#
# for j=1:size(varType,"*")
#     myStr="";
#     a=completion("",varType(j));
#     myStr=varType(j)+"_kw = [";
#     for i=1:size(a,"*")
#         myStr = myStr + """" + a(i) + """";
#         if size(a,"*") <> i then
#            myStr = myStr + ","; end
#         end
#     myStr = myStr + "]";
#     mputl(myStr,fd);
# end
# mclose(fd);
#
# Then replace "$" by "\\$" manually.

functions_kw = ["%XMLAttr_6","%XMLAttr_e","%XMLAttr_i_XMLElem","%XMLAttr_length","%XMLAttr_p","%XMLAttr_size","%XMLDoc_6","%XMLDoc_e","%XMLDoc_i_XMLList","%XMLDoc_p","%XMLElem_6","%XMLElem_e","%XMLElem_i_XMLDoc","%XMLElem_i_XMLElem","%XMLElem_i_XMLList","%XMLElem_p","%XMLList_6","%XMLList_e","%XMLList_i_XMLElem","%XMLList_i_XMLList","%XMLList_length","%XMLList_p","%XMLList_size","%XMLNs_6","%XMLNs_e","%XMLNs_i_XMLElem","%XMLNs_p","%XMLSet_6","%XMLSet_e","%XMLSet_length","%XMLSet_p","%XMLSet_size","%XMLValid_p","%b_i_XMLList","%c_i_XMLAttr","%c_i_XMLDoc","%c_i_XMLElem","%c_i_XMLList","%ce_i_XMLList","%fptr_i_XMLList","%h_i_XMLList","%hm_i_XMLList","%i_abs","%i_cumprod","%i_cumsum","%i_diag","%i_i_XMLList","%i_matrix","%i_max","%i_maxi","%i_min","%i_mini","%i_mput","%i_p","%i_prod","%i_sum","%i_tril","%i_triu","%ip_i_XMLList","%l_i_XMLList","%lss_i_XMLList","%mc_i_XMLList","%msp_full","%msp_i_XMLList","%msp_spget","%p_i_XMLList","%ptr_i_XMLList","%r_i_XMLList","%s_i_XMLList","%sp_i_XMLList","%spb_i_XMLList","%st_i_XMLList","Calendar","ClipBoard","Matplot","Matplot1","PlaySound","TCL_DeleteInterp","TCL_DoOneEvent","TCL_EvalFile","TCL_EvalStr","TCL_ExistArray","TCL_ExistInterp","TCL_ExistVar","TCL_GetVar","TCL_GetVersion","TCL_SetVar","TCL_UnsetVar","TCL_UpVar","_","_code2str","_str2code","about","abs","acos","addcb","addf","addhistory","addinter","amell","and","argn","arl2_ius","ascii","asin","atan","backslash","balanc","banner","base2dec","basename","bdiag","beep","besselh","besseli","besselj","besselk","bessely","beta","bezout","bfinit","blkfc1i","blkslvi","bool2s","browsehistory","browsevar","bsplin3val","buildDocv2","buildouttb","bvode","c_link","calerf","call","callblk","captions","cd","cdfbet","cdfbin","cdfchi","cdfchn","cdff","cdffnc","cdfgam","cdfnbn","cdfnor","cdfpoi","cdft","ceil","champ","champ1","chdir","chol","clc","clean","clear","clear_pixmap","clearfun","clearglobal","closeEditor","closeXcos","code2str","coeff","comp","completion","conj","contour2di","contr","conv2","convstr","copy","copyfile","corr","cos","coserror","createdir","cshep2d","ctree2","ctree3","ctree4","cumprod","cumsum","curblock","curblockc","dasrt","dassl","data2sig","debug","dec2base","deff","definedfields","degree","delbpt","delete","deletefile","delip","delmenu","det","dgettext","dhinf","diag","diary","diffobjs","disp","dispbpt","displayhistory","disposefftwlibrary","dlgamma","dnaupd","dneupd","double","draw","drawaxis","drawlater","drawnow","dsaupd","dsearch","dseupd","duplicate","editor","editvar","emptystr","end_scicosim","ereduc","errcatch","errclear","error","eval_cshep2d","exec","execstr","exists","exit","exp","expm","exportUI","export_to_hdf5","eye","fadj2sp","fec","feval","fft","fftw","fftw_flags","fftw_forget_wisdom","fftwlibraryisloaded","file","filebrowser","fileext","fileinfo","fileparts","filesep","find","findBD","findfiles","floor","format","fort","fprintfMat","freq","frexp","fromc","fromjava","fscanfMat","fsolve","fstair","full","fullpath","funcprot","funptr","gamma","gammaln","geom3d","get","get_absolute_file_path","get_fftw_wisdom","getblocklabel","getcallbackobject","getdate","getdebuginfo","getdefaultlanguage","getdrives","getdynlibext","getenv","getfield","gethistory","gethistoryfile","getinstalledlookandfeels","getio","getlanguage","getlongpathname","getlookandfeel","getmd5","getmemory","getmodules","getos","getpid","getrelativefilename","getscicosvars","getscilabmode","getshortpathname","gettext","getvariablesonstack","getversion","glist","global","glue","grand","grayplot","grep","gsort","gstacksize","havewindow","helpbrowser","hess","hinf","historymanager","historysize","host","iconvert","iconvert","ieee","ilib_verbose","imag","impl","import_from_hdf5","imult","inpnvi","int","int16","int2d","int32","int3d","int8","interp","interp2d","interp3d","intg","intppty","inttype","inv","is_handle_valid","isalphanum","isascii","isdef","isdigit","isdir","isequal","isequalbitwise","iserror","isfile","isglobal","isletter","isreal","iswaitingforinput","javaclasspath","javalibrarypath","kron","lasterror","ldiv","ldivf","legendre","length","lib","librarieslist","libraryinfo","linear_interpn","lines","link","linmeq","list","load","loadScicos","loadfftwlibrary","loadhistory","log","log1p","lsq","lsq_splin","lsqrsolve","lsslist","lstcat","lstsize","ltitr","lu","ludel","lufact","luget","lusolve","macr2lst","macr2tree","matfile_close","matfile_listvar","matfile_open","matfile_varreadnext","matfile_varwrite","matrix","max","maxfiles","mclearerr","mclose","meof","merror","messagebox","mfprintf","mfscanf","mget","mgeti","mgetl","mgetstr","min","mlist","mode","model2blk","mopen","move","movefile","mprintf","mput","mputl","mputstr","mscanf","mseek","msprintf","msscanf","mtell","mtlb_mode","mtlb_sparse","mucomp","mulf","nearfloat","newaxes","newest","newfun","nnz","notify","number_properties","ode","odedc","ones","opentk","optim","or","ordmmd","parallel_concurrency","parallel_run","param3d","param3d1","part","pathconvert","pathsep","phase_simulation","plot2d","plot2d1","plot2d2","plot2d3","plot2d4","plot3d","plot3d1","pointer_xproperty","poly","ppol","pppdiv","predef","print","printf","printfigure","printsetupbox","prod","progressionbar","prompt","pwd","qld","qp_solve","qr","raise_window","rand","rankqr","rat","rcond","rdivf","read","read4b","readb","readgateway","readmps","real","realtime","realtimeinit","regexp","relocate_handle","remez","removedir","removelinehistory","res_with_prec","resethistory","residu","resume","return","ricc","ricc_old","rlist","roots","rotate_axes","round","rpem","rtitr","rubberbox","save","saveafterncommands","saveconsecutivecommands","savehistory","schur","sci_haltscicos","sci_tree2","sci_tree3","sci_tree4","sciargs","scicos_debug","scicos_debug_count","scicos_time","scicosim","scinotes","sctree","semidef","set","set_blockerror","set_fftw_wisdom","set_xproperty","setbpt","setdefaultlanguage","setenv","setfield","sethistoryfile","setlanguage","setlookandfeel","setmenu","sfact","sfinit","show_pixmap","show_window","showalluimenushandles","sident","sig2data","sign","simp","simp_mode","sin","size","slash","sleep","sorder","sparse","spchol","spcompack","spec","spget","splin","splin2d","splin3d","spones","sprintf","sqrt","stacksize","str2code","strcat","strchr","strcmp","strcspn","strindex","string","stringbox","stripblanks","strncpy","strrchr","strrev","strsplit","strspn","strstr","strsubst","strtod","strtok","subf","sum","svd","swap_handles","symfcti","syredi","system_getproperty","system_setproperty","ta2lpd","tan","taucs_chdel","taucs_chfact","taucs_chget","taucs_chinfo","taucs_chsolve","tempname","testmatrix","timer","tlist","tohome","tokens","toolbar","toprint","tr_zer","tril","triu","type","typename","uiDisplayTree","uicontextmenu","uicontrol","uigetcolor","uigetdir","uigetfile","uigetfont","uimenu","uint16","uint32","uint8","uipopup","uiputfile","uiwait","ulink","umf_ludel","umf_lufact","umf_luget","umf_luinfo","umf_lusolve","umfpack","unglue","unix","unsetmenu","unzoom","updatebrowsevar","usecanvas","user","var2vec","varn","vec2var","waitbar","warnBlockByUID","warning","what","where","whereis","who","winsid","with_embedded_jre","with_module","writb","write","write4b","x_choose","x_choose_modeless","x_dialog","x_mdialog","xarc","xarcs","xarrows","xchange","xchoicesi","xclick","xcos","xcosAddToolsMenu","xcosConfigureXmlFile","xcosDiagramToScilab","xcosPalCategoryAdd","xcosPalDelete","xcosPalDisable","xcosPalEnable","xcosPalGenerateIcon","xcosPalLoad","xcosPalMove","xcosUpdateBlock","xdel","xfarc","xfarcs","xfpoly","xfpolys","xfrect","xget","xgetech","xgetmouse","xgraduate","xgrid","xlfont","xls_open","xls_read","xmlAddNs","xmlAsNumber","xmlAsText","xmlDTD","xmlDelete","xmlDocument","xmlDump","xmlElement","xmlFormat","xmlGetNsByHref","xmlGetNsByPrefix","xmlGetOpenDocs","xmlIsValidObject","xmlNs","xmlRead","xmlReadStr","xmlRelaxNG","xmlRemove","xmlSchema","xmlSetAttributes","xmlValidate","xmlWrite","xmlXPath","xname","xpause","xpoly","xpolys","xrect","xrects","xs2bmp","xs2eps","xs2gif","xs2jpg","xs2pdf","xs2png","xs2ppm","xs2ps","xs2svg","xsegs","xset","xsetech","xstring","xstringb","xtitle","zeros","znaupd","zneupd","zoom_rect"]

commands_kw = ["abort","apropos","break","case","catch","clc","clear","continue","do","else","elseif","end","endfunction","exit","for","function","help","if","pause","pwd","quit","resume","return","select","then","try","what","while","who"]

macros_kw = ["%0_i_st","%3d_i_h","%Block_xcosUpdateBlock","%TNELDER_p","%TNELDER_string","%TNMPLOT_p","%TNMPLOT_string","%TOPTIM_p","%TOPTIM_string","%TSIMPLEX_p","%TSIMPLEX_string","%_gsort","%_strsplit","%ar_p","%asn","%b_a_b","%b_a_s","%b_c_s","%b_c_spb","%b_cumprod","%b_cumsum","%b_d_s","%b_diag","%b_e","%b_f_s","%b_f_spb","%b_g_s","%b_g_spb","%b_h_s","%b_h_spb","%b_i_b","%b_i_ce","%b_i_h","%b_i_hm","%b_i_s","%b_i_sp","%b_i_spb","%b_i_st","%b_iconvert","%b_l_b","%b_l_s","%b_m_b","%b_m_s","%b_matrix","%b_n_hm","%b_o_hm","%b_p_s","%b_prod","%b_r_b","%b_r_s","%b_s_b","%b_s_s","%b_string","%b_sum","%b_tril","%b_triu","%b_x_b","%b_x_s","%c_a_c","%c_b_c","%c_b_s","%c_diag","%c_e","%c_eye","%c_f_s","%c_i_c","%c_i_ce","%c_i_h","%c_i_hm","%c_i_lss","%c_i_r","%c_i_s","%c_i_st","%c_matrix","%c_n_l","%c_n_st","%c_o_l","%c_o_st","%c_ones","%c_rand","%c_tril","%c_triu","%cblock_c_cblock","%cblock_c_s","%cblock_e","%cblock_f_cblock","%cblock_p","%cblock_size","%ce_6","%ce_c_ce","%ce_e","%ce_f_ce","%ce_i_ce","%ce_i_s","%ce_i_st","%ce_matrix","%ce_p","%ce_size","%ce_string","%ce_t","%champdat_i_h","%choose","%diagram_xcos","%dir_p","%fptr_i_st","%grayplot_i_h","%h_i_st","%hm_1_hm","%hm_1_s","%hm_2_hm","%hm_2_s","%hm_3_hm","%hm_3_s","%hm_4_hm","%hm_4_s","%hm_5","%hm_a_hm","%hm_a_r","%hm_a_s","%hm_abs","%hm_and","%hm_bool2s","%hm_c_hm","%hm_ceil","%hm_conj","%hm_cos","%hm_cumprod","%hm_cumsum","%hm_d_hm","%hm_d_s","%hm_degree","%hm_e","%hm_exp","%hm_f_hm","%hm_fft","%hm_find","%hm_floor","%hm_g_hm","%hm_h_hm","%hm_i_b","%hm_i_ce","%hm_i_hm","%hm_i_i","%hm_i_p","%hm_i_r","%hm_i_s","%hm_i_st","%hm_iconvert","%hm_imag","%hm_int","%hm_isnan","%hm_isreal","%hm_j_hm","%hm_j_s","%hm_k_hm","%hm_k_s","%hm_log","%hm_m_p","%hm_m_r","%hm_m_s","%hm_matrix","%hm_maxi","%hm_mean","%hm_median","%hm_mini","%hm_n_b","%hm_n_c","%hm_n_hm","%hm_n_i","%hm_n_p","%hm_n_s","%hm_o_b","%hm_o_c","%hm_o_hm","%hm_o_i","%hm_o_p","%hm_o_s","%hm_ones","%hm_or","%hm_p","%hm_prod","%hm_q_hm","%hm_r_s","%hm_rand","%hm_real","%hm_round","%hm_s","%hm_s_hm","%hm_s_r","%hm_s_s","%hm_sign","%hm_sin","%hm_size","%hm_sqrt","%hm_st_deviation","%hm_string","%hm_sum","%hm_x_hm","%hm_x_p","%hm_x_s","%hm_zeros","%i_1_s","%i_2_s","%i_3_s","%i_4_s","%i_Matplot","%i_a_i","%i_a_s","%i_and","%i_ascii","%i_b_s","%i_bezout","%i_champ","%i_champ1","%i_contour","%i_contour2d","%i_d_i","%i_d_s","%i_e","%i_fft","%i_g_i","%i_gcd","%i_h_i","%i_i_ce","%i_i_h","%i_i_hm","%i_i_i","%i_i_s","%i_i_st","%i_j_i","%i_j_s","%i_l_s","%i_lcm","%i_length","%i_m_i","%i_m_s","%i_mfprintf","%i_mprintf","%i_msprintf","%i_n_s","%i_o_s","%i_or","%i_p_i","%i_p_s","%i_plot2d","%i_plot2d1","%i_plot2d2","%i_q_s","%i_r_i","%i_r_s","%i_round","%i_s_i","%i_s_s","%i_sign","%i_string","%i_x_i","%i_x_s","%ip_a_s","%ip_i_st","%ip_m_s","%ip_n_ip","%ip_o_ip","%ip_p","%ip_s_s","%ip_string","%k","%l_i_h","%l_i_s","%l_i_st","%l_isequal","%l_n_c","%l_n_l","%l_n_m","%l_n_p","%l_n_s","%l_n_st","%l_o_c","%l_o_l","%l_o_m","%l_o_p","%l_o_s","%l_o_st","%lss_a_lss","%lss_a_p","%lss_a_r","%lss_a_s","%lss_c_lss","%lss_c_p","%lss_c_r","%lss_c_s","%lss_e","%lss_eye","%lss_f_lss","%lss_f_p","%lss_f_r","%lss_f_s","%lss_i_ce","%lss_i_lss","%lss_i_p","%lss_i_r","%lss_i_s","%lss_i_st","%lss_inv","%lss_l_lss","%lss_l_p","%lss_l_r","%lss_l_s","%lss_m_lss","%lss_m_p","%lss_m_r","%lss_m_s","%lss_n_lss","%lss_n_p","%lss_n_r","%lss_n_s","%lss_norm","%lss_o_lss","%lss_o_p","%lss_o_r","%lss_o_s","%lss_ones","%lss_r_lss","%lss_r_p","%lss_r_r","%lss_r_s","%lss_rand","%lss_s","%lss_s_lss","%lss_s_p","%lss_s_r","%lss_s_s","%lss_size","%lss_t","%lss_v_lss","%lss_v_p","%lss_v_r","%lss_v_s","%lt_i_s","%m_n_l","%m_o_l","%mc_i_h","%mc_i_s","%mc_i_st","%mc_n_st","%mc_o_st","%mc_string","%mps_p","%mps_string","%msp_a_s","%msp_abs","%msp_e","%msp_find","%msp_i_s","%msp_i_st","%msp_length","%msp_m_s","%msp_maxi","%msp_n_msp","%msp_nnz","%msp_o_msp","%msp_p","%msp_sparse","%msp_spones","%msp_t","%p_a_lss","%p_a_r","%p_c_lss","%p_c_r","%p_cumprod","%p_cumsum","%p_d_p","%p_d_r","%p_d_s","%p_det","%p_e","%p_f_lss","%p_f_r","%p_i_ce","%p_i_h","%p_i_hm","%p_i_lss","%p_i_p","%p_i_r","%p_i_s","%p_i_st","%p_inv","%p_j_s","%p_k_p","%p_k_r","%p_k_s","%p_l_lss","%p_l_p","%p_l_r","%p_l_s","%p_m_hm","%p_m_lss","%p_m_r","%p_matrix","%p_n_l","%p_n_lss","%p_n_r","%p_o_l","%p_o_lss","%p_o_r","%p_o_sp","%p_p_s","%p_prod","%p_q_p","%p_q_r","%p_q_s","%p_r_lss","%p_r_p","%p_r_r","%p_r_s","%p_s_lss","%p_s_r","%p_simp","%p_string","%p_sum","%p_v_lss","%p_v_p","%p_v_r","%p_v_s","%p_x_hm","%p_x_r","%p_y_p","%p_y_r","%p_y_s","%p_z_p","%p_z_r","%p_z_s","%r_a_hm","%r_a_lss","%r_a_p","%r_a_r","%r_a_s","%r_c_lss","%r_c_p","%r_c_r","%r_c_s","%r_clean","%r_cumprod","%r_d_p","%r_d_r","%r_d_s","%r_det","%r_diag","%r_e","%r_eye","%r_f_lss","%r_f_p","%r_f_r","%r_f_s","%r_i_ce","%r_i_hm","%r_i_lss","%r_i_p","%r_i_r","%r_i_s","%r_i_st","%r_inv","%r_j_s","%r_k_p","%r_k_r","%r_k_s","%r_l_lss","%r_l_p","%r_l_r","%r_l_s","%r_m_hm","%r_m_lss","%r_m_p","%r_m_r","%r_m_s","%r_matrix","%r_n_lss","%r_n_p","%r_n_r","%r_n_s","%r_norm","%r_o_lss","%r_o_p","%r_o_r","%r_o_s","%r_ones","%r_p","%r_p_s","%r_prod","%r_q_p","%r_q_r","%r_q_s","%r_r_lss","%r_r_p","%r_r_r","%r_r_s","%r_rand","%r_s","%r_s_hm","%r_s_lss","%r_s_p","%r_s_r","%r_s_s","%r_simp","%r_size","%r_string","%r_sum","%r_t","%r_tril","%r_triu","%r_v_lss","%r_v_p","%r_v_r","%r_v_s","%r_x_p","%r_x_r","%r_x_s","%r_y_p","%r_y_r","%r_y_s","%r_z_p","%r_z_r","%r_z_s","%s_1_hm","%s_1_i","%s_2_hm","%s_2_i","%s_3_hm","%s_3_i","%s_4_hm","%s_4_i","%s_5","%s_a_b","%s_a_hm","%s_a_i","%s_a_ip","%s_a_lss","%s_a_msp","%s_a_r","%s_a_sp","%s_and","%s_b_i","%s_b_s","%s_c_b","%s_c_cblock","%s_c_lss","%s_c_r","%s_c_sp","%s_d_b","%s_d_i","%s_d_p","%s_d_r","%s_d_sp","%s_e","%s_f_b","%s_f_cblock","%s_f_lss","%s_f_r","%s_f_sp","%s_g_b","%s_g_s","%s_h_b","%s_h_s","%s_i_b","%s_i_c","%s_i_ce","%s_i_h","%s_i_hm","%s_i_i","%s_i_lss","%s_i_p","%s_i_r","%s_i_s","%s_i_sp","%s_i_spb","%s_i_st","%s_j_i","%s_k_hm","%s_k_p","%s_k_r","%s_k_sp","%s_l_b","%s_l_hm","%s_l_i","%s_l_lss","%s_l_p","%s_l_r","%s_l_s","%s_l_sp","%s_m_b","%s_m_hm","%s_m_i","%s_m_ip","%s_m_lss","%s_m_msp","%s_m_r","%s_matrix","%s_n_hm","%s_n_i","%s_n_l","%s_n_lss","%s_n_r","%s_n_st","%s_o_hm","%s_o_i","%s_o_l","%s_o_lss","%s_o_r","%s_o_st","%s_or","%s_p_b","%s_p_i","%s_pow","%s_q_hm","%s_q_i","%s_q_p","%s_q_r","%s_q_sp","%s_r_b","%s_r_i","%s_r_lss","%s_r_p","%s_r_r","%s_r_s","%s_r_sp","%s_s_b","%s_s_hm","%s_s_i","%s_s_ip","%s_s_lss","%s_s_r","%s_s_sp","%s_simp","%s_v_lss","%s_v_p","%s_v_r","%s_v_s","%s_x_b","%s_x_hm","%s_x_i","%s_x_r","%s_y_p","%s_y_r","%s_y_sp","%s_z_p","%s_z_r","%s_z_sp","%sn","%sp_a_s","%sp_a_sp","%sp_and","%sp_c_s","%sp_ceil","%sp_cos","%sp_cumprod","%sp_cumsum","%sp_d_s","%sp_d_sp","%sp_diag","%sp_e","%sp_exp","%sp_f_s","%sp_floor","%sp_gsort","%sp_i_ce","%sp_i_h","%sp_i_s","%sp_i_sp","%sp_i_st","%sp_int","%sp_inv","%sp_k_s","%sp_k_sp","%sp_l_s","%sp_l_sp","%sp_length","%sp_norm","%sp_or","%sp_p_s","%sp_prod","%sp_q_s","%sp_q_sp","%sp_r_s","%sp_r_sp","%sp_round","%sp_s_s","%sp_s_sp","%sp_sin","%sp_sqrt","%sp_string","%sp_sum","%sp_tril","%sp_triu","%sp_y_s","%sp_y_sp","%sp_z_s","%sp_z_sp","%spb_and","%spb_c_b","%spb_cumprod","%spb_cumsum","%spb_diag","%spb_e","%spb_f_b","%spb_g_b","%spb_g_spb","%spb_h_b","%spb_h_spb","%spb_i_b","%spb_i_ce","%spb_i_h","%spb_i_st","%spb_or","%spb_prod","%spb_sum","%spb_tril","%spb_triu","%st_6","%st_c_st","%st_e","%st_f_st","%st_i_b","%st_i_c","%st_i_fptr","%st_i_h","%st_i_i","%st_i_ip","%st_i_lss","%st_i_msp","%st_i_p","%st_i_r","%st_i_s","%st_i_sp","%st_i_spb","%st_i_st","%st_matrix","%st_n_c","%st_n_l","%st_n_mc","%st_n_p","%st_n_s","%st_o_c","%st_o_l","%st_o_mc","%st_o_p","%st_o_s","%st_o_tl","%st_p","%st_size","%st_string","%st_t","%ticks_i_h","%xls_e","%xls_p","%xlssheet_e","%xlssheet_p","%xlssheet_size","%xlssheet_string","DominationRank","G_make","IsAScalar","NDcost","OS_Version","PlotSparse","ReadHBSparse","ReadmiMatrix","TCL_CreateSlave","WritemiMatrix","abcd","abinv","accept_func_default","accept_func_vfsa","acf","acosd","acosh","acoshm","acosm","acot","acotd","acoth","acsc","acscd","acsch","add_demo","add_help_chapter","add_module_help_chapter","add_param","add_profiling","adj2sp","aff2ab","ana_style","analpf","analyze","aplat","apropos","arhnk","arl2","arma2p","armac","armax","armax1","arobasestring2strings","arsimul","ascii2string","asciimat","asec","asecd","asech","asind","asinh","asinhm","asinm","assert_checkalmostequal","assert_checkequal","assert_checkerror","assert_checkfalse","assert_checkfilesequal","assert_checktrue","assert_comparecomplex","assert_computedigits","assert_cond2reltol","assert_cond2reqdigits","assert_generror","atand","atanh","atanhm","atanm","atomsAutoload","atomsAutoloadAdd","atomsAutoloadDel","atomsAutoloadList","atomsCategoryList","atomsCheckModule","atomsDepTreeShow","atomsGetConfig","atomsGetInstalled","atomsGetLoaded","atomsGetLoadedPath","atomsInstall","atomsIsInstalled","atomsIsLoaded","atomsList","atomsLoad","atomsRemove","atomsRepositoryAdd","atomsRepositoryDel","atomsRepositoryList","atomsRestoreConfig","atomsSaveConfig","atomsSearch","atomsSetConfig","atomsShow","atomsSystemInit","atomsSystemUpdate","atomsTest","atomsUpdate","atomsVersion","augment","auread","auwrite","balreal","bench_run","bilin","bilt","bin2dec","binomial","bitand","bitcmp","bitget","bitor","bitset","bitxor","black","blanks","bloc2exp","bloc2ss","block_parameter_error","bode","bstap","buttmag","bvodeS","bytecode","bytecodewalk","cainv","calendar","calfrq","canon","casc","cat","cat_code","cb_m2sci_gui","ccontrg","cell","cell2mat","cellstr","center","cepstrum","cfspec","char","chart","cheb1mag","cheb2mag","check_gateways","check_help","check_modules_xml","check_versions","chepol","chfact","chsolve","classmarkov","clean_help","clock","cls2dls","cmb_lin","cmndred","cmoment","coding_ga_binary","coding_ga_identity","coff","coffg","colcomp","colcompr","colinout","colregul","companion","complex","compute_initial_temp","cond","cond2sp","condestsp","config","configure_msifort","configure_msvc","cont_frm","cont_mat","contrss","conv","convert_to_float","convertindex","convol","convol2d","copfac","correl","cosd","cosh","coshm","cosm","cotd","cotg","coth","cothm","covar","createfun","createstruct","crossover_ga_binary","crossover_ga_default","csc","cscd","csch","csgn","csim","cspect","ctr_gram","czt","dae","daeoptions","damp","datafit","date","datenum","datevec","dbphi","dcf","ddp","dec2bin","dec2hex","dec2oct","del_help_chapter","del_module_help_chapter","demo_begin","demo_choose","demo_compiler","demo_end","demo_file_choice","demo_folder_choice","demo_function_choice","demo_gui","demo_mdialog","demo_message","demo_run","demo_viewCode","denom","derivat","derivative","des2ss","des2tf","detectmsifort64tools","detectmsvc64tools","determ","detr","detrend","devtools_run_builder","dft","dhnorm","diff","diophant","dir","dirname","dispfiles","dllinfo","dscr","dsimul","dt_ility","dtsi","edit","edit_error","eigenmarkov","ell1mag","enlarge_shape","entropy","eomday","epred","eqfir","eqiir","equil","equil1","erf","erfc","erfcx","erfinv","etime","eval","evans","evstr","expression2code","extract_help_examples","factor","factorial","factors","faurre","ffilt","fft2","fftshift","fieldnames","filt_sinc","filter","findABCD","findAC","findBDK","findR","find_freq","find_links","find_scicos_version","findm","findmsifortcompiler","findmsvccompiler","findx0BD","firstnonsingleton","fit_dat","fix","fixedpointgcd","flipdim","flts","fminsearch","format_txt","fourplan","fprintf","frep2tf","freson","frfit","frmag","fscanf","fseek_origin","fsfirlin","fspec","fspecg","fstabst","ftest","ftuneq","fullfile","fullrf","fullrfk","fun2string","g_margin","gainplot","gamitg","gcare","gcd","gencompilationflags_unix","generateBlockImage","generateBlockImages","generic_i_ce","generic_i_h","generic_i_hm","generic_i_s","generic_i_st","genlib","genlib_old","genmarkov","geomean","getDiagramVersion","getModelicaPath","get_file_path","get_function_path","get_param","get_profile","get_scicos_version","getd","getscilabkeywords","getshell","gettklib","gfare","gfrancis","givens","glever","gmres","group","gschur","gspec","gtild","h2norm","h_cl","h_inf","h_inf_st","h_norm","hallchart","halt","hank","hankelsv","harmean","haveacompiler","head_comments","help","help_from_sci","help_skeleton","hermit","hex2dec","hilb","hilbert","horner","householder","hrmt","htrianr","hypermat","ifft","iir","iirgroup","iirlp","iirmod","ilib_build","ilib_compile","ilib_for_link","ilib_gen_Make","ilib_gen_Make_unix","ilib_gen_cleaner","ilib_gen_gateway","ilib_gen_loader","ilib_include_flag","ilib_mex_build","im_inv","importScicosDiagram","importScicosPal","importXcosDiagram","imrep2ss","ind2sub","inistate","init_ga_default","init_param","initial_scicos_tables","input","instruction2code","intc","intdec","integrate","interp1","interpln","intersect","intl","intsplin","inttrap","inv_coeff","invr","invrs","invsyslin","iqr","isLeapYear","is_absolute_path","is_param","iscell","iscellstr","isempty","isfield","isinf","isnan","isnum","issparse","isstruct","isvector","jmat","justify","kalm","karmarkar","kernel","kpure","krac2","kroneck","lattn","launchtest","lcf","lcm","lcmdiag","leastsq","leqe","leqr","lev","levin","lex_sort","lft","lin","lin2mu","lincos","lindquist","linf","linfn","linsolve","linspace","list2vec","list_param","listfiles","listfunctions","listvarinfile","lmisolver","lmitool","loadXcosLibs","loadmatfile","loadwave","log10","log2","logm","logspace","lqe","lqg","lqg2stan","lqg_ltr","lqr","ls","lyap","m2sci_gui","m_circle","macglov","macrovar","mad","makecell","manedit","mapsound","markp2ss","matfile2sci","mdelete","mean","meanf","median","mese","meshgrid","mfft","mfile2sci","minreal","minss","mkdir","modulo","moment","mrfit","msd","mstr2sci","mtlb","mtlb_0","mtlb_a","mtlb_all","mtlb_any","mtlb_axes","mtlb_axis","mtlb_beta","mtlb_box","mtlb_choices","mtlb_close","mtlb_colordef","mtlb_cond","mtlb_conv","mtlb_cov","mtlb_cumprod","mtlb_cumsum","mtlb_dec2hex","mtlb_delete","mtlb_diag","mtlb_diff","mtlb_dir","mtlb_double","mtlb_e","mtlb_echo","mtlb_error","mtlb_eval","mtlb_exist","mtlb_eye","mtlb_false","mtlb_fft","mtlb_fftshift","mtlb_filter","mtlb_find","mtlb_findstr","mtlb_fliplr","mtlb_fopen","mtlb_format","mtlb_fprintf","mtlb_fread","mtlb_fscanf","mtlb_full","mtlb_fwrite","mtlb_get","mtlb_grid","mtlb_hold","mtlb_i","mtlb_ifft","mtlb_image","mtlb_imp","mtlb_int16","mtlb_int32","mtlb_int8","mtlb_is","mtlb_isa","mtlb_isfield","mtlb_isletter","mtlb_isspace","mtlb_l","mtlb_legendre","mtlb_linspace","mtlb_logic","mtlb_logical","mtlb_loglog","mtlb_lower","mtlb_max","mtlb_mean","mtlb_median","mtlb_mesh","mtlb_meshdom","mtlb_min","mtlb_more","mtlb_num2str","mtlb_ones","mtlb_pcolor","mtlb_plot","mtlb_prod","mtlb_qr","mtlb_qz","mtlb_rand","mtlb_randn","mtlb_rcond","mtlb_realmax","mtlb_realmin","mtlb_repmat","mtlb_s","mtlb_semilogx","mtlb_semilogy","mtlb_setstr","mtlb_size","mtlb_sort","mtlb_sortrows","mtlb_sprintf","mtlb_sscanf","mtlb_std","mtlb_strcmp","mtlb_strcmpi","mtlb_strfind","mtlb_strrep","mtlb_subplot","mtlb_sum","mtlb_t","mtlb_toeplitz","mtlb_tril","mtlb_triu","mtlb_true","mtlb_type","mtlb_uint16","mtlb_uint32","mtlb_uint8","mtlb_upper","mtlb_var","mtlb_zeros","mu2lin","mutation_ga_binary","mutation_ga_default","mvcorrel","mvvacov","nancumsum","nand2mean","nanmax","nanmean","nanmeanf","nanmedian","nanmin","nanstdev","nansum","narsimul","ndgrid","ndims","nehari","neigh_func_csa","neigh_func_default","neigh_func_fsa","neigh_func_vfsa","neldermead_cget","neldermead_configure","neldermead_costf","neldermead_defaultoutput","neldermead_destroy","neldermead_display","neldermead_function","neldermead_get","neldermead_log","neldermead_new","neldermead_restart","neldermead_search","neldermead_updatesimp","nextpow2","nfreq","nicholschart","nlev","nmplot_cget","nmplot_configure","nmplot_contour","nmplot_destroy","nmplot_display","nmplot_function","nmplot_get","nmplot_historyplot","nmplot_log","nmplot_new","nmplot_outputcmd","nmplot_restart","nmplot_search","nmplot_simplexhistory","noisegen","nonreg_test_run","norm","now","null","num2cell","numdiff","numer","nyquist","nyquistfrequencybounds","obs_gram","obscont","observer","obsv_mat","obsvss","oct2dec","odeoptions","optim_ga","optim_moga","optim_nsga","optim_nsga2","optim_sa","optimbase_cget","optimbase_checkbounds","optimbase_checkcostfun","optimbase_checkx0","optimbase_configure","optimbase_destroy","optimbase_display","optimbase_function","optimbase_get","optimbase_hasbounds","optimbase_hasconstraints","optimbase_hasnlcons","optimbase_histget","optimbase_histset","optimbase_incriter","optimbase_isfeasible","optimbase_isinbounds","optimbase_isinnonlincons","optimbase_log","optimbase_logshutdown","optimbase_logstartup","optimbase_new","optimbase_outputcmd","optimbase_outstruct","optimbase_proj2bnds","optimbase_set","optimbase_stoplog","optimbase_terminate","optimget","optimplotfunccount","optimplotfval","optimplotx","optimset","optimsimplex_center","optimsimplex_check","optimsimplex_compsomefv","optimsimplex_computefv","optimsimplex_deltafv","optimsimplex_deltafvmax","optimsimplex_destroy","optimsimplex_dirmat","optimsimplex_fvmean","optimsimplex_fvstdev","optimsimplex_fvvariance","optimsimplex_getall","optimsimplex_getallfv","optimsimplex_getallx","optimsimplex_getfv","optimsimplex_getn","optimsimplex_getnbve","optimsimplex_getve","optimsimplex_getx","optimsimplex_gradientfv","optimsimplex_log","optimsimplex_new","optimsimplex_print","optimsimplex_reflect","optimsimplex_setall","optimsimplex_setallfv","optimsimplex_setallx","optimsimplex_setfv","optimsimplex_setn","optimsimplex_setnbve","optimsimplex_setve","optimsimplex_setx","optimsimplex_shrink","optimsimplex_size","optimsimplex_sort","optimsimplex_tostring","optimsimplex_xbar","orth","p_margin","pack","pareto_filter","parrot","pbig","pca","pcg","pdiv","pen2ea","pencan","pencost","penlaur","perctl","perl","perms","permute","pertrans","pfactors","pfss","phasemag","phaseplot","phc","pinv","playsnd","plotprofile","plzr","pmodulo","pol2des","pol2str","polar","polfact","prbs_a","prettyprint","primes","princomp","profile","proj","projsl","projspec","psmall","pspect","qmr","qpsolve","quart","quaskro","rafiter","randpencil","range","rank","read_csv","readxls","recompilefunction","recons","reglin","regress","remezb","remove_param","remove_profiling","repfreq","replace_Ix_by_Fx","repmat","reset_profiling","resize_matrix","returntoscilab","rhs2code","ric_desc","riccati","rmdir","routh_t","rowcomp","rowcompr","rowinout","rowregul","rowshuff","rref","sample","samplef","samwr","savematfile","savewave","scanf","sci2exp","sciGUI_init","sci_sparse","scicos_getvalue","scicos_simulate","scicos_workspace_init","scisptdemo","scitest","sdiff","sec","secd","sech","selection_ga_elitist","selection_ga_random","sensi","set_param","setdiff","sgrid","show_margins","show_pca","showprofile","signm","sinc","sincd","sind","sinh","sinhm","sinm","sm2des","sm2ss","smga","smooth","solve","sound","soundsec","sp2adj","spaninter","spanplus","spantwo","specfact","speye","sprand","spzeros","sqroot","sqrtm","squarewave","squeeze","srfaur","srkf","ss2des","ss2ss","ss2tf","sscanf","sskf","ssprint","ssrand","st_deviation","st_i_generic","st_ility","stabil","statgain","stdev","stdevf","steadycos","strange","strcmpi","struct","sub2ind","sva","svplot","sylm","sylv","sysconv","sysdiag","sysfact","syslin","syssize","system","systmat","tabul","tand","tanh","tanhm","tanm","tbx_build_blocks","tbx_build_cleaner","tbx_build_gateway","tbx_build_gateway_clean","tbx_build_gateway_loader","tbx_build_help","tbx_build_help_loader","tbx_build_loader","tbx_build_macros","tbx_build_src","tbx_builder","tbx_builder_gateway","tbx_builder_gateway_lang","tbx_builder_help","tbx_builder_help_lang","tbx_builder_macros","tbx_builder_src","tbx_builder_src_lang","temp_law_csa","temp_law_default","temp_law_fsa","temp_law_huang","temp_law_vfsa","test_clean","test_on_columns","test_run","test_run_level","testexamples","tf2des","tf2ss","thrownan","tic","time_id","toc","toeplitz","tokenpos","toolboxes","trace","trans","translatepaths","tree2code","trfmod","trianfml","trimmean","trisolve","trzeros","typeof","ui_observer","union","unique","unit_test_run","unix_g","unix_s","unix_w","unix_x","unobs","unpack","variance","variancef","vec2list","vectorfind","ver","warnobsolete","wavread","wavwrite","wcenter","weekday","wfir","wfir_gui","whereami","who_user","whos","wiener","wigner","winclose","window","winlist","with_javasci","with_macros_source","with_modelica_compiler","with_pvm","with_texmacs","with_tk","write_csv","xcosBlockEval","xcosBlockInterface","xcosCodeGeneration","xcosConfigureModelica","xcosPal","xcosPalAdd","xcosPalAddBlock","xcosPalExport","xcosShowBlockWarning","xcosValidateBlockSet","xcosValidateCompareBlock","xcos_compile","xcos_run","xcos_simulate","xcos_workspace_init","xmltochm","xmltoformat","xmltohtml","xmltojar","xmltopdf","xmltops","xmltoweb","yulewalk","zeropen","zgrid","zpbutt","zpch1","zpch2","zpell"]

builtin_consts = ["\\$","%F","%T","%e","%eps","%f","%fftw","%gui","%i","%inf","%io","%modalWarning","%nan","%pi","%s","%t","%tk","%toolboxes","%toolboxes_dir","%z","PWD","SCI","SCIHOME","TMPDIR","a","ans","assertlib","atomslib","cacsdlib","compatibility_functilib","corelib","data_structureslib","demo_toolslib","development_toolslib","differential_equationlib","dynamic_linklib","elementary_functionslib","fd","fileiolib","functionslib","genetic_algorithmslib","helptoolslib","home","i","integerlib","interpolationlib","iolib","j","linear_algebralib","m2scilib","matiolib","modules_managerlib","myStr","neldermeadlib","optimbaselib","optimizationlib","optimsimplexlib","output_streamlib","overloadinglib","parameterslib","polynomialslib","scicos_autolib","scicos_utilslib","scinoteslib","signal_processinglib","simulated_annealinglib","soundlib","sparselib","special_functionslib","spreadsheetlib","statisticslib","stringlib","tclscilib","timelib","umfpacklib","varType","xcoslib"]
