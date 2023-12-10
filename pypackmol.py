#!/bin/env python
import os
import ase.io as aseio
from ase.data import chemical_symbols, atomic_names, atomic_masses
import dpdata

thisdir = os.path.dirname(__file__)
datadir = os.path.join(thisdir,'data')

def gen_ele_xyz():
    '''
    generate xyz file for element
    '''
    for i,ele in enumerate(chemical_symbols):
        with open('{}/{}.xyz'.format(datadir,ele),'w') as f:
            f.write('1\n')
            f.write('#{}\n'.format(atomic_names[i]))
            f.write('{0:3} {1:15.9f} {1:15.9f} {1:15.9f}\n'.format(ele, 0))

def gen_packmol_in(ele=['Si','O', 'Ge', 'Bi'], n=[1000,2050,10,10], box=40):
    command = []
    command.append('# A mixture of atoms')
    command.append('tolerance 2.0')
    command.append('filetype xyz')
    command.append('output glass.xyz')
    for e, i in zip(ele,n):
        command.append('structure {}/{}.xyz'.format(datadir, e))
        command.append('    number {}'.format(i))
        command.append('    inside box 0. 0. 0. 40. 40. 40.')
        command.append('end structure')

    with open('glass.in','w') as f:
        f.write('\n'.join(command))

def insert_mass_to_lammps_data(f='2.data', ele=['Si','O', 'Ge', 'Bi']):
    cont = [line for line in open(f)]
    for i, line in enumerate(cont):
        if 'Atoms' in line:
            n = i
    con_i='Masses\n\n'
    for i, e in enumerate(ele):
        en = chemical_symbols.index(e)
        masses= atomic_masses[en]
       #con_i +='{:6} {:11.5f} # {}\n'.format(i+1, masses, e)
        con_i +='{:6} {:11.5f} \n'.format(i+1, masses)
    con_i +='\n'

    cont.insert(n,con_i)

    with open(f,'w') as f:
        f.write(''.join(cont))

if __name__ == '__main__':
    gen_ele_xyz()
    box = 40
    gen_packmol_in()
    g = aseio.read('glass.xyz',format='xyz')
    g.set_cell([box+1,box+1,box+1])
    aseio.write('1.vasp',g,format='vasp')
    aseio.write('1.data',g,format='lammps-data')
    d_poscar = dpdata.System("1.vasp", fmt="vasp/poscar")
    d_poscar.to( 'lammps/lmp', '2.data')
    insert_mass_to_lammps_data()


