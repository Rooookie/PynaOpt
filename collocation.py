#!/usr/bin/env python

import sys
import time
class ModelScript(object):
    """
    GAMS model scripts
    """   
    def __init__(self, title, par_def, var_def, eqn_def, sol_stat, plt_stat):
        """
        All the variables are strings
        """
        self.title = title
        self.par_def = par_def
        self.var_def = var_def
        self.eqn_def = eqn_def
        self.sol_stat = sol_stat
        self.plt_stat = plt_stat
                
def write_model(ModelScript):
    """
    Write to the temporary GAMS file
    """
    _tmp_file = open('collocation_model.gms','w')
    _tmp_file.write(ModelScript.title + '\n')
    _tmp_file.write(ModelScript.par_def + '\n')
    _tmp_file.write(ModelScript.var_def + '\n')
    _tmp_file.write(ModelScript.eqn_def + '\n')
    _tmp_file.write(ModelScript.sol_stat + '\n')
    _tmp_file = open('result_plt.gms','w')
    _tmp_file.write(ModelScript.plt_stat)
    _tmp_file.close()
    
def set_title():
    """
    Editing the title part
    """
    _title = ['$title',
              '$ontext',
              'Description of the GAMS model',
              'Time-stamp: <>',
              '$offtext',
              '',
              '$oneolcom',
              '$eolcom #',
              '']
    _title = '\n'.join(_title)
    return _title

def set_par_def(num_fin, num_col, tot_time, diff_vars):
    """
    Editing the parameter definiation part
    """
    _par_def = ['* model parameter declaration',
                'set k     finite elements /1*%s/;' % num_fin,
                'set q     collocation points /1*%s/;' % num_col,
                '',
                'alias(k,kp);',
                'alias(q,qp);',
                '',
                '* parameters for the collocation method',
                'parameters'
                '          len(k) lengths of the finite elements',
                '          time_horizon total length of time;',
                'len(k) = 1/card(k);',
                'time_horizon = %s;' % tot_time]
    _diff_list = ['\n* parameters for initilizing differential varibales\n\nparameters'];
    for var in diff_vars:
        _diff_list.append('        %sini' % (var))
    _diff_list = '\n'.join(_diff_list)
    _diff_list = _diff_list + ';\n'
    for var in diff_vars:
        _diff_list = _diff_list + '%sini = ;\n' % var
    if int(num_col) == 3:
        _col_table = ['table Omega(q,q) collocation coefficients of 3-pt Radau roots',
                      '1                            2                          3',
                      '1    0.196815433731079        0.394424288467084        0.376403042786093',
                      '2   -0.0655354025650992       0.292073492494108        0.512485883439094',
                      '3    0.0237709688340207       -0.0415487809611925      0.111111073774813;']
    else:
        _col_table = ['table Omega(q,q)   radau collacation coefficients',
                      '1                        2',
                      '1      0.416666125000187        0.749999625000188',
                      '2     -0.0833331250001875       0.250000374999812;']
    _par_def = '\n'.join(_par_def)
    _col_table = '\n'.join(_col_table)
    _par_def = _par_def + '\n' + _diff_list + '\n' + _col_table
    return _par_def

def set_var_def(diff_vars, alge_vars, cntr_vars):
    """
    Define variables according to the list of variables
    """
    _tmp_head = ['',
                 'variables',
                 '\n* objective function\n',
                 '        obj',
                 '\n* variables to be optimized\n']
    _tmp_head = '\n'.join(_tmp_head)  
    _tmp_body = []     
    for var in cntr_vars:
        _var_list = '        %s(k)' % var
        _tmp_body.append(_var_list)
    _tmp_body.append('\n* differential variables\n')
    for var in diff_vars:
        _var_list = '        %s(k,q), %s0(k), %sdot(k,q)' % (var, var, var)
        _tmp_body.append(_var_list)
    _tmp_body.append('\n* algebraic variables\n')
    for var in alge_vars:
        _var_list = '        %s(k,q)' % var
        _tmp_body.append(_var_list)
    _tmp_body = '\n'.join(_tmp_body)
    _var_def = _tmp_head + '\n' + _tmp_body + ';'
    return _var_def

def set_eqn_def(diff_vars, alge_vars):
    """
    Define equations according to the list of variables
    """
    _tmp_head = ['\nequations objective,'];
    for var in diff_vars:
      _eqn_list = ['          collocation_%s,' % var,
                   '          continuity_%s,' % var,
                   '          initialization_%s,' % var,
                   '          dynamic_%s,' % var]  
      _eqn_list = '\n'.join(_eqn_list)  
      _tmp_head.append(_eqn_list)
    for var in alge_vars:
        _eqn_list = '          algebraic_%s,' % var
        _tmp_head.append(_eqn_list)
    _tmp_head = '\n'.join(_tmp_head)
    _tmp_head = _tmp_head[: -1] + ';'
    _tmp_body = ['\n* objective function\n\nobjective..\n        obj =e= ;\n'];
    _tmp_body.append('* collocation over finite elements')
    for var in diff_vars:
        _tmp_body.append('\ncollocation_%s(k,q)..\n        %s(k,q) =e= %s0(k) + time_horizon*len(k)*sum(qp,Omega(qp,q)*%sdot(k,qp));\n' % (var, var, var, var))
    _tmp_body.append('* continuity conditions')
    for var in diff_vars:
        _tmp_body.append('\ncontinuity_%s(k,q)$(ord(k) > 1 and ord(q) = card(q))..\n        %s(k-1,q) =e= %s0(k);\n' % (var, var, var))
    _tmp_body.append('* initial conditions')
    for var in diff_vars:
        _tmp_body.append('\ninitialization_%s(k)$(ord(k) = 1)..\n        %s0(k) =e= %s_ini;\n' % (var, var, var))
    _tmp_body.append('* ODEs for the system at collocation points')
    for var in diff_vars:
        _tmp_body.append('\ndynamics_%s(k,q)..\n        %sdot(k,q) =e= ;\n' % (var, var))
    _tmp_body.append('* algebraic equations')
    for var in alge_vars:
        _tmp_body.append('\nalgebraic_%s(k,q)..\n        %s(k,q) =e= ;\n' % (var, var))
    _tmp_body = '\n'.join(_tmp_body)
    
    _eqn_def = _tmp_head + '\n' + _tmp_body 
    return _eqn_def
          
def set_sol_stat(diff_vars, alge_vars, cntr_vars):
    """
    Editing model and solution status
    """
    _tmp_head = ['model dyna_opt using /all/;',
                 'option NLP = coinipopt;',
                 'option decimals = 5;',
                 '$onecho > coinipopt.opt',
                 '# linear_solver ma57',
                 '# mu_strategy adaptive',
                 '# mu_oracle probing',
                 'max_iter 5000',
                 'tol 1e-5',
                 '$offecho',
                 'dyna_opt.optfile = 1;']
    _tmp_head = '\n'.join(_tmp_head)
    _tmp_body = ['* bounds on variables']
    for var in cntr_vars:
         _tmp_body.append('%s.lo = ;\n%s.up = ;\n' % (var, var))
    _tmp_body = '\n'.join(_tmp_body)
    _tmp_tail = ['* parameters for initialization\nparameters']     
    for var in cntr_vars:
        _var_list = '        %s_i(k)' % var
        _tmp_tail.append(_var_list)
    for var in diff_vars:
        _var_list = '        %s_i(k,q), %s0_i(k), %sdot_i(k,q)' % (var, var, var)
        _tmp_tail.append(_var_list)
    for var in alge_vars:
        _var_list = '        %s_i(k,q)' % var
        _tmp_tail.append(_var_list)
    _tmp_tail[-1] = _tmp_tail[-1] + ';\n'
    for var in cntr_vars:
        _tmp_tail.append('%s_i(k) = ;' % var)
    for var in diff_vars:
        _tmp_tail.append('%s_i(k,q) = ;\n%s0_i(k) = ;\n%sdot_i(k,q) = ;' % (var, var, var))
    for var in alge_vars:
        _tmp_tail.append('%s_i(k,q) = ;' % var)
    _tmp_tail = '\n'.join(_tmp_tail)
    _sol_stat = ['']
    for var in cntr_vars:
        _sol_stat.append('%s.l(k) = %s_i(k);' % (var, var))
    for var in diff_vars:
        _sol_stat.append('%s.l(k,q) = %s_i(k,q);\n%s0.l(k) = %s0_i(k);\n%sdot.l(k,q) = %sdot_i(k,q);' % (var, var, var, var, var, var))
    for var in alge_vars:
        _sol_stat.append('%s.l(k,q) = %s_i(k,q);' % (var, var))
    _sol_stat = '\n'.join(_sol_stat)
    _sol_stat = _sol_stat + '\n\nsolve dyna_opt using NLP minimizing obj;'
    _sol_stat = '\n'.join([_tmp_head, _tmp_body, _tmp_tail, _sol_stat, '\n$include result_plt.gms'])
    return _sol_stat

def set_plt_stat(diff_vars, alge_vars, cntr_vars):
    """
    Editing for plotting function
    """
    _tmp_head = ['variables time(k,q), time0(k), dummy_obj;',
                 'equations dummy_objective, collocation_time, continuity_time, initilization_time;',
                 '',
                 'dummy_objective..',
                 '        dummy_obj =e= 0;',
                 '',
                 'collocation_time(k,q)..',
                 '        time(k,q) =e= time0(k) + len(k)*sum(qp,Omega(qp,q));',
                 '',
                 'continuity_time(k,q)$(ord(k) > 1 and ord(q) = card(q))..',
                 '        time0(k) =e= time(k-1,q);',
                 '',
                 'initilization_time..',
                 '        time0(\'1\') =e= 0;',
                 '',
                 'model time_axis using /dummy_objective, collocation_time, continuity_time, initilization_time/;',
                 '$offlisting',
                 '$offsymxref offsymlist',
                 'option solprint = off;',
                 'option limrow = 0;',
                 'option limcol = 0;',
                 'option sysout = off;',
                 'solve time_axis using LP maximizing dummy_obj;']
    _tmp_head = '\n'.join(_tmp_head)
    _tmp_body = ['axis(k,q)']
    for var in cntr_vars:
        _tmp_body.append('%s_plot(k)' % var)
    for var in diff_vars:
        _tmp_body.append('%s_plot(k,q)' % var)
    for var in alge_vars:
        _tmp_body.append('%s_plot(k,q)' % var)
    _tmp_body = '\n\n* parameters for figures\n\nparameters ' + ', '.join(_tmp_body) + ';'
    _plt_stat = _tmp_head + '\n' + _tmp_body 
    _tmp_body = ['axis(k,q) = time_horizon*time.l(k,q);']
    for var in cntr_vars:
        _tmp_body.append('%s_plot(k) = %s.l(k);' % (var, var))
    for var in diff_vars:
        _tmp_body.append('%s_plot(k,q) = %s.l(k,q);' % (var, var))
    for var in alge_vars:
        _tmp_body.append('%s_plot(k,q) = %s.l(k,q);' % (var, var))
    _tmp_body = '\n'.join(_tmp_body)
    _plt_stat = _plt_stat + '\n' + _tmp_body
    _tmp_list = ['0']
    for var in cntr_vars:
        _tmp_list.append('%s_plot(\'1\')' % var)
    for var in diff_vars:
        _tmp_list.append('%sini' % var)
    for var in alge_vars:
        _tmp_list.append('%sini' % var)
    _tmp_list = ', '.join(_tmp_list)
    _tmp_list2 = ['axis(k,q)']
    for var in cntr_vars:
        _tmp_list2.append('%s_plot(k)' % var)
    for var in diff_vars:
        _tmp_list2.append('%s_plot(k,q)' % var)
    for var in alge_vars:
        _tmp_list2.append('%s_plot(k,q)' % var)
    _tmp_list2 = ', '.join(_tmp_list2)
    _tmp_tail = ['file datafile /opt_sltn.dat/;',
                 'put datafile;',
                 'datafile.nd = 5;',
                 'put \'# optimal objective value\'/;',
                 'put \'#\', obj.l /;',
                 'put \'# axis\'/;',
                 'put ' + _tmp_list + '/',
                 'loop(k,',
                 '        loop(q,',
                 '        put ' + _tmp_list2 + '/',
                 '        );',
                 ');',
                 'putclose;']
    _tmp_tail = '\n'.join(_tmp_tail)
    _plt_stat = _plt_stat + '\n' + _tmp_tail
    _tmp_tail = ['',
                 'file pltfile /results.gpl/;',
                 'put pltfile;',
                 'put',
                 '    \'set term postscript enhanced color\'/',
                 '    \'set output "control_profiles.ps"\'/',
                 '    \'set key\'/',
                 '    \'set autoscale\'/',
                 '    \'set ytics font ",10"\'/',
                 '    \'set multiplot layout 2, 1\'/',
                 '    \'set xlabel " []"\'/',
                 '    \'set ylabel " []"\'/',
                 '    \'plot "opt_sltn.dat" using 1:2 with fsteps lw 2\'/',
                 '    \'set xlabel " []"\'/',
                 '    \'set ylabel " []"\'/',
                 '    \'plot "opt_sltn.dat" using 1:3 with fsteps lw 2\'/',
                 '    \'unset multiplot\'/',
                 '    \'unset key\'/',
                 '    \'unset label\'/',
                 '    \'set output "state_profiles.ps"\'/',
                 '    \'set key\'/',
                 '    \'set autoscale\'/',
                 '    \'set ytics font ",10"\'/',
                 '    \'set multiplot layout 1, 1\'/',
                 '    \'set xlabel " []"\'/',
                 '    \'set ylabel " []"\'/',
                 '    \'plot "opt_sltn.dat" using 1:4 with lines title "" lw 2,\ \'/',
                 '    \'"opt_sltn.dat" using 1:5 with lines title "" lw 2\'',
                 '    \'unset multiplot\'/',
                 '    \'unset key\'/',
                 '    \'unset label\'/',
                 'putclose;']
    _plt_stat = _plt_stat + '\n' + '\n'.join(_tmp_tail)
    return _plt_stat

def read_inputs():
    """
    read the input file
    """
    _line_count = 0
    for _line in open("data_file.dat", 'r').readlines():
        _line = _line.strip().split()
        if len(_line) == 0 or _line[0] == '#':
            continue
        else: 
            _line_count = _line_count + 1
        if _line_count == 1:
            _num_fin = _line[0]
            _num_col = _line[1]
            _tot_time = _line[2]
        elif _line_count == 2:
            _diff_vars = _line
        elif _line_count == 3:
            _alge_vars = _line
        elif _line_count == 4:
            _cntr_vars = _line
        else:
            continue
    return _num_fin, _num_col, _tot_time, _diff_vars, _alge_vars, _cntr_vars     
         
if __name__ == '__main__':
    num_fin, num_col, tot_time, diff_vars, alge_vars, cntr_vars = read_inputs()
    title = set_title()
    par_def = set_par_def(num_fin, num_col, tot_time, diff_vars)
    var_def = set_var_def(diff_vars, alge_vars, cntr_vars)
    eqn_def = set_eqn_def(diff_vars, alge_vars)
    sol_stat = set_sol_stat(diff_vars, alge_vars, cntr_vars)
    plt_stat = set_plt_stat(diff_vars, alge_vars, cntr_vars)
    my_model = ModelScript(title, par_def, var_def, eqn_def, sol_stat, plt_stat)
    write_model(my_model)


  

                    




